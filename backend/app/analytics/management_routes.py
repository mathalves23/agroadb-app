"""
API Endpoints - Management Reports

Endpoints REST para os relatórios gerenciais avançados.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user, require_role
from app.domain.user import User

# Importar classes consolidadas
from app.analytics.management_reports_consolidated import (
    ROIReport,
    CostReport,
    ScraperPerformanceReport,
    UptimeReport,
    ErrorReport,
    ManagementReportsConsolidator
)

router = APIRouter(prefix="/api/analytics/management", tags=["Management Reports"])


# ============================================================================
# ROI REPORTS
# ============================================================================

@router.get("/roi")
async def get_roi_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_roi: Optional[float] = Query(None, description="ROI mínimo (%)"),
    max_roi: Optional[float] = Query(None, description="ROI máximo (%)"),
    user_id: Optional[int] = Query(None, description="Filtrar por usuário"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "finance", "executive"]))
):
    """
    Relatório de ROI por Investigação
    
    Calcula retorno sobre investimento de cada investigação.
    
    **Requer: admin, finance ou executive**
    """
    report = ROIReport(db)
    return report.generate_report(start_date, end_date, min_roi, max_roi, user_id)


# ============================================================================
# COST REPORTS
# ============================================================================

@router.get("/costs")
async def get_cost_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    group_by: str = Query("investigation", regex="^(investigation|user|scraper|day)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "finance", "manager"]))
):
    """
    Relatório de Custos por Investigação
    
    Análise detalhada de custos operacionais.
    
    **group_by**: investigation, user, scraper, day
    
    **Requer: admin, finance ou manager**
    """
    report = CostReport(db)
    return report.generate_report(start_date, end_date, group_by)


# ============================================================================
# SCRAPER PERFORMANCE REPORTS
# ============================================================================

@router.get("/performance/scrapers")
async def get_scraper_performance_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    scraper_name: Optional[str] = Query(None, description="Filtrar por scraper específico"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Relatório de Performance de Scrapers
    
    Analisa taxa de sucesso, tempo de execução e confiabilidade.
    
    **Requer: admin ou manager**
    """
    report = ScraperPerformanceReport(db)
    return report.generate_report(start_date, end_date, scraper_name)


# ============================================================================
# UPTIME REPORTS
# ============================================================================

@router.get("/uptime")
async def get_uptime_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Relatório de Uptime e Disponibilidade
    
    Monitora disponibilidade de componentes críticos do sistema.
    
    **Requer: admin ou manager**
    """
    report = UptimeReport(db)
    return report.generate_report(start_date, end_date)


# ============================================================================
# ERROR REPORTS
# ============================================================================

@router.get("/errors")
async def get_error_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Relatório de Erros e Falhas
    
    Analisa erros, frequência, impacto e custo estimado.
    
    **severity**: low, medium, high, critical
    
    **Requer: admin ou manager**
    """
    report = ErrorReport(db)
    return report.generate_report(start_date, end_date, severity)


# ============================================================================
# CONSOLIDATED EXECUTIVE REPORT
# ============================================================================

@router.get("/executive")
async def get_executive_management_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "executive"]))
):
    """
    Relatório Executivo Consolidado
    
    Integra todos os 5 relatórios gerenciais em um único dashboard:
    - ROI por investigação
    - Custos operacionais
    - Performance de scrapers
    - Uptime e disponibilidade
    - Erros e falhas
    
    Inclui score de saúde operacional e ações prioritárias.
    
    **Requer: admin ou executive**
    """
    consolidator = ManagementReportsConsolidator(db)
    
    # Importar ROI e Cost reports dinamicamente
    from app.analytics.management_reports import ROIReport, CostReport
    consolidator.roi_report = ROIReport(db)
    consolidator.cost_report = CostReport(db)
    
    # Gerar relatório executivo
    executive_report = consolidator.generate_executive_management_report(start_date, end_date)
    
    # Adicionar ROI e Cost ao relatório
    executive_report["reports"]["roi"] = consolidator.roi_report.generate_report(start_date, end_date)
    executive_report["reports"]["costs"] = consolidator.cost_report.generate_report(start_date, end_date)
    
    return executive_report


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def management_reports_health():
    """Health check do módulo de relatórios gerenciais"""
    return {
        "status": "healthy",
        "module": "management_reports",
        "reports_available": [
            "roi",
            "costs",
            "performance",
            "uptime",
            "errors",
            "executive"
        ]
    }
