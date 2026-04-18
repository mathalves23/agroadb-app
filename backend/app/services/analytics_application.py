"""
Camada de aplicação async para analytics.

Delega ao legado síncrono em `app.analytics` via `AsyncSession.run_sync`, evitando
duplicar consultas SQL até uma migração completa para SQLAlchemy 2 async.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics import AnalyticsAggregator, MetricsCalculator


async def overview_metrics(
    db: AsyncSession,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    def _work(sync_sess):
        return MetricsCalculator(sync_sess).get_overview_metrics(start_date, end_date)

    return await db.run_sync(_work)


async def executive_summary(
    db: AsyncSession,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    def _work(sync_sess):
        return AnalyticsAggregator(sync_sess).generate_executive_summary(start_date, end_date)

    return await db.run_sync(_work)
