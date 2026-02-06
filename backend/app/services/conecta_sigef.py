"""
Conecta gov.br - Integração SIGEF
"""
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.services.conecta_auth import ConectaAuthService, ConectaCredentials


class ConectaSIGEFService:
    """Cliente para SIGEF via Conecta"""

    def __init__(self) -> None:
        self.base_url = (settings.CONECTA_SIGEF_API_URL or "").strip().rstrip("/")
        self.path_imovel = settings.CONECTA_SIGEF_IMOVEL_PATH or ""
        self.path_parcelas = settings.CONECTA_SIGEF_PARCELAS_PATH or ""
        self.token_url = (settings.CONECTA_SIGEF_TOKEN_URL or "").strip()
        if not self.token_url and self.base_url:
            self.token_url = f"{self.base_url.rstrip('/')}/oauth2/jwt-token"
        self.timeout = 30.0
        self.auth = ConectaAuthService(
            ConectaCredentials(
                base_url=self.base_url,
                client_id=settings.CONECTA_SIGEF_CLIENT_ID,
                client_secret=settings.CONECTA_SIGEF_CLIENT_SECRET,
                api_key=settings.CONECTA_SIGEF_API_KEY,
            ),
            token_url=self.token_url,
        )

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("CONECTA_SIGEF_API_URL não configurada")
        if not path:
            raise ValueError("Path SIGEF não configurado")
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def _credentials_missing(self) -> bool:
        return not self.auth.has_credentials()

    def _credential_error(self) -> ValueError:
        return ValueError(
            "Credenciais Conecta SIGEF não configuradas. "
            "Configure CONECTA_SIGEF_CLIENT_ID/CONECTA_SIGEF_CLIENT_SECRET ou CONECTA_SIGEF_API_KEY no .env."
        )

    async def consultar_imovel(self, codigo_imovel: str) -> Dict[str, Any]:
        if self._credentials_missing():
            raise self._credential_error()
        path = self.path_imovel.replace("{codigo_imovel}", codigo_imovel).replace("{codigo}", codigo_imovel)
        url = self._build_url(path)
        headers = await self.auth.build_headers()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            if response.status_code >= 400:
                raise ValueError(f"SIGEF erro {response.status_code}: {response.text}")
            return response.json()

    async def consultar_parcelas(self, cpf_cnpj: Optional[str] = None) -> Dict[str, Any]:
        if self._credentials_missing():
            raise self._credential_error()
        url = self._build_url(self.path_parcelas)
        headers = await self.auth.build_headers()
        params: Dict[str, Any] = {}
        if cpf_cnpj:
            params["cpf_cnpj"] = cpf_cnpj
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code >= 400:
                raise ValueError(f"SIGEF erro {response.status_code}: {response.text}")
            return response.json()
