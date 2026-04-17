"""
Portal gov.br - API de Serviços
"""
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings


class PortalServicosService:
    """Cliente para API de Serviços do Portal gov.br"""

    def __init__(self) -> None:
        self.base_url = settings.PORTAL_SERVICOS_API_URL.strip().rstrip("/")
        self.timeout = 30.0

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("PORTAL_SERVICOS_API_URL não configurada")
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    async def _get_json(self, path: str, token: Optional[str] = None) -> Dict[str, Any]:
        url = self._build_url(path)
        headers: Dict[str, str] = {}
        if token:
            headers["Authorization"] = token
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            if response.status_code >= 400:
                raise ValueError(f"Portal Serviços erro {response.status_code}: {response.text}")
            return response.json()

    async def consultar_orgao(self, cod_siorg: str) -> Dict[str, Any]:
        return await self._get_json(f"/orgao/{cod_siorg}")

    async def consultar_servico(self, servico_id: str) -> Dict[str, Any]:
        return await self._get_json(f"/servicos/{servico_id}")

    async def consultar_servico_simples(self, servico_id: str) -> Dict[str, Any]:
        return await self._get_json(f"/servicos/simples/{servico_id}")

    async def listar_servicos_auth(self, token: Optional[str]) -> Dict[str, Any]:
        return await self._get_json("/servicos-auth", token=token or settings.PORTAL_SERVICOS_AUTH_TOKEN)
