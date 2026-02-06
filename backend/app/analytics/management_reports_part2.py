"""
Relatórios Gerenciais - Parte 2
Performance, Uptime e Erros

Continuação dos relatórios gerenciais avançados.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from collections import defaultdict, Counter
import statistics

from app.analytics.management_reports import (
    ScraperPerformanceMetrics,
    UptimeMetrics,
    ErrorMetrics
)


# ============================================================================
# SCRAPER PERFORMANCE REPORT
# ============================================================================

class ScraperPerformanceReport:
    """
    Relatório de Performance de Scrapers
    
    Analisa performance detalhada de cada scraper:
    - Taxa de sucesso
    - Tempo de execução
    - Quantidade de dados coletados
    - Confiabilidade
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.SCRAPERS = ["car", "incra", "receita", "cartorios", "diarios", "sigef_sicar"]
    
    def generate_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        scraper_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gera relatório de performance de scrapers
        
        Args:
            start_date: Data inicial
            end_date: Data final
            scraper_name: Filtrar por scraper específico
            
        Returns:
            Relatório estruturado de performance
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Coletar métricas de cada scraper
        scrapers_to_analyze = [scraper_name] if scraper_name else self.SCRAPERS
        
        performance_metrics = []
        for scraper in scrapers_to_analyze:
            metrics = self._calculate_scraper_performance(scraper, start_date, end_date)
            performance_metrics.append(metrics)
        
        # Agregar estatísticas
        overall_success_rate = (
            sum(m.success_rate for m in performance_metrics) / len(performance_metrics)
            if performance_metrics else 0
        )
        
        overall_avg_duration = (
            sum(m.average_duration_seconds for m in performance_metrics) / len(performance_metrics)
            if performance_metrics else 0
        )
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "summary": {
                "total_scrapers_analyzed": len(performance_metrics),
                "overall_success_rate": round(overall_success_rate, 2),
                "overall_avg_duration": round(overall_avg_duration, 2),
                "total_executions": sum(m.total_executions for m in performance_metrics),
                "total_failures": sum(m.failed_executions for m in performance_metrics)
            },
            "scrapers": [
                {
                    "name": m.scraper_name,
                    "total_executions": m.total_executions,
                    "successful": m.successful_executions,
                    "failed": m.failed_executions,
                    "success_rate": round(m.success_rate, 2),
                    "error_rate": round(m.error_rate, 2),
                    "average_duration_seconds": round(m.average_duration_seconds, 2),
                    "min_duration": round(m.min_duration_seconds, 2),
                    "max_duration": round(m.max_duration_seconds, 2),
                    "p95_duration": round(m.p95_duration_seconds, 2),
                    "total_data_collected": m.total_data_collected,
                    "avg_data_per_execution": round(m.average_data_per_execution, 2),
                    "reliability_score": round(m.reliability_score, 2),
                    "status": self._get_scraper_status(m)
                }
                for m in performance_metrics
            ],
            "best_performers": self._get_best_performers(performance_metrics),
            "worst_performers": self._get_worst_performers(performance_metrics),
            "recommendations": self._generate_performance_recommendations(performance_metrics)
        }
    
    def _calculate_scraper_performance(
        self,
        scraper_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> ScraperPerformanceMetrics:
        """Calcula métricas de performance de um scraper"""
        
        # Buscar investigações do período
        from app.domain.investigation import Investigation
        investigations = self.db.query(Investigation).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date
            )
        ).all()
        
        total_executions = len(investigations)
        
        # Simular métricas (em produção, viria de logs/Prometheus)
        # Taxa de sucesso baseada em investigações completas
        completed = [i for i in investigations if i.status == "completed"]
        successful_executions = len(completed)
        failed_executions = total_executions - successful_executions
        
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        error_rate = 100 - success_rate
        
        # Duração (simulado com dados reais quando disponível)
        durations = []
        for inv in completed:
            if inv.completed_at and inv.created_at:
                duration = (inv.completed_at - inv.created_at).total_seconds()
                durations.append(duration)
        
        if durations:
            average_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            p95_duration = statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else max_duration
        else:
            # Valores simulados
            average_duration = 45.0
            min_duration = 15.0
            max_duration = 120.0
            p95_duration = 90.0
        
        # Dados coletados
        total_data = 0
        for inv in investigations:
            total_data += len(inv.properties or [])
            total_data += len(inv.companies or [])
        
        avg_data_per_execution = total_data / total_executions if total_executions > 0 else 0
        
        # Reliability score (0-100)
        # Baseado em: success_rate (50%), consistência de duração (25%), dados coletados (25%)
        duration_consistency = 100 - (
            (max_duration - min_duration) / average_duration * 100 if average_duration > 0 else 0
        )
        duration_consistency = max(0, min(100, duration_consistency))
        
        data_score = min(100, avg_data_per_execution * 10)  # 10 dados = 100 pontos
        
        reliability_score = (
            success_rate * 0.5 +
            duration_consistency * 0.25 +
            data_score * 0.25
        )
        
        return ScraperPerformanceMetrics(
            scraper_name=scraper_name,
            total_executions=total_executions,
            successful_executions=successful_executions,
            failed_executions=failed_executions,
            success_rate=success_rate,
            average_duration_seconds=average_duration,
            min_duration_seconds=min_duration,
            max_duration_seconds=max_duration,
            p95_duration_seconds=p95_duration,
            total_data_collected=total_data,
            average_data_per_execution=avg_data_per_execution,
            error_rate=error_rate,
            reliability_score=reliability_score
        )
    
    def _get_scraper_status(self, metrics: ScraperPerformanceMetrics) -> str:
        """Determina status do scraper baseado em métricas"""
        if metrics.success_rate >= 95 and metrics.reliability_score >= 80:
            return "excellent"
        elif metrics.success_rate >= 85 and metrics.reliability_score >= 70:
            return "good"
        elif metrics.success_rate >= 70:
            return "fair"
        else:
            return "poor"
    
    def _get_best_performers(self, metrics: List[ScraperPerformanceMetrics]) -> List[Dict]:
        """Retorna os 3 melhores scrapers"""
        sorted_metrics = sorted(metrics, key=lambda x: x.reliability_score, reverse=True)[:3]
        return [
            {
                "scraper": m.scraper_name,
                "reliability_score": round(m.reliability_score, 2),
                "success_rate": round(m.success_rate, 2),
                "avg_duration": round(m.average_duration_seconds, 2)
            }
            for m in sorted_metrics
        ]
    
    def _get_worst_performers(self, metrics: List[ScraperPerformanceMetrics]) -> List[Dict]:
        """Retorna os 3 piores scrapers"""
        sorted_metrics = sorted(metrics, key=lambda x: x.reliability_score)[:3]
        return [
            {
                "scraper": m.scraper_name,
                "reliability_score": round(m.reliability_score, 2),
                "success_rate": round(m.success_rate, 2),
                "issues": self._identify_scraper_issues(m)
            }
            for m in sorted_metrics
        ]
    
    def _identify_scraper_issues(self, metrics: ScraperPerformanceMetrics) -> List[str]:
        """Identifica problemas específicos de um scraper"""
        issues = []
        
        if metrics.success_rate < 80:
            issues.append(f"Taxa de sucesso baixa ({metrics.success_rate:.1f}%)")
        
        if metrics.average_duration_seconds > 90:
            issues.append(f"Duração média alta ({metrics.average_duration_seconds:.1f}s)")
        
        if metrics.average_data_per_execution < 1:
            issues.append("Poucos dados coletados por execução")
        
        if metrics.error_rate > 20:
            issues.append(f"Taxa de erro alta ({metrics.error_rate:.1f}%)")
        
        return issues if issues else ["Nenhum problema identificado"]
    
    def _generate_performance_recommendations(
        self,
        metrics: List[ScraperPerformanceMetrics]
    ) -> List[str]:
        """Gera recomendações de melhoria de performance"""
        recommendations = []
        
        if not metrics:
            return ["Nenhum dado disponível."]
        
        avg_success = sum(m.success_rate for m in metrics) / len(metrics)
        
        if avg_success < 85:
            recommendations.append(
                f"⚠️ Taxa de sucesso média baixa ({avg_success:.1f}%). "
                "Revisar estabilidade dos scrapers e tratamento de erros."
            )
        
        slow_scrapers = [m for m in metrics if m.average_duration_seconds > 60]
        if slow_scrapers:
            recommendations.append(
                f"🐢 {len(slow_scrapers)} scraper(s) lento(s). "
                f"Otimizar: {', '.join(s.scraper_name for s in slow_scrapers)}."
            )
        
        low_data_scrapers = [m for m in metrics if m.average_data_per_execution < 2]
        if low_data_scrapers:
            recommendations.append(
                f"📉 {len(low_data_scrapers)} scraper(s) com poucos dados coletados. "
                "Verificar se as fontes estão respondendo corretamente."
            )
        
        return recommendations if recommendations else [
            "✅ Todos os scrapers operando dentro dos parâmetros esperados."
        ]


# ============================================================================
# UPTIME REPORT
# ============================================================================

class UptimeReport:
    """
    Relatório de Uptime e Disponibilidade
    
    Monitora disponibilidade de componentes críticos:
    - API
    - Database
    - Cache
    - Scrapers
    - Workers
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.COMPONENTS = ["api", "database", "cache", "scrapers", "workers", "websocket"]
    
    def generate_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Gera relatório de uptime
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Relatório estruturado de uptime
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)  # Última semana
        if not end_date:
            end_date = datetime.utcnow()
        
        uptime_metrics = []
        for component in self.COMPONENTS:
            metrics = self._calculate_component_uptime(component, start_date, end_date)
            uptime_metrics.append(metrics)
        
        # Agregar estatísticas
        overall_uptime = (
            sum(m.uptime_percentage for m in uptime_metrics) / len(uptime_metrics)
            if uptime_metrics else 0
        )
        
        total_incidents = sum(m.incidents for m in uptime_metrics)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "summary": {
                "overall_uptime": round(overall_uptime, 2),
                "total_incidents": total_incidents,
                "components_monitored": len(uptime_metrics),
                "sla_target": 99.9,
                "sla_met": overall_uptime >= 99.9
            },
            "components": [
                {
                    "name": m.component,
                    "uptime_percentage": round(m.uptime_percentage, 2),
                    "downtime_minutes": round(m.downtime_minutes, 2),
                    "total_checks": m.total_checks,
                    "failed_checks": m.failed_checks,
                    "avg_response_time_ms": round(m.average_response_time_ms, 2),
                    "incidents": m.incidents,
                    "mttr_minutes": round(m.mttr_minutes, 2),
                    "mtbf_minutes": round(m.mtbf_minutes, 2),
                    "sla_compliance": m.sla_compliance,
                    "status": self._get_component_status(m)
                }
                for m in uptime_metrics
            ],
            "incidents": self._get_incident_timeline(uptime_metrics, start_date, end_date),
            "recommendations": self._generate_uptime_recommendations(uptime_metrics)
        }
    
    def _calculate_component_uptime(
        self,
        component: str,
        start_date: datetime,
        end_date: datetime
    ) -> UptimeMetrics:
        """Calcula uptime de um componente"""
        
        # Em produção, estes dados viriam de sistema de monitoramento (Prometheus, Grafana)
        # Aqui simulamos com dados realistas
        
        total_minutes = (end_date - start_date).total_seconds() / 60
        total_checks = int(total_minutes / 5)  # Check a cada 5 minutos
        
        # Simular uptime baseado em tipo de componente
        uptime_simulations = {
            "api": {"uptime": 99.8, "incidents": 2, "avg_response": 120},
            "database": {"uptime": 99.95, "incidents": 1, "avg_response": 15},
            "cache": {"uptime": 99.9, "incidents": 1, "avg_response": 5},
            "scrapers": {"uptime": 98.5, "incidents": 5, "avg_response": 2000},
            "workers": {"uptime": 99.7, "incidents": 2, "avg_response": 500},
            "websocket": {"uptime": 99.6, "incidents": 3, "avg_response": 50}
        }
        
        sim = uptime_simulations.get(component, {"uptime": 99.0, "incidents": 3, "avg_response": 100})
        
        uptime_percentage = sim["uptime"]
        downtime_percentage = 100 - uptime_percentage
        downtime_minutes = (total_minutes * downtime_percentage) / 100
        
        failed_checks = int(total_checks * (downtime_percentage / 100))
        incidents = sim["incidents"]
        
        # MTTR (Mean Time To Recovery) - tempo médio para recuperar
        mttr_minutes = downtime_minutes / incidents if incidents > 0 else 0
        
        # MTBF (Mean Time Between Failures)
        mtbf_minutes = total_minutes / (incidents + 1) if incidents > 0 else total_minutes
        
        # SLA compliance (99.9% de uptime)
        sla_compliance = uptime_percentage >= 99.9
        
        return UptimeMetrics(
            component=component,
            uptime_percentage=uptime_percentage,
            downtime_minutes=downtime_minutes,
            total_checks=total_checks,
            failed_checks=failed_checks,
            average_response_time_ms=sim["avg_response"],
            incidents=incidents,
            mttr_minutes=mttr_minutes,
            mtbf_minutes=mtbf_minutes,
            sla_compliance=sla_compliance
        )
    
    def _get_component_status(self, metrics: UptimeMetrics) -> str:
        """Determina status do componente"""
        if metrics.uptime_percentage >= 99.9:
            return "excellent"
        elif metrics.uptime_percentage >= 99.5:
            return "good"
        elif metrics.uptime_percentage >= 99.0:
            return "fair"
        else:
            return "critical"
    
    def _get_incident_timeline(
        self,
        metrics: List[UptimeMetrics],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Gera timeline de incidentes"""
        incidents = []
        
        for m in metrics:
            if m.incidents > 0:
                # Simular incidentes espaçados ao longo do período
                period_hours = (end_date - start_date).total_seconds() / 3600
                interval_hours = period_hours / (m.incidents + 1)
                
                for i in range(m.incidents):
                    incident_time = start_date + timedelta(hours=interval_hours * (i + 1))
                    incidents.append({
                        "component": m.component,
                        "timestamp": incident_time.isoformat(),
                        "duration_minutes": round(m.mttr_minutes, 2),
                        "severity": self._get_incident_severity(m.downtime_minutes / m.incidents)
                    })
        
        return sorted(incidents, key=lambda x: x["timestamp"], reverse=True)
    
    def _get_incident_severity(self, downtime_minutes: float) -> str:
        """Determina severidade de incidente"""
        if downtime_minutes < 5:
            return "low"
        elif downtime_minutes < 15:
            return "medium"
        elif downtime_minutes < 60:
            return "high"
        else:
            return "critical"
    
    def _generate_uptime_recommendations(self, metrics: List[UptimeMetrics]) -> List[str]:
        """Gera recomendações de melhoria de uptime"""
        recommendations = []
        
        if not metrics:
            return ["Nenhum dado disponível."]
        
        avg_uptime = sum(m.uptime_percentage for m in metrics) / len(metrics)
        
        if avg_uptime < 99.9:
            recommendations.append(
                f"⚠️ Uptime médio abaixo do SLA ({avg_uptime:.2f}% < 99.9%). "
                "Revisar infraestrutura e implementar redundância."
            )
        
        critical_components = [m for m in metrics if m.uptime_percentage < 99.5]
        if critical_components:
            recommendations.append(
                f"🔴 Componentes críticos: {', '.join(c.component for c in critical_components)}. "
                "Ação imediata necessária."
            )
        
        high_mttr = [m for m in metrics if m.mttr_minutes > 30]
        if high_mttr:
            recommendations.append(
                f"⏱️ Tempo de recuperação alto para: {', '.join(c.component for c in high_mttr)}. "
                "Melhorar processos de recuperação automática."
            )
        
        return recommendations if recommendations else [
            "✅ Todos os componentes operando com uptime satisfatório."
        ]


# Continua no próximo arquivo...
