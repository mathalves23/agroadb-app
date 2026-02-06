"""
Banco Central do Brasil — Dados Abertos
https://dadosabertos.bcb.gov.br/
Consulta: PIX Participantes, Taxas de Câmbio, PTAX
Sem autenticação. Gratuito.
"""
from typing import Any, Dict, List, Optional
import httpx
from datetime import date


class BCBService:
    """Cliente para dados abertos do Banco Central (gratuito, sem auth)"""

    OLINDA_URL = "https://olinda.bcb.gov.br/olinda/servico"

    def __init__(self) -> None:
        self.timeout = 30.0

    async def _get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            if resp.status_code >= 400:
                raise ValueError(f"BCB erro {resp.status_code}: {resp.text[:300]}")
            return resp.json()

    async def consultar_pix_participantes(self) -> Dict[str, Any]:
        """Lista participantes do PIX"""
        url = f"{self.OLINDA_URL}/Pix_DadosAbertos/versao/v1/odata/ParticipantesDoEcossistema?$format=json&$top=50"
        return await self._get(url)

    async def consultar_taxa_cambio(self, moeda: str = "USD", data_ref: Optional[str] = None) -> Dict[str, Any]:
        """Consulta taxa de câmbio PTAX"""
        if not data_ref:
            data_ref = date.today().strftime("%m-%d-%Y")
        url = (
            f"{self.OLINDA_URL}/PTAX/versao/v1/odata/"
            f"CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)"
            f"?@moeda='{moeda}'&@dataCotacao='{data_ref}'&$format=json"
        )
        return await self._get(url)

    async def consultar_taxas_juros(self) -> Dict[str, Any]:
        """Consulta taxas de juros de operações de crédito"""
        url = f"{self.OLINDA_URL}/taxaJuros/versao/v2/odata/TaxasJuros?$format=json&$top=30"
        return await self._get(url)

    async def consultar_selic(self) -> Dict[str, Any]:
        """Consulta taxa SELIC"""
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/10?formato=json"
        return await self._get(url)

    async def consultar_ipca(self) -> Dict[str, Any]:
        """Consulta IPCA — inflação"""
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/12?formato=json"
        return await self._get(url)

    async def consultar_cdi(self) -> Dict[str, Any]:
        """Consulta CDI"""
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados/ultimos/10?formato=json"
        return await self._get(url)
