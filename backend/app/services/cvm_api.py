"""
CVM — Comissão de Valores Mobiliários (Dados Abertos)
https://dados.cvm.gov.br/
Consulta: Fundos de Investimento, FIIs, Participantes
Sem autenticação. Gratuito.
"""
from typing import Any, Dict, List, Optional
import httpx

from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected


class CVMService:
    """Cliente para dados abertos da CVM (gratuito, sem auth)"""

    BASE_URL = "https://dados.cvm.gov.br/api/3"

    def __init__(self) -> None:
        self.timeout = 30.0

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            if resp.status_code >= 400:
                raise ValueError(f"CVM erro {resp.status_code}: {resp.text[:300]}")
            return resp.json()

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="cvm", failure_threshold=5, recovery_timeout=60.0)
    async def buscar_datasets(self, query: str, rows: int = 10) -> Dict[str, Any]:
        """Busca datasets da CVM por termo"""
        return await self._get("/action/package_search", params={"q": query, "rows": rows})

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="cvm", failure_threshold=5, recovery_timeout=60.0)
    async def buscar_fundos(self, cnpj: Optional[str] = None, nome: Optional[str] = None) -> Dict[str, Any]:
        """Busca fundos de investimento por CNPJ ou nome"""
        query = "fundos investimento"
        if cnpj:
            query += f" {cnpj}"
        if nome:
            query += f" {nome}"
        return await self._get("/action/package_search", params={"q": query, "rows": 10})

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="cvm", failure_threshold=5, recovery_timeout=60.0)
    async def buscar_fii(self, cnpj: Optional[str] = None) -> Dict[str, Any]:
        """Busca fundos imobiliários"""
        query = "fundo imobiliario FII"
        if cnpj:
            query += f" {cnpj}"
        return await self._get("/action/package_search", params={"q": query, "rows": 10})

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="cvm", failure_threshold=5, recovery_timeout=60.0)
    async def buscar_participantes(self, cnpj: Optional[str] = None) -> Dict[str, Any]:
        """Busca participantes do mercado"""
        query = "participantes"
        if cnpj:
            query += f" {cnpj}"
        return await self._get("/action/package_search", params={"q": query, "rows": 10})

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="cvm", failure_threshold=5, recovery_timeout=60.0)
    async def detalhar_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """Detalha um dataset específico"""
        return await self._get("/action/package_show", params={"id": dataset_id})
