"""
Repository for Notifications
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.domain.notification import Notification, NotificationType, NotificationPriority


class NotificationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, notification_data: Dict[str, Any]) -> Notification:
        """Cria uma nova notificação"""
        notification = Notification(**notification_data)
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """Busca notificação por ID (apenas do usuário)"""
        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_user_notifications(
        self,
        user_id: int,
        include_read: bool = True,
        include_archived: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Lista notificações do usuário"""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if not include_read:
            query = query.where(Notification.is_read == False)
        
        if not include_archived:
            query = query.where(Notification.is_archived == False)
        
        # Ordenar por não lidas primeiro, depois por data
        query = query.order_by(
            Notification.is_read.asc(),
            Notification.created_at.desc()
        ).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_unread(self, user_id: int) -> int:
        """Conta notificações não lidas"""
        result = await self.db.execute(
            select(func.count(Notification.id))
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.is_archived == False
            )
        )
        return result.scalar() or 0

    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Marca notificação como lida"""
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
            .values(
                is_read=True,
                read_at=datetime.utcnow()
            )
        )
        await self.db.flush()
        return result.rowcount > 0

    async def mark_all_as_read(self, user_id: int) -> int:
        """Marca todas notificações como lidas"""
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
            .values(
                is_read=True,
                read_at=datetime.utcnow()
            )
        )
        await self.db.flush()
        return result.rowcount

    async def archive(self, notification_id: int, user_id: int) -> bool:
        """Arquiva uma notificação"""
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
            .values(is_archived=True)
        )
        await self.db.flush()
        return result.rowcount > 0

    async def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Deleta uma notificação"""
        result = await self.db.execute(
            delete(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        await self.db.flush()
        return result.rowcount > 0

    async def delete_old_notifications(self, days: int = 90) -> int:
        """Deleta notificações antigas (limpeza automática)"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            delete(Notification)
            .where(
                or_(
                    and_(
                        Notification.is_read == True,
                        Notification.created_at < cutoff_date
                    ),
                    Notification.expires_at < datetime.utcnow()
                )
            )
        )
        await self.db.flush()
        return result.rowcount

    async def get_unsent_email_notifications(self, limit: int = 100) -> List[Notification]:
        """Busca notificações que precisam ser enviadas por email"""
        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.email_sent == False,
                Notification.created_at > datetime.utcnow() - timedelta(hours=24)  # Apenas últimas 24h
            )
            .order_by(Notification.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_email_sent(self, notification_id: int) -> None:
        """Marca que o email foi enviado"""
        await self.db.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(
                email_sent=True,
                email_sent_at=datetime.utcnow()
            )
        )
        await self.db.flush()

    async def get_stats(self, user_id: int) -> Dict[str, int]:
        """Estatísticas de notificações do usuário"""
        # Total
        total_result = await self.db.execute(
            select(func.count(Notification.id))
            .where(Notification.user_id == user_id)
        )
        total = total_result.scalar() or 0
        
        # Não lidas
        unread_result = await self.db.execute(
            select(func.count(Notification.id))
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        unread = unread_result.scalar() or 0
        
        # Por tipo
        type_result = await self.db.execute(
            select(Notification.type, func.count(Notification.id))
            .where(Notification.user_id == user_id)
            .group_by(Notification.type)
        )
        by_type = {row[0]: row[1] for row in type_result.all()}
        
        return {
            "total": total,
            "unread": unread,
            "by_type": by_type
        }
