"""
Portal da Transparência — CGU
https://portaldatransparencia.gov.br/api-de-dados
Consulta: CEIS, CNEP, Contratos, Servidores, Sanções
Auth: API Key gratuita (registrar no portal)
"""
from typing import Any, Dict, Optional
import logging
import httpx

from app.core.cache import cache_service
from app.core.config import settings
from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected

logger = logging.getLogger(__name__)


class PortalTransparenciaService:
    """Cliente para Portal da Transparência (CGU)"""

    BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"

    def __init__(self) -> None:
        self.api_key = getattr(settings, "PORTAL_TRANSPARENCIA_API_KEY", "")
        self.timeout = 30.0

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Accept": "application/json"}
        if self.api_key:
            headers["chave-api-dados"] = self.api_key
        return headers

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, headers=self._headers(), params=params)
            if resp.status_code >= 400:
                raise ValueError(f"Portal Transparência erro {resp.status_code}: {resp.text[:300]}")
            data = resp.json()
            if isinstance(data, list):
                return {"items": data, "total": len(data)}
            return data

    async def _cached_get(self, method: str, doc: str, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Wrapper que adiciona cache ao redor de _get para métodos de consulta."""
        cleaned_doc = doc.replace(".", "").replace("/", "").replace("-", "").strip()
        cache_key = f"cache:transparencia:{method}:{cleaned_doc}"

        # ── Cache: tentar recuperar ──────────────────────────────────────
        try:
            cached = await cache_service.get(cache_key)
            if cached is not None:
                cached["_from_cache"] = True
                return cached
        except Exception as exc:
            logger.warning("Cache GET falhou para %s: %s", cache_key, exc)

        result = await self._get(path, params=params)

        # Só cacheia respostas com dados (items não-vazios ou chaves significativas)
        if result and not result.get("error"):
            try:
                await cache_service.set(cache_key, result, ttl=3600)
            except Exception as exc:
                logger.warning("Cache SET falhou para %s: %s", cache_key, exc)

        return result

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="portal_transparencia", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_ceis(self, cnpj_cpf: str) -> Dict[str, Any]:
        """Cadastro de Empresas Inidôneas e Suspensas (sanções)"""
        return await self._cached_get("ceis", cnpj_cpf, "/ceis", params={"cnpjSancionado": cnpj_cpf})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="portal_transparencia", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_cnep(self, cnpj_cpf: str) -> Dict[str, Any]:
        """Cadastro Nacional de Empresas Punidas"""
        return await self._cached_get("cnep", cnpj_cpf, "/cnep", params={"cnpjSancionado": cnpj_cpf})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="portal_transparencia", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_ceaf(self, cpf: str) -> Dict[str, Any]:
        """Cadastro de Expulsões da Administração Federal"""
        return await self._cached_get("ceaf", cpf, "/ceaf", params={"cpfSancionado": cpf})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="portal_transparencia", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_acordos_leniencia(self, cnpj: str) -> Dict[str, Any]:
        """Acordos de Leniência"""
        return await self._cached_get("acordos_leniencia", cnpj, "/acordos-leniencia", params={"cnpjSancionado": cnpj})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="portal_transparencia", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_contratos(self, cpf_cnpj: str) -> Dict[str, Any]:
        """Contratos do governo federal vinculados a CPF/CNPJ"""
        return await self._cached_get("contratos", cpf_cnpj, "/contratos", params={"cpfCnpjContratado": cpf_cnpj})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="portal_transparencia", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_servidores(self, cpf: str) -> Dict[str, Any]:
        """Servidores públicos federais por CPF"""
        return await self._cached_get("servidores", cpf, "/servidores", params={"cpf": cpf})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="portal_transparencia", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_gastos_cartao(self, cpf_cnpj: str) -> Dict[str, Any]:
        """Gastos com cartão de pagamento por CPF/CNPJ"""
        return await self._cached_get("gastos_cartao", cpf_cnpj, "/cartoes", params={"cpfCnpjFavorecido": cpf_cnpj})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="portal_transparencia", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_despesas(self, cpf_cnpj: str) -> Dict[str, Any]:
        """Despesas do governo federal por favorecido"""
        return await self._cached_get("despesas", cpf_cnpj, "/despesas/recursos-recebidos", params={"cpfCnpjFavorecido": cpf_cnpj})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="portal_transparencia", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_beneficios(self, cpf: str) -> Dict[str, Any]:
        """Benefícios ao cidadão (Bolsa Família, BPC, Seguro Defeso)"""
        return await self._cached_get("beneficios", cpf, "/beneficios-cidadao", params={"cpfBeneficiario": cpf})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="portal_transparencia", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_viagens(self, cpf: str) -> Dict[str, Any]:
        """Viagens a serviço do governo"""
        return await self._cached_get("viagens", cpf, "/viagens", params={"cpfViajante": cpf})
