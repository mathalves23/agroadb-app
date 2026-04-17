"""
Serviço de Integração com IBAMA
Consulta embargos ambientais, CTF, autos de infração
"""
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


@dataclass
class IBAMAEmbargo:
    """Embargo ambiental do IBAMA"""
    numero_auto: str
    cpf_cnpj: str
    nome_autuado: str
    data_autuacao: str
    tipo_infracao: str
    descricao: str
    valor_multa: float
    municipio: str
    uf: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_embargada_ha: Optional[float] = None
    status: str = "ATIVO"
    

@dataclass
class IBAMACTFRegistro:
    """Registro no Cadastro Técnico Federal"""
    numero_ctf: str
    cpf_cnpj: str
    razao_social: str
    nome_fantasia: Optional[str]
    situacao: str
    data_vencimento: Optional[str]
    atividades: List[str]
    tipo_pessoa: str


@dataclass
class IBAMAAutoInfracao:
    """Auto de infração ambiental"""
    numero_auto: str
    serie: str
    data_lavratura: str
    cpf_cnpj_autuado: str
    nome_autuado: str
    tipo_infracao: str
    enquadramento_legal: str
    valor_auto: float
    municipio: str
    uf: str
    status: str


class IBAMAService:
    """
    Serviço de integração com IBAMA
    
    Funcionalidades:
    - Consulta de embargos ambientais
    - Verificação de CTF (Cadastro Técnico Federal)
    - Consulta de autos de infração
    - Verificação de áreas embargadas
    """
    
    # URLs dos serviços públicos do IBAMA
    BASE_URL = "https://servicos.ibama.gov.br"
    CTF_CONSULTA_URL = f"{BASE_URL}/ctf/publico/areasembargadas/ConsultaPublicaAreasEmbargadas.php"
    EMBARGOS_URL = f"{BASE_URL}/ctf/publico/areasembargadas/consulta.php"
    
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
    
    async def consultar_embargo(self, cpf_cnpj: str) -> List[IBAMAEmbargo]:
        """
        Consulta embargos ambientais por CPF/CNPJ
        
        Args:
            cpf_cnpj: CPF ou CNPJ (com ou sem formatação)
            
        Returns:
            Lista de embargos encontrados
        """
        try:
            # Limpar documento
            doc_clean = re.sub(r'[^\d]', '', cpf_cnpj)
            
            logger.info(f"Consultando embargos IBAMA para {cpf_cnpj}")
            
            # Dados para requisição
            params = {
                'tipoConsulta': 'cpfcnpj',
                'documento': doc_clean
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AgroADB/1.0)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            async with self.session.get(
                self.CTF_CONSULTA_URL,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status != 200:
                    logger.warning(f"IBAMA retornou status {response.status}")
                    return []
                
                html = await response.text()
                embargos = self._parse_embargos_html(html)
                
                logger.info(f"✅ IBAMA: {len(embargos)} embargo(s) encontrado(s)")
                
                return embargos
        
        except aiohttp.ClientError as e:
            logger.error(f"Erro de conexão com IBAMA: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro ao consultar embargos IBAMA: {e}")
            return []
    
    def _parse_embargos_html(self, html: str) -> List[IBAMAEmbargo]:
        """Faz parsing do HTML de resposta do IBAMA"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            embargos = []
            
            # Buscar tabela de resultados
            table = soup.find('table', {'class': ['resultado', 'table']})
            
            if not table:
                return []
            
            rows = table.find_all('tr')[1:]  # Pular cabeçalho
            
            for row in rows:
                cols = row.find_all('td')
                
                if len(cols) < 8:
                    continue
                
                try:
                    embargo = IBAMAEmbargo(
                        numero_auto=cols[0].text.strip(),
                        cpf_cnpj=cols[1].text.strip(),
                        nome_autuado=cols[2].text.strip(),
                        data_autuacao=cols[3].text.strip(),
                        tipo_infracao=cols[4].text.strip(),
                        descricao=cols[5].text.strip(),
                        valor_multa=self._parse_currency(cols[6].text.strip()),
                        municipio=cols[7].text.strip() if len(cols) > 7 else '',
                        uf=cols[8].text.strip() if len(cols) > 8 else '',
                        status=cols[9].text.strip() if len(cols) > 9 else 'ATIVO'
                    )
                    embargos.append(embargo)
                    
                except Exception as e:
                    logger.warning(f"Erro ao parsear linha de embargo: {e}")
                    continue
            
            return embargos
            
        except Exception as e:
            logger.error(f"Erro ao fazer parsing do HTML do IBAMA: {e}")
            return []
    
    async def consultar_ctf(self, cpf_cnpj: str) -> Optional[IBAMACTFRegistro]:
        """
        Consulta Cadastro Técnico Federal (CTF)
        
        Args:
            cpf_cnpj: CPF ou CNPJ
            
        Returns:
            Dados do CTF ou None se não encontrado
        """
        try:
            doc_clean = re.sub(r'[^\d]', '', cpf_cnpj)
            
            logger.info(f"Consultando CTF IBAMA para {cpf_cnpj}")
            
            # URL de consulta pública do CTF
            url = f"{self.BASE_URL}/ctf/publico/consulta_por_cpf_cnpj.php"
            
            params = {'documento': doc_clean}
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AgroADB/1.0)',
            }
            
            async with self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status != 200:
                    logger.warning(f"CTF IBAMA retornou status {response.status}")
                    return None
                
                html = await response.text()
                ctf = self._parse_ctf_html(html, cpf_cnpj)
                
                if ctf:
                    logger.info(f"✅ CTF encontrado: {ctf.numero_ctf}")
                else:
                    logger.info("CTF não encontrado")
                
                return ctf
        
        except Exception as e:
            logger.error(f"Erro ao consultar CTF: {e}")
            return None
    
    def _parse_ctf_html(self, html: str, cpf_cnpj: str) -> Optional[IBAMACTFRegistro]:
        """Parse do HTML da consulta de CTF"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Buscar informações do CTF
            numero_ctf_elem = soup.find(text=re.compile(r'N[úu]mero\s+CTF', re.I))
            if not numero_ctf_elem:
                return None
            
            # Extrair dados (estrutura varia, adaptar conforme necessário)
            numero_ctf = self._extract_next_value(numero_ctf_elem)
            razao_social = self._extract_field_value(soup, 'Razão Social')
            situacao = self._extract_field_value(soup, 'Situação')
            
            return IBAMACTFRegistro(
                numero_ctf=numero_ctf,
                cpf_cnpj=cpf_cnpj,
                razao_social=razao_social or 'N/A',
                nome_fantasia=self._extract_field_value(soup, 'Nome Fantasia'),
                situacao=situacao or 'DESCONHECIDO',
                data_vencimento=self._extract_field_value(soup, 'Vencimento'),
                atividades=[],
                tipo_pessoa='PF' if len(re.sub(r'[^\d]', '', cpf_cnpj)) == 11 else 'PJ'
            )
            
        except Exception as e:
            logger.warning(f"Erro ao fazer parsing do CTF: {e}")
            return None
    
    async def consultar_auto_infracao(self, numero_auto: str) -> Optional[IBAMAAutoInfracao]:
        """
        Consulta auto de infração específico
        
        Args:
            numero_auto: Número do auto de infração
            
        Returns:
            Dados do auto ou None
        """
        try:
            logger.info(f"Consultando auto de infração IBAMA: {numero_auto}")
            
            url = f"{self.BASE_URL}/ctf/publico/auto_infracao/consulta.php"
            
            params = {'numero_auto': numero_auto}
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AgroADB/1.0)',
            }
            
            async with self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status != 200:
                    return None
                
                html = await response.text()
                auto = self._parse_auto_infracao_html(html)
                
                if auto:
                    logger.info(f"✅ Auto de infração encontrado: {numero_auto}")
                
                return auto
        
        except Exception as e:
            logger.error(f"Erro ao consultar auto de infração: {e}")
            return None
    
    def _parse_auto_infracao_html(self, html: str) -> Optional[IBAMAAutoInfracao]:
        """Parse do auto de infração"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extrair campos do auto
            numero = self._extract_field_value(soup, 'Número do Auto')
            serie = self._extract_field_value(soup, 'Série')
            
            if not numero:
                return None
            
            return IBAMAAutoInfracao(
                numero_auto=numero,
                serie=serie or '',
                data_lavratura=self._extract_field_value(soup, 'Data') or '',
                cpf_cnpj_autuado=self._extract_field_value(soup, 'CPF/CNPJ') or '',
                nome_autuado=self._extract_field_value(soup, 'Nome') or '',
                tipo_infracao=self._extract_field_value(soup, 'Tipo') or '',
                enquadramento_legal=self._extract_field_value(soup, 'Enquadramento') or '',
                valor_auto=self._parse_currency(
                    self._extract_field_value(soup, 'Valor') or '0'
                ),
                municipio=self._extract_field_value(soup, 'Município') or '',
                uf=self._extract_field_value(soup, 'UF') or '',
                status=self._extract_field_value(soup, 'Status') or 'ATIVO'
            )
            
        except Exception as e:
            logger.warning(f"Erro ao parsear auto de infração: {e}")
            return None
    
    # Métodos auxiliares
    
    @staticmethod
    def _parse_currency(value: str) -> float:
        """Converte string monetária para float"""
        try:
            # Remove "R$", pontos e substitui vírgula por ponto
            clean = re.sub(r'[R$\s.]', '', value)
            clean = clean.replace(',', '.')
            return float(clean)
        except:
            return 0.0
    
    @staticmethod
    def _extract_next_value(element) -> str:
        """Extrai próximo valor após um elemento"""
        try:
            parent = element.parent
            next_sibling = parent.find_next_sibling()
            if next_sibling:
                return next_sibling.text.strip()
        except:
            pass
        return ''
    
    @staticmethod
    def _extract_field_value(soup: BeautifulSoup, field_name: str) -> Optional[str]:
        """Extrai valor de um campo por nome"""
        try:
            label = soup.find(text=re.compile(field_name, re.I))
            if label:
                parent = label.parent
                # Tentar próximo elemento
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.text.strip()
                # Tentar no mesmo elemento
                text = parent.text.replace(label, '').strip()
                return text if text else None
        except:
            pass
        return None
