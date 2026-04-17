"""
IBGE — Serviço de Dados
https://servicodados.ibge.gov.br/api/docs/
Consulta: Municípios, UFs, Nomes, Localidades
Sem autenticação. Gratuito.
"""
from typing import Any, Dict, List
import logging
import httpx

from app.core.cache import cache_service
from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected

logger = logging.getLogger(__name__)


class IBGEService:
    """Cliente para API do IBGE (gratuito, sem auth)"""

    BASE_URL = "https://servicodados.ibge.gov.br/api"

    def __init__(self) -> None:
        self.timeout = 30.0

    async def _get(self, path: str) -> Any:
        url = f"{self.BASE_URL}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            if resp.status_code >= 400:
                raise ValueError(f"IBGE erro {resp.status_code}: {resp.text[:300]}")
            return resp.json()

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="ibge", failure_threshold=5, recovery_timeout=60.0)
    async def listar_estados(self) -> List[Dict[str, Any]]:
        """Lista todos os estados"""
        return await self._get("/v1/localidades/estados?orderBy=nome")

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="ibge", failure_threshold=5, recovery_timeout=60.0)
    async def listar_municipios_uf(self, uf: str) -> List[Dict[str, Any]]:
        """Lista municípios de um estado"""
        # ── Cache ────────────────────────────────────────────────────────
        cache_key = f"cache:ibge:municipios_{uf.strip().upper()}"
        try:
            cached = await cache_service.get(cache_key)
            if cached is not None:
                if isinstance(cached, dict):
                    cached["_from_cache"] = True
                elif isinstance(cached, list) and cached:
                    cached[0]["_from_cache"] = True
                return cached
        except Exception as exc:
            logger.warning("Cache GET falhou para %s: %s", cache_key, exc)

        result = await self._get(f"/v1/localidades/estados/{uf}/municipios?orderBy=nome")

        if result:
            try:
                await cache_service.set(cache_key, result, ttl=7200)
            except Exception as exc:
                logger.warning("Cache SET falhou para %s: %s", cache_key, exc)

        return result

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="ibge", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_municipio(self, codigo_ibge: str) -> Dict[str, Any]:
        """Consulta dados de um município pelo código IBGE"""
        # ── Cache ────────────────────────────────────────────────────────
        cache_key = f"cache:ibge:municipio_{codigo_ibge}"
        try:
            cached = await cache_service.get(cache_key)
            if cached is not None:
                cached["_from_cache"] = True
                return cached
        except Exception as exc:
            logger.warning("Cache GET falhou para %s: %s", cache_key, exc)

        result = await self._get(f"/v1/localidades/municipios/{codigo_ibge}")

        if result:
            try:
                await cache_service.set(cache_key, result, ttl=7200)
            except Exception as exc:
                logger.warning("Cache SET falhou para %s: %s", cache_key, exc)

        return result

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="ibge", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_nome(self, nome: str) -> List[Dict[str, Any]]:
        """Frequência de nomes no Brasil"""
        # ── Cache ────────────────────────────────────────────────────────
        cache_key = f"cache:ibge:{nome.strip().lower()}"
        try:
            cached = await cache_service.get(cache_key)
            if cached is not None:
                if isinstance(cached, dict):
                    cached["_from_cache"] = True
                elif isinstance(cached, list) and cached:
                    cached[0]["_from_cache"] = True
                return cached
        except Exception as exc:
            logger.warning("Cache GET falhou para %s: %s", cache_key, exc)

        result = await self._get(f"/v2/censos/nomes/{nome}")

        if result:
            try:
                await cache_service.set(cache_key, result, ttl=7200)
            except Exception as exc:
                logger.warning("Cache SET falhou para %s: %s", cache_key, exc)

        return result

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="ibge", failure_threshold=5, recovery_timeout=60.0)
    async def listar_paises(self) -> List[Dict[str, Any]]:
        """Lista todos os países"""
        return await self._get("/v1/localidades/paises?orderBy=nome")

    @retry_with_backoff(max_retries=2, base_delay=0.5)
    @circuit_protected(service_name="ibge", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_malha_municipio(self, codigo_ibge: str) -> Dict[str, Any]:
        """Malha geográfica do município (GeoJSON)"""
        url = f"{self.BASE_URL}/v3/malhas/municipios/{codigo_ibge}?formato=application/vnd.geo+json"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            if resp.status_code >= 400:
                raise ValueError(f"IBGE malha erro {resp.status_code}")
            return resp.json()
