"""
Collaboration Domain Models
InvestigationShare, InvestigationComment, InvestigationChangeLog
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, UniqueConstraint
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class PermissionLevel(str, Enum):
    """Níveis de permissão para compartilhamento"""
    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    ADMIN = "admin"


class InvestigationShare(Base):
    """Modelo de Compartilhamento de Investigação"""
    __tablename__ = "investigation_shares"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    shared_with_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission = Column(String(20), nullable=False, default=PermissionLevel.VIEW.value)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    investigation = relationship("Investigation", back_populates="shares")
    owner = relationship("User", foreign_keys=[owner_id])
    shared_with = relationship("User", foreign_keys=[shared_with_id])

    __table_args__ = (
        UniqueConstraint('investigation_id', 'shared_with_id', name='uq_investigation_share'),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "investigation_id": self.investigation_id,
            "owner_id": self.owner_id,
            "shared_with_id": self.shared_with_id,
            "shared_with_email": self.shared_with.email if self.shared_with else None,
            "shared_with_name": self.shared_with.full_name if self.shared_with else None,
            "permission": self.permission,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
        }


class InvestigationComment(Base):
    """Modelo de Comentário em Investigação"""
    __tablename__ = "investigation_comments"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("investigation_comments.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, nullable=True)
    is_edited = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    investigation = relationship("Investigation", back_populates="comments")
    user = relationship("User")
    replies = relationship("InvestigationComment", backref="parent", remote_side=[id])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "investigation_id": self.investigation_id,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else "Usuário Desconhecido",
            "user_email": self.user.email if self.user else None,
            "parent_id": self.parent_id,
            "content": self.content if not self.is_deleted else "[Comentário deletado]",
            "is_internal": self.is_internal,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_edited": self.is_edited,
            "is_deleted": self.is_deleted,
            "replies_count": len(self.replies) if self.replies else 0,
        }


class InvestigationChangeLog(Base):
    """Modelo de Histórico de Alterações"""
    __tablename__ = "investigation_change_logs"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(50), nullable=False)
    field_changed = Column(String(100), nullable=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    investigation = relationship("Investigation", back_populates="change_logs")
    user = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "investigation_id": self.investigation_id,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else "Sistema",
            "user_email": self.user.email if self.user else None,
            "action": self.action,
            "field_changed": self.field_changed,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "ip_address": self.ip_address,
        }
