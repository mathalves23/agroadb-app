"""
Company Domain Model
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Company(Base):
    """Company model"""
    
    __tablename__ = "companies"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), nullable=False, index=True)
    
    # Company identification
    cnpj: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    corporate_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    trade_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    opening_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Location
    state: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Business info
    main_activity: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    legal_nature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    capital: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Related people
    partners: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Source
    data_source: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    investigation = relationship("Investigation", back_populates="companies")
    
    def __repr__(self) -> str:
        return f"<Company {self.cnpj}>"
