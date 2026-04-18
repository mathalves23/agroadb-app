"""
Materialized views PostgreSQL para agregações de dashboard.
Em SQLite / testes, as operações são ignoradas com segurança.
"""
from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

MV_NAME = "mv_dashboard_investigation_summary"


async def try_refresh_investigation_summary(db: AsyncSession) -> bool:
    """
    REFRESH MATERIALIZED VIEW no PostgreSQL.
    Retorna True se o refresh foi executado.
    """
    bind = db.get_bind()
    if bind.dialect.name != "postgresql":
        return False
    try:
        await db.execute(text(f"REFRESH MATERIALIZED VIEW {MV_NAME}"))
        logger.info("Materialized view %s atualizada", MV_NAME)
        return True
    except Exception as exc:
        logger.warning("Refresh MV ignorado ou falhou: %s", exc)
        return False


