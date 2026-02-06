"""
Property Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PropertyBase(BaseModel):
    """Base property schema"""
    car_number: Optional[str] = Field(None, max_length=100)
    ccir_number: Optional[str] = Field(None, max_length=100)
    matricula: Optional[str] = Field(None, max_length=100)
    property_name: Optional[str] = Field(None, max_length=255)
    area_hectares: Optional[float] = Field(None, ge=0)
    state: Optional[str] = Field(None, max_length=2)
    city: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    coordinates: Optional[dict] = None
    owner_name: Optional[str] = Field(None, max_length=255)
    owner_cpf_cnpj: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


class PropertyCreate(PropertyBase):
    """Schema for creating a property"""
    data_source: str = Field(..., max_length=100)
    raw_data: Optional[dict] = None


class PropertyResponse(PropertyBase):
    """Schema for property response"""
    id: int
    investigation_id: int
    data_source: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeaseContractBase(BaseModel):
    """Base lease contract schema"""
    lessor_name: Optional[str] = Field(None, max_length=255)
    lessor_cpf_cnpj: Optional[str] = Field(None, max_length=20)
    lessee_name: Optional[str] = Field(None, max_length=255)
    lessee_cpf_cnpj: Optional[str] = Field(None, max_length=20)
    property_description: Optional[str] = None
    area_leased: Optional[float] = Field(None, ge=0)
    value: Optional[float] = Field(None, ge=0)


class LeaseContractCreate(LeaseContractBase):
    """Schema for creating a lease contract"""
    data_source: str = Field(..., max_length=100)
    raw_data: Optional[dict] = None


class LeaseContractResponse(LeaseContractBase):
    """Schema for lease contract response"""
    id: int
    investigation_id: int
    data_source: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CompanyBase(BaseModel):
    """Base company schema"""
    cnpj: str = Field(..., max_length=20)
    corporate_name: Optional[str] = Field(None, max_length=255)
    trade_name: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=2)
    city: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    main_activity: Optional[str] = Field(None, max_length=500)


class CompanyCreate(CompanyBase):
    """Schema for creating a company"""
    data_source: str = Field(..., max_length=100)
    raw_data: Optional[dict] = None


class CompanyResponse(CompanyBase):
    """Schema for company response"""
    id: int
    investigation_id: int
    data_source: str
    partners: Optional[dict]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
