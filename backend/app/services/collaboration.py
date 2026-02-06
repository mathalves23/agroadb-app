"""
Sistema de Colaboração - Compartilhamento de Investigações
Permite que múltiplos usuários trabalhem juntos em investigações
"""
from typing import Optional, List
from datetime import datetime
import logging

from app.domain.collaboration import (
    PermissionLevel,
    InvestigationShare,
    InvestigationComment,
    InvestigationChangeLog,
)

logger = logging.getLogger(__name__)


class CollaborationService:
    """
    Serviço de Colaboração
    
    Gerencia compartilhamentos, comentários e histórico de alterações
    """
    
    @staticmethod
    async def share_investigation(
        db,
        investigation_id: int,
        owner_id: int,
        shared_with_email: str,
        permission: PermissionLevel,
        expires_at: Optional[datetime] = None
    ) -> InvestigationShare:
        """
        Compartilha investigação com outro usuário
        
        Args:
            db: Sessão do banco
            investigation_id: ID da investigação
            owner_id: ID de quem está compartilhando
            shared_with_email: Email do usuário a receber acesso
            permission: Nível de permissão
            expires_at: Data de expiração (opcional)
            
        Returns:
            InvestigationShare criado
        """
        from sqlalchemy import select
        from app.domain.user import User
        
        # Buscar usuário por email
        query = select(User).where(User.email == shared_with_email)
        result = await db.execute(query)
        shared_with_user = result.scalar_one_or_none()
        
        if not shared_with_user:
            raise ValueError(f"Usuário com email {shared_with_email} não encontrado")
        
        # Verificar se já existe compartilhamento
        existing_query = select(InvestigationShare).where(
            InvestigationShare.investigation_id == investigation_id,
            InvestigationShare.shared_with_id == shared_with_user.id
        )
        existing_result = await db.execute(existing_query)
        existing_share = existing_result.scalar_one_or_none()
        
        if existing_share:
            # Atualizar permissão existente
            existing_share.permission = permission.value
            existing_share.expires_at = expires_at
            existing_share.is_active = True
            await db.commit()
            await db.refresh(existing_share)
            
            logger.info(f"✏️ Compartilhamento atualizado: Investigation {investigation_id} com {shared_with_email}")
            return existing_share
        
        # Criar novo compartilhamento
        share = InvestigationShare(
            investigation_id=investigation_id,
            owner_id=owner_id,
            shared_with_id=shared_with_user.id,
            permission=permission.value,
            expires_at=expires_at,
            is_active=True
        )
        
        db.add(share)
        await db.commit()
        await db.refresh(share)
        
        # Registrar no histórico
        await CollaborationService.log_change(
            db,
            investigation_id=investigation_id,
            user_id=owner_id,
            action="shared",
            description=f"Compartilhado com {shared_with_email} ({permission.value})"
        )
        
        logger.info(f"✅ Investigação {investigation_id} compartilhada com {shared_with_email} ({permission.value})")
        
        return share
    
    @staticmethod
    async def revoke_access(
        db,
        investigation_id: int,
        owner_id: int,
        shared_with_id: int
    ) -> bool:
        """
        Remove acesso de um usuário à investigação
        
        Args:
            db: Sessão do banco
            investigation_id: ID da investigação
            owner_id: ID de quem está removendo o acesso
            shared_with_id: ID do usuário a perder acesso
            
        Returns:
            True se removido com sucesso
        """
        from sqlalchemy import select
        
        query = select(InvestigationShare).where(
            InvestigationShare.investigation_id == investigation_id,
            InvestigationShare.shared_with_id == shared_with_id
        )
        result = await db.execute(query)
        share = result.scalar_one_or_none()
        
        if not share:
            return False
        
        share.is_active = False
        await db.commit()
        
        # Registrar no histórico
        await CollaborationService.log_change(
            db,
            investigation_id=investigation_id,
            user_id=owner_id,
            action="access_revoked",
            description=f"Acesso removido do usuário ID {shared_with_id}"
        )
        
        logger.info(f"🚫 Acesso removido: Investigation {investigation_id}, User {shared_with_id}")
        
        return True
    
    @staticmethod
    async def check_permission(
        db,
        investigation_id: int,
        user_id: int,
        required_permission: PermissionLevel
    ) -> bool:
        """
        Verifica se usuário tem permissão necessária
        
        Args:
            db: Sessão do banco
            investigation_id: ID da investigação
            user_id: ID do usuário
            required_permission: Permissão necessária
            
        Returns:
            True se usuário tem permissão
        """
        from sqlalchemy import select, or_
        from app.domain.investigation import Investigation
        
        # Verificar se é o dono
        query = select(Investigation).where(Investigation.id == investigation_id)
        result = await db.execute(query)
        investigation = result.scalar_one_or_none()
        
        if investigation and investigation.user_id == user_id:
            return True  # Dono tem todas as permissões
        
        # Verificar compartilhamento
        share_query = select(InvestigationShare).where(
            InvestigationShare.investigation_id == investigation_id,
            InvestigationShare.shared_with_id == user_id,
            InvestigationShare.is_active == True,
            or_(
                InvestigationShare.expires_at.is_(None),
                InvestigationShare.expires_at > datetime.utcnow()
            )
        )
        share_result = await db.execute(share_query)
        share = share_result.scalar_one_or_none()
        
        if not share:
            return False
        
        # Hierarquia de permissões
        permission_hierarchy = {
            PermissionLevel.VIEW: 1,
            PermissionLevel.COMMENT: 2,
            PermissionLevel.EDIT: 3,
            PermissionLevel.ADMIN: 4
        }
        
        user_level = permission_hierarchy.get(PermissionLevel(share.permission), 0)
        required_level = permission_hierarchy.get(required_permission, 0)
        
        return user_level >= required_level
    
    @staticmethod
    async def add_comment(
        db,
        investigation_id: int,
        user_id: int,
        content: str,
        parent_id: Optional[int] = None,
        is_internal: bool = False
    ) -> InvestigationComment:
        """
        Adiciona comentário ou anotação
        
        Args:
            db: Sessão do banco
            investigation_id: ID da investigação
            user_id: ID do usuário
            content: Conteúdo do comentário
            parent_id: ID do comentário pai (para respostas)
            is_internal: Se é anotação privada
            
        Returns:
            InvestigationComment criado
        """
        comment = InvestigationComment(
            investigation_id=investigation_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id,
            is_internal=is_internal,
            created_at=datetime.utcnow()
        )
        
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        
        logger.info(f"💬 Comentário adicionado: Investigation {investigation_id}, User {user_id}")
        
        return comment
    
    @staticmethod
    async def log_change(
        db,
        investigation_id: int,
        user_id: Optional[int],
        action: str,
        field_changed: Optional[str] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> InvestigationChangeLog:
        """
        Registra alteração no histórico
        
        Args:
            db: Sessão do banco
            investigation_id: ID da investigação
            user_id: ID do usuário (None para sistema)
            action: Ação realizada
            field_changed: Campo alterado
            old_value: Valor anterior
            new_value: Novo valor
            description: Descrição da mudança
            ip_address: IP do usuário
            user_agent: User agent
            
        Returns:
            InvestigationChangeLog criado
        """
        log = InvestigationChangeLog(
            investigation_id=investigation_id,
            user_id=user_id,
            action=action,
            field_changed=field_changed,
            old_value=old_value,
            new_value=new_value,
            description=description,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(log)
        await db.commit()
        await db.refresh(log)
        
        return log
    
    @staticmethod
    async def get_shared_investigations(
        db,
        user_id: int,
        include_owned: bool = False
    ) -> List[dict]:
        """
        Retorna investigações compartilhadas com o usuário
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            include_owned: Se deve incluir investigações próprias
            
        Returns:
            Lista de investigações com permissões
        """
        from sqlalchemy import select, or_
        from app.domain.investigation import Investigation
        
        # Investigações compartilhadas
        query = select(Investigation, InvestigationShare).join(
            InvestigationShare,
            Investigation.id == InvestigationShare.investigation_id
        ).where(
            InvestigationShare.shared_with_id == user_id,
            InvestigationShare.is_active == True,
            or_(
                InvestigationShare.expires_at.is_(None),
                InvestigationShare.expires_at > datetime.utcnow()
            )
        )
        
        result = await db.execute(query)
        shared_investigations = []
        
        for investigation, share in result:
            inv_dict = investigation.to_dict() if hasattr(investigation, 'to_dict') else {}
            inv_dict['permission'] = share.permission
            inv_dict['shared_by'] = share.owner_id
            inv_dict['is_shared'] = True
            shared_investigations.append(inv_dict)
        
        # Investigações próprias (se solicitado)
        if include_owned:
            owned_query = select(Investigation).where(Investigation.user_id == user_id)
            owned_result = await db.execute(owned_query)
            
            for investigation in owned_result.scalars():
                inv_dict = investigation.to_dict() if hasattr(investigation, 'to_dict') else {}
                inv_dict['permission'] = PermissionLevel.ADMIN.value
                inv_dict['is_owner'] = True
                inv_dict['is_shared'] = False
                shared_investigations.append(inv_dict)
        
        return shared_investigations


# Instância global
collaboration_service = CollaborationService()
