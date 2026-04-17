"""
Integração com Projudi (Tribunais Estaduais)
Sistema usado por vários estados: MT, PR, SC, e outros
"""
import aiohttp
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class ProjudiProcess:
    """Processo do Projudi"""
    numero_processo: str
    tribunal: str
    classe: str
    assunto: str
    data_autuacao: Optional[datetime]
    status: str
    comarca: str
    vara: str
    partes: List[Dict[str, str]]
    movimentacoes: List[Dict]
    url: str


class ProjudiService:
    """
    Serviço de integração com Projudi
    
    Tribunais suportados:
    - TJMT (Mato Grosso)
    - TJPR (Paraná)
    - TJSC (Santa Catarina)
    - TJAC (Acre)
    - TJAM (Amazonas)
    - TJAP (Amapá)
    - TJBA (Bahia)
    - TJGO (Goiás)
    - TJMA (Maranhão)
    - TJPA (Pará)
    - TJPI (Piauí)
    - TJRN (Rio Grande do Norte)
    - TJRO (Rondônia)
    - TJRR (Roraima)
    - TJTO (Tocantins)
    """
    
    TRIBUNAL_URLS = {
        'tjmt': 'https://projudi.tjmt.jus.br/projudi/',
        'tjpr': 'https://projudi.tjpr.jus.br/projudi/',
        'tjsc': 'https://projudi.tjsc.jus.br/projudi/',
        'tjac': 'https://projudi.tjac.jus.br/projudi/',
        'tjam': 'https://projudi.tjam.jus.br/projudi/',
        'tjap': 'https://projudi.tjap.jus.br/projudi/',
        'tjba': 'https://projudi.tjba.jus.br/projudi/',
        'tjgo': 'https://projudi.tjgo.jus.br/projudi/',
        'tjma': 'https://projudi.tjma.jus.br/projudi/',
        'tjpa': 'https://projudi.tjpa.jus.br/projudi/',
        'tjpi': 'https://projudi.tjpi.jus.br/projudi/',
        'tjrn': 'https://projudi.tjrn.jus.br/projudi/',
        'tjro': 'https://projudi.tjro.jus.br/projudi/',
        'tjrr': 'https://projudi.tjrr.jus.br/projudi/',
        'tjto': 'https://projudi.tjto.jus.br/projudi/',
    }
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=True)
    
    async def consultar_processos(
        self,
        cpf_cnpj: str,
        tribunal: str = 'tjmt'
    ) -> List[ProjudiProcess]:
        """
        Consulta processos no Projudi
        
        Args:
            cpf_cnpj: CPF ou CNPJ (com ou sem formatação)
            tribunal: Código do tribunal (tjmt, tjpr, tjsc, etc)
        
        Returns:
            Lista de processos encontrados
        """
        
        tribunal_lower = tribunal.lower()
        
        if tribunal_lower not in self.TRIBUNAL_URLS:
            logger.warning(f"Tribunal {tribunal} não suportado no Projudi")
            return []
        
        try:
            base_url = self.TRIBUNAL_URLS[tribunal_lower]
            search_url = f"{base_url}consulta_publica/consulta_publica_principal.action"
            
            # Limpar documento
            doc_clean = re.sub(r'[^\d]', '', cpf_cnpj)
            
            # Tentar primeiro com requisição HTTP simples
            processes = await self._search_http(
                search_url, doc_clean, tribunal_lower, base_url
            )
            
            # Se não funcionar, usar Selenium
            if not processes:
                logger.info(f"Tentando busca com Selenium em {tribunal_lower}")
                processes = await self._search_selenium(
                    search_url, doc_clean, tribunal_lower, base_url
                )
            
            logger.info(
                f"✅ {tribunal.upper()} (Projudi): {len(processes)} processos encontrados"
            )
            
            return processes
        
        except Exception as e:
            logger.error(f"Erro ao consultar Projudi {tribunal}: {e}")
            return []
    
    async def _search_http(
        self,
        url: str,
        documento: str,
        tribunal: str,
        base_url: str
    ) -> List[ProjudiProcess]:
        """Busca usando requisição HTTP direta"""
        
        try:
            data = {
                'tipoConsulta': 'PARTE',
                'documento': documento,
                'metodo': 'pesquisar'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'pt-BR,pt;q=0.9',
            }
            
            async with self.session.post(
                url,
                data=data,
                headers=headers,
                timeout=30,
                allow_redirects=True
            ) as response:
                
                if response.status == 200:
                    html = await response.text()
                    
                    # Parse HTML
                    processes = self._parse_projudi_html(html, tribunal, base_url)
                    
                    return processes
                
                else:
                    logger.warning(f"HTTP {response.status} ao buscar Projudi {tribunal}")
                    return []
        
        except Exception as e:
            logger.warning(f"Erro na busca HTTP Projudi {tribunal}: {e}")
            return []
    
    async def _search_selenium(
        self,
        url: str,
        documento: str,
        tribunal: str,
        base_url: str
    ) -> List[ProjudiProcess]:
        """Busca usando Selenium (para sites com JavaScript)"""
        
        def _selenium_search():
            """Execução síncrona do Selenium"""
            try:
                # Configurar Chrome headless
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--user-agent=Mozilla/5.0')
                
                driver = webdriver.Chrome(options=chrome_options)
                
                try:
                    # Acessar página
                    driver.get(url)
                    
                    # Aguardar carregamento
                    wait = WebDriverWait(driver, 10)
                    
                    # Selecionar tipo de consulta por documento
                    try:
                        radio_parte = wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//input[@value='PARTE']")
                            )
                        )
                        radio_parte.click()
                    except:
                        logger.warning("Radio button PARTE não encontrado")
                    
                    # Preencher campo de documento
                    try:
                        campo_doc = driver.find_element(By.NAME, "documento")
                        campo_doc.clear()
                        campo_doc.send_keys(documento)
                    except:
                        logger.error("Campo de documento não encontrado")
                        return []
                    
                    # Clicar no botão de pesquisa
                    try:
                        btn_pesquisar = driver.find_element(
                            By.XPATH, "//input[@type='submit'][@value='Pesquisar']"
                        )
                        btn_pesquisar.click()
                    except:
                        logger.error("Botão de pesquisa não encontrado")
                        return []
                    
                    # Aguardar resultados
                    try:
                        wait.until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, "resultadoConsulta")
                            )
                        )
                    except TimeoutException:
                        logger.info("Nenhum resultado encontrado")
                        return []
                    
                    # Obter HTML da página de resultados
                    html = driver.page_source
                    
                    # Parse HTML
                    processes = self._parse_projudi_html(html, tribunal, base_url)
                    
                    return processes
                
                finally:
                    driver.quit()
            
            except Exception as e:
                logger.error(f"Erro no Selenium Projudi: {e}")
                return []
        
        # Executar Selenium em thread separada
        loop = asyncio.get_event_loop()
        processes = await loop.run_in_executor(self.executor, _selenium_search)
        
        return processes
    
    def _parse_projudi_html(
        self,
        html: str,
        tribunal: str,
        base_url: str
    ) -> List[ProjudiProcess]:
        """Parse HTML do Projudi usando BeautifulSoup"""
        
        processes = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Encontrar divs/tables de resultados
            results = soup.find_all('div', class_='resultadoConsulta')
            
            if not results:
                # Tentar encontrar tabelas
                results = soup.find_all('table', class_='tabelaConsulta')
            
            for result in results:
                result_text = result.get_text()
                
                # Extrair número do processo (vários formatos possíveis)
                numero_matches = re.findall(
                    r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}',
                    result_text
                )
                
                if not numero_matches:
                    # Tentar formato alternativo
                    numero_matches = re.findall(
                        r'\d{6,8}-?\d{2}\.?\d{4}',
                        result_text
                    )
                
                if not numero_matches:
                    continue
                
                numero_processo = numero_matches[0]
                
                # Extrair informações
                rows = result.find_all('tr')
                
                data_dict = {}
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        data_dict[label] = value
                
                # Extrair partes
                partes = []
                partes_text = result.find('div', class_='partes')
                if partes_text:
                    partes_lines = partes_text.get_text().split('\n')
                    for line in partes_lines:
                        if ':' in line:
                            tipo, nome = line.split(':', 1)
                            partes.append({
                                'tipo': tipo.strip(),
                                'nome': nome.strip()
                            })
                
                # Extrair movimentações
                movimentacoes = []
                mov_section = result.find('div', class_='movimentacoes')
                if mov_section:
                    mov_items = mov_section.find_all('div', class_='movimentacao')
                    for mov in mov_items[:10]:  # Últimas 10
                        movimentacoes.append({
                            'data': mov.find('span', class_='data').get_text(strip=True) if mov.find('span', class_='data') else '',
                            'descricao': mov.find('div', class_='texto').get_text(strip=True) if mov.find('div', class_='texto') else mov.get_text(strip=True)
                        })
                
                # Criar objeto do processo
                process = ProjudiProcess(
                    numero_processo=numero_processo,
                    tribunal=tribunal.upper(),
                    classe=data_dict.get('Classe:', data_dict.get('Classe', '')),
                    assunto=data_dict.get('Assunto:', data_dict.get('Assunto', '')),
                    data_autuacao=self._parse_date(
                        data_dict.get('Data Autuação:', data_dict.get('Autuação', ''))
                    ),
                    status=data_dict.get('Status:', data_dict.get('Situação', 'ATIVO')),
                    comarca=data_dict.get('Comarca:', data_dict.get('Comarca', '')),
                    vara=data_dict.get('Vara:', data_dict.get('Vara', '')),
                    partes=partes,
                    movimentacoes=movimentacoes,
                    url=base_url
                )
                
                processes.append(process)
        
        except Exception as e:
            logger.error(f"Erro ao parsear HTML do Projudi: {e}")
        
        return processes
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse data no formato dd/mm/yyyy"""
        if not date_str:
            return None
        
        try:
            # Extrair data do texto
            date_match = re.search(r'\d{2}/\d{2}/\d{4}', date_str)
            if date_match:
                return datetime.strptime(date_match.group(0), '%d/%m/%Y')
        except:
            pass
        
        return None
