"""
User Analytics - Módulo Consolidado

Import único para todas as funcionalidades de User Analytics.
"""

# Funnel + Feature Adoption
from app.analytics.user_analytics import (
    FunnelAnalytics,
    FeatureAdoptionAnalytics,
    FunnelStep,
    FunnelAnalysis,
    FeatureUsage,
    FeatureAdoptionStatus
)

# Heatmaps + Sessions + NPS
from app.analytics.user_analytics_part2 import (
    HeatmapAnalytics,
    SessionRecordingAnalytics,
    NPSAnalytics,
    HeatmapPoint,
    HeatmapData,
    SessionEvent,
    SessionRecording,
    NPSResponse,
    NPSAnalysis
)

__all__ = [
    # Classes
    "FunnelAnalytics",
    "FeatureAdoptionAnalytics",
    "HeatmapAnalytics",
    "SessionRecordingAnalytics",
    "NPSAnalytics",
    
    # Models - Funnel
    "FunnelStep",
    "FunnelAnalysis",
    
    # Models - Feature Adoption
    "FeatureUsage",
    "FeatureAdoptionStatus",
    
    # Models - Heatmap
    "HeatmapPoint",
    "HeatmapData",
    
    # Models - Session
    "SessionEvent",
    "SessionRecording",
    
    # Models - NPS
    "NPSResponse",
    "NPSAnalysis"
]


# Quick access examples
"""
# Funnel
from app.analytics.user_analytics_consolidated import FunnelAnalytics
funnel = FunnelAnalytics(db)
result = funnel.analyze_funnel("investigation_creation")

# Feature Adoption
from app.analytics.user_analytics_consolidated import FeatureAdoptionAnalytics
adoption = FeatureAdoptionAnalytics(db)
result = adoption.analyze_feature_adoption()

# Heatmap
from app.analytics.user_analytics_consolidated import HeatmapAnalytics
heatmap = HeatmapAnalytics(db)
result = heatmap.generate_heatmap("/dashboard")

# Session
from app.analytics.user_analytics_consolidated import SessionRecordingAnalytics
session = SessionRecordingAnalytics(db)
result = session.get_session_recording("session_123")

# NPS
from app.analytics.user_analytics_consolidated import NPSAnalytics
nps = NPSAnalytics(db)
result = nps.calculate_nps()
"""
