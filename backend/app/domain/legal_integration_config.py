"""
Configurações persistidas de integrações jurídicas por utilizador.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LegalIntegrationConfig(Base):
    __tablename__ = "legal_integration_configs"
    __table_args__ = (UniqueConstraint("user_id", "system_name", name="uq_legal_config_user_system"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    system_name: Mapped[str] = mapped_column(String(120), nullable=False)
    api_endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    api_key_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    credentials: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user = relationship("User", back_populates="legal_integration_configs")
