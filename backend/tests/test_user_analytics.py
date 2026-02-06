"""
Testes para User Analytics

Testes unitários e de integração para analytics de usuário.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.analytics.user_analytics import (
    FunnelAnalytics,
    FeatureAdoptionAnalytics,
    FunnelStep,
    FeatureUsage
)
from app.analytics.user_analytics_part2 import (
    HeatmapAnalytics,
    SessionRecordingAnalytics,
    NPSAnalytics,
    HeatmapPoint,
    SessionEvent,
    NPSResponse
)
from app.domain.user import User
from app.domain.investigation import Investigation
from app.domain.property import Property
from app.domain.company import Company


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock da sessão do banco"""
    return Mock(spec=Session)


@pytest.fixture
def sample_users():
    """Usuários de exemplo"""
    return [
        User(id=i, username=f"user{i}", email=f"user{i}@example.com", is_active=True, role="user")
        for i in range(1, 101)
    ]


@pytest.fixture
def sample_investigations():
    """Investigações de exemplo"""
    now = datetime.utcnow()
    invs = []
    
    for i in range(1, 51):
        inv = Investigation(
            id=i,
            user_id=(i % 10) + 1,
            cpf_cnpj=f"1234567890{i}",
            status="completed" if i % 3 != 0 else "in_progress",
            created_at=now - timedelta(days=30-i),
            updated_at=now - timedelta(days=29-i),
            completed_at=now - timedelta(days=29-i) if i % 3 != 0 else None,
            properties=[Property(id=j) for j in range(i, i+3)],
            companies=[Company(id=j) for j in range(i, i+2)]
        )
        invs.append(inv)
    
    return invs


# ============================================================================
# TESTES - FUNNEL ANALYTICS
# ============================================================================

class TestFunnelAnalytics:
    """Testes para análise de funil"""
    
    def test_analyze_funnel_structure(self, mock_db, sample_users, sample_investigations):
        """Testa estrutura da análise de funil"""
        analytics = FunnelAnalytics(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        mock_db.query().filter().all.return_value = sample_investigations
        
        funnel = analytics.analyze_funnel("investigation_creation")
        
        assert funnel.funnel_name
        assert funnel.total_users_started >= 0
        assert funnel.total_users_completed >= 0
        assert 0 <= funnel.overall_conversion_rate <= 100
        assert len(funnel.steps) > 0
        assert isinstance(funnel.bottlenecks, list)
        assert isinstance(funnel.recommendations, list)
    
    def test_funnel_steps_order(self, mock_db, sample_investigations):
        """Testa ordem das etapas do funil"""
        analytics = FunnelAnalytics(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        mock_db.query().filter().all.return_value = sample_investigations
        
        funnel = analytics.analyze_funnel("user_onboarding")
        
        # Verificar que steps estão em ordem
        for i in range(len(funnel.steps) - 1):
            assert funnel.steps[i].step_order < funnel.steps[i+1].step_order
    
    def test_funnel_conversion_calculation(self, mock_db, sample_investigations):
        """Testa cálculo de conversão"""
        analytics = FunnelAnalytics(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        mock_db.query().filter().all.return_value = sample_investigations
        
        funnel = analytics.analyze_funnel("investigation_completion")
        
        if funnel.total_users_started > 0:
            expected_conversion = (funnel.total_users_completed / funnel.total_users_started) * 100
            assert abs(funnel.overall_conversion_rate - expected_conversion) < 0.1
    
    def test_identify_bottlenecks(self, mock_db):
        """Testa identificação de gargalos"""
        analytics = FunnelAnalytics(mock_db)
        
        steps = [
            FunnelStep(
                step_name="step1",
                step_order=1,
                users_entered=100,
                users_completed=95,
                conversion_rate=95.0,
                drop_off_rate=5.0,
                average_time_seconds=30,
                median_time_seconds=25
            ),
            FunnelStep(
                step_name="step2",
                step_order=2,
                users_entered=95,
                users_completed=60,
                conversion_rate=63.2,
                drop_off_rate=36.8,  # Alto drop-off!
                average_time_seconds=45,
                median_time_seconds=40
            )
        ]
        
        bottlenecks = analytics._identify_bottlenecks(steps)
        
        assert len(bottlenecks) > 0
        assert any("step2" in b for b in bottlenecks)
    
    def test_get_funnel_comparison(self, mock_db, sample_investigations):
        """Testa comparação de funis"""
        analytics = FunnelAnalytics(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        mock_db.query().filter().all.return_value = sample_investigations
        
        now = datetime.utcnow()
        period1_start = now - timedelta(days=60)
        period1_end = now - timedelta(days=30)
        period2_start = now - timedelta(days=30)
        period2_end = now
        
        comparison = analytics.get_funnel_comparison(
            "investigation_creation",
            period1_start,
            period1_end,
            period2_start,
            period2_end
        )
        
        assert "period1" in comparison
        assert "period2" in comparison
        assert "changes" in comparison
        assert "trend" in comparison["changes"]


# ============================================================================
# TESTES - FEATURE ADOPTION
# ============================================================================

class TestFeatureAdoptionAnalytics:
    """Testes para feature adoption"""
    
    def test_analyze_feature_adoption_structure(self, mock_db, sample_investigations):
        """Testa estrutura da análise de adoção"""
        analytics = FeatureAdoptionAnalytics(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = analytics.analyze_feature_adoption()
        
        assert "period" in result
        assert "summary" in result
        assert "features" in result
        assert "top_features" in result
        assert "underperforming_features" in result
        assert "recommendations" in result
    
    def test_feature_adoption_rates(self, mock_db, sample_investigations):
        """Testa taxas de adoção"""
        analytics = FeatureAdoptionAnalytics(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        mock_db.query().filter().all.return_value = sample_investigations
        
        result = analytics.analyze_feature_adoption()
        
        for feature in result["features"]:
            assert 0 <= feature["adoption_rate"] <= 100
            assert feature["active_users"] >= 0
            assert feature["power_users"] >= 0
            assert feature["casual_users"] >= 0
    
    def test_get_user_adoption_profile(self, mock_db, sample_investigations):
        """Testa perfil de adoção de usuário"""
        analytics = FeatureAdoptionAnalytics(mock_db)
        
        user = User(id=1, username="test", email="test@example.com", is_active=True)
        mock_db.query().filter().first.return_value = user
        mock_db.query().filter().scalar.return_value = 15
        
        profile = analytics.get_user_adoption_profile(1)
        
        assert "user_id" in profile
        assert "adoption_score" in profile
        assert "user_type" in profile
        assert "features" in profile
        assert "recommendations" in profile
        assert 0 <= profile["adoption_score"] <= 100
    
    def test_user_type_classification(self, mock_db):
        """Testa classificação de tipo de usuário"""
        analytics = FeatureAdoptionAnalytics(mock_db)
        
        assert analytics._classify_user_type(8, 75) == "power_user"
        assert analytics._classify_user_type(5, 45) == "active_user"
        assert analytics._classify_user_type(2, 25) == "casual_user"
        assert analytics._classify_user_type(1, 15) == "inactive_user"


# ============================================================================
# TESTES - HEATMAP ANALYTICS
# ============================================================================

class TestHeatmapAnalytics:
    """Testes para heatmap analytics"""
    
    def test_generate_heatmap_structure(self, mock_db):
        """Testa estrutura do heatmap"""
        analytics = HeatmapAnalytics(mock_db)
        
        heatmap = analytics.generate_heatmap("/dashboard")
        
        assert heatmap.page == "/dashboard"
        assert heatmap.total_clicks >= 0
        assert heatmap.unique_users >= 0
        assert isinstance(heatmap.points, list)
        assert isinstance(heatmap.hot_zones, list)
        assert isinstance(heatmap.cold_zones, list)
    
    def test_heatmap_points_validity(self, mock_db):
        """Testa validade dos pontos do heatmap"""
        analytics = HeatmapAnalytics(mock_db)
        
        heatmap = analytics.generate_heatmap("/investigations")
        
        for point in heatmap.points:
            assert 0 <= point.x <= 100
            assert 0 <= point.y <= 100
            assert point.intensity >= 0
            assert point.page == "/investigations"
    
    def test_hot_zones_identification(self, mock_db):
        """Testa identificação de zonas quentes"""
        analytics = HeatmapAnalytics(mock_db)
        
        heatmap = analytics.generate_heatmap("/investigations/new")
        
        assert len(heatmap.hot_zones) <= 5  # Top 5
        for zone in heatmap.hot_zones:
            assert "element" in zone
            assert "click_count" in zone
            assert "average_intensity" in zone
    
    def test_compare_heatmaps(self, mock_db):
        """Testa comparação de heatmaps"""
        analytics = HeatmapAnalytics(mock_db)
        
        now = datetime.utcnow()
        comparison = analytics.compare_heatmaps(
            "/dashboard",
            now - timedelta(days=14),
            now - timedelta(days=7),
            now - timedelta(days=7),
            now
        )
        
        assert "period1" in comparison
        assert "period2" in comparison
        assert "changes" in comparison
        assert "clicks_change" in comparison["changes"]


# ============================================================================
# TESTES - SESSION RECORDING
# ============================================================================

class TestSessionRecordingAnalytics:
    """Testes para session recording"""
    
    def test_get_session_recording_structure(self, mock_db):
        """Testa estrutura da gravação de sessão"""
        analytics = SessionRecordingAnalytics(mock_db)
        
        recording = analytics.get_session_recording("test_session_123")
        
        assert recording.session_id == "test_session_123"
        assert recording.user_id > 0
        assert recording.duration_seconds >= 0
        assert recording.pages_visited >= 0
        assert isinstance(recording.events, list)
        assert recording.device_type in ["desktop", "mobile", "tablet"]
    
    def test_session_events_validity(self, mock_db):
        """Testa validade dos eventos da sessão"""
        analytics = SessionRecordingAnalytics(mock_db)
        
        recording = analytics.get_session_recording("test_session_456")
        
        for event in recording.events:
            assert event.event_type in ["click", "scroll", "input", "navigation", "error"]
            assert event.page
            assert isinstance(event.timestamp, datetime)
    
    def test_analyze_session_patterns_structure(self, mock_db):
        """Testa estrutura da análise de padrões"""
        analytics = SessionRecordingAnalytics(mock_db)
        
        patterns = analytics.analyze_session_patterns()
        
        assert "period" in patterns
        assert "summary" in patterns
        assert "popular_pages" in patterns
        assert "common_actions" in patterns
        assert "exit_points" in patterns
        assert "recommendations" in patterns
    
    def test_session_metrics_validity(self, mock_db):
        """Testa validade das métricas de sessão"""
        analytics = SessionRecordingAnalytics(mock_db)
        
        patterns = analytics.analyze_session_patterns()
        summary = patterns["summary"]
        
        assert summary["total_sessions"] >= 0
        assert summary["average_duration_seconds"] >= 0
        assert 0 <= summary["bounce_rate"] <= 100
        assert 0 <= summary["error_rate"] <= 100


# ============================================================================
# TESTES - NPS ANALYTICS
# ============================================================================

class TestNPSAnalytics:
    """Testes para NPS analytics"""
    
    def test_calculate_nps_structure(self, mock_db):
        """Testa estrutura da análise de NPS"""
        analytics = NPSAnalytics(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        
        nps = analytics.calculate_nps()
        
        assert nps.total_responses >= 0
        assert nps.detractors >= 0
        assert nps.passives >= 0
        assert nps.promoters >= 0
        assert -100 <= nps.nps_score <= 100
        assert 0 <= nps.average_score <= 10
        assert 0 <= nps.response_rate <= 100
        assert nps.trend in ["improving", "stable", "declining"]
    
    def test_nps_score_calculation(self, mock_db):
        """Testa cálculo do NPS score"""
        analytics = NPSAnalytics(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        
        nps = analytics.calculate_nps()
        
        total = nps.detractors + nps.passives + nps.promoters
        
        if total > 0:
            promoter_pct = nps.promoters / total * 100
            detractor_pct = nps.detractors / total * 100
            expected_nps = promoter_pct - detractor_pct
            
            assert abs(nps.nps_score - expected_nps) < 0.1
    
    def test_nps_response_validation(self):
        """Testa validação de resposta NPS"""
        # Score válido
        response = NPSResponse(
            user_id=1,
            score=9,
            category="promoter",
            created_at=datetime.utcnow()
        )
        assert response.score == 9
        
        # Score inválido
        with pytest.raises(ValueError):
            NPSResponse(
                user_id=1,
                score=11,  # Inválido!
                category="promoter",
                created_at=datetime.utcnow()
            )
    
    def test_get_nps_feedback_analysis_structure(self, mock_db):
        """Testa estrutura da análise de feedback"""
        analytics = NPSAnalytics(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        
        feedback = analytics.get_nps_feedback_analysis()
        
        assert "total_feedback" in feedback
        assert "feedback_rate" in feedback
        assert "promoters" in feedback
        assert "detractors" in feedback
        assert "action_items" in feedback
    
    def test_nps_by_segment(self, mock_db):
        """Testa NPS por segmento"""
        analytics = NPSAnalytics(mock_db)
        
        mock_db.query().filter().scalar.return_value = 100
        
        nps = analytics.calculate_nps()
        
        assert isinstance(nps.by_segment, dict)
        for segment, score in nps.by_segment.items():
            assert -100 <= score <= 100


# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

@pytest.mark.integration
class TestUserAnalyticsIntegration:
    """Testes de integração de user analytics"""
    
    def test_full_user_analytics_pipeline(self, mock_db, sample_users, sample_investigations):
        """Testa pipeline completo de user analytics"""
        
        mock_db.query().filter().scalar.return_value = 100
        mock_db.query().filter().all.return_value = sample_investigations
        
        # 1. Funil
        funnel_analytics = FunnelAnalytics(mock_db)
        funnel = funnel_analytics.analyze_funnel("investigation_creation")
        assert funnel.total_users_started >= 0
        
        # 2. Feature Adoption
        adoption_analytics = FeatureAdoptionAnalytics(mock_db)
        adoption = adoption_analytics.analyze_feature_adoption()
        assert "features" in adoption
        
        # 3. Heatmap
        heatmap_analytics = HeatmapAnalytics(mock_db)
        heatmap = heatmap_analytics.generate_heatmap("/dashboard")
        assert heatmap.total_clicks >= 0
        
        # 4. Session
        session_analytics = SessionRecordingAnalytics(mock_db)
        session = session_analytics.get_session_recording("test_123")
        assert session.events_count >= 0
        
        # 5. NPS
        nps_analytics = NPSAnalytics(mock_db)
        nps = nps_analytics.calculate_nps()
        assert -100 <= nps.nps_score <= 100


# ============================================================================
# TESTES DE PERFORMANCE
# ============================================================================

@pytest.mark.performance
class TestUserAnalyticsPerformance:
    """Testes de performance"""
    
    def test_funnel_analysis_performance(self, mock_db, sample_investigations):
        """Testa performance da análise de funil"""
        import time
        
        analytics = FunnelAnalytics(mock_db)
        
        mock_db.query().filter().scalar.return_value = 1000
        mock_db.query().filter().all.return_value = sample_investigations * 20
        
        start = time.time()
        analytics.analyze_funnel("investigation_creation")
        duration = time.time() - start
        
        assert duration < 2.0  # < 2 segundos
    
    def test_heatmap_generation_performance(self, mock_db):
        """Testa performance da geração de heatmap"""
        import time
        
        analytics = HeatmapAnalytics(mock_db)
        
        start = time.time()
        analytics.generate_heatmap("/dashboard")
        duration = time.time() - start
        
        assert duration < 1.0  # < 1 segundo
