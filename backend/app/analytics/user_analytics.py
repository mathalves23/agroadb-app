"""
User Analytics - Analytics de Usuário

Sistema completo de analytics comportamental e de engajamento de usuários.

Funcionalidades:
1. Funnel de Uso - Análise de conversão em funis
2. Feature Adoption - Adoção de funcionalidades
3. Heatmaps de Navegação - Mapas de calor de cliques/navegação
4. Session Recordings - Gravação de sessões
5. NPS (Net Promoter Score) - Satisfação do cliente
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from pydantic import BaseModel, Field, validator
from enum import Enum
from collections import defaultdict, Counter
import json
import logging

from app.domain.user import User
from app.domain.investigation import Investigation

logger = logging.getLogger(__name__)


# ============================================================================
# MODELS
# ============================================================================

class FunnelStep(BaseModel):
    """Etapa do funil"""
    step_name: str
    step_order: int
    users_entered: int
    users_completed: int
    conversion_rate: float
    drop_off_rate: float
    average_time_seconds: float
    median_time_seconds: float


class FunnelAnalysis(BaseModel):
    """Análise completa de funil"""
    funnel_name: str
    total_users_started: int
    total_users_completed: int
    overall_conversion_rate: float
    average_completion_time_seconds: float
    steps: List[FunnelStep]
    bottlenecks: List[str]
    recommendations: List[str]


class FeatureUsage(BaseModel):
    """Uso de uma feature"""
    feature_name: str
    total_users: int
    active_users: int
    adoption_rate: float
    first_use_date: datetime
    last_use_date: datetime
    usage_frequency: float  # vezes por usuário ativo
    power_users: int  # usuários que usam muito
    casual_users: int  # usuários que usam pouco
    growth_rate: float  # taxa de crescimento


class FeatureAdoptionStatus(str, Enum):
    """Status de adoção de feature"""
    NOT_STARTED = "not_started"
    EXPLORING = "exploring"
    ADOPTING = "adopting"
    ADOPTED = "adopted"
    POWER_USER = "power_user"
    CHURNED = "churned"


class HeatmapPoint(BaseModel):
    """Ponto no heatmap"""
    x: float
    y: float
    intensity: int
    page: str
    element: Optional[str] = None


class HeatmapData(BaseModel):
    """Dados de heatmap"""
    page: str
    total_clicks: int
    unique_users: int
    points: List[HeatmapPoint]
    hot_zones: List[Dict[str, Any]]  # Zonas mais clicadas
    cold_zones: List[Dict[str, Any]]  # Zonas menos clicadas


class SessionEvent(BaseModel):
    """Evento em uma sessão"""
    timestamp: datetime
    event_type: str  # "click", "scroll", "input", "navigation", "error"
    page: str
    element: Optional[str] = None
    value: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None


class SessionRecording(BaseModel):
    """Gravação de sessão"""
    session_id: str
    user_id: int
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    pages_visited: int
    events_count: int
    events: List[SessionEvent]
    user_agent: str
    device_type: str
    browser: str
    errors_encountered: int
    completed_actions: List[str]


class NPSResponse(BaseModel):
    """Resposta de NPS"""
    user_id: int
    score: int  # 0-10
    category: str  # "detractor", "passive", "promoter"
    feedback: Optional[str] = None
    created_at: datetime
    
    @validator('score')
    def validate_score(cls, v):
        if not 0 <= v <= 10:
            raise ValueError('Score deve estar entre 0 e 10')
        return v


class NPSAnalysis(BaseModel):
    """Análise de NPS"""
    total_responses: int
    detractors: int
    passives: int
    promoters: int
    nps_score: float  # -100 a 100
    average_score: float
    response_rate: float
    trend: str  # "improving", "stable", "declining"
    by_segment: Dict[str, float]  # NPS por segmento


# ============================================================================
# 1. FUNNEL ANALYTICS
# ============================================================================

class FunnelAnalytics:
    """
    Análise de Funil de Uso
    
    Analisa conversão de usuários através de funis definidos.
    Identifica gargalos e oportunidades de otimização.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Funis pré-definidos
        self.FUNNELS = {
            "investigation_creation": {
                "name": "Criação de Investigação",
                "steps": [
                    "landing_page",
                    "login",
                    "dashboard",
                    "new_investigation_click",
                    "form_filled",
                    "investigation_created"
                ]
            },
            "investigation_completion": {
                "name": "Conclusão de Investigação",
                "steps": [
                    "investigation_created",
                    "scrapers_started",
                    "data_collected",
                    "report_viewed",
                    "investigation_completed"
                ]
            },
            "user_onboarding": {
                "name": "Onboarding de Usuário",
                "steps": [
                    "signup",
                    "email_verified",
                    "profile_completed",
                    "first_investigation",
                    "second_investigation"
                ]
            }
        }
    
    def analyze_funnel(
        self,
        funnel_key: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_segment: Optional[str] = None
    ) -> FunnelAnalysis:
        """
        Analisa um funil específico
        
        Args:
            funnel_key: Chave do funil (investigation_creation, etc)
            start_date: Data inicial
            end_date: Data final
            user_segment: Segmento de usuários (new, active, power)
            
        Returns:
            Análise completa do funil
        """
        if funnel_key not in self.FUNNELS:
            raise ValueError(f"Funil '{funnel_key}' não encontrado")
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        funnel_config = self.FUNNELS[funnel_key]
        
        # Coletar dados por etapa
        steps_data = []
        previous_users = None
        
        for i, step_name in enumerate(funnel_config["steps"]):
            step_data = self._analyze_step(
                step_name,
                i,
                start_date,
                end_date,
                previous_users,
                user_segment
            )
            steps_data.append(step_data)
            previous_users = step_data.users_completed
        
        # Calcular métricas gerais
        total_started = steps_data[0].users_entered if steps_data else 0
        total_completed = steps_data[-1].users_completed if steps_data else 0
        overall_conversion = (total_completed / total_started * 100) if total_started > 0 else 0
        
        avg_time = sum(s.average_time_seconds for s in steps_data) / len(steps_data) if steps_data else 0
        
        # Identificar gargalos
        bottlenecks = self._identify_bottlenecks(steps_data)
        
        # Gerar recomendações
        recommendations = self._generate_funnel_recommendations(steps_data, bottlenecks)
        
        return FunnelAnalysis(
            funnel_name=funnel_config["name"],
            total_users_started=total_started,
            total_users_completed=total_completed,
            overall_conversion_rate=round(overall_conversion, 2),
            average_completion_time_seconds=round(avg_time, 2),
            steps=steps_data,
            bottlenecks=bottlenecks,
            recommendations=recommendations
        )
    
    def _analyze_step(
        self,
        step_name: str,
        step_order: int,
        start_date: datetime,
        end_date: datetime,
        previous_users: Optional[int],
        user_segment: Optional[str]
    ) -> FunnelStep:
        """Analisa uma etapa específica do funil"""
        
        # Simular dados (em produção, viria de events tracking)
        # Mapear etapas para eventos reais do sistema
        
        if step_name in ["landing_page", "signup"]:
            users_entered = self.db.query(func.count(User.id)).filter(
                and_(
                    User.created_at >= start_date,
                    User.created_at <= end_date
                )
            ).scalar()
        elif "investigation" in step_name:
            users_entered = self.db.query(func.count(func.distinct(Investigation.user_id))).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date
                )
            ).scalar()
        else:
            # Usar previous_users ou estimar
            users_entered = previous_users or 100
        
        # Simular conversão baseada em patterns típicos
        conversion_rates = {
            "landing_page": 0.95,
            "login": 0.90,
            "dashboard": 0.85,
            "new_investigation_click": 0.70,
            "form_filled": 0.85,
            "investigation_created": 0.95,
            "scrapers_started": 0.90,
            "data_collected": 0.85,
            "report_viewed": 0.75,
            "investigation_completed": 0.80,
            "signup": 0.95,
            "email_verified": 0.85,
            "profile_completed": 0.70,
            "first_investigation": 0.80,
            "second_investigation": 0.60
        }
        
        base_conversion = conversion_rates.get(step_name, 0.75)
        users_completed = int(users_entered * base_conversion)
        
        conversion_rate = (users_completed / users_entered * 100) if users_entered > 0 else 0
        drop_off_rate = 100 - conversion_rate
        
        # Tempo médio por etapa (simulado)
        time_estimates = {
            "landing_page": 30,
            "login": 45,
            "dashboard": 60,
            "new_investigation_click": 10,
            "form_filled": 180,
            "investigation_created": 5,
            "scrapers_started": 10,
            "data_collected": 600,
            "report_viewed": 120,
            "investigation_completed": 60,
            "signup": 120,
            "email_verified": 300,
            "profile_completed": 180,
            "first_investigation": 900,
            "second_investigation": 600
        }
        
        avg_time = time_estimates.get(step_name, 120)
        median_time = avg_time * 0.8  # Mediana tipicamente menor que média
        
        return FunnelStep(
            step_name=step_name,
            step_order=step_order,
            users_entered=users_entered,
            users_completed=users_completed,
            conversion_rate=round(conversion_rate, 2),
            drop_off_rate=round(drop_off_rate, 2),
            average_time_seconds=avg_time,
            median_time_seconds=median_time
        )
    
    def _identify_bottlenecks(self, steps: List[FunnelStep]) -> List[str]:
        """Identifica gargalos no funil"""
        bottlenecks = []
        
        for step in steps:
            # Gargalo se drop-off > 30%
            if step.drop_off_rate > 30:
                bottlenecks.append(
                    f"{step.step_name}: {step.drop_off_rate:.1f}% de abandono"
                )
            
            # Gargalo se tempo muito alto (> 10 min)
            if step.average_time_seconds > 600:
                bottlenecks.append(
                    f"{step.step_name}: Tempo médio muito alto ({step.average_time_seconds/60:.1f} min)"
                )
        
        return bottlenecks
    
    def _generate_funnel_recommendations(
        self,
        steps: List[FunnelStep],
        bottlenecks: List[str]
    ) -> List[str]:
        """Gera recomendações de otimização"""
        recommendations = []
        
        if not steps:
            return ["Dados insuficientes para análise."]
        
        # Analisar conversão geral
        overall_conversion = (steps[-1].users_completed / steps[0].users_entered * 100) if steps[0].users_entered > 0 else 0
        
        if overall_conversion < 30:
            recommendations.append(
                f"⚠️ Conversão geral muito baixa ({overall_conversion:.1f}%). "
                "Revisar todo o funil urgentemente."
            )
        elif overall_conversion < 50:
            recommendations.append(
                f"📊 Conversão abaixo do ideal ({overall_conversion:.1f}%). "
                "Focar nos gargalos identificados."
            )
        
        # Recomendar para cada gargalo
        for bottleneck in bottlenecks:
            if "abandono" in bottleneck:
                recommendations.append(
                    f"🔴 {bottleneck.split(':')[0]}: Implementar melhorias de UX e reduzir fricção."
                )
            elif "Tempo" in bottleneck:
                recommendations.append(
                    f"⏱️ {bottleneck.split(':')[0]}: Otimizar performance e simplificar processo."
                )
        
        # Analisar drop-offs sequenciais
        high_dropoffs = [s for s in steps if s.drop_off_rate > 25]
        if len(high_dropoffs) > 2:
            recommendations.append(
                "💡 Múltiplas etapas com alto abandono. Considerar simplificar o fluxo."
            )
        
        return recommendations if recommendations else [
            "✅ Funil operando dentro dos parâmetros esperados."
        ]
    
    def get_funnel_comparison(
        self,
        funnel_key: str,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime
    ) -> Dict[str, Any]:
        """Compara funil em dois períodos diferentes"""
        
        funnel1 = self.analyze_funnel(funnel_key, period1_start, period1_end)
        funnel2 = self.analyze_funnel(funnel_key, period2_start, period2_end)
        
        # Calcular diferenças
        conversion_diff = funnel2.overall_conversion_rate - funnel1.overall_conversion_rate
        time_diff = funnel2.average_completion_time_seconds - funnel1.average_completion_time_seconds
        
        return {
            "period1": {
                "start": period1_start.isoformat(),
                "end": period1_end.isoformat(),
                "conversion_rate": funnel1.overall_conversion_rate,
                "avg_time": funnel1.average_completion_time_seconds
            },
            "period2": {
                "start": period2_start.isoformat(),
                "end": period2_end.isoformat(),
                "conversion_rate": funnel2.overall_conversion_rate,
                "avg_time": funnel2.average_completion_time_seconds
            },
            "changes": {
                "conversion_rate_change": round(conversion_diff, 2),
                "conversion_rate_change_pct": round((conversion_diff / funnel1.overall_conversion_rate * 100) if funnel1.overall_conversion_rate > 0 else 0, 2),
                "time_change_seconds": round(time_diff, 2),
                "trend": "improving" if conversion_diff > 0 else "declining" if conversion_diff < 0 else "stable"
            }
        }


# ============================================================================
# 2. FEATURE ADOPTION ANALYTICS
# ============================================================================

class FeatureAdoptionAnalytics:
    """
    Análise de Adoção de Funcionalidades
    
    Monitora quais features estão sendo usadas, por quem e com que frequência.
    Identifica features com baixa adoção e power users.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Features rastreadas
        self.FEATURES = {
            "investigations": "Criar Investigações",
            "scrapers": "Executar Scrapers",
            "reports": "Gerar Relatórios",
            "export": "Exportar Dados",
            "collaboration": "Colaboração",
            "analytics": "Ver Analytics",
            "advanced_search": "Busca Avançada",
            "api_access": "Acesso API",
            "webhooks": "Webhooks",
            "integrations": "Integrações"
        }
    
    def analyze_feature_adoption(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Analisa adoção de todas as features
        
        Returns:
            Análise completa de adoção
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        total_users = self.db.query(func.count(User.id)).filter(
            User.is_active == True
        ).scalar()
        
        features_data = []
        
        for feature_key, feature_name in self.FEATURES.items():
            usage = self._analyze_feature_usage(
                feature_key,
                feature_name,
                start_date,
                end_date,
                total_users
            )
            features_data.append(usage)
        
        # Ordenar por adoption rate
        features_data.sort(key=lambda x: x.adoption_rate, reverse=True)
        
        # Estatísticas gerais
        avg_adoption = sum(f.adoption_rate for f in features_data) / len(features_data) if features_data else 0
        
        high_adoption = [f for f in features_data if f.adoption_rate > 70]
        medium_adoption = [f for f in features_data if 30 <= f.adoption_rate <= 70]
        low_adoption = [f for f in features_data if f.adoption_rate < 30]
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "summary": {
                "total_users": total_users,
                "total_features": len(features_data),
                "average_adoption_rate": round(avg_adoption, 2),
                "high_adoption_features": len(high_adoption),
                "medium_adoption_features": len(medium_adoption),
                "low_adoption_features": len(low_adoption)
            },
            "features": [
                {
                    "name": f.feature_name,
                    "adoption_rate": round(f.adoption_rate, 2),
                    "active_users": f.active_users,
                    "usage_frequency": round(f.usage_frequency, 2),
                    "power_users": f.power_users,
                    "casual_users": f.casual_users,
                    "growth_rate": round(f.growth_rate, 2),
                    "status": self._get_adoption_status(f.adoption_rate)
                }
                for f in features_data
            ],
            "top_features": [
                {"name": f.feature_name, "adoption_rate": round(f.adoption_rate, 2)}
                for f in features_data[:5]
            ],
            "underperforming_features": [
                {"name": f.feature_name, "adoption_rate": round(f.adoption_rate, 2)}
                for f in low_adoption
            ],
            "recommendations": self._generate_adoption_recommendations(features_data)
        }
    
    def _analyze_feature_usage(
        self,
        feature_key: str,
        feature_name: str,
        start_date: datetime,
        end_date: datetime,
        total_users: int
    ) -> FeatureUsage:
        """Analisa uso de uma feature específica"""
        
        # Mapear features para eventos/queries reais
        if feature_key == "investigations":
            active_users = self.db.query(func.count(func.distinct(Investigation.user_id))).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date
                )
            ).scalar()
            
            # Frequência de uso
            total_investigations = self.db.query(func.count(Investigation.id)).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date
                )
            ).scalar()
            
            usage_frequency = total_investigations / active_users if active_users > 0 else 0
            
            # Power users (> 10 investigações)
            power_users_query = self.db.query(Investigation.user_id, func.count(Investigation.id).label('count')).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date
                )
            ).group_by(Investigation.user_id).having(func.count(Investigation.id) > 10).all()
            
            power_users = len(power_users_query)
            casual_users = active_users - power_users
            
        else:
            # Simular para outras features
            adoption_rates = {
                "scrapers": 0.85,
                "reports": 0.70,
                "export": 0.55,
                "collaboration": 0.40,
                "analytics": 0.30,
                "advanced_search": 0.25,
                "api_access": 0.15,
                "webhooks": 0.10,
                "integrations": 0.20
            }
            
            base_adoption = adoption_rates.get(feature_key, 0.50)
            active_users = int(total_users * base_adoption)
            usage_frequency = 3.5 if base_adoption > 0.5 else 1.8
            power_users = int(active_users * 0.2)
            casual_users = active_users - power_users
        
        adoption_rate = (active_users / total_users * 100) if total_users > 0 else 0
        
        # Growth rate (simulado - comparar com período anterior)
        growth_rate = 5.5 if adoption_rate > 50 else -2.3 if adoption_rate < 20 else 1.2
        
        return FeatureUsage(
            feature_name=feature_name,
            total_users=total_users,
            active_users=active_users,
            adoption_rate=adoption_rate,
            first_use_date=start_date,
            last_use_date=end_date,
            usage_frequency=usage_frequency,
            power_users=power_users,
            casual_users=casual_users,
            growth_rate=growth_rate
        )
    
    def _get_adoption_status(self, adoption_rate: float) -> str:
        """Determina status de adoção"""
        if adoption_rate >= 80:
            return "excellent"
        elif adoption_rate >= 60:
            return "good"
        elif adoption_rate >= 40:
            return "fair"
        elif adoption_rate >= 20:
            return "poor"
        else:
            return "critical"
    
    def _generate_adoption_recommendations(
        self,
        features: List[FeatureUsage]
    ) -> List[str]:
        """Gera recomendações de melhoria de adoção"""
        recommendations = []
        
        low_adoption = [f for f in features if f.adoption_rate < 30]
        
        if low_adoption:
            recommendations.append(
                f"⚠️ {len(low_adoption)} feature(s) com baixa adoção (<30%). "
                "Considerar melhorar onboarding e documentação."
            )
            
            for feature in low_adoption[:3]:
                recommendations.append(
                    f"📉 {feature.feature_name} ({feature.adoption_rate:.1f}%): "
                    "Criar tutoriais e destacar benefícios."
                )
        
        # Features em crescimento
        growing = [f for f in features if f.growth_rate > 5]
        if growing:
            recommendations.append(
                f"📈 {len(growing)} feature(s) com crescimento forte. "
                "Continuar investindo nestas áreas."
            )
        
        # Features em declínio
        declining = [f for f in features if f.growth_rate < -2]
        if declining:
            recommendations.append(
                f"🔴 {len(declining)} feature(s) em declínio. "
                "Investigar motivos e implementar melhorias."
            )
        
        return recommendations if recommendations else [
            "✅ Adoção de features saudável em geral."
        ]
    
    def get_user_adoption_profile(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """Perfil de adoção de um usuário específico"""
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Usuário {user_id} não encontrado")
        
        # Analisar quais features o usuário usa
        features_used = []
        
        # Investigations
        inv_count = self.db.query(func.count(Investigation.id)).filter(
            Investigation.user_id == user_id
        ).scalar()
        
        if inv_count > 0:
            status = self._determine_user_feature_status(inv_count, "investigations")
            features_used.append({
                "feature": "Investigações",
                "usage_count": inv_count,
                "status": status
            })
        
        # Simular outras features
        other_features = [
            ("Relatórios", 15, "adopting"),
            ("Exportação", 5, "exploring"),
            ("Analytics", 2, "exploring")
        ]
        
        for feat_name, count, status in other_features:
            features_used.append({
                "feature": feat_name,
                "usage_count": count,
                "status": status
            })
        
        # Calcular score geral de adoção
        adoption_score = min((len(features_used) / len(self.FEATURES)) * 100, 100)
        
        return {
            "user_id": user_id,
            "username": user.username,
            "features_used": len(features_used),
            "features_available": len(self.FEATURES),
            "adoption_score": round(adoption_score, 2),
            "user_type": self._classify_user_type(len(features_used), adoption_score),
            "features": features_used,
            "recommendations": self._generate_user_recommendations(features_used, adoption_score)
        }
    
    def _determine_user_feature_status(
        self,
        usage_count: int,
        feature_key: str
    ) -> str:
        """Determina status de adoção de feature para usuário"""
        if usage_count == 0:
            return FeatureAdoptionStatus.NOT_STARTED.value
        elif usage_count < 3:
            return FeatureAdoptionStatus.EXPLORING.value
        elif usage_count < 10:
            return FeatureAdoptionStatus.ADOPTING.value
        elif usage_count < 50:
            return FeatureAdoptionStatus.ADOPTED.value
        else:
            return FeatureAdoptionStatus.POWER_USER.value
    
    def _classify_user_type(
        self,
        features_used: int,
        adoption_score: float
    ) -> str:
        """Classifica tipo de usuário"""
        if adoption_score >= 70:
            return "power_user"
        elif adoption_score >= 40:
            return "active_user"
        elif adoption_score >= 20:
            return "casual_user"
        else:
            return "inactive_user"
    
    def _generate_user_recommendations(
        self,
        features_used: List[Dict],
        adoption_score: float
    ) -> List[str]:
        """Gera recomendações personalizadas para usuário"""
        recommendations = []
        
        if adoption_score < 30:
            recommendations.append(
                "💡 Você está usando apenas algumas funcionalidades. "
                "Explore mais features para aproveitar todo o potencial da plataforma!"
            )
        
        exploring = [f for f in features_used if f["status"] == "exploring"]
        if exploring:
            recommendations.append(
                f"🚀 Continue explorando: {', '.join(f['feature'] for f in exploring[:2])}. "
                "Veja tutoriais para dominar essas features."
            )
        
        if len(features_used) < 5:
            recommendations.append(
                "✨ Experimente novas funcionalidades como Colaboração, Analytics e Integrações."
            )
        
        return recommendations if recommendations else [
            "✅ Você está aproveitando bem a plataforma!"
        ]


# Continua no próximo arquivo...
