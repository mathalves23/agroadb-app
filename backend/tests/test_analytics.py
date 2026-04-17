"""
Testes para o módulo Analytics

Testes unitários e de integração para métricas, dashboards e relatórios.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.analytics import MetricsCalculator, AnalyticsAggregator
from app.analytics.dashboard import DashboardBuilder, ReportGenerator
from app.analytics.reports import CustomReportBuilder, ReportConfig, ReportType, ReportPeriod, ReportFormat
from app.analytics.bi_integrations import (
    MetabaseConnector,
    PowerBIConnector,
    TableauConnector,
    UniversalBIAdapter
)
from app.domain.user import User
from app.domain.investigation import Investigation


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock da sessão do banco de dados"""
    return Mock(spec=Session)


@pytest.fixture
def sample_users():
    """Usuários de exemplo para testes"""
    return [
        User(
            id=1,
            username="user1",
            email="user1@example.com",
            is_active=True,
            role="user",
            created_at=datetime.utcnow() - timedelta(days=60)
        ),
        User(
            id=2,
            username="user2",
            email="user2@example.com",
            is_active=True,
            role="user",
            created_at=datetime.utcnow() - timedelta(days=30)
        ),
        User(
            id=3,
            username="user3",
            email="user3@example.com",
            is_active=False,
            role="user",
            created_at=datetime.utcnow() - timedelta(days=90)
        )
    ]


@pytest.fixture
def sample_investigations():
    """Investigações de exemplo para testes"""
    return [
        Investigation(
            id=1,
            user_id=1,
            cpf_cnpj="12345678901",
            status="completed",
            created_at=datetime.utcnow() - timedelta(days=10),
            updated_at=datetime.utcnow() - timedelta(days=9)
        ),
        Investigation(
            id=2,
            user_id=1,
            cpf_cnpj="98765432100",
            status="in_progress",
            created_at=datetime.utcnow() - timedelta(days=5),
            updated_at=datetime.utcnow() - timedelta(days=4)
        ),
        Investigation(
            id=3,
            user_id=2,
            cpf_cnpj="11122233344",
            status="completed",
            created_at=datetime.utcnow() - timedelta(days=3),
            updated_at=datetime.utcnow() - timedelta(days=2)
        )
    ]


# ============================================================================
# TESTES - METRICSCALCULATOR
# ============================================================================

class TestMetricsCalculator:
    """Testes para MetricsCalculator"""
    
    def test_get_overview_metrics_structure(self, mock_db):
        """Testa estrutura do retorno de overview_metrics"""
        calculator = MetricsCalculator(mock_db)
        
        # Mock das queries
        mock_db.query().scalar.return_value = 10
        mock_db.query().filter().scalar.return_value = 8
        mock_db.query().group_by().all.return_value = [
            ("completed", 5),
            ("in_progress", 3),
            ("pending", 2)
        ]
        
        result = calculator.get_overview_metrics()
        
        # Validar estrutura
        assert "users" in result
        assert "investigations" in result
        assert "period" in result
        
        assert "total" in result["users"]
        assert "active" in result["users"]
        assert "inactive" in result["users"]
        
        assert "total" in result["investigations"]
        assert "by_status" in result["investigations"]
        assert "completion_rate" in result["investigations"]
    
    def test_get_overview_metrics_with_dates(self, mock_db):
        """Testa overview_metrics com datas específicas"""
        calculator = MetricsCalculator(mock_db)
        
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)
        
        mock_db.query().scalar.return_value = 5
        mock_db.query().filter().scalar.return_value = 3
        mock_db.query().group_by().all.return_value = []
        
        result = calculator.get_overview_metrics(start, end)
        
        assert result["period"]["days"] == 30
        assert datetime.fromisoformat(result["period"]["start"]) == start
        assert datetime.fromisoformat(result["period"]["end"]) == end
    
    def test_get_usage_metrics_structure(self, mock_db):
        """Testa estrutura de usage_metrics"""
        calculator = MetricsCalculator(mock_db)
        
        mock_db.query().filter().group_by().all.return_value = [
            (datetime(2024, 1, 1).date(), 5),
            (datetime(2024, 1, 2).date(), 8)
        ]
        mock_db.query().join().filter().group_by().order_by().limit().all.return_value = []
        mock_db.query().filter().all.return_value = []
        
        result = calculator.get_usage_metrics()
        
        assert "daily_activity" in result
        assert "top_users" in result
        assert "completion_time" in result
        assert isinstance(result["daily_activity"], list)
    
    def test_get_scrapers_metrics_structure(self, mock_db):
        """Testa estrutura de scrapers_metrics"""
        calculator = MetricsCalculator(mock_db)
        
        mock_db.query().filter().scalar.return_value = 10
        
        result = calculator.get_scrapers_metrics()
        
        assert "by_scraper" in result
        assert "total_executions" in result
        assert "total_successes" in result
        assert "total_failures" in result
        assert "average_duration_seconds" in result
        
        # Validar que todos os scrapers estão presentes
        expected_scrapers = ["car", "incra", "receita", "cartorios", "diarios", "sigef_sicar"]
        for scraper in expected_scrapers:
            assert scraper in result["by_scraper"]
    
    def test_get_geographic_metrics_structure(self, mock_db):
        """Testa estrutura de geographic_metrics"""
        calculator = MetricsCalculator(mock_db)
        
        mock_db.query().all.return_value = []
        
        result = calculator.get_geographic_metrics()
        
        assert "by_state" in result
        assert "total_states" in result
        assert isinstance(result["by_state"], list)
    
    def test_get_performance_metrics_structure(self, mock_db):
        """Testa estrutura de performance_metrics"""
        calculator = MetricsCalculator(mock_db)
        
        result = calculator.get_performance_metrics()
        
        assert "api" in result
        assert "database" in result
        assert "cache" in result
        
        # API metrics
        assert "average_response_time_ms" in result["api"]
        assert "error_rate" in result["api"]
        
        # Database metrics
        assert "average_query_time_ms" in result["database"]
        assert "connections_active" in result["database"]
        
        # Cache metrics
        assert "hit_rate" in result["cache"]
        assert "keys_count" in result["cache"]
    
    def test_get_financial_metrics_structure(self, mock_db):
        """Testa estrutura de financial_metrics"""
        calculator = MetricsCalculator(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        mock_db.query().filter().scalar.return_value = 50
        
        result = calculator.get_financial_metrics()
        
        assert "period_metrics" in result
        assert "revenue" in result
        assert "roi" in result
        
        # Period metrics
        assert "investigations" in result["period_metrics"]
        assert "cost_per_investigation" in result["period_metrics"]
        
        # Revenue
        assert "mrr" in result["revenue"]
        assert "arr" in result["revenue"]
        
        # ROI
        assert "margin_percentage" in result["roi"]


# ============================================================================
# TESTES - ANALYTICSAGGREGATOR
# ============================================================================

class TestAnalyticsAggregator:
    """Testes para AnalyticsAggregator"""
    
    def test_generate_executive_summary_structure(self, mock_db):
        """Testa estrutura do sumário executivo"""
        aggregator = AnalyticsAggregator(mock_db)
        
        # Mock do calculator
        with patch.object(aggregator.calculator, 'get_overview_metrics') as mock_overview:
            mock_overview.return_value = {
                "users": {"total": 10, "active": 8, "inactive": 2, "new_in_period": 3},
                "investigations": {
                    "total": 50,
                    "in_period": 20,
                    "by_status": {"completed": 30, "in_progress": 15},
                    "completion_rate": 60.0
                }
            }
            
            with patch.object(aggregator.calculator, 'get_usage_metrics') as mock_usage:
                mock_usage.return_value = {
                    "daily_activity": [],
                    "top_users": [],
                    "completion_time": {"average_hours": 24.5}
                }
                
                with patch.object(aggregator.calculator, 'get_scrapers_metrics') as mock_scrapers:
                    mock_scrapers.return_value = {
                        "total_executions": 100,
                        "total_successes": 85,
                        "by_scraper": {}
                    }
                    
                    with patch.object(aggregator.calculator, 'get_geographic_metrics') as mock_geo:
                        mock_geo.return_value = {"by_state": []}
                        
                        with patch.object(aggregator.calculator, 'get_performance_metrics') as mock_perf:
                            mock_perf.return_value = {"api": {"error_rate": 0.01}}
                            
                            with patch.object(aggregator.calculator, 'get_financial_metrics') as mock_fin:
                                mock_fin.return_value = {
                                    "revenue": {"mrr": 10000},
                                    "roi": {"margin_percentage": 70},
                                    "period_metrics": {"total_cost": 3000}
                                }
                                
                                result = aggregator.generate_executive_summary()
        
        # Validar estrutura
        assert "generated_at" in result
        assert "period" in result
        assert "kpis" in result
        assert "overview" in result
        assert "usage" in result
        assert "scrapers" in result
        assert "geographic" in result
        assert "performance" in result
        assert "financial" in result
        assert "health_score" in result
    
    def test_calculate_health_score(self, mock_db):
        """Testa cálculo do health score"""
        aggregator = AnalyticsAggregator(mock_db)
        
        overview = {
            "investigations": {"completion_rate": 80.0}
        }
        performance = {
            "api": {"error_rate": 0.01}
        }
        financial = {
            "roi": {"margin_percentage": 70.0}
        }
        
        score = aggregator._calculate_health_score(overview, performance, financial)
        
        assert 0 <= score <= 100
        assert isinstance(score, float)
    
    def test_get_user_analytics_not_found(self, mock_db):
        """Testa analytics de usuário não encontrado"""
        aggregator = AnalyticsAggregator(mock_db)
        
        mock_db.query().filter().first.return_value = None
        
        with pytest.raises(ValueError, match="não encontrado"):
            aggregator.get_user_analytics(999)
    
    def test_get_funnel_metrics_structure(self, mock_db):
        """Testa estrutura das métricas de funil"""
        aggregator = AnalyticsAggregator(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        
        result = aggregator.get_funnel_metrics()
        
        assert "funnel" in result
        assert "drop_off" in result
        assert isinstance(result["funnel"], list)
        assert len(result["funnel"]) == 3  # created, started, completed


# ============================================================================
# TESTES - DASHBOARDBUILDER
# ============================================================================

class TestDashboardBuilder:
    """Testes para DashboardBuilder"""
    
    def test_build_executive_dashboard_structure(self, mock_db):
        """Testa estrutura do dashboard executivo"""
        builder = DashboardBuilder(mock_db)
        
        with patch.object(builder.aggregator, 'generate_executive_summary') as mock_summary:
            mock_summary.return_value = {
                "kpis": {
                    "active_users": 100,
                    "total_investigations": 500,
                    "completion_rate": 75.0,
                    "mrr": 50000
                },
                "health_score": 85.0,
                "usage": {"daily_activity": [], "top_users": []},
                "overview": {"investigations": {"by_status": {"completed": 300}}},
                "financial": {"revenue": {"mrr": 50000}},
                "performance": {"api": {"average_response_time_ms": 120}}
            }
            
            dashboard = builder.build_executive_dashboard()
        
        assert dashboard.dashboard_id == "executive"
        assert dashboard.title == "Dashboard Executivo"
        assert len(dashboard.widgets) > 0
        
        # Verificar widgets principais
        widget_ids = [w.widget_id for w in dashboard.widgets]
        assert "kpis" in widget_ids
        assert "health_score" in widget_ids
    
    def test_build_operations_dashboard_structure(self, mock_db):
        """Testa estrutura do dashboard operacional"""
        builder = DashboardBuilder(mock_db)
        
        with patch.object(builder.aggregator, 'generate_operational_report') as mock_report:
            mock_report.return_value = {
                "overview": {"investigations": {"in_period": 50}},
                "usage": {"daily_activity": [], "completion_time": {"average_hours": 24}},
                "scrapers": {"by_scraper": {}},
                "recommendations": ["Tudo ok"]
            }
            
            dashboard = builder.build_operations_dashboard()
        
        assert dashboard.dashboard_id == "operations"
        assert len(dashboard.widgets) > 0
    
    def test_build_realtime_dashboard_structure(self, mock_db):
        """Testa estrutura do dashboard em tempo real"""
        builder = DashboardBuilder(mock_db)
        
        with patch.object(builder.calculator, 'get_overview_metrics') as mock_overview:
            mock_overview.return_value = {
                "users": {"active": 50},
                "investigations": {"in_period": 10}
            }
            
            with patch.object(builder.calculator, 'get_performance_metrics') as mock_perf:
                mock_perf.return_value = {
                    "api": {"average_response_time_ms": 120, "error_rate": 0.01},
                    "database": {"connections_active": 10},
                    "cache": {"hit_rate": 0.8}
                }
                
                dashboard = builder.build_realtime_dashboard()
        
        assert dashboard.dashboard_id == "realtime"
        assert len(dashboard.widgets) > 0


# ============================================================================
# TESTES - CUSTOMREPORTBUILDER
# ============================================================================

class TestCustomReportBuilder:
    """Testes para CustomReportBuilder"""
    
    def test_calculate_period_last_7_days(self, mock_db):
        """Testa cálculo de período: últimos 7 dias"""
        builder = CustomReportBuilder(mock_db)
        
        start, end = builder._calculate_period(ReportPeriod.LAST_7_DAYS, None, None)
        
        assert (end - start).days == 7
    
    def test_calculate_period_last_30_days(self, mock_db):
        """Testa cálculo de período: últimos 30 dias"""
        builder = CustomReportBuilder(mock_db)
        
        start, end = builder._calculate_period(ReportPeriod.LAST_30_DAYS, None, None)
        
        assert (end - start).days == 30
    
    def test_calculate_period_custom(self, mock_db):
        """Testa cálculo de período: customizado"""
        builder = CustomReportBuilder(mock_db)
        
        custom_start = datetime(2024, 1, 1)
        custom_end = datetime(2024, 1, 31)
        
        start, end = builder._calculate_period(ReportPeriod.CUSTOM, custom_start, custom_end)
        
        assert start == custom_start
        assert end == custom_end
    
    def test_calculate_period_custom_without_dates(self, mock_db):
        """Testa período customizado sem fornecer datas"""
        builder = CustomReportBuilder(mock_db)
        
        with pytest.raises(ValueError, match="requires custom_start and custom_end"):
            builder._calculate_period(ReportPeriod.CUSTOM, None, None)
    
    def test_generate_report_executive_type(self, mock_db):
        """Testa geração de relatório executivo"""
        builder = CustomReportBuilder(mock_db)
        
        config = ReportConfig(
            report_id="test_exec",
            title="Test Executive Report",
            report_type=ReportType.EXECUTIVE,
            period=ReportPeriod.LAST_30_DAYS
        )
        
        with patch.object(builder.aggregator, 'generate_executive_summary') as mock_summary:
            mock_summary.return_value = {"test": "data"}
            
            report = builder.generate_report(config)
        
        assert report["report_id"] == "test_exec"
        assert report["title"] == "Test Executive Report"
        assert report["type"] == "executive"
        assert "data" in report


# ============================================================================
# TESTES - BI INTEGRATIONS
# ============================================================================

class TestBIIntegrations:
    """Testes para integrações BI"""
    
    def test_metabase_connector_get_connection_config(self, mock_db):
        """Testa configuração de conexão Metabase"""
        connector = MetabaseConnector(mock_db)
        
        config = connector.get_connection_config()
        
        assert "engine" in config
        assert config["engine"] == "postgres"
        assert "name" in config
        assert "details" in config
    
    def test_metabase_connector_get_suggested_questions(self, mock_db):
        """Testa queries sugeridas para Metabase"""
        connector = MetabaseConnector(mock_db)
        
        questions = connector.get_suggested_questions()
        
        assert len(questions) > 0
        for question in questions:
            assert "name" in question
            assert "sql" in question
            assert "visualization" in question
    
    def test_powerbi_connector_get_connection_config(self, mock_db):
        """Testa configuração de conexão Power BI"""
        connector = PowerBIConnector(mock_db)
        
        config = connector.get_connection_config()
        
        assert "type" in config
        assert config["type"] == "PostgreSQL"
        assert "server" in config
        assert "database" in config
    
    def test_powerbi_export_structure(self, mock_db):
        """Testa estrutura de exportação Power BI"""
        connector = PowerBIConnector(mock_db)
        
        with patch.object(connector.aggregator, 'generate_executive_summary') as mock_summary:
            mock_summary.return_value = {
                "overview": {"users": {}, "investigations": {}},
                "usage": {},
                "scrapers": {},
                "geographic": {},
                "performance": {},
                "financial": {}
            }
            
            export = connector.export_for_powerbi()
        
        assert "model" in export
        assert "measures" in export
        assert "sample_data" in export
    
    def test_tableau_connector_get_connection_config(self, mock_db):
        """Testa configuração de conexão Tableau"""
        connector = TableauConnector(mock_db)
        
        config = connector.get_connection_config()
        
        assert "type" in config
        assert config["type"] == "postgres"
        assert "server" in config
        assert "database" in config
    
    def test_universal_adapter_get_dataset_catalog(self, mock_db):
        """Testa catálogo de datasets"""
        adapter = UniversalBIAdapter(mock_db)
        
        catalog = adapter.get_dataset_catalog()
        
        assert len(catalog) > 0
        for dataset in catalog:
            assert hasattr(dataset, 'name')
            assert hasattr(dataset, 'description')
            assert hasattr(dataset, 'fields')
    
    def test_universal_adapter_get_dataset_data(self, mock_db):
        """Testa obtenção de dados de dataset"""
        adapter = UniversalBIAdapter(mock_db)
        
        with patch.object(adapter.calculator, 'get_overview_metrics') as mock_overview:
            mock_overview.return_value = {"test": "data"}
            
            data = adapter.get_dataset_data("metrics_overview")
        
        assert "dataset" in data
        assert "data" in data
        assert "metadata" in data


# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

@pytest.mark.integration
class TestAnalyticsIntegration:
    """Testes de integração do módulo analytics"""
    
    def test_full_analytics_pipeline(self, mock_db):
        """Testa pipeline completo de analytics"""
        # 1. Coletar métricas
        calculator = MetricsCalculator(mock_db)
        mock_db.query().scalar.return_value = 10
        mock_db.query().group_by().all.return_value = []
        
        overview = calculator.get_overview_metrics()
        assert "users" in overview
        
        # 2. Gerar dashboard
        builder = DashboardBuilder(mock_db)
        with patch.object(builder.aggregator, 'generate_executive_summary') as mock_summary:
            mock_summary.return_value = {
                "kpis": {},
                "health_score": 85.0,
                "overview": overview,
                "usage": {"daily_activity": [], "top_users": []},
                "scrapers": {},
                "geographic": {"by_state": []},
                "performance": {"api": {}},
                "financial": {"revenue": {}}
            }
            
            dashboard = builder.build_executive_dashboard()
            assert len(dashboard.widgets) > 0
        
        # 3. Gerar relatório
        report_builder = CustomReportBuilder(mock_db)
        config = ReportConfig(
            report_id="test",
            title="Test",
            report_type=ReportType.EXECUTIVE,
            period=ReportPeriod.LAST_30_DAYS
        )
        
        with patch.object(report_builder.aggregator, 'generate_executive_summary') as mock_summary:
            mock_summary.return_value = {"test": "data"}
            report = report_builder.generate_report(config)
            assert report["report_id"] == "test"


# ============================================================================
# TESTES DE PERFORMANCE
# ============================================================================

@pytest.mark.performance
class TestAnalyticsPerformance:
    """Testes de performance do módulo analytics"""
    
    def test_metrics_calculation_performance(self, mock_db):
        """Testa performance do cálculo de métricas"""
        import time
        
        calculator = MetricsCalculator(mock_db)
        mock_db.query().scalar.return_value = 1000
        mock_db.query().group_by().all.return_value = []
        
        start = time.time()
        calculator.get_overview_metrics()
        duration = time.time() - start
        
        # Deve ser rápido (< 1 segundo)
        assert duration < 1.0
    
    def test_dashboard_build_performance(self, mock_db):
        """Testa performance da construção de dashboard"""
        import time
        
        builder = DashboardBuilder(mock_db)
        
        with patch.object(builder.aggregator, 'generate_executive_summary') as mock_summary:
            mock_summary.return_value = {
                "kpis": {},
                "health_score": 85.0,
                "overview": {"users": {}, "investigations": {"by_status": {}}},
                "usage": {"daily_activity": [], "top_users": []},
                "scrapers": {"by_scraper": {}},
                "geographic": {"by_state": []},
                "performance": {"api": {}},
                "financial": {"revenue": {}}
            }
            
            start = time.time()
            builder.build_executive_dashboard()
            duration = time.time() - start
        
        # Deve ser rápido (< 2 segundos)
        assert duration < 2.0
