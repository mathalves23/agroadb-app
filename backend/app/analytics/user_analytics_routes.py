"""
Rotas API - Analytics de Usuário
=================================

Endpoints para analytics de usuário completo.

Autor: AgroADB Team
Data: 2026-02-05
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.api.v1.deps import require_admin
from app.analytics.user_analytics_full import UserAnalytics
from app.domain.user import User

router = APIRouter(prefix="/admin/user-analytics", tags=["User Analytics"])


@router.get("/funnel")
async def get_usage_funnel(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Funnel de uso dos usuários"""
    try:
        analytics = UserAnalytics(db)
        return await analytics.get_usage_funnel(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feature-adoption")
async def get_feature_adoption(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Adoção de features pelos usuários"""
    try:
        analytics = UserAnalytics(db)
        return await analytics.get_feature_adoption(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap")
async def get_navigation_heatmap(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Heatmap de navegação"""
    try:
        analytics = UserAnalytics(db)
        return await analytics.get_navigation_heatmap(start_date, end_date, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nps")
async def get_nps_score(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Net Promoter Score (NPS)"""
    try:
        analytics = UserAnalytics(db)
        return await analytics.get_nps_score(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/complete")
async def get_complete_user_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Analytics completo de usuário"""
    try:
        analytics = UserAnalytics(db)
        return await analytics.get_complete_user_analytics(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
