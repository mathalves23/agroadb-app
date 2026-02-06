"""
Conecta gov.br - Integração SNCCI
"""
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.services.conecta_auth import ConectaAuthService, ConectaCredentials


class ConectaSNCCIService:
    """Cliente para SNCCI via Conecta"""

    def __init__(self) -> None:
        self.base_url = settings.CONECTA_SNCCI_API_URL.strip().rstrip("/")
        self.path_parcelas = settings.CONECTA_SNCCI_PARCELAS_PATH
        self.path_creditos_ativos = settings.CONECTA_SNCCI_CREDITOS_ATIVOS_PATH
        self.path_creditos = settings.CONECTA_SNCCI_CREDITOS_PATH
        self.path_boletos = settings.CONECTA_SNCCI_BOLETOS_PATH
        self.token_url = settings.CONECTA_SNCCI_TOKEN_URL.strip()
        self.timeout = 30.0
        self.auth = ConectaAuthService(
            ConectaCredentials(
                base_url=self.base_url,
                client_id=settings.CONECTA_SNCCI_CLIENT_ID,
                client_secret=settings.CONECTA_SNCCI_CLIENT_SECRET,
                api_key=settings.CONECTA_SNCCI_API_KEY,
            ),
            token_url=self.token_url,
        )

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("CONECTA_SNCCI_API_URL não configurada")
        if not path:
            raise ValueError("Path SNCCI não configurado")
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    async def _get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = await self.auth.build_headers()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code >= 400:
                raise ValueError(f"SNCCI erro {response.status_code}: {response.text}")
            return response.json()

    async def _get_bytes(self, url: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        headers = await self.auth.build_headers()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers, params=params)
            return response

    async def listar_parcelas(self, cod_credito: str) -> Dict[str, Any]:
        url = self._build_url(self.path_parcelas)
        return await self._get_json(url, params={"codCredito": cod_credito})

    async def listar_creditos_ativos(self, cod_beneficiario: str) -> Dict[str, Any]:
        url = self._build_url(self.path_creditos_ativos)
        return await self._get_json(url, params={"codBeneficiario": cod_beneficiario})

    async def consultar_credito(self, codigo: str) -> Dict[str, Any]:
        url = self._build_url(self.path_creditos.format(codigo=codigo))
        return await self._get_json(url)

    async def baixar_boleto(self, cd_plano_pagamento_parcela: str) -> httpx.Response:
        url = self._build_url(self.path_boletos)
        return await self._get_bytes(url, params={"cdPlanoPagamentoParcela": cd_plano_pagamento_parcela})
