"""
Serviço de Integração com FUNAI
Consulta terras indígenas e verifica sobreposições
"""
import aiohttp
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class TerraIndigena:
    """Terra indígena da FUNAI"""
    nome: str
    etnia: str
    municipios: List[str]
    uf: str
    fase: str  # DECLARADA, HOMOLOGADA, REGULARIZADA, etc
    area_hectares: float
    modalidade: str
    situacao_fundiaria: str
    decreto: Optional[str] = None
    data_decreto: Optional[str] = None
    perimetro_aprovado: Optional[str] = None


@dataclass
class SobreposicaoTerraIndigena:
    """Resultado de verificação de sobreposição"""
    tem_sobreposicao: bool
    terras_sobrepostas: List[TerraIndigena]
    area_sobreposta_ha: Optional[float] = None
    percentual_sobreposicao: Optional[float] = None


class FUNAIService:
    """
    Serviço de integração com FUNAI
    
    Funcionalidades:
    - Consulta de terras indígenas
    - Verificação de sobreposição com propriedades
    - Consulta por município/UF
    - Busca por coordenadas geográficas
    """
    
    # URLs dos serviços WFS da FUNAI
    GEOSERVER_URL = "https://geoserver.funai.gov.br/geoserver/wfs"
    REST_API_URL = "https://geoserver.funai.gov.br/geoserver/rest"
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self.session = session
        self._own_session = session is None
    
    async def __aenter__(self):
        if self._own_session:
            self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._own_session and self.session:
            await self.session.close()
    
    async def consultar_terras_indigenas(
        self,
        municipio: Optional[str] = None,
        uf: Optional[str] = None,
        nome: Optional[str] = None
    ) -> List[TerraIndigena]:
        """
        Consulta terras indígenas
        
        Args:
            municipio: Nome do município (opcional)
            uf: Sigla da UF (opcional)
            nome: Nome da terra indígena (opcional)
            
        Returns:
            Lista de terras indígenas encontradas
        """
        try:
            logger.info(
                f"Consultando terras indígenas FUNAI "
                f"(município={municipio}, uf={uf}, nome={nome})"
            )
            
            # Parâmetros WFS para GeoJSON
            params = {
                'service': 'WFS',
                'version': '2.0.0',
                'request': 'GetFeature',
                'typeName': 'funai:terras_indigenas',
                'outputFormat': 'application/json',
                'srsName': 'EPSG:4326'
            }
            
            # Construir filtro CQL
            filters = []
            if municipio:
                filters.append(f"municipios ILIKE '%{municipio}%'")
            if uf:
                filters.append(f"uf = '{uf.upper()}'")
            if nome:
                filters.append(f"nome ILIKE '%{nome}%'")
            
            if filters:
                params['CQL_FILTER'] = ' AND '.join(filters)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AgroADB/1.0)',
                'Accept': 'application/json'
            }
            
            async with self.session.get(
                self.GEOSERVER_URL,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status != 200:
                    logger.warning(f"FUNAI retornou status {response.status}")
                    return []
                
                data = await response.json()
                terras = self._parse_geojson(data)
                
                logger.info(f"✅ FUNAI: {len(terras)} terra(s) indígena(s) encontrada(s)")
                
                return terras
        
        except aiohttp.ClientError as e:
            logger.error(f"Erro de conexão com FUNAI: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro ao consultar FUNAI: {e}")
            return []
    
    def _parse_geojson(self, geojson: Dict) -> List[TerraIndigena]:
        """Parse do GeoJSON retornado pela FUNAI"""
        try:
            terras = []
            
            features = geojson.get('features', [])
            
            for feature in features:
                props = feature.get('properties', {})
                
                # Extrair municípios
                municipios_str = props.get('municipios', '')
                municipios = [m.strip() for m in municipios_str.split(',') if m.strip()]
                
                terra = TerraIndigena(
                    nome=props.get('terrai_nom', props.get('nome', 'N/A')),
                    etnia=props.get('etnia_nome', props.get('etnia', 'N/A')),
                    municipios=municipios,
                    uf=props.get('uf_sigla', props.get('uf', '')),
                    fase=props.get('fase_ti', props.get('fase', 'N/A')),
                    area_hectares=float(props.get('area_ha', 0)),
                    modalidade=props.get('modalidade', 'N/A'),
                    situacao_fundiaria=props.get('situacao', 'N/A'),
                    decreto=props.get('decreto'),
                    data_decreto=props.get('data_decreto'),
                    perimetro_aprovado=props.get('perimetro')
                )
                
                terras.append(terra)
            
            return terras
            
        except Exception as e:
            logger.error(f"Erro ao fazer parsing do GeoJSON da FUNAI: {e}")
            return []
    
    async def verificar_sobreposicao_por_coordenadas(
        self,
        latitude: float,
        longitude: float,
        raio_km: float = 10.0
    ) -> SobreposicaoTerraIndigena:
        """
        Verifica se coordenadas estão em ou próximas de terra indígena
        
        Args:
            latitude: Latitude em graus decimais
            longitude: Longitude em graus decimais
            raio_km: Raio de busca em km
            
        Returns:
            Resultado da verificação de sobreposição
        """
        try:
            logger.info(
                f"Verificando sobreposição com terras indígenas "
                f"em ({latitude}, {longitude})"
            )
            
            # Converter raio para graus (aproximado)
            raio_graus = raio_km / 111.0  # 1 grau ≈ 111 km
            
            # Criar bbox
            bbox = (
                longitude - raio_graus,
                latitude - raio_graus,
                longitude + raio_graus,
                latitude + raio_graus
            )
            
            params = {
                'service': 'WFS',
                'version': '2.0.0',
                'request': 'GetFeature',
                'typeName': 'funai:terras_indigenas',
                'outputFormat': 'application/json',
                'srsName': 'EPSG:4326',
                'bbox': ','.join(map(str, bbox))
            }
            
            async with self.session.get(
                self.GEOSERVER_URL,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status != 200:
                    logger.warning(f"FUNAI retornou status {response.status}")
                    return SobreposicaoTerraIndigena(
                        tem_sobreposicao=False,
                        terras_sobrepostas=[]
                    )
                
                data = await response.json()
                terras = self._parse_geojson(data)
                
                tem_sobreposicao = len(terras) > 0
                
                if tem_sobreposicao:
                    logger.warning(
                        f"⚠️ SOBREPOSIÇÃO COM TERRA INDÍGENA DETECTADA! "
                        f"{len(terras)} terra(s) no raio de {raio_km}km"
                    )
                else:
                    logger.info("✅ Nenhuma sobreposição com terra indígena detectada")
                
                return SobreposicaoTerraIndigena(
                    tem_sobreposicao=tem_sobreposicao,
                    terras_sobrepostas=terras
                )
        
        except Exception as e:
            logger.error(f"Erro ao verificar sobreposição com FUNAI: {e}")
            return SobreposicaoTerraIndigena(
                tem_sobreposicao=False,
                terras_sobrepostas=[]
            )
    
    async def buscar_por_car(self, car_code: str) -> SobreposicaoTerraIndigena:
        """
        Verifica sobreposição usando código CAR
        
        Nota: Esta funcionalidade requer integração com SICAR para obter
        coordenadas do CAR e então fazer análise espacial.
        
        Args:
            car_code: Código do CAR
            
        Returns:
            Resultado da verificação
        """
        logger.info(f"Verificação de sobreposição para CAR {car_code}")
        
        # Esta funcionalidade requer:
        # 1. Buscar geometria do CAR no SICAR
        # 2. Buscar geometrias de terras indígenas
        # 3. Fazer análise de interseção espacial
        
        # Por enquanto, retornar não implementado
        logger.warning("Análise espacial completa não implementada nesta versão")
        
        return SobreposicaoTerraIndigena(
            tem_sobreposicao=False,
            terras_sobrepostas=[]
        )
    
    async def listar_etnias(self, uf: Optional[str] = None) -> List[str]:
        """
        Lista etnias presentes nas terras indígenas
        
        Args:
            uf: Filtrar por UF (opcional)
            
        Returns:
            Lista de nomes de etnias
        """
        try:
            terras = await self.consultar_terras_indigenas(uf=uf)
            
            # Extrair etnias únicas
            etnias = sorted(set(
                terra.etnia 
                for terra in terras 
                if terra.etnia and terra.etnia != 'N/A'
            ))
            
            logger.info(f"✅ {len(etnias)} etnia(s) encontrada(s)")
            
            return etnias
            
        except Exception as e:
            logger.error(f"Erro ao listar etnias: {e}")
            return []
