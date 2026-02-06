"""
Banco Nacional de Mandados de Prisão (BNMP) — CNJ
https://portalbnmp.pdpj.jus.br/#/pesquisa-peca
Consulta pública: mandados com situação "Aguardando Cumprimento" e vigentes.
Parâmetros: cpf, nome, nome_mae
Retorna até 30 resultados.
Gratuito, sem autenticação.
"""
from typing import Any, Dict, List, Optional
import httpx

from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import circuit_protected


class BNMPService:
    """Cliente para consulta ao Banco Nacional de Mandados de Prisão (BNMP/CNJ)"""

    # API pública do portal BNMP
    BASE_URL = "https://portalbnmp.pdpj.jus.br"
    API_URL = f"{BASE_URL}/bnmpportal/api/pesquisa-pecas/filter"

    def __init__(self) -> None:
        self.timeout = 30.0
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "AgroADB/1.0",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/",
        }

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="bnmp_cnj", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_cpf(self, cpf: str) -> Dict[str, Any]:
        """
        Consulta mandados de prisão vigentes por CPF.
        Retorna mandados com situação "Aguardando Cumprimento".
        """
        cleaned = cpf.replace(".", "").replace("-", "").strip()
        if len(cleaned) != 11:
            raise ValueError("CPF deve ter 11 dígitos")

        payload = {
            "bpiDocumento": cleaned,
            "tipoBuscaPessoa": "CPF",
            "orgaoJudiciario": {},
            "page": 0,
            "size": 30,
            "sort": ["dataExpedicao,desc"],
        }
        return await self._post_search(payload, {"cpf": cleaned})

    @retry_with_backoff(max_retries=2, base_delay=1.0)
    @circuit_protected(service_name="bnmp_cnj", failure_threshold=5, recovery_timeout=60.0)
    async def consultar_por_nome(
        self, nome: str, nome_mae: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Consulta mandados de prisão vigentes por nome (e opcionalmente nome da mãe).
        """
        if not nome or len(nome.strip()) < 3:
            raise ValueError("Nome deve ter pelo menos 3 caracteres")

        payload: Dict[str, Any] = {
            "bpiNome": nome.strip().upper(),
            "tipoBuscaPessoa": "NOME",
            "orgaoJudiciario": {},
            "page": 0,
            "size": 30,
            "sort": ["dataExpedicao,desc"],
        }
        if nome_mae:
            payload["bpiNomeMae"] = nome_mae.strip().upper()

        return await self._post_search(payload, {"nome": nome, "nome_mae": nome_mae})

    async def _post_search(
        self, payload: Dict[str, Any], params_audit: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa a busca no BNMP"""
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, verify=True
        ) as client:
            try:
                resp = await client.post(
                    self.API_URL,
                    json=payload,
                    headers=self.headers,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    mandados = data.get("content", data.get("mandados", []))
                    if isinstance(data, list):
                        mandados = data

                    return {
                        "total": data.get("totalElements", len(mandados) if isinstance(mandados, list) else 0),
                        "mandados": mandados if isinstance(mandados, list) else [],
                        "fonte": "BNMP/CNJ",
                        "consulta": params_audit,
                    }

                # Fallback: tenta GET com query params
                return await self._get_fallback(params_audit)

            except httpx.RequestError:
                return await self._get_fallback(params_audit)

    async def _get_fallback(self, params_audit: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback com GET no endpoint alternativo"""
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, verify=True
        ) as client:
            try:
                search_url = f"{self.BASE_URL}/bnmpportal/api/pesquisa-pecas/filter"
                params: Dict[str, str] = {}
                if params_audit.get("cpf"):
                    params["bpiDocumento"] = params_audit["cpf"]
                    params["tipoBuscaPessoa"] = "CPF"
                elif params_audit.get("nome"):
                    params["bpiNome"] = params_audit["nome"]
                    params["tipoBuscaPessoa"] = "NOME"

                resp = await client.get(
                    search_url,
                    params=params,
                    headers=self.headers,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    mandados = data.get("content", data.get("mandados", []))
                    if isinstance(data, list):
                        mandados = data
                    return {
                        "total": data.get("totalElements", len(mandados) if isinstance(mandados, list) else 0),
                        "mandados": mandados if isinstance(mandados, list) else [],
                        "fonte": "BNMP/CNJ",
                        "consulta": params_audit,
                    }
            except httpx.RequestError:
                pass

        # Se nenhuma abordagem funcionar, retorna referência
        return {
            "total": 0,
            "mandados": [],
            "fonte": "BNMP/CNJ",
            "consulta": params_audit,
            "mensagem": "Consulta disponível via portal BNMP.",
            "portal_url": "https://portalbnmp.pdpj.jus.br/#/pesquisa-peca",
        }

    async def verificar_disponibilidade(self) -> Dict[str, Any]:
        """Verifica se o portal BNMP está acessível"""
        async with httpx.AsyncClient(
            timeout=15.0, follow_redirects=True, verify=True
        ) as client:
            try:
                resp = await client.head(f"{self.BASE_URL}/bnmpportal/api")
                return {
                    "disponivel": resp.status_code < 500,
                    "status_code": resp.status_code,
                    "url": self.BASE_URL,
                }
            except httpx.RequestError as e:
                return {
                    "disponivel": False,
                    "erro": str(e)[:200],
                    "url": self.BASE_URL,
                }
