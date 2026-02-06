"""
DataJud (CNJ) - Serviço de integração com API Pública
"""
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected


class DataJudService:
    """Cliente simples para API Pública do DataJud (CNJ)"""

    def __init__(self) -> None:
        self.base_url = settings.DATAJUD_API_URL.strip().rstrip("/")
        self.api_key = settings.DATAJUD_API_KEY
        self.timeout = 30.0

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("DATAJUD_API_URL não configurada")
        if not (self.base_url.startswith("http://") or self.base_url.startswith("https://")):
            raise ValueError("DATAJUD_API_URL inválida")
        clean = path.strip()
        if clean.startswith("http://") or clean.startswith("https://"):
            raise ValueError("Path inválido para DataJud")
        if not clean.startswith("/"):
            clean = f"/{clean}"
        return f"{self.base_url}{clean}"

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="datajud", failure_threshold=5, recovery_timeout=60.0)
    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("DATAJUD_API_KEY não configurada")

        url = self._build_url(path)
        headers = {
            "Authorization": f"APIKey {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(url, params=params, json=payload, headers=headers)
                else:
                    raise ValueError("Método não suportado. Use GET ou POST.")
        except httpx.RequestError as exc:
            raise ValueError(f"Falha de rede/DNS ao acessar DataJud: {exc}") from exc

        if response.status_code >= 400:
            raise ValueError(f"DataJud erro {response.status_code}: {response.text}")

        return response.json()
