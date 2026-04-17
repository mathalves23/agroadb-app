"""
INCRA (Instituto Nacional de Colonização e Reforma Agrária) Scraper

Integração com SNCR (Sistema Nacional de Cadastro Rural)
API Governamental: https://www.gov.br/conecta/catalogo/apis/sncr-sistema-nacional-de-cadastro-rural
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import re

from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class INCRAScraper(BaseScraper):
    """
    Scraper para dados do INCRA/SNCR
    
    Utiliza API oficial do SNCR (Sistema Nacional de Cadastro Rural):
    - Consulta de CCIR (Certificado de Cadastro de Imóvel Rural)
    - Busca de imóveis por CPF/CNPJ
    - Busca por código do imóvel
    - Consulta de situação cadastral
    """
    
    def __init__(self):
        super().__init__()
        # APIs oficiais do SNCR/INCRA
        self.sncr_api_base = "https://sncr.serpro.gov.br/api"
        self.ccir_emissao_url = "https://sncr.serpro.gov.br/ccir/emissao"
        self.ccir_consulta_url = "https://sncr.serpro.gov.br/ccir/consulta"
        
        # Cache de resultados (evitar requisições duplicadas)
        self.cache: Dict[str, tuple[datetime, List[Dict[str, Any]]]] = {}
        self.cache_ttl = timedelta(hours=24)  # Cache válido por 24 horas
    
    def _get_from_cache(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """Busca resultado do cache se ainda válido"""
        if key in self.cache:
            timestamp, data = self.cache[key]
            if datetime.now() - timestamp < self.cache_ttl:
                return data
        return None
    
    def _save_to_cache(self, key: str, data: List[Dict[str, Any]]) -> None:
        """Salva resultado no cache"""
        self.cache[key] = (datetime.now(), data)
    
    def _clean_cpf_cnpj(self, cpf_cnpj: str) -> str:
        """Remove formatação de CPF/CNPJ"""
        return re.sub(r'[^\d]', '', cpf_cnpj)
    
    def _format_ccir(self, ccir: str) -> str:
        """Formata número do CCIR"""
        # CCIR tem 13 dígitos
        ccir_clean = re.sub(r'[^\d]', '', ccir)
        if len(ccir_clean) == 13:
            return ccir_clean
        return ccir
    
    async def search(
        self, 
        name: Optional[str] = None, 
        cpf_cnpj: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca imóveis rurais no SNCR/INCRA
        
        Args:
            name: Nome do proprietário ou imóvel
            cpf_cnpj: CPF ou CNPJ do proprietário
            state: Sigla do estado (ex: SP, MG, GO)
            city: Nome do município
        
        Returns:
            Lista de imóveis encontrados com dados completos
        """
        results = []
        
        # Verificar cache
        cache_key = f"{name}_{cpf_cnpj}_{state}_{city}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Estratégia 1: Busca por CPF/CNPJ (mais preciso)
            if cpf_cnpj:
                results.extend(await self._search_by_cpf_cnpj(cpf_cnpj, state, city))
            
            # Estratégia 2: Busca por nome (se disponível na API)
            if name and not results:
                results.extend(await self._search_by_name(name, state, city))
            
            # Salvar no cache
            if results:
                self._save_to_cache(cache_key, results)
        
        except Exception as e:
            # Log error mas não falha a investigação toda
            logger.error(f"Error searching INCRA/SNCR: {str(e)}")
        
        return results
    
    async def _search_by_cpf_cnpj(
        self,
        cpf_cnpj: str,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca por CPF/CNPJ no SNCR
        
        Nota: A API do SNCR tem acesso restrito. Em produção,
        considerar usar serviços terceirizados ou parceria com órgãos públicos.
        """
        results = []
        
        # Limpar CPF/CNPJ
        cpf_cnpj_clean = self._clean_cpf_cnpj(cpf_cnpj)
        
        try:
            # Consulta à API pública (simulação - implementar com API real)
            # Em produção, usar API oficial do SNCR via Serpro
            
            # Por enquanto, retornar estrutura de exemplo com dados mockados
            # TODO: Implementar integração real com SNCR após obter credenciais
            
            # Estrutura esperada de retorno:
            property_data = {
                "ccir_number": f"{cpf_cnpj_clean[:8]}-2024",  # Formato: número-ano
                "property_code": f"{state or 'XX'}-{cpf_cnpj_clean[:10]}",  # Código de 13 dígitos
                "property_name": f"Imóvel Rural - {cpf_cnpj_clean[:8]}",
                "owner_name": "Nome a ser extraído da API",
                "owner_cpf_cnpj": cpf_cnpj_clean,
                
                # Localização
                "state": state or "Aguardando API",
                "city": city or "Município a ser extraído",
                "address": "Zona Rural, s/n",
                "coordinates": {
                    "latitude": 0.0,
                    "longitude": 0.0,
                },
                
                # Áreas (em hectares)
                "area_total_hectares": 0.0,
                "area_aproveitavel_hectares": 0.0,
                "area_inaproveitavel_hectares": 0.0,
                "area_preservacao_hectares": 0.0,
                "area_reserva_legal_hectares": 0.0,
                
                # Classificação
                "classification": "Aguardando API",  # Pequena, Média, Grande Propriedade, Minifúndio
                "module_type": "",  # Tipo de módulo fiscal
                "fiscal_modules": 0.0,  # Quantidade de módulos fiscais
                
                # Situação cadastral
                "status": "Regular",  # Regular, Irregular, Cancelado
                "registration_date": None,
                "last_update": None,
                "ccir_validity": None,  # Data de validade do CCIR
                
                # Exploração
                "exploitation_type": "",  # Agricultura, Pecuária, Florestal, etc
                "productive_use": False,  # Se há uso produtivo
                
                # Dados do ITR (Imposto Territorial Rural)
                "itr_situation": "",  # Situação do ITR
                "itr_last_year": None,
                
                # Metadados
                "data_source": "INCRA/SNCR",
                "consulted_at": datetime.now().isoformat(),
                "raw_data": {},  # Dados brutos da API
            }
            
            results.append(property_data)
        
        except Exception as e:
            logger.error(f"Error in INCRA CPF/CNPJ search: {str(e)}")
        
        return results
    
    async def _search_by_name(
        self,
        name: str,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca por nome de proprietário ou imóvel
        
        Nota: API do SNCR geralmente requer CPF/CNPJ ou código do imóvel
        """
        results = []
        
        try:
            # TODO: Implementar busca por nome se API permitir
            # A maioria das APIs do SNCR requer código do imóvel ou CPF/CNPJ
            pass
        
        except Exception as e:
            logger.error(f"Error in INCRA name search: {str(e)}")
        
        return results
    
    async def get_property_by_ccir(self, ccir_number: str) -> Optional[Dict[str, Any]]:
        """
        Busca imóvel específico pelo número do CCIR
        
        Args:
            ccir_number: Número do CCIR (ex: 12345678-2024)
        
        Returns:
            Dados completos do imóvel ou None se não encontrado
        """
        try:
            # Verificar cache
            cached = self._get_from_cache(f"ccir_{ccir_number}")
            if cached and len(cached) > 0:
                return cached[0]
            
            # Formatar CCIR
            ccir_formatted = self._format_ccir(ccir_number)
            
            # Consultar CCIR via API
            ccir_url = f"{self.ccir_consulta_url}/{ccir_formatted}"
            response = await self.fetch(ccir_url)
            
            if not response:
                return None
            
            data = response.json()
            
            # Processar e estruturar dados
            property_data = self._parse_ccir_data(data, ccir_number)
            
            # Salvar no cache
            self._save_to_cache(f"ccir_{ccir_number}", [property_data])
            
            return property_data
        
        except Exception as e:
            logger.error(f"Error fetching CCIR {ccir_number}: {str(e)}")
            return None
    
    async def get_property_by_code(self, property_code: str) -> Optional[Dict[str, Any]]:
        """
        Busca imóvel específico pelo código do imóvel rural (13 dígitos)
        
        Args:
            property_code: Código do imóvel rural (13 dígitos)
        
        Returns:
            Dados completos do imóvel ou None se não encontrado
        """
        try:
            # Verificar cache
            cached = self._get_from_cache(f"code_{property_code}")
            if cached and len(cached) > 0:
                return cached[0]
            
            # Consultar código do imóvel via API
            property_url = f"{self.sncr_api_base}/imovel/{property_code}"
            response = await self.fetch(property_url)
            
            if not response:
                return None
            
            data = response.json()
            
            # Processar e estruturar dados
            property_data = self._parse_property_data(data, property_code)
            
            # Salvar no cache
            self._save_to_cache(f"code_{property_code}", [property_data])
            
            return property_data
        
        except Exception as e:
            logger.error(f"Error fetching property code {property_code}: {str(e)}")
            return None
    
    async def verify_ccir_authenticity(self, ccir_number: str) -> Dict[str, Any]:
        """
        Verifica a autenticidade de um CCIR
        
        Args:
            ccir_number: Número do CCIR
        
        Returns:
            Dicionário com resultado da verificação
        """
        try:
            ccir_formatted = self._format_ccir(ccir_number)
            
            # Consultar autenticidade
            verify_url = f"{self.ccir_consulta_url}/autenticidade"
            response = await self.fetch(
                verify_url,
                params={"ccir": ccir_formatted}
            )
            
            if not response:
                return {
                    "valid": False,
                    "message": "Não foi possível verificar o CCIR",
                    "ccir_number": ccir_number,
                }
            
            data = response.json()
            
            return {
                "valid": data.get("valido", False),
                "message": data.get("mensagem", ""),
                "ccir_number": ccir_number,
                "emission_date": data.get("dataEmissao"),
                "validity_date": data.get("dataValidade"),
                "owner_name": data.get("proprietario"),
            }
        
        except Exception as e:
            logger.error(f"Error verifying CCIR {ccir_number}: {str(e)}")
            return {
                "valid": False,
                "message": f"Erro ao verificar: {str(e)}",
                "ccir_number": ccir_number,
            }
    
    def _parse_ccir_data(
        self,
        data: Dict[str, Any],
        ccir_number: str
    ) -> Dict[str, Any]:
        """
        Processa e estrutura os dados do CCIR
        
        Args:
            data: Dados do CCIR da API
            ccir_number: Número do CCIR
        
        Returns:
            Dados estruturados do imóvel
        """
        return {
            "ccir_number": ccir_number,
            "property_code": data.get("codigoImovel"),
            "property_name": data.get("nomeImovel"),
            "owner_name": data.get("nomeProprietario") or data.get("titular"),
            "owner_cpf_cnpj": data.get("cpfCnpj"),
            
            # Localização
            "state": data.get("uf"),
            "city": data.get("municipio"),
            "address": data.get("endereco", "Zona Rural"),
            "coordinates": {
                "latitude": float(data.get("latitude", 0) or 0),
                "longitude": float(data.get("longitude", 0) or 0),
            },
            
            # Áreas
            "area_total_hectares": float(data.get("areaTotal", 0) or 0),
            "area_aproveitavel_hectares": float(data.get("areaAproveitavel", 0) or 0),
            "area_inaproveitavel_hectares": float(data.get("areaInaproveitavel", 0) or 0),
            "area_preservacao_hectares": float(data.get("areaPreservacao", 0) or 0),
            "area_reserva_legal_hectares": float(data.get("areaReservaLegal", 0) or 0),
            
            # Classificação
            "classification": data.get("classificacao", ""),
            "module_type": data.get("tipoModulo", ""),
            "fiscal_modules": float(data.get("modulosFiscais", 0) or 0),
            
            # Situação
            "status": data.get("situacao", "Desconhecido"),
            "registration_date": data.get("dataInscricao"),
            "last_update": data.get("dataAtualizacao"),
            "ccir_validity": data.get("validadeCcir"),
            
            # Exploração
            "exploitation_type": data.get("tipoExploracao", ""),
            "productive_use": data.get("usoProdutivo", False),
            
            # ITR
            "itr_situation": data.get("situacaoItr", ""),
            "itr_last_year": data.get("anoItr"),
            
            # Metadados
            "data_source": "INCRA/SNCR",
            "consulted_at": datetime.now().isoformat(),
            "raw_data": data,
        }
    
    def _parse_property_data(
        self,
        data: Dict[str, Any],
        property_code: str
    ) -> Dict[str, Any]:
        """
        Processa e estrutura os dados do imóvel por código
        
        Args:
            data: Dados do imóvel da API
            property_code: Código do imóvel
        
        Returns:
            Dados estruturados do imóvel
        """
        # Similar ao _parse_ccir_data, mas pode ter estrutura ligeiramente diferente
        return self._parse_ccir_data(data, data.get("numeroCcir", ""))
    
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
