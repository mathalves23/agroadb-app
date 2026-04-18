"""API keys — armazena apenas hash SHA-256 da chave."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.api_key import ApiKey


def hash_api_key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ApiKeyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_active(self, user_id: int) -> List[ApiKey]:
        r = await self.db.execute(
            select(ApiKey)
            .where(ApiKey.user_id == user_id, ApiKey.revoked_at.is_(None))
            .order_by(ApiKey.created_at.desc())
        )
        return list(r.scalars().all())

    async def list_all(self, user_id: int) -> List[ApiKey]:
        r = await self.db.execute(
            select(ApiKey).where(ApiKey.user_id == user_id).order_by(ApiKey.created_at.desc())
        )
        return list(r.scalars().all())

    async def create(self, *, user_id: int, name: str, rate_limit_rpm: int) -> Tuple[ApiKey, str]:
        raw = secrets.token_urlsafe(32)
        row = ApiKey(
            user_id=user_id,
            name=name,
            key_hash=hash_api_key(raw),
            rate_limit_rpm=rate_limit_rpm,
        )
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row, raw

    async def revoke(self, user_id: int, api_key_id: int) -> Optional[str]:
        """Revoga a chave. Devolve o key_hash para limpar cache Redis, ou None."""
        r = await self.db.execute(
            select(ApiKey).where(ApiKey.id == api_key_id, ApiKey.user_id == user_id)
        )
        row = r.scalar_one_or_none()
        if not row or row.revoked_at is not None:
            return None

        kh = row.key_hash
        row.revoked_at = datetime.utcnow()
        await self.db.flush()
        return kh
