"""
Lease Contract Domain Model
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, Date, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LeaseContract(Base):
    """Lease contract model"""
    
    __tablename__ = "lease_contracts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), nullable=False, index=True)
    
    # Contract parties
    lessor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    lessor_cpf_cnpj: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    lessee_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    lessee_cpf_cnpj: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Contract details
    contract_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Property reference
    property_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    area_leased: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Financial
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    payment_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Source
    data_source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    investigation = relationship("Investigation", back_populates="lease_contracts")
    
    def __repr__(self) -> str:
        return f"<LeaseContract {self.id}>"
