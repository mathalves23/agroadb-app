"""
Integração com e-SAJ (Tribunais Estaduais)
Sistema unificado usado por vários estados: SP, GO, MS, SC, AL, CE, entre outros
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class ESAJProcess:
    """Processo do e-SAJ"""
    numero_processo: str
    tribunal: str
    grau: str  # 1G, 2G
    classe: str
    assunto: str
    area: str
    data_distribuicao: Optional[datetime]
    status: str
    comarca: str
    foro: str
    vara: str
    juiz: str
    valor_acao: Optional[float]
    partes: List[Dict[str, str]]
    movimentacoes: List[Dict]
    url: str


class ESAJService:
    """
    Serviço de integração com e-SAJ
    
    Tribunais suportados:
    - TJSP (São Paulo)
    - TJGO (Goiás)
    - TJMS (Mato Grosso do Sul)
    - TJSC (Santa Catarina)
    - TJAL (Alagoas)
    - TJCE (Ceará)
    """
    
    # URLs dos tribunais - 1º Grau
    TRIBUNAL_URLS_1G = {
        'tjsp': 'https://esaj.tjsp.jus.br/cpopg/open.do',
        'tjgo': 'https://projudi.tjgo.jus.br/cpopg/open.do',
        'tjms': 'https://esaj.tjms.jus.br/cpopg/open.do',
        'tjsc': 'https://esaj.tjsc.jus.br/cpopg/open.do',
        'tjal': 'https://www2.tjal.jus.br/cpopg/open.do',
        'tjce': 'https://esaj.tjce.jus.br/cpopg/open.do',
    }
    
    # URLs dos tribunais - 2º Grau
    TRIBUNAL_URLS_2G = {
        'tjsp': 'https://esaj.tjsp.jus.br/cposg/open.do',
        'tjgo': 'https://projudi.tjgo.jus.br/cposg/open.do',
        'tjms': 'https://esaj.tjms.jus.br/cposg/open.do',
        'tjsc': 'https://esaj.tjsc.jus.br/cposg/open.do',
        'tjal': 'https://www2.tjal.jus.br/cposg/open.do',
        'tjce': 'https://esaj.tjce.jus.br/cposg/open.do',
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
    
    async def consultar_processos_1g(
        self,
        cpf_cnpj: str,
        tribunal: str = 'tjsp'
    ) -> List[ESAJProcess]:
        """
        Consulta processos de 1º Grau
        
        Args:
            cpf_cnpj: CPF ou CNPJ (com ou sem formatação)
            tribunal: Código do tribunal (tjsp, tjgo, tjms, etc)
        
        Returns:
            Lista de processos encontrados
        """
        
        tribunal_lower = tribunal.lower()
        
        if tribunal_lower not in self.TRIBUNAL_URLS_1G:
            logger.warning(f"Tribunal {tribunal} não suportado no e-SAJ 1ºG")
            return []
        
        try:
            url = self.TRIBUNAL_URLS_1G[tribunal_lower]
            
            # Limpar documento
            doc_clean = re.sub(r'[^\d]', '', cpf_cnpj)
            
            # Tentar primeiro com requisição HTTP simples
            processes = await self._search_http(url, doc_clean, tribunal_lower, '1G')
            
            # Se não funcionar, usar Selenium
            if not processes:
                logger.info(f"Tentando busca com Selenium em {tribunal_lower} 1ºG")
                processes = await self._search_selenium(url, doc_clean, tribunal_lower, '1G')
            
            logger.info(
                f"✅ {tribunal.upper()} 1ºG: {len(processes)} processos encontrados"
            )
            
            return processes
        
        except Exception as e:
            logger.error(f"Erro ao consultar {tribunal} 1ºG: {e}")
            return []
    
    async def consultar_processos_2g(
        self,
        cpf_cnpj: str,
        tribunal: str = 'tjsp'
    ) -> List[ESAJProcess]:
        """
        Consulta processos de 2º Grau
        
        Args:
            cpf_cnpj: CPF ou CNPJ (com ou sem formatação)
            tribunal: Código do tribunal (tjsp, tjgo, tjms, etc)
        
        Returns:
            Lista de processos encontrados
        """
        
        tribunal_lower = tribunal.lower()
        
        if tribunal_lower not in self.TRIBUNAL_URLS_2G:
            logger.warning(f"Tribunal {tribunal} não suportado no e-SAJ 2ºG")
            return []
        
        try:
            url = self.TRIBUNAL_URLS_2G[tribunal_lower]
            
            # Limpar documento
            doc_clean = re.sub(r'[^\d]', '', cpf_cnpj)
            
            # Tentar primeiro com requisição HTTP simples
            processes = await self._search_http(url, doc_clean, tribunal_lower, '2G')
            
            # Se não funcionar, usar Selenium
            if not processes:
                logger.info(f"Tentando busca com Selenium em {tribunal_lower} 2ºG")
                processes = await self._search_selenium(url, doc_clean, tribunal_lower, '2G')
            
            logger.info(
                f"✅ {tribunal.upper()} 2ºG: {len(processes)} processos encontrados"
            )
            
            return processes
        
        except Exception as e:
            logger.error(f"Erro ao consultar {tribunal} 2ºG: {e}")
            return []
    
    async def _search_http(
        self,
        url: str,
        documento: str,
        tribunal: str,
        grau: str
    ) -> List[ESAJProcess]:
        """Busca usando requisição HTTP direta"""
        
        try:
            params = {
                'conversationId': '',
                'dadosConsulta.localPesquisa.cdLocal': '-1',
                'cbPesquisa': 'DOCPARTE',
                'dadosConsulta.tipoNuProcesso': 'UNIFICADO',
                'dadosConsulta.valorConsultaNuUnificado': '',
                'dadosConsulta.valorConsulta': documento,
                'uuidCaptcha': ''
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            }
            
            async with self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=30,
                allow_redirects=True
            ) as response:
                
                if response.status == 200:
                    html = await response.text()
                    
                    # Parse HTML
                    processes = self._parse_esaj_html(html, tribunal, grau, url)
                    
                    return processes
                
                else:
                    logger.warning(f"HTTP {response.status} ao buscar {tribunal} {grau}")
                    return []
        
        except Exception as e:
            logger.warning(f"Erro na busca HTTP {tribunal} {grau}: {e}")
            return []
    
    async def _search_selenium(
        self,
        url: str,
        documento: str,
        tribunal: str,
        grau: str
    ) -> List[ESAJProcess]:
        """Busca usando Selenium (para sites com JavaScript/captcha)"""
        
        def _selenium_search():
            """Execução síncrona do Selenium"""
            try:
                # Configurar Chrome headless
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
                
                driver = webdriver.Chrome(options=chrome_options)
                
                try:
                    # Acessar página
                    driver.get(url)
                    
                    # Aguardar carregamento
                    wait = WebDriverWait(driver, 10)
                    
                    # Selecionar tipo de busca por documento
                    try:
                        select_pesquisa = wait.until(
                            EC.presence_of_element_located((By.ID, "cbPesquisa"))
                        )
                        select_pesquisa.send_keys("DOCPARTE")
                    except:
                        logger.warning("Campo de seleção de pesquisa não encontrado")
                    
                    # Preencher campo de documento
                    try:
                        campo_doc = driver.find_element(By.ID, "dadosConsulta.valorConsulta")
                        campo_doc.clear()
                        campo_doc.send_keys(documento)
                    except NoSuchElementException:
                        logger.error("Campo de documento não encontrado")
                        return []
                    
                    # Clicar no botão de pesquisa
                    try:
                        btn_pesquisar = driver.find_element(By.ID, "pbEnviar")
                        btn_pesquisar.click()
                    except NoSuchElementException:
                        logger.error("Botão de pesquisa não encontrado")
                        return []
                    
                    # Aguardar resultados
                    try:
                        wait.until(
                            EC.presence_of_element_located((By.CLASS_NAME, "esajTable"))
                        )
                    except TimeoutException:
                        logger.info("Nenhum resultado encontrado")
                        return []
                    
                    # Obter HTML da página de resultados
                    html = driver.page_source
                    
                    # Parse HTML
                    processes = self._parse_esaj_html(html, tribunal, grau, url)
                    
                    return processes
                
                finally:
                    driver.quit()
            
            except Exception as e:
                logger.error(f"Erro no Selenium: {e}")
                return []
        
        # Executar Selenium em thread separada
        loop = asyncio.get_event_loop()
        processes = await loop.run_in_executor(self.executor, _selenium_search)
        
        return processes
    
    def _parse_esaj_html(
        self,
        html: str,
        tribunal: str,
        grau: str,
        url: str
    ) -> List[ESAJProcess]:
        """Parse HTML do e-SAJ usando BeautifulSoup"""
        
        processes = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Encontrar tabelas de processos
            tables = soup.find_all('table', class_='esajTable')
            
            for table in tables:
                # Extrair número do processo
                numero_match = re.search(
                    r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}',
                    table.get_text()
                )
                
                if not numero_match:
                    continue
                
                numero_processo = numero_match.group(0)
                
                # Extrair outras informações
                rows = table.find_all('tr')
                
                data_dict = {}
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        data_dict[label] = value
                
                # Extrair partes
                partes = []
                partes_section = soup.find('table', id=re.compile(r'tablePartes'))
                if partes_section:
                    parte_rows = partes_section.find_all('tr')
                    for pr in parte_rows:
                        parte_text = pr.get_text(strip=True)
                        if ':' in parte_text:
                            tipo, nome = parte_text.split(':', 1)
                            partes.append({
                                'tipo': tipo.strip(),
                                'nome': nome.strip()
                            })
                
                # Extrair movimentações
                movimentacoes = []
                mov_section = soup.find('table', id=re.compile(r'tabelaMovimentacoes'))
                if mov_section:
                    mov_rows = mov_section.find_all('tr')
                    for mr in mov_rows:
                        cells = mr.find_all('td')
                        if len(cells) >= 2:
                            movimentacoes.append({
                                'data': cells[0].get_text(strip=True),
                                'descricao': cells[1].get_text(strip=True)
                            })
                
                # Criar objeto do processo
                process = ESAJProcess(
                    numero_processo=numero_processo,
                    tribunal=tribunal.upper(),
                    grau=grau,
                    classe=data_dict.get('Classe:', data_dict.get('Classe', '')),
                    assunto=data_dict.get('Assunto:', data_dict.get('Assunto', '')),
                    area=data_dict.get('Área:', data_dict.get('Área', '')),
                    data_distribuicao=self._parse_date(
                        data_dict.get('Distribuído em:', data_dict.get('Distribuição', ''))
                    ),
                    status=data_dict.get('Status:', data_dict.get('Situação', 'ATIVO')),
                    comarca=data_dict.get('Comarca:', data_dict.get('Comarca', '')),
                    foro=data_dict.get('Foro:', data_dict.get('Foro', '')),
                    vara=data_dict.get('Vara:', data_dict.get('Vara', '')),
                    juiz=data_dict.get('Juiz:', data_dict.get('Juiz', '')),
                    valor_acao=self._parse_valor(
                        data_dict.get('Valor da ação:', data_dict.get('Valor', ''))
                    ),
                    partes=partes,
                    movimentacoes=movimentacoes[:10],  # Últimas 10 movimentações
                    url=url
                )
                
                processes.append(process)
        
        except Exception as e:
            logger.error(f"Erro ao parsear HTML do e-SAJ: {e}")
        
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
    
    def _parse_valor(self, valor_str: str) -> Optional[float]:
        """Parse valor monetário"""
        if not valor_str:
            return None
        
        try:
            # Remover R$, pontos e trocar vírgula por ponto
            valor_clean = re.sub(r'[R$\s]', '', valor_str)
            valor_clean = valor_clean.replace('.', '').replace(',', '.')
            return float(valor_clean)
        except:
            return None
