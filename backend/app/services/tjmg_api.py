"""
TJMG — Tribunal de Justiça do Estado de Minas Gerais
Consulta pública de processos via PJe (web scraping do formulário de consulta pública):
  https://pje-consulta-publica.tjmg.jus.br/
Consulta 2ª instância via TJMG Jurisprudência (API pública):
  https://www5.tjmg.jus.br/jurisprudencia/
Gestão de Acessos API: https://gestao-acessos-api.tjmg.jus.br/api-docs
"""
from typing import Any, Dict, List, Optional
import re
import logging
import httpx

from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected

logger = logging.getLogger(__name__)


class TJMGService:
    """Cliente para APIs do TJMG.

    O PJe do TJMG NÃO possui uma API REST pública JSON — a consulta pública
    é um formulário web JSF/Seam. Utilizamos o endpoint interno do PJe que
    o próprio front-end do sistema chama via AJAX, ou a busca de jurisprudência.
    """

    # PJe Consulta Pública (1º grau)
    PJE_BASE_URL = "https://pje-consulta-publica.tjmg.jus.br"
    # Jurisprudência TJMG (2ª instância — API pública com JSON)
    JURIS_BASE_URL = "https://www5.tjmg.jus.br/jurisprudencia"
    # Gestão de Acessos (Swagger)
    GESTAO_BASE_URL = "https://gestao-acessos-api.tjmg.jus.br"

    def __init__(self) -> None:
        self.timeout = 30.0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AgroADB/1.0",
            "Accept": "application/json, text/html, */*",
        }

    # ─── helpers ──────────────────────────────────────────────────────

    async def _get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """GET esperando JSON. Se vier HTML, extrai o que puder."""
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=True) as client:
            resp = await client.get(url, params=params, headers=self.headers)
            ct = resp.headers.get("content-type", "")
            if resp.status_code >= 400:
                if "html" in ct:
                    # PJe retorna HTML em erros — extrair mensagem amigável
                    return self._empty_result(f"TJMG retornou HTTP {resp.status_code}")
                raise ValueError(f"TJMG erro {resp.status_code}: {resp.text[:300]}")
            if "json" in ct:
                return resp.json()
            # HTML — tentar extrair processos via regex simplificado
            return self._parse_pje_html(resp.text)

    async def _post_json(self, url: str, data: Optional[Dict[str, Any]] = None) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=True) as client:
            resp = await client.post(url, json=data, headers={**self.headers, "Content-Type": "application/json"})
            ct = resp.headers.get("content-type", "")
            if resp.status_code >= 400:
                if "html" in ct:
                    return self._empty_result(f"TJMG retornou HTTP {resp.status_code}")
                raise ValueError(f"TJMG erro {resp.status_code}: {resp.text[:300]}")
            if "json" in ct:
                return resp.json()
            return self._parse_pje_html(resp.text)

    @staticmethod
    def _empty_result(mensagem: str = "") -> Dict[str, Any]:
        return {
            "processos": [],
            "total": 0,
            "fonte": "TJMG/PJe",
            "mensagem": mensagem or "Nenhum processo encontrado",
            "consulta_manual": "https://pje-consulta-publica.tjmg.jus.br",
        }

    @staticmethod
    def _parse_pje_html(html: str) -> Dict[str, Any]:
        """Extrai processos de HTML do PJe consulta pública (tabela de resultados)."""
        processos: List[Dict[str, str]] = []
        # O PJe exibe processos em uma tabela; cada <tr> tem número, última movimentação
        rows = re.findall(r'<tr[^>]*class="[^"]*rich-table-row[^"]*"[^>]*>(.*?)</tr>', html, re.DOTALL)
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) >= 2:
                numero = re.sub(r'<[^>]+>', '', cells[0]).strip()
                movimentacao = re.sub(r'<[^>]+>', '', cells[1]).strip()
                if numero and re.search(r'\d{7}', numero):
                    processos.append({"numero": numero, "ultima_movimentacao": movimentacao})

        return {
            "processos": processos,
            "total": len(processos),
            "fonte": "TJMG/PJe",
            "consulta_manual": "https://pje-consulta-publica.tjmg.jus.br",
        }

    # ─── Consulta Pública PJe (1º grau) ────────────────────────────────
    # O PJe consulta pública do TJMG usa formulários JSF, sem API REST.
    # Tentamos o endpoint interno de consulta que o sistema usa via AJAX.

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="tjmg", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_numero(self, numero_processo: str) -> Dict[str, Any]:
        """Consulta processo por número no PJe TJMG."""
        cleaned = numero_processo.replace(".", "").replace("-", "").strip()
        # Tentar endpoint interno do PJe
        url = f"{self.PJE_BASE_URL}/pje/ConsultaPublica/listView.seam"
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=True) as client:
                resp = await client.get(url, params={"numeroProcesso": cleaned}, headers=self.headers)
                if resp.status_code == 200 and "rich-table-row" in resp.text:
                    return self._parse_pje_html(resp.text)
        except Exception as e:
            logger.warning("TJMG PJe consulta por número falhou: %s", e)

        return self._empty_result(f"Processo {numero_processo} — consulte manualmente no PJe TJMG")

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="tjmg", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_cpf(self, cpf: str) -> Dict[str, Any]:
        """Consulta processos por CPF no PJe TJMG."""
        cleaned = cpf.replace(".", "").replace("-", "").strip()
        url = f"{self.PJE_BASE_URL}/pje/ConsultaPublica/listView.seam"
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=True) as client:
                resp = await client.get(url, params={"cpf": cleaned}, headers=self.headers)
                if resp.status_code == 200 and "rich-table-row" in resp.text:
                    return self._parse_pje_html(resp.text)
        except Exception as e:
            logger.warning("TJMG PJe consulta por CPF falhou: %s", e)

        # Fallback: buscar jurisprudência
        juris = await self._buscar_jurisprudencia(cpf=cleaned)
        if juris.get("total", 0) > 0:
            return juris
        return self._empty_result("Nenhum processo público encontrado para este CPF no TJMG")

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="tjmg", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """Consulta processos por CNPJ no PJe TJMG."""
        cleaned = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
        url = f"{self.PJE_BASE_URL}/pje/ConsultaPublica/listView.seam"
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=True) as client:
                resp = await client.get(url, params={"cnpj": cleaned}, headers=self.headers)
                if resp.status_code == 200 and "rich-table-row" in resp.text:
                    return self._parse_pje_html(resp.text)
        except Exception as e:
            logger.warning("TJMG PJe consulta por CNPJ falhou: %s", e)

        juris = await self._buscar_jurisprudencia(cnpj=cleaned)
        if juris.get("total", 0) > 0:
            return juris
        return self._empty_result("Nenhum processo público encontrado para este CNPJ no TJMG")

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="tjmg", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_nome_parte(self, nome_parte: str) -> Dict[str, Any]:
        """Consulta processos por nome da parte no PJe TJMG."""
        url = f"{self.PJE_BASE_URL}/pje/ConsultaPublica/listView.seam"
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=True) as client:
                resp = await client.get(url, params={"nomeParte": nome_parte}, headers=self.headers)
                if resp.status_code == 200 and "rich-table-row" in resp.text:
                    return self._parse_pje_html(resp.text)
        except Exception as e:
            logger.warning("TJMG PJe consulta por nome falhou: %s", e)

        return self._empty_result(f"Nenhum processo encontrado para '{nome_parte}' no TJMG")

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="tjmg", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_advogado(self, nome_advogado: str) -> Dict[str, Any]:
        """Consulta processos por nome do advogado no PJe TJMG."""
        url = f"{self.PJE_BASE_URL}/pje/ConsultaPublica/listView.seam"
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=True) as client:
                resp = await client.get(url, params={"nomeAdvogado": nome_advogado}, headers=self.headers)
                if resp.status_code == 200 and "rich-table-row" in resp.text:
                    return self._parse_pje_html(resp.text)
        except Exception as e:
            logger.warning("TJMG PJe consulta por advogado falhou: %s", e)

        return self._empty_result(f"Nenhum processo encontrado para advogado '{nome_advogado}' no TJMG")

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="tjmg", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_completa(
        self,
        cpf: Optional[str] = None,
        cnpj: Optional[str] = None,
        nome_parte: Optional[str] = None,
        nome_advogado: Optional[str] = None,
        numero_processo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Consulta completa combinando múltiplos critérios."""
        if numero_processo:
            return await self.consultar_por_numero(numero_processo)
        if cpf:
            return await self.consultar_por_cpf(cpf)
        if cnpj:
            return await self.consultar_por_cnpj(cnpj)
        if nome_parte:
            return await self.consultar_por_nome_parte(nome_parte)
        if nome_advogado:
            return await self.consultar_por_advogado(nome_advogado)
        raise ValueError("Informe pelo menos um parâmetro de busca")

    # ─── Jurisprudência TJMG (API pública com dados JSON-like) ──────

    async def _buscar_jurisprudencia(
        self,
        cpf: Optional[str] = None,
        cnpj: Optional[str] = None,
        texto_livre: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Busca jurisprudência no portal do TJMG (2ª instância)."""
        query = cpf or cnpj or texto_livre or ""
        if not query:
            return self._empty_result()

        url = f"{self.JURIS_BASE_URL}/pesquisaPalavrasEspelhoAcordao.do"
        params = {
            "palavrasConsulta": query,
            "tipoConsulta": "1",
            "orderByData": "2",
            "linhasPorPagina": "10",
            "pesquisarPor": "ementa",
            "pesquisaTesauro": "true",
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=True) as client:
                resp = await client.get(url, params=params, headers=self.headers)
                if resp.status_code == 200:
                    # Extrair emendas da página de resultados
                    resultados = self._parse_jurisprudencia_html(resp.text)
                    return {
                        "processos": resultados,
                        "total": len(resultados),
                        "fonte": "TJMG/Jurisprudência",
                        "consulta_manual": f"{self.JURIS_BASE_URL}/pesquisaPalavrasEspelhoAcordao.do?palavrasConsulta={query}",
                    }
        except Exception as e:
            logger.warning("TJMG jurisprudência falhou: %s", e)

        return self._empty_result()

    @staticmethod
    def _parse_jurisprudencia_html(html: str) -> List[Dict[str, str]]:
        """Extrai resultados de jurisprudência da página HTML do TJMG."""
        resultados: List[Dict[str, str]] = []
        # Cada resultado tem número do processo e ementa
        blocos = re.findall(
            r'Processo[:\s]*([\d.\-/]+).*?Ementa[:\s]*(.*?)(?=Processo[:\s]*[\d.\-/]+|$)',
            html, re.DOTALL | re.IGNORECASE,
        )
        for numero, ementa in blocos[:10]:
            ementa_limpa = re.sub(r'<[^>]+>', '', ementa).strip()[:500]
            resultados.append({
                "numero": numero.strip(),
                "ementa": ementa_limpa,
                "fonte": "TJMG/Jurisprudência",
            })
        return resultados

    # ─── Gestão de Acessos API ───

    async def gestao_configuration(self) -> Dict[str, Any]:
        """Consulta configuração do ambiente da API de Gestão de Acessos."""
        url = f"{self.GESTAO_BASE_URL}/configuration"
        return await self._get_json(url)

    async def gestao_perfis(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Lista perfis ativos."""
        url = f"{self.GESTAO_BASE_URL}/v1/perfis/ativos"
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            resp = await client.get(url, headers={**self.headers, **headers})
            if resp.status_code >= 400:
                return self._empty_result(f"Gestão de Acessos erro {resp.status_code}")
            return resp.json()

    async def gestao_autorizacoes(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Lista autorizações."""
        url = f"{self.GESTAO_BASE_URL}/v1/autorizacoes/"
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            resp = await client.get(url, headers={**self.headers, **headers})
            if resp.status_code >= 400:
                return self._empty_result(f"Gestão de Acessos erro {resp.status_code}")
            return resp.json()

    async def gestao_usuario_ativo(self, username: str, token: Optional[str] = None) -> Dict[str, Any]:
        """Verifica se um usuário está ativo."""
        url = f"{self.GESTAO_BASE_URL}/v1/usuarios/{username}/ativo"
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            resp = await client.get(url, headers={**self.headers, **headers})
            if resp.status_code >= 400:
                return self._empty_result(f"Gestão de Acessos erro {resp.status_code}")
            return resp.json()
