"""
Notification Service - Criação e gerenciamento de notificações
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.notification import NotificationType, NotificationPriority
from app.repositories.notification import NotificationRepository
from app.repositories.user_settings import UserSettingsRepository
from app.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço para criar e gerenciar notificações"""
    
    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        action_url: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        investigation_id: Optional[int] = None,
        send_email: bool = True
    ) -> Dict[str, Any]:
        """
        Cria uma notificação e opcionalmente envia email
        """
        notification_repo = NotificationRepository(db)
        settings_repo = UserSettingsRepository(db)
        
        # Verificar preferências do usuário
        should_send_email = False
        if send_email:
            email_pref = await settings_repo.get_config(user_id, f"email_{type.value}")
            should_send_email = email_pref != "false"  # Default é true
        
        # Criar notificação no banco
        notification_data = {
            "user_id": user_id,
            "type": type,
            "title": title,
            "message": message,
            "priority": priority,
            "action_url": action_url,
            "icon": icon or NotificationService._get_default_icon(type),
            "color": color or NotificationService._get_default_color(type),
            "investigation_id": investigation_id
        }
        
        notification = await notification_repo.create(notification_data)
        
        # Enviar email se necessário
        if should_send_email:
            try:
                # Buscar email do usuário
                from app.repositories.user import UserRepository
                user_repo = UserRepository(db)
                user = await user_repo.get(user_id)
                
                if user and user.email:
                    await EmailService.send_notification_email(
                        to_email=user.email,
                        user_name=user.full_name,
                        notification_type=type,
                        title=title,
                        message=message,
                        action_url=action_url
                    )
                    await notification_repo.mark_email_sent(notification.id)
            except Exception as e:
                logger.error(f"Erro ao enviar email de notificação: {e}")
        
        return {
            "id": notification.id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "created_at": notification.created_at.isoformat(),
            "is_read": notification.is_read
        }
    
    @staticmethod
    def _get_default_icon(type: NotificationType) -> str:
        """Retorna ícone padrão para cada tipo"""
        icons = {
            NotificationType.INVESTIGATION_CREATED: "FileText",
            NotificationType.INVESTIGATION_SHARED: "Share2",
            NotificationType.INVESTIGATION_COMMENT: "MessageSquare",
            NotificationType.INVESTIGATION_UPDATED: "RefreshCw",
            NotificationType.REPORT_READY: "FileCheck",
            NotificationType.QUERY_COMPLETED: "CheckCircle",
            NotificationType.SYSTEM_UPDATE: "Bell",
            NotificationType.ALERT: "AlertTriangle"
        }
        return icons.get(type, "Bell")
    
    @staticmethod
    def _get_default_color(type: NotificationType) -> str:
        """Retorna cor padrão para cada tipo"""
        colors = {
            NotificationType.INVESTIGATION_CREATED: "blue",
            NotificationType.INVESTIGATION_SHARED: "purple",
            NotificationType.INVESTIGATION_COMMENT: "green",
            NotificationType.INVESTIGATION_UPDATED: "indigo",
            NotificationType.REPORT_READY: "emerald",
            NotificationType.QUERY_COMPLETED: "teal",
            NotificationType.SYSTEM_UPDATE: "gray",
            NotificationType.ALERT: "red"
        }
        return colors.get(type, "gray")
    
    @staticmethod
    async def notify_investigation_created(
        db: AsyncSession,
        user_id: int,
        investigation_id: int,
        investigation_name: str
    ):
        """Notifica sobre nova investigação criada"""
        await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.INVESTIGATION_CREATED,
            title="Nova Investigação Criada",
            message=f'Investigação "{investigation_name}" foi criada com sucesso.',
            action_url=f"/investigations/{investigation_id}",
            investigation_id=investigation_id,
            send_email=True
        )
    
    @staticmethod
    async def notify_investigation_shared(
        db: AsyncSession,
        user_id: int,
        investigation_id: int,
        investigation_name: str,
        shared_by: str
    ):
        """Notifica sobre investigação compartilhada"""
        await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.INVESTIGATION_SHARED,
            title="Investigação Compartilhada",
            message=f'{shared_by} compartilhou "{investigation_name}" com você.',
            action_url=f"/investigations/{investigation_id}",
            investigation_id=investigation_id,
            priority=NotificationPriority.HIGH,
            send_email=True
        )
    
    @staticmethod
    async def notify_report_ready(
        db: AsyncSession,
        user_id: int,
        investigation_id: int,
        investigation_name: str,
        report_type: str
    ):
        """Notifica sobre relatório pronto"""
        await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.REPORT_READY,
            title="Relatório Disponível",
            message=f'Relatório de {report_type} para "{investigation_name}" está pronto.',
            action_url=f"/investigations/{investigation_id}",
            investigation_id=investigation_id,
            priority=NotificationPriority.HIGH,
            send_email=True
        )
    
    @staticmethod
    async def notify_query_completed(
        db: AsyncSession,
        user_id: int,
        investigation_id: int,
        provider: str,
        result_count: int
    ):
        """Notifica sobre consulta concluída"""
        await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.QUERY_COMPLETED,
            title="Consulta Concluída",
            message=f'Consulta em {provider} retornou {result_count} resultado(s).',
            action_url=f"/investigations/{investigation_id}",
            investigation_id=investigation_id,
            send_email=False  # Não enviar email para cada consulta
        )
    
    @staticmethod
    async def notify_comment_added(
        db: AsyncSession,
        user_id: int,
        investigation_id: int,
        investigation_name: str,
        commenter_name: str
    ):
        """Notifica sobre novo comentário"""
        await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.INVESTIGATION_COMMENT,
            title="Novo Comentário",
            message=f'{commenter_name} comentou em "{investigation_name}".',
            action_url=f"/investigations/{investigation_id}",
            investigation_id=investigation_id,
            send_email=True
        )
