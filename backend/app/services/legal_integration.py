"""
Integração com Ferramentas Jurídicas
Sistema de integração com APIs e sistemas jurídicos
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domain.investigation import Investigation, InvestigationStatus
from app.repositories.investigation import InvestigationRepository
from app.repositories.legal_query import LegalQueryRepository

# ==================== Models ====================


class PJeCase(BaseModel):
    """Modelo para processo no PJe"""

    numero_processo: str = Field(..., description="Número do processo CNJ")
    tribunal: str = Field(..., description="Tribunal de origem")
    classe: Optional[str] = None
    assunto: Optional[str] = None
    area: Optional[str] = None
    valor_causa: Optional[float] = None
    data_distribuicao: Optional[datetime] = None
    partes: List[Dict[str, str]] = Field(default_factory=list)
    movimentacoes: List[Dict[str, Any]] = Field(default_factory=list)


class DueDiligenceExport(BaseModel):
    """Modelo para exportação de due diligence"""

    investigation_id: int
    target_name: str
    target_document: str
    executive_summary: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    financial_data: Dict[str, Any]
    legal_data: Dict[str, Any]
    properties: List[Dict[str, Any]]
    companies: List[Dict[str, Any]]
    red_flags: List[str]


class LegalSystemIntegration(BaseModel):
    """Modelo para integração com sistema jurídico"""

    system_name: str
    api_endpoint: str
    api_key: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None
    enabled: bool = True


# ==================== Serviço de Integração com PJe ====================


class PJeService:
    """Serviço para integração com o Processo Judicial Eletrônico (PJe)"""

    def __init__(self):
        self.base_url = settings.PJE_API_URL or "https://api.pje.jus.br"
        self.api_key = settings.PJE_API_KEY
        self.timeout = 30.0

    async def consultar_processo(self, numero_processo: str, tribunal: str) -> Optional[PJeCase]:
        """
        Consulta um processo no PJe

        Args:
            numero_processo: Número do processo no formato CNJ
            tribunal: Código do tribunal (ex: TRT2, TST, STJ)

        Returns:
            Dados do processo ou None se não encontrado
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/processos/{numero_processo}",
                    params={"tribunal": tribunal},
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    return PJeCase(**data)
                elif response.status_code == 404:
                    return None
                else:
                    raise Exception(f"Erro ao consultar PJe: {response.status_code}")

        except httpx.TimeoutException:
            raise Exception("Timeout ao consultar PJe")
        except Exception as e:
            raise Exception(f"Erro na integração com PJe: {str(e)}")

    async def consultar_processos_parte(
        self, cpf_cnpj: str, tipo_parte: str = "qualquer"
    ) -> List[PJeCase]:
        """
        Consulta processos de uma parte (autor, réu, etc)

        Args:
            cpf_cnpj: CPF ou CNPJ da parte
            tipo_parte: Tipo de participação (autor, reu, qualquer)

        Returns:
            Lista de processos encontrados
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/processos/parte",
                    params={"documento": cpf_cnpj, "tipo": tipo_parte},
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    return [PJeCase(**processo) for processo in data.get("processos", [])]
                else:
                    return []

        except Exception as e:
            raise Exception(f"Erro ao consultar processos por parte: {str(e)}")

    async def obter_movimentacoes(self, numero_processo: str) -> List[Dict[str, Any]]:
        """
        Obtém as movimentações de um processo

        Args:
            numero_processo: Número do processo

        Returns:
            Lista de movimentações
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/processos/{numero_processo}/movimentacoes",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 200:
                    return response.json().get("movimentacoes", [])
                else:
                    return []

        except Exception as e:
            raise Exception(f"Erro ao obter movimentações: {str(e)}")


# ==================== Serviço de Due Diligence ====================


def _due_diligence_from_investigation(
    investigation: Investigation,
    legal_queries: List[Any],
) -> DueDiligenceExport:
    props = investigation.properties or []
    comps = investigation.companies or []
    target_doc = investigation.target_cpf_cnpj or ""

    total_results = sum(getattr(q, "result_count", 0) or 0 for q in legal_queries)
    providers = {getattr(q, "provider", "") for q in legal_queries}

    red_flags: List[str] = []
    if investigation.status == InvestigationStatus.FAILED:
        red_flags.append("Investigação concluída com falha — rever fontes e parâmetros")
    if total_results > 80:
        red_flags.append(
            "Volume muito elevado de resultados em consultas legais — priorizar revisão humana"
        )
    for p in props:
        raw = getattr(p, "raw_data", None) or {}
        blob = str(raw).lower()
        if "embargo" in blob or "embarg" in blob:
            red_flags.append(f"Possível menção a embargo em imóvel (id {p.id})")
    for c in comps:
        cap = c.capital or 0
        if cap and cap < 1000:
            red_flags.append(f"Capital social muito baixo em {c.cnpj}")

    if investigation.status == InvestigationStatus.COMPLETED and not red_flags:
        red_flags.append("Nenhum alerta heurístico automático — validar manualmente")

    overall = "low"
    if investigation.status == InvestigationStatus.FAILED or len(red_flags) >= 3:
        overall = "high"
    elif total_results > 25 or len(props) > 5:
        overall = "medium"

    executive_summary = {
        "status": (
            investigation.status.value
            if hasattr(investigation.status, "value")
            else str(investigation.status)
        ),
        "risk_level": {"low": "Baixo", "medium": "Médio", "high": "Alto"}.get(overall, overall),
        "total_properties": len(props),
        "total_companies": len(comps),
        "red_flags_count": len(red_flags),
        "legal_queries": len(legal_queries),
        "legal_providers": sorted(providers),
        "completion_date": (
            investigation.completed_at.isoformat() if investigation.completed_at else None
        ),
    }

    risk_analysis = {
        "overall_risk": overall,
        "financial_risk": "unknown",
        "legal_risk": "high" if total_results > 30 else "medium" if total_results > 5 else "low",
        "operational_risk": "medium" if len(legal_queries) > 15 else "low",
        "factors": [
            f"{len(props)} imóveis indexados",
            f"{len(comps)} empresas indexadas",
            f"{len(legal_queries)} consultas legais registadas",
        ],
    }

    estimated_land_value = sum(
        (p.area_hectares or 0) * 45000.0 for p in props
    )  # ordem de grandeza genérica (R$), não substitui avaliação

    financial_data = {
        "total_assets": round(estimated_land_value, 2),
        "total_liabilities": None,
        "net_worth": None,
        "revenue_last_year": None,
        "note": "Valores patrimoniais são heurísticos (área × constante); não são laudos oficiais",
    }

    legal_data = {
        "legal_query_count": len(legal_queries),
        "total_result_rows": total_results,
        "providers": sorted(providers),
    }

    properties_out = [
        {
            "matricula": p.matricula,
            "car": p.car_number,
            "area_ha": p.area_hectares,
            "estado": p.state,
            "municipio": p.city,
            "fonte": p.data_source,
        }
        for p in props
    ]
    companies_out = [
        {
            "cnpj": c.cnpj,
            "razao_social": c.corporate_name,
            "nome_fantasia": c.trade_name,
            "capital_social": c.capital,
            "fonte": c.data_source,
        }
        for c in comps
    ]

    return DueDiligenceExport(
        investigation_id=investigation.id,
        target_name=investigation.target_name,
        target_document=target_doc,
        executive_summary=executive_summary,
        risk_analysis=risk_analysis,
        financial_data=financial_data,
        legal_data=legal_data,
        properties=properties_out,
        companies=companies_out,
        red_flags=red_flags[:20],
    )


class DueDiligenceService:
    """Serviço para exportação de relatórios de due diligence"""

    @staticmethod
    async def gerar_relatorio_completo(
        db: AsyncSession,
        investigation_id: int,
    ) -> DueDiligenceExport:
        inv_repo = InvestigationRepository(db)
        investigation = await inv_repo.get_with_relations(investigation_id)
        if not investigation:
            raise ValueError(f"Investigação {investigation_id} não encontrada")

        lq_repo = LegalQueryRepository(db)
        legal_queries = await lq_repo.list_by_investigation(investigation_id)

        return _due_diligence_from_investigation(investigation, legal_queries)

    @staticmethod
    async def exportar_para_sistema(
        report: DueDiligenceExport, system_integration: LegalSystemIntegration
    ) -> bool:
        """
        Exporta relatório para sistema jurídico externo

        Args:
            report: Relatório de due diligence
            system_integration: Configuração da integração

        Returns:
            True se exportado com sucesso
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = report.dict()

                headers = {"Content-Type": "application/json"}

                if system_integration.api_key:
                    headers["Authorization"] = f"Bearer {system_integration.api_key}"

                response = await client.post(
                    system_integration.api_endpoint, json=payload, headers=headers
                )

                return response.status_code in [200, 201]

        except Exception as e:
            raise Exception(f"Erro ao exportar para sistema: {str(e)}")


# ==================== Serviço de Integração Geral ====================


class LegalIntegrationService:
    """Serviço geral de integração com ferramentas jurídicas"""

    def __init__(self):
        self.pje_service = PJeService()
        self.due_diligence_service = DueDiligenceService()

    async def sincronizar_processos(
        self,
        db: AsyncSession,
        cpf_cnpj: str,
        investigation_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Sincroniza processos judiciais de uma parte

        Args:
            db: Sessão do banco de dados
            cpf_cnpj: CPF ou CNPJ para consulta
            investigation_id: ID da investigação (opcional)

        Returns:
            Resultado da sincronização
        """
        try:
            # Consultar processos no PJe
            processos = await self.pje_service.consultar_processos_parte(cpf_cnpj)

            # TODO: Salvar processos no banco de dados
            # for processo in processos:
            #     db_processo = JudicialProcess(**processo.dict())
            #     db.add(db_processo)
            # db.commit()

            return {
                "success": True,
                "total_processos": len(processos),
                "processos": [p.dict() for p in processos],
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    async def gerar_e_exportar_due_diligence(
        self,
        db: AsyncSession,
        investigation_id: int,
        target_system: Optional[LegalSystemIntegration] = None,
    ) -> Dict[str, Any]:
        """
        Gera relatório de due diligence e exporta para sistema externo

        Args:
            db: Sessão do banco de dados
            investigation_id: ID da investigação
            target_system: Sistema alvo para exportação (opcional)

        Returns:
            Resultado da operação
        """
        try:
            # Gerar relatório
            report = await self.due_diligence_service.gerar_relatorio_completo(db, investigation_id)

            result = {
                "success": True,
                "report_generated": True,
                "investigation_id": investigation_id,
                "timestamp": datetime.now().isoformat(),
            }

            # Exportar se sistema alvo fornecido
            if target_system and target_system.enabled:
                exported = await self.due_diligence_service.exportar_para_sistema(
                    report, target_system
                )
                result["exported"] = exported
                result["target_system"] = target_system.system_name

            return result

        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}


# Instância global
legal_integration_service = LegalIntegrationService()
