"""
Testes Completos - Analytics e Integrações
===========================================

Suite de testes para todos os módulos implementados:
- Dashboard Administrativo
- Relatórios Gerenciais
- Analytics de Usuário
- Exportação Data Warehouse
- Integrações (CAR, Tribunais, Órgãos Federais, Bureaus, Produtividade)

Autor: AgroADB Team
Data: 2026-02-05
Versão: 1.0.0
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Imports dos módulos a testar
from app.analytics.admin_dashboard import AdminDashboard
from app.analytics.management_reports_full import ManagementReports
from app.analytics.user_analytics_full import UserAnalytics
from app.analytics.data_warehouse_export import DataWarehouseExporter
from app.integrations.car_estados import CARIntegration
from app.integrations.tribunais import TribunalIntegration
from app.integrations.orgaos_federais import OrgaoFederalIntegration
from app.integrations.bureaus import BureauIntegration
from app.integrations.comunicacao import (
    SlackIntegration,
    TeamsIntegration,
    ZapierIntegration,
    ProductivityIntegration
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock do banco de dados"""
    db = Mock()
    return db


@pytest.fixture
def admin_dashboard(mock_db):
    """Fixture do AdminDashboard"""
    return AdminDashboard(mock_db)


@pytest.fixture
def management_reports(mock_db):
    """Fixture do ManagementReports"""
    return ManagementReports(mock_db)


@pytest.fixture
def user_analytics(mock_db):
    """Fixture do UserAnalytics"""
    return UserAnalytics(mock_db)


@pytest.fixture
def data_warehouse_exporter(mock_db):
    """Fixture do DataWarehouseExporter"""
    return DataWarehouseExporter(mock_db)


# ============================================================================
# TESTES - DASHBOARD ADMINISTRATIVO
# ============================================================================

@pytest.mark.asyncio
async def test_get_platform_metrics(admin_dashboard, mock_db):
    """Testa obtenção de métricas da plataforma"""
    # Mock das queries
    mock_db.query.return_value.scalar.return_value = 100
    mock_db.query.return_value.filter.return_value.scalar.return_value = 50
    
    result = await admin_dashboard.get_platform_metrics()
    
    assert "users" in result
    assert "investigations" in result
    assert "period" in result
    assert isinstance(result["users"]["total"], int)


@pytest.mark.asyncio
async def test_get_investigations_by_period(admin_dashboard, mock_db):
    """Testa investigações por período"""
    mock_db.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = []
    
    result = await admin_dashboard.get_investigations_by_period(
        group_by="month"
    )
    
    assert "data" in result
    assert "totals" in result
    assert result["period"]["group_by"] == "month"


@pytest.mark.asyncio
async def test_get_average_completion_time(admin_dashboard, mock_db):
    """Testa tempo médio de conclusão"""
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    result = await admin_dashboard.get_average_completion_time()
    
    assert "average_time" in result
    assert "total_completed" in result
    assert "days" in result["average_time"]


@pytest.mark.asyncio
async def test_get_conversion_rate(admin_dashboard, mock_db):
    """Testa taxa de conversão"""
    mock_db.query.return_value.filter.return_value.scalar.return_value = 100
    
    result = await admin_dashboard.get_conversion_rate()
    
    assert "conversion_rates" in result
    assert "funnel" in result
    assert "health_score" in result


@pytest.mark.asyncio
async def test_get_most_active_users(admin_dashboard, mock_db):
    """Testa usuários mais ativos"""
    mock_db.query.return_value.join.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
    
    result = await admin_dashboard.get_most_active_users(limit=5)
    
    assert "active_users" in result
    assert "total_investigations" in result


# ============================================================================
# TESTES - RELATÓRIOS GERENCIAIS
# ============================================================================

@pytest.mark.asyncio
async def test_get_roi_by_investigation(management_reports, mock_db):
    """Testa cálculo de ROI"""
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    result = await management_reports.get_roi_by_investigation()
    
    assert "summary" in result
    assert "investigations" in result
    assert "total_invested" in result["summary"]
    assert "total_recovered" in result["summary"]


@pytest.mark.asyncio
async def test_get_cost_per_investigation(management_reports, mock_db):
    """Testa cálculo de custos"""
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    result = await management_reports.get_cost_per_investigation()
    
    assert "summary" in result
    assert "cost_breakdown" in result["summary"]


@pytest.mark.asyncio
async def test_get_scraper_performance(management_reports, mock_db):
    """Testa análise de performance de scrapers"""
    result = await management_reports.get_scraper_performance()
    
    assert "scrapers" in result
    assert "summary" in result
    assert "recommendations" in result
    assert isinstance(result["scrapers"], list)


@pytest.mark.asyncio
async def test_get_uptime_availability(management_reports, mock_db):
    """Testa métricas de uptime"""
    result = await management_reports.get_uptime_availability()
    
    assert "overall" in result
    assert "components" in result
    assert "uptime_percentage" in result["overall"]


@pytest.mark.asyncio
async def test_get_errors_and_failures(management_reports, mock_db):
    """Testa análise de erros"""
    result = await management_reports.get_errors_and_failures()
    
    assert "summary" in result
    assert "by_type" in result
    assert "by_severity" in result


# ============================================================================
# TESTES - ANALYTICS DE USUÁRIO
# ============================================================================

@pytest.mark.asyncio
async def test_get_usage_funnel(user_analytics, mock_db):
    """Testa funnel de uso"""
    mock_db.query.return_value.filter.return_value.scalar.return_value = 100
    
    result = await user_analytics.get_usage_funnel()
    
    assert "funnel" in result
    assert "bottlenecks" in result
    assert "recommendations" in result
    assert len(result["funnel"]) == 6  # 6 estágios


@pytest.mark.asyncio
async def test_get_feature_adoption(user_analytics, mock_db):
    """Testa adoção de features"""
    mock_db.query.return_value.filter.return_value.scalar.return_value = 100
    
    result = await user_analytics.get_feature_adoption()
    
    assert "features" in result
    assert "by_category" in result
    assert "low_adoption_features" in result


@pytest.mark.asyncio
async def test_get_navigation_heatmap(user_analytics, mock_db):
    """Testa heatmap de navegação"""
    result = await user_analytics.get_navigation_heatmap()
    
    assert "heatmap_data" in result
    assert "top_pages" in result
    assert "top_elements" in result


@pytest.mark.asyncio
async def test_get_nps_score(user_analytics, mock_db):
    """Testa cálculo de NPS"""
    result = await user_analytics.get_nps_score()
    
    assert "nps" in result
    assert "distribution" in result
    assert "score" in result["nps"]
    assert "promoters" in result["distribution"]


# ============================================================================
# TESTES - EXPORTAÇÃO DATA WAREHOUSE
# ============================================================================

@pytest.mark.asyncio
async def test_export_to_bigquery(data_warehouse_exporter, mock_db):
    """Testa exportação para BigQuery"""
    mock_db.query.return_value.limit.return_value.all.return_value = []
    
    result = await data_warehouse_exporter.export_to_bigquery(
        dataset="agroadb",
        table="investigations"
    )
    
    assert result["status"] == "success"
    assert "records_exported" in result
    assert "bigquery_job_id" in result


@pytest.mark.asyncio
async def test_export_to_redshift(data_warehouse_exporter, mock_db):
    """Testa exportação para Redshift"""
    mock_db.query.return_value.limit.return_value.all.return_value = []
    
    result = await data_warehouse_exporter.export_to_redshift(
        schema="public",
        table="investigations"
    )
    
    assert result["status"] == "success"
    assert "records_exported" in result


@pytest.mark.asyncio
async def test_create_tableau_extract(data_warehouse_exporter, mock_db):
    """Testa criação de extrato Tableau"""
    mock_db.query.return_value.limit.return_value.all.return_value = []
    
    result = await data_warehouse_exporter.create_tableau_extract(
        extract_name="investigations_2024"
    )
    
    assert result["status"] == "success"
    assert result["extract_format"] == "hyper"
    assert "schema" in result


@pytest.mark.asyncio
async def test_create_powerbi_dataset(data_warehouse_exporter, mock_db):
    """Testa criação de dataset Power BI"""
    mock_db.query.return_value.limit.return_value.all.return_value = []
    
    result = await data_warehouse_exporter.create_powerbi_dataset(
        workspace_id="workspace123",
        dataset_name="AgroADB_Investigations"
    )
    
    assert result["status"] == "success"
    assert "dataset_id" in result
    assert "refresh_schedule" in result


# ============================================================================
# TESTES - INTEGRAÇÕES CAR
# ============================================================================

@pytest.mark.asyncio
async def test_car_query():
    """Testa consulta CAR"""
    integration = CARIntegration()
    
    result = await integration.query_car(
        car_code="SP-1234567-ABCDEFGH",
        state="SP"
    )
    
    assert result.state == "SP"
    assert result.car_code == "SP-1234567-ABCDEFGH"
    # Pode ser sucesso ou falha dependendo da simulação


# ============================================================================
# TESTES - INTEGRAÇÕES TRIBUNAIS
# ============================================================================

@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_query_process_esaj(mock_get):
    """Testa consulta de processo no ESAJ"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Processo encontrado</body></html>"
    mock_get.return_value = mock_response
    
    integration = TribunalIntegration()
    
    result = await integration.query_process(
        process_number="0001234-56.2023.8.26.0100",
        state="SP",
        system="esaj"
    )
    
    assert result.state == "SP"
    assert result.system == "esaj"
    await integration.close()


# ============================================================================
# TESTES - INTEGRAÇÕES ÓRGÃOS FEDERAIS
# ============================================================================

@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_query_ibama(mock_get):
    """Testa consulta IBAMA"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"embargos": [], "infracoes": []}
    mock_get.return_value = mock_response
    
    integration = OrgaoFederalIntegration()
    
    result = await integration.query_ibama("12345678900")
    
    assert result["success"] == True
    assert "embargos" in result
    await integration.close()


# ============================================================================
# TESTES - INTEGRAÇÕES BUREAUS
# ============================================================================

def test_bureau_integration_no_api_key():
    """Testa Bureau sem API key"""
    integration = BureauIntegration()
    
    # Não deve falhar, apenas indicar que não está configurado
    assert integration.serasa_api_key is None
    assert integration.boavista_api_key is None


@pytest.mark.asyncio
async def test_query_serasa_no_key():
    """Testa consulta Serasa sem API key"""
    integration = BureauIntegration()
    
    result = await integration.query_serasa("12345678900")
    
    assert result["success"] == False
    assert "API key" in result["error"]


# ============================================================================
# TESTES - INTEGRAÇÕES PRODUTIVIDADE
# ============================================================================

@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_slack_send_message(mock_post):
    """Testa envio de mensagem Slack"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True, "message": "sent"}
    mock_post.return_value = mock_response
    
    integration = SlackIntegration(webhook_url="https://hooks.slack.com/test")
    
    result = await integration._send_via_webhook("Test message")
    
    assert result["success"] == True
    await integration.close()


@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_teams_send_message(mock_post):
    """Testa envio de mensagem Teams"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "1"
    mock_post.return_value = mock_response
    
    integration = TeamsIntegration(webhook_url="https://outlook.office.com/webhook/test")
    
    result = await integration.send_message(
        title="Test",
        text="Test message"
    )
    
    assert result["success"] == True
    await integration.close()


@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_zapier_trigger(mock_post):
    """Testa trigger Zapier"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "success"
    mock_post.return_value = mock_response
    
    integration = ZapierIntegration(webhook_url="https://hooks.zapier.com/test")
    
    result = await integration.trigger_zap(
        event_type="test_event",
        data={"key": "value"}
    )
    
    assert result["success"] == True
    await integration.close()


# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

@pytest.mark.asyncio
async def test_complete_dashboard_generation(admin_dashboard, mock_db):
    """Testa geração completa do dashboard"""
    mock_db.query.return_value.filter.return_value.scalar.return_value = 100
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    result = await admin_dashboard.get_complete_dashboard()
    
    assert "platform_metrics" in result
    assert "investigations_by_period" in result
    assert "conversion_rate" in result
    assert "active_users" in result


@pytest.mark.asyncio
async def test_complete_management_report(management_reports, mock_db):
    """Testa geração completa de relatório gerencial"""
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    result = await management_reports.get_complete_management_report()
    
    assert "roi_analysis" in result
    assert "cost_analysis" in result
    assert "scraper_performance" in result
    assert "uptime_availability" in result
    assert "overall_health" in result


# ============================================================================
# EXECUÇÃO DOS TESTES
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
