"""
TSE — Tribunal Superior Eleitoral (Dados Abertos)
https://dadosabertos.tse.jus.br/
Consulta: Candidatos, Bens declarados, Doações
Sem autenticação. Gratuito.
"""
from typing import Any, Dict, List, Optional
import httpx

from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected


class TSEService:
    """Cliente para dados abertos do TSE (gratuito, sem auth)"""

    BASE_URL = "https://dadosabertos.tse.jus.br/api/3"

    def __init__(self) -> None:
        self.timeout = 30.0

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            if resp.status_code >= 400:
                raise ValueError(f"TSE erro {resp.status_code}: {resp.text[:300]}")
            return resp.json()

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="tse", failure_threshold=5, recovery_timeout=60.0)
    async def buscar_datasets(self, query: str, rows: int = 10) -> Dict[str, Any]:
        """Busca datasets do TSE por termo"""
        return await self._get("/action/package_search", params={"q": query, "rows": rows})

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="tse", failure_threshold=5, recovery_timeout=60.0)
    async def listar_datasets(self, offset: int = 0, limit: int = 20) -> Dict[str, Any]:
        """Lista datasets disponíveis"""
        return await self._get("/action/package_list", params={"offset": offset, "limit": limit})

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="tse", failure_threshold=5, recovery_timeout=60.0)
    async def detalhar_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """Detalha um dataset específico"""
        return await self._get("/action/package_show", params={"id": dataset_id})

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="tse", failure_threshold=5, recovery_timeout=60.0)
    async def buscar_candidatos(self, nome: Optional[str] = None, cpf: Optional[str] = None, ano: int = 2024) -> Dict[str, Any]:
        """Busca candidatos por nome ou CPF via datasets"""
        query = f"candidatos {ano}"
        if nome:
            query += f" {nome}"
        if cpf:
            query += f" {cpf}"
        return await self._get("/action/package_search", params={"q": query, "rows": 5})

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="tse", failure_threshold=5, recovery_timeout=60.0)
    async def buscar_bens_candidatos(self, ano: int = 2024) -> Dict[str, Any]:
        """Busca dataset de bens declarados de candidatos"""
        return await self._get("/action/package_search", params={"q": f"bens candidatos {ano}", "rows": 5})
