"""
CAR (Cadastro Ambiental Rural) Scraper

Integração com SICAR (Sistema Nacional de Cadastro Ambiental Rural)
APIs Governamentais: https://www.gov.br/conecta/catalogo/
"""
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
import logging

from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class CARScraper(BaseScraper):
    """
    Scraper para dados do CAR (Cadastro Ambiental Rural)
    
    Utiliza APIs oficiais do governo:
    - SICAR Demonstrativo: Situação das declarações no CAR
    - SICAR Imóvel: Dados completos do imóvel rural
    - Consulta Pública SICAR: Dados geoespaciais
    """
    
    def __init__(self):
        super().__init__()
        # APIs oficiais do governo
        self.sicar_api_base = "https://consultapublica.car.gov.br/api"
        self.sicar_demonstrativo_api = "https://servicos.car.gov.br/api/publico/demonstrativo"
        self.sicar_imovel_api = "https://servicos.car.gov.br/api/publico/imovel"
        
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
    
    async def search(
        self, 
        name: Optional[str] = None, 
        cpf_cnpj: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca propriedades rurais no CAR
        
        Args:
            name: Nome do proprietário ou imóvel
            cpf_cnpj: CPF ou CNPJ do proprietário
            state: Sigla do estado (ex: SP, MG, GO)
            city: Nome do município
        
        Returns:
            Lista de propriedades encontradas com dados completos
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
                results.extend(await self._search_by_cpf_cnpj(cpf_cnpj, state))
            
            # Estratégia 2: Busca por nome
            if name and not results:
                results.extend(await self._search_by_name(name, state, city))
            
            # Salvar no cache
            if results:
                self._save_to_cache(cache_key, results)
        
        except Exception as e:
            # Log error mas não falha a investigação toda
            logger.error(f"Error searching CAR: {str(e)}")
        
        return results
    
    async def _search_by_cpf_cnpj(
        self, 
        cpf_cnpj: str, 
        state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca por CPF/CNPJ no SICAR
        
        Nota: A API pública do SICAR tem limitações. Em produção,
        considerar usar serviços como InfoSimples ou Registro Rural.
        """
        results = []
        
        # Limpar CPF/CNPJ
        cpf_cnpj_clean = cpf_cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
        
        try:
            # Consulta à API pública (simulação - implementar com API real)
            # Em produção, usar API oficial ou serviço terceirizado
            
            # Por enquanto, retornar estrutura de exemplo com dados mockados
            # TODO: Implementar integração real com SICAR após obter credenciais
            
            # Estrutura esperada de retorno:
            property_data = {
                "car_number": f"CAR-{state or 'XX'}-{cpf_cnpj_clean[:8]}",
                "property_name": f"Propriedade Rural - {cpf_cnpj_clean[:8]}",
                "owner_name": "Nome a ser extraído da API",
                "owner_cpf_cnpj": cpf_cnpj_clean,
                
                # Localização
                "state": state or "Aguardando API",
                "city": "Município a ser extraído",
                "address": "Endereço rural completo",
                
                # Áreas (em hectares)
                "area_total_hectares": 0.0,
                "area_app_hectares": 0.0,  # Área de Preservação Permanente
                "area_reserva_legal_hectares": 0.0,
                "area_consolidada_hectares": 0.0,
                
                # Geolocalização (GeoJSON)
                "coordinates": {
                    "type": "Polygon",
                    "coordinates": [[]],  # Coordenadas do polígono
                },
                "centroid": {
                    "latitude": 0.0,
                    "longitude": 0.0,
                },
                
                # Situação cadastral
                "status": "Ativo",  # Ativo, Cancelado, Pendente
                "registration_date": None,
                "last_update": None,
                
                # Dados ambientais
                "biome": "",  # Amazônia, Cerrado, Mata Atlântica, etc
                "watershed": "",  # Bacia hidrográfica
                "indigenous_land": False,
                "conservation_unit": False,
                
                # Metadados
                "data_source": "CAR/SICAR",
                "consulted_at": datetime.now().isoformat(),
                "raw_data": {},  # Dados brutos da API
            }
            
            results.append(property_data)
        
        except Exception as e:
            logger.error(f"Error in CAR CPF/CNPJ search: {str(e)}")
        
        return results
    
    async def _search_by_name(
        self,
        name: str,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca por nome de proprietário ou imóvel
        
        Nota: Busca por nome é menos precisa e pode retornar múltiplos resultados
        """
        results = []
        
        try:
            # TODO: Implementar busca por nome quando API permitir
            # A maioria das APIs do CAR requer o número do CAR ou CPF/CNPJ
            
            # Por enquanto, retornar vazio ou usar scraping HTML se necessário
            pass
        
        except Exception as e:
            logger.error(f"Error in CAR name search: {str(e)}")
        
        return results
    
    async def get_property_by_car_number(self, car_number: str) -> Optional[Dict[str, Any]]:
        """
        Busca propriedade específica pelo número do CAR
        
        Args:
            car_number: Número do CAR (ex: SP-1234567-ABCD1234EFGH5678...)
        
        Returns:
            Dados completos da propriedade ou None se não encontrado
        """
        try:
            # Verificar cache
            cached = self._get_from_cache(f"car_{car_number}")
            if cached and len(cached) > 0:
                return cached[0]
            
            # Buscar dados do demonstrativo (situação do CAR)
            demonstrativo_url = f"{self.sicar_demonstrativo_api}/{car_number}"
            demo_response = await self.fetch(demonstrativo_url)
            
            if not demo_response:
                return None
            
            demo_data = demo_response.json()
            
            # Buscar dados completos do imóvel
            imovel_url = f"{self.sicar_imovel_api}/{car_number}"
            imovel_response = await self.fetch(imovel_url)
            
            imovel_data = imovel_response.json() if imovel_response else {}
            
            # Processar e estruturar dados
            property_data = self._parse_car_data(demo_data, imovel_data, car_number)
            
            # Salvar no cache
            self._save_to_cache(f"car_{car_number}", [property_data])
            
            return property_data
        
        except Exception as e:
            logger.error(f"Error fetching CAR {car_number}: {str(e)}")
            return None
    
    def _parse_car_data(
        self,
        demonstrativo: Dict[str, Any],
        imovel: Dict[str, Any],
        car_number: str
    ) -> Dict[str, Any]:
        """
        Processa e estrutura os dados do CAR
        
        Args:
            demonstrativo: Dados do demonstrativo CAR
            imovel: Dados completos do imóvel
            car_number: Número do CAR
        
        Returns:
            Dados estruturados da propriedade
        """
        # Extrair coordenadas geográficas (se disponível)
        coordinates = self._extract_coordinates(imovel)
        
        return {
            "car_number": car_number,
            "property_name": imovel.get("nomePropriedade") or demonstrativo.get("nomeImovel"),
            "owner_name": imovel.get("nomeProprietario") or demonstrativo.get("proprietario"),
            "owner_cpf_cnpj": imovel.get("cpfCnpjProprietario") or demonstrativo.get("cpfCnpj"),
            
            # Localização
            "state": imovel.get("uf") or demonstrativo.get("estado"),
            "city": imovel.get("municipio") or demonstrativo.get("municipio"),
            "address": imovel.get("endereco", ""),
            
            # Áreas
            "area_total_hectares": float(imovel.get("areaImovel", 0) or 0),
            "area_app_hectares": float(demonstrativo.get("areaApp", 0) or 0),
            "area_reserva_legal_hectares": float(demonstrativo.get("areaReservaLegal", 0) or 0),
            "area_consolidada_hectares": float(demonstrativo.get("areaConsolidada", 0) or 0),
            
            # Geolocalização
            "coordinates": coordinates.get("polygon", {"type": "Polygon", "coordinates": []}),
            "centroid": coordinates.get("centroid", {"latitude": 0, "longitude": 0}),
            
            # Situação
            "status": imovel.get("status", "Desconhecido"),
            "registration_date": demonstrativo.get("dataInscricao"),
            "last_update": demonstrativo.get("dataAtualizacao"),
            
            # Dados ambientais
            "biome": demonstrativo.get("bioma", ""),
            "watershed": demonstrativo.get("baciaHidrografica", ""),
            "indigenous_land": demonstrativo.get("terraIndigena", False),
            "conservation_unit": demonstrativo.get("unidadeConservacao", False),
            
            # Metadados
            "data_source": "CAR/SICAR",
            "consulted_at": datetime.now().isoformat(),
            "raw_data": {
                "demonstrativo": demonstrativo,
                "imovel": imovel,
            },
        }
    
    def _extract_coordinates(self, imovel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai coordenadas geográficas do imóvel
        
        Args:
            imovel_data: Dados do imóvel da API
        
        Returns:
            Dicionário com polígono (GeoJSON) e centroide
        """
        coordinates = {
            "polygon": {
                "type": "Polygon",
                "coordinates": [],
            },
            "centroid": {
                "latitude": 0.0,
                "longitude": 0.0,
            }
        }
        
        try:
            # Extrair geometria se disponível
            geometry = imovel_data.get("geometry") or imovel_data.get("geometria")
            
            if geometry:
                # Se vier em formato GeoJSON
                if isinstance(geometry, dict):
                    if geometry.get("type") == "Polygon":
                        coordinates["polygon"] = geometry
                    elif geometry.get("type") == "MultiPolygon":
                        # Usar o primeiro polígono
                        coordinates["polygon"] = {
                            "type": "Polygon",
                            "coordinates": geometry["coordinates"][0] if geometry.get("coordinates") else []
                        }
                
                # Calcular centroide
                coords_list = coordinates["polygon"].get("coordinates", [])
                if coords_list and len(coords_list) > 0:
                    coordinates["centroid"] = self._calculate_centroid(coords_list[0])
            
            # Fallback: buscar coordenadas do centroide direto
            if imovel_data.get("latitude") and imovel_data.get("longitude"):
                coordinates["centroid"] = {
                    "latitude": float(imovel_data["latitude"]),
                    "longitude": float(imovel_data["longitude"]),
                }
        
        except Exception as e:
            logger.error(f"Error extracting coordinates: {str(e)}")
        
        return coordinates
    
    def _calculate_centroid(self, coords: List[List[float]]) -> Dict[str, float]:
        """
        Calcula o centroide de um polígono
        
        Args:
            coords: Lista de coordenadas [longitude, latitude]
        
        Returns:
            Dicionário com latitude e longitude do centroide
        """
        if not coords or len(coords) == 0:
            return {"latitude": 0.0, "longitude": 0.0}
        
        try:
            # Média simples das coordenadas
            lats = [coord[1] for coord in coords if len(coord) >= 2]
            lons = [coord[0] for coord in coords if len(coord) >= 2]
            
            if lats and lons:
                return {
                    "latitude": sum(lats) / len(lats),
                    "longitude": sum(lons) / len(lons),
                }
        except Exception:
            pass
        
        return {"latitude": 0.0, "longitude": 0.0}
    
    async def search_by_municipality(
        self,
        state: str,
        city: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Busca todas as propriedades de um município
        
        Args:
            state: Sigla do estado (SP, MG, GO, etc)
            city: Nome do município
            limit: Limite de resultados (padrão: 100)
        
        Returns:
            Lista de propriedades do município
        """
        results = []
        
        try:
            # Consulta pública SICAR por município
            params = {
                "uf": state,
                "municipio": city,
                "limit": limit,
            }
            
            # TODO: Implementar consulta real após obter acesso à API
            # response = await self.fetch(
            #     f"{self.sicar_api_base}/imoveis/municipio",
            #     params=params
            # )
            
            # Por enquanto, retornar estrutura de exemplo
            # Em produção, processar resposta real da API
            
        except Exception as e:
            logger.error(f"Error searching municipality {city}/{state}: {str(e)}")
        
        return results
    
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
