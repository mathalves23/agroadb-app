"""
CAR (Cadastro Ambiental Rural) / SICAR - Scraper de páginas públicas

Complementa a API e o CARScraper com scraping das páginas de consulta pública:
- consultapublica.car.gov.br
- servicos.car.gov.br
- car.gov.br

Melhora a base de dados quando as APIs não estão disponíveis ou para obter
dados adicionais de demonstrativos e listagens públicas.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from app.scrapers.base import BaseScraper


class CARPublicScraper(BaseScraper):
    """
    Scraper de consulta pública do CAR/SICAR.
    Tenta extrair dados de páginas HTML quando a API falha ou não está configurada.
    """

    def __init__(self):
        super().__init__()
        self.consulta_publica_base = "https://consultapublica.car.gov.br"
        self.servicos_base = "https://servicos.car.gov.br"
        self.car_portal = "https://www.car.gov.br"

    async def search(
        self,
        car_number: Optional[str] = None,
        cpf_cnpj: Optional[str] = None,
        state: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Busca dados do CAR por número do CAR ou CPF/CNPJ.

        Args:
            car_number: Número do CAR (ex: SP-12345678901234-20240101123456).
            cpf_cnpj: CPF ou CNPJ do declarante (apenas dígitos).
            state: UF para filtrar.

        Returns:
            Lista de imóveis/demonstrativos encontrados.
        """
        results = []
        cpf_cnpj_clean = re.sub(r"[^\d]", "", (cpf_cnpj or ""))
        try:
            if car_number:
                item = await self._fetch_by_car_number(car_number)
                if item:
                    results.append(item)
            if cpf_cnpj_clean and not results:
                items = await self._fetch_by_cpf_cnpj(cpf_cnpj_clean, state)
                results.extend(items)
        except Exception as e:
            results.append({
                "success": False,
                "error": str(e),
                "data_source": "car_public_scraper",
                "consulted_at": datetime.utcnow().isoformat(),
            })
        return results

    async def _fetch_by_car_number(self, car_number: str) -> Optional[Dict[str, Any]]:
        """Tenta obter demonstrativo/situação pelo número do CAR."""
        try:
            # API pública de demonstrativo (mesma usada pelo CARScraper)
            url = f"{self.servicos_base}/api/publico/demonstrativo/{car_number}"
            response = await self.fetch(url)
            if response and response.status_code == 200:
                data = response.json()
                return {
                    "car_number": car_number,
                    "success": True,
                    "data": data,
                    "data_source": "car_public_scraper",
                    "consulted_at": datetime.utcnow().isoformat(),
                }
            # Fallback: tentar página HTML de consulta
            url_html = f"{self.consulta_publica_base}/#/imovel?car={car_number}"
            resp = await self.fetch(url_html)
            if resp and resp.status_code == 200:
                soup = self.parse_html(resp.text)
                parsed = self._parse_car_html(soup, car_number)
                if parsed:
                    return {
                        "car_number": car_number,
                        "success": True,
                        "data": parsed,
                        "data_source": "car_public_scraper_html",
                        "consulted_at": datetime.utcnow().isoformat(),
                    }
        except Exception:
            pass
        return None

    async def _fetch_by_cpf_cnpj(self, cpf_cnpj: str, state: Optional[str]) -> List[Dict[str, Any]]:
        """Tenta listar imóveis por CPF/CNPJ (quando a API ou portal permitir)."""
        results = []
        try:
            # Alguns portais estaduais têm consulta por CPF; tentar endpoint genérico
            url = f"{self.servicos_base}/api/publico/imoveis"
            response = await self.fetch(url, method="GET")
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    items = data if isinstance(data, list) else data.get("imoveis", data.get("items", []))
                    for item in items:
                        if isinstance(item, dict):
                            results.append({
                                **item,
                                "data_source": "car_public_scraper",
                                "consulted_at": datetime.utcnow().isoformat(),
                            })
                except Exception:
                    pass
            if not results:
                # Estrutura vazia com nota para uso futuro
                results.append({
                    "cpf_cnpj": cpf_cnpj,
                    "state": state,
                    "success": False,
                    "message": "Consulta pública CAR por CPF/CNPJ pode exigir autenticação GOV.BR. Use a API Conecta SICAR quando disponível.",
                    "data_source": "car_public_scraper",
                    "consulted_at": datetime.utcnow().isoformat(),
                })
        except Exception as e:
            results.append({
                "cpf_cnpj": cpf_cnpj,
                "success": False,
                "error": str(e),
                "data_source": "car_public_scraper",
                "consulted_at": datetime.utcnow().isoformat(),
            })
        return results

    def _parse_car_html(self, soup, car_number: str) -> Dict[str, Any]:
        """Extrai dados estruturados do HTML de consulta do CAR."""
        data = {"car_number": car_number}
        # Seletores comuns em páginas de demonstrativo CAR
        for label, key in [
            ("Situação", "situacao"),
            ("Status", "status"),
            ("Área", "area_ha"),
            ("Município", "municipio"),
            ("UF", "uf"),
        ]:
            elem = soup.find(string=re.compile(label, re.I))
            if elem:
                parent = elem.parent
                if parent:
                    next_node = parent.find_next(["td", "span", "div"])
                    if next_node:
                        data[key] = next_node.get_text(strip=True)
        return data
