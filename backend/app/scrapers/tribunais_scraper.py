"""
Tribunais / DataJud Scraper

Complementa a API DataJud com scraping das páginas de consulta pública dos tribunais:
- ESAJ (todos os TJs estaduais)
- Projudi (PR, SC, RS, MS, MT, RO, AC)
- PJe (consulta pública nacional)

Melhora a base de dados quando a API DataJud não está configurada ou para obter
partes e movimentações diretamente do HTML.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.scrapers.base import BaseScraper
from app.integrations.tribunais import TribunalConfig, TribunalIntegration


class TribunaisScraper(BaseScraper):
    """
    Scraper de consulta pública de processos judiciais (ESAJ, Projudi, PJe).
    Retorna dados enriquecidos (classe, assunto, juiz, partes, movimentações).
    """

    def __init__(self):
        super().__init__()
        self.esaj_states = TribunalConfig.ESAJ_STATES
        self.projudi_states = TribunalConfig.PROJUDI_STATES
        self.pje_url = TribunalConfig.PJE_URL

    async def search(
        self,
        process_number: Optional[str] = None,
        state: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Busca processo por número nos tribunais (ESAJ, Projudi ou PJe).

        Args:
            process_number: Número do processo (CNJ ou formato do tribunal).
            state: UF do tribunal (ex: SP, RJ). Se não informado, tenta ESAJ SP.

        Returns:
            Lista com um item por processo encontrado (data_source, process_number, state, system, data).
        """
        if not process_number:
            return []
        uf = (state or "SP").upper()
        results = []
        try:
            integration = TribunalIntegration()
            try:
                # Tenta ESAJ primeiro se o estado tiver
                if uf in self.esaj_states:
                    result = await integration._query_esaj(process_number, uf)
                    if result.success and result.data:
                        results.append(self._result_to_dict(result, "esaj"))
                        return results
                # Projudi
                if uf in self.projudi_states:
                    result = await integration._query_projudi(process_number, uf)
                    if result.success and result.data:
                        results.append(self._result_to_dict(result, "projudi"))
                        return results
                # PJe (nacional)
                result = await integration._query_pje(process_number)
                if result.success and result.data:
                    results.append(self._result_to_dict(result, "pje"))
                    return results
            finally:
                await integration.close()
        except Exception as e:
            results.append({
                "process_number": process_number,
                "state": uf,
                "system": "scraper",
                "success": False,
                "error": str(e),
                "data_source": "tribunais_scraper",
                "consulted_at": datetime.utcnow().isoformat(),
            })
        return results

    def _result_to_dict(self, result, system: str) -> Dict[str, Any]:
        return {
            "process_number": result.process_number,
            "state": result.state,
            "system": system,
            "success": result.success,
            "data": result.data or {},
            "error": result.error,
            "data_source": "tribunais_scraper",
            "consulted_at": datetime.utcnow().isoformat(),
        }

    async def search_esaj(self, process_number: str, state: str) -> List[Dict[str, Any]]:
        """Força busca apenas no ESAJ do estado."""
        if state.upper() not in self.esaj_states:
            return []
        integration = TribunalIntegration()
        try:
            result = await integration._query_esaj(process_number, state.upper())
            return [self._result_to_dict(result, "esaj")] if result.success else []
        finally:
            await integration.close()

    async def search_projudi(self, process_number: str, state: str) -> List[Dict[str, Any]]:
        """Força busca apenas no Projudi do estado."""
        if state.upper() not in self.projudi_states:
            return []
        integration = TribunalIntegration()
        try:
            result = await integration._query_projudi(process_number, state.upper())
            return [self._result_to_dict(result, "projudi")] if result.success else []
        finally:
            await integration.close()

    async def search_pje(self, process_number: str) -> List[Dict[str, Any]]:
        """Força busca apenas no PJe (nacional)."""
        integration = TribunalIntegration()
        try:
            result = await integration._query_pje(process_number)
            return [self._result_to_dict(result, "pje")] if result.success else []
        finally:
            await integration.close()
