"""
Integração com Tribunais Estaduais

Suporta consulta de processos judiciais em:
- ESAJ (SP, PR, SC, RS e outros)
- Projudi (vários estados)
- PJe 2.0 (sistema unificado)
- Outros sistemas estaduais
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import httpx
from bs4 import BeautifulSoup
import re
import asyncio

logger = logging.getLogger(__name__)


class TribunalConfig:
    """Configuração dos sistemas de tribunais"""
    
    # ESAJ - Estados que usam o sistema ESAJ
    ESAJ_STATES = {
        "SP": "https://esaj.tjsp.jus.br",
        "PR": "https://esaj.tjpr.jus.br",
        "SC": "https://esaj.tjsc.jus.br",
        "RS": "https://esaj.tjrs.jus.br",
        "AC": "https://esaj.tjac.jus.br",
        "AL": "https://esaj.tjal.jus.br",
        "AP": "https://esaj.tjap.jus.br",
        "AM": "https://esaj.tjam.jus.br",
        "BA": "https://esaj.tjba.jus.br",
        "CE": "https://esaj.tjce.jus.br",
        "ES": "https://esaj.tjes.jus.br",
        "GO": "https://esaj.tjgo.jus.br",
        "MA": "https://esaj.tjma.jus.br",
        "MT": "https://esaj.tjmt.jus.br",
        "MS": "https://esaj.tjms.jus.br",
        "MG": "https://esaj.tjmg.jus.br",
        "PA": "https://esaj.tjpa.jus.br",
        "PB": "https://esaj.tjpb.jus.br",
        "PE": "https://esaj.tjpe.jus.br",
        "PI": "https://esaj.tjpi.jus.br",
        "RJ": "https://esaj.tjrj.jus.br",
        "RN": "https://esaj.tjrn.jus.br",
        "RO": "https://esaj.tjro.jus.br",
        "RR": "https://esaj.tjrr.jus.br",
        "SE": "https://esaj.tjse.jus.br",
        "TO": "https://esaj.tjto.jus.br",
    }
    
    # Projudi - Estados que usam Projudi
    PROJUDI_STATES = {
        "PR": "https://projudi.tjpr.jus.br",
        "SC": "https://projudi.tjsc.jus.br",
        "RS": "https://projudi.tjrs.jus.br",
        "MS": "https://projudi.tjms.jus.br",
        "MT": "https://projudi.tjmt.jus.br",
        "RO": "https://projudi.tjro.jus.br",
        "AC": "https://projudi.tjac.jus.br",
    }
    
    # PJe - Processo Judicial Eletrônico (nacional)
    PJE_URL = "https://pje.jus.br"
    
    TIMEOUT = 30.0


class ProcessResult:
    """Resultado da consulta de processo"""
    
    def __init__(
        self,
        process_number: str,
        state: str,
        system: str,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        self.process_number = process_number
        self.state = state
        self.system = system
        self.success = success
        self.data = data or {}
        self.error = error
        self.queried_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "process_number": self.process_number,
            "state": self.state,
            "system": self.system,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "queried_at": self.queried_at.isoformat()
        }


class TribunalIntegration:
    """
    Integração unificada com tribunais estaduais
    
    Suporta:
    - ESAJ (25+ estados)
    - Projudi (7 estados)
    - PJe 2.0 (nacional)
    """
    
    def __init__(self, timeout: float = TribunalConfig.TIMEOUT):
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
    
    async def query_process(
        self,
        process_number: str,
        state: str,
        system: Optional[str] = None
    ) -> ProcessResult:
        """
        Consulta processo judicial
        
        Args:
            process_number: Número do processo (ex: "0001234-56.2023.8.26.0100")
            state: Estado (sigla)
            system: Sistema específico ("esaj", "projudi", "pje") ou None (auto)
            
        Returns:
            ProcessResult com dados do processo
        """
        process_number = self._normalize_process_number(process_number)
        state = state.upper()
        
        logger.info(f"Consultando processo {process_number} em {state}")
        
        try:
            # Determinar sistema a usar
            if not system:
                system = self._detect_system(state)
            
            # Consultar no sistema apropriado
            if system == "esaj":
                result = await self._query_esaj(process_number, state)
            elif system == "projudi":
                result = await self._query_projudi(process_number, state)
            elif system == "pje":
                result = await self._query_pje(process_number)
            else:
                return ProcessResult(
                    process_number=process_number,
                    state=state,
                    system=system,
                    success=False,
                    error=f"Sistema '{system}' não suportado"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao consultar processo: {str(e)}")
            return ProcessResult(
                process_number=process_number,
                state=state,
                system=system or "unknown",
                success=False,
                error=str(e)
            )
    
    async def query_multiple_processes(
        self,
        processes: List[Dict[str, str]]
    ) -> List[ProcessResult]:
        """
        Consulta múltiplos processos simultaneamente
        
        Args:
            processes: Lista de dicts {"number": "...", "state": "...", "system": "..."}
        """
        tasks = [
            self.query_process(
                p["number"],
                p["state"],
                p.get("system")
            )
            for p in processes
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Converter exceções em resultados
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                proc = processes[i]
                final_results.append(ProcessResult(
                    process_number=proc["number"],
                    state=proc["state"],
                    system=proc.get("system", "unknown"),
                    success=False,
                    error=str(result)
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def _query_esaj(
        self,
        process_number: str,
        state: str
    ) -> ProcessResult:
        """Consulta processo no ESAJ"""
        
        if state not in TribunalConfig.ESAJ_STATES:
            return ProcessResult(
                process_number=process_number,
                state=state,
                system="esaj",
                success=False,
                error=f"Estado {state} não tem ESAJ"
            )
        
        base_url = TribunalConfig.ESAJ_STATES[state]
        
        # URL de consulta pública (1º grau)
        url = f"{base_url}/cpopg/search.do"
        
        # Parâmetros da busca
        params = {
            "conversationId": "",
            "dadosConsulta.localPesquisa.cdLocal": "-1",
            "cbPesquisa": "NUMPROC",
            "dadosConsulta.tipoNuProcesso": "UNIFICADO",
            "numeroDigitoAnoUnificado": process_number[:15],
            "foroNumeroUnificado": process_number[16:20] if len(process_number) > 16 else "",
            "dadosConsulta.valorConsultaNuUnificado": process_number,
            "dadosConsulta.valorConsulta": "",
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Verificar se encontrou o processo
            error_div = soup.find('div', class_='mensagemErro')
            if error_div and 'não encontrado' in error_div.text.lower():
                return ProcessResult(
                    process_number=process_number,
                    state=state,
                    system="esaj",
                    success=False,
                    error="Processo não encontrado"
                )
            
            # Extrair dados do processo
            data = self._parse_esaj_page(soup)
            data['process_number'] = process_number
            data['state'] = state
            
            return ProcessResult(
                process_number=process_number,
                state=state,
                system="esaj",
                success=True,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Erro ao consultar ESAJ {state}: {str(e)}")
            raise
    
    async def _query_projudi(
        self,
        process_number: str,
        state: str
    ) -> ProcessResult:
        """Consulta processo no Projudi"""
        
        if state not in TribunalConfig.PROJUDI_STATES:
            return ProcessResult(
                process_number=process_number,
                state=state,
                system="projudi",
                success=False,
                error=f"Estado {state} não tem Projudi"
            )
        
        base_url = TribunalConfig.PROJUDI_STATES[state]
        url = f"{base_url}/publico/consulta"
        
        try:
            # Projudi requer POST
            data = {
                "numeroProcesso": process_number,
                "tipoConsulta": "completa"
            }
            
            response = await self.client.post(url, data=data)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse página Projudi
            process_data = self._parse_projudi_page(soup)
            process_data['process_number'] = process_number
            process_data['state'] = state
            
            if not process_data:
                return ProcessResult(
                    process_number=process_number,
                    state=state,
                    system="projudi",
                    success=False,
                    error="Processo não encontrado"
                )
            
            return ProcessResult(
                process_number=process_number,
                state=state,
                system="projudi",
                success=True,
                data=process_data
            )
            
        except Exception as e:
            logger.error(f"Erro ao consultar Projudi {state}: {str(e)}")
            raise
    
    async def _query_pje(
        self,
        process_number: str
    ) -> ProcessResult:
        """Consulta processo no PJe (nacional)"""
        
        url = f"{TribunalConfig.PJE_URL}/consultapublica"
        
        try:
            params = {"numeroProcesso": process_number}
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse PJe
            data = self._parse_pje_page(soup)
            data['process_number'] = process_number
            
            if not data:
                return ProcessResult(
                    process_number=process_number,
                    state="BR",  # Nacional
                    system="pje",
                    success=False,
                    error="Processo não encontrado"
                )
            
            return ProcessResult(
                process_number=process_number,
                state="BR",
                system="pje",
                success=True,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Erro ao consultar PJe: {str(e)}")
            raise
    
    def _parse_esaj_page(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse da página ESAJ"""
        data = {}
        
        try:
            # Classe do processo
            classe_elem = soup.find('span', id='classeProcesso')
            if classe_elem:
                data['class'] = classe_elem.text.strip()
            
            # Assunto
            assunto_elem = soup.find('span', id='assuntoProcesso')
            if assunto_elem:
                data['subject'] = assunto_elem.text.strip()
            
            # Juiz
            juiz_elem = soup.find('span', id='juizProcesso')
            if juiz_elem:
                data['judge'] = juiz_elem.text.strip()
            
            # Valor da ação
            valor_elem = soup.find('span', id='valorAcaoProcesso')
            if valor_elem:
                valor_text = valor_elem.text.strip().replace('.', '').replace(',', '.')
                try:
                    data['value'] = float(re.sub(r'[^\d.]', '', valor_text))
                except:
                    pass
            
            # Área
            area_elem = soup.find('div', id='areaProcesso')
            if area_elem:
                data['area'] = area_elem.text.strip()
            
            # Distribuição
            dist_elem = soup.find('div', id='dataHoraDistribuicaoProcesso')
            if dist_elem:
                data['distribution_date'] = dist_elem.text.strip()
            
            # Partes
            partes = []
            partes_section = soup.find('table', id='tableTodasPartes')
            if partes_section:
                rows = partes_section.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        tipo = cols[0].text.strip()
                        nome = cols[1].text.strip()
                        partes.append({"type": tipo, "name": nome})
            
            data['parties'] = partes
            
            # Movimentações (últimas 10)
            movimentacoes = []
            mov_section = soup.find('table', id='tabelaTodasMovimentacoes')
            if mov_section:
                rows = mov_section.find_all('tr', limit=10)
                for row in rows:
                    date_elem = row.find('td', class_='dataMovimentacao')
                    desc_elem = row.find('td', class_='descricaoMovimentacao')
                    
                    if date_elem and desc_elem:
                        movimentacoes.append({
                            "date": date_elem.text.strip(),
                            "description": desc_elem.text.strip()
                        })
            
            data['movements'] = movimentacoes
            
        except Exception as e:
            logger.warning(f"Erro ao fazer parse ESAJ: {str(e)}")
        
        return data
    
    def _parse_projudi_page(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse da página Projudi"""
        data = {}
        
        try:
            # Estratégia genérica para Projudi
            # (cada estado tem layout um pouco diferente)
            
            # Buscar por labels comuns
            for label in ['Classe', 'Assunto', 'Juiz', 'Valor', 'Área']:
                elem = soup.find(text=re.compile(label, re.IGNORECASE))
                if elem and elem.find_next('span'):
                    data[label.lower()] = elem.find_next('span').text.strip()
            
            # Partes
            partes = []
            partes_div = soup.find('div', {'class': lambda x: x and 'parte' in x.lower()})
            if partes_div:
                items = partes_div.find_all('div', limit=20)
                for item in items:
                    text = item.text.strip()
                    if ':' in text:
                        tipo, nome = text.split(':', 1)
                        partes.append({"type": tipo.strip(), "name": nome.strip()})
            
            data['parties'] = partes
            
        except Exception as e:
            logger.warning(f"Erro ao fazer parse Projudi: {str(e)}")
        
        return data
    
    def _parse_pje_page(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse da página PJe"""
        data = {}
        
        try:
            # PJe tem estrutura mais consistente
            fields = {
                'class': 'classeProcesso',
                'subject': 'assuntoProcesso',
                'judge': 'juizProcesso',
                'court': 'orgaoJulgador',
                'distribution_date': 'dataDistribuicao'
            }
            
            for key, field_id in fields.items():
                elem = soup.find(id=field_id)
                if elem:
                    data[key] = elem.text.strip()
        
        except Exception as e:
            logger.warning(f"Erro ao fazer parse PJe: {str(e)}")
        
        return data
    
    def _normalize_process_number(self, number: str) -> str:
        """Normaliza número do processo"""
        # Remove caracteres não numéricos
        clean = re.sub(r'[^\d]', '', number)
        
        # Formato CNJ: 0000000-00.0000.0.00.0000
        if len(clean) == 20:
            return f"{clean[:7]}-{clean[7:9]}.{clean[9:13]}.{clean[13]}.{clean[14:16]}.{clean[16:]}"
        
        return number
    
    def _detect_system(self, state: str) -> str:
        """Detecta qual sistema o estado usa"""
        if state in TribunalConfig.ESAJ_STATES:
            return "esaj"
        elif state in TribunalConfig.PROJUDI_STATES:
            return "projudi"
        else:
            return "pje"
    
    async def close(self):
        """Fecha cliente HTTP"""
        await self.client.aclose()
    
    def __del__(self):
        """Cleanup"""
        try:
            asyncio.get_event_loop().run_until_complete(self.close())
        except:
            pass


# Funções de conveniência

async def query_process_by_number(
    process_number: str,
    state: str
) -> ProcessResult:
    """Consulta processo por número"""
    integration = TribunalIntegration()
    
    try:
        result = await integration.query_process(process_number, state)
        return result
    finally:
        await integration.close()


async def query_processes_by_cpf_cnpj(
    cpf_cnpj: str,
    states: Optional[List[str]] = None
) -> List[ProcessResult]:
    """
    Busca processos de um CPF/CNPJ em vários estados
    
    Nota: Requer consulta por nome (não apenas número)
    """
    # Esta função é complexa pois requer scraping mais avançado
    # Por ora retorna estrutura para implementação futura
    logger.warning("Busca por CPF/CNPJ requer implementação avançada")
    return []
