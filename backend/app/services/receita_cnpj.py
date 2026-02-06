"""
Receita Federal — Consulta Cadastral de CNPJ
https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Solicitacao.asp
Parâmetros: cnpj
Retorna: razão social, nome fantasia, situação cadastral, atividade econômica,
         endereço, capital social, QSA (sócios), natureza jurídica, porte, etc.
Gratuito, consulta pública.
"""
from typing import Any, Dict, List
import logging
import re
import httpx

from app.core.cache import cache_service
from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected

logger = logging.getLogger(__name__)


class ReceitaCNPJService:
    """Cliente para consulta cadastral de CNPJ na Receita Federal"""

    BASE_URL = "https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva"
    CONSULTA_URL = f"{BASE_URL}/Cnpjreva_Solicitacao.asp"
    RESULTADO_URL = f"{BASE_URL}/Cnpjreva_Comprovante.asp"

    # Fallbacks públicos (BrasilAPI / ReceitaWS / MinhaReceita)
    BRASIL_API_URL = "https://brasilapi.com.br/api/cnpj/v1"
    RECEITAWS_URL = "https://receitaws.com.br/v1/cnpj"
    MINHA_RECEITA_URL = "https://minhareceita.org"

    def __init__(self) -> None:
        self.timeout = 30.0
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/json",
            "User-Agent": "AgroADB/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    @circuit_protected(service_name="receita_cnpj", failure_threshold=5, recovery_timeout=60.0)
    async def consultar(self, cnpj: str) -> Dict[str, Any]:
        """
        Consulta dados cadastrais de CNPJ na Receita Federal.
        Tenta: Receita Federal (direto) → BrasilAPI → ReceitaWS → MinhaReceita.
        Retorna: razão social, situação cadastral, endereço, QSA, capital social, etc.
        """
        cleaned = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
        if len(cleaned) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")

        # ── Cache: tentar recuperar ──────────────────────────────────────
        cache_key = f"cache:receita_cnpj:{cleaned}"
        try:
            cached = await cache_service.get(cache_key)
            if cached is not None:
                cached["_from_cache"] = True
                return cached
        except Exception as exc:
            logger.warning("Cache GET falhou para %s: %s", cache_key, exc)

        # 1) Tenta portal da Receita Federal (direto)
        result = await self._consultar_receita_federal(cleaned)
        if result and result.get("razao_social"):
            try:
                await cache_service.set(cache_key, result, ttl=1800)
            except Exception as exc:
                logger.warning("Cache SET falhou para %s: %s", cache_key, exc)
            return result

        # 2) Fallback: BrasilAPI
        result = await self._consultar_brasilapi(cleaned)
        if result and result.get("razao_social"):
            try:
                await cache_service.set(cache_key, result, ttl=1800)
            except Exception as exc:
                logger.warning("Cache SET falhou para %s: %s", cache_key, exc)
            return result

        # 3) Fallback: ReceitaWS
        result = await self._consultar_receitaws(cleaned)
        if result and result.get("razao_social"):
            try:
                await cache_service.set(cache_key, result, ttl=1800)
            except Exception as exc:
                logger.warning("Cache SET falhou para %s: %s", cache_key, exc)
            return result

        # 4) Fallback: MinhaReceita
        result = await self._consultar_minhareceita(cleaned)
        if result and result.get("razao_social"):
            try:
                await cache_service.set(cache_key, result, ttl=1800)
            except Exception as exc:
                logger.warning("Cache SET falhou para %s: %s", cache_key, exc)
            return result

        # Nenhuma fonte retornou dados completos (não cacheia falhas)
        return {
            "cnpj": cleaned,
            "razao_social": None,
            "situacao_cadastral": None,
            "fonte": "Receita Federal / CNPJ",
            "mensagem": "Consulta disponível via portal da Receita Federal.",
            "portal_url": self.CONSULTA_URL,
        }

    async def _consultar_receita_federal(self, cnpj: str) -> Dict[str, Any] | None:
        """Consulta direta no portal da Receita Federal."""
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, verify=True
        ) as client:
            try:
                # POST no formulário
                resp = await client.post(
                    self.CONSULTA_URL,
                    data={"cnpj": cnpj},
                    headers=self.headers,
                )
                if resp.status_code < 400:
                    ct = resp.headers.get("content-type", "")
                    if "json" in ct:
                        data = resp.json()
                        data["fonte"] = "Receita Federal (direto)"
                        return data

                    result = self._parse_html(resp.text, cnpj)
                    if result.get("razao_social") or result.get("situacao_cadastral"):
                        return result

                # Tenta página de resultado diretamente
                resp2 = await client.get(
                    self.RESULTADO_URL,
                    params={"cnpj": cnpj},
                    headers={
                        "Accept": "text/html,application/json",
                        "User-Agent": "AgroADB/1.0",
                    },
                )
                if resp2.status_code < 400:
                    ct2 = resp2.headers.get("content-type", "")
                    if "json" in ct2:
                        data = resp2.json()
                        data["fonte"] = "Receita Federal (direto)"
                        return data
                    result = self._parse_html(resp2.text, cnpj)
                    if result.get("razao_social") or result.get("situacao_cadastral"):
                        return result

            except httpx.RequestError:
                pass

        return None

    async def _consultar_brasilapi(self, cnpj: str) -> Dict[str, Any] | None:
        """Fallback: BrasilAPI."""
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.get(f"{self.BRASIL_API_URL}/{cnpj}")
                if resp.status_code == 200:
                    data = resp.json()
                    return self._normalizar_brasilapi(data, cnpj)
            except httpx.RequestError:
                pass
        return None

    async def _consultar_receitaws(self, cnpj: str) -> Dict[str, Any] | None:
        """Fallback: ReceitaWS."""
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.get(f"{self.RECEITAWS_URL}/{cnpj}")
                if resp.status_code == 200:
                    data = resp.json()
                    return self._normalizar_receitaws(data, cnpj)
            except httpx.RequestError:
                pass
        return None

    async def _consultar_minhareceita(self, cnpj: str) -> Dict[str, Any] | None:
        """Fallback: MinhaReceita."""
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.get(f"{self.MINHA_RECEITA_URL}/{cnpj}")
                if resp.status_code == 200:
                    data = resp.json()
                    return self._normalizar_minhareceita(data, cnpj)
            except httpx.RequestError:
                pass
        return None

    # ── Normalizadores ─────────────────────────────────────────────────

    def _normalizar_brasilapi(self, data: Dict[str, Any], cnpj: str) -> Dict[str, Any]:
        qsa: List[Dict[str, Any]] = []
        for s in data.get("qsa", []):
            qsa.append({
                "nome": s.get("nome_socio"),
                "qualificacao": s.get("qualificacao_socio"),
                "pais_origem": s.get("pais_origem"),
            })

        atividades_sec: List[Dict[str, Any]] = []
        for a in data.get("cnaes_secundarios", []):
            atividades_sec.append({
                "codigo": a.get("codigo"),
                "descricao": a.get("descricao"),
            })

        return {
            "cnpj": cnpj,
            "razao_social": data.get("razao_social"),
            "nome_fantasia": data.get("nome_fantasia"),
            "situacao_cadastral": data.get("descricao_situacao_cadastral"),
            "situacao_cadastral_data": data.get("data_situacao_cadastral"),
            "abertura_data": data.get("data_inicio_atividade"),
            "natureza_juridica": data.get("natureza_juridica"),
            "porte": data.get("porte"),
            "capital_social": data.get("capital_social"),
            "atividade_economica": {
                "codigo": data.get("cnae_fiscal"),
                "descricao": data.get("cnae_fiscal_descricao"),
            },
            "atividade_economica_secundaria_lista": atividades_sec,
            "endereco": {
                "logradouro": data.get("logradouro"),
                "numero": data.get("numero"),
                "complemento": data.get("complemento"),
                "bairro": data.get("bairro"),
                "municipio": data.get("municipio"),
                "uf": data.get("uf"),
                "cep": data.get("cep"),
            },
            "telefone": data.get("ddd_telefone_1"),
            "email": data.get("email"),
            "qsa": qsa,
            "matriz_filial": "MATRIZ" if data.get("identificador_matriz_filial") == 1 else "FILIAL",
            "fonte": "BrasilAPI",
        }

    def _normalizar_receitaws(self, data: Dict[str, Any], cnpj: str) -> Dict[str, Any]:
        qsa: List[Dict[str, Any]] = []
        for s in data.get("qsa", []):
            qsa.append({
                "nome": s.get("nome"),
                "qualificacao": s.get("qual"),
                "pais_origem": s.get("pais_origem"),
            })

        atividades_sec: List[Dict[str, Any]] = []
        for a in data.get("atividades_secundarias", []):
            atividades_sec.append({
                "codigo": a.get("code"),
                "descricao": a.get("text"),
            })

        return {
            "cnpj": cnpj,
            "razao_social": data.get("nome"),
            "nome_fantasia": data.get("fantasia"),
            "situacao_cadastral": data.get("situacao"),
            "situacao_cadastral_data": data.get("data_situacao"),
            "abertura_data": data.get("abertura"),
            "natureza_juridica": data.get("natureza_juridica"),
            "porte": data.get("porte"),
            "capital_social": data.get("capital_social"),
            "atividade_economica": {
                "codigo": (data.get("atividade_principal") or [{}])[0].get("code"),
                "descricao": (data.get("atividade_principal") or [{}])[0].get("text"),
            },
            "atividade_economica_secundaria_lista": atividades_sec,
            "endereco": {
                "logradouro": data.get("logradouro"),
                "numero": data.get("numero"),
                "complemento": data.get("complemento"),
                "bairro": data.get("bairro"),
                "municipio": data.get("municipio"),
                "uf": data.get("uf"),
                "cep": data.get("cep"),
            },
            "telefone": data.get("telefone"),
            "email": data.get("email"),
            "qsa": qsa,
            "matriz_filial": data.get("tipo"),
            "fonte": "ReceitaWS",
        }

    def _normalizar_minhareceita(self, data: Dict[str, Any], cnpj: str) -> Dict[str, Any]:
        qsa: List[Dict[str, Any]] = []
        for s in data.get("qsa", []):
            qsa.append({
                "nome": s.get("nome_socio"),
                "qualificacao": s.get("qualificacao_socio"),
                "pais_origem": s.get("pais_origem"),
            })

        atividades_sec: List[Dict[str, Any]] = []
        for a in data.get("cnaes_secundarios", []):
            atividades_sec.append({
                "codigo": a.get("codigo"),
                "descricao": a.get("descricao"),
            })

        return {
            "cnpj": cnpj,
            "razao_social": data.get("razao_social"),
            "nome_fantasia": data.get("nome_fantasia"),
            "situacao_cadastral": data.get("descricao_situacao_cadastral"),
            "situacao_cadastral_data": data.get("data_situacao_cadastral"),
            "abertura_data": data.get("data_inicio_atividade"),
            "natureza_juridica": data.get("natureza_juridica"),
            "porte": data.get("descricao_porte"),
            "capital_social": data.get("capital_social"),
            "atividade_economica": {
                "codigo": data.get("cnae_fiscal"),
                "descricao": data.get("cnae_fiscal_descricao"),
            },
            "atividade_economica_secundaria_lista": atividades_sec,
            "endereco": {
                "logradouro": data.get("logradouro"),
                "numero": data.get("numero"),
                "complemento": data.get("complemento"),
                "bairro": data.get("bairro"),
                "municipio": data.get("municipio"),
                "uf": data.get("uf"),
                "cep": data.get("cep"),
            },
            "telefone": data.get("ddd_telefone_1"),
            "email": data.get("email"),
            "qsa": qsa,
            "matriz_filial": "MATRIZ" if data.get("identificador_matriz_filial") == 1 else "FILIAL",
            "fonte": "MinhaReceita",
        }

    # ── HTML Parser (portal Receita Federal) ───────────────────────────

    def _parse_html(self, html: str, cnpj: str) -> Dict[str, Any]:
        """Extrai dados básicos do HTML retornado pela Receita Federal usando BeautifulSoup."""
        from bs4 import BeautifulSoup

        result: Dict[str, Any] = {
            "cnpj": cnpj,
            "fonte": "Receita Federal (direto)",
        }

        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(separator="\n")

        # Map of field name -> list of label patterns to search for
        field_labels = {
            "razao_social": ["Razão Social", "NOME EMPRESARIAL", "Razao Social"],
            "nome_fantasia": ["Nome Fantasia"],
            "situacao_cadastral": ["Situação Cadastral"],
            "situacao_cadastral_data": ["Data da Situação Cadastral", "Data Situação Cadastral"],
            "abertura_data": ["Data de Abertura", "Data Abertura"],
            "natureza_juridica": ["Natureza Jurídica"],
            "porte": ["Porte"],
            "capital_social": ["Capital Social"],
            "atividade_economica": ["Atividade Econômica Principal"],
            "telefone": ["Telefone"],
            "email": ["E-mail", "Email"],
            "endereco_logradouro": ["Logradouro"],
            "endereco_municipio": ["Município"],
            "endereco_uf": ["UF"],
            "endereco_cep": ["CEP"],
            "matriz_filial": ["Tipo", "MATRIZ/FILIAL"],
        }

        # Try to find values in structured HTML (label/value pairs)
        for field, labels in field_labels.items():
            for label in labels:
                # Try finding by text in tags
                tag = soup.find(string=re.compile(re.escape(label), re.IGNORECASE))
                if tag:
                    # Value is usually in the next sibling or parent's next sibling
                    parent = tag.find_parent()
                    if parent:
                        next_elem = parent.find_next_sibling()
                        if next_elem:
                            value = next_elem.get_text(strip=True)
                            if value and value.upper() not in ("", "***", "********"):
                                result[field] = value
                                break

            # Fallback: try regex on plain text
            if field not in result:
                import re as _re
                for label in labels:
                    pattern = _re.escape(label) + r'\s*[:\-]?\s*(.+?)(?:\n|$)'
                    match = _re.search(pattern, text, _re.IGNORECASE)
                    if match:
                        value = match.group(1).strip()
                        if value and value.upper() not in ("", "***", "********"):
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
