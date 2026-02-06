"""
Integrações com Órgãos Ambientais e Patrimoniais
IBAMA, FUNAI, ICMBio, SPU
"""
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ==================== IBAMA ====================

@dataclass
class IBAMAEmbargo:
    """Embargo ambiental do IBAMA"""
    numero_auto: str
    cpf_cnpj: str
    nome_autuado: str
    data_autuacao: datetime
    tipo_infracao: str
    descricao: str
    valor_multa: float
    municipio: str
    uf: str
    latitude: Optional[float]
    longitude: Optional[float]
    status: str  # ATIVO, QUITADO, CANCELADO


class IBAMAIntegration:
    """
    Integração com IBAMA
    
    Dados disponíveis:
    - Embargos ambientais
    - Áreas embargadas
    - Autuações ambientais
    - CTF (Cadastro Técnico Federal)
    """
    
    BASE_URL = "https://servicos.ibama.gov.br/ctf/publico"
    EMBARGOS_URL = "https://servicos.ibama.gov.br/ctf/publico/areasembargadas/consulta.php"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_embargos(
        self,
        cpf_cnpj: str
    ) -> List[IBAMAEmbargo]:
        """Busca embargos ambientais"""
        
        try:
            # Limpar documento
            doc_clean = ''.join(filter(str.isdigit, cpf_cnpj))
            
            params = {
                'tipoConsulta': 'documento',
                'documento': doc_clean
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AgroADB/1.0)',
            }
            
            async with self.session.get(
                self.EMBARGOS_URL,
                params=params,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    embargos = []
                    for item in data.get('embargos', []):
                        embargo = IBAMAEmbargo(
                            numero_auto=item.get('numeroAuto', ''),
                            cpf_cnpj=item.get('cpfCnpj', ''),
                            nome_autuado=item.get('nomeAutuado', ''),
                            data_autuacao=self._parse_date(item.get('dataAutuacao')),
                            tipo_infracao=item.get('tipoInfracao', ''),
                            descricao=item.get('descricao', ''),
                            valor_multa=float(item.get('valorMulta', 0)),
                            municipio=item.get('municipio', ''),
                            uf=item.get('uf', ''),
                            latitude=item.get('latitude'),
                            longitude=item.get('longitude'),
                            status=item.get('status', 'ATIVO')
                        )
                        embargos.append(embargo)
                    
                    logger.info(
                        f"✅ IBAMA: {len(embargos)} embargos encontrados"
                    )
                    
                    return embargos
                
                else:
                    logger.warning(f"IBAMA retornou status {response.status}")
                    return []
        
        except Exception as e:
            logger.error(f"Erro ao consultar IBAMA: {e}")
            return []
    
    async def check_ctf(self, cpf_cnpj: str) -> Optional[Dict]:
        """Verifica registro no Cadastro Técnico Federal"""
        
        try:
            url = f"{self.BASE_URL}/ctf/consulta"
            
            doc_clean = ''.join(filter(str.isdigit, cpf_cnpj))
            
            params = {'documento': doc_clean}
            
            async with self.session.get(
                url,
                params=params,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    logger.info(f"✅ IBAMA CTF: Dados encontrados")
                    
                    return {
                        'possui_ctf': data.get('possuiCTF', False),
                        'numero_ctf': data.get('numeroCTF'),
                        'atividades': data.get('atividades', []),
                        'situacao': data.get('situacao')
                    }
                
                else:
                    return None
        
        except Exception as e:
            logger.error(f"Erro ao consultar CTF: {e}")
            return None
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse data do IBAMA"""
        if not date_str:
            return datetime.now()
        
        try:
            return datetime.strptime(date_str, '%d/%m/%Y')
        except:
            return datetime.now()


# ==================== FUNAI ====================

@dataclass
class FUNAILand:
    """Terra indígena da FUNAI"""
    nome: str
    etnia: str
    municipios: List[str]
    uf: str
    fase: str  # DECLARADA, HOMOLOGADA, REGULARIZADA, etc
    area_hectares: float
    modalidade: str
    decreto: Optional[str]
    data_decreto: Optional[datetime]


class FUNAIIntegration:
    """
    Integração com FUNAI
    
    Dados:
    - Terras indígenas
    - Limites territoriais
    - Status de regularização
    """
    
    GEOSERVER_URL = "https://geoserver.funai.gov.br/geoserver/wfs"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_indigenous_lands(
        self,
        municipio: Optional[str] = None,
        uf: Optional[str] = None
    ) -> List[FUNAILand]:
        """Busca terras indígenas"""
        
        try:
            params = {
                'service': 'WFS',
                'version': '1.0.0',
                'request': 'GetFeature',
                'typeName': 'funai:terras_indigenas',
                'outputFormat': 'application/json'
            }
            
            # Filtro CQL se necessário
            filters = []
            if municipio:
                filters.append(f"municipios LIKE '%{municipio}%'")
            if uf:
                filters.append(f"uf = '{uf}'")
            
            if filters:
                params['CQL_FILTER'] = ' AND '.join(filters)
            
            async with self.session.get(
                self.GEOSERVER_URL,
                params=params,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    lands = []
                    for feature in data.get('features', []):
                        props = feature.get('properties', {})
                        
                        land = FUNAILand(
                            nome=props.get('nome', ''),
                            etnia=props.get('etnia', ''),
                            municipios=props.get('municipios', '').split(','),
                            uf=props.get('uf', ''),
                            fase=props.get('fase', ''),
                            area_hectares=float(props.get('area_ha', 0)),
                            modalidade=props.get('modalidade', ''),
                            decreto=props.get('decreto'),
                            data_decreto=None  # Parse se disponível
                        )
                        lands.append(land)
                    
                    logger.info(
                        f"✅ FUNAI: {len(lands)} terras indígenas encontradas"
                    )
                    
                    return lands
                
                else:
                    logger.warning(f"FUNAI retornou status {response.status}")
                    return []
        
        except Exception as e:
            logger.error(f"Erro ao consultar FUNAI: {e}")
            return []
    
    async def check_overlap_with_property(
        self,
        car_number: str
    ) -> Dict:
        """Verifica sobreposição com terras indígenas"""
        
        # Esta funcionalidade requer análise espacial
        # Seria necessário buscar geometria do CAR e verificar intersecção
        
        logger.info(f"Verificando sobreposição para CAR {car_number}")
        
        return {
            'has_overlap': False,
            'overlapping_lands': [],
            'message': 'Análise espacial não implementada nesta versão'
        }


# ==================== ICMBio ====================

@dataclass
class ConservationUnit:
    """Unidade de conservação do ICMBio"""
    nome: str
    categoria: str  # Parque Nacional, Reserva, etc
    grupo: str  # Proteção Integral, Uso Sustentável
    esfera: str  # Federal, Estadual, Municipal
    municipios: List[str]
    uf: str
    area_hectares: float
    ato_legal: str
    data_criacao: Optional[datetime]


class ICMBioIntegration:
    """
    Integração com ICMBio
    
    Dados:
    - Unidades de conservação
    - Áreas protegidas
    - Limites territoriais
    """
    
    GEOSERVER_URL = "https://geoserver.icmbio.gov.br/geoserver/wfs"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_conservation_units(
        self,
        municipio: Optional[str] = None,
        uf: Optional[str] = None
    ) -> List[ConservationUnit]:
        """Busca unidades de conservação"""
        
        try:
            params = {
                'service': 'WFS',
                'version': '1.0.0',
                'request': 'GetFeature',
                'typeName': 'icmbio:unidades_conservacao',
                'outputFormat': 'application/json'
            }
            
            filters = []
            if municipio:
                filters.append(f"municipios LIKE '%{municipio}%'")
            if uf:
                filters.append(f"uf = '{uf}'")
            
            if filters:
                params['CQL_FILTER'] = ' AND '.join(filters)
            
            async with self.session.get(
                self.GEOSERVER_URL,
                params=params,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    units = []
                    for feature in data.get('features', []):
                        props = feature.get('properties', {})
                        
                        unit = ConservationUnit(
                            nome=props.get('nome', ''),
                            categoria=props.get('categoria', ''),
                            grupo=props.get('grupo', ''),
                            esfera=props.get('esfera', ''),
                            municipios=props.get('municipios', '').split(','),
                            uf=props.get('uf', ''),
                            area_hectares=float(props.get('area_ha', 0)),
                            ato_legal=props.get('ato_legal', ''),
                            data_criacao=None
                        )
                        units.append(unit)
                    
                    logger.info(
                        f"✅ ICMBio: {len(units)} unidades de conservação encontradas"
                    )
                    
                    return units
                
                else:
                    return []
        
        except Exception as e:
            logger.error(f"Erro ao consultar ICMBio: {e}")
            return []


# ==================== SPU ====================

@dataclass
class SPUProperty:
    """Imóvel da SPU (Secretaria do Patrimônio da União)"""
    rip: str  # Registro de Imóvel Patrimonial
    tipo: str
    utilizacao: str
    municipio: str
    uf: str
    area_m2: float
    ocupante: Optional[str]
    situacao: str


class SPUIntegration:
    """
    Integração com SPU
    
    Dados:
    - Imóveis da União
    - Terrenos de marinha
    - Terras devolutas federais
    """
    
    BASE_URL = "https://www.gov.br/economia/pt-br/acesso-a-informacao/acoes-e-programas/patrimonio-da-uniao"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_federal_properties(
        self,
        municipio: str,
        uf: str
    ) -> List[SPUProperty]:
        """Busca imóveis da União"""
        
        # API pública da SPU é limitada
        # Dados geralmente disponíveis via datasets abertos
        
        logger.info(f"Consultando SPU para {municipio}/{uf}")
        
        # Retornar vazio por enquanto
        # Em produção, integrar com datasets abertos
        return []
    
    async def check_federal_land(
        self,
        car_number: str
    ) -> Dict:
        """Verifica se propriedade está em terra da União"""
        
        logger.info(f"Verificando terra da União para CAR {car_number}")
        
        return {
            'is_federal_land': False,
            'property_type': None,
            'message': 'Consulta não disponível via API pública'
        }
