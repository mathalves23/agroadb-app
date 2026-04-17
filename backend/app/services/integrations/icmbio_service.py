"""
Serviço de Integração com ICMBio
Consulta unidades de conservação e áreas protegidas
"""
import aiohttp
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class UnidadeConservacao:
    """Unidade de conservação do ICMBio"""
    nome: str
    categoria: str  # Parque Nacional, Reserva Biológica, etc
    grupo: str  # Proteção Integral, Uso Sustentável
    esfera: str  # Federal, Estadual, Municipal
    municipios: List[str]
    uf: str
    area_hectares: float
    ato_legal: str
    ano_criacao: Optional[int] = None
    administracao: Optional[str] = None
    bioma: Optional[str] = None


@dataclass
class SobreposicaoUC:
    """Resultado de verificação de sobreposição com UC"""
    tem_sobreposicao: bool
    unidades_sobrepostas: List[UnidadeConservacao]
    area_sobreposta_ha: Optional[float] = None
    percentual_sobreposicao: Optional[float] = None


class ICMBioService:
    """
    Serviço de integração com ICMBio
    
    Funcionalidades:
    - Consulta de unidades de conservação
    - Verificação de sobreposição com áreas protegidas
    - Consulta por município/UF
    - Busca por coordenadas
    """
    
    # URLs dos serviços WFS do ICMBio
    GEOSERVER_URL = "https://geoserver.icmbio.gov.br/geoserver/wfs"
    
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
    
    async def consultar_unidades_conservacao(
        self,
        municipio: Optional[str] = None,
        uf: Optional[str] = None,
        categoria: Optional[str] = None,
        grupo: Optional[str] = None
    ) -> List[UnidadeConservacao]:
        """
        Consulta unidades de conservação
        
        Args:
            municipio: Nome do município (opcional)
            uf: Sigla da UF (opcional)
            categoria: Categoria da UC (opcional)
            grupo: Grupo da UC - Proteção Integral ou Uso Sustentável (opcional)
            
        Returns:
            Lista de unidades de conservação encontradas
        """
        try:
            logger.info(
                f"Consultando unidades de conservação ICMBio "
                f"(município={municipio}, uf={uf}, categoria={categoria})"
            )
            
            # Parâmetros WFS para GeoJSON
            params = {
                'service': 'WFS',
                'version': '2.0.0',
                'request': 'GetFeature',
                'typeName': 'ucfed:unidades_conservacao_federais',
                'outputFormat': 'application/json',
                'srsName': 'EPSG:4326'
            }
            
            # Construir filtro CQL
            filters = []
            if municipio:
                filters.append(f"municipios ILIKE '%{municipio}%'")
            if uf:
                filters.append(f"uf = '{uf.upper()}'")
            if categoria:
                filters.append(f"categoria ILIKE '%{categoria}%'")
            if grupo:
                filters.append(f"grupo ILIKE '%{grupo}%'")
            
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
                    logger.warning(f"ICMBio retornou status {response.status}")
                    return []
                
                data = await response.json()
                unidades = self._parse_geojson(data)
                
                logger.info(
                    f"✅ ICMBio: {len(unidades)} unidade(s) de "
                    f"conservação encontrada(s)"
                )
                
                return unidades
        
        except aiohttp.ClientError as e:
            logger.error(f"Erro de conexão com ICMBio: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro ao consultar ICMBio: {e}")
            return []
    
    def _parse_geojson(self, geojson: Dict) -> List[UnidadeConservacao]:
        """Parse do GeoJSON retornado pelo ICMBio"""
        try:
            unidades = []
            
            features = geojson.get('features', [])
            
            for feature in features:
                props = feature.get('properties', {})
                
                # Extrair municípios
                municipios_str = props.get('municipios', '')
                municipios = [m.strip() for m in municipios_str.split(',') if m.strip()]
                
                # Extrair ano de criação
                ano_str = props.get('ano_criacao', props.get('ano', ''))
                ano = None
                if ano_str:
                    try:
                        ano = int(str(ano_str)[:4])
                    except:
                        pass
                
                unidade = UnidadeConservacao(
                    nome=props.get('nome_uc', props.get('nome', 'N/A')),
                    categoria=props.get('categoria', 'N/A'),
                    grupo=props.get('grupo', 'N/A'),
                    esfera=props.get('esfera', 'N/A'),
                    municipios=municipios,
                    uf=props.get('uf_sigla', props.get('uf', '')),
                    area_hectares=float(props.get('area_ha', 0)),
                    ato_legal=props.get('ato_legal', 'N/A'),
                    ano_criacao=ano,
                    administracao=props.get('administracao'),
                    bioma=props.get('bioma')
                )
                
                unidades.append(unidade)
            
            return unidades
            
        except Exception as e:
            logger.error(f"Erro ao fazer parsing do GeoJSON do ICMBio: {e}")
            return []
    
    async def verificar_sobreposicao_por_coordenadas(
        self,
        latitude: float,
        longitude: float,
        raio_km: float = 10.0
    ) -> SobreposicaoUC:
        """
        Verifica se coordenadas estão em ou próximas de UC
        
        Args:
            latitude: Latitude em graus decimais
            longitude: Longitude em graus decimais
            raio_km: Raio de busca em km
            
        Returns:
            Resultado da verificação de sobreposição
        """
        try:
            logger.info(
                f"Verificando sobreposição com UCs "
                f"em ({latitude}, {longitude})"
            )
            
            # Converter raio para graus (aproximado)
            raio_graus = raio_km / 111.0
            
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
                'typeName': 'ucfed:unidades_conservacao_federais',
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
                    logger.warning(f"ICMBio retornou status {response.status}")
                    return SobreposicaoUC(
                        tem_sobreposicao=False,
                        unidades_sobrepostas=[]
                    )
                
                data = await response.json()
                unidades = self._parse_geojson(data)
                
                tem_sobreposicao = len(unidades) > 0
                
                if tem_sobreposicao:
                    logger.warning(
                        f"⚠️ SOBREPOSIÇÃO COM UNIDADE DE CONSERVAÇÃO DETECTADA! "
                        f"{len(unidades)} UC(s) no raio de {raio_km}km"
                    )
                else:
                    logger.info("✅ Nenhuma sobreposição com UC detectada")
                
                return SobreposicaoUC(
                    tem_sobreposicao=tem_sobreposicao,
                    unidades_sobrepostas=unidades
                )
        
        except Exception as e:
            logger.error(f"Erro ao verificar sobreposição com ICMBio: {e}")
            return SobreposicaoUC(
                tem_sobreposicao=False,
                unidades_sobrepostas=[]
            )
    
    async def listar_categorias(self, grupo: Optional[str] = None) -> List[str]:
        """
        Lista categorias de UCs
        
        Args:
            grupo: Filtrar por grupo - "Proteção Integral" ou "Uso Sustentável"
            
        Returns:
            Lista de categorias
        """
        try:
            unidades = await self.consultar_unidades_conservacao(grupo=grupo)
            
            # Extrair categorias únicas
            categorias = sorted(set(
                uc.categoria 
                for uc in unidades 
                if uc.categoria and uc.categoria != 'N/A'
            ))
            
            logger.info(f"✅ {len(categorias)} categoria(s) encontrada(s)")
            
            return categorias
            
        except Exception as e:
            logger.error(f"Erro ao listar categorias: {e}")
            return []
    
    async def estatisticas_por_uf(self, uf: str) -> Dict:
        """
        Estatísticas de UCs por UF
        
        Args:
            uf: Sigla da UF
            
        Returns:
            Estatísticas agregadas
        """
        try:
            unidades = await self.consultar_unidades_conservacao(uf=uf)
            
            if not unidades:
                return {
                    'total_unidades': 0,
                    'area_total_ha': 0,
                    'por_grupo': {},
                    'por_categoria': {}
                }
            
            # Agrupar por grupo
            por_grupo = {}
            for uc in unidades:
                grupo = uc.grupo
                if grupo not in por_grupo:
                    por_grupo[grupo] = {'count': 0, 'area_ha': 0}
                por_grupo[grupo]['count'] += 1
                por_grupo[grupo]['area_ha'] += uc.area_hectares
            
            # Agrupar por categoria
            por_categoria = {}
            for uc in unidades:
                cat = uc.categoria
                if cat not in por_categoria:
                    por_categoria[cat] = {'count': 0, 'area_ha': 0}
                por_categoria[cat]['count'] += 1
                por_categoria[cat]['area_ha'] += uc.area_hectares
            
            area_total = sum(uc.area_hectares for uc in unidades)
            
            return {
                'total_unidades': len(unidades),
                'area_total_ha': area_total,
                'por_grupo': por_grupo,
                'por_categoria': por_categoria
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}
