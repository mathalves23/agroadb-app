"""
Conecta gov.br - Integração Consulta CNPJ (RFB)
"""
from typing import Any, Dict
import httpx

from app.core.config import settings
from app.services.conecta_auth import ConectaAuthService, ConectaCredentials


class ConectaCNPJService:
    """Cliente para Consulta CNPJ via Conecta"""

    def __init__(self) -> None:
        self.base_url = settings.CONECTA_CNPJ_API_URL.strip().rstrip("/")
        self.path_basica = settings.CONECTA_CNPJ_BASICA_PATH
        self.path_qsa = settings.CONECTA_CNPJ_QSA_PATH
        self.path_empresa = settings.CONECTA_CNPJ_EMPRESA_PATH
        self.token_url = settings.CONECTA_CNPJ_TOKEN_URL.strip()
        self.timeout = 30.0
        self.auth = ConectaAuthService(
            ConectaCredentials(
                base_url=self.base_url,
                client_id=settings.CONECTA_CNPJ_CLIENT_ID,
                client_secret=settings.CONECTA_CNPJ_CLIENT_SECRET,
                api_key=settings.CONECTA_CNPJ_API_KEY,
            ),
            token_url=self.token_url,
        )

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("CONECTA_CNPJ_API_URL não configurada")
        if not path:
            raise ValueError("Path CNPJ não configurado")
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    async def _get_json(self, url: str, cpf_usuario: str) -> Dict[str, Any]:
        headers = await self.auth.build_headers()
        headers["x-cpf-usuario"] = cpf_usuario
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            if response.status_code >= 400:
                raise ValueError(f"CNPJ erro {response.status_code}: {response.text}")
            return response.json()

    async def consultar_basica(self, cnpj: str, cpf_usuario: str) -> Dict[str, Any]:
        url = self._build_url(self.path_basica.format(cnpj=cnpj))
        return await self._get_json(url, cpf_usuario)

    async def consultar_qsa(self, cnpj: str, cpf_usuario: str) -> Dict[str, Any]:
        url = self._build_url(self.path_qsa.format(cnpj=cnpj))
        return await self._get_json(url, cpf_usuario)

    async def consultar_empresa(self, cnpj: str, cpf_usuario: str) -> Dict[str, Any]:
        url = self._build_url(self.path_empresa.format(cnpj=cnpj))
        return await self._get_json(url, cpf_usuario)
