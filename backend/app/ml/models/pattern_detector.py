"""
Pattern Detector - Detecção de Padrões Suspeitos

Este módulo utiliza machine learning e regras heurísticas para detectar
padrões suspeitos em investigações patrimoniais rurais.

Padrões detectados:
- Grilagem de terras
- Lavagem de dinheiro via propriedades rurais
- Esquemas de "laranjas" (testas de ferro)
- Arrendamentos circulares
- Propriedades "fantasma"
- Estruturas societárias complexas
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict, Counter
import re
import logging

from app.domain.investigation import Investigation
from app.domain.property import Property
from app.domain.company import Company
from app.domain.lease_contract import LeaseContract

logger = logging.getLogger(__name__)


class Pattern:
    """Representa um padrão suspeito detectado"""
    
    def __init__(
        self,
        pattern_type: str,
        confidence: float,
        description: str,
        evidence: List[str],
        severity: str,
        entities_involved: List[str]
    ):
        self.pattern_type = pattern_type
        self.confidence = confidence  # 0.0 - 1.0
        self.description = description
        self.evidence = evidence
        self.severity = severity  # low, medium, high, critical
        self.entities_involved = entities_involved
        self.detected_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "pattern_type": self.pattern_type,
            "confidence": round(self.confidence, 3),
            "confidence_percentage": round(self.confidence * 100, 1),
            "description": self.description,
            "evidence": self.evidence,
            "severity": self.severity,
            "entities_involved": self.entities_involved,
            "detected_at": self.detected_at.isoformat()
        }


class PatternDetectionResult:
    """Resultado da detecção de padrões"""
    
    def __init__(
        self,
        investigation_id: int,
        patterns: List[Pattern],
        analyzed_at: datetime
    ):
        self.investigation_id = investigation_id
        self.patterns = patterns
        self.analyzed_at = analyzed_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "investigation_id": self.investigation_id,
            "patterns_detected": len(self.patterns),
            "patterns": [p.to_dict() for p in self.patterns],
            "analyzed_at": self.analyzed_at.isoformat(),
            "has_critical_patterns": any(p.severity == "critical" for p in self.patterns),
            "has_high_patterns": any(p.severity == "high" for p in self.patterns),
            "severity_summary": {
                "critical": sum(1 for p in self.patterns if p.severity == "critical"),
                "high": sum(1 for p in self.patterns if p.severity == "high"),
                "medium": sum(1 for p in self.patterns if p.severity == "medium"),
                "low": sum(1 for p in self.patterns if p.severity == "low")
            }
        }


class PatternDetector:
    """
    Detector de Padrões Suspeitos
    
    Utiliza regras heurísticas e análise de dados para detectar:
    1. Grilagem de terras
    2. Lavagem de dinheiro
    3. Esquemas de laranjas
    4. Arrendamentos circulares
    5. Propriedades fantasma
    6. Estruturas societárias complexas
    7. Evasão fiscal
    8. Fraudes documentais
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect(self, investigation_id: int) -> PatternDetectionResult:
        """
        Detecta padrões suspeitos em uma investigação
        
        Args:
            investigation_id: ID da investigação
            
        Returns:
            PatternDetectionResult com padrões detectados
        """
        logger.info(f"Iniciando detecção de padrões para investigação {investigation_id}")
        
        # Buscar investigação
        investigation = self.db.query(Investigation).filter(
            Investigation.id == investigation_id
        ).first()
        
        if not investigation:
            raise ValueError(f"Investigação {investigation_id} não encontrada")
        
        # Detectar cada tipo de padrão
        patterns: List[Pattern] = []
        
        patterns.extend(self._detect_land_grabbing(investigation))
        patterns.extend(self._detect_money_laundering(investigation))
        patterns.extend(self._detect_shell_scheme(investigation))
        patterns.extend(self._detect_circular_leases(investigation))
        patterns.extend(self._detect_ghost_properties(investigation))
        patterns.extend(self._detect_complex_structures(investigation))
        patterns.extend(self._detect_tax_evasion(investigation))
        patterns.extend(self._detect_document_fraud(investigation))
        
        result = PatternDetectionResult(
            investigation_id=investigation_id,
            patterns=patterns,
            analyzed_at=datetime.utcnow()
        )
        
        logger.info(
            f"Detecção concluída: {len(patterns)} padrões detectados "
            f"({sum(1 for p in patterns if p.severity == 'critical')} críticos)"
        )
        
        return result
    
    def _detect_land_grabbing(self, investigation: Investigation) -> List[Pattern]:
        """
        Detecta indícios de grilagem de terras
        
        Sinais:
        - Propriedades muito grandes sem documentação adequada
        - Propriedades em áreas públicas ou terras indígenas
        - Documentos de propriedade recentes para terras antigas
        - Sobreposição de matrículas
        """
        patterns = []
        properties = investigation.properties or []
        
        for prop in properties:
            prop_data = prop.additional_data or {}
            evidence = []
            confidence = 0.0
            
            # 1. Propriedade muito grande sem CAR ou matrícula
            area = float(prop_data.get("area_hectares", 0) or 0)
            has_car = bool(prop_data.get("car_code"))
            has_matricula = bool(prop_data.get("matricula"))
            
            if area > 1000 and not (has_car or has_matricula):
                confidence += 0.4
                evidence.append(
                    f"Propriedade de {area:.1f} ha sem CAR ou matrícula"
                )
            
            # 2. Propriedade em área pública ou indígena
            if prop_data.get("in_public_land") or prop_data.get("in_indigenous_land"):
                confidence += 0.5
                evidence.append("Propriedade em terra pública ou indígena")
            
            # 3. Documento recente para terra antiga
            doc_date = prop_data.get("document_date")
            if doc_date and area > 500:
                # Se documento tem menos de 5 anos mas terra é grande (suspeito)
                if isinstance(doc_date, str):
                    try:
                        doc_date = datetime.fromisoformat(doc_date)
                    except:
                        doc_date = None
                
                if doc_date and (datetime.utcnow() - doc_date).days < 1825:  # 5 anos
                    confidence += 0.3
                    evidence.append(
                        f"Documento recente ({doc_date.year}) para propriedade grande"
                    )
            
            # 4. Propriedade em área de preservação
            if prop_data.get("in_protected_area"):
                confidence += 0.4
                evidence.append("Propriedade em área de preservação ambiental")
            
            if confidence > 0.5 and evidence:
                severity = "critical" if confidence > 0.8 else "high"
                patterns.append(Pattern(
                    pattern_type="land_grabbing",
                    confidence=min(confidence, 1.0),
                    description="Possível grilagem de terras detectada",
                    evidence=evidence,
                    severity=severity,
                    entities_involved=[prop.name or prop.address or "Propriedade"]
                ))
        
        return patterns
    
    def _detect_money_laundering(self, investigation: Investigation) -> List[Pattern]:
        """
        Detecta indícios de lavagem de dinheiro
        
        Sinais:
        - Compras e vendas rápidas (flipping)
        - Valores incompatíveis com perfil do proprietário
        - Empresas offshore envolvidas
        - Pagamentos em espécie para grandes valores
        """
        patterns = []
        evidence = []
        confidence = 0.0
        entities = []
        
        companies = investigation.companies or []
        properties = investigation.properties or []
        
        # 1. Empresas offshore
        offshore_count = 0
        for company in companies:
            company_data = company.additional_data or {}
            country = company_data.get("country", "Brasil")
            
            tax_havens = [
                "cayman", "virgens", "panama", "bahamas", "bermuda",
                "luxemburgo", "suiça", "liechtenstein", "monaco"
            ]
            
            if any(haven in country.lower() for haven in tax_havens):
                offshore_count += 1
                entities.append(company.name)
        
        if offshore_count > 0:
            confidence += 0.4 + (offshore_count * 0.1)
            evidence.append(
                f"{offshore_count} empresa(s) offshore envolvida(s)"
            )
        
        # 2. Múltiplas transações recentes
        recent_transactions = 0
        for prop in properties:
            prop_data = prop.additional_data or {}
            last_transaction = prop_data.get("last_transaction_date")
            
            if last_transaction:
                if isinstance(last_transaction, str):
                    try:
                        last_transaction = datetime.fromisoformat(last_transaction)
                    except:
                        last_transaction = None
                
                if last_transaction:
                    days_ago = (datetime.utcnow() - last_transaction).days
                    if days_ago < 180:  # 6 meses
                        recent_transactions += 1
        
        if recent_transactions >= 3:
            confidence += 0.3
            evidence.append(
                f"{recent_transactions} propriedades com transações nos últimos 6 meses"
            )
        
        # 3. Valores muito altos
        total_value = sum(
            float(p.additional_data.get("estimated_value", 0) or 0)
            for p in properties
        )
        
        if total_value > 10_000_000:  # 10 milhões
            confidence += 0.2
            evidence.append(
                f"Valor total estimado: R$ {total_value:,.2f}"
            )
        
        # 4. Estrutura societária complexa (múltiplas camadas)
        if len(companies) >= 5:
            confidence += 0.25
            evidence.append(
                f"Estrutura societária complexa ({len(companies)} empresas)"
            )
        
        if confidence > 0.6 and evidence:
            severity = "critical" if confidence > 0.85 else "high"
            patterns.append(Pattern(
                pattern_type="money_laundering",
                confidence=min(confidence, 1.0),
                description="Possível esquema de lavagem de dinheiro detectado",
                evidence=evidence,
                severity=severity,
                entities_involved=entities or ["Múltiplas entidades"]
            ))
        
        return patterns
    
    def _detect_shell_scheme(self, investigation: Investigation) -> List[Pattern]:
        """
        Detecta esquema de laranjas (testas de ferro)
        
        Sinais:
        - Múltiplas pessoas com baixo perfil econômico como proprietárias
        - Mesmos endereços/telefones para diferentes proprietários
        - Padrões de nomes (ex: todos parentes, nomes similares)
        - CPFs sequenciais ou padrão suspeito
        """
        patterns = []
        evidence = []
        confidence = 0.0
        entities = []
        
        properties = investigation.properties or []
        
        # Coletar CPFs e informações dos proprietários
        owners_info = []
        for prop in properties:
            prop_data = prop.additional_data or {}
            owner_cpf = prop_data.get("owner_cpf")
            owner_name = prop_data.get("owner_name")
            owner_phone = prop_data.get("owner_phone")
            owner_address = prop_data.get("owner_address")
            
            if owner_cpf:
                owners_info.append({
                    "cpf": owner_cpf,
                    "name": owner_name,
                    "phone": owner_phone,
                    "address": owner_address
                })
        
        if len(owners_info) < 3:
            return patterns  # Precisa de pelo menos 3 para detectar padrão
        
        # 1. Verificar telefones duplicados
        phones = [o["phone"] for o in owners_info if o.get("phone")]
        phone_counts = Counter(phones)
        duplicate_phones = sum(1 for count in phone_counts.values() if count > 1)
        
        if duplicate_phones > 0:
            confidence += 0.3
            evidence.append(
                f"{duplicate_phones} proprietários compartilham telefones"
            )
        
        # 2. Verificar endereços duplicados
        addresses = [o["address"] for o in owners_info if o.get("address")]
        address_counts = Counter(addresses)
        duplicate_addresses = sum(1 for count in address_counts.values() if count > 1)
        
        if duplicate_addresses > 0:
            confidence += 0.3
            evidence.append(
                f"{duplicate_addresses} proprietários compartilham endereços"
            )
        
        # 3. Verificar nomes similares (possíveis parentes)
        names = [o["name"] for o in owners_info if o.get("name")]
        surnames = [" ".join(name.split()[1:]) for name in names if name and len(name.split()) > 1]
        surname_counts = Counter(surnames)
        common_surnames = sum(1 for count in surname_counts.values() if count >= 3)
        
        if common_surnames > 0:
            confidence += 0.2
            evidence.append(
                f"{common_surnames} sobrenomes compartilhados (possível família)"
            )
        
        # 4. CPFs com padrão sequencial (muito suspeito)
        cpfs = [o["cpf"] for o in owners_info if o.get("cpf")]
        if len(cpfs) >= 3:
            # Extrair números dos CPFs (remover formatação)
            cpf_numbers = []
            for cpf in cpfs:
                numbers = re.sub(r'\D', '', cpf)
                if len(numbers) == 11:
                    cpf_numbers.append(int(numbers[:9]))  # Primeiros 9 dígitos
            
            if len(cpf_numbers) >= 3:
                cpf_numbers.sort()
                # Verificar se há CPFs muito próximos (diferença < 100)
                sequential = 0
                for i in range(len(cpf_numbers) - 1):
                    if cpf_numbers[i+1] - cpf_numbers[i] < 100:
                        sequential += 1
                
                if sequential >= 2:
                    confidence += 0.5
                    evidence.append(
                        f"{sequential} CPFs sequenciais ou muito próximos (ALTAMENTE SUSPEITO)"
                    )
                    entities.extend([o["name"] for o in owners_info if o.get("name")])
        
        # 5. Muitos proprietários para poucas propriedades
        if len(owners_info) >= len(properties) * 1.5:
            confidence += 0.2
            evidence.append(
                f"{len(owners_info)} proprietários para {len(properties)} propriedades"
            )
        
        if confidence > 0.5 and evidence:
            severity = "critical" if confidence > 0.8 else "high"
            patterns.append(Pattern(
                pattern_type="shell_scheme",
                confidence=min(confidence, 1.0),
                description="Possível esquema de 'laranjas' (testas de ferro) detectado",
                evidence=evidence,
                severity=severity,
                entities_involved=entities[:5] if entities else ["Múltiplos proprietários"]
            ))
        
        return patterns
    
    def _detect_circular_leases(self, investigation: Investigation) -> List[Pattern]:
        """
        Detecta arrendamentos circulares (A arrenda para B, B para C, C para A)
        
        Sinal de possível fraude fiscal ou lavagem de dinheiro
        """
        patterns = []
        leases = investigation.lease_contracts or []
        
        if len(leases) < 2:
            return patterns
        
        # Mapear arrendamentos (lessor -> lessee)
        lease_graph = defaultdict(list)
        entities = set()
        
        for lease in leases:
            lessor = lease.lessor_name or "Unknown"
            lessee = lease.lessee_name or "Unknown"
            lease_graph[lessor].append(lessee)
            entities.add(lessor)
            entities.add(lessee)
        
        # Detectar ciclos
        cycles_found = []
        
        def find_cycle(node, path, visited):
            """DFS para encontrar ciclos"""
            if node in path:
                # Ciclo encontrado
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                return cycle
            
            if node in visited:
                return None
            
            visited.add(node)
            path.append(node)
            
            for neighbor in lease_graph.get(node, []):
                result = find_cycle(neighbor, path.copy(), visited.copy())
                if result:
                    return result
            
            return None
        
        for start_node in lease_graph.keys():
            cycle = find_cycle(start_node, [], set())
            if cycle and len(cycle) >= 2:
                cycle_str = " → ".join(cycle + [cycle[0]])
                if cycle_str not in cycles_found:
                    cycles_found.append(cycle_str)
        
        if cycles_found:
            confidence = 0.7 + (len(cycles_found) * 0.1)
            evidence = [f"Ciclo de arrendamento detectado: {cycle}" for cycle in cycles_found]
            
            patterns.append(Pattern(
                pattern_type="circular_leases",
                confidence=min(confidence, 1.0),
                description="Arrendamento circular detectado (possível fraude)",
                evidence=evidence,
                severity="critical",
                entities_involved=list(entities)[:10]
            ))
        
        return patterns
    
    def _detect_ghost_properties(self, investigation: Investigation) -> List[Pattern]:
        """
        Detecta propriedades "fantasma" (existem no papel mas não na prática)
        
        Sinais:
        - Sem geolocalização
        - Sem CAR ou matrícula
        - Dados incompletos
        - Área declarada incompatível com região
        """
        patterns = []
        properties = investigation.properties or []
        
        ghost_properties = []
        
        for prop in properties:
            prop_data = prop.additional_data or {}
            red_flags = []
            
            # 1. Sem localização
            has_location = (
                prop_data.get("latitude") and prop_data.get("longitude")
            ) or prop_data.get("coordinates")
            
            if not has_location:
                red_flags.append("sem geolocalização")
            
            # 2. Sem documentação
            has_car = bool(prop_data.get("car_code"))
            has_matricula = bool(prop_data.get("matricula"))
            has_ccir = bool(prop_data.get("ccir"))
            
            if not (has_car or has_matricula or has_ccir):
                red_flags.append("sem documentação (CAR/matrícula/CCIR)")
            
            # 3. Dados muito incompletos
            essential_fields = ["area_hectares", "municipality", "state"]
            missing_fields = [
                field for field in essential_fields
                if not prop_data.get(field)
            ]
            
            if len(missing_fields) >= 2:
                red_flags.append(f"dados incompletos ({len(missing_fields)} campos essenciais faltando)")
            
            # 4. Endereço genérico ou inválido
            address = prop.address or ""
            if not address or len(address) < 10 or address.lower() in ["n/a", "não informado", "sem endereço"]:
                red_flags.append("endereço ausente ou inválido")
            
            if len(red_flags) >= 3:
                ghost_properties.append({
                    "name": prop.name or prop.address or "Propriedade",
                    "red_flags": red_flags
                })
        
        if ghost_properties:
            confidence = 0.5 + (len(ghost_properties) * 0.1)
            evidence = [
                f"{p['name']}: {', '.join(p['red_flags'])}"
                for p in ghost_properties
            ]
            
            patterns.append(Pattern(
                pattern_type="ghost_properties",
                confidence=min(confidence, 1.0),
                description=f"{len(ghost_properties)} propriedade(s) 'fantasma' detectada(s)",
                evidence=evidence,
                severity="high",
                entities_involved=[p["name"] for p in ghost_properties]
            ))
        
        return patterns
    
    def _detect_complex_structures(self, investigation: Investigation) -> List[Pattern]:
        """
        Detecta estruturas societárias excessivamente complexas
        
        Pode indicar tentativa de ocultar beneficiário final
        """
        patterns = []
        companies = investigation.companies or []
        
        if len(companies) < 3:
            return patterns
        
        evidence = []
        confidence = 0.0
        
        # 1. Muitas empresas
        if len(companies) >= 5:
            confidence += 0.3
            evidence.append(f"{len(companies)} empresas envolvidas")
        
        # 2. Empresas com múltiplas camadas
        layers_count = 0
        for company in companies:
            company_data = company.additional_data or {}
            partners = company_data.get("partners", [])
            
            # Verificar se algum sócio é PJ
            pj_partners = sum(1 for p in partners if p.get("cnpj"))
            if pj_partners > 0:
                layers_count += 1
        
        if layers_count >= 3:
            confidence += 0.4
            evidence.append(
                f"{layers_count} empresas com sócios PJ (estrutura em camadas)"
            )
        
        # 3. Empresas offshore
        offshore_count = sum(
            1 for c in companies
            if "offshore" in (c.additional_data or {}).get("type", "").lower()
        )
        
        if offshore_count > 0:
            confidence += 0.3
            evidence.append(f"{offshore_count} empresa(s) offshore")
        
        if confidence > 0.6 and evidence:
            patterns.append(Pattern(
                pattern_type="complex_structures",
                confidence=min(confidence, 1.0),
                description="Estrutura societária excessivamente complexa",
                evidence=evidence,
                severity="high",
                entities_involved=[c.name for c in companies[:5]]
            ))
        
        return patterns
    
    def _detect_tax_evasion(self, investigation: Investigation) -> List[Pattern]:
        """
        Detecta indícios de evasão fiscal
        
        Sinais:
        - Empresas inativas mas com propriedades
        - Valores declarados muito baixos
        - Empresas em regimes especiais de tributação com movimentação alta
        """
        patterns = []
        evidence = []
        confidence = 0.0
        entities = []
        
        companies = investigation.companies or []
        properties = investigation.properties or []
        
        # 1. Empresas inativas com propriedades
        inactive_with_properties = 0
        for company in companies:
            company_data = company.additional_data or {}
            status = company_data.get("status", "").lower()
            
            if "inativa" in status or "baixada" in status or "suspensa" in status:
                # Verificar se tem propriedades
                company_properties = [
                    p for p in properties
                    if company.cnpj in str(p.additional_data)
                ]
                
                if company_properties:
                    inactive_with_properties += 1
                    entities.append(company.name)
        
        if inactive_with_properties > 0:
            confidence += 0.5
            evidence.append(
                f"{inactive_with_properties} empresa(s) inativa(s) com propriedades"
            )
        
        # 2. Valores declarados muito baixos
        low_value_properties = 0
        for prop in properties:
            prop_data = prop.additional_data or {}
            area = float(prop_data.get("area_hectares", 0) or 0)
            value = float(prop_data.get("estimated_value", 0) or 0)
            
            # Se propriedade grande (>100ha) com valor muito baixo (<100k)
            if area > 100 and value > 0 and value < 100_000:
                low_value_properties += 1
        
        if low_value_properties >= 2:
            confidence += 0.3
            evidence.append(
                f"{low_value_properties} propriedades com valor declarado muito baixo"
            )
        
        # 3. Empresas Simples Nacional com movimentação alta
        simples_suspeito = 0
        for company in companies:
            company_data = company.additional_data or {}
            regime = company_data.get("tax_regime", "").lower()
            capital = float(company_data.get("capital_social", 0) or 0)
            
            if "simples" in regime and capital > 5_000_000:
                simples_suspeito += 1
                entities.append(company.name)
        
        if simples_suspeito > 0:
            confidence += 0.4
            evidence.append(
                f"{simples_suspeito} empresa(s) no Simples com capital social alto"
            )
        
        if confidence > 0.5 and evidence:
            patterns.append(Pattern(
                pattern_type="tax_evasion",
                confidence=min(confidence, 1.0),
                description="Possíveis indícios de evasão fiscal",
                evidence=evidence,
                severity="high",
                entities_involved=entities
            ))
        
        return patterns
    
    def _detect_document_fraud(self, investigation: Investigation) -> List[Pattern]:
        """
        Detecta possíveis fraudes documentais
        
        Sinais:
        - Datas inconsistentes
        - Documentos duplicados
        - Números de documento inválidos
        """
        patterns = []
        evidence = []
        confidence = 0.0
        entities = []
        
        properties = investigation.properties or []
        leases = investigation.lease_contracts or []
        
        # 1. Matrículas duplicadas
        matriculas = [
            p.additional_data.get("matricula")
            for p in properties
            if p.additional_data and p.additional_data.get("matricula")
        ]
        
        if len(matriculas) != len(set(matriculas)):
            duplicates = len(matriculas) - len(set(matriculas))
            confidence += 0.6
            evidence.append(f"{duplicates} matrícula(s) duplicada(s)")
        
        # 2. CARs duplicados
        cars = [
            p.additional_data.get("car_code")
            for p in properties
            if p.additional_data and p.additional_data.get("car_code")
        ]
        
        if len(cars) != len(set(cars)):
            duplicates = len(cars) - len(set(cars))
            confidence += 0.6
            evidence.append(f"{duplicates} código(s) CAR duplicado(s)")
        
        # 3. Datas inconsistentes em contratos
        for lease in leases:
            if lease.start_date and lease.end_date:
                if lease.end_date < lease.start_date:
                    confidence += 0.5
                    evidence.append(
                        f"Contrato com data de fim antes da data de início"
                    )
                    entities.append(f"Contrato {lease.document_number or 'sem número'}")
        
        # 4. Documentos com números inválidos ou suspeitos
        for lease in leases:
            doc_num = lease.document_number
            if doc_num:
                # Verificar padrões suspeitos
                if doc_num in ["00000", "11111", "12345", "99999"]:
                    confidence += 0.4
                    evidence.append(
                        f"Número de documento suspeito: {doc_num}"
                    )
        
        if confidence > 0.5 and evidence:
            patterns.append(Pattern(
                pattern_type="document_fraud",
                confidence=min(confidence, 1.0),
                description="Possíveis irregularidades documentais detectadas",
                evidence=evidence,
                severity="critical",
                entities_involved=entities
            ))
        
        return patterns
