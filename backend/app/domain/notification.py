"""
Notification Model - Sistema de notificações do usuário
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Tipos de notificações"""
    INVESTIGATION_CREATED = "investigation_created"
    INVESTIGATION_SHARED = "investigation_shared"
    INVESTIGATION_COMMENT = "investigation_comment"
    INVESTIGATION_UPDATED = "investigation_updated"
    REPORT_READY = "report_ready"
    QUERY_COMPLETED = "query_completed"
    SYSTEM_UPDATE = "system_update"
    ALERT = "alert"


class NotificationPriority(str, enum.Enum):
    """Prioridade da notificação"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """Notificações do usuário"""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Conteúdo
    type = Column(Enum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.NORMAL)
    
    # Metadados
    action_url = Column(String(500), nullable=True)  # Link para ação
    icon = Column(String(50), nullable=True)  # Nome do ícone (lucide-react)
    color = Column(String(50), nullable=True)  # Cor do tema (blue, green, red, etc)
    
    # Referências (opcional)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    
    # Estado
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    # Email
    email_sent = Column(Boolean, default=False, nullable=False)
    email_sent_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True)  # Notificações podem expirar
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    investigation = relationship("Investigation", foreign_keys=[investigation_id])
    
    def __repr__(self):
        return f"<Notification {self.id} - {self.type} - {'Read' if self.is_read else 'Unread'}>"
