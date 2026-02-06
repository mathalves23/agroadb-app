"""
Conecta gov.br - Autenticação (OAuth2 ou APIKey)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import time
import httpx


@dataclass
class ConectaCredentials:
    base_url: str
    client_id: str
    client_secret: str
    api_key: str


class ConectaAuthService:
    """Gerencia autenticação do Conecta (OAuth2 client_credentials)"""

    def __init__(self, credentials: ConectaCredentials, token_url: str):
        self.credentials = credentials
        self.token_url = token_url
        self._token_cache: Optional[Dict[str, Any]] = None

    def has_api_key(self) -> bool:
        return bool(self.credentials.api_key)

    def has_oauth(self) -> bool:
        return bool(self.credentials.client_id and self.credentials.client_secret)

    def has_credentials(self) -> bool:
        """Indica se há pelo menos uma forma de autenticação (APIKey ou OAuth2)."""
        return self.has_api_key() or self.has_oauth()

    def _token_valid(self) -> bool:
        if not self._token_cache:
            return False
        expires_in = int(self._token_cache.get("expires_in", 0))
        created_at = float(self._token_cache.get("_created_at", 0))
        return (time.time() - created_at) < max(0, expires_in - 30)

    async def get_access_token(self) -> str:
        if self._token_valid():
            return self._token_cache["access_token"]

        if not self.has_oauth():
            raise ValueError("Credenciais OAuth2 do Conecta não configuradas")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.credentials.client_id,
                    "client_secret": self.credentials.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            payload = response.json()
            payload["_created_at"] = time.time()
            self._token_cache = payload
            return payload["access_token"]

    async def build_headers(self) -> Dict[str, str]:
        if not self.has_credentials():
            raise ValueError(
                "Credenciais Conecta não configuradas. "
                "Configure client_id/client_secret (OAuth2) ou api_key no .env."
            )
        if self.has_api_key():
            return {"Authorization": f"APIKey {self.credentials.api_key}"}

        token = await self.get_access_token()
        return {"Authorization": f"Bearer {token}"}
