"""Links de convidado (token) para visualização só de leitura sem conta."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime
from typing import Any, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.collaboration import InvestigationGuestLink


def hash_guest_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def new_guest_token() -> str:
    return secrets.token_urlsafe(32)


async def create_guest_link(
    db: AsyncSession,
    *,
    investigation_id: int,
    created_by_id: int,
    expires_at: Optional[datetime],
    label: Optional[str],
    allow_downloads: bool,
) -> Tuple[InvestigationGuestLink, str]:
    """Persiste link e devolve (row, token_em_texto_claro)."""
    raw = new_guest_token()
    th = hash_guest_token(raw)
    row = InvestigationGuestLink(
        investigation_id=investigation_id,
        created_by_id=created_by_id,
        token_hash=th,
        label=(label or None),
        expires_at=expires_at,
        revoked_at=None,
        allow_downloads=allow_downloads,
        access_count=0,
        last_access_at=None,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row, raw


async def list_guest_links(db: AsyncSession, investigation_id: int) -> List[InvestigationGuestLink]:
    r = await db.execute(
        select(InvestigationGuestLink)
        .where(InvestigationGuestLink.investigation_id == investigation_id)
        .order_by(InvestigationGuestLink.created_at.desc())
    )
    return list(r.scalars().all())


async def get_guest_link_by_token(
    db: AsyncSession, raw_token: str
) -> Optional[InvestigationGuestLink]:
    if not raw_token or len(raw_token) < 16:
        return None
    th = hash_guest_token(raw_token.strip())
    r = await db.execute(
        select(InvestigationGuestLink).where(InvestigationGuestLink.token_hash == th)
    )
    return r.scalar_one_or_none()


async def get_guest_link_by_id(
    db: AsyncSession, investigation_id: int, link_id: int
) -> Optional[InvestigationGuestLink]:
    r = await db.execute(
        select(InvestigationGuestLink).where(
            InvestigationGuestLink.id == link_id,
            InvestigationGuestLink.investigation_id == investigation_id,
        )
    )
    return r.scalar_one_or_none()


def guest_link_is_valid(link: InvestigationGuestLink, *, now: Optional[datetime] = None) -> bool:
    now = now or datetime.utcnow()
    if link.revoked_at is not None:
        return False
    if link.expires_at is not None and link.expires_at <= now:
        return False
    return True


async def record_guest_access(db: AsyncSession, link: InvestigationGuestLink) -> None:
    link.access_count = int(link.access_count or 0) + 1
    link.last_access_at = datetime.utcnow()
    await db.commit()
    await db.refresh(link)


async def revoke_guest_link(db: AsyncSession, link: InvestigationGuestLink) -> None:
    link.revoked_at = datetime.utcnow()
    await db.commit()
