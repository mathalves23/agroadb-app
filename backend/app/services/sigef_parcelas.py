"""
SIGEF Parcelas - Integração via web service configurável
"""
from typing import Any, Dict, Optional
import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SigefParcelasService:
    """Cliente para consulta de parcelas SIGEF via WS externo"""

    def __init__(self) -> None:
        self.base_url = settings.SIGEF_PARCELAS_API_URL.strip()
        self.max_pages = settings.SIGEF_PARCELAS_MAX_PAGES
        self.timeout = 60.0

    async def query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.base_url:
            raise ValueError("SIGEF_PARCELAS_API_URL não configurada")
        if not (self.base_url.startswith("http://") or self.base_url.startswith("https://")):
            raise ValueError("SIGEF_PARCELAS_API_URL inválida")

        # Validação e limitação de paginação para evitar instabilidade
        pagina = int(params.get("pagina", 1))
        if pagina < 1:
            pagina = 1
            params["pagina"] = 1
        if pagina > self.max_pages:
            params["pagina"] = self.max_pages
            logger.info(
                "sigef_parcelas: pagina limitada a max_pages=%s",
                self.max_pages,
                extra={"max_pages": self.max_pages},
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
        except httpx.RequestError as exc:
            raise ValueError(f"Falha de rede/DNS ao acessar SIGEF: {exc}") from exc

        if response.status_code >= 400:
            raise ValueError(f"SIGEF Parcelas erro {response.status_code}: {response.text}")

        result = response.json()
        count = len(result) if isinstance(result, list) else (len(result.get("parcelas", [])) if isinstance(result, dict) else 0)
        logger.info(
            "sigef_parcelas: consulta executada",
            extra={"param_keys": list(params.keys()), "result_count": count, "pagina": params.get("pagina")},
        )
        return result
