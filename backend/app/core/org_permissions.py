"""RBAC grosso ao nível da organização (papéis por membro)."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.organization import OrganizationMember

_ROLE_ORDER = {"billing": 1, "member": 2, "admin": 3, "owner": 4}


def role_at_least(role: Optional[str], minimum: str) -> bool:
    if not role:
        return False
    return _ROLE_ORDER.get(role, 0) >= _ROLE_ORDER.get(minimum, 99)


async def get_member_role(db: AsyncSession, user_id: int, organization_id: int) -> Optional[str]:
    r = await db.execute(
        select(OrganizationMember.role).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == organization_id,
        )
    )
    row = r.one_or_none()
    return row[0] if row else None


async def require_org_any_role(
    db: AsyncSession,
    user_id: int,
    organization_id: int,
    allowed: frozenset[str],
) -> str:
    """Exige que o utilizador pertença à organização com um dos papéis indicados."""
    from fastapi import HTTPException, status

    role = await get_member_role(db, user_id, organization_id)
    if role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão nesta organização.",
        )
    return role


async def require_org_role(
    db: AsyncSession, user_id: int, organization_id: int, minimum: str
) -> str:
    from fastapi import HTTPException, status

    role = await get_member_role(db, user_id, organization_id)
    if not role_at_least(role, minimum):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente nesta organização.",
        )
    return role
