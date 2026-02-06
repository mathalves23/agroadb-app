"""
Integração com PJe (Processo Judicial Eletrônico)
Sistema unificado da Justiça Federal e trabalhista
"""
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PJeProcess:
    """Processo do PJe"""
    numero_processo: str
    classe: str
    assunto: str
    data_autuacao: datetime
    status: str
    orgao_julgador: str
    partes: List[Dict[str, str]]
    movimentacoes: List[Dict]
    valor_causa: Optional[float]
    segredo_justica: bool


class PJeIntegration:
    """
    Integração com sistema PJe
    
    API: Consulta unificada CNJ
    Cobertura: Justiça Federal (TRF1-TRF5), Justiça do Trabalho (TRT)
    
    Tribunais Regionais Federais:
    - TRF1: AC, AM, AP, BA, DF, GO, MA, MG, MT, PA, PI, RO, RR, TO
    - TRF2: ES, RJ
    - TRF3: MS, SP
    - TRF4: PR, RS, SC
    - TRF5: AL, CE, PB, PE, RN, SE
    """
    
    BASE_URL = "https://www.cnj.jus.br/pjeconsulta/api/v1"
    
    # URLs específicas dos TRFs
    TRF_URLS = {
        'trf1': 'https://pje1g.trf1.jus.br/pje',
        'trf2': 'https://pje.trf2.jus.br/pje',
        'trf3': 'https://pje1g.trf3.jus.br/pje',
        'trf4': 'https://pje1g.trf4.jus.br/pje',
        'trf5': 'https://pje.trf5.jus.br/pje',
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PJE_API_KEY")
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_processes_by_cpf(
        self,
        cpf: str
    ) -> List[PJeProcess]:
        """Busca processos por CPF"""
        
        if not self.api_key:
            logger.warning("PJe API key não configurada")
            return []
        
        try:
            url = f"{self.BASE_URL}/processos/search"
            
            params = {
                'cpf': cpf,
                'tipo': 'parte'
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    processes = self._parse_processes(data.get('processos', []))
                    
                    logger.info(
                        f"✅ PJe: {len(processes)} processos encontrados para CPF {cpf}"
                    )
                    
                    return processes
                
                elif response.status == 404:
                    logger.info(f"PJe: Nenhum processo encontrado para CPF {cpf}")
                    return []
                
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Erro PJe {response.status}: {error_text}"
                    )
                    return []
        
        except Exception as e:
            logger.error(f"Erro ao consultar PJe: {e}")
            return []
    
    async def search_processes_by_cnpj(
        self,
        cnpj: str
    ) -> List[PJeProcess]:
        """Busca processos por CNPJ"""
        
        if not self.api_key:
            logger.warning("PJe API key não configurada")
            return []
        
        try:
            url = f"{self.BASE_URL}/processos/search"
            
            params = {
                'cnpj': cnpj,
                'tipo': 'parte'
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    processes = self._parse_processes(data.get('processos', []))
                    
                    logger.info(
                        f"✅ PJe: {len(processes)} processos encontrados para CNPJ {cnpj}"
                    )
                    
                    return processes
                
                else:
                    return []
        
        except Exception as e:
            logger.error(f"Erro ao consultar PJe: {e}")
            return []
    
    async def get_process_details(
        self,
        numero_processo: str
    ) -> Optional[PJeProcess]:
        """Busca detalhes de um processo específico"""
        
        if not self.api_key:
            return None
        
        try:
            url = f"{self.BASE_URL}/processos/{numero_processo}"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(
                url,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    process = self._parse_process(data)
                    
                    logger.info(f"✅ PJe: Detalhes do processo {numero_processo} obtidos")
                    
                    return process
                
                else:
                    return None
        
        except Exception as e:
            logger.error(f"Erro ao buscar processo PJe: {e}")
            return None
    
    def _parse_processes(self, processes_data: List[Dict]) -> List[PJeProcess]:
        """Parse lista de processos"""
        processes = []
        
        for proc_data in processes_data:
            try:
                process = self._parse_process(proc_data)
                processes.append(process)
            except Exception as e:
                logger.warning(f"Erro ao parsear processo: {e}")
                continue
        
        return processes
    
    def _parse_process(self, data: Dict) -> PJeProcess:
        """Parse dados de um processo"""
        
        # Data de autuação
        data_autuacao = None
        if data.get('dataAutuacao'):
            try:
                data_autuacao = datetime.fromisoformat(
                    data['dataAutuacao'].replace('Z', '+00:00')
                )
            except:
                pass
        
        # Valor da causa
        valor_causa = None
        if data.get('valorCausa'):
            try:
                valor_causa = float(data['valorCausa'])
            except:
                pass
        
        return PJeProcess(
            numero_processo=data.get('numeroProcesso', ''),
            classe=data.get('classe', ''),
            assunto=data.get('assunto', ''),
            data_autuacao=data_autuacao,
            status=data.get('status', 'DESCONHECIDO'),
            orgao_julgador=data.get('orgaoJulgador', ''),
            partes=data.get('partes', []),
            movimentacoes=data.get('movimentacoes', []),
            valor_causa=valor_causa,
            segredo_justica=data.get('segregoJustica', False)
        )
    
    async def consultar_todos_tribunais(
        self,
        cpf_cnpj: str
    ) -> Dict[str, List[PJeProcess]]:
        """
        Busca processos em todos os tribunais federais (TRF1-TRF5)
        
        Args:
            cpf_cnpj: CPF ou CNPJ
        
        Returns:
            Dicionário com tribunal -> lista de processos
        """
        
        if not self.api_key:
            logger.warning("PJe API key não configurada")
            return {}
        
        results = {}
        
        # Determinar tipo de documento
        doc_clean = ''.join(filter(str.isdigit, cpf_cnpj))
        is_cpf = len(doc_clean) == 11
        
        # Buscar em cada TRF
        for trf_code, trf_url in self.TRF_URLS.items():
            try:
                if is_cpf:
                    processes = await self.search_processes_by_cpf(cpf_cnpj)
                else:
                    processes = await self.search_processes_by_cnpj(cpf_cnpj)
                
                if processes:
                    results[trf_code.upper()] = processes
                    logger.info(f"✅ {trf_code.upper()}: {len(processes)} processos")
            
            except Exception as e:
                logger.error(f"Erro ao buscar em {trf_code.upper()}: {e}")
                continue
        
        total_processes = sum(len(procs) for procs in results.values())
        logger.info(
            f"✅ PJe: Busca completa - {total_processes} processos "
            f"em {len(results)} tribunais"
        )
        
        return results


import os
