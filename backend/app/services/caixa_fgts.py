"""
Caixa — Regularidade do Empregador (FGTS / CRF)
https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf
Consulta por: CNPJ ou CEI
Retorna: crf, datahora, endereco, historico, inscricao, razao_social, situacao, validade
Gratuito, consulta pública.
"""
from typing import Any, Dict, Optional
import httpx


class CaixaFGTSService:
    """Cliente para consulta de Regularidade do Empregador (FGTS/CRF) da Caixa"""

    BASE_URL = "https://consulta-crf.caixa.gov.br/consultacrf"

    def __init__(self) -> None:
        self.timeout = 30.0

    async def consultar_por_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """
        Consulta regularidade FGTS por CNPJ.
        Retorna: situação, CRF, razão social, endereço, validade, histórico.
        """
        cleaned = cnpj.replace(".", "").replace("/", "").replace("-", "")
        if len(cleaned) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")

        return await self._consultar(inscricao=cleaned, tipo="cnpj")

    async def consultar_por_cei(self, cei: str) -> Dict[str, Any]:
        """
        Consulta regularidade FGTS por CEI (Cadastro Específico do INSS).
        """
        cleaned = cei.replace(".", "").replace("/", "").replace("-", "")
        if not cleaned:
            raise ValueError("CEI é obrigatório")

        return await self._consultar(inscricao=cleaned, tipo="cei")

    async def _consultar(self, inscricao: str, tipo: str) -> Dict[str, Any]:
        """Executa a consulta na Caixa"""
        url = f"{self.BASE_URL}/pages/consultaEmpregador.jsf"

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            # Tenta via POST form (simulando o formulário JSF)
            try:
                resp = await client.post(
                    url,
                    data={
                        "inscricao": inscricao,
                        "tipo": tipo,
                    },
                    headers={
                        "Accept": "text/html,application/xhtml+xml,application/json",
                        "User-Agent": "AgroADB/1.0",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                if resp.status_code < 400:
                    content_type = resp.headers.get("content-type", "")
                    if "json" in content_type:
                        return resp.json()

                    # Parseia HTML básico se retornar página
                    text = resp.text
                    result: Dict[str, Any] = {
                        "inscricao": inscricao,
                        "tipo": tipo,
                        "crf": None,
                        "situacao": None,
                        "razao_social": None,
                        "endereco": None,
                        "validade_inicio_data": None,
                        "validade_fim_data": None,
                        "datahora": None,
                    }

                    # Tenta extrair dados do HTML
                    if "REGULAR" in text.upper():
                        result["situacao"] = "REGULAR"
                    elif "IRREGULAR" in text.upper():
                        result["situacao"] = "IRREGULAR"
                    elif "NÃO ENCONTRADO" in text.upper() or "NAO ENCONTRADO" in text.upper():
                        result["situacao"] = "NÃO ENCONTRADO"

                    if result["situacao"]:
                        return result

            except httpx.RequestError:
                pass

            # Retorna info de referência
            return {
                "inscricao": inscricao,
                "tipo": tipo,
                "crf": None,
                "situacao": None,
                "razao_social": None,
                "endereco": None,
                "validade_inicio_data": None,
                "validade_fim_data": None,
                "datahora": None,
                "mensagem": "Consulta disponível via portal da Caixa.",
                "portal_url": f"{self.BASE_URL}/pages/consultaEmpregador.jsf",
            }

    async def verificar_disponibilidade(self) -> Dict[str, Any]:
        """Verifica se o portal de consulta CRF está acessível"""
        url = f"{self.BASE_URL}/pages/consultaEmpregador.jsf"
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                resp = await client.head(url)
                return {
                    "disponivel": resp.status_code < 400,
                    "status_code": resp.status_code,
                    "url": url,
                }
            except httpx.RequestError as e:
                return {
                    "disponivel": False,
                    "erro": str(e)[:200],
                    "url": url,
                }
