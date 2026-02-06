"""
Conecta gov.br - Integração CADIN Consulta/Contratante
"""
from typing import Any, Dict
import httpx

from app.core.config import settings
from app.services.conecta_auth import ConectaAuthService, ConectaCredentials


class ConectaCadinService:
    """Cliente para CADIN via Conecta"""

    def __init__(self) -> None:
        self.base_url = settings.CONECTA_CADIN_API_URL.strip().rstrip("/")
        self.path_info_cpf = settings.CONECTA_CADIN_INFO_CPF_PATH
        self.path_info_cnpj = settings.CONECTA_CADIN_INFO_CNPJ_PATH
        self.path_completa_cpf = settings.CONECTA_CADIN_COMPLETA_CPF_PATH
        self.path_completa_cnpj = settings.CONECTA_CADIN_COMPLETA_CNPJ_PATH
        self.path_versao = settings.CONECTA_CADIN_VERSAO_PATH
        self.token_url = settings.CONECTA_CADIN_TOKEN_URL.strip()
        self.timeout = 30.0
        self.auth = ConectaAuthService(
            ConectaCredentials(
                base_url=self.base_url,
                client_id=settings.CONECTA_CADIN_CLIENT_ID,
                client_secret=settings.CONECTA_CADIN_CLIENT_SECRET,
                api_key=settings.CONECTA_CADIN_API_KEY,
            ),
            token_url=self.token_url,
        )

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("CONECTA_CADIN_API_URL não configurada")
        if not path:
            raise ValueError("Path CADIN não configurado")
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    async def _get_json(self, url: str) -> Dict[str, Any]:
        headers = await self.auth.build_headers()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            if response.status_code >= 400:
                raise ValueError(f"CADIN erro {response.status_code}: {response.text}")
            return response.json()

    async def info_cpf(self, cpf: str) -> Dict[str, Any]:
        url = self._build_url(self.path_info_cpf.format(cpf=cpf))
        return await self._get_json(url)

    async def info_cnpj(self, cnpj: str) -> Dict[str, Any]:
        url = self._build_url(self.path_info_cnpj.format(cnpj=cnpj))
        return await self._get_json(url)

    async def completa_cpf(self, cpf: str) -> Dict[str, Any]:
        url = self._build_url(self.path_completa_cpf.format(cpf=cpf))
        return await self._get_json(url)

    async def completa_cnpj(self, cnpj: str) -> Dict[str, Any]:
        url = self._build_url(self.path_completa_cnpj.format(cnpj=cnpj))
        return await self._get_json(url)

    async def versao(self) -> Dict[str, Any]:
        url = self._build_url(self.path_versao)
        return await self._get_json(url)
