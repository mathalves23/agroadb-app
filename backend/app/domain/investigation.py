"""
Investigation Domain Model
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InvestigationStatus(str, Enum):
    """Investigation status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Investigation(Base):
    """Investigation model"""
    
    __tablename__ = "investigations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Target info
    target_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_cpf_cnpj: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    target_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Investigation details
    status: Mapped[InvestigationStatus] = mapped_column(
        SQLEnum(InvestigationStatus), default=InvestigationStatus.PENDING, nullable=False
    )
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Results summary
    properties_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lease_contracts_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    companies_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="investigations")
    properties = relationship("Property", back_populates="investigation", cascade="all, delete-orphan")
    lease_contracts = relationship("LeaseContract", back_populates="investigation", cascade="all, delete-orphan")
    companies = relationship("Company", back_populates="investigation", cascade="all, delete-orphan")
    shares = relationship("InvestigationShare", back_populates="investigation", cascade="all, delete-orphan")
    comments = relationship("InvestigationComment", back_populates="investigation", cascade="all, delete-orphan")
    change_logs = relationship("InvestigationChangeLog", back_populates="investigation", cascade="all, delete-orphan")
    legal_queries = relationship("LegalQuery", back_populates="investigation", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Investigation {self.id} - {self.target_name}>"
