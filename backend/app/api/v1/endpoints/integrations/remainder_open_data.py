"""Integrações — dados abertos, status, CAR, Conecta, SIGEF, birôs e health."""

import io
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.api.v1.endpoints.integrations_helpers import conecta_items as _conecta_items
from app.api.v1.endpoints.integrations_helpers import (
    conecta_standard_response as _conecta_standard_response,
)
from app.api.v1.endpoints.integrations_helpers import (
    is_credentials_missing as _is_credentials_missing,
)
from app.api.v1.endpoints.integrations_helpers import result_count as _result_count
from app.core.audit import AuditLogger
from app.core.config import settings
from app.core.database import get_db
from app.domain.user import User
from app.integrations.bureaus import BureauIntegration
from app.integrations.car_estados import CARIntegration, query_car_single
from app.integrations.comunicacao import ComunicacaoIntegration
from app.integrations.orgaos_federais import OrgaoFederalIntegration
from app.integrations.tribunais import TribunalIntegration, query_process_by_number
from app.services.antecedentes_mg import AntecedentesMGService
from app.services.bcb_api import BCBService
from app.services.bnmp_cnj import BNMPService
from app.services.brasil_api import BrasilAPIService
from app.services.caixa_fgts import CaixaFGTSService
from app.services.conecta_cadin import ConectaCadinService
from app.services.conecta_cnd import ConectaCNDService
from app.services.conecta_cnpj import ConectaCNPJService
from app.services.conecta_sicar import ConectaSICARService
from app.services.conecta_sigef import ConectaSIGEFService
from app.services.conecta_sigef_geo import ConectaSIGEFGeoService
from app.services.conecta_sncci import ConectaSNCCIService
from app.services.conecta_sncr import ConectaSNCRService
from app.services.cvm_api import CVMService
from app.services.dados_gov import DadosGovService
from app.services.ibge_api import IBGEService
from app.services.legal_query_audit import record_legal_query_if_investigation
from app.services.portal_servicos import PortalServicosService
from app.services.portal_transparencia import PortalTransparenciaService
from app.services.receita_cnpj import ReceitaCNPJService
from app.services.receita_cpf import ReceitaCPFService
from app.services.redesim_api import RedesimService
from app.services.seeu_cnj import SEEUService
from app.services.servicos_estaduais import ServicosEstaduaisService
from app.services.sicar_publico import SICARPublicoService
from app.services.sigef_parcelas import SigefParcelasService
from app.services.sigef_publico import SIGEFPublicoService
from app.services.tjmg_api import TJMGService
from app.services.tse_api import TSEService

logger = logging.getLogger(__name__)
audit_logger = AuditLogger()

router = APIRouter()


# Status de configuração
@router.get("/status", summary="Status das integrações externas")
async def integrations_status(current_user: User = Depends(get_current_user)):
    datajud_configured = bool(settings.DATAJUD_API_URL.strip() and settings.DATAJUD_API_KEY)
    sigef_configured = bool(settings.SIGEF_PARCELAS_API_URL.strip())
    return {
        "datajud": {
            "configured": datajud_configured,
            "api_url": settings.DATAJUD_API_URL.strip(),
        },
        "sigef_parcelas": {
            "configured": sigef_configured,
            "api_url": settings.SIGEF_PARCELAS_API_URL.strip(),
        },
        "conecta": {
            "sncr": bool(settings.CONECTA_SNCR_API_URL.strip()),
            "sigef": bool(settings.CONECTA_SIGEF_API_URL.strip()),
            "sicar": bool(settings.CONECTA_SICAR_API_URL.strip()),
            "sncci": bool(settings.CONECTA_SNCCI_API_URL.strip()),
            "sigef_geo": bool(settings.CONECTA_SIGEF_GEO_API_URL.strip()),
            "cnpj": bool(settings.CONECTA_CNPJ_API_URL.strip()),
            "cnd": bool(settings.CONECTA_CND_API_URL.strip()),
            "cadin": bool(settings.CONECTA_CADIN_API_URL.strip()),
        },
        "portal_servicos": {
            "configured": bool(settings.PORTAL_SERVICOS_API_URL.strip()),
            "api_url": settings.PORTAL_SERVICOS_API_URL.strip(),
        },
        "servicos_estaduais": {
            "configured": bool(settings.SERVICOS_ESTADUAIS_API_URL.strip()),
            "api_url": settings.SERVICOS_ESTADUAIS_API_URL.strip(),
        },
        "brasil_api": {
            "configured": True,
            "api_url": "https://brasilapi.com.br/api",
            "auth_required": False,
        },
        "portal_transparencia": {
            "configured": bool(getattr(settings, "PORTAL_TRANSPARENCIA_API_KEY", "")),
            "api_url": "https://api.portaldatransparencia.gov.br/api-de-dados",
            "auth_required": True,
        },
        "ibge": {
            "configured": True,
            "api_url": "https://servicodados.ibge.gov.br/api",
            "auth_required": False,
        },
        "tse": {
            "configured": True,
            "api_url": "https://dadosabertos.tse.jus.br/api/3",
            "auth_required": False,
        },
        "cvm": {
            "configured": True,
            "api_url": "https://dados.cvm.gov.br/api/3",
            "auth_required": False,
        },
        "bcb": {
            "configured": True,
            "api_url": "https://olinda.bcb.gov.br",
            "auth_required": False,
        },
        "dados_gov": {
            "configured": True,
            "api_url": "https://dados.gov.br/dados/api/publico",
            "auth_required": False,
        },
        "redesim_cnpj": {
            "configured": True,
            "api_url": "https://receitaws.com.br/v1/cnpj",
            "auth_required": False,
        },
        "tjmg": {
            "configured": True,
            "api_url": "https://pje-consulta-publica.tjmg.jus.br",
            "auth_required": False,
        },
        "antecedentes_mg": {
            "configured": True,
            "api_url": "https://www.policiacivil.mg.gov.br",
            "auth_required": False,
        },
        "sicar_publico": {
            "configured": True,
            "api_url": "https://consultapublica.car.gov.br/publico",
            "auth_required": False,
        },
        "caixa_fgts": {
            "configured": True,
            "api_url": "https://consulta-crf.caixa.gov.br",
            "auth_required": False,
        },
        "bnmp_cnj": {
            "configured": True,
            "api_url": "https://portalbnmp.pdpj.jus.br",
            "auth_required": False,
        },
        "seeu_cnj": {
            "configured": True,
            "api_url": "https://seeu.pje.jus.br/seeu",
            "auth_required": False,
        },
        "sigef_publico": {
            "configured": True,
            "api_url": "https://sigef.incra.gov.br/consultar/parcelas",
            "auth_required": False,
        },
        "receita_cpf": {
            "configured": True,
            "api_url": "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao",
            "auth_required": False,
        },
        "receita_cnpj": {
            "configured": True,
            "api_url": "https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva",
            "auth_required": False,
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


class BrasilAPICnpjRequest(BaseModel):
    cnpj: str
    investigation_id: Optional[int] = None


class BrasilAPICepRequest(BaseModel):
    cep: str


# CAR Endpoints


@router.post("/car/query", summary="Consultar CAR")
async def query_car(request: CARQueryRequest, current_user: User = Depends(get_current_user)):
    """Consulta CAR em um estado específico"""
    try:
        result = await query_car_single(request.car_code, request.state)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/car/states", summary="Listar estados disponíveis")
async def list_car_states(current_user: User = Depends(get_current_user)):
    """Lista todos os estados com sistema CAR"""
    from app.integrations.car_estados import CARStateConfig

    return {
        "states": list(CARStateConfig.URLS.keys()),
        "total": len(CARStateConfig.URLS),
        "with_api": CARStateConfig.HAS_API,
    }


# Tribunais Endpoints


@router.post("/brasil-api/cnpj", summary="BrasilAPI - Consulta CNPJ (gratuito)")
async def brasil_api_cnpj(
    request: BrasilAPICnpjRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BrasilAPIService()
    try:
        result = await service.consultar_cnpj(request.cnpj)
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="brasil_api",
            query_type="cnpj",
            query_params={"cnpj": request.cnpj},
            result_count=1 if "cnpj" in result else 0,
            response=result,
        )
        return _conecta_standard_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/brasil-api/cep", summary="BrasilAPI - Consulta CEP (gratuito)")
async def brasil_api_cep(
    request: BrasilAPICepRequest,
    current_user: User = Depends(get_current_user),
):
    service = BrasilAPIService()
    try:
        return await service.consultar_cep(request.cep)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brasil-api/bancos", summary="BrasilAPI - Listar bancos")
async def brasil_api_bancos(current_user: User = Depends(get_current_user)):
    service = BrasilAPIService()
    try:
        return await service.listar_bancos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brasil-api/ddd/{ddd}", summary="BrasilAPI - Consulta DDD")
async def brasil_api_ddd(ddd: str, current_user: User = Depends(get_current_user)):
    service = BrasilAPIService()
    try:
        return await service.consultar_ddd(ddd)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brasil-api/pix/participantes", summary="BrasilAPI - Participantes PIX")
async def brasil_api_pix(current_user: User = Depends(get_current_user)):
    service = BrasilAPIService()
    try:
        return await service.consultar_pix()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brasil-api/corretoras", summary="BrasilAPI - Corretoras CVM")
async def brasil_api_corretoras(current_user: User = Depends(get_current_user)):
    service = BrasilAPIService()
    try:
        return await service.consultar_corretoras()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brasil-api/municipios/{uf}", summary="BrasilAPI - Municípios por UF")
async def brasil_api_municipios(uf: str, current_user: User = Depends(get_current_user)):
    service = BrasilAPIService()
    try:
        return await service.listar_municipios_uf(uf)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health Check


@router.get("/health", summary="Status das integrações")
async def integrations_health():
    """Verifica status de todas as integrações"""
    return {
        "car": {"status": "available", "states": 27},
        "tribunais": {"status": "available", "systems": ["esaj", "projudi", "pje"]},
        "orgaos_federais": {
            "status": "available",
            "services": ["ibama", "icmbio", "funai", "spu", "cvm"],
        },
        "bureaus": {"status": "requires_api_keys", "services": ["serasa", "boavista"]},
        "comunicacao": {"status": "requires_webhooks", "services": ["slack", "teams"]},
        "ocr": {"status": "available", "services": ["tesseract", "pdf2image"]},
        "environmental": {"status": "available", "services": ["ibama", "funai", "icmbio"]},
    }
