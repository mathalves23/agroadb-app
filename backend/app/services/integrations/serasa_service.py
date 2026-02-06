"""
Integração com Serasa Experian
Consultas de crédito, score e restrições
"""
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import os

logger = logging.getLogger(__name__)


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
    origem: str


@dataclass
class SerasaConsulta:
    """Consulta recente no Serasa"""
    data: datetime
    empresa: str
    cnpj: str
    motivo: str


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
    cheques_valor_total: float
    dividas_quantidade: int
    dividas_valor_total: float
    participacao_empresas: List[Dict]
    consultas_ultimos_90_dias: int
    consultas_recentes: List[SerasaConsulta]
    data_consulta: datetime


class SerasaService:
    """
    Serviço de integração com Serasa Experian
    
    ATENÇÃO: Esta integração requer contrato comercial com a Serasa Experian.
    
    Requisitos:
    - Conta empresarial Serasa Experian
    - Contrato de uso da API de crédito
    - Client ID e Client Secret (credenciais OAuth2)
    
    Produtos disponíveis:
    - Score de Crédito
    - Consulta de Restrições
    - Histórico de Consultas
    - Relatório Completo
    
    Documentação: https://desenvolvedores.serasaexperian.com.br/
    """
    
    BASE_URL = "https://api.serasaexperian.com.br/consulta-credito/v1"
    AUTH_URL = "https://auth.serasaexperian.com.br/oauth2/token"
    
    def __init__(self):
        self.client_id = os.getenv("SERASA_CLIENT_ID")
        self.client_secret = os.getenv("SERASA_CLIENT_SECRET")
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self._authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _authenticate(self):
        """Autentica na API do Serasa usando OAuth2"""
        
        if not self.client_id or not self.client_secret:
            logger.warning("⚠️  Credenciais Serasa não configuradas")
            logger.info(
                "Configure SERASA_CLIENT_ID e SERASA_CLIENT_SECRET no .env"
            )
            return
        
        try:
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'consulta-credito'
            }
            
            async with self.session.post(
                self.AUTH_URL,
                data=data,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    auth_data = await response.json()
                    self.access_token = auth_data.get('access_token')
                    
                    # Calcular quando o token expira
                    expires_in = auth_data.get('expires_in', 3600)
                    self.token_expires_at = datetime.now().timestamp() + expires_in
                    
                    logger.info("✅ Autenticado no Serasa Experian")
                
                elif response.status == 401:
                    logger.error("❌ Credenciais Serasa inválidas")
                
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Erro ao autenticar Serasa: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Erro na autenticação Serasa: {e}")
    
    async def _ensure_authenticated(self):
        """Garante que o token está válido"""
        
        if not self.access_token:
            await self._authenticate()
            return
        
        # Verificar se token expirou
        if self.token_expires_at and datetime.now().timestamp() >= self.token_expires_at:
            logger.info("Token Serasa expirado, renovando...")
            await self._authenticate()
    
    async def consultar_score(
        self,
        cpf_cnpj: str
    ) -> Optional[SerasaScore]:
        """
        Consulta apenas o score de crédito
        
        Args:
            cpf_cnpj: CPF ou CNPJ (com ou sem formatação)
        
        Returns:
            Score ou None se não disponível
        """
        
        await self._ensure_authenticated()
        
        if not self.access_token:
            logger.warning("⚠️  Serasa não autenticado")
            return None
        
        try:
            url = f"{self.BASE_URL}/score"
            
            # Limpar documento
            doc_clean = ''.join(filter(str.isdigit, cpf_cnpj))
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
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
                    
                    score = SerasaScore(
                        score=data.get('score', 0),
                        faixa=data.get('faixa', 'INDEFINIDO'),
                        probabilidade_inadimplencia=data.get(
                            'probabilidadeInadimplencia', 0.0
                        ),
                        data_consulta=datetime.now()
                    )
                    
                    logger.info(
                        f"✅ Serasa Score: {score.score} ({score.faixa})"
                    )
                    
                    return score
                
                elif response.status == 404:
                    logger.info(f"Serasa: Documento {cpf_cnpj} não encontrado")
                    return None
                
                else:
                    error_text = await response.text()
                    logger.error(f"Erro Serasa Score {response.status}: {error_text}")
                    return None
        
        except Exception as e:
            logger.error(f"Erro ao consultar Score Serasa: {e}")
            return None
    
    async def consultar_restricoes(
        self,
        cpf_cnpj: str
    ) -> List[SerasaRestriction]:
        """
        Consulta restrições financeiras (negativações)
        
        Args:
            cpf_cnpj: CPF ou CNPJ
        
        Returns:
            Lista de restrições
        """
        
        await self._ensure_authenticated()
        
        if not self.access_token:
            return []
        
        try:
            url = f"{self.BASE_URL}/restricoes"
            
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
                    
                    restricoes = []
                    for rest_data in data.get('restricoes', []):
                        restricao = SerasaRestriction(
                            tipo=rest_data.get('tipo', ''),
                            credor=rest_data.get('credor', ''),
                            valor=float(rest_data.get('valor', 0)),
                            data_ocorrencia=self._parse_date(
                                rest_data.get('dataOcorrencia')
                            ),
                            cidade=rest_data.get('cidade', ''),
                            uf=rest_data.get('uf', ''),
                            origem=rest_data.get('origem', '')
                        )
                        restricoes.append(restricao)
                    
                    logger.info(
                        f"✅ Serasa: {len(restricoes)} restrições encontradas"
                    )
                    
                    return restricoes
                
                else:
                    return []
        
        except Exception as e:
            logger.error(f"Erro ao consultar restrições Serasa: {e}")
            return []
    
    async def consultar_consultas_recentes(
        self,
        cpf_cnpj: str
    ) -> List[SerasaConsulta]:
        """
        Consulta quem consultou o CPF/CNPJ nos últimos 90 dias
        
        Args:
            cpf_cnpj: CPF ou CNPJ
        
        Returns:
            Lista de consultas recentes
        """
        
        await self._ensure_authenticated()
        
        if not self.access_token:
            return []
        
        try:
            url = f"{self.BASE_URL}/consultas-recentes"
            
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
                    
                    consultas = []
                    for cons_data in data.get('consultas', []):
                        consulta = SerasaConsulta(
                            data=self._parse_date(cons_data.get('data')),
                            empresa=cons_data.get('empresa', ''),
                            cnpj=cons_data.get('cnpj', ''),
                            motivo=cons_data.get('motivo', '')
                        )
                        consultas.append(consulta)
                    
                    logger.info(
                        f"✅ Serasa: {len(consultas)} consultas recentes"
                    )
                    
                    return consultas
                
                else:
                    return []
        
        except Exception as e:
            logger.error(f"Erro ao consultar histórico Serasa: {e}")
            return []
    
    async def get_full_report(
        self,
        cpf_cnpj: str
    ) -> Optional[SerasaReport]:
        """
        Busca relatório completo de crédito
        
        Inclui:
        - Score
        - Restrições
        - Protestos
        - Ações judiciais
        - Cheques sem fundo
        - Dívidas
        - Participação em empresas
        - Consultas recentes
        
        Args:
            cpf_cnpj: CPF ou CNPJ
        
        Returns:
            Relatório completo ou None
        """
        
        await self._ensure_authenticated()
        
        if not self.access_token:
            logger.warning("⚠️  Serasa não autenticado")
            return None
        
        try:
            url = f"{self.BASE_URL}/relatorio-completo"
            
            doc_clean = ''.join(filter(str.isdigit, cpf_cnpj))
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'documento': doc_clean,
                'tipo': 'CPF' if len(doc_clean) == 11 else 'CNPJ',
                'incluirScore': True,
                'incluirRestricoes': True,
                'incluirConsultas': True,
                'incluirParticipacoes': True
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
                        f"✅ Serasa: Relatório completo obtido - "
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
    
    def _parse_serasa_report(self, data: Dict) -> SerasaReport:
        """Parse relatório completo do Serasa"""
        
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
                uf=rest_data.get('uf', ''),
                origem=rest_data.get('origem', '')
            )
            restricoes.append(restricao)
        
        # Parse consultas recentes
        consultas = []
        for cons_data in data.get('consultasRecentes', []):
            consulta = SerasaConsulta(
                data=self._parse_date(cons_data.get('data')),
                empresa=cons_data.get('empresa', ''),
                cnpj=cons_data.get('cnpj', ''),
                motivo=cons_data.get('motivo', '')
            )
            consultas.append(consulta)
        
        return SerasaReport(
            cpf_cnpj=data.get('documento', ''),
            nome=data.get('nome', ''),
            score=score,
            restricoes=restricoes,
            protestos_quantidade=data.get('protestos', {}).get('quantidade', 0),
            protestos_valor_total=float(data.get('protestos', {}).get('valorTotal', 0)),
            acoes_quantidade=data.get('acoes', {}).get('quantidade', 0),
            acoes_valor_total=float(data.get('acoes', {}).get('valorTotal', 0)),
            cheques_quantidade=data.get('cheques', {}).get('quantidade', 0),
            cheques_valor_total=float(data.get('cheques', {}).get('valorTotal', 0)),
            dividas_quantidade=data.get('dividas', {}).get('quantidade', 0),
            dividas_valor_total=float(data.get('dividas', {}).get('valorTotal', 0)),
            participacao_empresas=data.get('participacaoEmpresas', []),
            consultas_ultimos_90_dias=len(consultas),
            consultas_recentes=consultas,
            data_consulta=datetime.now()
        )
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse data do Serasa"""
        if not date_str:
            return datetime.now()
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except:
                return datetime.now()
