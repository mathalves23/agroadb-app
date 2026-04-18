"""
Analytics & Metrics System - Sistema de Métricas e Analytics

Este módulo coleta, processa e expõe métricas de uso da plataforma AgroADB.

Componentes:
- MetricsCalculator: Calcula métricas individuais
- AnalyticsAggregator: Agrega múltiplas métricas em relatórios

Métricas coletadas:
- Uso geral (usuários, investigações, ações)
- Performance (tempos de resposta, sucesso/erro)
- Scrapers (execuções, taxa de sucesso)
- ML (análises executadas)
- Integrações (consultas externas)
- Financeiro (receita, custos, ROI)
- Geográfico (distribuição por estado)

Para mais informações, consulte README.md e INTEGRATION_GUIDE.md
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract
from collections import defaultdict
import logging

from app.domain.user import User
from app.domain.investigation import Investigation, InvestigationStatus
from app.domain.property import Property
from app.domain.company import Company

logger = logging.getLogger(__name__)


def _scalar_count(val: Any) -> int:
    """Normaliza resultado de COUNT/scalar para int (compatível com mocks em testes)."""
    if val is None:
        return 0
    if isinstance(val, bool):
        return int(val)
    if isinstance(val, (int, float)):
        return int(val)
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


__version__ = "1.0.0"
__all__ = [
    "MetricsCalculator",
    "AnalyticsAggregator"
]


class MetricsCalculator:
    """Calculador de métricas do sistema"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_overview_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Métricas gerais do sistema
        
        Returns:
            Dict com métricas gerais (usuários, investigações, etc)
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Total de usuários
        total_users = _scalar_count(self.db.query(func.count(User.id)).scalar())
        active_users = _scalar_count(self.db.query(func.count(User.id)).filter(
            User.is_active == True
        ).scalar())
        
        # Usuários novos no período
        new_users = _scalar_count(self.db.query(func.count(User.id)).filter(
            and_(
                User.created_at >= start_date,
                User.created_at <= end_date
            )
        ).scalar())
        
        # Total de investigações
        total_investigations = _scalar_count(self.db.query(func.count(Investigation.id)).scalar())
        
        # Investigações no período
        period_investigations = _scalar_count(self.db.query(func.count(Investigation.id)).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date
            )
        ).scalar())
        
        # Investigações por status
        investigations_by_status = self.db.query(
            Investigation.status,
            func.count(Investigation.id)
        ).group_by(Investigation.status).all()
        
        status_dict: Dict[str, Any] = {}
        for status, count in investigations_by_status:
            key = getattr(status, "value", status)
            status_dict[str(key)] = _scalar_count(count)
        
        # Taxa de conclusão
        completed = status_dict.get(InvestigationStatus.COMPLETED.value, status_dict.get("completed", 0))
        completion_rate = (completed / total_investigations * 100) if total_investigations > 0 else 0
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users,
                "new_in_period": new_users
            },
            "investigations": {
                "total": total_investigations,
                "in_period": period_investigations,
                "by_status": status_dict,
                "completion_rate": round(completion_rate, 2)
            },
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            }
        }
    
    def get_usage_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Métricas de uso da plataforma"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Investigações criadas por dia
        daily_investigations = self.db.query(
            func.date(Investigation.created_at).label('date'),
            func.count(Investigation.id).label('count')
        ).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date
            )
        ).group_by(func.date(Investigation.created_at)).all()
        
        # Usuários mais ativos (top 10)
        top_users = self.db.query(
            User.id,
            User.username,
            User.email,
            func.count(Investigation.id).label('investigation_count')
        ).join(Investigation, Investigation.user_id == User.id).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date
            )
        ).group_by(User.id, User.username, User.email).order_by(
            func.count(Investigation.id).desc()
        ).limit(10).all()
        
        # Tempo médio de conclusão
        completed_investigations = self.db.query(
            Investigation.created_at,
            Investigation.updated_at
        ).filter(
            and_(
                Investigation.status == "completed",
                Investigation.created_at >= start_date,
                Investigation.updated_at <= end_date
            )
        ).all()
        
        completion_times = []
        for created, updated in completed_investigations:
            if created and updated:
                delta = (updated - created).total_seconds() / 3600  # horas
                completion_times.append(delta)
        
        avg_completion_time = (
            sum(completion_times) / len(completion_times)
            if completion_times else 0
        )
        
        return {
            "daily_activity": [
                {"date": str(date), "count": count}
                for date, count in daily_investigations
            ],
            "top_users": [
                {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "investigation_count": count
                }
                for user_id, username, email, count in top_users
            ],
            "completion_time": {
                "average_hours": round(avg_completion_time, 2),
                "total_completed": len(completion_times)
            }
        }
    
    def get_scrapers_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Métricas dos scrapers"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Esta é uma implementação simplificada
        # Em produção, você coletaria métricas do sistema de filas
        
        # Simular dados de scrapers
        scrapers = ["car", "incra", "receita", "cartorios", "diarios", "sigef_sicar"]
        
        metrics = {
            "by_scraper": {},
            "total_executions": 0,
            "total_successes": 0,
            "total_failures": 0,
            "average_duration_seconds": 0
        }
        
        # Contar propriedades e empresas como proxy de execuções bem-sucedidas
        properties_count = self.db.query(func.count(Property.id)).filter(
            and_(
                Property.created_at >= start_date,
                Property.created_at <= end_date
            )
        ).scalar()
        
        companies_count = self.db.query(func.count(Company.id)).filter(
            and_(
                Company.created_at >= start_date,
                Company.created_at <= end_date
            )
        ).scalar()
        
        # Estimar execuções (cada investigação roda ~6 scrapers)
        investigations_count = self.db.query(func.count(Investigation.id)).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date
            )
        ).scalar()
        
        total_executions = investigations_count * 6
        success_rate = 0.85  # Assumir 85% de sucesso
        
        metrics["total_executions"] = total_executions
        metrics["total_successes"] = int(total_executions * success_rate)
        metrics["total_failures"] = int(total_executions * (1 - success_rate))
        metrics["average_duration_seconds"] = 45.0
        
        # Por scraper
        for scraper in scrapers:
            metrics["by_scraper"][scraper] = {
                "executions": investigations_count,
                "successes": int(investigations_count * success_rate),
                "failures": int(investigations_count * (1 - success_rate)),
                "success_rate": success_rate
            }
        
        return metrics
    
    def get_geographic_metrics(self) -> Dict[str, Any]:
        """Métricas geográficas (estados com mais propriedades)"""
        
        # Contar propriedades por estado
        # Assumindo que temos campo 'state' no additional_data
        investigations = self.db.query(Investigation).all()
        
        state_counts = defaultdict(int)
        state_areas = defaultdict(float)
        
        for inv in investigations:
            for prop in (inv.properties or []):
                prop_data = prop.additional_data or {}
                state = prop_data.get("state", "Unknown")
                area = float(prop_data.get("area_hectares", 0) or 0)
                
                state_counts[state] += 1
                state_areas[state] += area
        
        # Top 10 estados
        top_states = sorted(
            state_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "by_state": [
                {
                    "state": state,
                    "properties_count": count,
                    "total_area_hectares": round(state_areas[state], 2)
                }
                for state, count in top_states
            ],
            "total_states": len([s for s in state_counts.keys() if s != "Unknown"])
        }
    
    def get_performance_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Métricas de performance do sistema"""
        
        # Esta é uma versão simplificada
        # Em produção, você coletaria de logs e Prometheus
        
        return {
            "api": {
                "average_response_time_ms": 120,
                "p95_response_time_ms": 450,
                "p99_response_time_ms": 850,
                "requests_per_second": 25.5,
                "error_rate": 0.02
            },
            "database": {
                "average_query_time_ms": 15,
                "slow_queries": 3,
                "connections_active": 12,
                "connections_max": 100
            },
            "cache": {
                "hit_rate": 0.78,
                "miss_rate": 0.22,
                "keys_count": 1250,
                "memory_used_mb": 128
            }
        }
    
    def get_financial_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Métricas financeiras (se aplicável)"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Calcular custo aproximado por investigação
        # Baseado em uso de recursos (scrapers, ML, armazenamento)
        
        investigations_count = self.db.query(func.count(Investigation.id)).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date
            )
        ).scalar()
        
        # Custos estimados (em reais)
        cost_per_investigation = 5.50  # R$ 5,50 por investigação
        total_cost = investigations_count * cost_per_investigation
        
        # MRR (Monthly Recurring Revenue) - exemplo
        active_users = self.db.query(func.count(User.id)).filter(
            User.is_active == True
        ).scalar()
        
        price_per_user = 299.90  # R$ 299,90/mês por usuário
        mrr = active_users * price_per_user
        
        return {
            "period_metrics": {
                "investigations": investigations_count,
                "cost_per_investigation": cost_per_investigation,
                "total_cost": round(total_cost, 2),
                "average_cost_per_day": round(
                    total_cost / max((end_date - start_date).days, 1),
                    2
                )
            },
            "revenue": {
                "active_users": active_users,
                "price_per_user": price_per_user,
                "mrr": round(mrr, 2),
                "arr": round(mrr * 12, 2)
            },
            "roi": {
                "revenue": round(mrr, 2),
                "costs": round(total_cost, 2),
                "profit": round(mrr - total_cost, 2),
                "margin_percentage": round(
                    ((mrr - total_cost) / mrr * 100) if mrr > 0 else 0,
                    2
                )
            }
        }


class AnalyticsAggregator:
    """Agregador de métricas para relatórios gerenciais"""
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = MetricsCalculator(db)
    
    def generate_executive_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Gera sumário executivo com todas as métricas principais
        
        Ideal para CEOs, diretores, investidores
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Coletar todas as métricas
        overview = self.calculator.get_overview_metrics(start_date, end_date)
        usage = self.calculator.get_usage_metrics(start_date, end_date)
        scrapers = self.calculator.get_scrapers_metrics(start_date, end_date)
        geographic = self.calculator.get_geographic_metrics()
        performance = self.calculator.get_performance_metrics(start_date, end_date)
        financial = self.calculator.get_financial_metrics(start_date, end_date)
        
        # Calcular KPIs principais
        kpis = self._calculate_kpis(overview, usage, financial)
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "kpis": kpis,
            "overview": overview,
            "usage": usage,
            "scrapers": scrapers,
            "geographic": geographic,
            "performance": performance,
            "financial": financial,
            "health_score": self._calculate_health_score(
                overview, performance, financial
            )
        }
    
    def generate_operational_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Relatório operacional detalhado
        
        Ideal para gerentes de operação, product managers
        """
        overview = self.calculator.get_overview_metrics(start_date, end_date)
        usage = self.calculator.get_usage_metrics(start_date, end_date)
        scrapers = self.calculator.get_scrapers_metrics(start_date, end_date)
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "overview": overview,
            "usage": usage,
            "scrapers": scrapers,
            "recommendations": self._generate_operational_recommendations(
                overview, usage, scrapers
            )
        }
    
    def get_user_analytics(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Analytics de um usuário específico"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Usuário {user_id} não encontrado")
        
        # Investigações do usuário
        investigations = self.db.query(Investigation).filter(
            and_(
                Investigation.user_id == user_id,
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date
            )
        ).all()
        
        # Calcular estatísticas
        total = len(investigations)
        completed = sum(1 for i in investigations if i.status == "completed")
        in_progress = sum(1 for i in investigations if i.status == "in_progress")
        
        total_properties = sum(len(i.properties or []) for i in investigations)
        total_companies = sum(len(i.companies or []) for i in investigations)
        
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat()
            },
            "investigations": {
                "total": total,
                "completed": completed,
                "in_progress": in_progress,
                "completion_rate": round((completed / total * 100) if total > 0 else 0, 2)
            },
            "data_collected": {
                "properties": total_properties,
                "companies": total_companies,
                "avg_per_investigation": round(
                    (total_properties + total_companies) / total if total > 0 else 0,
                    2
                )
            }
        }
    
    def get_funnel_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Métricas de funil (conversão)"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Etapas do funil
        total_created = self.db.query(func.count(Investigation.id)).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date
            )
        ).scalar()
        
        started = self.db.query(func.count(Investigation.id)).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date,
                Investigation.status.in_(["in_progress", "completed"])
            )
        ).scalar()
        
        completed = self.db.query(func.count(Investigation.id)).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date,
                Investigation.status == "completed"
            )
        ).scalar()
        
        # Calcular conversão
        conversion_started = (started / total_created * 100) if total_created > 0 else 0
        conversion_completed = (completed / total_created * 100) if total_created > 0 else 0
        
        return {
            "funnel": [
                {"step": "created", "count": total_created, "percentage": 100.0},
                {"step": "started", "count": started, "percentage": round(conversion_started, 2)},
                {"step": "completed", "count": completed, "percentage": round(conversion_completed, 2)}
            ],
            "drop_off": {
                "created_to_started": round(100 - conversion_started, 2),
                "started_to_completed": round(
                    ((started - completed) / started * 100) if started > 0 else 0,
                    2
                )
            }
        }
    
    def _calculate_kpis(
        self,
        overview: Dict,
        usage: Dict,
        financial: Dict
    ) -> Dict[str, Any]:
        """Calcula KPIs principais"""
        return {
            "active_users": overview["users"]["active"],
            "total_investigations": overview["investigations"]["total"],
            "completion_rate": overview["investigations"]["completion_rate"],
            "avg_completion_time_hours": usage["completion_time"]["average_hours"],
            "mrr": financial["revenue"]["mrr"],
            "profit_margin": financial["roi"]["margin_percentage"]
        }
    
    def _calculate_health_score(
        self,
        overview: Dict,
        performance: Dict,
        financial: Dict
    ) -> float:
        """
        Calcula score de saúde do sistema (0-100)
        
        Baseado em:
        - Taxa de conclusão de investigações
        - Performance da API
        - Margem de lucro
        """
        score = 0.0
        
        # Taxa de conclusão (30 pontos)
        completion_rate = overview["investigations"]["completion_rate"]
        score += min(completion_rate / 100 * 30, 30)
        
        # Performance API (30 pontos)
        error_rate = performance["api"]["error_rate"]
        score += max(30 - (error_rate * 1000), 0)
        
        # Margem de lucro (40 pontos)
        margin = financial["roi"]["margin_percentage"]
        score += min(margin / 100 * 40, 40)
        
        return round(min(score, 100), 2)
    
    def _generate_operational_recommendations(
        self,
        overview: Dict,
        usage: Dict,
        scrapers: Dict
    ) -> List[str]:
        """Gera recomendações operacionais"""
        recommendations = []
        
        # Taxa de conclusão baixa
        completion_rate = overview["investigations"]["completion_rate"]
        if completion_rate < 70:
            recommendations.append(
                f"⚠️ Taxa de conclusão baixa ({completion_rate}%). "
                "Investigar motivos de abandono."
            )
        
        # Tempo de conclusão alto
        avg_time = usage["completion_time"]["average_hours"]
        if avg_time > 48:
            recommendations.append(
                f"⏱️ Tempo médio de conclusão alto ({avg_time:.1f}h). "
                "Considerar otimizar scrapers."
            )
        
        # Taxa de falha de scrapers alta
        total_exec = scrapers["total_executions"]
        failures = scrapers["total_failures"]
        if total_exec > 0:
            failure_rate = failures / total_exec
            if failure_rate > 0.2:
                recommendations.append(
                    f"🔧 Taxa de falha de scrapers alta ({failure_rate:.1%}). "
                    "Revisar estabilidade."
                )
        
        if not recommendations:
            recommendations.append("✅ Sistema operando normalmente. Manter monitoramento.")
        
        return recommendations
