"""
Machine Learning Module for AgroADB

Este módulo contém todos os componentes de inteligência artificial e machine learning
para análise avançada de investigações patrimoniais rurais.

Componentes:
- RiskAnalyzer: Cálculo de score de risco
- PatternDetector: Detecção de padrões suspeitos
- NetworkAnalyzer: Análise de redes e relacionamentos
- OCRProcessor: Extração de texto de documentos
"""

from app.ml.models.risk_analyzer import RiskAnalyzer
from app.ml.models.pattern_detector import PatternDetector
from app.ml.models.network_analyzer import NetworkAnalyzer
from app.ml.models.ocr_processor import OCRProcessor

__all__ = [
    "RiskAnalyzer",
    "PatternDetector",
    "NetworkAnalyzer",
    "OCRProcessor",
]
