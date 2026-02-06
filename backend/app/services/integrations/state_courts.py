"""
Integração com ESAJ (e-SAJ) e Projudi
Tribunais de Justiça Estaduais
"""
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class StateCourtProcess:
    """Processo de tribunal estadual"""
    numero_processo: str
    tribunal: str  # TJSP, TJMG, etc
    sistema: str  # ESAJ, Projudi
    classe: str
    assunto: str
    data_distribuicao: Optional[datetime]
    status: str
    comarca: str
    vara: str
    partes: List[Dict[str, str]]
    movimentacoes: List[Dict]


class ESAJIntegration:
    """
    Integração com e-SAJ
    
    Tribunais suportados:
    - TJSP (São Paulo)
    - TJSC (Santa Catarina)
    - TJAL (Alagoas)
    - TJCE (Ceará)
    - TJMS (Mato Grosso do Sul)
    """
    
    TRIBUNAL_URLS = {
        'TJSP': 'https://esaj.tjsp.jus.br/cpopg/open.do',
        'TJSC': 'https://esaj.tjsc.jus.br/cpopg/open.do',
        'TJAL': 'https://www2.tjal.jus.br/cpopg/open.do',
        'TJCE': 'https://esaj.tjce.jus.br/cpopg/open.do',
        'TJMS': 'https://esaj.tjms.jus.br/cpopg/open.do',
    }
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_processes(
        self,
        tribunal: str,
        documento: str,  # CPF ou CNPJ
        tipo: str = 'parte'
    ) -> List[StateCourtProcess]:
        """Busca processos em tribunal específico"""
        
        if tribunal not in self.TRIBUNAL_URLS:
            logger.warning(f"Tribunal {tribunal} não suportado no e-SAJ")
            return []
        
        try:
            base_url = self.TRIBUNAL_URLS[tribunal]
            
            # Preparar documento (remover formatação)
            doc_clean = re.sub(r'[^\d]', '', documento)
            
            params = {
                'conversationId': '',
                'dadosConsulta.localPesquisa.cdLocal': '-1',
                'cbPesquisa': 'DOCPARTE',
                'dadosConsulta.tipoNuProcesso': 'UNIFICADO',
                'dadosConsulta.valorConsultaNuUnificado': '',
                'dadosConsulta.valorConsulta': doc_clean,
                'uuidCaptcha': ''
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AgroADB/1.0)',
                'Accept': 'text/html,application/xhtml+xml',
            }
            
            async with self.session.get(
                base_url,
                params=params,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    html = await response.text()
                    
                    # Parse HTML (seria melhor usar BeautifulSoup)
                    processes = self._parse_esaj_html(html, tribunal)
                    
                    logger.info(
                        f"✅ {tribunal}: {len(processes)} processos encontrados"
                    )
                    
                    return processes
                
                else:
                    logger.error(f"Erro {tribunal} {response.status}")
                    return []
        
        except Exception as e:
            logger.error(f"Erro ao consultar {tribunal}: {e}")
            return []
    
    def _parse_esaj_html(self, html: str, tribunal: str) -> List[StateCourtProcess]:
        """Parse HTML do e-SAJ (simplificado)"""
        processes = []
        
        # Regex simplificado para encontrar números de processo
        # Formato: NNNNNNN-DD.AAAA.J.TR.OOOO
        pattern = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
        matches = re.findall(pattern, html)
        
        for numero in matches:
            # Criar processo básico
            # Em produção, seria necessário parse mais completo
            process = StateCourtProcess(
                numero_processo=numero,
                tribunal=tribunal,
                sistema='ESAJ',
                classe='',
                assunto='',
                data_distribuicao=None,
                status='ATIVO',
                comarca='',
                vara='',
                partes=[],
                movimentacoes=[]
            )
            processes.append(process)
        
        return processes


class ProjudiIntegration:
    """
    Integração com Projudi
    
    Tribunais suportados:
    - TJPR (Paraná)
    - TJAC (Acre)
    - TJAM (Amazonas)
    - TJAP (Amapá)
    - TJBA (Bahia)
    - TJGO (Goiás)
    - TJMA (Maranhão)
    - TJMT (Mato Grosso)
    - TJPA (Pará)
    - TJPI (Piauí)
    - TJRN (Rio Grande do Norte)
    - TJRO (Rondônia)
    - TJRR (Roraima)
    - TJTO (Tocantins)
    """
    
    TRIBUNAL_URLS = {
        'TJPR': 'https://projudi.tjpr.jus.br/projudi/',
        'TJAC': 'https://projudi.tjac.jus.br/projudi/',
        'TJAM': 'https://projudi.tjam.jus.br/projudi/',
        'TJAP': 'https://projudi.tjap.jus.br/projudi/',
        'TJBA': 'https://projudi.tjba.jus.br/projudi/',
        'TJGO': 'https://projudi.tjgo.jus.br/projudi/',
        'TJMA': 'https://projudi.tjma.jus.br/projudi/',
        'TJMT': 'https://projudi.tjmt.jus.br/projudi/',
        'TJPA': 'https://projudi.tjpa.jus.br/projudi/',
        'TJPI': 'https://projudi.tjpi.jus.br/projudi/',
        'TJRN': 'https://projudi.tjrn.jus.br/projudi/',
        'TJRO': 'https://projudi.tjro.jus.br/projudi/',
        'TJRR': 'https://projudi.tjrr.jus.br/projudi/',
        'TJTO': 'https://projudi.tjto.jus.br/projudi/',
    }
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_processes(
        self,
        tribunal: str,
        documento: str
    ) -> List[StateCourtProcess]:
        """Busca processos no Projudi"""
        
        if tribunal not in self.TRIBUNAL_URLS:
            logger.warning(f"Tribunal {tribunal} não suportado no Projudi")
            return []
        
        try:
            base_url = self.TRIBUNAL_URLS[tribunal]
            search_url = f"{base_url}consulta_publica/consulta_publica_principal.action"
            
            doc_clean = re.sub(r'[^\d]', '', documento)
            
            data = {
                'tipoConsulta': 'PARTE',
                'documento': doc_clean,
                'metodo': 'pesquisar'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AgroADB/1.0)',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            async with self.session.post(
                search_url,
                data=data,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    html = await response.text()
                    
                    processes = self._parse_projudi_html(html, tribunal)
                    
                    logger.info(
                        f"✅ {tribunal} (Projudi): {len(processes)} processos encontrados"
                    )
                    
                    return processes
                
                else:
                    logger.error(f"Erro Projudi {tribunal} {response.status}")
                    return []
        
        except Exception as e:
            logger.error(f"Erro ao consultar Projudi {tribunal}: {e}")
            return []
    
    def _parse_projudi_html(
        self,
        html: str,
        tribunal: str
    ) -> List[StateCourtProcess]:
        """Parse HTML do Projudi"""
        processes = []
        
        # Regex para número de processo Projudi
        # Formato pode variar por tribunal
        pattern = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
        matches = re.findall(pattern, html)
        
        for numero in matches:
            process = StateCourtProcess(
                numero_processo=numero,
                tribunal=tribunal,
                sistema='Projudi',
                classe='',
                assunto='',
                data_distribuicao=None,
                status='ATIVO',
                comarca='',
                vara='',
                partes=[],
                movimentacoes=[]
            )
            processes.append(process)
        
        return processes


class UnifiedStateCourtSearch:
    """
    Busca unificada em todos os tribunais estaduais
    """
    
    @classmethod
    async def search_all_tribunals(
        cls,
        documento: str,
        tribunais: Optional[List[str]] = None
    ) -> Dict[str, List[StateCourtProcess]]:
        """
        Busca em todos os tribunais (ou lista específica)
        
        Args:
            documento: CPF ou CNPJ
            tribunais: Lista opcional de tribunais (ex: ['TJSP', 'TJMG'])
                      Se None, busca em todos
        
        Returns:
            Dict com tribunal -> processos encontrados
        """
        
        results = {}
        
        # Tribunais com e-SAJ
        esaj_tribunals = ['TJSP', 'TJSC', 'TJAL', 'TJCE', 'TJMS']
        
        # Tribunais com Projudi
        projudi_tribunals = [
            'TJPR', 'TJAC', 'TJAM', 'TJAP', 'TJBA', 'TJGO',
            'TJMA', 'TJMT', 'TJPA', 'TJPI', 'TJRN', 'TJRO',
            'TJRR', 'TJTO'
        ]
        
        # Filtrar tribunais se especificado
        if tribunais:
            esaj_tribunals = [t for t in esaj_tribunals if t in tribunais]
            projudi_tribunals = [t for t in projudi_tribunals if t in tribunais]
        
        # Buscar em e-SAJ
        async with ESAJIntegration() as esaj:
            for tribunal in esaj_tribunals:
                try:
                    processes = await esaj.search_processes(tribunal, documento)
                    if processes:
                        results[tribunal] = processes
                except Exception as e:
                    logger.error(f"Erro ao buscar {tribunal}: {e}")
        
        # Buscar em Projudi
        async with ProjudiIntegration() as projudi:
            for tribunal in projudi_tribunals:
                try:
                    processes = await projudi.search_processes(tribunal, documento)
                    if processes:
                        results[tribunal] = processes
                except Exception as e:
                    logger.error(f"Erro ao buscar {tribunal}: {e}")
        
        total_processes = sum(len(procs) for procs in results.values())
        logger.info(
            f"✅ Busca unificada concluída: {total_processes} processos "
            f"em {len(results)} tribunais"
        )
        
        return results
