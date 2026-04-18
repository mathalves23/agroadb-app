"""API v1 — analytics assíncronos (montado em /api/v1/analytics)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user, get_db
from app.domain.user import User
from app.services import analytics_application as analytics_app

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class AnalyticsOverviewResponse(BaseModel):
    """Contrato mínimo para o sumário de overview (campos estáveis)."""

    model_config = ConfigDict(extra="allow")

    users: Dict[str, Any]
    investigations: Dict[str, Any]
    period: Dict[str, Any]


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def analytics_overview(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_active_user),
):
    return await analytics_app.overview_metrics(db, start_date, end_date)


@router.get("/executive-summary")
async def analytics_executive_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Relatório executivo completo (payload alinhado ao `AnalyticsAggregator` legado)."""
    return await analytics_app.executive_summary(db, start_date, end_date)
