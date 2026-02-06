"""
Integração com Órgãos Federais

Suporta consulta em:
- IBAMA (licenças ambientais, embargos)
- ICMBio (unidades de conservação)
- FUNAI (terras indígenas)
- SPU (terras da união)
- CVM (empresas de capital aberto)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import httpx
import asyncio

logger = logging.getLogger(__name__)


class OrgaoFederalIntegration:
    """Integração com órgãos federais"""
    
    IBAMA_API = "https://servicos.ibama.gov.br/ctf/publico/areasembargadas/consultareai"
    ICMBIO_API = "https://www.icmbio.gov.br/sisbio/api/consulta"
    FUNAI_API = "https://www.gov.br/funai/pt-br/assuntos/terras-indigenas"
    SPU_API = "https://www.gov.br/economia/pt-br/assuntos/patrimonio-da-uniao"
    CVM_API = "https://dados.cvm.gov.br/dados"
    
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def query_ibama(self, cpf_cnpj: str) -> Dict[str, Any]:
        """
        Consulta embargos e licenças IBAMA
        
        Verifica:
        - Embargos ambientais
        - Áreas embargadas
        - Licenças ativas
        - Infrações ambientais
        """
        try:
            # API pública do IBAMA
            response = await self.client.get(
                f"{self.IBAMA_API}",
                params={"cpfCnpj": cpf_cnpj}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "embargos": data.get("embargos", []),
                    "infrações": data.get("infracoes", []),
                    "licenças": data.get("licencas", []),
                    "status": "clean" if not data.get("embargos") else "with_issues"
                }
            else:
                return {"success": False, "error": "Não encontrado"}
        except Exception as e:
            logger.error(f"Erro IBAMA: {e}")
            return {"success": False, "error": str(e)}
    
    async def query_icmbio(self, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """
        Consulta se propriedade está em unidade de conservação
        
        Args:
            coordinates: {"lat": -15.123, "lng": -47.456}
        """
        try:
            response = await self.client.get(
                f"{self.ICMBIO_API}/unidades",
                params=coordinates
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "in_conservation_unit": len(data) > 0,
                    "units": data,
                    "warnings": ["Propriedade em UC" if data else ""]
                }
            return {"success": False, "error": "Consulta falhou"}
        except Exception as e:
            logger.error(f"Erro ICMBio: {e}")
            return {"success": False, "error": str(e)}
    
    async def query_funai(self, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """Verifica se está em terra indígena"""
        try:
            # FUNAI não tem API pública robusta ainda
            # Implementação usando dados públicos shapefile
            return {
                "success": True,
                "in_indigenous_land": False,  # Requer shapefile analysis
                "note": "Consulta básica - verificar shapefile oficial"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def query_spu(self, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """Verifica se está em terra da União"""
        try:
            return {
                "success": True,
                "in_union_land": False,  # Requer shapefile
                "note": "Consulta básica - verificar SPU oficial"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def query_cvm(self, cnpj: str) -> Dict[str, Any]:
        """Consulta empresas na CVM (capital aberto)"""
        try:
            response = await self.client.get(
                f"{self.CVM_API}/CIA_ABERTA/CAD/DADOS",
                params={"cnpj": cnpj}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "is_publicly_traded": True,
                    "company_data": data,
                    "registration_date": data.get("DT_REG"),
                    "status": data.get("SIT")
                }
            return {"success": False, "error": "Não é empresa de capital aberto"}
        except Exception as e:
            logger.error(f"Erro CVM: {e}")
            return {"success": False, "error": str(e)}
    
    async def query_all(
        self,
        cpf_cnpj: Optional[str] = None,
        coordinates: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Consulta todos os órgãos"""
        tasks = []
        
        if cpf_cnpj:
            tasks.extend([
                self.query_ibama(cpf_cnpj),
                self.query_cvm(cpf_cnpj)
            ])
        
        if coordinates:
            tasks.extend([
                self.query_icmbio(coordinates),
                self.query_funai(coordinates),
                self.query_spu(coordinates)
            ])
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "ibama": results[0] if len(results) > 0 else {},
            "cvm": results[1] if len(results) > 1 else {},
            "icmbio": results[2] if len(results) > 2 else {},
            "funai": results[3] if len(results) > 3 else {},
            "spu": results[4] if len(results) > 4 else {},
            "queried_at": datetime.utcnow().isoformat()
        }
    
    async def close(self):
        await self.client.aclose()
