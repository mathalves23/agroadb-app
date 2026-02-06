"""
Relatórios Gerenciais Completos - AgroADB
==========================================

Este módulo implementa relatórios gerenciais detalhados incluindo:

1. ROI por Investigação
2. Custo por Investigação
3. Performance de Scrapers
4. Uptime e Disponibilidade
5. Erros e Falhas

Autor: AgroADB Team
Data: 2026-02-05
Versão: 1.0.0
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ManagementReports:
    """Classe para geração de relatórios gerenciais"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    async def get_roi_by_investigation(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_roi: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calcula o ROI (Return on Investment) por investigação
        
        ROI = ((Valor Recuperado - Custo) / Custo) * 100
        
        Args:
            start_date: Data inicial
            end_date: Data final
            min_roi: ROI mínimo para filtrar
            
        Returns:
            Dict com ROI por investigação
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            from app.domain.investigation import Investigation
            
            # Simula dados financeiros (em produção viriam de tabelas específicas)
            investigations = self.db.query(Investigation).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date,
                    Investigation.status == "completed"
                )
            ).all()
            
            results = []
            total_invested = 0
            total_recovered = 0
            
            for inv in investigations:
                # Custos estimados (em produção viriam de tabela de custos)
                base_cost = 500.0  # Custo base por investigação
                scraper_cost = 50.0 * (inv.id % 10)  # Simula custo de scrapers
                human_hours = (inv.id % 20) + 10  # Simula horas de trabalho
                human_cost = human_hours * 100.0  # R$ 100/hora
                
                total_cost = base_cost + scraper_cost + human_cost
                
                # Valor recuperado/economizado (simulado)
                value_recovered = total_cost * (2 + (inv.id % 10))  # Simula recuperação
                
                # Calcula ROI
                roi = ((value_recovered - total_cost) / total_cost * 100) if total_cost > 0 else 0
                
                # Aplica filtro de ROI mínimo
                if min_roi is None or roi >= min_roi:
                    results.append({
                        "investigation_id": inv.id,
                        "investigation_title": inv.title,
                        "created_at": inv.created_at.isoformat(),
                        "completed_at": inv.completed_at.isoformat() if inv.completed_at else None,
                        "costs": {
                            "base": round(base_cost, 2),
                            "scrapers": round(scraper_cost, 2),
                            "human_hours": human_hours,
                            "human_cost": round(human_cost, 2),
                            "total": round(total_cost, 2)
                        },
                        "value_recovered": round(value_recovered, 2),
                        "roi_percentage": round(roi, 2),
                        "net_value": round(value_recovered - total_cost, 2)
                    })
                    
                    total_invested += total_cost
                    total_recovered += value_recovered
            
            # Ordena por ROI decrescente
            results.sort(key=lambda x: x['roi_percentage'], reverse=True)
            
            # Calcula ROI médio
            avg_roi = (sum(r['roi_percentage'] for r in results) / len(results)) if results else 0
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_investigations": len(results),
                    "total_invested": round(total_invested, 2),
                    "total_recovered": round(total_recovered, 2),
                    "net_profit": round(total_recovered - total_invested, 2),
                    "average_roi": round(avg_roi, 2),
                    "best_roi": round(results[0]['roi_percentage'], 2) if results else 0,
                    "worst_roi": round(results[-1]['roi_percentage'], 2) if results else 0
                },
                "investigations": results[:50]  # Limita a 50 resultados
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao calcular ROI: {str(e)}")
            raise
    
    async def get_cost_per_investigation(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: Optional[str] = None  # category, priority, user
    ) -> Dict[str, Any]:
        """
        Calcula o custo detalhado por investigação
        
        Args:
            start_date: Data inicial
            end_date: Data final
            group_by: Agrupamento opcional
            
        Returns:
            Dict com custos detalhados
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            from app.domain.investigation import Investigation
            
            investigations = self.db.query(Investigation).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date
                )
            ).all()
            
            results = []
            cost_breakdown = {
                "infrastructure": 0,
                "scrapers": 0,
                "human_resources": 0,
                "integrations": 0,
                "storage": 0,
                "total": 0
            }
            
            for inv in investigations:
                # Calcula custos detalhados
                infrastructure = 50.0  # Custo de infraestrutura
                scrapers = 30.0 * (inv.id % 8)  # Custo de execução de scrapers
                human_hours = (inv.id % 25) + 5
                human_resources = human_hours * 100.0
                integrations = 20.0 * (inv.id % 5)  # Custo de APIs externas
                storage = 10.0  # Custo de armazenamento
                
                total = infrastructure + scrapers + human_resources + integrations + storage
                
                inv_data = {
                    "investigation_id": inv.id,
                    "investigation_title": inv.title,
                    "category": inv.category or "uncategorized",
                    "priority": inv.priority or "medium",
                    "status": inv.status,
                    "created_by_id": inv.user_id,
                    "costs": {
                        "infrastructure": round(infrastructure, 2),
                        "scrapers": round(scrapers, 2),
                        "human_resources": round(human_resources, 2),
                        "human_hours": human_hours,
                        "integrations": round(integrations, 2),
                        "storage": round(storage, 2),
                        "total": round(total, 2)
                    }
                }
                
                results.append(inv_data)
                
                # Acumula breakdown
                cost_breakdown["infrastructure"] += infrastructure
                cost_breakdown["scrapers"] += scrapers
                cost_breakdown["human_resources"] += human_resources
                cost_breakdown["integrations"] += integrations
                cost_breakdown["storage"] += storage
                cost_breakdown["total"] += total
            
            # Agrupamento opcional
            grouped_data = None
            if group_by:
                grouped = defaultdict(lambda: {"count": 0, "total_cost": 0})
                
                for inv_data in results:
                    if group_by == "category":
                        key = inv_data["category"]
                    elif group_by == "priority":
                        key = inv_data["priority"]
                    elif group_by == "user":
                        key = f"user_{inv_data['created_by_id']}"
                    else:
                        key = "all"
                    
                    grouped[key]["count"] += 1
                    grouped[key]["total_cost"] += inv_data["costs"]["total"]
                
                # Calcula média por grupo
                grouped_data = {}
                for key, data in grouped.items():
                    grouped_data[key] = {
                        "count": data["count"],
                        "total_cost": round(data["total_cost"], 2),
                        "average_cost": round(data["total_cost"] / data["count"] if data["count"] > 0 else 0, 2)
                    }
            
            # Calcula médias
            avg_cost = cost_breakdown["total"] / len(results) if results else 0
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_investigations": len(results),
                    "total_cost": round(cost_breakdown["total"], 2),
                    "average_cost_per_investigation": round(avg_cost, 2),
                    "cost_breakdown": {k: round(v, 2) for k, v in cost_breakdown.items()},
                    "cost_breakdown_percentage": {
                        "infrastructure": round((cost_breakdown["infrastructure"] / cost_breakdown["total"] * 100) if cost_breakdown["total"] > 0 else 0, 2),
                        "scrapers": round((cost_breakdown["scrapers"] / cost_breakdown["total"] * 100) if cost_breakdown["total"] > 0 else 0, 2),
                        "human_resources": round((cost_breakdown["human_resources"] / cost_breakdown["total"] * 100) if cost_breakdown["total"] > 0 else 0, 2),
                        "integrations": round((cost_breakdown["integrations"] / cost_breakdown["total"] * 100) if cost_breakdown["total"] > 0 else 0, 2),
                        "storage": round((cost_breakdown["storage"] / cost_breakdown["total"] * 100) if cost_breakdown["total"] > 0 else 0, 2)
                    }
                },
                "grouped_data": grouped_data,
                "investigations": results[:50]
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao calcular custos: {str(e)}")
            raise
    
    async def get_scraper_performance(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Analisa a performance detalhada dos scrapers
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Dict com performance dos scrapers
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            # Dados simulados de performance de scrapers
            scrapers_performance = [
                {
                    "scraper_name": "INCRA",
                    "total_executions": 1250,
                    "successful": 1194,
                    "failed": 56,
                    "success_rate": 95.52,
                    "avg_duration_seconds": 12.3,
                    "min_duration_seconds": 3.2,
                    "max_duration_seconds": 45.8,
                    "total_data_mb": 450.2,
                    "errors": {
                        "timeout": 32,
                        "connection_error": 15,
                        "parse_error": 9
                    },
                    "uptime_percentage": 98.5,
                    "cost_per_execution": 0.08
                },
                {
                    "scraper_name": "Receita Federal",
                    "total_executions": 980,
                    "successful": 962,
                    "failed": 18,
                    "success_rate": 98.16,
                    "avg_duration_seconds": 8.7,
                    "min_duration_seconds": 2.1,
                    "max_duration_seconds": 28.3,
                    "total_data_mb": 320.5,
                    "errors": {
                        "timeout": 8,
                        "connection_error": 6,
                        "parse_error": 4
                    },
                    "uptime_percentage": 99.2,
                    "cost_per_execution": 0.05
                },
                {
                    "scraper_name": "CAR (Nacional)",
                    "total_executions": 850,
                    "successful": 783,
                    "failed": 67,
                    "success_rate": 92.12,
                    "avg_duration_seconds": 15.2,
                    "min_duration_seconds": 4.5,
                    "max_duration_seconds": 62.1,
                    "total_data_mb": 680.3,
                    "errors": {
                        "timeout": 45,
                        "connection_error": 12,
                        "parse_error": 10
                    },
                    "uptime_percentage": 96.8,
                    "cost_per_execution": 0.12
                },
                {
                    "scraper_name": "SIGEF",
                    "total_executions": 720,
                    "successful": 679,
                    "failed": 41,
                    "success_rate": 94.31,
                    "avg_duration_seconds": 10.5,
                    "min_duration_seconds": 3.8,
                    "max_duration_seconds": 38.2,
                    "total_data_mb": 540.1,
                    "errors": {
                        "timeout": 25,
                        "connection_error": 10,
                        "parse_error": 6
                    },
                    "uptime_percentage": 97.9,
                    "cost_per_execution": 0.09
                },
                {
                    "scraper_name": "Cartórios",
                    "total_executions": 650,
                    "successful": 583,
                    "failed": 67,
                    "success_rate": 89.69,
                    "avg_duration_seconds": 18.9,
                    "min_duration_seconds": 5.2,
                    "max_duration_seconds": 78.5,
                    "total_data_mb": 890.4,
                    "errors": {
                        "timeout": 38,
                        "connection_error": 18,
                        "parse_error": 11
                    },
                    "uptime_percentage": 95.2,
                    "cost_per_execution": 0.15
                }
            ]
            
            # Calcula totais e médias
            total_executions = sum(s['total_executions'] for s in scrapers_performance)
            total_successful = sum(s['successful'] for s in scrapers_performance)
            total_failed = sum(s['failed'] for s in scrapers_performance)
            avg_success_rate = sum(s['success_rate'] for s in scrapers_performance) / len(scrapers_performance)
            avg_duration = sum(s['avg_duration_seconds'] for s in scrapers_performance) / len(scrapers_performance)
            total_data = sum(s['total_data_mb'] for s in scrapers_performance)
            total_cost = sum(s['total_executions'] * s['cost_per_execution'] for s in scrapers_performance)
            
            # Agrupa erros
            error_summary = defaultdict(int)
            for scraper in scrapers_performance:
                for error_type, count in scraper['errors'].items():
                    error_summary[error_type] += count
            
            # Identifica scrapers problemáticos
            problematic = [s for s in scrapers_performance if s['success_rate'] < 95 or s['uptime_percentage'] < 97]
            top_performers = sorted(scrapers_performance, key=lambda x: x['success_rate'], reverse=True)[:3]
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_executions": total_executions,
                    "successful": total_successful,
                    "failed": total_failed,
                    "overall_success_rate": round(avg_success_rate, 2),
                    "average_duration_seconds": round(avg_duration, 2),
                    "total_data_collected_mb": round(total_data, 2),
                    "total_cost": round(total_cost, 2),
                    "cost_per_mb": round(total_cost / total_data if total_data > 0 else 0, 2)
                },
                "error_summary": dict(error_summary),
                "scrapers": scrapers_performance,
                "top_performers": top_performers,
                "problematic_scrapers": problematic,
                "recommendations": self._generate_scraper_recommendations(scrapers_performance)
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao analisar performance de scrapers: {str(e)}")
            raise
    
    def _generate_scraper_recommendations(self, scrapers: List[Dict]) -> List[str]:
        """Gera recomendações baseadas na performance dos scrapers"""
        recommendations = []
        
        for scraper in scrapers:
            if scraper['success_rate'] < 90:
                recommendations.append(
                    f"⚠️ {scraper['scraper_name']}: Taxa de sucesso baixa ({scraper['success_rate']:.1f}%). "
                    f"Revisar lógica de scraping e tratamento de erros."
                )
            
            if scraper['uptime_percentage'] < 95:
                recommendations.append(
                    f"⚠️ {scraper['scraper_name']}: Uptime baixo ({scraper['uptime_percentage']:.1f}%). "
                    f"Implementar retry logic e fallbacks."
                )
            
            if scraper['avg_duration_seconds'] > 20:
                recommendations.append(
                    f"🐌 {scraper['scraper_name']}: Tempo médio alto ({scraper['avg_duration_seconds']:.1f}s). "
                    f"Otimizar queries e implementar cache."
                )
            
            timeout_rate = scraper['errors']['timeout'] / scraper['total_executions'] * 100
            if timeout_rate > 5:
                recommendations.append(
                    f"⏱️ {scraper['scraper_name']}: Taxa de timeout alta ({timeout_rate:.1f}%). "
                    f"Aumentar timeout ou otimizar requests."
                )
        
        if not recommendations:
            recommendations.append("✅ Todos os scrapers estão operando dentro dos parâmetros esperados.")
        
        return recommendations
    
    async def get_uptime_availability(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Analisa uptime e disponibilidade do sistema
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Dict com métricas de uptime
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            total_hours = (end_date - start_date).total_seconds() / 3600
            
            # Dados simulados de uptime (em produção viriam de monitoramento)
            uptime_data = {
                "api": {
                    "total_hours": total_hours,
                    "uptime_hours": total_hours * 0.998,  # 99.8% uptime
                    "downtime_hours": total_hours * 0.002,
                    "uptime_percentage": 99.8,
                    "incidents": [
                        {
                            "timestamp": (datetime.utcnow() - timedelta(days=5)).isoformat(),
                            "duration_minutes": 12,
                            "reason": "Manutenção programada de banco de dados",
                            "impact": "low"
                        },
                        {
                            "timestamp": (datetime.utcnow() - timedelta(days=15)).isoformat(),
                            "duration_minutes": 8,
                            "reason": "Spike de tráfego inesperado",
                            "impact": "medium"
                        }
                    ]
                },
                "database": {
                    "total_hours": total_hours,
                    "uptime_hours": total_hours * 0.999,  # 99.9% uptime
                    "downtime_hours": total_hours * 0.001,
                    "uptime_percentage": 99.9,
                    "avg_query_time_ms": 45.2,
                    "slow_queries": 23
                },
                "scrapers": {
                    "total_hours": total_hours,
                    "uptime_hours": total_hours * 0.972,  # 97.2% uptime
                    "downtime_hours": total_hours * 0.028,
                    "uptime_percentage": 97.2,
                    "failed_jobs": 156
                },
                "integrations": {
                    "total_hours": total_hours,
                    "uptime_hours": total_hours * 0.985,  # 98.5% uptime
                    "downtime_hours": total_hours * 0.015,
                    "uptime_percentage": 98.5,
                    "timeout_rate": 3.2
                }
            }
            
            # Calcula SLA (Service Level Agreement)
            sla_target = 99.5
            overall_uptime = sum(comp['uptime_percentage'] for comp in uptime_data.values()) / len(uptime_data)
            sla_compliance = overall_uptime >= sla_target
            
            # Próxima janela de manutenção
            next_maintenance = datetime.utcnow() + timedelta(days=7)
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_hours": round(total_hours, 2)
                },
                "overall": {
                    "uptime_percentage": round(overall_uptime, 2),
                    "sla_target": sla_target,
                    "sla_compliance": sla_compliance,
                    "health_status": "healthy" if overall_uptime >= 99 else "degraded" if overall_uptime >= 95 else "critical"
                },
                "components": uptime_data,
                "next_maintenance": {
                    "scheduled_at": next_maintenance.isoformat(),
                    "estimated_duration_minutes": 30,
                    "affected_services": ["API", "Database"]
                }
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao calcular uptime: {str(e)}")
            raise
    
    async def get_errors_and_failures(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None  # low, medium, high, critical
    ) -> Dict[str, Any]:
        """
        Analisa erros e falhas do sistema
        
        Args:
            start_date: Data inicial
            end_date: Data final
            severity: Filtro de severidade
            
        Returns:
            Dict com análise de erros
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            # Dados simulados de erros (em produção viriam de logs/Sentry)
            errors = [
                {
                    "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                    "type": "DatabaseConnectionError",
                    "message": "Connection timeout to database",
                    "severity": "high",
                    "component": "database",
                    "affected_users": 12,
                    "resolution_time_minutes": 8,
                    "status": "resolved"
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
                    "type": "ScraperTimeout",
                    "message": "INCRA scraper timeout after 60s",
                    "severity": "medium",
                    "component": "scrapers",
                    "affected_users": 3,
                    "resolution_time_minutes": 0,
                    "status": "auto_retry"
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(hours=12)).isoformat(),
                    "type": "ValidationError",
                    "message": "Invalid CPF format in investigation",
                    "severity": "low",
                    "component": "api",
                    "affected_users": 1,
                    "resolution_time_minutes": 2,
                    "status": "resolved"
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                    "type": "RateLimitExceeded",
                    "message": "Receita Federal API rate limit exceeded",
                    "severity": "medium",
                    "component": "integrations",
                    "affected_users": 8,
                    "resolution_time_minutes": 15,
                    "status": "resolved"
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                    "type": "OutOfMemoryError",
                    "message": "Worker process ran out of memory",
                    "severity": "high",
                    "component": "workers",
                    "affected_users": 15,
                    "resolution_time_minutes": 25,
                    "status": "resolved"
                }
            ]
            
            # Aplica filtro de severidade
            if severity:
                errors = [e for e in errors if e['severity'] == severity]
            
            # Agrupa por tipo
            by_type = defaultdict(int)
            by_component = defaultdict(int)
            by_severity = defaultdict(int)
            
            total_affected_users = 0
            total_resolution_time = 0
            
            for error in errors:
                by_type[error['type']] += 1
                by_component[error['component']] += 1
                by_severity[error['severity']] += 1
                total_affected_users += error['affected_users']
                total_resolution_time += error['resolution_time_minutes']
            
            # Taxa de erros
            error_rate = len(errors) / ((end_date - start_date).total_seconds() / 3600)  # Erros por hora
            
            # MTTR (Mean Time To Resolution)
            mttr_minutes = total_resolution_time / len(errors) if errors else 0
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_errors": len(errors),
                    "error_rate_per_hour": round(error_rate, 2),
                    "total_affected_users": total_affected_users,
                    "mttr_minutes": round(mttr_minutes, 2),
                    "resolved": len([e for e in errors if e['status'] == 'resolved']),
                    "pending": len([e for e in errors if e['status'] != 'resolved'])
                },
                "by_type": dict(by_type),
                "by_component": dict(by_component),
                "by_severity": dict(by_severity),
                "recent_errors": errors[:20],
                "critical_errors": [e for e in errors if e['severity'] == 'critical'],
                "recommendations": self._generate_error_recommendations(by_type, by_component)
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao analisar erros: {str(e)}")
            raise
    
    def _generate_error_recommendations(
        self,
        by_type: Dict[str, int],
        by_component: Dict[str, int]
    ) -> List[str]:
        """Gera recomendações baseadas nos erros"""
        recommendations = []
        
        # Análise por tipo de erro
        if by_type.get('DatabaseConnectionError', 0) > 5:
            recommendations.append(
                "🔧 Múltiplos erros de conexão ao banco. Revisar pool de conexões e timeouts."
            )
        
        if by_type.get('ScraperTimeout', 0) > 10:
            recommendations.append(
                "⏱️ Muitos timeouts de scrapers. Aumentar timeout ou implementar retry exponencial."
            )
        
        if by_type.get('OutOfMemoryError', 0) > 0:
            recommendations.append(
                "💾 Erros de memória detectados. Aumentar recursos ou otimizar processamento."
            )
        
        # Análise por componente
        problematic_component = max(by_component.items(), key=lambda x: x[1])[0] if by_component else None
        if problematic_component:
            recommendations.append(
                f"⚠️ Componente '{problematic_component}' apresenta mais erros. Priorizar investigação."
            )
        
        if not recommendations:
            recommendations.append("✅ Nível de erros dentro do esperado.")
        
        return recommendations
    
    async def get_complete_management_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Gera relatório gerencial completo
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Dict com relatório completo
        """
        try:
            roi = await self.get_roi_by_investigation(start_date, end_date)
            costs = await self.get_cost_per_investigation(start_date, end_date)
            scrapers = await self.get_scraper_performance(start_date, end_date)
            uptime = await self.get_uptime_availability(start_date, end_date)
            errors = await self.get_errors_and_failures(start_date, end_date)
            
            return {
                "report_version": "1.0.0",
                "generated_at": datetime.utcnow().isoformat(),
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                },
                "roi_analysis": roi,
                "cost_analysis": costs,
                "scraper_performance": scrapers,
                "uptime_availability": uptime,
                "errors_failures": errors,
                "overall_health": {
                    "score": self._calculate_health_score(roi, costs, scrapers, uptime, errors),
                    "status": "healthy",  # healthy, warning, critical
                    "recommendations": self._generate_overall_recommendations(roi, costs, scrapers, uptime, errors)
                }
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório completo: {str(e)}")
            raise
    
    def _calculate_health_score(
        self,
        roi: Dict,
        costs: Dict,
        scrapers: Dict,
        uptime: Dict,
        errors: Dict
    ) -> float:
        """Calcula score de saúde geral do sistema (0-100)"""
        # ROI score (0-30 pontos)
        roi_score = min(30, roi['summary']['average_roi'] / 10)
        
        # Uptime score (0-30 pontos)
        uptime_score = (uptime['overall']['uptime_percentage'] / 100) * 30
        
        # Scraper score (0-25 pontos)
        scraper_score = (scrapers['summary']['overall_success_rate'] / 100) * 25
        
        # Error score (0-15 pontos) - invertido (menos erros = mais pontos)
        error_rate = errors['summary']['error_rate_per_hour']
        error_score = max(0, 15 - error_rate)
        
        total_score = roi_score + uptime_score + scraper_score + error_score
        
        return round(min(100, total_score), 2)
    
    def _generate_overall_recommendations(
        self,
        roi: Dict,
        costs: Dict,
        scrapers: Dict,
        uptime: Dict,
        errors: Dict
    ) -> List[str]:
        """Gera recomendações gerais"""
        recommendations = []
        
        # ROI
        if roi['summary']['average_roi'] < 100:
            recommendations.append("📊 ROI médio abaixo de 100%. Revisar processos e otimizar custos.")
        
        # Custos
        if costs['summary']['cost_breakdown']['human_resources'] / costs['summary']['total_cost'] > 0.7:
            recommendations.append("💰 Custos de RH representam >70% do total. Considerar automações.")
        
        # Uptime
        if uptime['overall']['uptime_percentage'] < 99:
            recommendations.append("⚠️ Uptime abaixo de 99%. Melhorar redundância e monitoramento.")
        
        # Scrapers
        if len(scrapers['problematic_scrapers']) > 2:
            recommendations.append(f"🔧 {len(scrapers['problematic_scrapers'])} scrapers problemáticos. Priorizar correções.")
        
        # Erros
        if errors['summary']['error_rate_per_hour'] > 5:
            recommendations.append("🐛 Taxa de erros elevada. Implementar melhorias em tratamento de erros.")
        
        if not recommendations:
            recommendations.append("✅ Sistema operando dentro dos parâmetros ideais.")
        
        return recommendations
