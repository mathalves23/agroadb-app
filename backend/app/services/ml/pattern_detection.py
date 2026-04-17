"""
Sistema de Detecção de Padrões e Anomalias
Usa algoritmos de ML para detectar comportamentos suspeitos
"""
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """Padrão detectado"""
    type: str
    confidence: float  # 0-1
    description: str
    entities: List[int]  # IDs das entidades envolvidas
    severity: str  # low, medium, high, critical
    evidence: Dict


@dataclass
class Anomaly:
    """Anomalia detectada"""
    type: str
    confidence: float
    description: str
    entity_id: int
    expected_value: float
    actual_value: float
    deviation: float


class PatternDetectionEngine:
    """
    Engine de detecção de padrões suspeitos
    
    Detecta:
    - Laranjas (pessoas/empresas de fachada)
    - Rede de empresas suspeita
    - Transações circular es
    - Concentração geográfica anormal
    - Padrões de data/hora suspeitos
    """
    
    @classmethod
    async def detect_patterns(
        cls,
        db,
        investigation_id: int
    ) -> List[Pattern]:
        """Detecta todos os padrões suspeitos"""
        try:
            patterns = []
            
            # 1. Detectar laranjas
            laranja_patterns = await cls._detect_laranjas(db, investigation_id)
            patterns.extend(laranja_patterns)
            
            # 2. Detectar rede suspeita de empresas
            network_patterns = await cls._detect_suspicious_network(db, investigation_id)
            patterns.extend(network_patterns)
            
            # 3. Detectar transações circulares
            circular_patterns = await cls._detect_circular_transactions(
                db, investigation_id
            )
            patterns.extend(circular_patterns)
            
            # 4. Detectar concentração anormal
            concentration_patterns = await cls._detect_abnormal_concentration(
                db, investigation_id
            )
            patterns.extend(concentration_patterns)
            
            # 5. Detectar padrões temporais suspeitos
            temporal_patterns = await cls._detect_temporal_anomalies(
                db, investigation_id
            )
            patterns.extend(temporal_patterns)
            
            logger.info(
                f"✅ Detectados {len(patterns)} padrões para "
                f"investigação {investigation_id}"
            )
            
            return patterns
        except Exception as e:
            logger.error(f"Erro ao detectar padrões para investigação {investigation_id}: {e}")
            # Retornar lista vazia como fallback
            return []
    
    @classmethod
    async def _detect_laranjas(
        cls, db, investigation_id: int
    ) -> List[Pattern]:
        """
        Detecta possíveis laranjas (pessoas/empresas de fachada)
        
        Indicadores:
        - Empresas com mesmo endereço
        - Sócios com participação em muitas empresas
        - Empresas abertas em sequência rápida
        - Capital social muito baixo
        """
        from sqlalchemy import select, func
        from app.domain.company import Company
        
        patterns = []
        
        # Buscar empresas
        query = select(Company).where(
            Company.investigation_id == investigation_id
        )
        result = await db.execute(query)
        companies = list(result.scalars().all())
        
        if len(companies) < 3:
            return patterns
        
        # 1. Empresas no mesmo endereço (suspeito de sede única)
        address_groups = {}
        for company in companies:
            if company.address:
                addr = f"{company.address} - {company.city}/{company.state}"
                if addr not in address_groups:
                    address_groups[addr] = []
                address_groups[addr].append(company)
        
        for address, comps in address_groups.items():
            if len(comps) >= 5:
                patterns.append(Pattern(
                    type='laranja_same_address',
                    confidence=0.85,
                    description=f'{len(comps)} empresas no mesmo endereço',
                    entities=[c.id for c in comps],
                    severity='high',
                    evidence={
                        'address': address,
                        'num_companies': len(comps),
                        'companies': [c.corporate_name for c in comps]
                    }
                ))
        
        # 2. Capital social muito baixo em muitas empresas
        low_capital_companies = [
            c for c in companies
            if c.capital and c.capital < 10000  # Menos de 10 mil
        ]
        
        if len(low_capital_companies) >= 10:
            patterns.append(Pattern(
                type='laranja_low_capital',
                confidence=0.70,
                description=f'{len(low_capital_companies)} empresas com capital social muito baixo',
                entities=[c.id for c in low_capital_companies],
                severity='medium',
                evidence={
                    'num_companies': len(low_capital_companies),
                    'avg_capital': np.mean([c.capital for c in low_capital_companies])
                }
            ))
        
        # 3. Empresas abertas em sequência rápida (30 dias)
        dated_companies = [c for c in companies if c.opening_date]
        dated_companies.sort(key=lambda x: x.opening_date)
        
        rapid_sequence = []
        for i in range(len(dated_companies) - 1):
            c1, c2 = dated_companies[i], dated_companies[i+1]
            if c1.opening_date and c2.opening_date:
                days_diff = (c2.opening_date - c1.opening_date).days
                if days_diff <= 30:
                    rapid_sequence.append((c1, c2, days_diff))
        
        if len(rapid_sequence) >= 5:
            patterns.append(Pattern(
                type='laranja_rapid_creation',
                confidence=0.80,
                description=f'{len(rapid_sequence)} pares de empresas criadas em sequência rápida',
                entities=[c.id for pair in rapid_sequence for c in pair[:2]],
                severity='high',
                evidence={
                    'num_sequences': len(rapid_sequence),
                    'sequences': [
                        {
                            'company1': pair[0].corporate_name,
                            'company2': pair[1].corporate_name,
                            'days_apart': pair[2]
                        }
                        for pair in rapid_sequence[:5]  # Primeiros 5
                    ]
                }
            ))
        
        return patterns
    
    @classmethod
    async def _detect_suspicious_network(
        cls, db, investigation_id: int
    ) -> List[Pattern]:
        """Detecta rede suspeita de empresas"""
        from sqlalchemy import select
        from app.domain.company import Company
        
        patterns = []
        
        query = select(Company).where(
            Company.investigation_id == investigation_id
        )
        result = await db.execute(query)
        companies = list(result.scalars().all())
        
        if len(companies) < 10:
            return patterns
        
        # 1. Alta proporção de empresas inativas (> 40%)
        inactive = [c for c in companies if c.status and 'inativa' in c.status.lower()]
        inactive_ratio = len(inactive) / len(companies)
        
        if inactive_ratio > 0.4:
            patterns.append(Pattern(
                type='suspicious_network_inactive',
                confidence=0.75,
                description=f'{int(inactive_ratio*100)}% das empresas estão inativas',
                entities=[c.id for c in inactive],
                severity='high',
                evidence={
                    'total_companies': len(companies),
                    'inactive_companies': len(inactive),
                    'inactive_ratio': inactive_ratio
                }
            ))
        
        # 2. Empresas com mesma atividade principal (possível cartel)
        activity_groups = {}
        for c in companies:
            if c.main_activity:
                if c.main_activity not in activity_groups:
                    activity_groups[c.main_activity] = []
                activity_groups[c.main_activity].append(c)
        
        for activity, comps in activity_groups.items():
            if len(comps) >= 8:
                patterns.append(Pattern(
                    type='suspicious_network_same_activity',
                    confidence=0.65,
                    description=f'{len(comps)} empresas com mesma atividade',
                    entities=[c.id for c in comps],
                    severity='medium',
                    evidence={
                        'activity': activity,
                        'num_companies': len(comps)
                    }
                ))
        
        return patterns
    
    @classmethod
    async def _detect_circular_transactions(
        cls, db, investigation_id: int
    ) -> List[Pattern]:
        """Detecta transações circulares entre empresas"""
        from sqlalchemy import select
        from app.domain.lease_contract import LeaseContract
        
        patterns = []
        
        # Buscar contratos
        query = select(LeaseContract).where(
            LeaseContract.investigation_id == investigation_id
        )
        result = await db.execute(query)
        contracts = list(result.scalars().all())
        
        if len(contracts) < 3:
            return patterns
        
        # Criar grafo de transações
        transaction_graph = {}
        for contract in contracts:
            if contract.lessor_cpf_cnpj and contract.lessee_cpf_cnpj:
                lessor = contract.lessor_cpf_cnpj
                lessee = contract.lessee_cpf_cnpj
                
                if lessor not in transaction_graph:
                    transaction_graph[lessor] = {'out': [], 'in': []}
                if lessee not in transaction_graph:
                    transaction_graph[lessee] = {'out': [], 'in': []}
                
                transaction_graph[lessor]['out'].append(lessee)
                transaction_graph[lessee]['in'].append(lessor)
        
        # Detectar ciclos simples (A -> B -> A)
        cycles_found = []
        for entity_a, connections in transaction_graph.items():
            for entity_b in connections['out']:
                if entity_b in transaction_graph:
                    # Verificar se B tem transação de volta para A
                    if entity_a in transaction_graph[entity_b]['out']:
                        cycles_found.append((entity_a, entity_b))
        
        if cycles_found:
            patterns.append(Pattern(
                type='circular_transactions',
                confidence=0.90,
                description=f'Detectados {len(cycles_found)} ciclos de transações',
                entities=[],  # Entidades são CPF/CNPJ, não IDs
                severity='critical',
                evidence={
                    'num_cycles': len(cycles_found),
                    'cycles': [
                        {'entity_a': cycle[0], 'entity_b': cycle[1]}
                        for cycle in cycles_found[:5]
                    ]
                }
            ))
        
        return patterns
    
    @classmethod
    async def _detect_abnormal_concentration(
        cls, db, investigation_id: int
    ) -> List[Pattern]:
        """Detecta concentração anormal de ativos"""
        from sqlalchemy import select
        from app.domain.property import Property
        
        patterns = []
        
        query = select(Property).where(
            Property.investigation_id == investigation_id
        )
        result = await db.execute(query)
        properties = list(result.scalars().all())
        
        if len(properties) < 5:
            return patterns
        
        # 1. Concentração geográfica anormal
        # Agrupar por cidade
        city_groups = {}
        for prop in properties:
            if prop.city and prop.state:
                city_key = f"{prop.city}/{prop.state}"
                if city_key not in city_groups:
                    city_groups[city_key] = []
                city_groups[city_key].append(prop)
        
        # Detectar cidades com muitas propriedades
        for city, props in city_groups.items():
            if len(props) >= 15:
                total_area = sum(p.area_hectares or 0 for p in props)
                patterns.append(Pattern(
                    type='abnormal_concentration_geographic',
                    confidence=0.70,
                    description=f'{len(props)} propriedades concentradas em {city}',
                    entities=[p.id for p in props],
                    severity='medium',
                    evidence={
                        'city': city,
                        'num_properties': len(props),
                        'total_area': total_area
                    }
                ))
        
        # 2. Propriedades muito grandes (outliers)
        areas = [p.area_hectares for p in properties if p.area_hectares]
        if len(areas) >= 5:
            mean_area = np.mean(areas)
            std_area = np.std(areas)
            
            outliers = [
                p for p in properties
                if p.area_hectares and p.area_hectares > mean_area + 3 * std_area
            ]
            
            if outliers:
                patterns.append(Pattern(
                    type='abnormal_concentration_size',
                    confidence=0.65,
                    description=f'{len(outliers)} propriedades com área muito acima da média',
                    entities=[p.id for p in outliers],
                    severity='medium',
                    evidence={
                        'num_outliers': len(outliers),
                        'mean_area': mean_area,
                        'outlier_areas': [p.area_hectares for p in outliers]
                    }
                ))
        
        return patterns
    
    @classmethod
    async def _detect_temporal_anomalies(
        cls, db, investigation_id: int
    ) -> List[Pattern]:
        """Detecta anomalias temporais"""
        from sqlalchemy import select
        from app.domain.company import Company
        from datetime import timedelta
        
        patterns = []
        
        # Empresas criadas em fins de semana (suspeito)
        query = select(Company).where(
            Company.investigation_id == investigation_id,
            Company.opening_date.isnot(None)
        )
        result = await db.execute(query)
        companies = list(result.scalars().all())
        
        weekend_companies = [
            c for c in companies
            if c.opening_date and c.opening_date.weekday() >= 5  # Sábado/Domingo
        ]
        
        if len(weekend_companies) >= 5:
            patterns.append(Pattern(
                type='temporal_anomaly_weekend',
                confidence=0.60,
                description=f'{len(weekend_companies)} empresas abertas em fins de semana',
                entities=[c.id for c in weekend_companies],
                severity='low',
                evidence={
                    'num_companies': len(weekend_companies),
                    'companies': [c.corporate_name for c in weekend_companies[:5]]
                }
            ))
        
        # Empresas abertas no mesmo dia
        date_groups = {}
        for c in companies:
            if c.opening_date:
                date_key = c.opening_date.date()
                if date_key not in date_groups:
                    date_groups[date_key] = []
                date_groups[date_key].append(c)
        
        for date, comps in date_groups.items():
            if len(comps) >= 5:
                patterns.append(Pattern(
                    type='temporal_anomaly_same_day',
                    confidence=0.75,
                    description=f'{len(comps)} empresas abertas no mesmo dia',
                    entities=[c.id for c in comps],
                    severity='medium',
                    evidence={
                        'date': date.isoformat(),
                        'num_companies': len(comps),
                        'companies': [c.corporate_name for c in comps]
                    }
                ))
        
        return patterns
