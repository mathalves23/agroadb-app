"""
Relatórios Gerenciais - Geração de relatórios customizados

Este módulo permite criar relatórios personalizados com filtros, agrupamentos e visualizações.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.analytics import AnalyticsAggregator, MetricsCalculator
from app.analytics.dashboard import ReportGenerator

logger = logging.getLogger(__name__)


class ReportFormat(str, Enum):
    """Formatos de exportação"""

    JSON = "json"
    EXCEL = "excel"
    CSV = "csv"
    PDF = "pdf"


class ReportPeriod(str, Enum):
    """Períodos pré-definidos"""

    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_QUARTER = "this_quarter"
    LAST_QUARTER = "last_quarter"
    THIS_YEAR = "this_year"
    LAST_YEAR = "last_year"
    CUSTOM = "custom"


class ReportType(str, Enum):
    """Tipos de relatório"""

    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    PERFORMANCE = "performance"
    USAGE = "usage"
    CUSTOM = "custom"


class ReportFilter(BaseModel):
    """Filtros para relatórios"""

    user_ids: Optional[List[int]] = None
    status: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_investigations: Optional[int] = None
    include_inactive: bool = False


class ReportConfig(BaseModel):
    """Configuração de relatório personalizado"""

    report_id: str
    title: str
    report_type: ReportType
    period: ReportPeriod
    custom_start: Optional[datetime] = None
    custom_end: Optional[datetime] = None
    filters: Optional[ReportFilter] = None
    metrics: List[str] = Field(default_factory=list)  # Métricas específicas
    group_by: Optional[str] = None  # Agrupar por: "day", "week", "month", "user", "status"
    format: ReportFormat = ReportFormat.JSON


class CustomReportBuilder:
    """Construtor de relatórios personalizados"""

    def __init__(self, db: Session):
        self.db = db
        self.calculator = MetricsCalculator(db)
        self.aggregator = AnalyticsAggregator(db)
        self.generator = ReportGenerator(db)

    def generate_report(self, config: ReportConfig) -> Dict[str, Any]:
        """
        Gera relatório baseado na configuração fornecida

        Args:
            config: Configuração do relatório

        Returns:
            Relatório estruturado
        """
        # Calcular período
        start_date, end_date = self._calculate_period(
            config.period, config.custom_start, config.custom_end
        )

        # Construir relatório baseado no tipo
        if config.report_type == ReportType.EXECUTIVE:
            data = self.aggregator.generate_executive_summary(start_date, end_date)
        elif config.report_type == ReportType.OPERATIONAL:
            data = self.aggregator.generate_operational_report(start_date, end_date)
        elif config.report_type == ReportType.FINANCIAL:
            data = self._build_financial_report(start_date, end_date, config)
        elif config.report_type == ReportType.PERFORMANCE:
            data = self._build_performance_report(start_date, end_date, config)
        elif config.report_type == ReportType.USAGE:
            data = self._build_usage_report(start_date, end_date, config)
        else:  # CUSTOM
            data = self._build_custom_report(start_date, end_date, config)

        # Aplicar filtros
        if config.filters:
            data = self._apply_filters(data, config.filters)

        # Aplicar agrupamento
        if config.group_by:
            data = self._apply_grouping(data, config.group_by, start_date, end_date)

        # Formatar resultado
        report = {
            "report_id": config.report_id,
            "title": config.title,
            "type": config.report_type.value,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "description": self._get_period_description(config.period),
            },
            "generated_at": datetime.utcnow().isoformat(),
            "data": data,
        }

        # Exportar no formato solicitado
        if config.format == ReportFormat.EXCEL:
            return self.generator.export_to_excel_format(report)
        elif config.format == ReportFormat.CSV:
            return self._export_to_csv(report)
        elif config.format == ReportFormat.PDF:
            return self._prepare_for_pdf(report)
        else:  # JSON
            return report

    def _calculate_period(
        self, period: ReportPeriod, custom_start: Optional[datetime], custom_end: Optional[datetime]
    ) -> Tuple[datetime, datetime]:
        """Calcula datas de início e fim baseado no período"""
        now = datetime.utcnow()

        if period == ReportPeriod.CUSTOM:
            if not custom_start or not custom_end:
                raise ValueError("Custom period requires custom_start and custom_end")
            return custom_start, custom_end

        elif period == ReportPeriod.TODAY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return start, now

        elif period == ReportPeriod.YESTERDAY:
            yesterday = now - timedelta(days=1)
            start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end = yesterday.replace(hour=23, minute=59, second=59)
            return start, end

        elif period == ReportPeriod.LAST_7_DAYS:
            start = now - timedelta(days=7)
            return start, now

        elif period == ReportPeriod.LAST_30_DAYS:
            start = now - timedelta(days=30)
            return start, now

        elif period == ReportPeriod.THIS_MONTH:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return start, now

        elif period == ReportPeriod.LAST_MONTH:
            first_this_month = now.replace(day=1)
            last_month_end = first_this_month - timedelta(seconds=1)
            last_month_start = last_month_end.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            return last_month_start, last_month_end

        elif period == ReportPeriod.THIS_QUARTER:
            quarter = (now.month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            start = now.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            return start, now

        elif period == ReportPeriod.LAST_QUARTER:
            current_quarter = (now.month - 1) // 3 + 1
            last_quarter = current_quarter - 1 if current_quarter > 1 else 4
            year = now.year if current_quarter > 1 else now.year - 1
            start_month = (last_quarter - 1) * 3 + 1
            end_month = start_month + 2

            start = datetime(year, start_month, 1)
            if end_month == 12:
                end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
            else:
                end = datetime(year, end_month + 1, 1) - timedelta(seconds=1)
            return start, end

        elif period == ReportPeriod.THIS_YEAR:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return start, now

        elif period == ReportPeriod.LAST_YEAR:
            start = datetime(now.year - 1, 1, 1)
            end = datetime(now.year - 1, 12, 31, 23, 59, 59)
            return start, end

        else:
            raise ValueError(f"Unknown period: {period}")

    def _get_period_description(self, period: ReportPeriod) -> str:
        """Retorna descrição legível do período"""
        descriptions = {
            ReportPeriod.TODAY: "Hoje",
            ReportPeriod.YESTERDAY: "Ontem",
            ReportPeriod.LAST_7_DAYS: "Últimos 7 dias",
            ReportPeriod.LAST_30_DAYS: "Últimos 30 dias",
            ReportPeriod.THIS_MONTH: "Este mês",
            ReportPeriod.LAST_MONTH: "Mês passado",
            ReportPeriod.THIS_QUARTER: "Este trimestre",
            ReportPeriod.LAST_QUARTER: "Trimestre passado",
            ReportPeriod.THIS_YEAR: "Este ano",
            ReportPeriod.LAST_YEAR: "Ano passado",
            ReportPeriod.CUSTOM: "Período personalizado",
        }
        return descriptions.get(period, "Desconhecido")

    def _build_financial_report(
        self, start_date: datetime, end_date: datetime, config: ReportConfig
    ) -> Dict[str, Any]:
        """Constrói relatório financeiro detalhado"""
        financial = self.calculator.get_financial_metrics(start_date, end_date)
        overview = self.calculator.get_overview_metrics(start_date, end_date)

        return {
            "financial_summary": financial,
            "user_metrics": {
                "total_users": overview["users"]["total"],
                "active_users": overview["users"]["active"],
                "new_users": overview["users"]["new_in_period"],
            },
            "revenue_analysis": {
                "mrr": financial["revenue"]["mrr"],
                "arr": financial["revenue"]["arr"],
                "arpu": round(financial["revenue"]["mrr"] / max(overview["users"]["active"], 1), 2),
            },
            "cost_analysis": {
                "total_cost": financial["period_metrics"]["total_cost"],
                "cost_per_investigation": financial["period_metrics"]["cost_per_investigation"],
                "cost_per_user": round(
                    financial["period_metrics"]["total_cost"] / max(overview["users"]["active"], 1),
                    2,
                ),
            },
            "profitability": financial["roi"],
        }

    def _build_performance_report(
        self, start_date: datetime, end_date: datetime, config: ReportConfig
    ) -> Dict[str, Any]:
        """Constrói relatório de performance"""
        performance = self.calculator.get_performance_metrics(start_date, end_date)
        scrapers = self.calculator.get_scrapers_metrics(start_date, end_date)

        return {
            "api_performance": performance["api"],
            "database_performance": performance["database"],
            "cache_performance": performance["cache"],
            "scrapers_performance": {
                "total_executions": scrapers["total_executions"],
                "success_rate": round(
                    (scrapers["total_successes"] / max(scrapers["total_executions"], 1)) * 100, 2
                ),
                "average_duration": scrapers["average_duration_seconds"],
                "by_scraper": scrapers["by_scraper"],
            },
            "recommendations": self._generate_performance_recommendations(performance, scrapers),
        }

    def _build_usage_report(
        self, start_date: datetime, end_date: datetime, config: ReportConfig
    ) -> Dict[str, Any]:
        """Constrói relatório de uso"""
        usage = self.calculator.get_usage_metrics(start_date, end_date)
        overview = self.calculator.get_overview_metrics(start_date, end_date)
        funnel = self.aggregator.get_funnel_metrics(start_date, end_date)

        return {
            "overview": overview,
            "usage_details": usage,
            "funnel_analysis": funnel,
            "engagement_metrics": {
                "active_users": overview["users"]["active"],
                "investigations_per_user": round(
                    overview["investigations"]["in_period"] / max(overview["users"]["active"], 1), 2
                ),
                "completion_rate": overview["investigations"]["completion_rate"],
                "avg_completion_time": usage["completion_time"]["average_hours"],
            },
        }

    def _build_custom_report(
        self, start_date: datetime, end_date: datetime, config: ReportConfig
    ) -> Dict[str, Any]:
        """Constrói relatório customizado com métricas específicas"""
        data = {}

        # Coletar apenas as métricas solicitadas
        available_metrics = {
            "overview": lambda: self.calculator.get_overview_metrics(start_date, end_date),
            "usage": lambda: self.calculator.get_usage_metrics(start_date, end_date),
            "scrapers": lambda: self.calculator.get_scrapers_metrics(start_date, end_date),
            "geographic": lambda: self.calculator.get_geographic_metrics(),
            "performance": lambda: self.calculator.get_performance_metrics(start_date, end_date),
            "financial": lambda: self.calculator.get_financial_metrics(start_date, end_date),
            "funnel": lambda: self.aggregator.get_funnel_metrics(start_date, end_date),
        }

        for metric in config.metrics:
            if metric in available_metrics:
                data[metric] = available_metrics[metric]()

        # Se nenhuma métrica especificada, incluir todas
        if not config.metrics:
            for metric, func in available_metrics.items():
                data[metric] = func()

        return data

    def _apply_filters(self, data: Dict, filters: ReportFilter) -> Dict:
        """Aplica filtros aos dados do relatório"""
        # Esta é uma implementação simplificada
        # Em produção, você aplicaria filtros mais sofisticados

        filtered_data = data.copy()

        # Exemplo: filtrar por status
        if filters.status and "overview" in filtered_data:
            if "investigations" in filtered_data["overview"]:
                by_status = filtered_data["overview"]["investigations"].get("by_status", {})
                filtered_by_status = {k: v for k, v in by_status.items() if k in filters.status}
                filtered_data["overview"]["investigations"]["by_status"] = filtered_by_status

        return filtered_data

    def _apply_grouping(
        self, data: Dict, group_by: str, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Agrupa dados por período ou dimensão"""
        grouped_data = data.copy()

        if group_by in ["day", "week", "month"]:
            # Adicionar agrupamento temporal
            grouped_data["grouped_by"] = group_by

            if "usage" in data and "daily_activity" in data["usage"]:
                daily = data["usage"]["daily_activity"]

                if group_by == "week":
                    # Agrupar por semana
                    weekly = {}
                    for item in daily:
                        date = datetime.fromisoformat(item["date"])
                        week = date.isocalendar()[1]
                        year = date.isocalendar()[0]
                        key = f"{year}-W{week:02d}"
                        weekly[key] = weekly.get(key, 0) + item["count"]

                    grouped_data["usage"]["weekly_activity"] = [
                        {"week": week, "count": count} for week, count in weekly.items()
                    ]

                elif group_by == "month":
                    # Agrupar por mês
                    monthly = {}
                    for item in daily:
                        date = datetime.fromisoformat(item["date"])
                        key = f"{date.year}-{date.month:02d}"
                        monthly[key] = monthly.get(key, 0) + item["count"]

                    grouped_data["usage"]["monthly_activity"] = [
                        {"month": month, "count": count} for month, count in monthly.items()
                    ]

        return grouped_data

    def _generate_performance_recommendations(self, performance: Dict, scrapers: Dict) -> List[str]:
        """Gera recomendações de performance"""
        recommendations = []

        # API
        avg_response = performance["api"]["average_response_time_ms"]
        if avg_response > 200:
            recommendations.append(
                f"⚡ Tempo de resposta da API alto ({avg_response}ms). "
                "Considerar otimização de queries ou adicionar cache."
            )

        error_rate = performance["api"]["error_rate"]
        if error_rate > 0.05:
            recommendations.append(
                f"⚠️ Taxa de erro da API alta ({error_rate:.1%}). "
                "Investigar logs para identificar causas."
            )

        # Database
        slow_queries = performance["database"]["slow_queries"]
        if slow_queries > 10:
            recommendations.append(
                f"🐢 {slow_queries} queries lentas detectadas. "
                "Revisar índices do banco de dados."
            )

        # Cache
        hit_rate = performance["cache"]["hit_rate"]
        if hit_rate < 0.7:
            recommendations.append(
                f"💾 Taxa de acerto do cache baixa ({hit_rate:.1%}). "
                "Revisar estratégia de cache."
            )

        # Scrapers
        if scrapers["total_executions"] > 0:
            success_rate = scrapers["total_successes"] / scrapers["total_executions"]
            if success_rate < 0.8:
                recommendations.append(
                    f"🔧 Taxa de sucesso dos scrapers baixa ({success_rate:.1%}). "
                    "Verificar estabilidade e tratamento de erros."
                )

        if not recommendations:
            recommendations.append("✅ Performance dentro dos parâmetros esperados.")

        return recommendations

    def _export_to_csv(self, report: Dict) -> Dict[str, Any]:
        """Prepara dados para exportação CSV"""
        return {
            "format": "csv",
            "data": self._flatten_for_csv(report["data"]),
            "metadata": {
                "report_id": report["report_id"],
                "title": report["title"],
                "generated_at": report["generated_at"],
            },
        }

    def _flatten_for_csv(self, data: Dict, prefix: str = "") -> List[Dict]:
        """Achata estrutura para CSV"""
        rows = []
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                rows.extend(self._flatten_for_csv(value, full_key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        rows.extend(self._flatten_for_csv(item, f"{full_key}[{i}]"))
                    else:
                        rows.append({"key": f"{full_key}[{i}]", "value": str(item)})
            else:
                rows.append({"key": full_key, "value": str(value)})
        return rows

    def _prepare_for_pdf(self, report: Dict) -> Dict[str, Any]:
        """Prepara dados para geração de PDF"""
        return {
            "format": "pdf",
            "template": "report_template",
            "data": report,
            "metadata": {
                "title": report["title"],
                "generated_at": report["generated_at"],
                "page_size": "A4",
                "orientation": "portrait",
            },
        }


class ScheduledReports:
    """Gerenciador de relatórios agendados"""

    def __init__(self, db: Session):
        self.db = db
        self.builder = CustomReportBuilder(db)

    def schedule_report(
        self,
        config: ReportConfig,
        schedule: str,  # cron-like: "0 9 * * 1" (toda segunda às 9h)
        recipients: List[str],  # emails
    ) -> Dict[str, Any]:
        """
        Agenda relatório para ser gerado e enviado automaticamente

        Args:
            config: Configuração do relatório
            schedule: Expressão cron
            recipients: Lista de emails destinatários

        Returns:
            Informações do agendamento
        """
        # Esta é uma implementação simplificada
        # Em produção, você usaria Celery Beat ou similar

        return {
            "schedule_id": f"sched_{config.report_id}_{datetime.utcnow().timestamp()}",
            "report_config": config.dict(),
            "schedule": schedule,
            "recipients": recipients,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "next_run": self._calculate_next_run(schedule),
        }

    def _calculate_next_run(self, schedule: str) -> str:
        """Calcula próxima execução (simplificado)"""
        # Em produção, usar croniter ou similar
        return (datetime.utcnow() + timedelta(days=1)).isoformat()


class ReportTemplates:
    """Templates pré-definidos de relatórios"""

    @staticmethod
    def get_weekly_executive_summary() -> ReportConfig:
        """Template: Sumário executivo semanal"""
        return ReportConfig(
            report_id="weekly_executive",
            title="Sumário Executivo Semanal",
            report_type=ReportType.EXECUTIVE,
            period=ReportPeriod.LAST_7_DAYS,
            format=ReportFormat.EXCEL,
        )

    @staticmethod
    def get_monthly_financial_report() -> ReportConfig:
        """Template: Relatório financeiro mensal"""
        return ReportConfig(
            report_id="monthly_financial",
            title="Relatório Financeiro Mensal",
            report_type=ReportType.FINANCIAL,
            period=ReportPeriod.LAST_MONTH,
            format=ReportFormat.EXCEL,
        )

    @staticmethod
    def get_daily_operations_report() -> ReportConfig:
        """Template: Relatório operacional diário"""
        return ReportConfig(
            report_id="daily_operations",
            title="Relatório Operacional Diário",
            report_type=ReportType.OPERATIONAL,
            period=ReportPeriod.YESTERDAY,
            format=ReportFormat.JSON,
        )

    @staticmethod
    def get_quarterly_performance_report() -> ReportConfig:
        """Template: Relatório de performance trimestral"""
        return ReportConfig(
            report_id="quarterly_performance",
            title="Relatório de Performance Trimestral",
            report_type=ReportType.PERFORMANCE,
            period=ReportPeriod.LAST_QUARTER,
            format=ReportFormat.PDF,
        )
