"""
SIGEF Parcelas - Scraper de fontes públicas

Complementa a API Conecta SIGEF e o serviço SIGEF Parcelas (WS) com:
- ArcGIS REST (MapServer) de imóveis certificados SIGEF (IBAMA, estados)
- Páginas públicas de listagem de parcelas quando disponíveis

Melhora a base de dados quando as credenciais não estão configuradas.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from app.scrapers.base import BaseScraper


class SigefParcelasScraper(BaseScraper):
    """
    Scraper de parcelas SIGEF a partir de fontes públicas (ArcGIS, portais).
    """

    def __init__(self):
        super().__init__()
        # ArcGIS REST - imóveis certificados SIGEF (públicos)
        self.arcgis_sigef_ibama = "https://pamgia.ibama.gov.br/server/rest/services/01_Publicacoes_Bases/lim_imovel_sigef_publico_a/MapServer/10"
        self.arcgis_sigef_pr = "https://geopr.iat.pr.gov.br/server/rest/services/00_PUBLICACOES/imoveis_certificados_sigef_incra/MapServer/0"

    async def search(
        self,
        codigo_imovel: Optional[str] = None,
        cpf_cnpj: Optional[str] = None,
        municipio: Optional[str] = None,
        uf: Optional[str] = None,
        max_records: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Busca parcelas/imóveis SIGEF por código, CPF/CNPJ, município ou UF.

        Args:
            codigo_imovel: Código do imóvel SIGEF.
            cpf_cnpj: CPF ou CNPJ (apenas dígitos).
            municipio: Nome do município.
            uf: Sigla do estado.
            max_records: Máximo de registros (default 100).

        Returns:
            Lista de imóveis/parcelas encontrados.
        """
        results = []
        try:
            # 1) Tentar ArcGIS REST (fonte pública)
            where_parts = []
            if codigo_imovel:
                where_parts.append(f"CODIGO_IMOVEL = '{codigo_imovel}'")
            if municipio:
                where_parts.append(f"MUNICIPIO LIKE '%{municipio}%'")
            if uf:
                where_parts.append(f"UF = '{uf.upper()}'")
            where = " AND ".join(where_parts) if where_parts else "1=1"

            for layer_url in [self.arcgis_sigef_ibama, self.arcgis_sigef_pr]:
                try:
                    url = f"{layer_url}/query"
                    params = {
                        "where": where,
                        "outFields": "*",
                        "returnGeometry": "false",
                        "f": "json",
                        "resultRecordCount": min(max_records, 500),
                    }
                    response = await self.fetch(url, params=params)
                    if response and response.status_code == 200:
                        data = response.json()
                        features = data.get("features", [])
                        for f in features:
                            attrs = f.get("attributes", {})
                            if attrs:
                                results.append({
                                    **attrs,
                                    "data_source": "sigef_parcelas_scraper_arcgis",
                                    "consulted_at": datetime.utcnow().isoformat(),
                                })
                        if results:
                            break
                except Exception:
                    continue

            if not results and (codigo_imovel or cpf_cnpj):
                # 2) Estrutura de fallback quando não houver dados públicos
                results.append({
                    "codigo_imovel": codigo_imovel,
                    "cpf_cnpj": cpf_cnpj,
                    "municipio": municipio,
                    "uf": uf,
                    "success": False,
                    "message": "Nenhum dado público encontrado. Configure SIGEF_PARCELAS_API_URL ou Conecta SIGEF para consulta completa.",
                    "data_source": "sigef_parcelas_scraper",
                    "consulted_at": datetime.utcnow().isoformat(),
                })
        except Exception as e:
            results.append({
                "success": False,
                "error": str(e),
                "data_source": "sigef_parcelas_scraper",
                "consulted_at": datetime.utcnow().isoformat(),
            })
        return results

    async def search_by_codigo(self, codigo_imovel: str) -> List[Dict[str, Any]]:
        """Busca apenas por código do imóvel."""
        return await self.search(codigo_imovel=codigo_imovel)

    async def search_by_uf_municipio(self, uf: str, municipio: Optional[str] = None) -> List[Dict[str, Any]]:
        """Busca por UF e opcionalmente município (listagem regional)."""
        return await self.search(uf=uf, municipio=municipio, max_records=200)
