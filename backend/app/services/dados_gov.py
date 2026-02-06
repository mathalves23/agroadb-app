"""
Portal Brasileiro de Dados Abertos — dados.gov.br (CGU)
https://dados.gov.br/swagger-ui/index.html
Consulta: Datasets, Organizações, Tags
Sem autenticação para leitura. Gratuito.
"""
from typing import Any, Dict, Optional
import httpx


class DadosGovService:
    """Cliente para dados.gov.br (gratuito, sem auth)"""

    BASE_URL = "https://dados.gov.br/dados/api/publico"

    def __init__(self) -> None:
        self.timeout = 30.0

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            if resp.status_code >= 400:
                raise ValueError(f"dados.gov.br erro {resp.status_code}: {resp.text[:300]}")
            return resp.json()

    async def buscar_datasets(self, query: str, pagina: int = 1, tamanhoPagina: int = 10) -> Dict[str, Any]:
        """Busca datasets por termo"""
        return await self._get("/conjuntos-dados", params={
            "isPrivado": "false",
            "nomeConjuntoDados": query,
            "pagina": pagina,
            "tamanhoPagina": tamanhoPagina
        })

    async def detalhar_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """Detalha um dataset pelo ID"""
        return await self._get(f"/conjuntos-dados/{dataset_id}")

    async def buscar_organizacoes(self, query: str = "", pagina: int = 1) -> Dict[str, Any]:
        """Busca organizações publicadoras"""
        params: Dict[str, Any] = {"pagina": pagina, "tamanhoPagina": 20}
        if query:
            params["nomeOrganizacao"] = query
        return await self._get("/organizacoes", params=params)

    async def buscar_rural(self, pagina: int = 1) -> Dict[str, Any]:
        """Busca datasets relacionados a propriedade rural"""
        return await self.buscar_datasets("rural propriedade terra", pagina=pagina)

    async def buscar_ambiental(self, pagina: int = 1) -> Dict[str, Any]:
        """Busca datasets ambientais"""
        return await self.buscar_datasets("ambiental desmatamento", pagina=pagina)
