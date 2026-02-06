"""
Conecta gov.br - Integração SNCR
"""
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.services.conecta_auth import ConectaAuthService, ConectaCredentials


class ConectaSNCRService:
    """Cliente para SNCR via Conecta"""

    def __init__(self) -> None:
        self.base_url = settings.CONECTA_SNCR_API_URL.strip().rstrip("/")
        self.path_imovel = settings.CONECTA_SNCR_IMOVEL_PATH
        self.path_cpf_cnpj = settings.CONECTA_SNCR_CPF_CNPJ_PATH
        self.path_situacao = settings.CONECTA_SNCR_SITUACAO_PATH
        self.path_ccir = settings.CONECTA_SNCR_CCIR_PATH
        self.token_url = settings.CONECTA_SNCR_TOKEN_URL.strip()
        self.timeout = 30.0
        self.auth = ConectaAuthService(
            ConectaCredentials(
                base_url=self.base_url,
                client_id=settings.CONECTA_SNCR_CLIENT_ID,
                client_secret=settings.CONECTA_SNCR_CLIENT_SECRET,
                api_key=settings.CONECTA_SNCR_API_KEY,
            ),
            token_url=self.token_url,
        )

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("CONECTA_SNCR_API_URL não configurada")
        if not path:
            raise ValueError("Path SNCR não configurado")
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    async def _get_json(self, url: str) -> Dict[str, Any]:
        headers = await self.auth.build_headers()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            if response.status_code >= 400:
                raise ValueError(f"SNCR erro {response.status_code}: {response.text}")
            return response.json()

    async def _get_bytes(self, url: str) -> httpx.Response:
        headers = await self.auth.build_headers()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            return response

    def _credentials_missing(self) -> bool:
        return not self.auth.has_credentials()

    async def consultar_imovel(self, codigo_imovel: str) -> Dict[str, Any]:
        if self._credentials_missing():
            raise ValueError(
                "Credenciais Conecta SNCR não configuradas. "
                "Configure CONECTA_SNCR_CLIENT_ID/CONECTA_SNCR_CLIENT_SECRET ou CONECTA_SNCR_API_KEY no .env."
            )
        url = self._build_url(self.path_imovel.format(codigo=codigo_imovel))
        return await self._get_json(url)

    async def consultar_por_cpf_cnpj(self, cpf_cnpj: str) -> Dict[str, Any]:
        if self._credentials_missing():
            raise ValueError(
                "Credenciais Conecta SNCR não configuradas. "
                "Configure CONECTA_SNCR_CLIENT_ID/CONECTA_SNCR_CLIENT_SECRET ou CONECTA_SNCR_API_KEY no .env."
            )
        url = self._build_url(self.path_cpf_cnpj.format(cpf_cnpj=cpf_cnpj))
        return await self._get_json(url)

    async def verificar_situacao(self, codigo_imovel: str) -> Dict[str, Any]:
        if self._credentials_missing():
            raise ValueError(
                "Credenciais Conecta SNCR não configuradas. "
                "Configure CONECTA_SNCR_CLIENT_ID/CONECTA_SNCR_CLIENT_SECRET ou CONECTA_SNCR_API_KEY no .env."
            )
        url = self._build_url(self.path_situacao.format(codigo=codigo_imovel))
        return await self._get_json(url)

    async def baixar_ccir(self, codigo_imovel: str) -> httpx.Response:
        if self._credentials_missing():
            raise ValueError(
                "Credenciais Conecta SNCR não configuradas. "
                "Configure CONECTA_SNCR_CLIENT_ID/CONECTA_SNCR_CLIENT_SECRET ou CONECTA_SNCR_API_KEY no .env."
            )
        url = self._build_url(self.path_ccir.format(codigo=codigo_imovel))
        return await self._get_bytes(url)
