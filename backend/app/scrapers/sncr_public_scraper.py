"""
SNCR / CCIR - Scraper de páginas públicas

Complementa a API Conecta SNCR e o INCRAScraper com scraping das páginas
de consulta pública do SNCR/CCIR (INCRA):
- sncr.serpro.gov.br (emissão e consulta CCIR)
- Portal INCRA (quando houver consulta pública)

Melhora a base de dados quando as credenciais Conecta não estão configuradas.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from app.scrapers.base import BaseScraper


class SNCRPublicScraper(BaseScraper):
    """
    Scraper de consulta pública SNCR/CCIR.
    Tenta extrair dados das páginas HTML do Serpro/INCRA.
    """

    def __init__(self):
        super().__init__()
        self.sncr_base = "https://sncr.serpro.gov.br"
        self.ccir_consulta = f"{self.sncr_base}/ccir/consulta"
        self.ccir_emissao = f"{self.sncr_base}/ccir/emissao"

    def _clean_cpf_cnpj(self, value: str) -> str:
        return re.sub(r"[^\d]", "", value or "")

    async def search(
        self,
        cpf_cnpj: Optional[str] = None,
        codigo_imovel: Optional[str] = None,
        ccir_number: Optional[str] = None,
        state: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Busca dados SNCR/CCIR por CPF/CNPJ, código do imóvel ou número CCIR.

        Args:
            cpf_cnpj: CPF ou CNPJ do proprietário.
            codigo_imovel: Código do imóvel rural (13 dígitos).
            ccir_number: Número do CCIR (ex: 12345678-2024).
            state: UF (opcional).

        Returns:
            Lista de imóveis/CCIRs encontrados.
        """
        results = []
        try:
            if ccir_number:
                item = await self._fetch_by_ccir(ccir_number)
                if item:
                    results.append(item)
            if codigo_imovel and not results:
                item = await self._fetch_by_codigo_imovel(codigo_imovel)
                if item:
                    results.append(item)
            if cpf_cnpj and not results:
                items = await self._fetch_by_cpf_cnpj(self._clean_cpf_cnpj(cpf_cnpj), state)
                results.extend(items)
        except Exception as e:
            results.append({
                "success": False,
                "error": str(e),
                "data_source": "sncr_public_scraper",
                "consulted_at": datetime.utcnow().isoformat(),
            })
        return results

    async def _fetch_by_ccir(self, ccir_number: str) -> Optional[Dict[str, Any]]:
        """Tenta consultar CCIR pelo número."""
        try:
            ccir_clean = re.sub(r"[^\d-]", "", ccir_number)
            url = f"{self.ccir_consulta}/{ccir_clean}"
            response = await self.fetch(url)
            if response and response.status_code == 200:
                # Se for JSON (API)
                try:
                    data = response.json()
                    return {
                        "ccir_number": ccir_number,
                        "success": True,
                        "data": data,
                        "data_source": "sncr_public_scraper",
                        "consulted_at": datetime.utcnow().isoformat(),
                    }
                except Exception:
                    pass
                # HTML: extrair dados da página
                soup = self.parse_html(response.text)
                parsed = self._parse_ccir_html(soup, ccir_number)
                return {
                    "ccir_number": ccir_number,
                    "success": True,
                    "data": parsed,
                    "data_source": "sncr_public_scraper_html",
                    "consulted_at": datetime.utcnow().isoformat(),
                }
        except Exception:
            pass
        return None

    async def _fetch_by_codigo_imovel(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Tenta consultar por código do imóvel."""
        try:
            codigo_clean = re.sub(r"[^\d]", "", codigo)[:20]
            if len(codigo_clean) < 10:
                return None
            # Endpoint comum em APIs SNCR
            url = f"{self.sncr_base}/api-sncr/v2/consultarImovelPorCodigo/{codigo_clean}"
            response = await self.fetch(url)
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        "codigo_imovel": codigo_clean,
                        "success": True,
                        "data": data,
                        "data_source": "sncr_public_scraper",
                        "consulted_at": datetime.utcnow().isoformat(),
                    }
                except Exception:
                    pass
        except Exception:
            pass
        return None

    async def _fetch_by_cpf_cnpj(self, cpf_cnpj: str, state: Optional[str]) -> List[Dict[str, Any]]:
        """Tenta listar imóveis por CPF/CNPJ (página de consulta ou API)."""
        results = []
        try:
            # Muitas consultas SNCR por CPF/CNPJ exigem autenticação; tentar página de emissão/consulta
            response = await self.fetch(self.ccir_emissao)
            if response and response.status_code == 200:
                soup = self.parse_html(response.text)
                # Verificar se há formulário público (campo CPF/CNPJ)
                form = soup.find("form")
                if form and ("cpf" in form.get_text().lower() or "cnpj" in form.get_text().lower()):
                    results.append({
                        "cpf_cnpj": cpf_cnpj,
                        "state": state,
                        "success": True,
                        "message": "Página de emissão CCIR disponível. Consulta por CPF/CNPJ pode exigir login.",
                        "data_source": "sncr_public_scraper",
                        "consulted_at": datetime.utcnow().isoformat(),
                    })
                else:
                    results.append({
                        "cpf_cnpj": cpf_cnpj,
                        "success": False,
                        "message": "Configure CONECTA_SNCR_* no .env para consulta por CPF/CNPJ. Scraper SNCR complementa com consulta por CCIR ou código do imóvel.",
                        "data_source": "sncr_public_scraper",
                        "consulted_at": datetime.utcnow().isoformat(),
                    })
            else:
                results.append({
                    "cpf_cnpj": cpf_cnpj,
                    "success": False,
                    "message": "Portal SNCR indisponível ou consulta por CPF/CNPJ requer credenciais Conecta.",
                    "data_source": "sncr_public_scraper",
                    "consulted_at": datetime.utcnow().isoformat(),
                })
        except Exception as e:
            results.append({
                "cpf_cnpj": cpf_cnpj,
                "success": False,
                "error": str(e),
                "data_source": "sncr_public_scraper",
                "consulted_at": datetime.utcnow().isoformat(),
            })
        return results

    def _parse_ccir_html(self, soup, ccir_number: str) -> Dict[str, Any]:
        """Extrai dados do HTML de consulta CCIR."""
        data = {"ccir_number": ccir_number}
        for label, key in [
            ("Situação", "situacao"),
            ("Proprietário", "proprietario"),
            ("Imóvel", "imovel"),
            ("Área", "area_ha"),
            ("Validade", "validade"),
        ]:
            elem = soup.find(string=re.compile(label, re.I))
            if elem and elem.parent:
                next_ = elem.parent.find_next(["td", "span", "div"])
                if next_:
                    data[key] = next_.get_text(strip=True)
        return data
