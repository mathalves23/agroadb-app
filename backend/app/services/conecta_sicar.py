"""
Conecta gov.br - Integração SICAR
"""
from typing import Any, Dict
import httpx

from app.core.config import settings
from app.services.conecta_auth import ConectaAuthService, ConectaCredentials


class ConectaSICARService:
    """Cliente para SICAR via Conecta"""

    def __init__(self) -> None:
        self.base_url = settings.CONECTA_SICAR_API_URL.strip().rstrip("/")
        self.path_cpf_cnpj = settings.CONECTA_SICAR_CPF_CNPJ_PATH
        self.path_imovel = settings.CONECTA_SICAR_IMOVEL_PATH
        self.token_url = settings.CONECTA_SICAR_TOKEN_URL.strip()
        self.timeout = 30.0
        self.auth = ConectaAuthService(
            ConectaCredentials(
                base_url=self.base_url,
                client_id=settings.CONECTA_SICAR_CLIENT_ID,
                client_secret=settings.CONECTA_SICAR_CLIENT_SECRET,
                api_key=settings.CONECTA_SICAR_API_KEY,
            ),
            token_url=self.token_url,
        )

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("CONECTA_SICAR_API_URL não configurada")
        if not path:
            raise ValueError("Path SICAR não configurado")
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def _credentials_missing(self) -> bool:
        return not self.auth.has_credentials()

    def _credential_error(self) -> ValueError:
        return ValueError(
            "Credenciais Conecta SICAR não configuradas. "
            "Configure CONECTA_SICAR_CLIENT_ID/CONECTA_SICAR_CLIENT_SECRET ou CONECTA_SICAR_API_KEY no .env."
        )

    async def consultar_por_cpf_cnpj(self, cpf_cnpj: str) -> Dict[str, Any]:
        if self._credentials_missing():
            raise self._credential_error()
        url = self._build_url(self.path_cpf_cnpj.format(cpf_cnpj=cpf_cnpj))
        headers = await self.auth.build_headers()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            if response.status_code >= 400:
                raise ValueError(f"SICAR erro {response.status_code}: {response.text}")
            return response.json()

    async def consultar_imovel(self, codigo_imovel: str) -> Dict[str, Any]:
        if self._credentials_missing():
            raise self._credential_error()
        if not self.path_imovel:
            raise ValueError("CONECTA_SICAR_IMOVEL_PATH não configurado")
        path = self.path_imovel.replace("{codigo_imovel}", codigo_imovel).replace("{codigo}", codigo_imovel)
        url = self._build_url(path)
        headers = await self.auth.build_headers()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            if response.status_code >= 400:
                raise ValueError(f"SICAR erro {response.status_code}: {response.text}")
            return response.json()
