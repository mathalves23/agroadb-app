"""
Portal gov.br - API de Serviços Estaduais
"""
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings


class ServicosEstaduaisService:
    """Cliente para API de Serviços Estaduais"""

    def __init__(self) -> None:
        self.base_url = settings.SERVICOS_ESTADUAIS_API_URL.strip().rstrip("/")
        self.timeout = 30.0

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("SERVICOS_ESTADUAIS_API_URL não configurada")
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    async def _request(self, method: str, path: str, token: Optional[str] = None, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = self._build_url(path)
        headers: Dict[str, str] = {}
        if token:
            headers["Authorization"] = token
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method.upper(), url, headers=headers, json=payload)
            if response.status_code >= 400:
                raise ValueError(f"Serviços Estaduais erro {response.status_code}: {response.text}")
            return response.json()

    async def autenticar(self, email: str, senha: str) -> Dict[str, Any]:
        return await self._request("POST", "/autenticacao", payload={"email": email, "senha": senha})

    async def inserir_servico(self, payload: Dict[str, Any], token: Optional[str]) -> Dict[str, Any]:
        return await self._request("POST", "/servicos", token=token, payload=payload)

    async def editar_servico(self, payload: Dict[str, Any], token: Optional[str]) -> Dict[str, Any]:
        return await self._request("PUT", "/servicos", token=token, payload=payload)

    async def consultar_servico(self, servico_id: str, token: Optional[str]) -> Dict[str, Any]:
        return await self._request("GET", f"/servicos/{servico_id}", token=token)
