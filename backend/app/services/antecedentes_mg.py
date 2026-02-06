"""
Antecedentes Criminais / MG — Polícia Civil de Minas Gerais
https://www.policiacivil.mg.gov.br/pagina/emissao-atestado
Consulta por: CPF + RG (emitido em MG)
Retorna: conseguiu_emitir_certidao_negativa, numero, codigo
"""
from typing import Any, Dict, Optional
import httpx


class AntecedentesMGService:
    """Cliente para consulta de Antecedentes Criminais da Polícia Civil de MG"""

    BASE_URL = "https://www.policiacivil.mg.gov.br"

    def __init__(self) -> None:
        self.timeout = 30.0

    async def consultar(self, cpf: str, rg: str) -> Dict[str, Any]:
        """
        Consulta antecedentes criminais em MG.
        Requer CPF e RG emitido em Minas Gerais.
        Retorna se conseguiu emitir certidão negativa, número e código.
        """
        cleaned_cpf = cpf.replace(".", "").replace("-", "")
        cleaned_rg = rg.replace(".", "").replace("-", "").replace(" ", "")

        if not cleaned_cpf or len(cleaned_cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        if not cleaned_rg:
            raise ValueError("RG é obrigatório (emitido em MG)")

        url = f"{self.BASE_URL}/antecedentes-criminais/consulta"

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            # Tenta via POST JSON
            try:
                resp = await client.post(
                    url,
                    json={"cpf": cleaned_cpf, "rg": cleaned_rg},
                    headers={"Accept": "application/json", "Content-Type": "application/json"},
                )
                if resp.status_code < 400:
                    content_type = resp.headers.get("content-type", "")
                    if "json" in content_type:
                        return resp.json()
                    return {
                        "conseguiu_emitir_certidao_negativa": None,
                        "numero": None,
                        "codigo": None,
                        "raw_status": resp.status_code,
                        "mensagem": "Resposta recebida mas não em formato JSON. Verifique diretamente no portal.",
                        "portal_url": f"{self.BASE_URL}/pagina/emissao-atestado",
                    }
            except httpx.RequestError:
                pass

            # Tenta via form-data (fallback)
            try:
                resp = await client.post(
                    url,
                    data={"cpf": cleaned_cpf, "rg": cleaned_rg},
                    headers={"Accept": "application/json"},
                )
                if resp.status_code < 400:
                    content_type = resp.headers.get("content-type", "")
                    if "json" in content_type:
                        return resp.json()
            except httpx.RequestError:
                pass

            # Se nenhum método funcionou, retorna info útil
            return {
                "conseguiu_emitir_certidao_negativa": None,
                "numero": None,
                "codigo": None,
                "mensagem": "Serviço de consulta disponível apenas via portal da Polícia Civil de MG.",
                "portal_url": f"{self.BASE_URL}/pagina/emissao-atestado",
                "parametros_enviados": {"cpf": f"***{cleaned_cpf[-4:]}", "rg": f"***{cleaned_rg[-3:]}"},
            }

    async def verificar_disponibilidade(self) -> Dict[str, Any]:
        """Verifica se o portal da Polícia Civil MG está acessível"""
        url = f"{self.BASE_URL}/pagina/emissao-atestado"
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
