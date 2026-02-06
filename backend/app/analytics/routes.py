"""
API Router - Endpoints REST para Analytics

Este módulo expõe todas as funcionalidades de analytics via REST API.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user, require_role
from app.domain.user import User
from app.analytics import MetricsCalculator, AnalyticsAggregator
from app.analytics.dashboard import DashboardBuilder, ReportGenerator
from app.analytics.reports import (
    CustomReportBuilder,
    ReportConfig,
    ReportType,
    ReportPeriod,
    ReportFormat,
    ReportTemplates,
    ScheduledReports
)
from app.analytics.bi_integrations import (
    MetabaseConnector,
    PowerBIConnector,
    TableauConnector,
    UniversalBIAdapter,
    BITool
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# ============================================================================
# SCHEMAS DE REQUEST/RESPONSE
# ============================================================================

class MetricsRequest(BaseModel):
    """Request para métricas com filtro de data"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class DashboardType(BaseModel):
    """Tipo de dashboard"""
    dashboard_type: str  # "executive", "operations", "realtime"


class UserAnalyticsRequest(BaseModel):
    """Request para analytics de usuário"""
    user_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ScheduleReportRequest(BaseModel):
    """Request para agendar relatório"""
    config: ReportConfig
    schedule: str  # cron expression
    recipients: List[str]  # emails


# ============================================================================
# ENDPOINTS - MÉTRICAS BÁSICAS
# ============================================================================

@router.get("/metrics/overview")
async def get_overview_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna métricas gerais do sistema
    
    - Usuários (total, ativos, novos)
    - Investigações (total, por status, taxa de conclusão)
    - Período analisado
    """
    calculator = MetricsCalculator(db)
    return calculator.get_overview_metrics(start_date, end_date)


@router.get("/metrics/usage")
async def get_usage_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna métricas de uso da plataforma
    
    - Atividade diária
    - Top usuários
    - Tempo médio de conclusão
    """
    calculator = MetricsCalculator(db)
    return calculator.get_usage_metrics(start_date, end_date)


@router.get("/metrics/scrapers")
async def get_scrapers_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Retorna métricas dos scrapers
    
    - Execuções totais
    - Taxa de sucesso
    - Performance por scraper
    
    **Requer: admin ou manager**
    """
    calculator = MetricsCalculator(db)
    return calculator.get_scrapers_metrics(start_date, end_date)


@router.get("/metrics/geographic")
async def get_geographic_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna métricas geográficas
    
    - Distribuição de propriedades por estado
    - Área total por estado
    """
    calculator = MetricsCalculator(db)
    return calculator.get_geographic_metrics()


@router.get("/metrics/performance")
async def get_performance_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Retorna métricas de performance do sistema
    
    - API (tempos de resposta, taxa de erro)
    - Database (query times, conexões)
    - Cache (hit rate, memory)
    
    **Requer: admin**
    """
    calculator = MetricsCalculator(db)
    return calculator.get_performance_metrics(start_date, end_date)


@router.get("/metrics/financial")
async def get_financial_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "finance"]))
):
    """
    Retorna métricas financeiras
    
    - Custos operacionais
    - Receita (MRR, ARR)
    - ROI e margem de lucro
    
    **Requer: admin ou finance**
    """
    calculator = MetricsCalculator(db)
    return calculator.get_financial_metrics(start_date, end_date)


# ============================================================================
# ENDPOINTS - DASHBOARDS
# ============================================================================

@router.get("/dashboards/executive")
async def get_executive_dashboard(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "executive"]))
):
    """
    Dashboard executivo com KPIs principais
    
    - KPIs (usuários, investigações, MRR)
    - Health Score
    - Gráficos de atividade e distribuição
    - Top usuários
    - Métricas financeiras
    
    **Requer: admin ou executive**
    """
    builder = DashboardBuilder(db)
    dashboard = builder.build_executive_dashboard(start_date, end_date)
    return dashboard.dict()


@router.get("/dashboards/operations")
async def get_operations_dashboard(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Dashboard operacional
    
    - Métricas gerais
    - Status dos scrapers
    - Recomendações operacionais
    
    **Requer: admin ou manager**
    """
    builder = DashboardBuilder(db)
    dashboard = builder.build_operations_dashboard(start_date, end_date)
    return dashboard.dict()


@router.get("/dashboards/user/{user_id}")
async def get_user_dashboard(
    user_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dashboard pessoal do usuário
    
    - Estatísticas pessoais
    - Dados coletados
    - Taxa de conclusão
    
    Usuários comuns só podem ver seu próprio dashboard.
    Admins podem ver de qualquer usuário.
    """
    # Validar permissão
    if current_user.id != user_id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Você só pode acessar seu próprio dashboard"
        )
    
    builder = DashboardBuilder(db)
    dashboard = builder.build_user_dashboard(user_id, start_date, end_date)
    return dashboard.dict()


@router.get("/dashboards/realtime")
async def get_realtime_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Dashboard em tempo real (últimas 24h)
    
    - Métricas das últimas 24 horas
    - Status dos componentes
    - Atualização automática
    
    **Requer: admin ou manager**
    """
    builder = DashboardBuilder(db)
    dashboard = builder.build_realtime_dashboard()
    return dashboard.dict()


# ============================================================================
# ENDPOINTS - RELATÓRIOS
# ============================================================================

@router.post("/reports/generate")
async def generate_custom_report(
    config: ReportConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Gera relatório customizado
    
    Permite configurar:
    - Tipo de relatório
    - Período
    - Filtros
    - Métricas específicas
    - Formato de exportação
    
    **Requer: admin ou manager**
    """
    builder = CustomReportBuilder(db)
    report = builder.generate_report(config)
    return report


@router.get("/reports/executive-summary")
async def get_executive_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "executive"]))
):
    """
    Sumário executivo completo
    
    Inclui todas as métricas principais agregadas.
    
    **Requer: admin ou executive**
    """
    aggregator = AnalyticsAggregator(db)
    return aggregator.generate_executive_summary(start_date, end_date)


@router.get("/reports/operational")
async def get_operational_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Relatório operacional detalhado
    
    **Requer: admin ou manager**
    """
    aggregator = AnalyticsAggregator(db)
    return aggregator.generate_operational_report(start_date, end_date)


@router.get("/reports/monthly/{year}/{month}")
async def get_monthly_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "executive"]))
):
    """
    Relatório mensal completo
    
    **Requer: admin ou executive**
    """
    generator = ReportGenerator(db)
    return generator.generate_monthly_report(year, month)


@router.get("/reports/quarterly/{year}/{quarter}")
async def get_quarterly_report(
    year: int,
    quarter: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "executive"]))
):
    """
    Relatório trimestral
    
    **Requer: admin ou executive**
    """
    generator = ReportGenerator(db)
    return generator.generate_quarterly_report(year, quarter)


@router.get("/reports/annual/{year}")
async def get_annual_report(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "executive"]))
):
    """
    Relatório anual completo
    
    **Requer: admin ou executive**
    """
    generator = ReportGenerator(db)
    return generator.generate_annual_report(year)


@router.get("/reports/templates")
async def get_report_templates(
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Lista templates de relatórios pré-configurados
    
    **Requer: admin ou manager**
    """
    return {
        "templates": [
            {
                "id": "weekly_executive",
                "name": "Sumário Executivo Semanal",
                "config": ReportTemplates.get_weekly_executive_summary().dict()
            },
            {
                "id": "monthly_financial",
                "name": "Relatório Financeiro Mensal",
                "config": ReportTemplates.get_monthly_financial_report().dict()
            },
            {
                "id": "daily_operations",
                "name": "Relatório Operacional Diário",
                "config": ReportTemplates.get_daily_operations_report().dict()
            },
            {
                "id": "quarterly_performance",
                "name": "Relatório de Performance Trimestral",
                "config": ReportTemplates.get_quarterly_performance_report().dict()
            }
        ]
    }


@router.post("/reports/schedule")
async def schedule_report(
    request: ScheduleReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Agenda relatório para envio automático
    
    **Requer: admin**
    """
    scheduler = ScheduledReports(db)
    result = scheduler.schedule_report(
        request.config,
        request.schedule,
        request.recipients
    )
    return result


@router.get("/reports/funnel")
async def get_funnel_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Métricas de funil de conversão
    
    **Requer: admin ou manager**
    """
    aggregator = AnalyticsAggregator(db)
    return aggregator.get_funnel_metrics(start_date, end_date)


# ============================================================================
# ENDPOINTS - INTEGRAÇÕES BI
# ============================================================================

@router.get("/bi/metabase/connection")
async def get_metabase_connection(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Configuração de conexão para Metabase
    
    **Requer: admin**
    """
    connector = MetabaseConnector(db)
    return {
        "connection_config": connector.get_connection_config(),
        "suggested_questions": connector.get_suggested_questions(),
        "dashboard_template": connector.create_dashboard_template()
    }


@router.get("/bi/powerbi/connection")
async def get_powerbi_connection(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Configuração de conexão para Power BI
    
    **Requer: admin**
    """
    connector = PowerBIConnector(db)
    return {
        "connection_config": connector.get_connection_config(),
        "dashboard_template": connector.get_dashboard_template()
    }


@router.get("/bi/powerbi/export")
async def export_for_powerbi(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Exporta dados em formato otimizado para Power BI
    
    **Requer: admin**
    """
    connector = PowerBIConnector(db)
    return connector.export_for_powerbi(start_date, end_date)


@router.get("/bi/tableau/connection")
async def get_tableau_connection(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Configuração de conexão para Tableau
    
    **Requer: admin**
    """
    connector = TableauConnector(db)
    return {
        "connection_config": connector.get_connection_config(),
        "workbook_template": connector.get_workbook_template()
    }


@router.get("/bi/tableau/export")
async def export_for_tableau(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Exporta dados em formato Tableau
    
    **Requer: admin**
    """
    connector = TableauConnector(db)
    return connector.export_for_tableau(start_date, end_date)


@router.get("/bi/datasets")
async def get_dataset_catalog(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Catálogo de datasets disponíveis para BI
    
    **Requer: admin**
    """
    adapter = UniversalBIAdapter(db)
    datasets = adapter.get_dataset_catalog()
    return {"datasets": [ds.dict() for ds in datasets]}


@router.get("/bi/datasets/{dataset_name}")
async def get_dataset_data(
    dataset_name: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Retorna dados de um dataset específico
    
    Suporta paginação e filtros por data.
    
    **Requer: admin**
    """
    adapter = UniversalBIAdapter(db)
    return adapter.get_dataset_data(dataset_name, start_date, end_date, limit, offset)


@router.get("/bi/odata/$metadata")
async def get_odata_metadata(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Metadata no formato OData (para ferramentas que suportam)
    
    **Requer: admin**
    """
    adapter = UniversalBIAdapter(db)
    return adapter.get_odata_metadata()


# ============================================================================
# ENDPOINTS - ANALYTICS DE USUÁRIO ESPECÍFICO
# ============================================================================

@router.get("/users/{user_id}/analytics")
async def get_user_analytics(
    user_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analytics detalhado de um usuário específico
    
    Usuários comuns só podem ver suas próprias analytics.
    Admins podem ver de qualquer usuário.
    """
    # Validar permissão
    if current_user.id != user_id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Você só pode acessar suas próprias analytics"
        )
    
    aggregator = AnalyticsAggregator(db)
    return aggregator.get_user_analytics(user_id, start_date, end_date)


# ============================================================================
# ENDPOINTS - HEALTH CHECK
# ============================================================================

@router.get("/health")
async def analytics_health_check():
    """
    Health check do sistema de analytics
    """
    return {
        "status": "healthy",
        "service": "analytics",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "metrics": True,
            "dashboards": True,
            "reports": True,
            "bi_integrations": True
        }
    }
