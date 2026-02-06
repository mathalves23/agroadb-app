"""
Rotas API - Relatórios Gerenciais
==================================

Endpoints para relatórios gerenciais completos.

Autor: AgroADB Team
Data: 2026-02-05
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.api.v1.deps import require_admin
from app.analytics.management_reports_full import ManagementReports
from app.domain.user import User

router = APIRouter(prefix="/admin/reports", tags=["Management Reports"])


@router.get("/roi")
async def get_roi_by_investigation(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_roi: Optional[float] = Query(None, description="ROI mínimo %"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Relatório de ROI por investigação"""
    try:
        reports = ManagementReports(db)
        return await reports.get_roi_by_investigation(start_date, end_date, min_roi)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs")
async def get_cost_per_investigation(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    group_by: Optional[str] = Query(None, regex="^(category|priority|user)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Relatório de custos por investigação"""
    try:
        reports = ManagementReports(db)
        return await reports.get_cost_per_investigation(start_date, end_date, group_by)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scraper-performance")
async def get_scraper_performance(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Relatório de performance dos scrapers"""
    try:
        reports = ManagementReports(db)
        return await reports.get_scraper_performance(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uptime")
async def get_uptime_availability(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Relatório de uptime e disponibilidade"""
    try:
        reports = ManagementReports(db)
        return await reports.get_uptime_availability(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors")
async def get_errors_and_failures(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Relatório de erros e falhas"""
    try:
        reports = ManagementReports(db)
        return await reports.get_errors_and_failures(start_date, end_date, severity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/complete")
async def get_complete_management_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Relatório gerencial completo"""
    try:
        reports = ManagementReports(db)
        return await reports.get_complete_management_report(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
