"""
Management Reports - Relatórios Gerenciais Consolidados

Módulo unificado com todos os 5 relatórios gerenciais:
1. ROI por investigação
2. Custo por investigação
3. Performance de scrapers
4. Uptime e disponibilidade
5. Erros e falhas

Importa e consolida todas as funcionalidades dos arquivos separados.
"""

# Importar classes base
from app.analytics.management_reports import (
    ROIReport,
    CostReport,
    ReportPeriod,
    ROIMetrics,
    CostMetrics,
    ScraperPerformanceMetrics,
    UptimeMetrics,
    ErrorMetrics
)

from app.analytics.management_reports_part2 import (
    ScraperPerformanceReport,
    UptimeReport
)

from app.analytics.management_reports_part3 import (
    ErrorReport,
    ManagementReportsConsolidator
)

__all__ = [
    "ROIReport",
    "CostReport",
    "ScraperPerformanceReport",
    "UptimeReport",
    "ErrorReport",
    "ManagementReportsConsolidator",
    "ReportPeriod",
    "ROIMetrics",
    "CostMetrics",
    "ScraperPerformanceMetrics",
    "UptimeMetrics",
    "ErrorMetrics"
]
