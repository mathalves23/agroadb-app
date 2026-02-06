"""
Receita Federal Scraper

Integração com múltiplas APIs públicas para consulta de CNPJ:
- BrasilAPI (primária)
- ReceitaWS (fallback 1)
- CNPJá (fallback 2)
- API Oficial RFB (fallback 3)
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import re
from enum import Enum

from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class APIProvider(Enum):
    """Provedores de API disponíveis"""
    BRASILAPI = "BrasilAPI"
    RECEITAWS = "ReceitaWS"
    CNPJA = "CNPJá"
    RFB_OFICIAL = "RFB Oficial"


class ReceitaScraper(BaseScraper):
    """
    Scraper para dados da Receita Federal
    
    Utiliza múltiplas APIs públicas com sistema de fallback:
    1. BrasilAPI (rápida e confiável)
    2. ReceitaWS (boa cobertura)
    3. CNPJá (5 req/min gratuita)
    4. API Oficial RFB (dados oficiais)
    
    Funcionalidades:
    - Busca de dados cadastrais completos
    - Extração de estrutura societária (QSA)
    - Análise de CNPJs relacionados
    - Sistema de cache e fallback
    """
    
    def __init__(self):
        super().__init__()
        
        # APIs disponíveis (ordem de prioridade)
        self.apis = {
            APIProvider.BRASILAPI: {
                "url": "https://brasilapi.com.br/api/cnpj/v1",
                "timeout": 10,
                "rate_limit": None,  # Sem limite conhecido
            },
            APIProvider.RECEITAWS: {
                "url": "https://www.receitaws.com.br/v1/cnpj",
                "timeout": 15,
                "rate_limit": 3,  # 3 por minuto
            },
            APIProvider.CNPJA: {
                "url": "https://publica.cnpj.ws/cnpj",
                "timeout": 10,
                "rate_limit": 5,  # 5 por minuto
            },
            APIProvider.RFB_OFICIAL: {
                "url": "https://servicos.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Solicitacao.asp",
                "timeout": 20,
                "rate_limit": None,
            },
        }
        
        # Cache de resultados
        self.cache: Dict[str, Tuple[datetime, Dict[str, Any]]] = {}
        self.cache_ttl = timedelta(hours=48)  # Cache de 48h para dados da Receita
        
        # Controle de rate limiting
        self.last_request: Dict[APIProvider, datetime] = {}
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Busca resultado do cache se ainda válido"""
        if key in self.cache:
            timestamp, data = self.cache[key]
            if datetime.now() - timestamp < self.cache_ttl:
                return data
        return None
    
    def _save_to_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Salva resultado no cache"""
        self.cache[key] = (datetime.now(), data)
    
    def _clean_cnpj(self, cnpj: str) -> str:
        """Remove formatação do CNPJ"""
        return re.sub(r'[^\d]', '', cnpj)
    
    def _format_cnpj(self, cnpj: str) -> str:
        """Formata CNPJ (12.345.678/0001-90)"""
        cnpj_clean = self._clean_cnpj(cnpj)
        if len(cnpj_clean) == 14:
            return f"{cnpj_clean[:2]}.{cnpj_clean[2:5]}.{cnpj_clean[5:8]}/{cnpj_clean[8:12]}-{cnpj_clean[12:]}"
        return cnpj
    
    def _validate_cnpj(self, cnpj: str) -> bool:
        """Valida formato do CNPJ"""
        cnpj_clean = self._clean_cnpj(cnpj)
        return len(cnpj_clean) == 14 and cnpj_clean.isdigit()
    
    def _can_make_request(self, provider: APIProvider) -> bool:
        """Verifica se pode fazer requisição respeitando rate limit"""
        api_config = self.apis[provider]
        rate_limit = api_config.get("rate_limit")
        
        if not rate_limit:
            return True
        
        if provider not in self.last_request:
            return True
        
        elapsed = (datetime.now() - self.last_request[provider]).total_seconds()
        min_interval = 60 / rate_limit  # Intervalo mínimo entre requisições
        
        return elapsed >= min_interval
    
    def _mark_request(self, provider: APIProvider) -> None:
        """Marca o tempo da última requisição"""
        self.last_request[provider] = datetime.now()
    
    async def search(self, cnpj: str) -> List[Dict[str, Any]]:
        """
        Busca dados de empresa por CNPJ com fallback automático
        
        Args:
            cnpj: CNPJ da empresa (com ou sem formatação)
        
        Returns:
            Lista com dados da empresa encontrada
        """
        results = []
        
        # Validar CNPJ
        if not self._validate_cnpj(cnpj):
            logger.warning(f"CNPJ inválido: {cnpj}")
            return results
        
        cnpj_clean = self._clean_cnpj(cnpj)
        
        # Verificar cache
        cached = self._get_from_cache(cnpj_clean)
        if cached:
            return [cached]
        
        # Tentar cada API em ordem de prioridade
        for provider in APIProvider:
            try:
                if not self._can_make_request(provider):
                    continue
                
                data = await self._fetch_from_provider(provider, cnpj_clean)
                
                if data:
                    self._mark_request(provider)
                    
                    # Processar dados
                    processed = self._process_company_data(data, provider)
                    
                    # Salvar no cache
                    self._save_to_cache(cnpj_clean, processed)
                    
                    results.append(processed)
                    break
            
            except Exception as e:
                logger.error(f"Error with {provider.value}: {str(e)}")
                continue

        # Fallback: tentar scraping da página pública da Receita (pode exigir captcha)
        if not results:
            try:
                html_data = await self._fetch_html_fallback(cnpj_clean)
                if html_data:
                    processed = self._process_company_data(html_data, APIProvider.RFB_OFICIAL)
                    self._save_to_cache(cnpj_clean, processed)
                    results.append(processed)
            except Exception as e:
                logger.error(f"Error in Receita HTML fallback: {str(e)}")
        
        return results
    
    async def _fetch_from_provider(
        self,
        provider: APIProvider,
        cnpj: str
    ) -> Optional[Dict[str, Any]]:
        """
        Busca dados de uma API específica
        
        Args:
            provider: Provedor da API
            cnpj: CNPJ limpo (apenas números)
        
        Returns:
            Dados brutos da API ou None se falhar
        """
        api_config = self.apis[provider]
        url = api_config["url"]
        timeout = api_config["timeout"]
        
        try:
            if provider == APIProvider.BRASILAPI:
                response = await self.fetch(f"{url}/{cnpj}", timeout=timeout)
            elif provider == APIProvider.RECEITAWS:
                response = await self.fetch(f"{url}/{cnpj}", timeout=timeout)
            elif provider == APIProvider.CNPJA:
                response = await self.fetch(f"{url}/{cnpj}", timeout=timeout)
            elif provider == APIProvider.RFB_OFICIAL:
                # API oficial pode ter formato diferente
                response = await self.fetch(
                    url,
                    params={"cnpj": cnpj},
                    timeout=timeout
                )
            else:
                return None
            
            if response and response.status_code == 200:
                return response.json()
        
        except Exception as e:
            logger.error(f"Error fetching from {provider.value}: {str(e)}")
        
        return None

    async def _fetch_html_fallback(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Fallback: tenta obter dados do CNPJ via página pública da Receita (HTML).
        Muitas páginas exigem captcha; este método tenta a requisição e extrai o que for possível.
        """
        try:
            # Página de consulta CNPJ Receita (pode redirecionar para solucao.receita ou exibir captcha)
            url = "https://solucao.receita.fazenda.gov.br/Solucao/servico/servicos/cnpj/consulta-publica"
            response = await self.fetch(url)
            if not response or response.status_code != 200:
                return None
            text = response.text
            if "captcha" in text.lower() or "captcha" in response.url.lower():
                return None
            soup = self.parse_html(text)
            # Extrair tabelas ou divs com dados cadastrais (estrutura varia por página)
            data = {"cnpj": cnpj}
            for label, key in [
                ("Razão Social", "razao_social"),
                ("Nome Fantasia", "nome_fantasia"),
                ("Situação Cadastral", "descricao_situacao_cadastral"),
                ("Município", "municipio"),
                ("UF", "uf"),
                ("CNAE", "cnae_fiscal"),
            ]:
                elem = soup.find(string=re.compile(label, re.I))
                if elem and elem.parent:
                    next_ = elem.parent.find_next(["td", "span", "div"])
                    if next_:
                        data[key] = next_.get_text(strip=True)
            if len(data) > 1:
                data["data_source_fallback"] = "receita_html_scraper"
                return data
        except Exception:
            pass
        return None
    
    def _process_company_data(
        self,
        data: Dict[str, Any],
        provider: APIProvider
    ) -> Dict[str, Any]:
        """
        Processa e padroniza dados da empresa
        
        Args:
            data: Dados brutos da API
            provider: Provedor que retornou os dados
        
        Returns:
            Dados processados e padronizados
        """
        # Campos comuns entre APIs
        cnpj = data.get("cnpj")
        
        # Extrair estrutura societária
        partners = self._extract_partners(data, provider)
        
        # Extrair CNPJs relacionados
        related_cnpjs = self._extract_related_cnpjs(data, partners)
        
        # Estruturar dados
        processed = {
            # Identificação
            "cnpj": self._format_cnpj(cnpj) if cnpj else None,
            "cnpj_clean": self._clean_cnpj(cnpj) if cnpj else None,
            "corporate_name": data.get("razao_social") or data.get("nome"),
            "trade_name": data.get("nome_fantasia") or data.get("fantasia"),
            
            # Situação Cadastral
            "status": data.get("descricao_situacao_cadastral") or data.get("situacao"),
            "status_date": data.get("data_situacao_cadastral") or data.get("data_situacao"),
            "status_reason": data.get("motivo_situacao_cadastral"),
            
            # Localização
            "address": self._format_address(data),
            "neighborhood": data.get("bairro"),
            "city": data.get("municipio"),
            "state": data.get("uf"),
            "zip_code": data.get("cep"),
            "country": data.get("pais") or "Brasil",
            
            # Contato
            "phone": data.get("ddd_telefone_1") or data.get("telefone"),
            "email": data.get("email"),
            
            # Atividade Econômica
            "main_activity": {
                "code": data.get("cnae_fiscal"),
                "description": data.get("cnae_fiscal_descricao"),
            },
            "secondary_activities": self._extract_secondary_activities(data),
            
            # Natureza Jurídica
            "legal_nature": {
                "code": data.get("codigo_natureza_juridica"),
                "description": data.get("natureza_juridica"),
            },
            
            # Porte
            "company_size": data.get("porte") or data.get("descricao_porte"),
            
            # Capital Social
            "capital": float(data.get("capital_social", 0) or 0),
            
            # Datas Importantes
            "opening_date": data.get("data_inicio_atividade") or data.get("abertura"),
            "registration_date": data.get("data_situacao_cadastral"),
            "last_update": data.get("ultima_atualizacao"),
            
            # Estrutura Societária (QSA)
            "partners": partners,
            "partners_count": len(partners),
            
            # CNPJs Relacionados
            "related_cnpjs": related_cnpjs,
            "related_count": len(related_cnpjs),
            
            # Indicadores
            "is_matriz": data.get("identificador_matriz_filial") == "1" or data.get("tipo") == "MATRIZ",
            "is_mei": data.get("opcao_pelo_mei") or False,
            "is_simples": data.get("opcao_pelo_simples") or False,
            
            # Metadados
            "data_source": f"Receita Federal via {provider.value}",
            "provider": provider.value,
            "consulted_at": datetime.now().isoformat(),
            "raw_data": data,
        }
        
        return processed
    
    def _format_address(self, data: Dict[str, Any]) -> str:
        """Formata endereço completo"""
        parts = []
        
        if logradouro := data.get("logradouro"):
            parts.append(logradouro)
        
        if numero := data.get("numero"):
            parts.append(numero)
        
        if complemento := data.get("complemento"):
            parts.append(complemento)
        
        return ", ".join(filter(None, parts)) if parts else ""
    
    def _extract_partners(
        self,
        data: Dict[str, Any],
        provider: APIProvider
    ) -> List[Dict[str, Any]]:
        """
        Extrai estrutura societária (QSA)
        
        Args:
            data: Dados brutos da API
            provider: Provedor da API
        
        Returns:
            Lista de sócios/administradores
        """
        partners = []
        qsa_data = data.get("qsa", []) or []
        
        for socio in qsa_data:
            partner = {
                "name": socio.get("nome_socio") or socio.get("nome"),
                "cpf_cnpj": self._clean_cpf_cnpj(
                    socio.get("cpf_cnpj_socio") or socio.get("documento") or ""
                ),
                "qualification": {
                    "code": socio.get("codigo_qualificacao_socio"),
                    "description": socio.get("qualificacao_socio") or socio.get("qualificacao"),
                },
                "entry_date": socio.get("data_entrada_sociedade"),
                "country": socio.get("pais_socio") or "Brasil",
                "legal_representative": socio.get("nome_representante_legal"),
                "representative_qualification": socio.get("qualificacao_representante_legal"),
                "age_range": socio.get("faixa_etaria"),
                "percentage": socio.get("percentual_capital_social"),
            }
            partners.append(partner)
        
        return partners
    
    def _clean_cpf_cnpj(self, doc: str) -> str:
        """Limpa CPF/CNPJ"""
        if not doc:
            return ""
        # Remove asteriscos (dados protegidos pela LGPD)
        doc = doc.replace("*", "")
        return re.sub(r'[^\d]', '', doc)
    
    def _extract_secondary_activities(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai atividades econômicas secundárias"""
        activities = []
        cnaes_secundarios = data.get("cnaes_secundarios", []) or []
        
        for cnae in cnaes_secundarios:
            activity = {
                "code": cnae.get("codigo"),
                "description": cnae.get("descricao"),
            }
            activities.append(activity)
        
        return activities
    
    def _extract_related_cnpjs(
        self,
        data: Dict[str, Any],
        partners: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analisa CNPJs relacionados através dos sócios
        
        Args:
            data: Dados brutos da empresa
            partners: Lista de sócios processados
        
        Returns:
            Lista de CNPJs potencialmente relacionados
        """
        related = []
        
        # CNPJs de sócios que são pessoas jurídicas
        for partner in partners:
            cpf_cnpj = partner.get("cpf_cnpj", "")
            if len(cpf_cnpj) == 14:  # É um CNPJ
                related.append({
                    "cnpj": self._format_cnpj(cpf_cnpj),
                    "cnpj_clean": cpf_cnpj,
                    "relationship": "Sócio PJ",
                    "partner_name": partner.get("name"),
                    "qualification": partner.get("qualification", {}).get("description"),
                })
        
        # Se for filial, adicionar matriz
        if data.get("identificador_matriz_filial") == "2":  # É filial
            cnpj_base = data.get("cnpj", "")[:8]  # Primeiros 8 dígitos
            if cnpj_base:
                matriz_cnpj = f"{cnpj_base}0001"  # Padrão da matriz
                related.append({
                    "cnpj": self._format_cnpj(matriz_cnpj + "00"),  # Adiciona DV genérico
                    "cnpj_clean": matriz_cnpj,
                    "relationship": "Matriz",
                    "partner_name": None,
                    "qualification": None,
                })
        
        return related
    
    async def get_full_corporate_structure(
        self,
        cnpj: str,
        depth: int = 2
    ) -> Dict[str, Any]:
        """
        Busca estrutura societária completa recursivamente
        
        Args:
            cnpj: CNPJ da empresa raiz
            depth: Profundidade da busca (níveis de recursão)
        
        Returns:
            Estrutura completa incluindo sócios e empresas relacionadas
        """
        if depth <= 0:
            return {}
        
        # Buscar dados da empresa principal
        company_data_list = await self.search(cnpj)
        
        if not company_data_list:
            return {}
        
        company_data = company_data_list[0]
        
        # Estrutura a ser retornada
        structure = {
            "company": company_data,
            "related_companies": [],
            "depth_level": depth,
        }
        
        # Buscar dados de CNPJs relacionados (próximo nível)
        related_cnpjs = company_data.get("related_cnpjs", [])
        
        for related in related_cnpjs:
            related_cnpj = related.get("cnpj_clean")
            if related_cnpj:
                related_structure = await self.get_full_corporate_structure(
                    related_cnpj,
                    depth - 1
                )
                if related_structure:
                    structure["related_companies"].append(related_structure)
        
        return structure
    
    async def analyze_corporate_network(self, cnpj: str) -> Dict[str, Any]:
        """
        Analisa rede corporativa e identifica grupos empresariais
        
        Args:
            cnpj: CNPJ da empresa para análise
        
        Returns:
            Análise da rede corporativa
        """
        # Buscar estrutura completa
        structure = await self.get_full_corporate_structure(cnpj, depth=2)
        
        if not structure:
            return {}
        
        # Análise
        all_cnpjs = set()
        all_partners = {}
        
        def extract_info(node: Dict[str, Any]) -> None:
            """Extrai informações recursivamente"""
            company = node.get("company", {})
            cnpj_clean = company.get("cnpj_clean")
            
            if cnpj_clean:
                all_cnpjs.add(cnpj_clean)
            
            # Extrair sócios
            for partner in company.get("partners", []):
                partner_doc = partner.get("cpf_cnpj")
                if partner_doc:
                    if partner_doc not in all_partners:
                        all_partners[partner_doc] = []
                    all_partners[partner_doc].append({
                        "cnpj": company.get("cnpj"),
                        "corporate_name": company.get("corporate_name"),
                        "qualification": partner.get("qualification", {}).get("description"),
                    })
            
            # Recursivamente processar empresas relacionadas
            for related in node.get("related_companies", []):
                extract_info(related)
        
        extract_info(structure)
        
        # Identificar sócios em comum
        common_partners = {
            doc: companies
            for doc, companies in all_partners.items()
            if len(companies) > 1
        }
        
        return {
            "root_cnpj": cnpj,
            "total_companies": len(all_cnpjs),
            "all_cnpjs": list(all_cnpjs),
            "total_partners": len(all_partners),
            "common_partners": common_partners,
            "common_partners_count": len(common_partners),
            "corporate_structure": structure,
            "analysis_date": datetime.now().isoformat(),
        }
    
    def clear_cache(self) -> None:
        """Limpa todo o cache de resultados"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_entries = len(self.cache)
        valid_entries = sum(
            1 for timestamp, _ in self.cache.values()
            if datetime.now() - timestamp < self.cache_ttl
        )
        
        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": total_entries - valid_entries,
            "ttl_hours": self.cache_ttl.total_seconds() / 3600,
        }
