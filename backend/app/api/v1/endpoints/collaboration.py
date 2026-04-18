"""
Endpoints de Colaboração
Compartilhamento, comentários e histórico de alterações
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr

from app.api.v1.deps import get_current_user, get_db
from app.core.audit import AuditAction, audit_logger
from app.domain.collaboration import (
    InvestigationChangeLog,
    InvestigationComment,
    InvestigationShare,
    PermissionLevel,
)
from app.domain.user import User
from app.repositories.investigation import InvestigationRepository
from app.repositories.user import UserRepository
from app.services.collaboration import collaboration_service
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== Schemas ====================


class ShareInvestigationRequest(BaseModel):
    email: EmailStr
    permission: PermissionLevel
    expires_at: Optional[datetime] = None


class UpdatePermissionRequest(BaseModel):
    permission: PermissionLevel


class AddCommentRequest(BaseModel):
    content: str
    parent_id: Optional[int] = None
    is_internal: bool = False


class UpdateCommentRequest(BaseModel):
    content: str


# ==================== Compartilhamento ====================


@router.post("/investigations/{investigation_id}/share")
async def share_investigation(
    investigation_id: int,
    data: ShareInvestigationRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Compartilha investigação com outro usuário

    **Permissões disponíveis**:
    - `view`: Apenas visualizar
    - `comment`: Visualizar + comentar
    - `edit`: Visualizar + comentar + editar
    - `admin`: Controle total

    **Exemplo**:
    ```json
    {
      "email": "usuario@example.com",
      "permission": "edit",
      "expires_at": "2026-12-31T23:59:59"
    }
    ```
    """
    try:
        # Verificar se usuário é dono ou tem permissão ADMIN
        has_permission = await collaboration_service.check_permission(
            db, investigation_id, current_user.id, PermissionLevel.ADMIN
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para compartilhar esta investigação",
            )

        # Compartilhar
        share = await collaboration_service.share_investigation(
            db,
            investigation_id=investigation_id,
            owner_id=current_user.id,
            shared_with_email=data.email,
            permission=data.permission,
            expires_at=data.expires_at,
        )

        # Enviar email de notificação
        try:
            user_repo = UserRepository(db)
            investigation_repo = InvestigationRepository(db)

            # Buscar usuário que receberá o compartilhamento
            shared_user = await user_repo.get_by_email(data.email)

            # Buscar dados da investigação
            investigation = await investigation_repo.get(investigation_id)

            if shared_user and investigation:
                await EmailService.send_investigation_shared(
                    user_email=shared_user.email,
                    user_name=shared_user.full_name or shared_user.username,
                    investigation={
                        "id": investigation.id,
                        "target_name": investigation.target_name,
                    },
                    shared_by_name=current_user.full_name or current_user.username,
                    permission_level=data.permission.value,
                )
                logger.info(f"📧 Email de compartilhamento enviado para {shared_user.email}")
        except Exception as email_error:
            logger.warning(f"Falha ao enviar email de compartilhamento: {email_error}")
            # Não falhar a operação se o email falhar

        # Audit log
        await audit_logger.log(
            db,
            action=AuditAction.INVESTIGATION_SHARED,
            user_id=current_user.id,
            username=current_user.email,
            resource_type="investigation",
            resource_id=str(investigation_id),
            details={"shared_with": data.email, "permission": data.permission.value},
            ip_address=request.client.host,
            success=True,
        )

        return {
            "status": "success",
            "message": f"Investigação compartilhada com {data.email}",
            "share": share.to_dict(),
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao compartilhar investigação: {str(e)}",
        )


@router.get("/investigations/{investigation_id}/shares")
async def list_shares(
    investigation_id: int, current_user: User = Depends(get_current_user), db=Depends(get_db)
):
    """Lista todos os compartilhamentos de uma investigação"""
    from sqlalchemy import select

    # Verificar permissão
    has_permission = await collaboration_service.check_permission(
        db, investigation_id, current_user.id, PermissionLevel.VIEW
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem acesso a esta investigação"
        )

    # Buscar compartilhamentos
    query = select(InvestigationShare).where(
        InvestigationShare.investigation_id == investigation_id,
        InvestigationShare.is_active == True,
    )
    result = await db.execute(query)
    shares = result.scalars().all()

    return {"total": len(shares), "shares": [share.to_dict() for share in shares]}


@router.delete("/investigations/{investigation_id}/shares/{shared_with_id}")
async def revoke_access(
    investigation_id: int,
    shared_with_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Remove acesso de um usuário"""
    # Verificar permissão ADMIN
    has_permission = await collaboration_service.check_permission(
        db, investigation_id, current_user.id, PermissionLevel.ADMIN
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para remover acessos",
        )

    success = await collaboration_service.revoke_access(
        db, investigation_id, current_user.id, shared_with_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Compartilhamento não encontrado"
        )

    # Audit log
    await audit_logger.log(
        db,
        action=AuditAction.INVESTIGATION_UPDATED,
        user_id=current_user.id,
        username=current_user.email,
        resource_type="investigation",
        resource_id=str(investigation_id),
        details={"action": "access_revoked", "user_id": shared_with_id},
        ip_address=request.client.host,
        success=True,
    )

    return {"status": "success", "message": "Acesso removido com sucesso"}


# ==================== Comentários ====================


@router.post("/investigations/{investigation_id}/comments")
async def add_comment(
    investigation_id: int,
    data: AddCommentRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Adiciona comentário ou anotação

    **Tipos**:
    - `is_internal: false` - Comentário compartilhado (visível para todos com acesso)
    - `is_internal: true` - Anotação privada (apenas você vê)
    """
    # Verificar permissão COMMENT
    required_permission = PermissionLevel.VIEW if data.is_internal else PermissionLevel.COMMENT
    has_permission = await collaboration_service.check_permission(
        db, investigation_id, current_user.id, required_permission
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para comentar"
        )

    comment = await collaboration_service.add_comment(
        db,
        investigation_id=investigation_id,
        user_id=current_user.id,
        content=data.content,
        parent_id=data.parent_id,
        is_internal=data.is_internal,
    )

    return {"status": "success", "message": "Comentário adicionado", "comment": comment.to_dict()}


@router.get("/investigations/{investigation_id}/comments")
async def list_comments(
    investigation_id: int,
    include_internal: bool = True,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Lista comentários de uma investigação"""
    from sqlalchemy import desc, select

    # Verificar permissão
    has_permission = await collaboration_service.check_permission(
        db, investigation_id, current_user.id, PermissionLevel.VIEW
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem acesso a esta investigação"
        )

    # Buscar comentários
    query = select(InvestigationComment).where(
        InvestigationComment.investigation_id == investigation_id,
        InvestigationComment.is_deleted == False,
    )

    # Filtrar comentários internos (apenas do próprio usuário)
    if include_internal:
        from sqlalchemy import or_

        query = query.where(
            or_(
                InvestigationComment.is_internal == False,
                InvestigationComment.user_id == current_user.id,
            )
        )
    else:
        query = query.where(InvestigationComment.is_internal == False)

    query = query.order_by(desc(InvestigationComment.created_at))

    result = await db.execute(query)
    comments = result.scalars().all()

    return {"total": len(comments), "comments": [comment.to_dict() for comment in comments]}


@router.put("/comments/{comment_id}")
async def update_comment(
    comment_id: int,
    data: UpdateCommentRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Atualiza comentário (apenas autor)"""
    from sqlalchemy import select

    query = select(InvestigationComment).where(InvestigationComment.id == comment_id)
    result = await db.execute(query)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comentário não encontrado"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode editar seus próprios comentários",
        )

    comment.content = data.content
    comment.updated_at = datetime.utcnow()
    comment.is_edited = True

    await db.commit()
    await db.refresh(comment)

    return {"status": "success", "message": "Comentário atualizado", "comment": comment.to_dict()}


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int, current_user: User = Depends(get_current_user), db=Depends(get_db)
):
    """Deleta comentário (autor ou admin da investigação)"""
    from sqlalchemy import select

    query = select(InvestigationComment).where(InvestigationComment.id == comment_id)
    result = await db.execute(query)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comentário não encontrado"
        )

    # Verificar se é autor ou admin da investigação
    is_author = comment.user_id == current_user.id
    is_admin = await collaboration_service.check_permission(
        db, comment.investigation_id, current_user.id, PermissionLevel.ADMIN
    )

    if not (is_author or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar este comentário",
        )

    comment.is_deleted = True
    comment.content = "[Comentário deletado]"

    await db.commit()

    return {"status": "success", "message": "Comentário deletado"}


# ==================== Histórico de Alterações ====================


@router.get("/investigations/{investigation_id}/changelog")
async def get_change_log(
    investigation_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Retorna histórico de alterações da investigação

    **Inclui**:
    - Criação
    - Atualizações de campos
    - Compartilhamentos
    - Remoção de acessos
    - Comentários importantes
    """
    from sqlalchemy import desc, select

    # Verificar permissão
    has_permission = await collaboration_service.check_permission(
        db, investigation_id, current_user.id, PermissionLevel.VIEW
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem acesso a esta investigação"
        )

    # Buscar histórico
    query = (
        select(InvestigationChangeLog)
        .where(InvestigationChangeLog.investigation_id == investigation_id)
        .order_by(desc(InvestigationChangeLog.timestamp))
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "total": len(logs),
        "limit": limit,
        "offset": offset,
        "changelog": [log.to_dict() for log in logs],
    }


# ==================== Minhas Investigações Compartilhadas ====================


@router.get("/shared-with-me")
async def get_shared_investigations(
    include_owned: bool = False, current_user: User = Depends(get_current_user), db=Depends(get_db)
):
    """
    Retorna investigações compartilhadas comigo

    **Parâmetros**:
    - `include_owned`: Se true, inclui investigações próprias também
    """
    investigations = await collaboration_service.get_shared_investigations(
        db, user_id=current_user.id, include_owned=include_owned
    )

    return {"total": len(investigations), "investigations": investigations}
