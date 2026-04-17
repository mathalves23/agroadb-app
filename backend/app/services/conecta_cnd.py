"""
Conecta gov.br - Integração Consulta CND (RFB/PGFN)
"""
from typing import Any, Dict
import httpx

from app.core.config import settings
from app.services.conecta_auth import ConectaAuthService, ConectaCredentials


class ConectaCNDService:
    """Cliente para Consulta CND via Conecta"""

    def __init__(self) -> None:
        self.base_url = settings.CONECTA_CND_API_URL.strip().rstrip("/")
        self.path_certidao = settings.CONECTA_CND_CERTIDAO_PATH
        self.token_url = settings.CONECTA_CND_TOKEN_URL.strip()
        self.timeout = 30.0
        self.auth = ConectaAuthService(
            ConectaCredentials(
                base_url=self.base_url,
                client_id=settings.CONECTA_CND_CLIENT_ID,
                client_secret=settings.CONECTA_CND_CLIENT_SECRET,
                api_key=settings.CONECTA_CND_API_KEY,
            ),
            token_url=self.token_url,
        )

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("CONECTA_CND_API_URL não configurada")
        if not path:
            raise ValueError("Path CND não configurado")
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    async def consultar_certidao(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self._build_url(self.path_certidao)
        headers = await self.auth.build_headers()
        headers["Content-Type"] = "application/json"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                raise ValueError(f"CND erro {response.status_code}: {response.text}")
            return response.json()
