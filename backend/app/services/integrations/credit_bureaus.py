"""
Integrações com Birôs de Crédito
Serasa Experian e Boa Vista SCPC
"""
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)


# ==================== SERASA ====================

@dataclass
class SerasaScore:
    """Score de crédito Serasa"""
    score: int  # 0-1000
    faixa: str  # MUITO BAIXO, BAIXO, MÉDIO, ALTO, MUITO ALTO
    probabilidade_inadimplencia: float  # 0-1
    data_consulta: datetime


@dataclass
class SerasaRestriction:
    """Restrição no Serasa"""
    tipo: str  # PROTESTO, CHEQUE SEM FUNDOS, ACAO JUDICIAL, DIVIDA VENCIDA
    credor: str
    valor: float
    data_ocorrencia: datetime
    cidade: str
    uf: str


@dataclass
class SerasaReport:
    """Relatório completo Serasa"""
    cpf_cnpj: str
    nome: str
    score: Optional[SerasaScore]
    restricoes: List[SerasaRestriction]
    protestos_quantidade: int
    protestos_valor_total: float
    acoes_quantidade: int
    acoes_valor_total: float
    cheques_quantidade: int
    dividas_quantidade: int
    dividas_valor_total: float
    participacao_empresas: List[Dict]
    consultas_ultimos_90_dias: int


class SerasaIntegration:
    """
    Integração com Serasa Experian
    
    Requer:
    - Conta empresarial Serasa
    - Contrato de uso da API
    - Credenciais de acesso
    
    Documentação: https://desenvolvedores.serasaexperian.com.br/
    """
    
    BASE_URL = "https://api.serasaexperian.com.br/consulta-credito/v1"
    AUTH_URL = "https://auth.serasaexperian.com.br/oauth2/token"
    
    def __init__(self):
        self.client_id = os.getenv("SERASA_CLIENT_ID")
        self.client_secret = os.getenv("SERASA_CLIENT_SECRET")
        self.access_token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self._authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _authenticate(self):
        """Autentica na API do Serasa"""
        
        if not self.client_id or not self.client_secret:
            logger.warning("Credenciais Serasa não configuradas")
            return
        
        try:
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            async with self.session.post(
                self.AUTH_URL,
                data=data,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    auth_data = await response.json()
                    self.access_token = auth_data.get('access_token')
                    
                    logger.info("✅ Autenticado no Serasa")
                
                else:
                    logger.error(f"Erro ao autenticar Serasa: {response.status}")
        
        except Exception as e:
            logger.error(f"Erro na autenticação Serasa: {e}")
    
    async def get_full_report(
        self,
        cpf_cnpj: str
    ) -> Optional[SerasaReport]:
        """Busca relatório completo de crédito"""
        
        if not self.access_token:
            logger.warning("Serasa não autenticado")
            return None
        
        try:
            url = f"{self.BASE_URL}/relatorio-completo"
            
            # Limpar documento
            doc_clean = ''.join(filter(str.isdigit, cpf_cnpj))
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'documento': doc_clean,
                'tipo': 'CPF' if len(doc_clean) == 11 else 'CNPJ'
            }
            
            async with self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    report = self._parse_serasa_report(data)
                    
                    logger.info(
                        f"✅ Serasa: Relatório obtido - "
                        f"Score: {report.score.score if report.score else 'N/A'}, "
                        f"{len(report.restricoes)} restrições"
                    )
                    
                    return report
                
                elif response.status == 404:
                    logger.info(f"Serasa: Documento {cpf_cnpj} não encontrado")
                    return None
                
                else:
                    error_text = await response.text()
                    logger.error(f"Erro Serasa {response.status}: {error_text}")
                    return None
        
        except Exception as e:
            logger.error(f"Erro ao consultar Serasa: {e}")
            return None
    
    async def get_score(self, cpf_cnpj: str) -> Optional[SerasaScore]:
        """Busca apenas o score de crédito"""
        
        if not self.access_token:
            return None
        
        try:
            url = f"{self.BASE_URL}/score"
            
            doc_clean = ''.join(filter(str.isdigit, cpf_cnpj))
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {'documento': doc_clean}
            
            async with self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    score = SerasaScore(
                        score=data.get('score', 0),
                        faixa=data.get('faixa', 'INDEFINIDO'),
                        probabilidade_inadimplencia=data.get(
                            'probabilidadeInadimplencia', 0.0
                        ),
                        data_consulta=datetime.now()
                    )
                    
                    logger.info(f"✅ Serasa Score: {score.score} ({score.faixa})")
                    
                    return score
                
                else:
                    return None
        
        except Exception as e:
            logger.error(f"Erro ao consultar Score Serasa: {e}")
            return None
    
    def _parse_serasa_report(self, data: Dict) -> SerasaReport:
        """Parse relatório do Serasa"""
        
        # Parse score
        score = None
        if data.get('score'):
            score = SerasaScore(
                score=data['score'].get('valor', 0),
                faixa=data['score'].get('faixa', ''),
                probabilidade_inadimplencia=data['score'].get(
                    'probabilidadeInadimplencia', 0.0
                ),
                data_consulta=datetime.now()
            )
        
        # Parse restrições
        restricoes = []
        for rest_data in data.get('restricoes', []):
            restricao = SerasaRestriction(
                tipo=rest_data.get('tipo', ''),
                credor=rest_data.get('credor', ''),
                valor=float(rest_data.get('valor', 0)),
                data_ocorrencia=self._parse_date(rest_data.get('dataOcorrencia')),
                cidade=rest_data.get('cidade', ''),
                uf=rest_data.get('uf', '')
            )
            restricoes.append(restricao)
        
        return SerasaReport(
            cpf_cnpj=data.get('documento', ''),
            nome=data.get('nome', ''),
            score=score,
            restricoes=restricoes,
            protestos_quantidade=data.get('protestos', {}).get('quantidade', 0),
            protestos_valor_total=data.get('protestos', {}).get('valorTotal', 0),
            acoes_quantidade=data.get('acoes', {}).get('quantidade', 0),
            acoes_valor_total=data.get('acoes', {}).get('valorTotal', 0),
            cheques_quantidade=data.get('cheques', {}).get('quantidade', 0),
            dividas_quantidade=data.get('dividas', {}).get('quantidade', 0),
            dividas_valor_total=data.get('dividas', {}).get('valorTotal', 0),
            participacao_empresas=data.get('participacaoEmpresas', []),
            consultas_ultimos_90_dias=data.get('consultasRecentes', 0)
        )
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse data do Serasa"""
        if not date_str:
            return datetime.now()
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.now()


# ==================== BOA VISTA ====================

@dataclass
class BoaVistaReport:
    """Relatório Boa Vista SCPC"""
    cpf_cnpj: str
    nome: str
    score: Optional[int]
    restricoes_financeiras: List[Dict]
    protestos: List[Dict]
    cheques_sem_fundo: List[Dict]
    acoes_judiciais: List[Dict]
    participacao_sociedades: List[Dict]
    consultas_recentes: int


class BoaVistaIntegration:
    """
    Integração com Boa Vista SCPC
    
    Requer:
    - Credenciamento Boa Vista
    - Contrato de uso da API
    - Certificado digital
    
    Documentação: https://developers.boavistaservicos.com.br/
    """
    
    BASE_URL = "https://api.boavistaservicos.com.br/v1"
    AUTH_URL = "https://auth.boavistaservicos.com.br/oauth2/token"
    
    def __init__(self):
        self.client_id = os.getenv("BOAVISTA_CLIENT_ID")
        self.client_secret = os.getenv("BOAVISTA_CLIENT_SECRET")
        self.access_token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self._authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _authenticate(self):
        """Autentica na API da Boa Vista"""
        
        if not self.client_id or not self.client_secret:
            logger.warning("Credenciais Boa Vista não configuradas")
            return
        
        try:
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            async with self.session.post(
                self.AUTH_URL,
                data=data,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    auth_data = await response.json()
                    self.access_token = auth_data.get('access_token')
                    
                    logger.info("✅ Autenticado na Boa Vista")
                
                else:
                    logger.error(f"Erro ao autenticar Boa Vista: {response.status}")
        
        except Exception as e:
            logger.error(f"Erro na autenticação Boa Vista: {e}")
    
    async def get_full_report(
        self,
        cpf_cnpj: str
    ) -> Optional[BoaVistaReport]:
        """Busca relatório completo"""
        
        if not self.access_token:
            logger.warning("Boa Vista não autenticada")
            return None
        
        try:
            url = f"{self.BASE_URL}/relatorio"
            
            doc_clean = ''.join(filter(str.isdigit, cpf_cnpj))
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'documento': doc_clean,
                'produto': 'RELATORIO_COMPLETO'
            }
            
            async with self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    report = BoaVistaReport(
                        cpf_cnpj=data.get('documento', ''),
                        nome=data.get('nome', ''),
                        score=data.get('score'),
                        restricoes_financeiras=data.get('restricoesFinanceiras', []),
                        protestos=data.get('protestos', []),
                        cheques_sem_fundo=data.get('chequesSemFundo', []),
                        acoes_judiciais=data.get('acoesJudiciais', []),
                        participacao_sociedades=data.get('participacaoSociedades', []),
                        consultas_recentes=data.get('consultasRecentes', 0)
                    )
                    
                    logger.info(
                        f"✅ Boa Vista: Relatório obtido - "
                        f"Score: {report.score or 'N/A'}"
                    )
                    
                    return report
                
                else:
                    logger.error(f"Erro Boa Vista {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Erro ao consultar Boa Vista: {e}")
            return None


# ==================== UNIFIED CREDIT SEARCH ====================

class UnifiedCreditSearch:
    """Busca unificada em todos os birôs"""
    
    @classmethod
    async def search_all_bureaus(
        cls,
        cpf_cnpj: str
    ) -> Dict:
        """Busca em Serasa e Boa Vista simultaneamente"""
        
        results = {
            'serasa': None,
            'boa_vista': None,
            'summary': {}
        }
        
        # Buscar Serasa
        try:
            async with SerasaIntegration() as serasa:
                serasa_report = await serasa.get_full_report(cpf_cnpj)
                results['serasa'] = serasa_report
        except Exception as e:
            logger.error(f"Erro ao buscar Serasa: {e}")
        
        # Buscar Boa Vista
        try:
            async with BoaVistaIntegration() as boavista:
                boavista_report = await boavista.get_full_report(cpf_cnpj)
                results['boa_vista'] = boavista_report
        except Exception as e:
            logger.error(f"Erro ao buscar Boa Vista: {e}")
        
        # Gerar resumo consolidado
        results['summary'] = cls._generate_summary(
            results['serasa'],
            results['boa_vista']
        )
        
        logger.info(f"✅ Busca unificada de crédito concluída para {cpf_cnpj}")
        
        return results
    
    @staticmethod
    def _generate_summary(
        serasa: Optional[SerasaReport],
        boavista: Optional[BoaVistaReport]
    ) -> Dict:
        """Gera resumo consolidado"""
        
        summary = {
            'score_medio': None,
            'total_restricoes': 0,
            'tem_protestos': False,
            'tem_acoes_judiciais': False,
            'tem_cheques_sem_fundo': False,
            'avaliacao': 'INDETERMINADO'
        }
        
        scores = []
        if serasa and serasa.score:
            scores.append(serasa.score.score)
            summary['total_restricoes'] += len(serasa.restricoes)
            summary['tem_protestos'] = serasa.protestos_quantidade > 0
            summary['tem_acoes_judiciais'] = serasa.acoes_quantidade > 0
            summary['tem_cheques_sem_fundo'] = serasa.cheques_quantidade > 0
        
        if boavista and boavista.score:
            scores.append(boavista.score)
            summary['total_restricoes'] += len(boavista.restricoes_financeiras)
            summary['tem_protestos'] = summary['tem_protestos'] or len(boavista.protestos) > 0
            summary['tem_acoes_judiciais'] = summary['tem_acoes_judiciais'] or len(boavista.acoes_judiciais) > 0
            summary['tem_cheques_sem_fundo'] = summary['tem_cheques_sem_fundo'] or len(boavista.cheques_sem_fundo) > 0
        
        if scores:
            summary['score_medio'] = int(sum(scores) / len(scores))
            
            # Avaliação baseada no score médio
            if summary['score_medio'] >= 800:
                summary['avaliacao'] = 'EXCELENTE'
            elif summary['score_medio'] >= 600:
                summary['avaliacao'] = 'BOM'
            elif summary['score_medio'] >= 400:
                summary['avaliacao'] = 'REGULAR'
            else:
                summary['avaliacao'] = 'RUIM'
        
        return summary
