"""
Relatórios Gerenciais Avançados - Management Reports

Sistema de relatórios gerenciais especializados para análise detalhada
de ROI, custos, performance, uptime e erros da plataforma AgroADB.

Este módulo complementa o sistema Analytics existente com relatórios
específicos para gestão operacional e financeira.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract, desc
from pydantic import BaseModel, Field
from enum import Enum
import logging
from collections import defaultdict

from app.domain.user import User
from app.domain.investigation import Investigation
from app.domain.property import Property
from app.domain.company import Company

logger = logging.getLogger(__name__)


# ============================================================================
# MODELS
# ============================================================================

class ReportPeriod(BaseModel):
    """Período do relatório"""
    start_date: datetime
    end_date: datetime
    days: int
    description: str


class ROIMetrics(BaseModel):
    """Métricas de ROI"""
    investigation_id: int
    investigation_cpf_cnpj: str
    created_at: datetime
    completed_at: Optional[datetime]
    total_cost: float
    revenue_generated: float
    roi_percentage: float
    roi_absolute: float
    status: str
    user_id: int
    properties_found: int
    companies_found: int


class CostMetrics(BaseModel):
    """Métricas de custo"""
    investigation_id: int
    scraper_costs: Dict[str, float]
    storage_cost: float
    processing_cost: float
    api_cost: float
    total_cost: float
    cost_per_property: float
    cost_per_company: float
    is_efficient: bool


class ScraperPerformanceMetrics(BaseModel):
    """Métricas de performance de scraper"""
    scraper_name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    average_duration_seconds: float
    min_duration_seconds: float
    max_duration_seconds: float
    p95_duration_seconds: float
    total_data_collected: int
    average_data_per_execution: float
    error_rate: float
    reliability_score: float


class UptimeMetrics(BaseModel):
    """Métricas de uptime"""
    component: str
    uptime_percentage: float
    downtime_minutes: float
    total_checks: int
    failed_checks: int
    average_response_time_ms: float
    incidents: int
    mttr_minutes: float  # Mean Time To Recovery
    mtbf_minutes: float  # Mean Time Between Failures
    sla_compliance: bool


class ErrorMetrics(BaseModel):
    """Métricas de erros"""
    error_type: str
    error_count: int
    first_occurrence: datetime
    last_occurrence: datetime
    affected_investigations: int
    affected_users: int
    severity: str  # "low", "medium", "high", "critical"
    is_recurring: bool
    average_time_to_fix_minutes: float
    estimated_cost_impact: float


# ============================================================================
# ROI REPORT
# ============================================================================

class ROIReport:
    """
    Relatório de ROI por Investigação
    
    Calcula o retorno sobre investimento de cada investigação,
    considerando custos operacionais e valor gerado.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Custos base (em reais)
        self.COST_PER_SCRAPER_EXECUTION = 0.50
        self.COST_PER_API_CALL = 0.05
        self.COST_STORAGE_PER_GB = 0.10
        self.COST_PROCESSING_PER_MINUTE = 0.20
        
        # Valores estimados de receita
        self.VALUE_PER_PROPERTY = 15.00  # Valor estimado por propriedade encontrada
        self.VALUE_PER_COMPANY = 10.00   # Valor estimado por empresa encontrada
        self.BASE_INVESTIGATION_VALUE = 50.00  # Valor base de uma investigação
    
    def generate_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_roi: Optional[float] = None,
        max_roi: Optional[float] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Gera relatório completo de ROI
        
        Args:
            start_date: Data inicial
            end_date: Data final
            min_roi: ROI mínimo (%)
            max_roi: ROI máximo (%)
            user_id: Filtrar por usuário específico
            
        Returns:
            Relatório estruturado com métricas de ROI
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Buscar investigações
        query = self.db.query(Investigation).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date
            )
        )
        
        if user_id:
            query = query.filter(Investigation.user_id == user_id)
        
        investigations = query.all()
        
        # Calcular ROI para cada investigação
        roi_metrics_list = []
        for inv in investigations:
            roi_data = self._calculate_investigation_roi(inv)
            
            # Aplicar filtros de ROI
            if min_roi is not None and roi_data.roi_percentage < min_roi:
                continue
            if max_roi is not None and roi_data.roi_percentage > max_roi:
                continue
            
            roi_metrics_list.append(roi_data)
        
        # Agregar estatísticas
        if roi_metrics_list:
            total_cost = sum(r.total_cost for r in roi_metrics_list)
            total_revenue = sum(r.revenue_generated for r in roi_metrics_list)
            avg_roi = sum(r.roi_percentage for r in roi_metrics_list) / len(roi_metrics_list)
            
            positive_roi = [r for r in roi_metrics_list if r.roi_percentage > 0]
            negative_roi = [r for r in roi_metrics_list if r.roi_percentage < 0]
            
            # Top 10 melhores ROIs
            top_roi = sorted(roi_metrics_list, key=lambda x: x.roi_percentage, reverse=True)[:10]
            
            # Top 10 piores ROIs
            bottom_roi = sorted(roi_metrics_list, key=lambda x: x.roi_percentage)[:10]
        else:
            total_cost = total_revenue = avg_roi = 0
            positive_roi = negative_roi = top_roi = bottom_roi = []
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "summary": {
                "total_investigations": len(roi_metrics_list),
                "total_cost": round(total_cost, 2),
                "total_revenue": round(total_revenue, 2),
                "total_profit": round(total_revenue - total_cost, 2),
                "average_roi": round(avg_roi, 2),
                "positive_roi_count": len(positive_roi),
                "negative_roi_count": len(negative_roi),
                "positive_roi_rate": round(len(positive_roi) / len(roi_metrics_list) * 100, 2) if roi_metrics_list else 0
            },
            "top_performers": [
                {
                    "investigation_id": r.investigation_id,
                    "cpf_cnpj": r.investigation_cpf_cnpj,
                    "roi_percentage": round(r.roi_percentage, 2),
                    "roi_absolute": round(r.roi_absolute, 2),
                    "cost": round(r.total_cost, 2),
                    "revenue": round(r.revenue_generated, 2)
                }
                for r in top_roi
            ],
            "worst_performers": [
                {
                    "investigation_id": r.investigation_id,
                    "cpf_cnpj": r.investigation_cpf_cnpj,
                    "roi_percentage": round(r.roi_percentage, 2),
                    "roi_absolute": round(r.roi_absolute, 2),
                    "cost": round(r.total_cost, 2),
                    "revenue": round(r.revenue_generated, 2)
                }
                for r in bottom_roi
            ],
            "detailed_metrics": [
                {
                    "investigation_id": r.investigation_id,
                    "cpf_cnpj": r.investigation_cpf_cnpj,
                    "status": r.status,
                    "cost": round(r.total_cost, 2),
                    "revenue": round(r.revenue_generated, 2),
                    "roi_percentage": round(r.roi_percentage, 2),
                    "roi_absolute": round(r.roi_absolute, 2),
                    "properties_found": r.properties_found,
                    "companies_found": r.companies_found,
                    "created_at": r.created_at.isoformat(),
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None
                }
                for r in roi_metrics_list
            ],
            "recommendations": self._generate_roi_recommendations(roi_metrics_list)
        }
    
    def _calculate_investigation_roi(self, investigation: Investigation) -> ROIMetrics:
        """Calcula ROI de uma investigação específica"""
        
        # Calcular custos
        # Assumir 6 scrapers por investigação
        scraper_cost = self.COST_PER_SCRAPER_EXECUTION * 6
        
        # API calls (estimativa baseada em quantidade de dados)
        properties_count = len(investigation.properties or [])
        companies_count = len(investigation.companies or [])
        api_calls = (properties_count + companies_count) * 2  # 2 calls por entidade
        api_cost = api_calls * self.COST_PER_API_CALL
        
        # Storage (estimativa baseada em dados coletados)
        estimated_size_gb = (properties_count * 0.001 + companies_count * 0.001)  # 1MB por entidade
        storage_cost = estimated_size_gb * self.COST_STORAGE_PER_GB
        
        # Processing (baseado em tempo de conclusão)
        if investigation.completed_at and investigation.created_at:
            processing_minutes = (investigation.completed_at - investigation.created_at).total_seconds() / 60
        else:
            processing_minutes = 30  # Default: 30 minutos
        processing_cost = (processing_minutes * self.COST_PROCESSING_PER_MINUTE)
        
        total_cost = scraper_cost + api_cost + storage_cost + processing_cost
        
        # Calcular receita estimada
        revenue = (
            self.BASE_INVESTIGATION_VALUE +
            (properties_count * self.VALUE_PER_PROPERTY) +
            (companies_count * self.VALUE_PER_COMPANY)
        )
        
        # Calcular ROI
        if total_cost > 0:
            roi_percentage = ((revenue - total_cost) / total_cost) * 100
        else:
            roi_percentage = 0
        
        roi_absolute = revenue - total_cost
        
        return ROIMetrics(
            investigation_id=investigation.id,
            investigation_cpf_cnpj=investigation.cpf_cnpj,
            created_at=investigation.created_at,
            completed_at=investigation.completed_at,
            total_cost=total_cost,
            revenue_generated=revenue,
            roi_percentage=roi_percentage,
            roi_absolute=roi_absolute,
            status=investigation.status,
            user_id=investigation.user_id,
            properties_found=properties_count,
            companies_found=companies_count
        )
    
    def _generate_roi_recommendations(self, roi_metrics: List[ROIMetrics]) -> List[str]:
        """Gera recomendações baseadas nas métricas de ROI"""
        recommendations = []
        
        if not roi_metrics:
            return ["Nenhuma investigação no período para análise."]
        
        avg_roi = sum(r.roi_percentage for r in roi_metrics) / len(roi_metrics)
        
        if avg_roi < 50:
            recommendations.append(
                f"⚠️ ROI médio baixo ({avg_roi:.1f}%). "
                "Considerar otimizar custos operacionais ou revisar precificação."
            )
        elif avg_roi > 150:
            recommendations.append(
                f"✅ ROI médio excelente ({avg_roi:.1f}%). "
                "Manter estratégia atual e considerar expansão."
            )
        
        negative_count = sum(1 for r in roi_metrics if r.roi_percentage < 0)
        negative_rate = (negative_count / len(roi_metrics)) * 100
        
        if negative_rate > 20:
            recommendations.append(
                f"🔴 {negative_rate:.1f}% das investigações com ROI negativo. "
                "Investigar causas e implementar melhorias."
            )
        
        # Analisar eficiência por quantidade de dados
        high_data_low_roi = [
            r for r in roi_metrics 
            if (r.properties_found + r.companies_found) > 10 and r.roi_percentage < 100
        ]
        
        if high_data_low_roi:
            recommendations.append(
                f"💡 {len(high_data_low_roi)} investigações com muitos dados mas ROI baixo. "
                "Revisar valor agregado por tipo de dado coletado."
            )
        
        return recommendations if recommendations else ["✅ Métricas de ROI saudáveis."]


# ============================================================================
# COST REPORT
# ============================================================================

class CostReport:
    """
    Relatório de Custo por Investigação
    
    Análise detalhada dos custos operacionais de cada investigação,
    quebrado por tipo de custo (scrapers, storage, processing, etc).
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Custos por scraper (em reais)
        self.SCRAPER_COSTS = {
            "car": 0.80,
            "incra": 0.70,
            "receita": 1.00,
            "cartorios": 0.90,
            "diarios": 0.60,
            "sigef_sicar": 0.50
        }
        
        self.COST_STORAGE_PER_GB = 0.10
        self.COST_PROCESSING_PER_MINUTE = 0.20
        self.COST_API_CALL = 0.05
    
    def generate_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "investigation"  # "investigation", "user", "scraper", "day"
    ) -> Dict[str, Any]:
        """
        Gera relatório de custos
        
        Args:
            start_date: Data inicial
            end_date: Data final
            group_by: Agrupar por (investigation, user, scraper, day)
            
        Returns:
            Relatório estruturado de custos
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        investigations = self.db.query(Investigation).filter(
            and_(
                Investigation.created_at >= start_date,
                Investigation.created_at <= end_date
            )
        ).all()
        
        cost_metrics_list = []
        for inv in investigations:
            cost_data = self._calculate_investigation_cost(inv)
            cost_metrics_list.append(cost_data)
        
        # Agregar por tipo solicitado
        if group_by == "investigation":
            grouped_data = self._group_by_investigation(cost_metrics_list)
        elif group_by == "user":
            grouped_data = self._group_by_user(cost_metrics_list, investigations)
        elif group_by == "scraper":
            grouped_data = self._group_by_scraper(cost_metrics_list)
        elif group_by == "day":
            grouped_data = self._group_by_day(cost_metrics_list, investigations)
        else:
            grouped_data = {}
        
        # Estatísticas gerais
        total_cost = sum(c.total_cost for c in cost_metrics_list)
        avg_cost = total_cost / len(cost_metrics_list) if cost_metrics_list else 0
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "summary": {
                "total_investigations": len(cost_metrics_list),
                "total_cost": round(total_cost, 2),
                "average_cost_per_investigation": round(avg_cost, 2),
                "cost_breakdown": self._calculate_cost_breakdown(cost_metrics_list)
            },
            "grouped_data": grouped_data,
            "most_expensive": self._get_most_expensive(cost_metrics_list),
            "cost_efficiency": self._analyze_cost_efficiency(cost_metrics_list),
            "recommendations": self._generate_cost_recommendations(cost_metrics_list)
        }
    
    def _calculate_investigation_cost(self, investigation: Investigation) -> CostMetrics:
        """Calcula custo detalhado de uma investigação"""
        
        # Custos por scraper
        scraper_costs = {}
        for scraper_name, cost in self.SCRAPER_COSTS.items():
            scraper_costs[scraper_name] = cost
        
        # Storage
        properties_count = len(investigation.properties or [])
        companies_count = len(investigation.companies or [])
        estimated_size_gb = (properties_count * 0.001 + companies_count * 0.001)
        storage_cost = estimated_size_gb * self.COST_STORAGE_PER_GB
        
        # Processing
        if investigation.completed_at and investigation.created_at:
            processing_minutes = (investigation.completed_at - investigation.created_at).total_seconds() / 60
        else:
            processing_minutes = 30
        processing_cost = processing_minutes * self.COST_PROCESSING_PER_MINUTE
        
        # API calls
        api_calls = (properties_count + companies_count) * 2
        api_cost = api_calls * self.COST_API_CALL
        
        total_cost = sum(scraper_costs.values()) + storage_cost + processing_cost + api_cost
        
        # Eficiência
        cost_per_property = total_cost / properties_count if properties_count > 0 else 0
        cost_per_company = total_cost / companies_count if companies_count > 0 else 0
        
        # Considerado eficiente se custo total < R$ 10 e encontrou dados
        is_efficient = total_cost < 10.0 and (properties_count > 0 or companies_count > 0)
        
        return CostMetrics(
            investigation_id=investigation.id,
            scraper_costs=scraper_costs,
            storage_cost=storage_cost,
            processing_cost=processing_cost,
            api_cost=api_cost,
            total_cost=total_cost,
            cost_per_property=cost_per_property,
            cost_per_company=cost_per_company,
            is_efficient=is_efficient
        )
    
    def _group_by_investigation(self, costs: List[CostMetrics]) -> Dict:
        """Agrupa custos por investigação"""
        return {
            "investigations": [
                {
                    "investigation_id": c.investigation_id,
                    "total_cost": round(c.total_cost, 2),
                    "scraper_costs": {k: round(v, 2) for k, v in c.scraper_costs.items()},
                    "storage_cost": round(c.storage_cost, 2),
                    "processing_cost": round(c.processing_cost, 2),
                    "api_cost": round(c.api_cost, 2),
                    "is_efficient": c.is_efficient
                }
                for c in costs
            ]
        }
    
    def _group_by_user(self, costs: List[CostMetrics], investigations: List[Investigation]) -> Dict:
        """Agrupa custos por usuário"""
        user_costs = defaultdict(float)
        user_investigations = defaultdict(int)
        
        inv_map = {inv.id: inv.user_id for inv in investigations}
        
        for cost in costs:
            user_id = inv_map.get(cost.investigation_id)
            if user_id:
                user_costs[user_id] += cost.total_cost
                user_investigations[user_id] += 1
        
        return {
            "by_user": [
                {
                    "user_id": user_id,
                    "total_cost": round(cost, 2),
                    "investigations_count": user_investigations[user_id],
                    "average_cost": round(cost / user_investigations[user_id], 2)
                }
                for user_id, cost in sorted(user_costs.items(), key=lambda x: x[1], reverse=True)
            ]
        }
    
    def _group_by_scraper(self, costs: List[CostMetrics]) -> Dict:
        """Agrupa custos por scraper"""
        scraper_totals = defaultdict(float)
        
        for cost in costs:
            for scraper, scraper_cost in cost.scraper_costs.items():
                scraper_totals[scraper] += scraper_cost
        
        return {
            "by_scraper": [
                {
                    "scraper": scraper,
                    "total_cost": round(cost, 2),
                    "executions": len(costs),
                    "average_cost": round(cost / len(costs), 2)
                }
                for scraper, cost in sorted(scraper_totals.items(), key=lambda x: x[1], reverse=True)
            ]
        }
    
    def _group_by_day(self, costs: List[CostMetrics], investigations: List[Investigation]) -> Dict:
        """Agrupa custos por dia"""
        daily_costs = defaultdict(float)
        inv_map = {inv.id: inv.created_at.date() for inv in investigations}
        
        for cost in costs:
            date = inv_map.get(cost.investigation_id)
            if date:
                daily_costs[date] += cost.total_cost
        
        return {
            "by_day": [
                {
                    "date": str(date),
                    "total_cost": round(cost, 2)
                }
                for date, cost in sorted(daily_costs.items())
            ]
        }
    
    def _calculate_cost_breakdown(self, costs: List[CostMetrics]) -> Dict:
        """Calcula distribuição de custos por categoria"""
        total_scraper = sum(sum(c.scraper_costs.values()) for c in costs)
        total_storage = sum(c.storage_cost for c in costs)
        total_processing = sum(c.processing_cost for c in costs)
        total_api = sum(c.api_cost for c in costs)
        total = total_scraper + total_storage + total_processing + total_api
        
        if total == 0:
            return {}
        
        return {
            "scrapers": {
                "amount": round(total_scraper, 2),
                "percentage": round((total_scraper / total) * 100, 2)
            },
            "storage": {
                "amount": round(total_storage, 2),
                "percentage": round((total_storage / total) * 100, 2)
            },
            "processing": {
                "amount": round(total_processing, 2),
                "percentage": round((total_processing / total) * 100, 2)
            },
            "api": {
                "amount": round(total_api, 2),
                "percentage": round((total_api / total) * 100, 2)
            }
        }
    
    def _get_most_expensive(self, costs: List[CostMetrics], limit: int = 10) -> List[Dict]:
        """Retorna as investigações mais caras"""
        sorted_costs = sorted(costs, key=lambda x: x.total_cost, reverse=True)[:limit]
        return [
            {
                "investigation_id": c.investigation_id,
                "total_cost": round(c.total_cost, 2),
                "cost_per_property": round(c.cost_per_property, 2),
                "cost_per_company": round(c.cost_per_company, 2)
            }
            for c in sorted_costs
        ]
    
    def _analyze_cost_efficiency(self, costs: List[CostMetrics]) -> Dict:
        """Analisa eficiência de custos"""
        if not costs:
            return {}
        
        efficient = [c for c in costs if c.is_efficient]
        inefficient = [c for c in costs if not c.is_efficient]
        
        return {
            "efficient_count": len(efficient),
            "inefficient_count": len(inefficient),
            "efficiency_rate": round((len(efficient) / len(costs)) * 100, 2),
            "average_cost_efficient": round(sum(c.total_cost for c in efficient) / len(efficient), 2) if efficient else 0,
            "average_cost_inefficient": round(sum(c.total_cost for c in inefficient) / len(inefficient), 2) if inefficient else 0
        }
    
    def _generate_cost_recommendations(self, costs: List[CostMetrics]) -> List[str]:
        """Gera recomendações de redução de custos"""
        recommendations = []
        
        if not costs:
            return ["Nenhum dado disponível para análise."]
        
        avg_cost = sum(c.total_cost for c in costs) / len(costs)
        
        if avg_cost > 10.0:
            recommendations.append(
                f"⚠️ Custo médio alto (R$ {avg_cost:.2f}). "
                "Avaliar otimização de scrapers e processamento."
            )
        
        # Verificar custo de scrapers
        avg_scraper_cost = sum(sum(c.scraper_costs.values()) for c in costs) / len(costs)
        if avg_scraper_cost > 5.0:
            recommendations.append(
                f"🔧 Custo de scrapers elevado (R$ {avg_scraper_cost:.2f}). "
                "Considerar cache de dados ou redução de fontes menos úteis."
            )
        
        # Verificar eficiência
        efficient_rate = len([c for c in costs if c.is_efficient]) / len(costs)
        if efficient_rate < 0.7:
            recommendations.append(
                f"📉 Apenas {efficient_rate*100:.1f}% das investigações são eficientes. "
                "Revisar processo e identificar gargalos."
            )
        
        return recommendations if recommendations else ["✅ Custos dentro do esperado."]


# Continuação em próximo arquivo...
