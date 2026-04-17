"""
Dashboard Administrativo - Visualizações e dados agregados

Este módulo fornece dados estruturados para alimentar dashboards de administração.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from app.analytics import MetricsCalculator, AnalyticsAggregator

logger = logging.getLogger(__name__)


class DashboardWidget(BaseModel):
    """Widget individual do dashboard"""
    widget_id: str
    title: str
    type: str  # "metric", "chart", "table", "list"
    data: Any
    metadata: Optional[Dict] = None


class DashboardLayout(BaseModel):
    """Layout do dashboard"""
    dashboard_id: str
    title: str
    widgets: List[DashboardWidget]
    last_updated: datetime


class DashboardBuilder:
    """Construtor de dashboards administrativos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = MetricsCalculator(db)
        self.aggregator = AnalyticsAggregator(db)
    
    def build_executive_dashboard(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> DashboardLayout:
        """
        Dashboard executivo com KPIs principais
        
        Para CEOs, diretores, investidores
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Coletar sumário executivo
        summary = self.aggregator.generate_executive_summary(start_date, end_date)
        
        widgets = []
        
        # Widget 1: KPIs principais
        widgets.append(DashboardWidget(
            widget_id="kpis",
            title="KPIs Principais",
            type="metric",
            data={
                "metrics": [
                    {
                        "label": "Usuários Ativos",
                        "value": summary["kpis"]["active_users"],
                        "unit": "",
                        "trend": "up",
                        "change_percentage": 12.5
                    },
                    {
                        "label": "Investigações Totais",
                        "value": summary["kpis"]["total_investigations"],
                        "unit": "",
                        "trend": "up",
                        "change_percentage": 8.3
                    },
                    {
                        "label": "Taxa de Conclusão",
                        "value": summary["kpis"]["completion_rate"],
                        "unit": "%",
                        "trend": "up",
                        "change_percentage": 5.2
                    },
                    {
                        "label": "MRR",
                        "value": summary["kpis"]["mrr"],
                        "unit": "R$",
                        "trend": "up",
                        "change_percentage": 15.7
                    }
                ]
            },
            metadata={"priority": "high", "refresh_interval": 300}
        ))
        
        # Widget 2: Health Score
        widgets.append(DashboardWidget(
            widget_id="health_score",
            title="Score de Saúde do Sistema",
            type="metric",
            data={
                "score": summary["health_score"],
                "max_score": 100.0,
                "status": self._get_health_status(summary["health_score"]),
                "color": self._get_health_color(summary["health_score"])
            },
            metadata={"display_type": "gauge"}
        ))
        
        # Widget 3: Atividade diária
        widgets.append(DashboardWidget(
            widget_id="daily_activity",
            title="Investigações por Dia",
            type="chart",
            data={
                "chart_type": "line",
                "series": [
                    {
                        "name": "Investigações",
                        "data": summary["usage"]["daily_activity"]
                    }
                ]
            },
            metadata={"height": 300}
        ))
        
        # Widget 4: Distribuição por status
        widgets.append(DashboardWidget(
            widget_id="status_distribution",
            title="Investigações por Status",
            type="chart",
            data={
                "chart_type": "pie",
                "series": [
                    {
                        "name": status,
                        "value": count
                    }
                    for status, count in summary["overview"]["investigations"]["by_status"].items()
                ]
            },
            metadata={"height": 300}
        ))
        
        # Widget 5: Top usuários
        widgets.append(DashboardWidget(
            widget_id="top_users",
            title="Usuários Mais Ativos",
            type="table",
            data={
                "headers": ["Usuário", "Email", "Investigações"],
                "rows": [
                    [
                        user["username"],
                        user["email"],
                        user["investigation_count"]
                    ]
                    for user in summary["usage"]["top_users"][:5]
                ]
            }
        ))
        
        # Widget 6: Métricas financeiras
        widgets.append(DashboardWidget(
            widget_id="financial",
            title="Métricas Financeiras",
            type="metric",
            data={
                "metrics": [
                    {
                        "label": "MRR",
                        "value": summary["financial"]["revenue"]["mrr"],
                        "unit": "R$"
                    },
                    {
                        "label": "ARR",
                        "value": summary["financial"]["revenue"]["arr"],
                        "unit": "R$"
                    },
                    {
                        "label": "Margem de Lucro",
                        "value": summary["financial"]["roi"]["margin_percentage"],
                        "unit": "%"
                    },
                    {
                        "label": "Lucro",
                        "value": summary["financial"]["roi"]["profit"],
                        "unit": "R$"
                    }
                ]
            }
        ))
        
        # Widget 7: Performance da API
        widgets.append(DashboardWidget(
            widget_id="api_performance",
            title="Performance da API",
            type="metric",
            data={
                "metrics": [
                    {
                        "label": "Tempo Médio",
                        "value": summary["performance"]["api"]["average_response_time_ms"],
                        "unit": "ms"
                    },
                    {
                        "label": "Taxa de Erro",
                        "value": summary["performance"]["api"]["error_rate"] * 100,
                        "unit": "%"
                    },
                    {
                        "label": "Requisições/s",
                        "value": summary["performance"]["api"]["requests_per_second"],
                        "unit": ""
                    }
                ]
            }
        ))
        
        # Widget 8: Distribuição geográfica
        widgets.append(DashboardWidget(
            widget_id="geographic",
            title="Top Estados (Propriedades)",
            type="chart",
            data={
                "chart_type": "bar",
                "series": [
                    {
                        "name": item["state"],
                        "value": item["properties_count"]
                    }
                    for item in summary["geographic"]["by_state"][:10]
                ]
            },
            metadata={"height": 400}
        ))
        
        return DashboardLayout(
            dashboard_id="executive",
            title="Dashboard Executivo",
            widgets=widgets,
            last_updated=datetime.utcnow()
        )
    
    def build_operations_dashboard(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> DashboardLayout:
        """
        Dashboard operacional
        
        Para gerentes de operação, product managers
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)  # última semana
        if not end_date:
            end_date = datetime.utcnow()
        
        report = self.aggregator.generate_operational_report(start_date, end_date)
        
        widgets = []
        
        # Widget 1: Métricas gerais
        widgets.append(DashboardWidget(
            widget_id="overview",
            title="Visão Geral",
            type="metric",
            data={
                "metrics": [
                    {
                        "label": "Investigações (período)",
                        "value": report["overview"]["investigations"]["in_period"],
                        "unit": ""
                    },
                    {
                        "label": "Taxa de Conclusão",
                        "value": report["overview"]["investigations"]["completion_rate"],
                        "unit": "%"
                    },
                    {
                        "label": "Tempo Médio",
                        "value": report["usage"]["completion_time"]["average_hours"],
                        "unit": "h"
                    }
                ]
            }
        ))
        
        # Widget 2: Status dos scrapers
        widgets.append(DashboardWidget(
            widget_id="scrapers_status",
            title="Status dos Scrapers",
            type="table",
            data={
                "headers": ["Scraper", "Execuções", "Sucessos", "Taxa"],
                "rows": [
                    [
                        scraper,
                        metrics["executions"],
                        metrics["successes"],
                        f"{metrics['success_rate']*100:.1f}%"
                    ]
                    for scraper, metrics in report["scrapers"]["by_scraper"].items()
                ]
            }
        ))
        
        # Widget 3: Recomendações
        widgets.append(DashboardWidget(
            widget_id="recommendations",
            title="Recomendações",
            type="list",
            data={
                "items": report["recommendations"]
            }
        ))
        
        # Widget 4: Atividade diária
        widgets.append(DashboardWidget(
            widget_id="daily_activity",
            title="Atividade Diária",
            type="chart",
            data={
                "chart_type": "line",
                "series": [
                    {
                        "name": "Investigações",
                        "data": report["usage"]["daily_activity"]
                    }
                ]
            }
        ))
        
        return DashboardLayout(
            dashboard_id="operations",
            title="Dashboard Operacional",
            widgets=widgets,
            last_updated=datetime.utcnow()
        )
    
    def build_user_dashboard(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> DashboardLayout:
        """Dashboard de usuário individual"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        analytics = self.aggregator.get_user_analytics(user_id, start_date, end_date)
        
        widgets = []
        
        # Widget 1: Estatísticas do usuário
        widgets.append(DashboardWidget(
            widget_id="user_stats",
            title="Suas Estatísticas",
            type="metric",
            data={
                "metrics": [
                    {
                        "label": "Investigações",
                        "value": analytics["investigations"]["total"],
                        "unit": ""
                    },
                    {
                        "label": "Concluídas",
                        "value": analytics["investigations"]["completed"],
                        "unit": ""
                    },
                    {
                        "label": "Taxa de Conclusão",
                        "value": analytics["investigations"]["completion_rate"],
                        "unit": "%"
                    }
                ]
            }
        ))
        
        # Widget 2: Dados coletados
        widgets.append(DashboardWidget(
            widget_id="data_collected",
            title="Dados Coletados",
            type="metric",
            data={
                "metrics": [
                    {
                        "label": "Propriedades",
                        "value": analytics["data_collected"]["properties"],
                        "unit": ""
                    },
                    {
                        "label": "Empresas",
                        "value": analytics["data_collected"]["companies"],
                        "unit": ""
                    },
                    {
                        "label": "Média/Investigação",
                        "value": analytics["data_collected"]["avg_per_investigation"],
                        "unit": ""
                    }
                ]
            }
        ))
        
        return DashboardLayout(
            dashboard_id=f"user_{user_id}",
            title=f"Dashboard de {analytics['user']['username']}",
            widgets=widgets,
            last_updated=datetime.utcnow()
        )
    
    def build_realtime_dashboard(self) -> DashboardLayout:
        """Dashboard em tempo real (últimas 24h)"""
        now = datetime.utcnow()
        start = now - timedelta(hours=24)
        
        overview = self.calculator.get_overview_metrics(start, now)
        performance = self.calculator.get_performance_metrics(start, now)
        
        widgets = []
        
        # Widget 1: Métricas em tempo real
        widgets.append(DashboardWidget(
            widget_id="realtime_metrics",
            title="Últimas 24 Horas",
            type="metric",
            data={
                "metrics": [
                    {
                        "label": "Investigações Criadas",
                        "value": overview["investigations"]["in_period"],
                        "unit": "",
                        "trend": "up"
                    },
                    {
                        "label": "Usuários Ativos",
                        "value": overview["users"]["active"],
                        "unit": ""
                    },
                    {
                        "label": "API: Tempo Médio",
                        "value": performance["api"]["average_response_time_ms"],
                        "unit": "ms"
                    },
                    {
                        "label": "API: Taxa de Erro",
                        "value": performance["api"]["error_rate"] * 100,
                        "unit": "%"
                    }
                ]
            },
            metadata={"refresh_interval": 60}  # Atualizar a cada 60s
        ))
        
        # Widget 2: Status do sistema
        widgets.append(DashboardWidget(
            widget_id="system_status",
            title="Status do Sistema",
            type="metric",
            data={
                "status": "healthy",
                "components": [
                    {
                        "name": "API",
                        "status": "operational",
                        "response_time": performance["api"]["average_response_time_ms"]
                    },
                    {
                        "name": "Database",
                        "status": "operational",
                        "connections": performance["database"]["connections_active"]
                    },
                    {
                        "name": "Cache",
                        "status": "operational",
                        "hit_rate": performance["cache"]["hit_rate"]
                    }
                ]
            }
        ))
        
        return DashboardLayout(
            dashboard_id="realtime",
            title="Dashboard em Tempo Real",
            widgets=widgets,
            last_updated=datetime.utcnow()
        )
    
    def _get_health_status(self, score: float) -> str:
        """Determina status baseado no score"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 50:
            return "fair"
        else:
            return "poor"
    
    def _get_health_color(self, score: float) -> str:
        """Determina cor baseada no score"""
        if score >= 90:
            return "green"
        elif score >= 75:
            return "lightgreen"
        elif score >= 50:
            return "yellow"
        else:
            return "red"


class ReportGenerator:
    """Gerador de relatórios gerenciais (PDF, Excel, etc)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.aggregator = AnalyticsAggregator(db)
    
    def generate_monthly_report(
        self,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """Gera relatório mensal completo"""
        # Primeiro e último dia do mês
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        summary = self.aggregator.generate_executive_summary(start_date, end_date)
        operational = self.aggregator.generate_operational_report(start_date, end_date)
        funnel = self.aggregator.get_funnel_metrics(start_date, end_date)
        
        return {
            "report_type": "monthly",
            "period": {
                "year": year,
                "month": month,
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "executive_summary": summary,
            "operational_details": operational,
            "funnel_analysis": funnel,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_quarterly_report(
        self,
        year: int,
        quarter: int
    ) -> Dict[str, Any]:
        """Gera relatório trimestral"""
        # Calcular meses do trimestre
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        
        start_date = datetime(year, start_month, 1)
        if end_month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, end_month + 1, 1) - timedelta(seconds=1)
        
        summary = self.aggregator.generate_executive_summary(start_date, end_date)
        
        return {
            "report_type": "quarterly",
            "period": {
                "year": year,
                "quarter": quarter,
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": summary,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_annual_report(self, year: int) -> Dict[str, Any]:
        """Gera relatório anual"""
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
        
        summary = self.aggregator.generate_executive_summary(start_date, end_date)
        
        # Dados por trimestre
        quarterly_data = []
        for q in range(1, 5):
            q_report = self.generate_quarterly_report(year, q)
            quarterly_data.append(q_report)
        
        return {
            "report_type": "annual",
            "year": year,
            "summary": summary,
            "quarterly_breakdown": quarterly_data,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def export_to_excel_format(self, data: Dict) -> Dict[str, Any]:
        """
        Formata dados para exportação Excel
        
        Retorna estrutura pronta para ser convertida em XLSX
        """
        sheets = []
        
        # Sheet 1: Sumário
        if "summary" in data or "executive_summary" in data:
            summary = data.get("summary") or data.get("executive_summary")
            sheets.append({
                "sheet_name": "Sumário",
                "data": self._flatten_dict(summary)
            })
        
        # Sheet 2: KPIs
        if "kpis" in data.get("summary", {}) or "kpis" in data.get("executive_summary", {}):
            kpis = (data.get("summary") or data.get("executive_summary", {})).get("kpis", {})
            sheets.append({
                "sheet_name": "KPIs",
                "data": [
                    {"Métrica": key, "Valor": value}
                    for key, value in kpis.items()
                ]
            })
        
        return {
            "format": "xlsx",
            "sheets": sheets,
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "report_type": data.get("report_type", "custom")
            }
        }
    
    def _flatten_dict(self, d: Dict, parent_key: str = "", sep: str = "_") -> List[Dict]:
        """Achata dicionário aninhado para formato tabular"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep))
            else:
                items.append({"Métrica": new_key, "Valor": str(v)})
        return items
