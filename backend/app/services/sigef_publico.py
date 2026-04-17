"""
INCRA / SIGEF — Consulta pública de Parcelas
https://sigef.incra.gov.br/consultar/parcelas
Consulta direta ao portal público do SIGEF (sem credenciais Conecta).
Parâmetros: cpf, cnpj, codigo_imovel
Paginação: até 5 páginas (acima disso o portal fica instável).
Retorna: parcelas (area_ha, cns, codigo_parcela, detentor, matricula, nome).
Gratuito, consulta pública.
"""
from typing import Any, Dict, List, Optional
import re
import httpx
import logging

from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected

logger = logging.getLogger(__name__)

MAX_PAGES = 5


class SIGEFPublicoService:
    """Cliente para consulta pública de parcelas SIGEF/INCRA"""

    BASE_URL = "https://sigef.incra.gov.br"
    CONSULTA_URL = f"{BASE_URL}/consultar/parcelas"
    # API JSON (usada pelo próprio site via AJAX)
    API_URL = f"{BASE_URL}/geo/parcela/pesquisar"

    def __init__(self) -> None:
        self.timeout = 45.0
        self.headers = {
            "Accept": "application/json, text/html",
            "User-Agent": "AgroADB/1.0",
            "Referer": f"{self.BASE_URL}/consultar/parcelas/",
        }

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="sigef_publico", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_cpf(self, cpf: str, paginas: int = MAX_PAGES) -> Dict[str, Any]:
        """Consulta parcelas SIGEF por CPF do detentor."""
        cleaned = cpf.replace(".", "").replace("-", "").strip()
        if len(cleaned) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        return await self._consultar_multiplas_paginas(
            {"cpf": cleaned}, paginas, {"cpf": cleaned}
        )

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="sigef_publico", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_cnpj(self, cnpj: str, paginas: int = MAX_PAGES) -> Dict[str, Any]:
        """Consulta parcelas SIGEF por CNPJ do detentor."""
        cleaned = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
        if len(cleaned) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")
        return await self._consultar_multiplas_paginas(
            {"cnpj": cleaned}, paginas, {"cnpj": cleaned}
        )

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="sigef_publico", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_codigo_imovel(self, codigo_imovel: str) -> Dict[str, Any]:
        """Consulta parcela SIGEF por código do imóvel."""
        if not codigo_imovel or not codigo_imovel.strip():
            raise ValueError("Código do imóvel é obrigatório")
        return await self._consultar_multiplas_paginas(
            {"codigo_imovel": codigo_imovel.strip()}, 1, {"codigo_imovel": codigo_imovel}
        )

    async def _consultar_multiplas_paginas(
        self,
        params: Dict[str, str],
        max_paginas: int,
        audit: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Consulta até N páginas de resultados."""
        max_paginas = min(max_paginas, MAX_PAGES)
        todas_parcelas: List[Dict[str, Any]] = []
        total_resultados = 0
        paginas_retornadas = 0

        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, verify=True
        ) as client:
            for pagina in range(1, max_paginas + 1):
                page_params = {**params, "pagina": str(pagina)}
                result = await self._consultar_pagina(client, page_params)

                if result is None:
                    break

                parcelas = result.get("parcelas", [])
                if isinstance(parcelas, list):
                    todas_parcelas.extend(parcelas)
                    paginas_retornadas += 1

                total_paginas = result.get("paginas", 1)
                total_resultados = result.get("resultados", len(todas_parcelas))

                # Se não há mais páginas, parar
                if pagina >= total_paginas:
                    break

                # Se a página veio vazia, parar
                if not parcelas:
                    break

        return {
            "paginas": paginas_retornadas,
            "paginas_retornadas": paginas_retornadas,
            "resultados": total_resultados,
            "resultados_retornados": len(todas_parcelas),
            "parcelas": todas_parcelas,
            "fonte": "SIGEF/INCRA (público)",
            "consulta": audit,
        }

    async def _consultar_pagina(
        self, client: httpx.AsyncClient, params: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """Consulta uma única página de resultados."""

        # Tenta API JSON do SIGEF (endpoint AJAX)
        try:
            resp = await client.get(
                self.API_URL,
                params=params,
                headers=self.headers,
            )
            if resp.status_code == 200:
                ct = resp.headers.get("content-type", "")
                if "json" in ct:
                    return resp.json()
        except httpx.RequestError:
            pass

        # Tenta POST no formulário
        try:
            resp = await client.post(
                self.CONSULTA_URL,
                data=params,
                headers={
                    **self.headers,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            if resp.status_code == 200:
                ct = resp.headers.get("content-type", "")
                if "json" in ct:
                    return resp.json()
                # Tenta parsear HTML básico
                return self._parse_html_parcelas(resp.text, params)
        except httpx.RequestError:
            pass

        # Tenta GET no formulário público
        try:
            resp = await client.get(
                self.CONSULTA_URL,
                params=params,
                headers=self.headers,
            )
            if resp.status_code == 200:
                ct = resp.headers.get("content-type", "")
                if "json" in ct:
                    return resp.json()
                return self._parse_html_parcelas(resp.text, params)
        except httpx.RequestError:
            pass

        return None

    def _parse_html_parcelas(
        self, html: str, params: Dict[str, str]
    ) -> Dict[str, Any]:
        """Extrai dados de parcelas do HTML retornado pelo SIGEF usando BeautifulSoup."""
        from bs4 import BeautifulSoup
        import re as _re

        soup = BeautifulSoup(html, "lxml")
        parcelas: List[Dict[str, Any]] = []

        # Find all table rows
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 3:
                clean = [cell.get_text(strip=True) for cell in cells]
                if any(clean):
                    parcela: Dict[str, Any] = {}
                    if len(clean) > 0 and clean[0]:
                        parcela["codigo_parcela"] = clean[0]
                    if len(clean) > 1 and clean[1]:
                        parcela["nome"] = clean[1]
                    if len(clean) > 2 and clean[2]:
                        try:
                            parcela["area_ha"] = float(
                                clean[2].replace(",", ".").replace(" ", "")
                            )
                        except ValueError:
                            parcela["area_ha"] = clean[2]
                    if len(clean) > 3 and clean[3]:
                        parcela["matricula"] = clean[3]
                    if len(clean) > 4 and clean[4]:
                        parcela["cns"] = clean[4]
                    if len(clean) > 5 and clean[5]:
                        parcela["detentor"] = clean[5]
                    if parcela:
                        parcelas.append(parcela)

        # Extract total results
        text = soup.get_text()
        total_match = _re.search(r'(\d+)\s*resultado', text, _re.IGNORECASE)
        total = int(total_match.group(1)) if total_match else len(parcelas)

        # Extract total pages
        page_links = soup.find_all("a", href=_re.compile(r'pagina=\d+'))
        paginas = 1
        for link in page_links:
            href = link.get("href", "")
            page_match = _re.search(r'pagina=(\d+)', href)
            if page_match:
                paginas = max(paginas, int(page_match.group(1)))

        return {
            "parcelas": parcelas,
            "paginas": paginas,
            "resultados": total,
        }

    async def verificar_disponibilidade(self) -> Dict[str, Any]:
        """Verifica se o portal SIGEF está acessível."""
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
