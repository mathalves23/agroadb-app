"""Sub-router tribunais (consulta simples, e-SAJ, Projudi)."""
"""
Endpoints REST para Integrações Externas

Expõe todas as integrações via API REST
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse, Response
import io
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict
import logging

from app.core.database import get_db
from app.core.config import settings
from app.api.v1.deps import get_current_user
from app.domain.user import User
from app.integrations.car_estados import CARIntegration, query_car_single
from app.integrations.tribunais import (
    TribunalIntegration,
    TribunalConfig,
    query_process_by_number,
)
from app.integrations.orgaos_federais import OrgaoFederalIntegration
from app.integrations.bureaus import BureauIntegration
from app.integrations.comunicacao import ComunicacaoIntegration
from app.services.sigef_parcelas import SigefParcelasService
from app.services.conecta_sncr import ConectaSNCRService
from app.services.conecta_sigef import ConectaSIGEFService
from app.services.conecta_sicar import ConectaSICARService
from app.services.conecta_sncci import ConectaSNCCIService
from app.services.conecta_sigef_geo import ConectaSIGEFGeoService
from app.services.conecta_cnpj import ConectaCNPJService
from app.services.conecta_cnd import ConectaCNDService
from app.services.conecta_cadin import ConectaCadinService
from app.services.portal_servicos import PortalServicosService
from app.services.servicos_estaduais import ServicosEstaduaisService
from app.services.brasil_api import BrasilAPIService
from app.services.portal_transparencia import PortalTransparenciaService
from app.services.ibge_api import IBGEService
from app.services.tse_api import TSEService
from app.services.cvm_api import CVMService
from app.services.bcb_api import BCBService
from app.services.dados_gov import DadosGovService
from app.services.redesim_api import RedesimService
from app.services.tjmg_api import TJMGService
from app.services.antecedentes_mg import AntecedentesMGService
from app.services.sicar_publico import SICARPublicoService
from app.services.caixa_fgts import CaixaFGTSService
from app.services.bnmp_cnj import BNMPService
from app.services.seeu_cnj import SEEUService
from app.services.sigef_publico import SIGEFPublicoService
from app.services.receita_cpf import ReceitaCPFService
from app.services.receita_cnpj import ReceitaCNPJService
from app.repositories.legal_query import LegalQueryRepository
from app.core.audit import AuditLogger
from app.api.v1.endpoints.integrations_helpers import (
    result_count as _result_count,
    is_credentials_missing as _is_credentials_missing,
    conecta_items as _conecta_items,
    conecta_standard_response as _conecta_standard_response,
)

logger = logging.getLogger(__name__)
audit_logger = AuditLogger()
router = APIRouter()


@router.get("/tribunais/systems", summary="Sistemas e estados de tribunais suportados")
async def list_tribunal_systems() -> Dict[str, Any]:
    """Lista estados com e-SAJ, Projudi e referência ao PJe (contrato estável para clientes)."""
    return {
        "esaj_states": sorted(TribunalConfig.ESAJ_STATES.keys()),
        "projudi_states": sorted(TribunalConfig.PROJUDI_STATES.keys()),
        "pje": {
            "base_url": TribunalConfig.PJE_URL,
            "description": "PJe 2.0 — consulta nacional",
        },
    }


# Schemas
class CARQueryRequest(BaseModel):
    car_code: str
    state: str


class ProcessQueryRequest(BaseModel):
    process_number: str
    state: str
    system: Optional[str] = None


class OrgaoQueryRequest(BaseModel):
    cpf_cnpj: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None


class BureauQueryRequest(BaseModel):
    cpf_cnpj: str
    product: str = "basic"


class NotificationRequest(BaseModel):
    title: str
    message: str
    risk_score: Optional[float] = None
    patterns_found: Optional[int] = None
    slack_channel: Optional[str] = None
    investigation_url: Optional[str] = None


class SigefParcelasRequest(BaseModel):
    cnpj: Optional[str] = None
    codigo_imovel: Optional[str] = None
    cpf: Optional[str] = None
    login_cpf: Optional[str] = None
    login_senha: Optional[str] = None
    pagina: Optional[int] = 1
    pkcs12_cert: Optional[str] = None
    pkcs12_pass: Optional[str] = None
    investigation_id: Optional[int] = None


class ConectaImovelRequest(BaseModel):
    codigo_imovel: str
    investigation_id: Optional[int] = None


class ConectaCpfCnpjRequest(BaseModel):
    cpf_cnpj: str
    investigation_id: Optional[int] = None


class SigefGeoParcelasRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    investigation_id: Optional[int] = None
    page: Optional[int] = None
    size: Optional[int] = None
    sort: Optional[List[str]] = None
    parcelaCodigo: Optional[str] = None
    codigoImovel: Optional[str] = None
    detentorCpf: Optional[str] = None
    detentorCnpj: Optional[str] = None
    titularCpf: Optional[str] = None
    titularCnpj: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None


class CnpjConsultaRequest(BaseModel):
    cnpj: str
    cpf_usuario: str
    investigation_id: Optional[int] = None


class CndConsultaRequest(BaseModel):
    tipoContribuinte: int
    contribuinteConsulta: str
    codigoIdentificacao: str
    gerarCertidaoPdf: Optional[bool] = None
    chave: Optional[str] = None
    investigation_id: Optional[int] = None


class CadinConsultaRequest(BaseModel):
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    investigation_id: Optional[int] = None


class PortalServicosAuthRequest(BaseModel):
    authorization: Optional[str] = None


class ServicosEstaduaisAuthRequest(BaseModel):
    email: str
    senha: str


class ServicosEstaduaisRequest(BaseModel):
    authorization: str
    uf: str
    idCategoria: str
    nomeServico: str
    siglaServico: Optional[str] = None
    descricaoServico: str
    statusServico: str
    tagsServico: Optional[str] = None
    nomesPopulares: Optional[str] = None
    solicitanteServico: Optional[str] = None
    url: Optional[str] = None
    linkServicoDigital: Optional[str] = None
    cidade: Optional[str] = None
    contato: Optional[str] = None
    idServicoOrigem: Optional[str] = None


class SncciParcelasRequest(BaseModel):
    cod_credito: str
    investigation_id: Optional[int] = None


class SncciCreditosAtivosRequest(BaseModel):
    cod_beneficiario: str
    investigation_id: Optional[int] = None


class SncciBoletoRequest(BaseModel):
    cd_plano_pagamento_parcela: str
    investigation_id: Optional[int] = None


# ======================================================================
# Tribunais Estaduais — e-SAJ e Projudi
# ======================================================================

class TribunalEstadualRequest(BaseModel):
    cpf_cnpj: str
    tribunal: str  # tjsp, tjgo, tjms, tjmt, tjpr, tjsc, etc
    investigation_id: Optional[int] = None

@router.post("/tribunais/esaj/1g", summary="Consulta e-SAJ 1º Grau")
async def consulta_esaj_1g(
    request: TribunalEstadualRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta processos de 1º Grau no e-SAJ (Tribunais Estaduais)
    
    Tribunais suportados:
    - TJSP (São Paulo)
    - TJGO (Goiás)
    - TJMS (Mato Grosso do Sul)
    - TJSC (Santa Catarina)
    - TJAL (Alagoas)
    - TJCE (Ceará)
    """
    from app.services.integrations.esaj_service import ESAJService
    
    try:
        async with ESAJService() as service:
            processes = await service.consultar_processos_1g(
                request.cpf_cnpj,
                request.tribunal
            )
        
        # Converter dataclasses para dicts
        processes_dict = [
            {
                'numero_processo': p.numero_processo,
                'tribunal': p.tribunal,
                'grau': p.grau,
                'classe': p.classe,
                'assunto': p.assunto,
                'area': p.area,
                'data_distribuicao': p.data_distribuicao.isoformat() if p.data_distribuicao else None,
                'status': p.status,
                'comarca': p.comarca,
                'foro': p.foro,
                'vara': p.vara,
                'juiz': p.juiz,
                'valor_acao': p.valor_acao,
                'partes': p.partes,
                'movimentacoes': p.movimentacoes,
                'url': p.url
            }
            for p in processes
        ]
        
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": f"esaj_{request.tribunal.lower()}_1g",
                "query_type": "processos_1g",
                "query_params": {"cpf_cnpj": request.cpf_cnpj, "tribunal": request.tribunal},
                "result_count": len(processes),
                "response": {"processos": processes_dict},
            })
        
        return {
            "success": True,
            "tribunal": request.tribunal.upper(),
            "grau": "1G",
            "total_processos": len(processes),
            "processos": processes_dict
        }
    
    except Exception as e:
        logger.error(f"Erro ao consultar e-SAJ 1G: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tribunais/esaj/2g", summary="Consulta e-SAJ 2º Grau")
async def consulta_esaj_2g(
    request: TribunalEstadualRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta processos de 2º Grau no e-SAJ (Tribunais Estaduais)
    """
    from app.services.integrations.esaj_service import ESAJService
    
    try:
        async with ESAJService() as service:
            processes = await service.consultar_processos_2g(
                request.cpf_cnpj,
                request.tribunal
            )
        
        processes_dict = [
            {
                'numero_processo': p.numero_processo,
                'tribunal': p.tribunal,
                'grau': p.grau,
                'classe': p.classe,
                'assunto': p.assunto,
                'area': p.area,
                'data_distribuicao': p.data_distribuicao.isoformat() if p.data_distribuicao else None,
                'status': p.status,
                'comarca': p.comarca,
                'foro': p.foro,
                'vara': p.vara,
                'juiz': p.juiz,
                'valor_acao': p.valor_acao,
                'partes': p.partes,
                'movimentacoes': p.movimentacoes,
                'url': p.url
            }
            for p in processes
        ]
        
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": f"esaj_{request.tribunal.lower()}_2g",
                "query_type": "processos_2g",
                "query_params": {"cpf_cnpj": request.cpf_cnpj, "tribunal": request.tribunal},
                "result_count": len(processes),
                "response": {"processos": processes_dict},
            })
        
        return {
            "success": True,
            "tribunal": request.tribunal.upper(),
            "grau": "2G",
            "total_processos": len(processes),
            "processos": processes_dict
        }
    
    except Exception as e:
        logger.error(f"Erro ao consultar e-SAJ 2G: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tribunais/projudi", summary="Consulta Projudi")
async def consulta_projudi(
    request: TribunalEstadualRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta processos no Projudi (Tribunais Estaduais)
    
    Tribunais suportados:
    - TJMT (Mato Grosso)
    - TJPR (Paraná)
    - TJSC (Santa Catarina)
    - TJAC, TJAM, TJAP, TJBA, TJGO, TJMA, TJPA, TJPI, TJRN, TJRO, TJRR, TJTO
    """
    from app.services.integrations.projudi_service import ProjudiService
    
    try:
        async with ProjudiService() as service:
            processes = await service.consultar_processos(
                request.cpf_cnpj,
                request.tribunal
            )
        
        processes_dict = [
            {
                'numero_processo': p.numero_processo,
                'tribunal': p.tribunal,
                'classe': p.classe,
                'assunto': p.assunto,
                'data_autuacao': p.data_autuacao.isoformat() if p.data_autuacao else None,
                'status': p.status,
                'comarca': p.comarca,
                'vara': p.vara,
                'partes': p.partes,
                'movimentacoes': p.movimentacoes,
                'url': p.url
            }
            for p in processes
        ]
        
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": f"projudi_{request.tribunal.lower()}",
                "query_type": "processos",
                "query_params": {"cpf_cnpj": request.cpf_cnpj, "tribunal": request.tribunal},
                "result_count": len(processes),
                "response": {"processos": processes_dict},
            })
        
        return {
            "success": True,
            "tribunal": request.tribunal.upper(),
            "sistema": "Projudi",
            "total_processos": len(processes),
            "processos": processes_dict
        }
    
    except Exception as e:
        logger.error(f"Erro ao consultar Projudi: {e}")
        raise HTTPException(status_code=500, detail=str(e))

