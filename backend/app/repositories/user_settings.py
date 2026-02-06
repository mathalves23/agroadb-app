"""
Repository for UserSettings
"""
from typing import Dict, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user_setting import UserSetting


class UserSettingsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_integration_configs(self, user_id: int) -> Dict[str, str]:
        """Retorna todas as configurações de integração do usuário"""
        result = await self.db.execute(
            select(UserSetting)
            .where(
                UserSetting.user_id == user_id,
                UserSetting.category == "integration"
            )
        )
        settings = result.scalars().all()
        return {s.key: s.value for s in settings if s.value}

    async def save_integration_configs(self, user_id: int, configs: Dict[str, str]) -> None:
        """Salva ou atualiza múltiplas configurações de integração"""
        for key, value in configs.items():
            # Verifica se já existe
            result = await self.db.execute(
                select(UserSetting)
                .where(
                    UserSetting.user_id == user_id,
                    UserSetting.key == key,
                    UserSetting.category == "integration"
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Atualiza
                existing.value = value
            else:
                # Cria novo
                setting = UserSetting(
                    user_id=user_id,
                    key=key,
                    value=value,
                    category="integration"
                )
                self.db.add(setting)
        
        await self.db.flush()

    async def get_config(self, user_id: int, key: str) -> Optional[str]:
        """Retorna uma configuração específica"""
        result = await self.db.execute(
            select(UserSetting)
            .where(
                UserSetting.user_id == user_id,
                UserSetting.key == key,
                UserSetting.category == "integration"
            )
        )
        setting = result.scalar_one_or_none()
        return setting.value if setting else None

    async def delete_integration_config(self, user_id: int, key: str) -> None:
        """Remove uma configuração específica"""
        await self.db.execute(
            delete(UserSetting)
            .where(
                UserSetting.user_id == user_id,
                UserSetting.key == key,
                UserSetting.category == "integration"
            )
        )
        await self.db.flush()

    async def get_all_settings(self, user_id: int) -> Dict[str, Dict[str, str]]:
        """Retorna todas as configurações agrupadas por categoria"""
        result = await self.db.execute(
            select(UserSetting).where(UserSetting.user_id == user_id)
        )
        settings = result.scalars().all()
        
        grouped: Dict[str, Dict[str, str]] = {}
        for setting in settings:
            if setting.category not in grouped:
                grouped[setting.category] = {}
            grouped[setting.category][setting.key] = setting.value
        
        return grouped
