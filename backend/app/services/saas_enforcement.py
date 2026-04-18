"""
Limites SaaS por organização (trial / plano) — aplicação em criação de recursos.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.investigation import Investigation
from app.repositories.organization import OrganizationRepository

logger = logging.getLogger(__name__)


async def _primary_org_subscription(
    db: AsyncSession, user_id: int
) -> Tuple[Optional[int], Optional[Dict[str, Any]]]:
    """Primeira organização do utilizador e limites da subscrição (se existir)."""
    orgs = await OrganizationRepository(db).list_for_user(user_id)
    if not orgs:
        return None, None
    org = orgs[0]
    sub = org.subscription
    if not sub:
        return org.id, None
    return org.id, sub.limits or {}


async def count_user_investigations(db: AsyncSession, user_id: int) -> int:
    r = await db.execute(select(func.count()).select_from(Investigation).where(Investigation.user_id == user_id))
    return int(r.scalar_one() or 0)


async def assert_can_create_investigation(db: AsyncSession, user_id: int) -> None:
    """
    Levanta HTTPException 403 se o limite do plano for excedido.
    Sem organização associada, não aplica limite (compatibilidade).
    """
    from fastapi import HTTPException, status

    _, limits = await _primary_org_subscription(db, user_id)
    if not limits:
        return
    max_inv = limits.get("max_investigations")
    if max_inv is None:
        return
    try:
        cap = int(max_inv)
    except (TypeError, ValueError):
        return
    current = await count_user_investigations(db, user_id)
    if current >= cap:
        logger.warning("Limite de investigações atingido: user=%s cap=%s", user_id, cap)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "plan_limit",
                "message": f"Limite de investigações do plano atingido ({cap}). Atualize a subscrição.",
            },
        )
