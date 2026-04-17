"""
SEEU — Sistema Eletrônico de Execução Unificado (CNJ)
https://seeu.pje.jus.br/seeu/processo/consultaPublica.do?actionType=iniciar
Consulta pública de processos de execução penal.
Parâmetros: cpf, cnpj, nome_parte, nome_mae, numero_processo
Retorna: processos encontrados, informações gerais, movimentações, partes.
Gratuito, sem autenticação.
"""
from typing import Any, Dict, Optional
import httpx

from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected


class SEEUService:
    """Cliente para consulta ao SEEU — Sistema Eletrônico de Execução Unificado (CNJ)"""

    BASE_URL = "https://seeu.pje.jus.br/seeu"
    CONSULTA_URL = f"{BASE_URL}/processo/consultaPublica.do"

    def __init__(self) -> None:
        self.timeout = 30.0
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/json",
            "User-Agent": "AgroADB/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="seeu_cnj", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_cpf(
        self, cpf: str, nome_mae: Optional[str] = None
    ) -> Dict[str, Any]:
        """Consulta processos de execução penal por CPF."""
        cleaned = cpf.replace(".", "").replace("-", "").strip()
        if len(cleaned) != 11:
            raise ValueError("CPF deve ter 11 dígitos")

        params: Dict[str, str] = {
            "actionType": "pesquisar",
            "cpf": cleaned,
        }
        if nome_mae:
            params["nomeMae"] = nome_mae.strip()

        return await self._consultar(params, {"cpf": cleaned, "nome_mae": nome_mae})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="seeu_cnj", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """Consulta processos de execução penal por CNPJ."""
        cleaned = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
        if len(cleaned) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")

        params = {
            "actionType": "pesquisar",
            "cnpj": cleaned,
        }
        return await self._consultar(params, {"cnpj": cleaned})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="seeu_cnj", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_nome(
        self, nome_parte: str, nome_mae: Optional[str] = None
    ) -> Dict[str, Any]:
        """Consulta processos de execução penal por nome da parte."""
        if not nome_parte or len(nome_parte.strip()) < 3:
            raise ValueError("Nome da parte deve ter pelo menos 3 caracteres")

        params: Dict[str, str] = {
            "actionType": "pesquisar",
            "nomeParte": nome_parte.strip(),
        }
        if nome_mae:
            params["nomeMae"] = nome_mae.strip()

        return await self._consultar(params, {"nome_parte": nome_parte, "nome_mae": nome_mae})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="seeu_cnj", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_processo(self, numero_processo: str) -> Dict[str, Any]:
        """Consulta processo de execução penal por número do processo."""
        cleaned = numero_processo.replace(".", "").replace("-", "").strip()
        if not cleaned:
            raise ValueError("Número do processo é obrigatório")

        params = {
            "actionType": "pesquisar",
            "numeroProcesso": cleaned,
        }
        return await self._consultar(params, {"numero_processo": numero_processo})

    async def _consultar(
        self, params: Dict[str, str], audit: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa a consulta no portal SEEU"""
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, verify=True
        ) as client:
            # Tenta POST (simulando o formulário)
            try:
                resp = await client.post(
                    self.CONSULTA_URL,
                    data=params,
                    headers=self.headers,
                )
                if resp.status_code < 400:
                    ct = resp.headers.get("content-type", "")
                    if "json" in ct:
                        data = resp.json()
                        processos = data.get("processos_encontrados", data.get("content", []))
                        if isinstance(data, list):
                            processos = data
                        return {
                            "total": len(processos) if isinstance(processos, list) else 0,
                            "processos": processos if isinstance(processos, list) else [],
                            "fonte": "SEEU/CNJ",
                            "consulta": audit,
                        }

                    # Se retornou HTML, tenta extrair informações básicas
                    text = resp.text
                    result: Dict[str, Any] = {
                        "total": 0,
                        "processos": [],
                        "fonte": "SEEU/CNJ",
                        "consulta": audit,
                    }

                    if "Nenhum processo encontrado" in text or "nenhum resultado" in text.lower():
                        result["mensagem"] = "Nenhum processo encontrado"
                    elif "processo" in text.lower() and ("número" in text.lower() or "classe" in text.lower()):
                        result["mensagem"] = "Processos encontrados — consulta detalhada disponível via portal"
                        result["total"] = 1  # Indica existência

                    return result

            except httpx.RequestError:
                pass

            # Tenta GET como fallback
            try:
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
                        data = resp.json()
                        processos = data.get("processos_encontrados", [])
                        return {
                            "total": len(processos) if isinstance(processos, list) else 0,
                            "processos": processos if isinstance(processos, list) else [],
                            "fonte": "SEEU/CNJ",
                            "consulta": audit,
                        }
            except httpx.RequestError:
                pass

        return {
            "total": 0,
            "processos": [],
            "fonte": "SEEU/CNJ",
            "consulta": audit,
            "mensagem": "Consulta disponível via portal SEEU.",
            "portal_url": f"{self.CONSULTA_URL}?actionType=iniciar",
        }

    async def verificar_disponibilidade(self) -> Dict[str, Any]:
        """Verifica se o portal SEEU está acessível"""
        url = f"{self.CONSULTA_URL}?actionType=iniciar"
        async with httpx.AsyncClient(
            timeout=15.0, follow_redirects=True, verify=True
        ) as client:
            try:
                resp = await client.head(url)
                return {
                    "disponivel": resp.status_code < 500,
                    "status_code": resp.status_code,
                    "url": url,
                }
            except httpx.RequestError as e:
                return {
                    "disponivel": False,
                    "erro": str(e)[:200],
                    "url": url,
                }
