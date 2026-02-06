"""
Property Domain Model
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Property(Base):
    """Property (rural or urban) model"""
    
    __tablename__ = "properties"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), nullable=False, index=True)
    
    # Property identification
    car_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    ccir_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    matricula: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Property details
    property_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    area_hectares: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Location
    state: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Geolocation (GeoJSON format)
    coordinates: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Ownership
    owner_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    owner_cpf_cnpj: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Additional info
    data_source: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    investigation = relationship("Investigation", back_populates="properties")
    
    def __repr__(self) -> str:
        return f"<Property {self.property_name or self.car_number}>"
