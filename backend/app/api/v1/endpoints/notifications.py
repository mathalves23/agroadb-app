"""
Notifications API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.domain.user import User
from app.domain.notification import NotificationType, NotificationPriority
from app.repositories.notification import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    priority: str
    action_url: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    investigation_id: Optional[int]
    is_read: bool
    is_archived: bool
    read_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationStatsResponse(BaseModel):
    total: int
    unread: int
    by_type: dict


@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    include_read: bool = Query(True, description="Incluir notificações lidas"),
    include_archived: bool = Query(False, description="Incluir notificações arquivadas"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista notificações do usuário"""
    repo = NotificationRepository(db)
    notifications = await repo.list_user_notifications(
        user_id=current_user.id,
        include_read=include_read,
        include_archived=include_archived,
        limit=limit,
        offset=offset
    )
    return notifications


@router.get("/unread/count")
async def count_unread_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Conta notificações não lidas"""
    repo = NotificationRepository(db)
    count = await repo.count_unread(current_user.id)
    return {"count": count}


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_notification_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Estatísticas de notificações"""
    repo = NotificationRepository(db)
    stats = await repo.get_stats(current_user.id)
    return stats


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Busca notificação por ID"""
    repo = NotificationRepository(db)
    notification = await repo.get_by_id(notification_id, current_user.id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    return notification


@router.patch("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marca notificação como lida"""
    repo = NotificationRepository(db)
    success = await repo.mark_as_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    await db.commit()
    return {"message": "Notificação marcada como lida"}


@router.post("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marca todas notificações como lidas"""
    repo = NotificationRepository(db)
    count = await repo.mark_all_as_read(current_user.id)
    await db.commit()
    return {"message": f"{count} notificações marcadas como lidas", "count": count}


@router.patch("/{notification_id}/archive")
async def archive_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Arquiva notificação"""
    repo = NotificationRepository(db)
    success = await repo.archive(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    await db.commit()
    return {"message": "Notificação arquivada"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deleta notificação"""
    repo = NotificationRepository(db)
    success = await repo.delete_notification(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    await db.commit()
    return {"message": "Notificação deletada"}


# Endpoint para testes (criar notificação manual)
@router.post("/test")
async def create_test_notification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cria notificação de teste"""
    from app.services.notification_service import NotificationService
    
    await NotificationService.create_notification(
        db=db,
        user_id=current_user.id,
        type=NotificationType.SYSTEM_UPDATE,
        title="Notificação de Teste",
        message="Esta é uma notificação de teste do sistema.",
        priority=NotificationPriority.NORMAL,
        action_url="/dashboard",
        send_email=False
    )
    
    await db.commit()
    return {"message": "Notificação de teste criada"}


@router.post("/test-email")
async def test_email_notification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Testa envio de emails de notificação
    
    Envia dois emails de teste para o usuário atual:
    - Um email de investigação concluída
    - Um email de investigação compartilhada
    
    **Útil para**: Validar configuração SMTP
    """
    from app.services.email_service import EmailService
    
    results = {
        "user_email": current_user.email,
        "investigation_completed": False,
        "investigation_shared": False,
        "errors": []
    }
    
    try:
        # Testar email de investigação concluída
        completed_result = await EmailService.send_investigation_completed(
            user_email=current_user.email,
            user_name=current_user.full_name or current_user.username,
            investigation={
                'id': 999,
                'target_name': 'João da Silva (Teste)',
                'properties_found': 5,
                'companies_found': 2,
                'lease_contracts_found': 3
            }
        )
        results["investigation_completed"] = completed_result
        
        if not completed_result:
            results["errors"].append("Falha ao enviar email de investigação concluída")
    
    except Exception as e:
        results["errors"].append(f"Erro ao enviar email de investigação concluída: {str(e)}")
    
    try:
        # Testar email de investigação compartilhada
        shared_result = await EmailService.send_investigation_shared(
            user_email=current_user.email,
            user_name=current_user.full_name or current_user.username,
            investigation={
                'id': 999,
                'target_name': 'Maria Santos (Teste)'
            },
            shared_by_name="Administrador do Sistema",
            permission_level="edit"
        )
        results["investigation_shared"] = shared_result
        
        if not shared_result:
            results["errors"].append("Falha ao enviar email de investigação compartilhada")
    
    except Exception as e:
        results["errors"].append(f"Erro ao enviar email de investigação compartilhada: {str(e)}")
    
    # Determinar status geral
    if results["investigation_completed"] and results["investigation_shared"]:
        results["status"] = "success"
        results["message"] = f"✅ Emails de teste enviados com sucesso para {current_user.email}"
    elif results["investigation_completed"] or results["investigation_shared"]:
        results["status"] = "partial"
        results["message"] = f"⚠️ Alguns emails foram enviados para {current_user.email}, mas houve falhas"
    else:
        results["status"] = "error"
        results["message"] = "❌ Falha ao enviar emails. Verifique as configurações SMTP."
    
    return results
