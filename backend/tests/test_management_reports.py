"""
Testes para Relatórios Gerenciais

Testes unitários e de integração para os 5 relatórios gerenciais.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.analytics.management_reports import ROIReport, CostReport
from app.analytics.management_reports_part2 import ScraperPerformanceReport, UptimeReport
from app.analytics.management_reports_part3 import ErrorReport, ManagementReportsConsolidator
from app.domain.user import User
from app.domain.investigation import Investigation
from app.domain.property import Property
from app.domain.company import Company


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock da sessão do banco de dados"""
    return Mock(spec=Session)


@pytest.fixture
def sample_investigations():
    """Investigações de exemplo"""
    now = datetime.utcnow()
    return [
        Investigation(
            id=1,
            user_id=1,
            cpf_cnpj="12345678901",
            status="completed",
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=9),
            completed_at=now - timedelta(days=9),
            properties=[Property(id=1), Property(id=2)],
            companies=[Company(id=1)]
        ),
        Investigation(
            id=2,
            user_id=1,
            cpf_cnpj="98765432100",
            status="in_progress",
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=4),
            properties=[Property(id=3)],
            companies=[]
        ),
        Investigation(
            id=3,
            user_id=2,
            cpf_cnpj="11122233344",
            status="completed",
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=2),
            completed_at=now - timedelta(days=2),
            properties=[Property(id=4), Property(id=5), Property(id=6)],
            companies=[Company(id=2), Company(id=3)]
        ),
        Investigation(
            id=4,
            user_id=2,
            cpf_cnpj="44455566677",
            status="failed",
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
            properties=[],
            companies=[]
        )
    ]


# ============================================================================
# TESTES - ROI REPORT
# ============================================================================

class TestROIReport:
    """Testes para ROI Report"""
    
    def test_generate_report_structure(self, mock_db, sample_investigations):
        """Testa estrutura do relatório de ROI"""
        report = ROIReport(mock_db)
        
        # Mock da query
        mock_db.query().filter().all.return_value = sample_investigations[:3]  # Apenas completas
        
        result = report.generate_report()
        
        # Validar estrutura
        assert "period" in result
        assert "summary" in result
        assert "top_performers" in result
        assert "worst_performers" in result
        assert "detailed_metrics" in result
        assert "recommendations" in result
        
        # Validar summary
        assert "total_investigations" in result["summary"]
        assert "total_cost" in result["summary"]
        assert "total_revenue" in result["summary"]
        assert "average_roi" in result["summary"]
    
    def test_calculate_investigation_roi(self, mock_db):
        """Testa cálculo de ROI de uma investigação"""
        report = ROIReport(mock_db)
        
        inv = Investigation(
            id=1,
            user_id=1,
            cpf_cnpj="12345678901",
            status="completed",
            created_at=datetime.utcnow() - timedelta(hours=2),
            completed_at=datetime.utcnow(),
            properties=[Property(id=i) for i in range(5)],
            companies=[Company(id=i) for i in range(3)]
        )
        
        roi_data = report._calculate_investigation_roi(inv)
        
        assert roi_data.investigation_id == 1
        assert roi_data.properties_found == 5
        assert roi_data.companies_found == 3
        assert roi_data.total_cost > 0
        assert roi_data.revenue_generated > 0
    
    def test_roi_with_filters(self, mock_db, sample_investigations):
        """Testa relatório de ROI com filtros"""
        report = ROIReport(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations[:2]
        
        # Filtrar por ROI mínimo
        result = report.generate_report(min_roi=50.0)
        
        assert "detailed_metrics" in result
    
    def test_roi_recommendations(self, mock_db, sample_investigations):
        """Testa geração de recomendações de ROI"""
        report = ROIReport(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations[:3]
        
        result = report.generate_report()
        
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0


# ============================================================================
# TESTES - COST REPORT
# ============================================================================

class TestCostReport:
    """Testes para Cost Report"""
    
    def test_generate_report_structure(self, mock_db, sample_investigations):
        """Testa estrutura do relatório de custos"""
        report = CostReport(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = report.generate_report()
        
        assert "period" in result
        assert "summary" in result
        assert "grouped_data" in result
        assert "most_expensive" in result
        assert "cost_efficiency" in result
        assert "recommendations" in result
    
    def test_calculate_investigation_cost(self, mock_db):
        """Testa cálculo de custo de uma investigação"""
        report = CostReport(mock_db)
        
        inv = Investigation(
            id=1,
            user_id=1,
            cpf_cnpj="12345678901",
            status="completed",
            created_at=datetime.utcnow() - timedelta(hours=1),
            completed_at=datetime.utcnow(),
            properties=[Property(id=i) for i in range(10)],
            companies=[Company(id=i) for i in range(5)]
        )
        
        cost_data = report._calculate_investigation_cost(inv)
        
        assert cost_data.investigation_id == 1
        assert cost_data.total_cost > 0
        assert cost_data.storage_cost >= 0
        assert cost_data.processing_cost >= 0
        assert cost_data.api_cost >= 0
        assert len(cost_data.scraper_costs) == 6  # 6 scrapers
    
    def test_group_by_user(self, mock_db, sample_investigations):
        """Testa agrupamento por usuário"""
        report = CostReport(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = report.generate_report(group_by="user")
        
        assert "grouped_data" in result
        assert "by_user" in result["grouped_data"]
    
    def test_cost_breakdown(self, mock_db, sample_investigations):
        """Testa breakdown de custos por categoria"""
        report = CostReport(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = report.generate_report()
        
        assert "cost_breakdown" in result["summary"]
        breakdown = result["summary"]["cost_breakdown"]
        
        if breakdown:
            assert "scrapers" in breakdown
            assert "storage" in breakdown
            assert "processing" in breakdown
            assert "api" in breakdown


# ============================================================================
# TESTES - SCRAPER PERFORMANCE REPORT
# ============================================================================

class TestScraperPerformanceReport:
    """Testes para Scraper Performance Report"""
    
    def test_generate_report_structure(self, mock_db, sample_investigations):
        """Testa estrutura do relatório de performance"""
        report = ScraperPerformanceReport(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = report.generate_report()
        
        assert "period" in result
        assert "summary" in result
        assert "scrapers" in result
        assert "best_performers" in result
        assert "worst_performers" in result
        assert "recommendations" in result
    
    def test_calculate_scraper_performance(self, mock_db, sample_investigations):
        """Testa cálculo de performance de scraper"""
        report = ScraperPerformanceReport(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        metrics = report._calculate_scraper_performance(
            "car",
            datetime.utcnow() - timedelta(days=30),
            datetime.utcnow()
        )
        
        assert metrics.scraper_name == "car"
        assert metrics.total_executions >= 0
        assert 0 <= metrics.success_rate <= 100
        assert metrics.average_duration_seconds >= 0
        assert 0 <= metrics.reliability_score <= 100
    
    def test_scraper_status_determination(self, mock_db):
        """Testa determinação de status do scraper"""
        report = ScraperPerformanceReport(mock_db)
        
        from app.analytics.management_reports import ScraperPerformanceMetrics
        
        # Scraper excelente
        excellent = ScraperPerformanceMetrics(
            scraper_name="test",
            total_executions=100,
            successful_executions=98,
            failed_executions=2,
            success_rate=98.0,
            average_duration_seconds=30.0,
            min_duration_seconds=10.0,
            max_duration_seconds=50.0,
            p95_duration_seconds=45.0,
            total_data_collected=500,
            average_data_per_execution=5.0,
            error_rate=2.0,
            reliability_score=90.0
        )
        
        status = report._get_scraper_status(excellent)
        assert status == "excellent"


# ============================================================================
# TESTES - UPTIME REPORT
# ============================================================================

class TestUptimeReport:
    """Testes para Uptime Report"""
    
    def test_generate_report_structure(self, mock_db):
        """Testa estrutura do relatório de uptime"""
        report = UptimeReport(mock_db)
        
        result = report.generate_report()
        
        assert "period" in result
        assert "summary" in result
        assert "components" in result
        assert "incidents" in result
        assert "recommendations" in result
    
    def test_calculate_component_uptime(self, mock_db):
        """Testa cálculo de uptime de componente"""
        report = UptimeReport(mock_db)
        
        metrics = report._calculate_component_uptime(
            "api",
            datetime.utcnow() - timedelta(days=7),
            datetime.utcnow()
        )
        
        assert metrics.component == "api"
        assert 0 <= metrics.uptime_percentage <= 100
        assert metrics.downtime_minutes >= 0
        assert metrics.total_checks > 0
        assert metrics.mttr_minutes >= 0
        assert metrics.mtbf_minutes >= 0
    
    def test_sla_compliance_check(self, mock_db):
        """Testa verificação de compliance com SLA"""
        report = UptimeReport(mock_db)
        
        result = report.generate_report()
        
        assert "sla_target" in result["summary"]
        assert "sla_met" in result["summary"]
        assert result["summary"]["sla_target"] == 99.9
    
    def test_incident_timeline(self, mock_db):
        """Testa geração de timeline de incidentes"""
        report = UptimeReport(mock_db)
        
        result = report.generate_report()
        
        assert "incidents" in result
        assert isinstance(result["incidents"], list)


# ============================================================================
# TESTES - ERROR REPORT
# ============================================================================

class TestErrorReport:
    """Testes para Error Report"""
    
    def test_generate_report_structure(self, mock_db, sample_investigations):
        """Testa estrutura do relatório de erros"""
        report = ErrorReport(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = report.generate_report()
        
        assert "period" in result
        assert "summary" in result
        assert "errors" in result
        assert "most_critical" in result
        assert "recurring_errors" in result
        assert "cost_analysis" in result
        assert "recommendations" in result
    
    def test_collect_errors(self, mock_db, sample_investigations):
        """Testa coleta de erros"""
        report = ErrorReport(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        errors = report._collect_errors(
            datetime.utcnow() - timedelta(days=30),
            datetime.utcnow(),
            None
        )
        
        assert len(errors) > 0
        for error in errors:
            assert error.error_type
            assert error.severity in ["low", "medium", "high", "critical"]
            assert error.error_count >= 0
    
    def test_error_cost_calculation(self, mock_db, sample_investigations):
        """Testa cálculo de custo de erros"""
        report = ErrorReport(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = report.generate_report()
        
        assert "cost_analysis" in result
        cost_analysis = result["cost_analysis"]
        
        assert "total_estimated_cost" in cost_analysis
        assert "by_severity" in cost_analysis
        assert cost_analysis["total_estimated_cost"] >= 0
    
    def test_recurring_errors_detection(self, mock_db, sample_investigations):
        """Testa detecção de erros recorrentes"""
        report = ErrorReport(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = report.generate_report()
        
        assert "recurring_errors" in result
        assert isinstance(result["recurring_errors"], list)


# ============================================================================
# TESTES - CONSOLIDATED REPORT
# ============================================================================

class TestManagementReportsConsolidator:
    """Testes para relatório consolidado"""
    
    def test_generate_executive_report_structure(self, mock_db, sample_investigations):
        """Testa estrutura do relatório executivo consolidado"""
        consolidator = ManagementReportsConsolidator(mock_db)
        
        # Mock das queries
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = consolidator.generate_executive_management_report()
        
        assert "generated_at" in result
        assert "period" in result
        assert "operational_health_score" in result
        assert "reports" in result
        assert "priority_actions" in result
        assert "key_metrics" in result
        assert "executive_summary" in result
    
    def test_operational_health_score(self, mock_db, sample_investigations):
        """Testa cálculo do score de saúde operacional"""
        consolidator = ManagementReportsConsolidator(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = consolidator.generate_executive_management_report()
        
        health_score = result["operational_health_score"]
        
        assert "total_score" in health_score
        assert "breakdown" in health_score
        assert "status" in health_score
        assert 0 <= health_score["total_score"] <= 100
        assert health_score["status"] in ["excellent", "good", "fair", "poor", "critical"]
    
    def test_priority_recommendations(self, mock_db, sample_investigations):
        """Testa priorização de recomendações"""
        consolidator = ManagementReportsConsolidator(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = consolidator.generate_executive_management_report()
        
        assert "priority_actions" in result
        actions = result["priority_actions"]
        
        assert isinstance(actions, list)
        assert len(actions) <= 10  # Top 10 apenas
        
        # Verificar que estão ordenadas por prioridade
        if len(actions) > 1:
            for i in range(len(actions) - 1):
                assert actions[i]["priority"] <= actions[i + 1]["priority"]
    
    def test_key_metrics_extraction(self, mock_db, sample_investigations):
        """Testa extração de métricas-chave"""
        consolidator = ManagementReportsConsolidator(mock_db)
        
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = consolidator.generate_executive_management_report()
        
        key_metrics = result["key_metrics"]
        
        assert "scrapers_success_rate" in key_metrics
        assert "system_uptime" in key_metrics
        assert "total_errors" in key_metrics
        assert "critical_errors" in key_metrics
        assert "error_cost_impact" in key_metrics
        assert "sla_compliance" in key_metrics


# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

@pytest.mark.integration
class TestManagementReportsIntegration:
    """Testes de integração dos relatórios"""
    
    def test_full_report_pipeline(self, mock_db, sample_investigations):
        """Testa pipeline completo de geração de relatórios"""
        mock_db.query().filter().all.return_value = sample_investigations
        
        # 1. Gerar ROI
        roi_report = ROIReport(mock_db)
        roi = roi_report.generate_report()
        assert "summary" in roi
        
        # 2. Gerar Custos
        cost_report = CostReport(mock_db)
        costs = cost_report.generate_report()
        assert "summary" in costs
        
        # 3. Gerar Performance
        perf_report = ScraperPerformanceReport(mock_db)
        performance = perf_report.generate_report()
        assert "summary" in performance
        
        # 4. Gerar Uptime
        uptime_report = UptimeReport(mock_db)
        uptime = uptime_report.generate_report()
        assert "summary" in uptime
        
        # 5. Gerar Erros
        error_report = ErrorReport(mock_db)
        errors = error_report.generate_report()
        assert "summary" in errors
        
        # 6. Consolidar tudo
        consolidator = ManagementReportsConsolidator(mock_db)
        executive = consolidator.generate_executive_management_report()
        
        assert "reports" in executive
        assert "performance" in executive["reports"]
        assert "uptime" in executive["reports"]
        assert "errors" in executive["reports"]


# ============================================================================
# TESTES DE PERFORMANCE
# ============================================================================

@pytest.mark.performance
class TestManagementReportsPerformance:
    """Testes de performance dos relatórios"""
    
    def test_roi_report_performance(self, mock_db, sample_investigations):
        """Testa performance do relatório de ROI"""
        import time
        
        report = ROIReport(mock_db)
        mock_db.query().filter().all.return_value = sample_investigations * 10
        
        start = time.time()
        report.generate_report()
        duration = time.time() - start
        
        assert duration < 2.0  # Deve ser rápido (< 2s)
    
    def test_consolidated_report_performance(self, mock_db, sample_investigations):
        """Testa performance do relatório consolidado"""
        import time
        
        consolidator = ManagementReportsConsolidator(mock_db)
        mock_db.query().filter().all.return_value = sample_investigations * 5
        
        start = time.time()
        consolidator.generate_executive_management_report()
        duration = time.time() - start
        
        assert duration < 5.0  # Deve ser razoavelmente rápido (< 5s)
