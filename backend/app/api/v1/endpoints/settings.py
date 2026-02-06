"""
Settings API Endpoints - Gerenciamento de configurações de usuário
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.domain.user import User
from app.repositories.user_settings import UserSettingsRepository

router = APIRouter(prefix="/settings", tags=["settings"])


class IntegrationConfigsRequest(BaseModel):
    """Request para salvar configurações de integrações"""
    configs: Dict[str, str]


class IntegrationConfigsResponse(BaseModel):
    """Response com configurações (keys mascaradas)"""
    configs: Dict[str, str]


@router.get("/integrations", response_model=Dict[str, str])
async def get_integration_configs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna as configurações de integrações do usuário
    Keys são mascaradas para segurança (apenas últimos 4 caracteres visíveis)
    """
    repo = UserSettingsRepository(db)
    configs = await repo.get_integration_configs(current_user.id)
    
    # Mascarar keys para segurança (mostrar apenas últimos 4 chars)
    masked_configs = {}
    for key, value in configs.items():
        if value and len(value) > 4:
            masked_configs[key] = '*' * (len(value) - 4) + value[-4:]
        else:
            masked_configs[key] = value
    
    return masked_configs


@router.post("/integrations")
async def save_integration_configs(
    configs: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Salva as configurações de integrações do usuário
    Apenas valores não vazios e não mascarados são salvos
    """
    repo = UserSettingsRepository(db)
    
    # Filtrar apenas keys que não estão mascaradas
    configs_to_save = {}
    for key, value in configs.items():
        if value and not value.startswith('*'):
            configs_to_save[key] = value.strip()
    
    await repo.save_integration_configs(current_user.id, configs_to_save)
    
    return {"message": "Configurações salvas com sucesso", "count": len(configs_to_save)}


@router.delete("/integrations/{key}")
async def delete_integration_config(
    key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove uma configuração específica"""
    repo = UserSettingsRepository(db)
    await repo.delete_integration_config(current_user.id, key)
    return {"message": f"Configuração {key} removida"}
