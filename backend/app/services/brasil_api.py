"""
BrasilAPI — API pública e gratuita
https://brasilapi.com.br/
Consulta: CNPJ, CEP, Bancos, IBGE Municípios
Sem autenticação. Sem limites declarados.
"""
from typing import Any, Dict, Optional
import logging
import httpx

from app.core.cache import cache_service
from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected

logger = logging.getLogger(__name__)


class BrasilAPIService:
    """Cliente para BrasilAPI (gratuito, sem auth)"""

    BASE_URL = "https://brasilapi.com.br/api"

    def __init__(self) -> None:
        self.timeout = 30.0

    async def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            if resp.status_code == 404:
                return {"error": "Não encontrado", "status": 404}
            if resp.status_code >= 400:
                raise ValueError(f"BrasilAPI erro {resp.status_code}: {resp.text[:300]}")
            return resp.json()

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="brasilapi", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """Consulta dados públicos de CNPJ"""
        cleaned = cnpj.replace(".", "").replace("/", "").replace("-", "")

        # ── Cache ────────────────────────────────────────────────────────
        cache_key = f"cache:brasilapi:{cleaned}"
        try:
            cached = await cache_service.get(cache_key)
            if cached is not None:
                cached["_from_cache"] = True
                return cached
        except Exception as exc:
            logger.warning("Cache GET falhou para %s: %s", cache_key, exc)

        result = await self._get(f"/cnpj/v1/{cleaned}")

        if result and not result.get("error"):
            try:
                await cache_service.set(cache_key, result, ttl=3600)
            except Exception as exc:
                logger.warning("Cache SET falhou para %s: %s", cache_key, exc)

        return result

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="brasilapi", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_cep(self, cep: str) -> Dict[str, Any]:
        """Consulta endereço por CEP"""
        cleaned = cep.replace("-", "").replace(".", "")

        # ── Cache ────────────────────────────────────────────────────────
        cache_key = f"cache:brasilapi:{cleaned}"
        try:
            cached = await cache_service.get(cache_key)
            if cached is not None:
                cached["_from_cache"] = True
                return cached
        except Exception as exc:
            logger.warning("Cache GET falhou para %s: %s", cache_key, exc)

        result = await self._get(f"/cep/v2/{cleaned}")

        if result and not result.get("error"):
            try:
                await cache_service.set(cache_key, result, ttl=3600)
            except Exception as exc:
                logger.warning("Cache SET falhou para %s: %s", cache_key, exc)

        return result

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="brasilapi", failure_threshold=5, recovery_timeout=60.0)
    async def listar_bancos(self) -> Dict[str, Any]:
        """Lista todos os bancos"""
        return await self._get("/banks/v1")

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="brasilapi", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_banco(self, codigo: str) -> Dict[str, Any]:
        """Consulta um banco por código"""
        return await self._get(f"/banks/v1/{codigo}")

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="brasilapi", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_ddd(self, ddd: str) -> Dict[str, Any]:
        """Consulta cidades de um DDD"""
        return await self._get(f"/ddd/v1/{ddd}")

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="brasilapi", failure_threshold=5, recovery_timeout=60.0)
    async def listar_municipios_uf(self, uf: str) -> Dict[str, Any]:
        """Lista municípios de uma UF (IBGE)"""
        return await self._get(f"/ibge/municipios/v1/{uf.upper()}")

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="brasilapi", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_feriados(self, ano: int) -> Dict[str, Any]:
        """Lista feriados nacionais de um ano"""
        return await self._get(f"/feriados/v1/{ano}")

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="brasilapi", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_fipe(self, codigo_fipe: str) -> Dict[str, Any]:
        """Consulta tabela FIPE de veículo"""
        return await self._get(f"/fipe/preco/v1/{codigo_fipe}")

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="brasilapi", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_corretoras(self) -> Dict[str, Any]:
        """Lista corretoras CVM"""
        return await self._get("/cvm/corretoras/v1")

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="brasilapi", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_pix(self) -> Dict[str, Any]:
        """Lista participantes PIX"""
        return await self._get("/pix/v1/participants")
