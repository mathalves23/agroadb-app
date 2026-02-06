"""
Receita Federal — Consulta Situação Cadastral de CPF
https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp
Parâmetros: cpf, data_nascimento (birthdate)
Retorna: nome, situação cadastral, data inscrição, ano óbito, etc.
Gratuito, consulta pública.
"""
from typing import Any, Dict, Optional
import logging
import httpx

from app.core.cache import cache_service
from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected

logger = logging.getLogger(__name__)


class ReceitaCPFService:
    """Cliente para consulta de situação cadastral de CPF na Receita Federal"""

    BASE_URL = "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao"
    CONSULTA_URL = f"{BASE_URL}/ConsultaPublica.asp"

    def __init__(self) -> None:
        self.timeout = 30.0
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/json",
            "User-Agent": "AgroADB/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    @circuit_protected(service_name="receita_cpf", failure_threshold=5, recovery_timeout=60.0)
    async def consultar(
        self, cpf: str, data_nascimento: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Consulta situação cadastral de CPF na Receita Federal.
        data_nascimento: formato DD/MM/AAAA
        Retorna: nome, situação cadastral, data inscrição, ano óbito, etc.
        """
        cleaned = cpf.replace(".", "").replace("-", "").strip()
        if len(cleaned) != 11:
            raise ValueError("CPF deve ter 11 dígitos")

        # ── Cache: tentar recuperar ──────────────────────────────────────
        cache_key = f"cache:receita_cpf:{cleaned}"
        try:
            cached = await cache_service.get(cache_key)
            if cached is not None:
                cached["_from_cache"] = True
                return cached
        except Exception as exc:
            logger.warning("Cache GET falhou para %s: %s", cache_key, exc)

        result: Dict[str, Any] = {
            "cpf": cleaned,
            "nome": None,
            "situacao_cadastral": None,
            "data_inscricao": None,
            "data_nascimento": data_nascimento,
            "ano_obito": None,
            "fonte": "Receita Federal / CPF",
        }

        form_data: Dict[str, str] = {
            "txtCPF": cleaned,
        }
        if data_nascimento:
            form_data["txtDataNascimento"] = data_nascimento

        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, verify=True
        ) as client:
            # Tenta POST no formulário público
            try:
                resp = await client.post(
                    self.CONSULTA_URL,
                    data=form_data,
                    headers=self.headers,
                )
                if resp.status_code < 400:
                    ct = resp.headers.get("content-type", "")
                    if "json" in ct:
                        json_result = resp.json()
                        try:
                            await cache_service.set(cache_key, json_result, ttl=1800)
                        except Exception as exc:
                            logger.warning("Cache SET falhou para %s: %s", cache_key, exc)
                        return json_result

                    text = resp.text
                    result = self._parse_html(text, result)
                    if result.get("situacao_cadastral"):
                        try:
                            await cache_service.set(cache_key, result, ttl=1800)
                        except Exception as exc:
                            logger.warning("Cache SET falhou para %s: %s", cache_key, exc)
                        return result

            except httpx.RequestError:
                pass

            # Tenta GET como fallback
            try:
                params = {"idChecked": cleaned}
                if data_nascimento:
                    params["Ession"] = data_nascimento
                resp = await client.get(
                    self.CONSULTA_URL,
                    params=params,
                    headers={
                        "Accept": "text/html,application/json",
                        "User-Agent": "AgroADB/1.0",
                    },
                )
                if resp.status_code < 400:
                    ct = resp.headers.get("content-type", "")
                    if "json" in ct:
                        json_result = resp.json()
                        try:
                            await cache_service.set(cache_key, json_result, ttl=1800)
                        except Exception as exc:
                            logger.warning("Cache SET falhou para %s: %s", cache_key, exc)
                        return json_result
                    result = self._parse_html(resp.text, result)
                    if result.get("situacao_cadastral"):
                        try:
                            await cache_service.set(cache_key, result, ttl=1800)
                        except Exception as exc:
                            logger.warning("Cache SET falhou para %s: %s", cache_key, exc)
                        return result
            except httpx.RequestError:
                pass

        # Nenhuma fonte retornou dados completos (não cacheia falhas)
        result["mensagem"] = "Consulta disponível via portal da Receita Federal."
        result["portal_url"] = self.CONSULTA_URL
        return result

    def _parse_html(self, html: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai dados básicos do HTML retornado pela Receita Federal usando BeautifulSoup."""
        from bs4 import BeautifulSoup
        import re as _re

        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(separator="\n")

        field_labels = {
            "nome": ["Nome da Pessoa Física", "Nome"],
            "situacao_cadastral": ["Situação Cadastral"],
            "data_inscricao": ["Data de Inscrição", "Data Inscrição"],
            "ano_obito": ["Óbito"],
            "digito_verificador": ["Dígito Verificador"],
        }

        for field, labels in field_labels.items():
            for label in labels:
                tag = soup.find(string=_re.compile(_re.escape(label), _re.IGNORECASE))
                if tag:
                    parent = tag.find_parent()
                    if parent:
                        next_elem = parent.find_next_sibling()
                        if next_elem:
                            value = next_elem.get_text(strip=True)
                            if value and value.upper() not in ("", "***", "********"):
                                result[field] = value
                                break

            if field not in result:
                for label in labels:
                    if field == "ano_obito":
                        pattern = _re.escape(label) + r'\s*[:\-]?\s*(\d{4})'
                    elif field == "digito_verificador":
                        pattern = _re.escape(label) + r'\s*[:\-]?\s*(\d+)'
                    else:
                        pattern = _re.escape(label) + r'\s*[:\-]?\s*(.+?)(?:\n|$)'
                    match = _re.search(pattern, text, _re.IGNORECASE)
                    if match:
                        value = match.group(1).strip()
                        if value:
                            result[field] = value
                            break

        return result

    async def verificar_disponibilidade(self) -> Dict[str, Any]:
        """Verifica se o portal da Receita Federal está acessível."""
        async with httpx.AsyncClient(
            timeout=15.0, follow_redirects=True, verify=True
        ) as client:
            try:
                resp = await client.head(self.CONSULTA_URL)
                return {
                    "disponivel": resp.status_code < 500,
                    "status_code": resp.status_code,
                    "url": self.CONSULTA_URL,
                }
            except httpx.RequestError as e:
                return {
                    "disponivel": False,
                    "erro": str(e)[:200],
                    "url": self.CONSULTA_URL,
                }
