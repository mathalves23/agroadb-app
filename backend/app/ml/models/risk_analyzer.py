"""
Risk Analyzer - Análise de Risco Automatizada

Este módulo calcula um score de risco (0.0 a 1.0) para investigações
baseado em múltiplos fatores e indicadores suspeitos.

Score interpretation:
- 0.0 - 0.3: Baixo risco (verde)
- 0.3 - 0.6: Risco médio (amarelo)
- 0.6 - 0.8: Risco alto (laranja)
- 0.8 - 1.0: Risco crítico (vermelho)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import logging

from app.domain.investigation import Investigation
from app.domain.property import Property
from app.domain.company import Company
from app.domain.lease_contract import LeaseContract

logger = logging.getLogger(__name__)


class RiskFactor:
    """Representa um fator de risco individual"""
    
    def __init__(
        self,
        name: str,
        weight: float,
        score: float,
        evidence: str,
        severity: str
    ):
        self.name = name
        self.weight = weight  # Peso do fator (0.0 - 1.0)
        self.score = score  # Score deste fator (0.0 - 1.0)
        self.evidence = evidence  # Evidência encontrada
        self.severity = severity  # low, medium, high, critical
    
    def weighted_score(self) -> float:
        """Calcula o score ponderado"""
        return self.score * self.weight


class RiskAnalysis:
    """Resultado completo da análise de risco"""
    
    def __init__(
        self,
        investigation_id: int,
        overall_score: float,
        risk_level: str,
        factors: List[RiskFactor],
        recommendations: List[str],
        analyzed_at: datetime
    ):
        self.investigation_id = investigation_id
        self.overall_score = overall_score
        self.risk_level = risk_level
        self.factors = factors
        self.recommendations = recommendations
        self.analyzed_at = analyzed_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "investigation_id": self.investigation_id,
            "overall_score": round(self.overall_score, 3),
            "risk_level": self.risk_level,
            "risk_percentage": round(self.overall_score * 100, 1),
            "factors": [
                {
                    "name": f.name,
                    "weight": f.weight,
                    "score": round(f.score, 3),
                    "weighted_score": round(f.weighted_score(), 3),
                    "evidence": f.evidence,
                    "severity": f.severity
                }
                for f in self.factors
            ],
            "recommendations": self.recommendations,
            "analyzed_at": self.analyzed_at.isoformat(),
            "total_factors": len(self.factors),
            "critical_factors": sum(1 for f in self.factors if f.severity == "critical"),
            "high_factors": sum(1 for f in self.factors if f.severity == "high")
        }


class RiskAnalyzer:
    """
    Analisador de Risco para Investigações
    
    Analisa múltiplos fatores para calcular um score de risco geral:
    - Propriedades múltiplas e dispersas
    - Empresas offshore ou em paraísos fiscais
    - Contratos de arrendamento irregulares
    - CPFs/CNPJs relacionados
    - Histórico de processos judiciais
    - Área total muito grande
    - Propriedades em áreas de proteção ambiental
    - Sobreposição de propriedades
    """
    
    # Pesos dos fatores de risco (soma = 1.0)
    WEIGHTS = {
        "multiple_properties": 0.15,
        "offshore_companies": 0.20,
        "irregular_leases": 0.18,
        "related_entities": 0.12,
        "legal_issues": 0.15,
        "large_area": 0.08,
        "protected_areas": 0.07,
        "property_overlap": 0.05
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze(self, investigation_id: int) -> RiskAnalysis:
        """
        Analisa uma investigação e retorna o score de risco
        
        Args:
            investigation_id: ID da investigação
            
        Returns:
            RiskAnalysis com score e fatores detalhados
        """
        logger.info(f"Iniciando análise de risco para investigação {investigation_id}")
        
        # Buscar investigação
        investigation = self.db.query(Investigation).filter(
            Investigation.id == investigation_id
        ).first()
        
        if not investigation:
            raise ValueError(f"Investigação {investigation_id} não encontrada")
        
        # Analisar cada fator de risco
        factors: List[RiskFactor] = []
        
        factors.append(self._analyze_multiple_properties(investigation))
        factors.append(self._analyze_offshore_companies(investigation))
        factors.append(self._analyze_irregular_leases(investigation))
        factors.append(self._analyze_related_entities(investigation))
        factors.append(self._analyze_legal_issues(investigation))
        factors.append(self._analyze_large_area(investigation))
        factors.append(self._analyze_protected_areas(investigation))
        factors.append(self._analyze_property_overlap(investigation))
        
        # Calcular score geral (soma ponderada)
        overall_score = sum(f.weighted_score() for f in factors)
        
        # Determinar nível de risco
        risk_level = self._get_risk_level(overall_score)
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(factors, risk_level)
        
        # Criar análise
        analysis = RiskAnalysis(
            investigation_id=investigation_id,
            overall_score=overall_score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            analyzed_at=datetime.utcnow()
        )
        
        logger.info(
            f"Análise concluída: Score={overall_score:.3f}, "
            f"Level={risk_level}, Factors={len(factors)}"
        )
        
        return analysis
    
    def _analyze_multiple_properties(self, investigation: Investigation) -> RiskFactor:
        """Analisa múltiplas propriedades"""
        properties = investigation.properties or []
        count = len(properties)
        
        # Score baseado na quantidade
        if count == 0:
            score = 0.0
            evidence = "Nenhuma propriedade encontrada"
            severity = "low"
        elif count <= 2:
            score = 0.2
            evidence = f"{count} propriedades encontradas"
            severity = "low"
        elif count <= 5:
            score = 0.5
            evidence = f"{count} propriedades encontradas"
            severity = "medium"
        elif count <= 10:
            score = 0.75
            evidence = f"{count} propriedades encontradas"
            severity = "high"
        else:
            score = 1.0
            evidence = f"{count} propriedades encontradas (suspeito)"
            severity = "critical"
        
        return RiskFactor(
            name="Múltiplas Propriedades",
            weight=self.WEIGHTS["multiple_properties"],
            score=score,
            evidence=evidence,
            severity=severity
        )
    
    def _analyze_offshore_companies(self, investigation: Investigation) -> RiskFactor:
        """Analisa empresas offshore ou em paraísos fiscais"""
        # Lista de países considerados paraísos fiscais
        tax_havens = [
            "Ilhas Cayman", "Ilhas Virgens Britânicas", "Panamá", "Bahamas",
            "Bermudas", "Luxemburgo", "Suíça", "Liechtenstein", "Mônaco",
            "Andorra", "Jersey", "Guernsey", "Malta", "Chipre"
        ]
        
        companies = investigation.companies or []
        offshore_count = 0
        offshore_names = []
        
        for company in companies:
            # Verificar se empresa está em paraíso fiscal
            company_data = company.additional_data or {}
            country = company_data.get("country", "Brasil")
            
            if any(haven.lower() in country.lower() for haven in tax_havens):
                offshore_count += 1
                offshore_names.append(company.name)
        
        if offshore_count == 0:
            score = 0.0
            evidence = "Nenhuma empresa offshore detectada"
            severity = "low"
        elif offshore_count == 1:
            score = 0.7
            evidence = f"1 empresa offshore: {offshore_names[0]}"
            severity = "high"
        else:
            score = 1.0
            evidence = f"{offshore_count} empresas offshore: {', '.join(offshore_names[:3])}"
            severity = "critical"
        
        return RiskFactor(
            name="Empresas Offshore",
            weight=self.WEIGHTS["offshore_companies"],
            score=score,
            evidence=evidence,
            severity=severity
        )
    
    def _analyze_irregular_leases(self, investigation: Investigation) -> RiskFactor:
        """Analisa contratos de arrendamento irregulares"""
        leases = investigation.lease_contracts or []
        irregular_count = 0
        issues = []
        
        for lease in leases:
            # Verificar irregularidades
            
            # 1. Contrato vencido há muito tempo
            if lease.end_date and lease.end_date < datetime.utcnow() - timedelta(days=365):
                irregular_count += 1
                issues.append(f"Contrato vencido há mais de 1 ano")
            
            # 2. Valor muito baixo ou muito alto (suspeito)
            if lease.monthly_value:
                if lease.monthly_value < 100:
                    irregular_count += 1
                    issues.append(f"Valor mensal muito baixo (R$ {lease.monthly_value})")
                elif lease.monthly_value > 1000000:
                    irregular_count += 1
                    issues.append(f"Valor mensal muito alto (R$ {lease.monthly_value:,.2f})")
            
            # 3. Sem documento
            if not lease.document_number:
                irregular_count += 1
                issues.append("Contrato sem número de documento")
        
        if irregular_count == 0:
            score = 0.0
            evidence = "Nenhuma irregularidade nos contratos"
            severity = "low"
        elif irregular_count <= 2:
            score = 0.4
            evidence = f"{irregular_count} irregularidades: {'; '.join(issues[:2])}"
            severity = "medium"
        else:
            score = 0.9
            evidence = f"{irregular_count} irregularidades detectadas"
            severity = "critical"
        
        return RiskFactor(
            name="Contratos Irregulares",
            weight=self.WEIGHTS["irregular_leases"],
            score=score,
            evidence=evidence,
            severity=severity
        )
    
    def _analyze_related_entities(self, investigation: Investigation) -> RiskFactor:
        """Analisa relacionamentos entre pessoas e empresas"""
        # Contar CPFs/CNPJs únicos relacionados
        cpfs = set()
        cnpjs = set()
        
        # CPF/CNPJ do alvo
        if investigation.target_cpf:
            cpfs.add(investigation.target_cpf)
        if investigation.target_cnpj:
            cnpjs.add(investigation.target_cnpj)
        
        # Propriedades
        for prop in (investigation.properties or []):
            prop_data = prop.additional_data or {}
            if prop_data.get("owner_cpf"):
                cpfs.add(prop_data["owner_cpf"])
            if prop_data.get("owner_cnpj"):
                cnpjs.add(prop_data["owner_cnpj"])
        
        # Empresas
        for company in (investigation.companies or []):
            cnpjs.add(company.cnpj)
            
            # Sócios
            company_data = company.additional_data or {}
            partners = company_data.get("partners", [])
            for partner in partners:
                if partner.get("cpf"):
                    cpfs.add(partner["cpf"])
        
        total_entities = len(cpfs) + len(cnpjs)
        
        if total_entities <= 3:
            score = 0.0
            evidence = f"{total_entities} entidades relacionadas"
            severity = "low"
        elif total_entities <= 7:
            score = 0.4
            evidence = f"{total_entities} entidades relacionadas"
            severity = "medium"
        elif total_entities <= 15:
            score = 0.7
            evidence = f"{total_entities} entidades relacionadas (rede complexa)"
            severity = "high"
        else:
            score = 1.0
            evidence = f"{total_entities} entidades relacionadas (rede muito complexa)"
            severity = "critical"
        
        return RiskFactor(
            name="Entidades Relacionadas",
            weight=self.WEIGHTS["related_entities"],
            score=score,
            evidence=evidence,
            severity=severity
        )
    
    def _analyze_legal_issues(self, investigation: Investigation) -> RiskFactor:
        """Analisa problemas jurídicos"""
        legal_data = investigation.legal_integration_data or {}
        
        # Contar processos
        processos = legal_data.get("processos", [])
        processos_count = len(processos)
        
        # Contar tipos de processos (criminal é mais grave)
        criminal_count = sum(
            1 for p in processos 
            if "criminal" in p.get("tipo", "").lower()
        )
        
        if processos_count == 0:
            score = 0.0
            evidence = "Nenhum processo judicial encontrado"
            severity = "low"
        elif processos_count <= 2 and criminal_count == 0:
            score = 0.3
            evidence = f"{processos_count} processos cíveis"
            severity = "medium"
        elif processos_count <= 5 and criminal_count == 0:
            score = 0.6
            evidence = f"{processos_count} processos"
            severity = "high"
        elif criminal_count > 0:
            score = 0.95
            evidence = f"{processos_count} processos ({criminal_count} criminais)"
            severity = "critical"
        else:
            score = 0.8
            evidence = f"{processos_count} processos judiciais"
            severity = "high"
        
        return RiskFactor(
            name="Questões Jurídicas",
            weight=self.WEIGHTS["legal_issues"],
            score=score,
            evidence=evidence,
            severity=severity
        )
    
    def _analyze_large_area(self, investigation: Investigation) -> RiskFactor:
        """Analisa área total muito grande"""
        properties = investigation.properties or []
        total_area = sum(
            float(p.additional_data.get("area_hectares", 0) or 0)
            for p in properties
        )
        
        # Área em hectares
        if total_area < 100:
            score = 0.0
            evidence = f"Área total: {total_area:.1f} ha (pequena)"
            severity = "low"
        elif total_area < 500:
            score = 0.2
            evidence = f"Área total: {total_area:.1f} ha (média)"
            severity = "low"
        elif total_area < 2000:
            score = 0.5
            evidence = f"Área total: {total_area:.1f} ha (grande)"
            severity = "medium"
        elif total_area < 5000:
            score = 0.7
            evidence = f"Área total: {total_area:.1f} ha (muito grande)"
            severity = "high"
        else:
            score = 0.9
            evidence = f"Área total: {total_area:.1f} ha (suspeito)"
            severity = "critical"
        
        return RiskFactor(
            name="Área Total",
            weight=self.WEIGHTS["large_area"],
            score=score,
            evidence=evidence,
            severity=severity
        )
    
    def _analyze_protected_areas(self, investigation: Investigation) -> RiskFactor:
        """Analisa propriedades em áreas de proteção ambiental"""
        properties = investigation.properties or []
        protected_count = 0
        
        for prop in properties:
            prop_data = prop.additional_data or {}
            
            # Verificar se está em área protegida
            if prop_data.get("in_protected_area") or prop_data.get("em_area_protegida"):
                protected_count += 1
            
            # Verificar palavras-chave na descrição
            description = (prop_data.get("description", "") or "").lower()
            protected_keywords = [
                "reserva", "parque", "proteção ambiental", "unidade de conservação",
                "área indígena", "quilombola", "icmbio", "ibama"
            ]
            
            if any(keyword in description for keyword in protected_keywords):
                protected_count += 1
        
        if protected_count == 0:
            score = 0.0
            evidence = "Nenhuma propriedade em área protegida"
            severity = "low"
        elif protected_count == 1:
            score = 0.6
            evidence = "1 propriedade em área protegida"
            severity = "high"
        else:
            score = 1.0
            evidence = f"{protected_count} propriedades em áreas protegidas"
            severity = "critical"
        
        return RiskFactor(
            name="Áreas Protegidas",
            weight=self.WEIGHTS["protected_areas"],
            score=score,
            evidence=evidence,
            severity=severity
        )
    
    def _analyze_property_overlap(self, investigation: Investigation) -> RiskFactor:
        """Analisa sobreposição de propriedades (mesmo CAR/matrícula)"""
        properties = investigation.properties or []
        
        # Verificar CARs duplicados
        cars = [
            p.additional_data.get("car_code")
            for p in properties
            if p.additional_data and p.additional_data.get("car_code")
        ]
        
        duplicates = len(cars) - len(set(cars))
        
        if duplicates == 0:
            score = 0.0
            evidence = "Nenhuma sobreposição detectada"
            severity = "low"
        elif duplicates <= 2:
            score = 0.5
            evidence = f"{duplicates} possíveis sobreposições"
            severity = "medium"
        else:
            score = 1.0
            evidence = f"{duplicates} sobreposições detectadas (suspeito)"
            severity = "critical"
        
        return RiskFactor(
            name="Sobreposição de Propriedades",
            weight=self.WEIGHTS["property_overlap"],
            score=score,
            evidence=evidence,
            severity=severity
        )
    
    def _get_risk_level(self, score: float) -> str:
        """Determina o nível de risco baseado no score"""
        if score < 0.3:
            return "low"
        elif score < 0.6:
            return "medium"
        elif score < 0.8:
            return "high"
        else:
            return "critical"
    
    def _generate_recommendations(
        self,
        factors: List[RiskFactor],
        risk_level: str
    ) -> List[str]:
        """Gera recomendações baseadas nos fatores de risco"""
        recommendations = []
        
        # Recomendações gerais por nível
        if risk_level == "critical":
            recommendations.append(
                "⚠️ ATENÇÃO: Score de risco CRÍTICO. Recomenda-se investigação aprofundada imediata."
            )
        elif risk_level == "high":
            recommendations.append(
                "⚠️ Score de risco ALTO. Verificação adicional é recomendada."
            )
        
        # Recomendações específicas por fator
        for factor in factors:
            if factor.severity in ["high", "critical"]:
                if "offshore" in factor.name.lower():
                    recommendations.append(
                        "🏢 Investigar estrutura societária das empresas offshore identificadas"
                    )
                elif "propriedade" in factor.name.lower():
                    recommendations.append(
                        "📍 Verificar regularidade fundiária de todas as propriedades"
                    )
                elif "contrato" in factor.name.lower():
                    recommendations.append(
                        "📄 Solicitar documentação completa dos contratos de arrendamento"
                    )
                elif "jurídica" in factor.name.lower():
                    recommendations.append(
                        "⚖️ Analisar processos judiciais em andamento e histórico"
                    )
                elif "protegida" in factor.name.lower():
                    recommendations.append(
                        "🌳 Verificar licenças ambientais e conformidade com ICMBio/IBAMA"
                    )
                elif "entidade" in factor.name.lower():
                    recommendations.append(
                        "🔗 Mapear rede completa de relacionamentos entre pessoas e empresas"
                    )
        
        # Recomendação final
        if not recommendations:
            recommendations.append(
                "✅ Risco baixo. Manter monitoramento regular."
            )
        else:
            recommendations.append(
                "📊 Gerar relatório detalhado para análise aprofundada"
            )
        
        return recommendations
