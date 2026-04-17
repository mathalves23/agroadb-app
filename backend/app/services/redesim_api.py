"""
REDESIM — Consulta Pública CNPJ
https://consultacnpj.redesim.gov.br/
+ ReceitaWS (público)
Consulta: CNPJ dados públicos
Sem autenticação. Gratuito (limitado).
"""
from typing import Any, Dict
import httpx


class RedesimService:
    """Cliente para consulta pública de CNPJ (gratuito, sem auth)"""

    # ReceitaWS é uma API pública muito confiável para consultar CNPJ
    RECEITAWS_URL = "https://receitaws.com.br/v1/cnpj"
    # Fallback: open CNPJ (Minha Receita)
    MINHA_RECEITA_URL = "https://minhareceita.org"

    def __init__(self) -> None:
        self.timeout = 30.0

    async def consultar_cnpj_receitaws(self, cnpj: str) -> Dict[str, Any]:
        """Consulta CNPJ via ReceitaWS (3 consultas/minuto grátis)"""
        cleaned = cnpj.replace(".", "").replace("/", "").replace("-", "")
        url = f"{self.RECEITAWS_URL}/{cleaned}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            if resp.status_code == 429:
                return {"error": "Rate limit atingido. Aguarde 1 minuto.", "status": 429}
            if resp.status_code >= 400:
                raise ValueError(f"ReceitaWS erro {resp.status_code}: {resp.text[:300]}")
            return resp.json()

    async def consultar_cnpj_minhareceita(self, cnpj: str) -> Dict[str, Any]:
        """Consulta CNPJ via Minha Receita (open source)"""
        cleaned = cnpj.replace(".", "").replace("/", "").replace("-", "")
        url = f"{self.MINHA_RECEITA_URL}/{cleaned}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            if resp.status_code >= 400:
                raise ValueError(f"MinhaReceita erro {resp.status_code}: {resp.text[:300]}")
            return resp.json()

    async def consultar_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """Tenta ReceitaWS, fallback para MinhaReceita"""
        try:
            result = await self.consultar_cnpj_receitaws(cnpj)
            if result.get("status") != 429:
                result["_fonte"] = "receitaws"
                return result
        except Exception:
            pass

        try:
            result = await self.consultar_cnpj_minhareceita(cnpj)
            result["_fonte"] = "minhareceita"
            return result
        except Exception as e:
            return {"error": str(e), "_fonte": "fallback_failed"}
