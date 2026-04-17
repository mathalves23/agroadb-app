"""
Machine Learning Services for AgroADB

Provides advanced analytics for investigations:
- Risk Scoring (0-100 scale)
- Pattern Detection (10+ suspicious patterns)
- Network Analysis (NetworkX graphs)

Example:
    from app.services.ml import (
        RiskScoringEngine,
        PatternDetectionEngine,
        NetworkAnalysisEngine
    )
    
    # Calculate risk score
    risk_score = await RiskScoringEngine.calculate_risk_score(db, investigation_id)
    
    # Detect patterns
    patterns = await PatternDetectionEngine.detect_patterns(db, investigation_id)
    
    # Analyze network
    network = await NetworkAnalysisEngine.analyze_network(db, investigation_id)
"""

from app.services.ml.risk_scoring import (
    RiskScoringEngine,
    RiskScore,
    RiskIndicator,
)

from app.services.ml.pattern_detection import (
    PatternDetectionEngine,
    Pattern,
    Anomaly,
)

from app.services.ml.network_analysis import (
    NetworkAnalysisEngine,
    NetworkNode,
    NetworkEdge,
    NetworkAnalysis,
)

__all__ = [
    # Risk Scoring
    'RiskScoringEngine',
    'RiskScore',
    'RiskIndicator',
    
    # Pattern Detection
    'PatternDetectionEngine',
    'Pattern',
    'Anomaly',
    
    # Network Analysis
    'NetworkAnalysisEngine',
    'NetworkNode',
    'NetworkEdge',
    'NetworkAnalysis',
]

__version__ = '1.0.0'
__author__ = 'AgroADB Team'
