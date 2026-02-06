"""
Investigation Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.domain.investigation import InvestigationStatus
from app.core.validators import limpar_documento, validar_cpf, validar_cnpj


def _validar_cpf_cnpj(v: Optional[str]) -> Optional[str]:
    """Limpa e valida um campo CPF/CNPJ. Retorna o documento limpo ou None."""
    if v is None:
        return None
    cleaned = limpar_documento(v)
    if not cleaned:
        return None
    if len(cleaned) == 11:
        if not validar_cpf(cleaned):
            raise ValueError("CPF inválido — dígitos verificadores não conferem")
        return cleaned
    elif len(cleaned) == 14:
        if not validar_cnpj(cleaned):
            raise ValueError("CNPJ inválido — dígitos verificadores não conferem")
        return cleaned
    else:
        raise ValueError(
            "Documento deve conter 11 dígitos (CPF) ou 14 dígitos (CNPJ)"
        )


class InvestigationBase(BaseModel):
    """Base investigation schema"""
    target_name: str = Field(..., min_length=1, max_length=255)
    target_cpf_cnpj: Optional[str] = Field(None, max_length=20)
    target_description: Optional[str] = None
    priority: int = Field(1, ge=1, le=5)

    @field_validator("target_cpf_cnpj", mode="before")
    @classmethod
    def validate_target_cpf_cnpj(cls, v: Optional[str]) -> Optional[str]:
        return _validar_cpf_cnpj(v)


class InvestigationCreate(InvestigationBase):
    """Schema for creating an investigation"""
    pass


class InvestigationUpdate(BaseModel):
    """Schema for updating an investigation"""
    target_name: Optional[str] = Field(None, min_length=1, max_length=255)
    target_cpf_cnpj: Optional[str] = Field(None, max_length=20)
    target_description: Optional[str] = None
    status: Optional[InvestigationStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

    @field_validator("target_cpf_cnpj", mode="before")
    @classmethod
    def validate_target_cpf_cnpj(cls, v: Optional[str]) -> Optional[str]:
        return _validar_cpf_cnpj(v)


class InvestigationResponse(BaseModel):
    """Schema for investigation response"""
    id: int
    user_id: int
    target_name: str
    target_cpf_cnpj: Optional[str] = None
    target_description: Optional[str] = None
    priority: int
    status: InvestigationStatus
    properties_found: int
    lease_contracts_found: int
    companies_found: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class InvestigationListResponse(BaseModel):
    """Schema for paginated investigation list"""
    items: list[InvestigationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
