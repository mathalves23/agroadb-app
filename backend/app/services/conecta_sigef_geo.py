"""
Conecta gov.br - Integração SIGEF GEO
"""
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.services.conecta_auth import ConectaAuthService, ConectaCredentials


class ConectaSIGEFGeoService:
    """Cliente para SIGEF GEO via Conecta"""

    def __init__(self) -> None:
        self.base_url = settings.CONECTA_SIGEF_GEO_API_URL.strip().rstrip("/")
        self.path_parcelas = settings.CONECTA_SIGEF_GEO_PARCELAS_PATH
        self.path_parcelas_geojson = settings.CONECTA_SIGEF_GEO_PARCELAS_GEOJSON_PATH
        self.token_url = settings.CONECTA_SIGEF_GEO_TOKEN_URL.strip()
        self.timeout = 60.0
        self.auth = ConectaAuthService(
            ConectaCredentials(
                base_url=self.base_url,
                client_id=settings.CONECTA_SIGEF_GEO_CLIENT_ID,
                client_secret=settings.CONECTA_SIGEF_GEO_CLIENT_SECRET,
                api_key=settings.CONECTA_SIGEF_GEO_API_KEY,
            ),
            token_url=self.token_url,
        )

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("CONECTA_SIGEF_GEO_API_URL não configurada")
        if not path:
            raise ValueError("Path SIGEF GEO não configurado")
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    async def _get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = await self.auth.build_headers()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code >= 400:
                raise ValueError(f"SIGEF GEO erro {response.status_code}: {response.text}")
            return response.json()

    async def consultar_parcelas(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = self._build_url(self.path_parcelas)
        return await self._get_json(url, params=params)

    async def consultar_parcelas_geojson(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = self._build_url(self.path_parcelas_geojson)
        return await self._get_json(url, params=params)
