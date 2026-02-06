"""
SICAR — Sistema Nacional de Cadastro Ambiental Rural (Consulta Pública)
https://consultapublica.car.gov.br/publico/imoveis/index
Consulta por: número do CAR
Retorna: area, car, coordenadas, municipio, status, tipo
Gratuito, sem autenticação.
"""
from typing import Any, Dict, Optional
import httpx


class SICARPublicoService:
    """Cliente para consulta pública do SICAR/CAR (gratuito, sem auth)"""

    BASE_URL = "https://consultapublica.car.gov.br/publico"

    def __init__(self) -> None:
        self.timeout = 30.0

    async def _get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            resp = await client.get(
                url,
                params=params,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "AgroADB/1.0",
                },
            )
            if resp.status_code >= 400:
                raise ValueError(f"SICAR Público erro {resp.status_code}: {resp.text[:300]}")
            content_type = resp.headers.get("content-type", "")
            if "json" in content_type:
                return resp.json()
            return {"raw": resp.text[:3000], "status": resp.status_code}

    async def _post(self, url: str, json_data: Optional[Dict[str, Any]] = None, form_data: Optional[Dict[str, Any]] = None) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            if json_data:
                resp = await client.post(
                    url,
                    json=json_data,
                    headers={"Accept": "application/json", "Content-Type": "application/json"},
                )
            else:
                resp = await client.post(
                    url,
                    data=form_data,
                    headers={"Accept": "application/json"},
                )
            if resp.status_code >= 400:
                raise ValueError(f"SICAR Público erro {resp.status_code}: {resp.text[:300]}")
            content_type = resp.headers.get("content-type", "")
            if "json" in content_type:
                return resp.json()
            return {"raw": resp.text[:3000], "status": resp.status_code}

    async def consultar_imovel_por_car(self, car: str) -> Dict[str, Any]:
        """
        Consulta dados de um imóvel no CAR pelo número de registro.
        Retorna: area, car, coordenadas, municipio, status, tipo.
        """
        cleaned = car.strip()
        if not cleaned:
            raise ValueError("Número do CAR é obrigatório")

        # Tenta endpoint de detalhes do imóvel
        url = f"{self.BASE_URL}/imoveis/detalhes"
        try:
            result = await self._get(url, params={"car": cleaned})
            if isinstance(result, dict) and not result.get("raw"):
                return result
        except Exception:
            pass

        # Fallback: tenta via busca
        url_busca = f"{self.BASE_URL}/imoveis/busca"
        try:
            result = await self._post(url_busca, json_data={"car": cleaned})
            if isinstance(result, dict) and not result.get("raw"):
                return result
        except Exception:
            pass

        # Fallback: form data
        try:
            result = await self._post(url_busca, form_data={"car": cleaned})
            if isinstance(result, dict) and not result.get("raw"):
                return result
        except Exception:
            pass

        # Retorna dados de referência caso APIs não funcionem diretamente
        return {
            "car": cleaned,
            "area": None,
            "coordenadas": None,
            "municipio": None,
            "status": None,
            "tipo": None,
            "mensagem": "Consulta disponível via portal público do SICAR.",
            "portal_url": f"{self.BASE_URL}/imoveis/index",
            "instrucoes": "Acesse o portal e informe o número do CAR para consulta manual.",
        }

    async def buscar_imoveis_municipio(self, codigo_ibge: str) -> Dict[str, Any]:
        """Busca imóveis CAR de um município pelo código IBGE"""
        url = f"{self.BASE_URL}/imoveis/index"
        return await self._get(url, params={"municipio": codigo_ibge})

    async def verificar_disponibilidade(self) -> Dict[str, Any]:
        """Verifica se o portal SICAR está acessível"""
        url = f"{self.BASE_URL}/imoveis/index"
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
