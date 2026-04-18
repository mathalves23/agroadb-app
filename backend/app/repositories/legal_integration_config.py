"""Persistência de configurações de integração jurídica."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.legal_integration_config import LegalIntegrationConfig


class LegalIntegrationConfigRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_user(self, user_id: int) -> List[LegalIntegrationConfig]:
        r = await self.db.execute(
            select(LegalIntegrationConfig)
            .where(LegalIntegrationConfig.user_id == user_id)
            .order_by(LegalIntegrationConfig.system_name)
        )
        return list(r.scalars().all())

    async def get_by_user_and_system(
        self, user_id: int, system_name: str
    ) -> Optional[LegalIntegrationConfig]:
        r = await self.db.execute(
            select(LegalIntegrationConfig).where(
                LegalIntegrationConfig.user_id == user_id,
                LegalIntegrationConfig.system_name == system_name,
            )
        )
        return r.scalar_one_or_none()

    async def upsert(
        self,
        *,
        user_id: int,
        system_name: str,
        api_endpoint: str,
        api_key_encrypted: Optional[str],
        credentials: Optional[dict],
        enabled: bool,
    ) -> LegalIntegrationConfig:
        row = await self.get_by_user_and_system(user_id, system_name)
        if row:
            row.api_endpoint = api_endpoint
            if api_key_encrypted is not None:
                row.api_key_encrypted = api_key_encrypted
            if credentials is not None:
                row.credentials = credentials
            row.enabled = enabled
            await self.db.flush()
            await self.db.refresh(row)
            return row
        row = LegalIntegrationConfig(
            user_id=user_id,
            system_name=system_name,
            api_endpoint=api_endpoint,
            api_key_encrypted=api_key_encrypted,
            credentials=credentials,
            enabled=enabled,
        )
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row
