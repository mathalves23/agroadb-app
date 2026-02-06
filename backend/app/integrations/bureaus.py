"""
Integração com Bureaus de Crédito

Suporta consulta em:
- Serasa Experian
- Boa Vista SCPC
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import httpx
import base64

logger = logging.getLogger(__name__)


class BureauIntegration:
    """
    Integração com bureaus de crédito
    
    IMPORTANTE: Requer credenciais e contrato comercial com os bureaus
    """
    
    def __init__(
        self,
        serasa_api_key: Optional[str] = None,
        boavista_api_key: Optional[str] = None,
        timeout: float = 30.0
    ):
        self.serasa_api_key = serasa_api_key
        self.boavista_api_key = boavista_api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def query_serasa(
        self,
        cpf_cnpj: str,
        product: str = "basic"
    ) -> Dict[str, Any]:
        """
        Consulta Serasa Experian
        
        Args:
            cpf_cnpj: CPF ou CNPJ
            product: Produto ('basic', 'plus', 'premium')
        
        Products:
        - basic: Score e restrições
        - plus: + histórico de consultas
        - premium: + análise completa
        """
        if not self.serasa_api_key:
            return {
                "success": False,
                "error": "API key Serasa não configurada",
                "note": "Configure SERASA_API_KEY nas variáveis de ambiente"
            }
        
        try:
            # API Serasa Experian
            url = "https://api.serasaexperian.com.br/consulta/v1"
            
            headers = {
                "Authorization": f"Bearer {self.serasa_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "documento": cpf_cnpj,
                "produto": product
            }
            
            response = await self.client.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "score": result.get("score"),
                    "score_class": self._classify_score(result.get("score")),
                    "restrictions": result.get("restricoes", []),
                    "credit_limit": result.get("limite_credito"),
                    "consultas_recent": result.get("consultas_ultimos_90_dias"),
                    "pendencias_financeiras": result.get("pendencias"),
                    "raw_data": result
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
        
        except Exception as e:
            logger.error(f"Erro Serasa: {e}")
            return {"success": False, "error": str(e)}
    
    async def query_boavista(
        self,
        cpf_cnpj: str
    ) -> Dict[str, Any]:
        """
        Consulta Boa Vista SCPC
        
        Similar ao Serasa mas com foco em histórico de pagamentos
        """
        if not self.boavista_api_key:
            return {
                "success": False,
                "error": "API key Boa Vista não configurada",
                "note": "Configure BOAVISTA_API_KEY nas variáveis de ambiente"
            }
        
        try:
            url = "https://api.boavistaservicos.com.br/v1/consulta"
            
            headers = {
                "Authorization": f"Basic {base64.b64encode(self.boavista_api_key.encode()).decode()}",
                "Content-Type": "application/json"
            }
            
            data = {"documento": cpf_cnpj}
            
            response = await self.client.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "score": result.get("score"),
                    "score_range": result.get("faixa_score"),
                    "restricoes": result.get("restricoes", []),
                    "cheques_sem_fundo": result.get("cheques_devolvidos"),
                    "protestos": result.get("protestos"),
                    "acoes_judiciais": result.get("acoes_judiciais"),
                    "falencias": result.get("falencias"),
                    "raw_data": result
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
        
        except Exception as e:
            logger.error(f"Erro Boa Vista: {e}")
            return {"success": False, "error": str(e)}
    
    async def query_all_bureaus(
        self,
        cpf_cnpj: str
    ) -> Dict[str, Any]:
        """Consulta todos os bureaus disponíveis"""
        import asyncio
        
        tasks = [
            self.query_serasa(cpf_cnpj),
            self.query_boavista(cpf_cnpj)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "serasa": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "boavista": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
            "consolidated_score": self._consolidate_scores(results),
            "risk_level": self._calculate_risk_level(results),
            "queried_at": datetime.utcnow().isoformat()
        }
    
    def _classify_score(self, score: Optional[int]) -> str:
        """Classifica score em faixas"""
        if not score:
            return "unknown"
        
        if score >= 800:
            return "excellent"
        elif score >= 700:
            return "good"
        elif score >= 600:
            return "fair"
        elif score >= 500:
            return "poor"
        else:
            return "very_poor"
    
    def _consolidate_scores(self, results: List) -> Optional[int]:
        """Consolida scores de múltiplos bureaus"""
        scores = []
        
        for result in results:
            if isinstance(result, dict) and result.get("success"):
                score = result.get("score")
                if score:
                    scores.append(score)
        
        if scores:
            return int(sum(scores) / len(scores))
        return None
    
    def _calculate_risk_level(self, results: List) -> str:
        """Calcula nível de risco baseado nos bureaus"""
        consolidated = self._consolidate_scores(results)
        
        if not consolidated:
            return "unknown"
        
        # Verificar restrições
        has_restrictions = False
        for result in results:
            if isinstance(result, dict) and result.get("success"):
                if result.get("restrictions") or result.get("restricoes"):
                    has_restrictions = True
                    break
        
        if has_restrictions:
            return "high"
        
        score_class = self._classify_score(consolidated)
        
        if score_class in ["excellent", "good"]:
            return "low"
        elif score_class == "fair":
            return "medium"
        else:
            return "high"
    
    async def close(self):
        await self.client.aclose()


# Função de conveniência
async def check_credit(
    cpf_cnpj: str,
    serasa_key: Optional[str] = None,
    boavista_key: Optional[str] = None
) -> Dict[str, Any]:
    """Verifica crédito em todos os bureaus"""
    integration = BureauIntegration(serasa_key, boavista_key)
    
    try:
        result = await integration.query_all_bureaus(cpf_cnpj)
        return result
    finally:
        await integration.close()
