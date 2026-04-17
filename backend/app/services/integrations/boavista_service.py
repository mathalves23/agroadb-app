"""
Integração com Boa Vista SCPC
Consultas de crédito e restrições
"""
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)


@dataclass
class BoaVistaScore:
    """Score de crédito Boa Vista"""
    score: int  # 0-1000
    classificacao: str
    data_consulta: datetime


@dataclass
class BoaVistaRestricao:
    """Restrição na Boa Vista"""
    tipo: str
    origem: str
    valor: float
    data_inclusao: datetime
    descricao: str


@dataclass
class BoaVistaProtesto:
    """Protesto registrado"""
    cartorio: str
    cidade: str
    uf: str
    data_protesto: datetime
    valor: float


@dataclass
class BoaVistaCheque:
    """Cheque sem fundo"""
    banco: str
    agencia: str
    numero_cheque: str
    data_ocorrencia: datetime
    valor: float
    motivo: str


@dataclass
class BoaVistaAcao:
    """Ação judicial"""
    tribunal: str
    numero_processo: str
    tipo: str
    data_distribuicao: datetime
    valor: Optional[float]


@dataclass
class BoaVistaReport:
    """Relatório completo Boa Vista SCPC"""
    cpf_cnpj: str
    nome: str
    score: Optional[BoaVistaScore]
    restricoes_financeiras: List[BoaVistaRestricao]
    protestos: List[BoaVistaProtesto]
    cheques_sem_fundo: List[BoaVistaCheque]
    acoes_judiciais: List[BoaVistaAcao]
    participacao_sociedades: List[Dict]
    consultas_recentes: int
    data_consulta: datetime


class BoaVistaService:
    """
    Serviço de integração com Boa Vista SCPC
    
    ATENÇÃO: Esta integração requer contrato comercial com a Boa Vista.
    
    Requisitos:
    - Credenciamento Boa Vista SCPC
    - Contrato de uso da API
    - Certificado digital (em alguns casos)
    - Client ID e Client Secret (credenciais OAuth2)
    
    Produtos disponíveis:
    - Score de Crédito
    - Consulta de Restrições Financeiras
    - Protestos
    - Cheques sem Fundo
    - Ações Judiciais
    - Participação em Sociedades
    
    Documentação: https://developers.boavistaservicos.com.br/
    """
    
    BASE_URL = "https://api.boavistaservicos.com.br/v1"
    AUTH_URL = "https://auth.boavistaservicos.com.br/oauth2/token"
    
    def __init__(self):
        self.client_id = os.getenv("BOAVISTA_CLIENT_ID")
        self.client_secret = os.getenv("BOAVISTA_CLIENT_SECRET")
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
        """Autentica na API da Boa Vista usando OAuth2"""
        
        if not self.client_id or not self.client_secret:
            logger.warning("⚠️  Credenciais Boa Vista não configuradas")
            logger.info(
                "Configure BOAVISTA_CLIENT_ID e BOAVISTA_CLIENT_SECRET no .env"
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
                    
                    logger.info("✅ Autenticado na Boa Vista SCPC")
                
                elif response.status == 401:
                    logger.error("❌ Credenciais Boa Vista inválidas")
                
                else:
                    error_text = await response.text()
                    logger.error(
                        f"❌ Erro ao autenticar Boa Vista: {response.status} - {error_text}"
                    )
        
        except Exception as e:
            logger.error(f"❌ Erro na autenticação Boa Vista: {e}")
    
    async def _ensure_authenticated(self):
        """Garante que o token está válido"""
        
        if not self.access_token:
            await self._authenticate()
            return
        
        # Verificar se token expirou
        if self.token_expires_at and datetime.now().timestamp() >= self.token_expires_at:
            logger.info("Token Boa Vista expirado, renovando...")
            await self._authenticate()
    
    async def consultar_score(
        self,
        cpf_cnpj: str
    ) -> Optional[BoaVistaScore]:
        """
        Consulta score de crédito
        
        Args:
            cpf_cnpj: CPF ou CNPJ (com ou sem formatação)
        
        Returns:
            Score ou None
        """
        
        await self._ensure_authenticated()
        
        if not self.access_token:
            logger.warning("⚠️  Boa Vista não autenticada")
            return None
        
        try:
            url = f"{self.BASE_URL}/score"
            
            doc_clean = ''.join(filter(str.isdigit, cpf_cnpj))
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'documento': doc_clean,
                'tipoPessoa': 'F' if len(doc_clean) == 11 else 'J'
            }
            
            async with self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    score = BoaVistaScore(
                        score=data.get('score', 0),
                        classificacao=data.get('classificacao', 'INDEFINIDO'),
                        data_consulta=datetime.now()
                    )
                    
                    logger.info(
                        f"✅ Boa Vista Score: {score.score} ({score.classificacao})"
                    )
                    
                    return score
                
                elif response.status == 404:
                    logger.info(f"Boa Vista: Documento {cpf_cnpj} não encontrado")
                    return None
                
                else:
                    error_text = await response.text()
                    logger.error(f"Erro Boa Vista Score {response.status}: {error_text}")
                    return None
        
        except Exception as e:
            logger.error(f"Erro ao consultar Score Boa Vista: {e}")
            return None
    
    async def consultar_restricoes(
        self,
        cpf_cnpj: str
    ) -> List[BoaVistaRestricao]:
        """
        Consulta restrições financeiras
        
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
                        restricao = BoaVistaRestricao(
                            tipo=rest_data.get('tipo', ''),
                            origem=rest_data.get('origem', ''),
                            valor=float(rest_data.get('valor', 0)),
                            data_inclusao=self._parse_date(
                                rest_data.get('dataInclusao')
                            ),
                            descricao=rest_data.get('descricao', '')
                        )
                        restricoes.append(restricao)
                    
                    logger.info(
                        f"✅ Boa Vista: {len(restricoes)} restrições encontradas"
                    )
                    
                    return restricoes
                
                else:
                    return []
        
        except Exception as e:
            logger.error(f"Erro ao consultar restrições Boa Vista: {e}")
            return []
    
    async def consultar_consultas_recentes(
        self,
        cpf_cnpj: str
    ) -> int:
        """
        Consulta quantidade de consultas recentes (90 dias)
        
        Args:
            cpf_cnpj: CPF ou CNPJ
        
        Returns:
            Número de consultas
        """
        
        await self._ensure_authenticated()
        
        if not self.access_token:
            return 0
        
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
                    
                    quantidade = data.get('quantidadeConsultas', 0)
                    
                    logger.info(
                        f"✅ Boa Vista: {quantidade} consultas recentes"
                    )
                    
                    return quantidade
                
                else:
                    return 0
        
        except Exception as e:
            logger.error(f"Erro ao consultar histórico Boa Vista: {e}")
            return 0
    
    async def get_full_report(
        self,
        cpf_cnpj: str
    ) -> Optional[BoaVistaReport]:
        """
        Busca relatório completo
        
        Inclui:
        - Score
        - Restrições financeiras
        - Protestos
        - Cheques sem fundo
        - Ações judiciais
        - Participação em sociedades
        
        Args:
            cpf_cnpj: CPF ou CNPJ
        
        Returns:
            Relatório completo ou None
        """
        
        await self._ensure_authenticated()
        
        if not self.access_token:
            logger.warning("⚠️  Boa Vista não autenticada")
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
                'produto': 'RELATORIO_COMPLETO',
                'incluirScore': True,
                'incluirRestricoes': True,
                'incluirProtestos': True,
                'incluirCheques': True,
                'incluirAcoes': True,
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
                    
                    report = self._parse_boavista_report(data)
                    
                    logger.info(
                        f"✅ Boa Vista: Relatório completo obtido - "
                        f"Score: {report.score.score if report.score else 'N/A'}"
                    )
                    
                    return report
                
                elif response.status == 404:
                    logger.info(f"Boa Vista: Documento {cpf_cnpj} não encontrado")
                    return None
                
                else:
                    error_text = await response.text()
                    logger.error(f"Erro Boa Vista {response.status}: {error_text}")
                    return None
        
        except Exception as e:
            logger.error(f"Erro ao consultar Boa Vista: {e}")
            return None
    
    def _parse_boavista_report(self, data: Dict) -> BoaVistaReport:
        """Parse relatório da Boa Vista"""
        
        # Parse score
        score = None
        if data.get('score'):
            score = BoaVistaScore(
                score=data['score'].get('valor', 0),
                classificacao=data['score'].get('classificacao', ''),
                data_consulta=datetime.now()
            )
        
        # Parse restrições
        restricoes = []
        for rest_data in data.get('restricoesFinanceiras', []):
            restricao = BoaVistaRestricao(
                tipo=rest_data.get('tipo', ''),
                origem=rest_data.get('origem', ''),
                valor=float(rest_data.get('valor', 0)),
                data_inclusao=self._parse_date(rest_data.get('dataInclusao')),
                descricao=rest_data.get('descricao', '')
            )
            restricoes.append(restricao)
        
        # Parse protestos
        protestos = []
        for prot_data in data.get('protestos', []):
            protesto = BoaVistaProtesto(
                cartorio=prot_data.get('cartorio', ''),
                cidade=prot_data.get('cidade', ''),
                uf=prot_data.get('uf', ''),
                data_protesto=self._parse_date(prot_data.get('dataProtesto')),
                valor=float(prot_data.get('valor', 0))
            )
            protestos.append(protesto)
        
        # Parse cheques
        cheques = []
        for cheque_data in data.get('chequesSemFundo', []):
            cheque = BoaVistaCheque(
                banco=cheque_data.get('banco', ''),
                agencia=cheque_data.get('agencia', ''),
                numero_cheque=cheque_data.get('numeroCheque', ''),
                data_ocorrencia=self._parse_date(cheque_data.get('dataOcorrencia')),
                valor=float(cheque_data.get('valor', 0)),
                motivo=cheque_data.get('motivo', '')
            )
            cheques.append(cheque)
        
        # Parse ações
        acoes = []
        for acao_data in data.get('acoesJudiciais', []):
            acao = BoaVistaAcao(
                tribunal=acao_data.get('tribunal', ''),
                numero_processo=acao_data.get('numeroProcesso', ''),
                tipo=acao_data.get('tipo', ''),
                data_distribuicao=self._parse_date(acao_data.get('dataDistribuicao')),
                valor=float(acao_data.get('valor', 0)) if acao_data.get('valor') else None
            )
            acoes.append(acao)
        
        return BoaVistaReport(
            cpf_cnpj=data.get('documento', ''),
            nome=data.get('nome', ''),
            score=score,
            restricoes_financeiras=restricoes,
            protestos=protestos,
            cheques_sem_fundo=cheques,
            acoes_judiciais=acoes,
            participacao_sociedades=data.get('participacaoSociedades', []),
            consultas_recentes=data.get('consultasRecentes', 0),
            data_consulta=datetime.now()
        )
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse data da Boa Vista"""
        if not date_str:
            return datetime.now()
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except:
                return datetime.now()
