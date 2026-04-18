"""
Sistema de Machine Learning para Score de Risco
Detecta padrões e calcula score de risco para investigações
"""
import numpy as np
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from app.core.config import settings
from app.services.ml.risk_calibration import apply_risk_calibration, load_calibration_config
from app.services.ml.risk_shap import additive_shap_for_indicators

logger = logging.getLogger(__name__)


@dataclass
class RiskIndicator:
    """Indicador de risco"""
    name: str
    value: float
    weight: float
    description: str
    severity: str  # low, medium, high, critical


@dataclass
class RiskScore:
    """Score de risco calculado"""
    total_score: float  # 0-100 (pós-calibração, se activa)
    risk_level: str  # very_low, low, medium, high, critical
    confidence: float  # 0-1
    indicators: List[RiskIndicator]
    patterns_detected: List[str]
    recommendations: List[str]
    timestamp: datetime
    raw_total_score: float = 0.0
    calibration_meta: Dict[str, Any] = field(default_factory=dict)
    shap_explanation: Dict[str, Any] = field(default_factory=dict)


class RiskScoringEngine:
    """
    Engine de Machine Learning para cálculo de score de risco
    
    Analisa múltiplos fatores:
    - Quantidade de propriedades
    - Valor total de contratos
    - Histórico judicial
    - Empresas relacionadas
    - Padrões suspeitos
    """
    
    # Pesos dos fatores de risco (devem somar 1.0)
    WEIGHTS = {
        'property_concentration': 0.15,  # Concentração de propriedades
        'contract_value': 0.20,          # Valor de contratos
        'legal_issues': 0.25,            # Questões judiciais
        'company_network': 0.15,         # Rede de empresas
        'temporal_patterns': 0.10,       # Padrões temporais
        'geographic_dispersion': 0.10,   # Dispersão geográfica
        'data_quality': 0.05             # Qualidade dos dados
    }
    
    @classmethod
    async def calculate_risk_score(
        cls,
        db,
        investigation_id: int
    ) -> RiskScore:
        """
        Calcula score de risco para uma investigação
        """
        try:
            from sqlalchemy import select
            from app.domain.investigation import Investigation
            
            # Buscar investigação
            query = select(Investigation).where(Investigation.id == investigation_id)
            result = await db.execute(query)
            investigation = result.scalar_one_or_none()
            
            if not investigation:
                raise ValueError(f"Investigação {investigation_id} não encontrada")
            
            indicators = []
            patterns = []
            
            # 1. Concentração de Propriedades
            property_score, property_patterns = await cls._analyze_property_concentration(
                db, investigation
            )
            indicators.append(RiskIndicator(
                name='property_concentration',
                value=property_score,
                weight=cls.WEIGHTS['property_concentration'],
                description='Concentração de propriedades rurais',
                severity=cls._get_severity(property_score)
            ))
            patterns.extend(property_patterns)
        except Exception as e:
            if isinstance(e, ValueError) and "não encontrada" in str(e).lower():
                raise
            logger.error(f"Erro ao calcular risk score para investigação {investigation_id}: {e}")
            # Retornar score básico de fallback
            return RiskScore(
                total_score=50.0,
                risk_level='medium',
                confidence=0.5,
                indicators=[
                    RiskIndicator(
                        name='basic_analysis',
                        value=50.0,
                        weight=1.0,
                        description='Análise básica (alguns dados indisponíveis)',
                        severity='medium'
                    )
                ],
                patterns_detected=['Análise completa em desenvolvimento'],
                recommendations=['Sistema de ML ainda está sendo calibrado'],
                timestamp=datetime.utcnow(),
                raw_total_score=50.0,
                calibration_meta={"calibration_enabled": False},
                shap_explanation={},
            )
        
        # 2. Valor de Contratos
        contract_score, contract_patterns = await cls._analyze_contract_values(
            db, investigation
        )
        indicators.append(RiskIndicator(
            name='contract_value',
            value=contract_score,
            weight=cls.WEIGHTS['contract_value'],
            description='Valor total de contratos de arrendamento',
            severity=cls._get_severity(contract_score)
        ))
        patterns.extend(contract_patterns)
        
        # 3. Questões Judiciais
        legal_score, legal_patterns = await cls._analyze_legal_issues(
            db, investigation
        )
        indicators.append(RiskIndicator(
            name='legal_issues',
            value=legal_score,
            weight=cls.WEIGHTS['legal_issues'],
            description='Processos judiciais e questões legais',
            severity=cls._get_severity(legal_score)
        ))
        patterns.extend(legal_patterns)
        
        # 4. Rede de Empresas
        company_score, company_patterns = await cls._analyze_company_network(
            db, investigation
        )
        indicators.append(RiskIndicator(
            name='company_network',
            value=company_score,
            weight=cls.WEIGHTS['company_network'],
            description='Complexidade da rede de empresas',
            severity=cls._get_severity(company_score)
        ))
        patterns.extend(company_patterns)
        
        # 5. Padrões Temporais
        temporal_score, temporal_patterns = await cls._analyze_temporal_patterns(
            db, investigation
        )
        indicators.append(RiskIndicator(
            name='temporal_patterns',
            value=temporal_score,
            weight=cls.WEIGHTS['temporal_patterns'],
            description='Padrões temporais suspeitos',
            severity=cls._get_severity(temporal_score)
        ))
        patterns.extend(temporal_patterns)
        
        # 6. Dispersão Geográfica
        geo_score, geo_patterns = await cls._analyze_geographic_dispersion(
            db, investigation
        )
        indicators.append(RiskIndicator(
            name='geographic_dispersion',
            value=geo_score,
            weight=cls.WEIGHTS['geographic_dispersion'],
            description='Dispersão geográfica de ativos',
            severity=cls._get_severity(geo_score)
        ))
        patterns.extend(geo_patterns)
        
        # 7. Qualidade dos Dados
        data_score = await cls._analyze_data_quality(db, investigation)
        indicators.append(RiskIndicator(
            name='data_quality',
            value=data_score,
            weight=cls.WEIGHTS['data_quality'],
            description='Completude e qualidade dos dados',
            severity=cls._get_severity(data_score)
        ))
        
        # Score bruto (linear nos indicadores)
        total_raw = sum(ind.value * ind.weight for ind in indicators)
        total_raw = round(total_raw, 2)

        cal_cfg = load_calibration_config(settings.RISK_CALIBRATION_PATH)
        total_score, cal_meta = apply_risk_calibration(total_raw, cal_cfg)

        shap_explanation = additive_shap_for_indicators(
            indicators,
            cls.WEIGHTS,
            neutral_baseline=float(settings.RISK_SHAP_NEUTRAL_BASELINE),
        )
        shap_explanation["prediction_calibrated"] = round(total_score, 2)
        shap_explanation["calibration_adjustment"] = round(total_score - total_raw, 4)

        # Calcular confiança baseada na qualidade dos dados
        confidence = 1.0 - (data_score / 100.0)
        
        # Determinar nível de risco
        risk_level = cls._determine_risk_level(total_score)
        
        # Gerar recomendações
        recommendations = cls._generate_recommendations(
            indicators, patterns, risk_level
        )
        
        logger.info(
            f"✅ Risk score calculado: raw={total_raw:.2f} calibrado={total_score:.2f} "
            f"({risk_level}) para investigação {investigation_id}"
        )
        
        return RiskScore(
            total_score=round(total_score, 2),
            risk_level=risk_level,
            confidence=round(confidence, 2),
            indicators=indicators,
            patterns_detected=patterns,
            recommendations=recommendations,
            timestamp=datetime.utcnow(),
            raw_total_score=total_raw,
            calibration_meta=cal_meta,
            shap_explanation=shap_explanation,
        )
    
    @classmethod
    async def _analyze_property_concentration(
        cls, db, investigation
    ) -> Tuple[float, List[str]]:
        """Analisa concentração de propriedades"""
        from sqlalchemy import select, func
        from app.domain.property import Property
        
        patterns = []
        
        # Buscar propriedades
        query = select(Property).where(
            Property.investigation_id == investigation.id
        )
        result = await db.execute(query)
        properties = result.scalars().all()
        
        if not properties:
            return 0.0, patterns
        
        num_properties = len(properties)
        total_area = sum(p.area_hectares or 0 for p in properties)
        
        # Score baseado em quantidade e área
        score = 0.0
        
        # Muitas propriedades = maior risco
        if num_properties >= 50:
            score += 40
            patterns.append(f"Alta concentração: {num_properties} propriedades")
        elif num_properties >= 20:
            score += 25
            patterns.append(f"Concentração moderada: {num_properties} propriedades")
        elif num_properties >= 10:
            score += 15
        
        # Grande área total = maior risco
        if total_area >= 100000:  # 100 mil hectares
            score += 35
            patterns.append(f"Área total crítica: {total_area:,.0f} hectares")
        elif total_area >= 50000:
            score += 20
            patterns.append(f"Área total alta: {total_area:,.0f} hectares")
        elif total_area >= 10000:
            score += 10
        
        # Propriedades em estados diferentes
        states = {p.state for p in properties if p.state}
        if len(states) >= 5:
            score += 25
            patterns.append(f"Propriedades em {len(states)} estados diferentes")
        elif len(states) >= 3:
            score += 15
        
        return min(score, 100.0), patterns
    
    @classmethod
    async def _analyze_contract_values(
        cls, db, investigation
    ) -> Tuple[float, List[str]]:
        """Analisa valores de contratos"""
        from sqlalchemy import select
        from app.domain.lease_contract import LeaseContract
        
        patterns = []
        
        query = select(LeaseContract).where(
            LeaseContract.investigation_id == investigation.id
        )
        result = await db.execute(query)
        contracts = result.scalars().all()
        
        if not contracts:
            return 0.0, patterns
        
        total_value = sum(c.value or 0 for c in contracts)
        num_contracts = len(contracts)
        
        score = 0.0
        
        # Valor total alto
        if total_value >= 100_000_000:  # 100 milhões
            score += 50
            patterns.append(f"Valor total crítico: R$ {total_value:,.2f}")
        elif total_value >= 50_000_000:
            score += 35
            patterns.append(f"Valor total alto: R$ {total_value:,.2f}")
        elif total_value >= 10_000_000:
            score += 20
        
        # Muitos contratos
        if num_contracts >= 30:
            score += 30
            patterns.append(f"Grande quantidade de contratos: {num_contracts}")
        elif num_contracts >= 15:
            score += 20
        
        # Contratos com valores discrepantes
        if contracts:
            values = [c.value for c in contracts if c.value]
            if values:
                avg_value = np.mean(values)
                std_value = np.std(values)
                
                outliers = [v for v in values if abs(v - avg_value) > 2 * std_value]
                if outliers:
                    score += 20
                    patterns.append(
                        f"Detectados {len(outliers)} contratos com valores atípicos"
                    )
        
        return min(score, 100.0), patterns
    
    @classmethod
    async def _analyze_legal_issues(
        cls, db, investigation
    ) -> Tuple[float, List[str]]:
        """Analisa questões judiciais"""
        from sqlalchemy import select, func
        from app.domain.legal_query import LegalQuery
        
        patterns = []
        
        query = select(LegalQuery).where(
            LegalQuery.investigation_id == investigation.id
        )
        result = await db.execute(query)
        legal_queries = result.scalars().all()
        
        if not legal_queries:
            return 0.0, patterns
        
        score = 0.0
        num_active_cases = 0
        critical_subjects = 0
        
        # Palavras-chave críticas
        critical_keywords = [
            'fraude', 'corrupção', 'lavagem', 'grilagem',
            'desmatamento', 'embargo', 'crime ambiental'
        ]
        
        for query_obj in legal_queries:
            if query_obj.status == 'ACTIVE':
                num_active_cases += 1
            
            # Verificar palavras críticas
            if query_obj.subject:
                for keyword in critical_keywords:
                    if keyword.lower() in query_obj.subject.lower():
                        critical_subjects += 1
                        break
        
        # Score baseado em casos ativos
        if num_active_cases >= 20:
            score += 50
            patterns.append(f"Casos judiciais ativos: {num_active_cases}")
        elif num_active_cases >= 10:
            score += 35
            patterns.append(f"Casos judiciais ativos: {num_active_cases}")
        elif num_active_cases >= 5:
            score += 20
        
        # Assuntos críticos
        if critical_subjects >= 5:
            score += 50
            patterns.append(
                f"Detectados {critical_subjects} processos com assuntos críticos"
            )
        elif critical_subjects >= 2:
            score += 30
            patterns.append(f"Processos com assuntos críticos: {critical_subjects}")
        
        return min(score, 100.0), patterns
    
    @classmethod
    async def _analyze_company_network(
        cls, db, investigation
    ) -> Tuple[float, List[str]]:
        """Analisa rede de empresas"""
        from sqlalchemy import select
        from app.domain.company import Company
        
        patterns = []
        
        query = select(Company).where(
            Company.investigation_id == investigation.id
        )
        result = await db.execute(query)
        companies = result.scalars().all()
        
        if not companies:
            return 0.0, patterns
        
        num_companies = len(companies)
        inactive_companies = sum(
            1 for c in companies 
            if c.status and 'inativa' in c.status.lower()
        )
        
        score = 0.0
        
        # Muitas empresas
        if num_companies >= 30:
            score += 40
            patterns.append(f"Rede empresarial extensa: {num_companies} empresas")
        elif num_companies >= 15:
            score += 25
        elif num_companies >= 5:
            score += 15
        
        # Alta proporção de empresas inativas (possível fraude)
        if inactive_companies > 0:
            inactive_ratio = inactive_companies / num_companies
            if inactive_ratio >= 0.5:
                score += 40
                patterns.append(
                    f"Alta taxa de empresas inativas: "
                    f"{inactive_companies}/{num_companies}"
                )
            elif inactive_ratio >= 0.3:
                score += 25
        
        # Empresas em múltiplos estados
        states = {c.state for c in companies if c.state}
        if len(states) >= 5:
            score += 20
            patterns.append(f"Empresas em {len(states)} estados")
        
        return min(score, 100.0), patterns
    
    @classmethod
    async def _analyze_temporal_patterns(
        cls, db, investigation
    ) -> Tuple[float, List[str]]:
        """Analisa padrões temporais suspeitos"""
        from sqlalchemy import select
        from app.domain.company import Company
        from app.domain.property import Property
        
        patterns = []
        score = 0.0
        
        # Empresas criadas em sequência rápida
        query = select(Company).where(
            Company.investigation_id == investigation.id,
            Company.opening_date.isnot(None)
        ).order_by(Company.opening_date)
        
        result = await db.execute(query)
        companies = result.scalars().all()
        
        if len(companies) >= 3:
            dates = [c.opening_date for c in companies if c.opening_date]
            
            # Verificar empresas criadas em até 30 dias
            rapid_creation = 0
            for i in range(len(dates) - 1):
                if dates[i] and dates[i+1]:
                    diff = (dates[i+1] - dates[i]).days
                    if diff <= 30:
                        rapid_creation += 1
            
            if rapid_creation >= 5:
                score += 40
                patterns.append(
                    f"Detectadas {rapid_creation} empresas criadas "
                    "em sequência rápida (suspeito)"
                )
            elif rapid_creation >= 3:
                score += 25
        
        # Propriedades registradas recentemente
        query = select(Property).where(
            Property.investigation_id == investigation.id,
            Property.created_at >= datetime.utcnow() - timedelta(days=180)
        )
        result = await db.execute(query)
        recent_properties = result.scalars().all()
        
        if len(recent_properties) >= 10:
            score += 30
            patterns.append(
                f"{len(recent_properties)} propriedades registradas "
                "nos últimos 6 meses"
            )
        
        return min(score, 100.0), patterns
    
    @classmethod
    async def _analyze_geographic_dispersion(
        cls, db, investigation
    ) -> Tuple[float, List[str]]:
        """Analisa dispersão geográfica"""
        from sqlalchemy import select
        from app.domain.property import Property
        
        patterns = []
        
        query = select(Property).where(
            Property.investigation_id == investigation.id
        )
        result = await db.execute(query)
        properties = result.scalars().all()
        
        if not properties:
            return 0.0, patterns
        
        score = 0.0
        
        # Estados únicos
        states = {p.state for p in properties if p.state}
        num_states = len(states)
        
        # Cidades únicas
        cities = {(p.state, p.city) for p in properties if p.state and p.city}
        num_cities = len(cities)
        
        # Alta dispersão geográfica
        if num_states >= 10:
            score += 50
            patterns.append(f"Alta dispersão: propriedades em {num_states} estados")
        elif num_states >= 5:
            score += 30
            patterns.append(f"Dispersão moderada: {num_states} estados")
        elif num_states >= 3:
            score += 15
        
        if num_cities >= 50:
            score += 25
            patterns.append(f"Propriedades em {num_cities} cidades diferentes")
        elif num_cities >= 20:
            score += 15
        
        return min(score, 100.0), patterns
    
    @classmethod
    async def _analyze_data_quality(cls, db, investigation) -> float:
        """Analisa qualidade e completude dos dados"""
        from sqlalchemy import select
        from app.domain.property import Property
        from app.domain.company import Company
        
        score = 0.0
        total_fields = 0
        missing_fields = 0
        
        # Verificar completude de propriedades
        query = select(Property).where(
            Property.investigation_id == investigation.id
        )
        result = await db.execute(query)
        properties = result.scalars().all()
        
        for prop in properties:
            fields = [
                prop.property_name, prop.car_number, prop.area_hectares,
                prop.owner_name, prop.owner_cpf_cnpj
            ]
            total_fields += len(fields)
            missing_fields += sum(1 for f in fields if not f)
        
        # Verificar completude de empresas
        query = select(Company).where(
            Company.investigation_id == investigation.id
        )
        result = await db.execute(query)
        companies = result.scalars().all()
        
        for company in companies:
            fields = [
                company.corporate_name, company.cnpj, company.status,
                company.opening_date, company.main_activity
            ]
            total_fields += len(fields)
            missing_fields += sum(1 for f in fields if not f)
        
        # Score de qualidade (invertido: mais missing = maior score)
        if total_fields > 0:
            completeness = 1.0 - (missing_fields / total_fields)
            score = (1.0 - completeness) * 100
        
        return min(score, 100.0)
    
    @staticmethod
    def _get_severity(score: float) -> str:
        """Determina severidade baseada no score"""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def _determine_risk_level(score: float) -> str:
        """Determina nível de risco baseado no score total"""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        elif score >= 20:
            return 'low'
        else:
            return 'very_low'
    
    @staticmethod
    def _generate_recommendations(
        indicators: List[RiskIndicator],
        patterns: List[str],
        risk_level: str
    ) -> List[str]:
        """Gera recomendações baseadas no score"""
        recommendations = []
        
        if risk_level in ['critical', 'high']:
            recommendations.append(
                "⚠️ Investigação prioritária: risco elevado detectado"
            )
            recommendations.append(
                "Considere análise detalhada manual dos dados"
            )
        
        # Recomendações específicas por indicador
        for ind in indicators:
            if ind.severity in ['critical', 'high']:
                if ind.name == 'property_concentration':
                    recommendations.append(
                        "🏞️ Investigar origem e legitimidade das propriedades"
                    )
                elif ind.name == 'legal_issues':
                    recommendations.append(
                        "⚖️ Analisar processos judiciais em andamento"
                    )
                elif ind.name == 'company_network':
                    recommendations.append(
                        "🏢 Mapear rede de empresas e sócios"
                    )
                elif ind.name == 'contract_value':
                    recommendations.append(
                        "💰 Verificar origem dos recursos dos contratos"
                    )
        
        if not recommendations:
            recommendations.append(
                "✅ Investigação dentro dos parâmetros normais"
            )
        
        return recommendations
