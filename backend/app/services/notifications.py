"""
Sistema de Notificações In-App
Notificações em tempo real dentro da plataforma
"""
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy import JSON
import logging

from app.core.database import Base

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Tipos de notificações"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationCategory(str, Enum):
    """Categorias de notificações"""
    INVESTIGATION = "investigation"
    SYSTEM = "system"
    SECURITY = "security"
    LGPD = "lgpd"
    BILLING = "billing"


class InAppNotification(Base):
    """
    Modelo de Notificação In-App
    
    Notificações exibidas dentro da plataforma
    """
    __tablename__ = "in_app_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(20), nullable=False)  # info, success, warning, error
    category = Column(String(50), nullable=False)  # investigation, system, etc
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    action_url = Column(String(500), nullable=True)  # URL para ação (opcional)
    action_label = Column(String(100), nullable=True)  # Label do botão (opcional)
    extra_data = Column(JSON, nullable=True)  # Dados adicionais (renomeado de 'metadata' para evitar conflito com SQLAlchemy)
    read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "category": self.category,
            "title": self.title,
            "message": self.message,
            "action_url": self.action_url,
            "action_label": self.action_label,
            "metadata": self.metadata,
            "read": self.read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None
        }


class NotificationService:
    """
    Serviço de Notificações In-App
    """
    
    @staticmethod
    async def create_notification(
        db,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        category: NotificationCategory = NotificationCategory.SYSTEM,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> InAppNotification:
        """
        Cria uma notificação in-app
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            title: Título da notificação
            message: Mensagem
            notification_type: Tipo (info, success, warning, error)
            category: Categoria
            action_url: URL para ação (opcional)
            action_label: Label do botão (opcional)
            metadata: Dados adicionais (opcional)
            
        Returns:
            Notificação criada
        """
        notification = InAppNotification(
            user_id=user_id,
            type=notification_type.value,
            category=category.value,
            title=title,
            message=message,
            action_url=action_url,
            action_label=action_label,
            metadata=metadata,
            read=False,
            created_at=datetime.utcnow()
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        logger.info(f"📬 Notificação criada para usuário {user_id}: {title}")
        
        return notification
    
    @staticmethod
    async def get_user_notifications(
        db,
        user_id: int,
        unread_only: bool = False,
        category: Optional[NotificationCategory] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[InAppNotification], int]:
        """
        Retorna notificações do usuário
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            unread_only: Apenas não lidas
            category: Filtrar por categoria
            limit: Limite de resultados
            offset: Offset para paginação
            
        Returns:
            Tupla (notificações, total_count)
        """
        from sqlalchemy import select, desc, func
        
        # Query base
        query = select(InAppNotification).where(InAppNotification.user_id == user_id)
        count_query = select(func.count(InAppNotification.id)).where(
            InAppNotification.user_id == user_id
        )
        
        # Filtros
        if unread_only:
            query = query.where(InAppNotification.read == False)
            count_query = count_query.where(InAppNotification.read == False)
        
        if category:
            query = query.where(InAppNotification.category == category.value)
            count_query = count_query.where(InAppNotification.category == category.value)
        
        # Ordenar e paginar
        query = query.order_by(desc(InAppNotification.created_at)).limit(limit).offset(offset)
        
        # Executar queries
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return notifications, total_count
    
    @staticmethod
    async def mark_as_read(db, notification_id: int, user_id: int) -> bool:
        """
        Marca notificação como lida
        
        Args:
            db: Sessão do banco
            notification_id: ID da notificação
            user_id: ID do usuário (para validação)
            
        Returns:
            True se marcado com sucesso
        """
        from sqlalchemy import select, update
        
        # Verificar se notificação existe e pertence ao usuário
        query = select(InAppNotification).where(
            InAppNotification.id == notification_id,
            InAppNotification.user_id == user_id
        )
        result = await db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
        
        # Marcar como lida
        notification.read = True
        notification.read_at = datetime.utcnow()
        
        await db.commit()
        
        return True
    
    @staticmethod
    async def mark_all_as_read(db, user_id: int) -> int:
        """
        Marca todas as notificações como lidas
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            
        Returns:
            Número de notificações marcadas
        """
        from sqlalchemy import update
        
        query = update(InAppNotification).where(
            InAppNotification.user_id == user_id,
            InAppNotification.read == False
        ).values(
            read=True,
            read_at=datetime.utcnow()
        )
        
        result = await db.execute(query)
        await db.commit()
        
        return result.rowcount
    
    @staticmethod
    async def delete_notification(db, notification_id: int, user_id: int) -> bool:
        """
        Deleta uma notificação
        
        Args:
            db: Sessão do banco
            notification_id: ID da notificação
            user_id: ID do usuário (para validação)
            
        Returns:
            True se deletado com sucesso
        """
        from sqlalchemy import select, delete
        
        # Verificar se notificação existe e pertence ao usuário
        query = select(InAppNotification).where(
            InAppNotification.id == notification_id,
            InAppNotification.user_id == user_id
        )
        result = await db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
        
        # Deletar
        await db.delete(notification)
        await db.commit()
        
        return True
    
    @staticmethod
    async def get_unread_count(db, user_id: int) -> int:
        """
        Retorna contagem de notificações não lidas
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            
        Returns:
            Número de notificações não lidas
        """
        from sqlalchemy import select, func
        
        query = select(func.count(InAppNotification.id)).where(
            InAppNotification.user_id == user_id,
            InAppNotification.read == False
        )
        
        result = await db.execute(query)
        return result.scalar()
    
    # Helpers para notificações específicas
    
    @staticmethod
    async def notify_investigation_completed(
        db,
        user_id: int,
        investigation_id: str,
        investigation_name: str,
        total_results: int
    ):
        """Notifica conclusão de investigação"""
        return await NotificationService.create_notification(
            db,
            user_id=user_id,
            title="✅ Investigação Concluída",
            message=f"A investigação '{investigation_name}' foi concluída com {total_results} resultados.",
            notification_type=NotificationType.SUCCESS,
            category=NotificationCategory.INVESTIGATION,
            action_url=f"/investigations/{investigation_id}",
            action_label="Ver Resultados",
            metadata={
                "investigation_id": investigation_id,
                "investigation_name": investigation_name,
                "total_results": total_results
            }
        )
    
    @staticmethod
    async def notify_investigation_failed(
        db,
        user_id: int,
        investigation_id: str,
        investigation_name: str,
        error: str
    ):
        """Notifica falha na investigação"""
        return await NotificationService.create_notification(
            db,
            user_id=user_id,
            title="❌ Erro na Investigação",
            message=f"Ocorreu um erro ao processar '{investigation_name}': {error}",
            notification_type=NotificationType.ERROR,
            category=NotificationCategory.INVESTIGATION,
            action_url=f"/investigations/{investigation_id}",
            action_label="Ver Detalhes",
            metadata={
                "investigation_id": investigation_id,
                "investigation_name": investigation_name,
                "error": error
            }
        )
    
    @staticmethod
    async def notify_2fa_enabled(db, user_id: int):
        """Notifica ativação de 2FA"""
        return await NotificationService.create_notification(
            db,
            user_id=user_id,
            title="🔒 2FA Ativado",
            message="Autenticação de dois fatores foi ativada na sua conta.",
            notification_type=NotificationType.SUCCESS,
            category=NotificationCategory.SECURITY,
            action_url="/settings/security",
            action_label="Ver Configurações"
        )
    
    @staticmethod
    async def notify_data_deletion_requested(db, user_id: int, request_id: int):
        """Notifica solicitação de exclusão de dados"""
        return await NotificationService.create_notification(
            db,
            user_id=user_id,
            title="📋 Solicitação de Exclusão Registrada",
            message="Sua solicitação de exclusão de dados foi registrada e será processada em até 15 dias úteis.",
            notification_type=NotificationType.INFO,
            category=NotificationCategory.LGPD,
            metadata={"request_id": request_id}
        )


# Instância global
notification_service = NotificationService()
