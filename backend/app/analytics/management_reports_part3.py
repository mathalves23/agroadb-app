"""
Relatórios Gerenciais - Parte 3
Erros e Falhas + Consolidação

Relatório de erros e integração de todos os relatórios gerenciais.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from collections import defaultdict, Counter

from app.analytics.management_reports import ErrorMetrics


# ============================================================================
# ERROR REPORT
# ============================================================================

class ErrorReport:
    """
    Relatório de Erros e Falhas
    
    Analisa erros do sistema:
    - Tipos de erros
    - Frequência
    - Impacto (usuários/investigações afetados)
    - Tempo de resolução
    - Custo estimado
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Custos estimados por severidade de erro (em reais)
        self.ERROR_COSTS = {
            "low": 5.00,
            "medium": 25.00,
            "high": 100.00,
            "critical": 500.00
        }
    
    def generate_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gera relatório de erros
        
        Args:
            start_date: Data inicial
            end_date: Data final
            severity: Filtrar por severidade (low, medium, high, critical)
            
        Returns:
            Relatório estruturado de erros
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Coletar erros do período
        error_metrics = self._collect_errors(start_date, end_date, severity)
        
        # Agregar estatísticas
        total_errors = sum(e.error_count for e in error_metrics)
        total_cost = sum(e.estimated_cost_impact for e in error_metrics)
        
        # Erros por severidade
        by_severity = defaultdict(int)
        for e in error_metrics:
            by_severity[e.severity] += e.error_count
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "summary": {
                "total_error_types": len(error_metrics),
                "total_error_occurrences": total_errors,
                "estimated_total_cost": round(total_cost, 2),
                "by_severity": dict(by_severity),
                "critical_errors": by_severity.get("critical", 0),
                "average_time_to_fix_minutes": self._calculate_avg_time_to_fix(error_metrics)
            },
            "errors": [
                {
                    "type": e.error_type,
                    "count": e.error_count,
                    "severity": e.severity,
                    "first_seen": e.first_occurrence.isoformat(),
                    "last_seen": e.last_occurrence.isoformat(),
                    "affected_investigations": e.affected_investigations,
                    "affected_users": e.affected_users,
                    "is_recurring": e.is_recurring,
                    "avg_time_to_fix": round(e.average_time_to_fix_minutes, 2),
                    "estimated_cost": round(e.estimated_cost_impact, 2),
                    "status": self._get_error_status(e)
                }
                for e in sorted(error_metrics, key=lambda x: x.error_count, reverse=True)
            ],
            "most_critical": self._get_most_critical_errors(error_metrics),
            "recurring_errors": self._get_recurring_errors(error_metrics),
            "cost_analysis": self._analyze_error_costs(error_metrics),
            "recommendations": self._generate_error_recommendations(error_metrics)
        }
    
    def _collect_errors(
        self,
        start_date: datetime,
        end_date: datetime,
        severity: Optional[str]
    ) -> List[ErrorMetrics]:
        """Coleta erros do período"""
        
        # Em produção, estes dados viriam de logs (ELK, Sentry, etc)
        # Aqui simulamos erros comuns baseados em investigações
        
        from app.domain.investigation import Investigation
        
        investigations = self.db.query(Investigation).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date
            )
        ).all()
        
        failed_investigations = [i for i in investigations if i.status == "failed"]
        
        # Simular tipos de erros comuns
        error_types = [
            {
                "type": "ScraperTimeoutError",
                "severity": "medium",
                "base_count": len(failed_investigations) * 0.3,
                "avg_fix_time": 15
            },
            {
                "type": "DatabaseConnectionError",
                "severity": "high",
                "base_count": 2,
                "avg_fix_time": 30
            },
            {
                "type": "AuthenticationError",
                "severity": "medium",
                "base_count": len(investigations) * 0.05,
                "avg_fix_time": 10
            },
            {
                "type": "DataValidationError",
                "severity": "low",
                "base_count": len(investigations) * 0.1,
                "avg_fix_time": 5
            },
            {
                "type": "ExternalAPIError",
                "severity": "high",
                "base_count": len(failed_investigations) * 0.4,
                "avg_fix_time": 45
            },
            {
                "type": "MemoryExhaustedError",
                "severity": "critical",
                "base_count": 1,
                "avg_fix_time": 120
            },
            {
                "type": "RateLimitExceeded",
                "severity": "medium",
                "base_count": len(investigations) * 0.02,
                "avg_fix_time": 20
            },
            {
                "type": "ParseError",
                "severity": "low",
                "base_count": len(investigations) * 0.15,
                "avg_fix_time": 8
            }
        ]
        
        error_metrics = []
        for error in error_types:
            # Filtrar por severidade se especificado
            if severity and error["severity"] != severity:
                continue
            
            count = int(error["base_count"])
            if count == 0:
                continue
            
            # Determinar se é recorrente (se aconteceu mais de 5 vezes)
            is_recurring = count > 5
            
            # Calcular impacto
            affected_investigations = min(count, len(investigations))
            affected_users = min(count, len(set(i.user_id for i in investigations)))
            
            # Calcular custo
            cost = self.ERROR_COSTS[error["severity"]] * count
            
            error_metrics.append(ErrorMetrics(
                error_type=error["type"],
                error_count=count,
                first_occurrence=start_date + timedelta(hours=2),
                last_occurrence=end_date - timedelta(hours=2),
                affected_investigations=affected_investigations,
                affected_users=affected_users,
                severity=error["severity"],
                is_recurring=is_recurring,
                average_time_to_fix_minutes=error["avg_fix_time"],
                estimated_cost_impact=cost
            ))
        
        return error_metrics
    
    def _calculate_avg_time_to_fix(self, errors: List[ErrorMetrics]) -> float:
        """Calcula tempo médio de correção"""
        if not errors:
            return 0
        return sum(e.average_time_to_fix_minutes for e in errors) / len(errors)
    
    def _get_error_status(self, error: ErrorMetrics) -> str:
        """Determina status do erro"""
        if error.severity == "critical":
            return "requires_immediate_action"
        elif error.is_recurring and error.severity in ["high", "medium"]:
            return "needs_investigation"
        elif error.error_count > 10:
            return "high_frequency"
        else:
            return "monitored"
    
    def _get_most_critical_errors(self, errors: List[ErrorMetrics]) -> List[Dict]:
        """Retorna erros mais críticos"""
        critical = [e for e in errors if e.severity in ["critical", "high"]]
        sorted_critical = sorted(critical, key=lambda x: (
            x.severity == "critical",
            x.error_count
        ), reverse=True)[:5]
        
        return [
            {
                "type": e.error_type,
                "severity": e.severity,
                "count": e.error_count,
                "affected_users": e.affected_users,
                "estimated_cost": round(e.estimated_cost_impact, 2)
            }
            for e in sorted_critical
        ]
    
    def _get_recurring_errors(self, errors: List[ErrorMetrics]) -> List[Dict]:
        """Retorna erros recorrentes"""
        recurring = [e for e in errors if e.is_recurring]
        
        return [
            {
                "type": e.error_type,
                "occurrence_count": e.error_count,
                "frequency_per_day": round(
                    e.error_count / ((e.last_occurrence - e.first_occurrence).days or 1),
                    2
                ),
                "avg_time_to_fix": round(e.average_time_to_fix_minutes, 2)
            }
            for e in sorted(recurring, key=lambda x: x.error_count, reverse=True)
        ]
    
    def _analyze_error_costs(self, errors: List[ErrorMetrics]) -> Dict:
        """Analisa custos de erros"""
        total_cost = sum(e.estimated_cost_impact for e in errors)
        
        cost_by_severity = defaultdict(float)
        for e in errors:
            cost_by_severity[e.severity] += e.estimated_cost_impact
        
        return {
            "total_estimated_cost": round(total_cost, 2),
            "by_severity": {
                severity: round(cost, 2)
                for severity, cost in sorted(
                    cost_by_severity.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            },
            "cost_per_error": round(total_cost / len(errors), 2) if errors else 0,
            "preventable_cost": round(
                sum(e.estimated_cost_impact for e in errors if e.is_recurring) * 0.7,
                2
            )
        }
    
    def _generate_error_recommendations(self, errors: List[ErrorMetrics]) -> List[str]:
        """Gera recomendações para redução de erros"""
        recommendations = []
        
        if not errors:
            return ["✅ Nenhum erro significativo detectado."]
        
        critical_count = sum(1 for e in errors if e.severity == "critical")
        if critical_count > 0:
            recommendations.append(
                f"🔴 {critical_count} tipo(s) de erro crítico detectado. "
                "AÇÃO IMEDIATA NECESSÁRIA."
            )
        
        recurring = [e for e in errors if e.is_recurring]
        if recurring:
            top_recurring = sorted(recurring, key=lambda x: x.error_count, reverse=True)[0]
            recommendations.append(
                f"🔄 Erro recorrente: {top_recurring.error_type} ({top_recurring.error_count}x). "
                "Implementar correção permanente."
            )
        
        high_cost_errors = [e for e in errors if e.estimated_cost_impact > 100]
        if high_cost_errors:
            total_preventable = sum(e.estimated_cost_impact for e in high_cost_errors) * 0.7
            recommendations.append(
                f"💰 Economia potencial de R$ {total_preventable:.2f} corrigindo "
                f"{len(high_cost_errors)} tipo(s) de erro de alto custo."
            )
        
        slow_fix = [e for e in errors if e.average_time_to_fix_minutes > 60]
        if slow_fix:
            recommendations.append(
                f"⏱️ {len(slow_fix)} tipo(s) de erro com correção lenta (>60min). "
                "Melhorar processos de debugging e deploy."
            )
        
        return recommendations if recommendations else [
            "✅ Erros dentro dos níveis aceitáveis. Continuar monitoramento."
        ]


# ============================================================================
# CONSOLIDATED MANAGEMENT REPORTS
# ============================================================================

class ManagementReportsConsolidator:
    """
    Consolidador de Todos os Relatórios Gerenciais
    
    Integra todos os relatórios em um único dashboard executivo.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.roi_report = None  # Será importado dinamicamente
        self.cost_report = None
        self.performance_report = ScraperPerformanceReport(db)
        self.uptime_report = UptimeReport(db)
        self.error_report = ErrorReport(db)
    
    def generate_executive_management_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Gera relatório executivo consolidado
        
        Integra todos os 5 relatórios gerenciais:
        1. ROI por investigação
        2. Custo por investigação
        3. Performance de scrapers
        4. Uptime e disponibilidade
        5. Erros e falhas
        
        Returns:
            Relatório executivo completo
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Gerar todos os relatórios
        # (ROI e Cost serão importados do arquivo principal)
        performance = self.performance_report.generate_report(start_date, end_date)
        uptime = self.uptime_report.generate_report(start_date, end_date)
        errors = self.error_report.generate_report(start_date, end_date)
        
        # Calcular scores gerais
        operational_health_score = self._calculate_operational_health(
            performance, uptime, errors
        )
        
        # Consolidar recomendações prioritárias
        all_recommendations = (
            performance.get("recommendations", []) +
            uptime.get("recommendations", []) +
            errors.get("recommendations", [])
        )
        
        priority_recommendations = self._prioritize_recommendations(all_recommendations)
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "operational_health_score": operational_health_score,
            "reports": {
                "performance": performance,
                "uptime": uptime,
                "errors": errors
            },
            "priority_actions": priority_recommendations,
            "key_metrics": self._extract_key_metrics(performance, uptime, errors),
            "executive_summary": self._generate_executive_summary(
                performance, uptime, errors, operational_health_score
            )
        }
    
    def _calculate_operational_health(
        self,
        performance: Dict,
        uptime: Dict,
        errors: Dict
    ) -> Dict:
        """Calcula score de saúde operacional (0-100)"""
        
        # Performance score (0-40 pontos)
        perf_success = performance["summary"]["overall_success_rate"]
        perf_score = min((perf_success / 100) * 40, 40)
        
        # Uptime score (0-35 pontos)
        uptime_pct = uptime["summary"]["overall_uptime"]
        uptime_score = min((uptime_pct / 100) * 35, 35)
        
        # Error score (0-25 pontos)
        # Menos erros = maior score
        total_errors = errors["summary"]["total_error_occurrences"]
        critical_errors = errors["summary"]["critical_errors"]
        
        # Penalizar erros críticos mais pesadamente
        error_penalty = (total_errors * 0.1) + (critical_errors * 2)
        error_score = max(25 - error_penalty, 0)
        
        total_score = perf_score + uptime_score + error_score
        
        return {
            "total_score": round(total_score, 2),
            "max_score": 100.0,
            "breakdown": {
                "performance": round(perf_score, 2),
                "uptime": round(uptime_score, 2),
                "errors": round(error_score, 2)
            },
            "status": self._get_health_status(total_score),
            "trend": "stable"  # Seria calculado comparando com período anterior
        }
    
    def _get_health_status(self, score: float) -> str:
        """Determina status baseado no score"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        elif score >= 40:
            return "poor"
        else:
            return "critical"
    
    def _prioritize_recommendations(self, recommendations: List[str]) -> List[Dict]:
        """Prioriza recomendações por urgência"""
        priority_map = {
            "🔴": 1,  # Crítico
            "⚠️": 2,   # Alto
            "💰": 3,   # Médio-Alto (custo)
            "🔄": 3,   # Médio (recorrente)
            "🐢": 4,   # Médio-Baixo
            "⏱️": 4,   # Médio-Baixo
            "✅": 5    # Baixo (OK)
        }
        
        prioritized = []
        for rec in recommendations:
            # Determinar prioridade pelo emoji inicial
            priority = 5  # Default
            for emoji, prio in priority_map.items():
                if rec.startswith(emoji):
                    priority = prio
                    break
            
            prioritized.append({
                "priority": priority,
                "message": rec
            })
        
        # Ordenar por prioridade e retornar top 10
        return sorted(prioritized, key=lambda x: x["priority"])[:10]
    
    def _extract_key_metrics(
        self,
        performance: Dict,
        uptime: Dict,
        errors: Dict
    ) -> Dict:
        """Extrai métricas-chave de todos os relatórios"""
        return {
            "scrapers_success_rate": performance["summary"]["overall_success_rate"],
            "system_uptime": uptime["summary"]["overall_uptime"],
            "total_errors": errors["summary"]["total_error_occurrences"],
            "critical_errors": errors["summary"]["critical_errors"],
            "error_cost_impact": errors["summary"]["estimated_total_cost"],
            "sla_compliance": uptime["summary"]["sla_met"]
        }
    
    def _generate_executive_summary(
        self,
        performance: Dict,
        uptime: Dict,
        errors: Dict,
        health_score: Dict
    ) -> str:
        """Gera sumário executivo textual"""
        status = health_score["status"]
        score = health_score["total_score"]
        
        summary = f"Score de Saúde Operacional: {score:.1f}/100 ({status.upper()})\n\n"
        
        # Performance
        perf_rate = performance["summary"]["overall_success_rate"]
        summary += f"• Performance dos Scrapers: {perf_rate:.1f}% de taxa de sucesso\n"
        
        # Uptime
        uptime_pct = uptime["summary"]["overall_uptime"]
        summary += f"• Disponibilidade do Sistema: {uptime_pct:.2f}% de uptime\n"
        
        # Errors
        total_errors = errors["summary"]["total_error_occurrences"]
        critical = errors["summary"]["critical_errors"]
        summary += f"• Erros: {total_errors} ocorrências ({critical} críticos)\n"
        
        # SLA
        if uptime["summary"]["sla_met"]:
            summary += "• SLA: ✅ Em conformidade (>99.9%)\n"
        else:
            summary += "• SLA: ⚠️ Abaixo do target (99.9%)\n"
        
        return summary


# Import da parte 2 para completar
from app.analytics.management_reports_part2 import (
    ScraperPerformanceReport,
    UptimeReport
)
