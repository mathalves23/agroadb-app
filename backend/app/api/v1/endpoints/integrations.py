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
from app.integrations.tribunais import TribunalIntegration, query_process_by_number
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

logger = logging.getLogger(__name__)
audit_logger = AuditLogger()

router = APIRouter(prefix="/integrations", tags=["integrations"])
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


def _result_count(result: Any) -> int:
    if isinstance(result, list):
        return len(result)
    if isinstance(result, dict):
        for key in ("parcelas", "resultados", "itens", "items", "processos", "hits"):
            value = result.get(key)
            if isinstance(value, list):
                return len(value)
    return 0


def _is_credentials_missing(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "não configuradas" in msg or "credenciais conecta" in msg or "credenciais ausentes" in msg


def _conecta_items(result: Any) -> list:
    """Extrai lista de itens do resultado para resposta padronizada."""
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for key in ("items", "itens", "resultados", "parcelas", "hits", "data"):
            value = result.get(key)
            if isinstance(value, list):
                return value
        return [result]
    return [result] if result is not None else []


def _conecta_standard_response(
    result: Any,
    pagination: Optional[Dict[str, Any]] = None,
    warnings: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Resposta padronizada para endpoints Conecta: success, items, pagination, warnings."""
    return {
        "success": True,
        "items": _conecta_items(result),
        "data": result,
        "pagination": pagination or {},
        "warnings": warnings or [],
    }


@router.post("/sigef/parcelas", summary="Consultar parcelas SIGEF (WS externo)")
async def query_sigef_parcelas(
    request: SigefParcelasRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Consulta parcelas SIGEF via web service configurável"""
    service = SigefParcelasService()
    params: Dict[str, Any] = {k: v for k, v in request.model_dump().items() if v not in (None, "")}
    try:
        result = await service.query(params)
        count = _result_count(result)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "sigef_parcelas",
                "query_type": "parcelas",
                "query_params": params,
                "result_count": count,
                "response": result if isinstance(result, dict) else {"result": result},
            })
        await audit_logger.log_action(
            db=db,
            user_id=current_user.id,
            action="consulta_sigef_parcelas",
            resource_type="sigef_parcelas",
            resource_id=str(request.investigation_id) if request.investigation_id else "ad-hoc",
            details={"result_count": count, "param_keys": list(params.keys())},
            success=True,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/sncr/imovel", summary="Consultar SNCR por código de imóvel")
async def conecta_sncr_imovel(
    request: ConectaImovelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSNCRService()
    try:
        result = await service.consultar_imovel(request.codigo_imovel)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_sncr",
                "query_type": "imovel",
                "query_params": {"codigo_imovel": request.codigo_imovel},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        if _is_credentials_missing(e):
            raise HTTPException(
                status_code=503,
                detail=str(e),
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/sncr/cpf-cnpj", summary="Consultar SNCR por CPF/CNPJ")
async def conecta_sncr_cpf_cnpj(
    request: ConectaCpfCnpjRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSNCRService()
    try:
        result = await service.consultar_por_cpf_cnpj(request.cpf_cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_sncr",
                "query_type": "cpf_cnpj",
                "query_params": {"cpf_cnpj": request.cpf_cnpj},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        if _is_credentials_missing(e):
            raise HTTPException(
                status_code=503,
                detail=str(e),
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conecta/sncr/situacao/{codigo}", summary="Verificar situação do imóvel SNCR")
async def conecta_sncr_situacao(
    codigo: str,
    investigation_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSNCRService()
    try:
        result = await service.verificar_situacao(codigo)
        if investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": investigation_id,
                "provider": "conecta_sncr",
                "query_type": "situacao",
                "query_params": {"codigo_imovel": codigo},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        if _is_credentials_missing(e):
            raise HTTPException(
                status_code=503,
                detail=str(e),
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conecta/sncr/ccir/{codigo}", summary="Baixar CCIR do imóvel SNCR")
async def conecta_sncr_ccir(
    codigo: str,
    current_user: User = Depends(get_current_user),
):
    service = ConectaSNCRService()
    try:
        response = await service.baixar_ccir(codigo)
        if response.status_code == 204:
            return Response(status_code=204)
        if response.status_code >= 400:
            raise HTTPException(status_code=400, detail=response.text)
        content_type = response.headers.get("content-type", "application/pdf")
        filename = f"ccir_{codigo}.pdf"
        return StreamingResponse(
            io.BytesIO(response.content),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as e:
        if _is_credentials_missing(e):
            raise HTTPException(
                status_code=503,
                detail=str(e),
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/sncci/parcelas", summary="SNCCI - Retorna parcelas em aberto do crédito")
async def conecta_sncci_parcelas(
    request: SncciParcelasRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSNCCIService()
    try:
        result = await service.listar_parcelas(request.cod_credito)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_sncci",
                "query_type": "parcelas",
                "query_params": {"cod_credito": request.cod_credito},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/sncci/creditos-ativos", summary="SNCCI - Retorna créditos ativos")
async def conecta_sncci_creditos_ativos(
    request: SncciCreditosAtivosRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSNCCIService()
    try:
        result = await service.listar_creditos_ativos(request.cod_beneficiario)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_sncci",
                "query_type": "creditos_ativos",
                "query_params": {"cod_beneficiario": request.cod_beneficiario},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conecta/sncci/creditos/{codigo}", summary="SNCCI - Retorna dados de crédito por código")
async def conecta_sncci_creditos(
    codigo: str,
    investigation_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSNCCIService()
    try:
        result = await service.consultar_credito(codigo)
        if investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": investigation_id,
                "provider": "conecta_sncci",
                "query_type": "creditos",
                "query_params": {"codigo": codigo},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/sncci/boletos", summary="SNCCI - Retorna PDF do boleto")
async def conecta_sncci_boletos(
    request: SncciBoletoRequest,
    current_user: User = Depends(get_current_user),
):
    service = ConectaSNCCIService()
    try:
        response = await service.baixar_boleto(request.cd_plano_pagamento_parcela)
        if response.status_code == 204:
            return Response(status_code=204)
        if response.status_code >= 400:
            raise HTTPException(status_code=400, detail=response.text)
        content_type = response.headers.get("content-type", "application/pdf")
        filename = "sncci_boleto.pdf"
        return StreamingResponse(
            io.BytesIO(response.content),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/sigef-geo/parcelas", summary="SIGEF GEO - Consultar parcelas")
async def conecta_sigef_geo_parcelas(
    request: SigefGeoParcelasRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSIGEFGeoService()
    params = request.model_dump(exclude_none=True)
    params.pop("investigation_id", None)
    try:
        result = await service.consultar_parcelas(params)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_sigef_geo",
                "query_type": "parcelas",
                "query_params": params,
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/sigef-geo/parcelas-geojson", summary="SIGEF GEO - Consultar parcelas (GeoJSON)")
async def conecta_sigef_geo_parcelas_geojson(
    request: SigefGeoParcelasRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSIGEFGeoService()
    params = request.model_dump(exclude_none=True)
    params.pop("investigation_id", None)
    try:
        result = await service.consultar_parcelas_geojson(params)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_sigef_geo",
                "query_type": "parcelas_geojson",
                "query_params": params,
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/cnpj/basica", summary="Consulta CNPJ Básica")
async def conecta_cnpj_basica(
    request: CnpjConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaCNPJService()
    try:
        result = await service.consultar_basica(request.cnpj, request.cpf_usuario)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_cnpj",
                "query_type": "basica",
                "query_params": {"cnpj": request.cnpj},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/cnpj/qsa", summary="Consulta CNPJ QSA")
async def conecta_cnpj_qsa(
    request: CnpjConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaCNPJService()
    try:
        result = await service.consultar_qsa(request.cnpj, request.cpf_usuario)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_cnpj",
                "query_type": "qsa",
                "query_params": {"cnpj": request.cnpj},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/cnpj/empresa", summary="Consulta CNPJ Empresa")
async def conecta_cnpj_empresa(
    request: CnpjConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaCNPJService()
    try:
        result = await service.consultar_empresa(request.cnpj, request.cpf_usuario)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_cnpj",
                "query_type": "empresa",
                "query_params": {"cnpj": request.cnpj},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/cnd/certidao", summary="Consulta CND (certidão)")
async def conecta_cnd_certidao(
    request: CndConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaCNDService()
    payload = request.model_dump(exclude_none=True)
    payload.pop("investigation_id", None)
    try:
        result = await service.consultar_certidao(payload)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_cnd",
                "query_type": "certidao",
                "query_params": payload,
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/cadin/info-cpf", summary="CADIN - Situação CPF")
async def conecta_cadin_info_cpf(
    request: CadinConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not request.cpf:
        raise HTTPException(status_code=400, detail="CPF é obrigatório")
    service = ConectaCadinService()
    try:
        result = await service.info_cpf(request.cpf)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_cadin",
                "query_type": "info_cpf",
                "query_params": {"cpf": request.cpf},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/cadin/info-cnpj", summary="CADIN - Situação CNPJ")
async def conecta_cadin_info_cnpj(
    request: CadinConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not request.cnpj:
        raise HTTPException(status_code=400, detail="CNPJ é obrigatório")
    service = ConectaCadinService()
    try:
        result = await service.info_cnpj(request.cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_cadin",
                "query_type": "info_cnpj",
                "query_params": {"cnpj": request.cnpj},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/cadin/completa-cpf", summary="CADIN - Consulta completa CPF")
async def conecta_cadin_completa_cpf(
    request: CadinConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not request.cpf:
        raise HTTPException(status_code=400, detail="CPF é obrigatório")
    service = ConectaCadinService()
    try:
        result = await service.completa_cpf(request.cpf)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_cadin",
                "query_type": "completa_cpf",
                "query_params": {"cpf": request.cpf},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/cadin/completa-cnpj", summary="CADIN - Consulta completa CNPJ")
async def conecta_cadin_completa_cnpj(
    request: CadinConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not request.cnpj:
        raise HTTPException(status_code=400, detail="CNPJ é obrigatório")
    service = ConectaCadinService()
    try:
        result = await service.completa_cnpj(request.cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_cadin",
                "query_type": "completa_cnpj",
                "query_params": {"cnpj": request.cnpj},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conecta/cadin/versao", summary="CADIN - Versão da API")
async def conecta_cadin_versao(
    current_user: User = Depends(get_current_user),
):
    service = ConectaCadinService()
    try:
        return await service.versao()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portal-servicos/orgao/{cod_siorg}", summary="Portal Serviços - Consultar órgão")
async def portal_servicos_orgao(
    cod_siorg: str,
    current_user: User = Depends(get_current_user),
):
    service = PortalServicosService()
    try:
        return await service.consultar_orgao(cod_siorg)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portal-servicos/servicos/{servico_id}", summary="Portal Serviços - Consultar serviço completo")
async def portal_servicos_servico(
    servico_id: str,
    current_user: User = Depends(get_current_user),
):
    service = PortalServicosService()
    try:
        return await service.consultar_servico(servico_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portal-servicos/servicos-simples/{servico_id}", summary="Portal Serviços - Consultar serviço simples")
async def portal_servicos_servico_simples(
    servico_id: str,
    current_user: User = Depends(get_current_user),
):
    service = PortalServicosService()
    try:
        return await service.consultar_servico_simples(servico_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portal-servicos/servicos-auth", summary="Portal Serviços - Listar serviços (auth)")
async def portal_servicos_auth(
    request: PortalServicosAuthRequest,
    current_user: User = Depends(get_current_user),
):
    service = PortalServicosService()
    try:
        return await service.listar_servicos_auth(request.authorization)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servicos-estaduais/auth", summary="Serviços Estaduais - Autenticar")
async def servicos_estaduais_auth(
    request: ServicosEstaduaisAuthRequest,
    current_user: User = Depends(get_current_user),
):
    service = ServicosEstaduaisService()
    try:
        return await service.autenticar(request.email, request.senha)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servicos-estaduais/servicos", summary="Serviços Estaduais - Inserir serviço")
async def servicos_estaduais_inserir(
    request: ServicosEstaduaisRequest,
    current_user: User = Depends(get_current_user),
):
    service = ServicosEstaduaisService()
    payload = request.model_dump(exclude={"authorization"})
    try:
        return await service.inserir_servico(payload, request.authorization)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/servicos-estaduais/servicos", summary="Serviços Estaduais - Editar serviço")
async def servicos_estaduais_editar(
    request: ServicosEstaduaisRequest,
    current_user: User = Depends(get_current_user),
):
    service = ServicosEstaduaisService()
    payload = request.model_dump(exclude={"authorization"})
    try:
        return await service.editar_servico(payload, request.authorization)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servicos-estaduais/servicos/{servico_id}", summary="Serviços Estaduais - Consultar serviço")
async def servicos_estaduais_consultar(
    servico_id: str,
    authorization: str,
    current_user: User = Depends(get_current_user),
):
    service = ServicosEstaduaisService()
    try:
        return await service.consultar_servico(servico_id, authorization)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/sigef/imovel", summary="Consultar SIGEF por código de imóvel")
async def conecta_sigef_imovel(
    request: ConectaImovelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSIGEFService()
    try:
        result = await service.consultar_imovel(request.codigo_imovel)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_sigef",
                "query_type": "imovel",
                "query_params": {"codigo_imovel": request.codigo_imovel},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        if _is_credentials_missing(e):
            raise HTTPException(
                status_code=503,
                detail=str(e),
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/sigef/parcelas", summary="Consultar SIGEF parcelas via Conecta")
async def conecta_sigef_parcelas(
    request: ConectaCpfCnpjRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSIGEFService()
    try:
        result = await service.consultar_parcelas(request.cpf_cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_sigef",
                "query_type": "parcelas",
                "query_params": {"cpf_cnpj": request.cpf_cnpj},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        if _is_credentials_missing(e):
            raise HTTPException(
                status_code=503,
                detail=str(e),
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/sicar/cpf-cnpj", summary="Consultar SICAR por CPF/CNPJ")
async def conecta_sicar_cpf_cnpj(
    request: ConectaCpfCnpjRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSICARService()
    try:
        result = await service.consultar_por_cpf_cnpj(request.cpf_cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_sicar",
                "query_type": "cpf_cnpj",
                "query_params": {"cpf_cnpj": request.cpf_cnpj},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        if _is_credentials_missing(e):
            raise HTTPException(
                status_code=503,
                detail=str(e),
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conecta/sicar/cpf-cnpj/{cpf_cnpj}", summary="Consultar SICAR por CPF/CNPJ (GET)")
async def conecta_sicar_cpf_cnpj_get(
    cpf_cnpj: str,
    investigation_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSICARService()
    try:
        result = await service.consultar_por_cpf_cnpj(cpf_cnpj)
        if investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": investigation_id,
                "provider": "conecta_sicar",
                "query_type": "cpf_cnpj",
                "query_params": {"cpf_cnpj": cpf_cnpj},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        if _is_credentials_missing(e):
            raise HTTPException(
                status_code=503,
                detail=str(e),
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conecta/sicar/imovel", summary="Consultar SICAR por código de imóvel")
async def conecta_sicar_imovel(
    request: ConectaImovelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConectaSICARService()
    try:
        result = await service.consultar_imovel(request.codigo_imovel)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "conecta_sicar",
                "query_type": "imovel",
                "query_params": {"codigo_imovel": request.codigo_imovel},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        if _is_credentials_missing(e):
            raise HTTPException(
                status_code=503,
                detail=str(e),
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CAR Endpoints

@router.post("/car/query", summary="Consultar CAR")
async def query_car(
    request: CARQueryRequest,
    current_user: User = Depends(get_current_user)
):
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
        "with_api": CARStateConfig.HAS_API
    }


# Tribunais Endpoints

@router.post("/tribunais/query", summary="Consultar processo judicial")
async def query_tribunal(
    request: ProcessQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Consulta processo judicial (ESAJ, Projudi, PJe)"""
    try:
        result = await query_process_by_number(request.process_number, request.state)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tribunais/systems", summary="Listar sistemas disponíveis")
async def list_tribunal_systems(current_user: User = Depends(get_current_user)):
    """Lista sistemas de tribunais"""
    from app.integrations.tribunais import TribunalConfig
    
    return {
        "esaj_states": list(TribunalConfig.ESAJ_STATES.keys()),
        "projudi_states": list(TribunalConfig.PROJUDI_STATES.keys()),
        "pje": "nacional"
    }


# Órgãos Federais Endpoints

@router.post("/orgaos/ibama", summary="Consultar IBAMA")
async def query_ibama(
    cpf_cnpj: str = Query(...),
    current_user: User = Depends(get_current_user)
):
    """Consulta embargos e licenças IBAMA"""
    integration = OrgaoFederalIntegration()
    try:
        result = await integration.query_ibama(cpf_cnpj)
        return result
    finally:
        await integration.close()


@router.post("/orgaos/icmbio", summary="Consultar ICMBio")
async def query_icmbio(
    lat: float = Query(...),
    lng: float = Query(...),
    current_user: User = Depends(get_current_user)
):
    """Verifica se coordenadas estão em unidade de conservação"""
    integration = OrgaoFederalIntegration()
    try:
        result = await integration.query_icmbio({"lat": lat, "lng": lng})
        return result
    finally:
        await integration.close()


@router.post("/orgaos/cvm", summary="Consultar CVM")
async def query_cvm(
    cnpj: str = Query(...),
    current_user: User = Depends(get_current_user)
):
    """Consulta empresa na CVM (capital aberto)"""
    integration = OrgaoFederalIntegration()
    try:
        result = await integration.query_cvm(cnpj)
        return result
    finally:
        await integration.close()


@router.post("/orgaos/all", summary="Consultar todos os órgãos")
async def query_all_orgaos(
    request: OrgaoQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Consulta todos os órgãos federais"""
    integration = OrgaoFederalIntegration()
    try:
        result = await integration.query_all(request.cpf_cnpj, request.coordinates)
        return result
    finally:
        await integration.close()


# Bureaus Endpoints

@router.post("/bureaus/serasa", summary="Consultar Serasa")
async def query_serasa(
    request: BureauQueryRequest,
    current_user: User = Depends(get_current_user),
    serasa_key: Optional[str] = None
):
    """Consulta Serasa Experian"""
    integration = BureauIntegration(serasa_api_key=serasa_key)
    try:
        result = await integration.query_serasa(request.cpf_cnpj, request.product)
        return result
    finally:
        await integration.close()


@router.post("/bureaus/boavista", summary="Consultar Boa Vista")
async def query_boavista(
    cpf_cnpj: str = Query(...),
    current_user: User = Depends(get_current_user),
    boavista_key: Optional[str] = None
):
    """Consulta Boa Vista SCPC"""
    integration = BureauIntegration(boavista_api_key=boavista_key)
    try:
        result = await integration.query_boavista(cpf_cnpj)
        return result
    finally:
        await integration.close()


@router.post("/bureaus/all", summary="Consultar todos os bureaus")
async def query_all_bureaus(
    cpf_cnpj: str = Query(...),
    current_user: User = Depends(get_current_user),
    serasa_key: Optional[str] = None,
    boavista_key: Optional[str] = None
):
    """Consulta todos os bureaus de crédito"""
    integration = BureauIntegration(serasa_key, boavista_key)
    try:
        result = await integration.query_all_bureaus(cpf_cnpj)
        return result
    finally:
        await integration.close()


# Comunicação Endpoints

@router.post("/notify/slack", summary="Enviar notificação Slack")
async def notify_slack(
    request: NotificationRequest,
    current_user: User = Depends(get_current_user),
    webhook_url: Optional[str] = None,
    bot_token: Optional[str] = None
):
    """Envia notificação para Slack"""
    from app.integrations.comunicacao import SlackIntegration
    
    integration = SlackIntegration(webhook_url, bot_token)
    try:
        if request.risk_score is not None:
            result = await integration.send_investigation_alert(
                request.title,
                request.risk_score,
                request.patterns_found or 0,
                request.slack_channel or "#investigations"
            )
        else:
            channel = request.slack_channel or "#general"
            result = await integration.send_message(channel, request.message)
        
        return result
    finally:
        await integration.close()


@router.post("/notify/teams", summary="Enviar notificação Teams")
async def notify_teams(
    request: NotificationRequest,
    current_user: User = Depends(get_current_user),
    webhook_url: Optional[str] = None
):
    """Envia notificação para Microsoft Teams"""
    from app.integrations.comunicacao import TeamsIntegration
    
    integration = TeamsIntegration(webhook_url)
    try:
        if request.risk_score is not None:
            result = await integration.send_investigation_alert(
                request.title,
                request.risk_score,
                request.patterns_found or 0,
                request.investigation_url
            )
        else:
            result = await integration.send_message(request.title, request.message)
        
        return result
    finally:
        await integration.close()


@router.post("/notify/all", summary="Enviar para todos os canais")
async def notify_all(
    request: NotificationRequest,
    current_user: User = Depends(get_current_user),
    slack_webhook: Optional[str] = None,
    slack_token: Optional[str] = None,
    teams_webhook: Optional[str] = None
):
    """Envia notificação para Slack e Teams"""
    integration = ComunicacaoIntegration(slack_webhook, slack_token, teams_webhook)
    try:
        result = await integration.notify_all(
            request.title,
            request.risk_score or 0.0,
            request.patterns_found or 0,
            request.slack_channel or "#investigations",
            request.investigation_url
        )
        return result
    finally:
        await integration.close()


# ======================================================================
# BrasilAPI Endpoints (Gratuito, sem auth)
# ======================================================================


class BrasilAPICnpjRequest(BaseModel):
    cnpj: str
    investigation_id: Optional[int] = None


class BrasilAPICepRequest(BaseModel):
    cep: str


@router.post("/brasil-api/cnpj", summary="BrasilAPI - Consulta CNPJ (gratuito)")
async def brasil_api_cnpj(
    request: BrasilAPICnpjRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BrasilAPIService()
    try:
        result = await service.consultar_cnpj(request.cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "brasil_api",
                "query_type": "cnpj",
                "query_params": {"cnpj": request.cnpj},
                "result_count": 1 if "cnpj" in result else 0,
                "response": result,
            })
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


# ======================================================================
# Portal da Transparência (CGU) — API Key gratuita
# ======================================================================


class TransparenciaRequest(BaseModel):
    cpf_cnpj: str
    investigation_id: Optional[int] = None


@router.post("/transparencia/sancoes", summary="Transparência - CEIS + CNEP (sanções)")
async def transparencia_sancoes(
    request: TransparenciaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PortalTransparenciaService()

    # Verificar se credenciais estão configuradas
    if not service.api_key:
        raise HTTPException(
            status_code=503,
            detail="Portal da Transparência não configurado. Configure PORTAL_TRANSPARENCIA_API_KEY no arquivo .env"
        )

    try:
        ceis = await service.consultar_ceis(request.cpf_cnpj)
        cnep = await service.consultar_cnep(request.cpf_cnpj)
        result = {"ceis": ceis, "cnep": cnep}
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            total = (ceis.get("total", 0) or 0) + (cnep.get("total", 0) or 0)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "portal_transparencia",
                "query_type": "sancoes",
                "query_params": {"cpf_cnpj": request.cpf_cnpj},
                "result_count": total,
                "response": result,
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        error_msg = str(e)
        if "401" in error_msg or "Chave de API" in error_msg:
            raise HTTPException(status_code=401, detail="API Key do Portal da Transparência inválida ou expirada")
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transparencia/contratos", summary="Transparência - Contratos federais")
async def transparencia_contratos(
    request: TransparenciaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PortalTransparenciaService()
    
    # Verificar se credenciais estão configuradas
    if not service.api_key:
        raise HTTPException(
            status_code=503,
            detail="Portal da Transparência não configurado. Configure PORTAL_TRANSPARENCIA_API_KEY no arquivo .env"
        )
    
    try:
        result = await service.consultar_contratos(request.cpf_cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "portal_transparencia",
                "query_type": "contratos",
                "query_params": {"cpf_cnpj": request.cpf_cnpj},
                "result_count": result.get("total", 0),
                "response": result,
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        # Erro da API (401, 404, etc)
        error_msg = str(e)
        if "401" in error_msg or "Chave de API" in error_msg:
            raise HTTPException(status_code=503, detail="Credenciais inválidas ou não configuradas")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Erro ao consultar contratos Portal Transparência: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transparencia/servidores", summary="Transparência - Servidores públicos")
async def transparencia_servidores(
    request: TransparenciaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PortalTransparenciaService()
    
    # Verificar se credenciais estão configuradas
    if not service.api_key:
        raise HTTPException(
            status_code=503,
            detail="Portal da Transparência não configurado. Configure PORTAL_TRANSPARENCIA_API_KEY no arquivo .env"
        )
    
    try:
        result = await service.consultar_servidores(request.cpf_cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "portal_transparencia",
                "query_type": "servidores",
                "query_params": {"cpf": request.cpf_cnpj},
                "result_count": result.get("total", 0),
                "response": result,
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        error_msg = str(e)
        if "401" in error_msg or "Chave de API" in error_msg:
            raise HTTPException(status_code=503, detail="Credenciais inválidas ou não configuradas")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Erro ao consultar servidores Portal Transparência: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transparencia/beneficios", summary="Transparência - Benefícios sociais")
async def transparencia_beneficios(
    request: TransparenciaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PortalTransparenciaService()
    
    # Verificar se credenciais estão configuradas
    if not service.api_key:
        raise HTTPException(
            status_code=503,
            detail="Portal da Transparência não configurado. Configure PORTAL_TRANSPARENCIA_API_KEY no arquivo .env"
        )
    
    try:
        result = await service.consultar_beneficios(request.cpf_cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "portal_transparencia",
                "query_type": "beneficios",
                "query_params": {"cpf": request.cpf_cnpj},
                "result_count": result.get("total", 0),
                "response": result,
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        error_msg = str(e)
        if "401" in error_msg or "Chave de API" in error_msg:
            raise HTTPException(status_code=503, detail="Credenciais inválidas ou não configuradas")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Erro ao consultar benefícios Portal Transparência: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transparencia/despesas", summary="Transparência - Despesas por favorecido")
async def transparencia_despesas(
    request: TransparenciaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PortalTransparenciaService()
    try:
        result = await service.consultar_despesas(request.cpf_cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "portal_transparencia",
                "query_type": "despesas",
                "query_params": {"cpf_cnpj": request.cpf_cnpj},
                "result_count": result.get("total", 0),
                "response": result,
            })
        return _conecta_standard_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transparencia/completa", summary="Transparência - Consulta completa (sanções + contratos + servidores + benefícios)")
async def transparencia_completa(
    request: TransparenciaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Consulta todos os dados disponíveis no Portal da Transparência para um CPF/CNPJ."""
    service = PortalTransparenciaService()
    result: Dict[str, Any] = {}
    errors: List[str] = []

    for key, method in [
        ("ceis", service.consultar_ceis),
        ("cnep", service.consultar_cnep),
        ("contratos", service.consultar_contratos),
        ("servidores", service.consultar_servidores),
        ("beneficios", service.consultar_beneficios),
        ("despesas", service.consultar_despesas),
    ]:
        try:
            result[key] = await method(request.cpf_cnpj)
        except Exception as e:
            errors.append(f"{key}: {str(e)[:100]}")
            result[key] = {"error": str(e)[:200]}

    total_count = sum(
        (r.get("total", 0) or 0) for r in result.values() if isinstance(r, dict) and "total" in r
    )

    if request.investigation_id:
        repo = LegalQueryRepository(db)
        await repo.create({
            "investigation_id": request.investigation_id,
            "provider": "portal_transparencia",
            "query_type": "completa",
            "query_params": {"cpf_cnpj": request.cpf_cnpj},
            "result_count": total_count,
            "response": result,
        })

    return _conecta_standard_response(result, warnings=errors)


# ======================================================================
# REDESIM / ReceitaWS — Consulta CNPJ pública gratuita
# ======================================================================


class RedesimCnpjRequest(BaseModel):
    cnpj: str
    investigation_id: Optional[int] = None


@router.post("/redesim/cnpj", summary="REDESIM/ReceitaWS - Consulta CNPJ público (gratuito)")
async def redesim_cnpj(
    request: RedesimCnpjRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RedesimService()
    try:
        result = await service.consultar_cnpj(request.cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "redesim_cnpj",
                "query_type": "cnpj",
                "query_params": {"cnpj": request.cnpj},
                "result_count": 1 if not result.get("error") else 0,
                "response": result,
            })
        return _conecta_standard_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# IBGE Endpoints (Gratuito, sem auth)
# ======================================================================


@router.get("/ibge/estados", summary="IBGE - Listar estados")
async def ibge_estados(current_user: User = Depends(get_current_user)):
    service = IBGEService()
    try:
        return await service.listar_estados()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ibge/municipios/{uf}", summary="IBGE - Listar municípios de UF")
async def ibge_municipios(uf: str, current_user: User = Depends(get_current_user)):
    service = IBGEService()
    try:
        return await service.listar_municipios_uf(uf)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ibge/municipio/{codigo_ibge}", summary="IBGE - Dados do município")
async def ibge_municipio(codigo_ibge: str, current_user: User = Depends(get_current_user)):
    service = IBGEService()
    try:
        return await service.consultar_municipio(codigo_ibge)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ibge/nome/{nome}", summary="IBGE - Frequência de nomes")
async def ibge_nome(nome: str, current_user: User = Depends(get_current_user)):
    service = IBGEService()
    try:
        return await service.consultar_nome(nome)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ibge/malha/{codigo_ibge}", summary="IBGE - Malha geográfica (GeoJSON)")
async def ibge_malha(codigo_ibge: str, current_user: User = Depends(get_current_user)):
    service = IBGEService()
    try:
        return await service.consultar_malha_municipio(codigo_ibge)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# TSE - Tribunal Superior Eleitoral (Gratuito, sem auth)
# ======================================================================


class TSEBuscaRequest(BaseModel):
    query: str
    investigation_id: Optional[int] = None


@router.post("/tse/buscar", summary="TSE - Buscar datasets eleitorais")
async def tse_buscar(
    request: TSEBuscaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TSEService()
    try:
        result = await service.buscar_datasets(request.query)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            count = result.get("result", {}).get("count", 0) if isinstance(result, dict) else 0
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "tse",
                "query_type": "busca",
                "query_params": {"query": request.query},
                "result_count": count,
                "response": result,
            })
        return _conecta_standard_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tse/candidatos/{ano}", summary="TSE - Datasets de candidatos por ano")
async def tse_candidatos(ano: int, current_user: User = Depends(get_current_user)):
    service = TSEService()
    try:
        return await service.buscar_candidatos(ano=ano)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tse/bens/{ano}", summary="TSE - Bens declarados de candidatos")
async def tse_bens(ano: int, current_user: User = Depends(get_current_user)):
    service = TSEService()
    try:
        return await service.buscar_bens_candidatos(ano=ano)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# CVM - Comissão de Valores Mobiliários (Gratuito, sem auth)
# ======================================================================


class CVMBuscaRequest(BaseModel):
    cnpj: Optional[str] = None
    nome: Optional[str] = None
    investigation_id: Optional[int] = None


@router.post("/cvm/fundos", summary="CVM - Buscar fundos de investimento")
async def cvm_fundos(
    request: CVMBuscaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CVMService()
    try:
        result = await service.buscar_fundos(cnpj=request.cnpj, nome=request.nome)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            count = result.get("result", {}).get("count", 0) if isinstance(result, dict) else 0
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "cvm",
                "query_type": "fundos",
                "query_params": {"cnpj": request.cnpj, "nome": request.nome},
                "result_count": count,
                "response": result,
            })
        return _conecta_standard_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cvm/fii", summary="CVM - Buscar fundos imobiliários (FII)")
async def cvm_fii(
    request: CVMBuscaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CVMService()
    try:
        result = await service.buscar_fii(cnpj=request.cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            count = result.get("result", {}).get("count", 0) if isinstance(result, dict) else 0
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "cvm",
                "query_type": "fii",
                "query_params": {"cnpj": request.cnpj},
                "result_count": count,
                "response": result,
            })
        return _conecta_standard_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cvm/participantes", summary="CVM - Participantes do mercado")
async def cvm_participantes(
    request: CVMBuscaRequest,
    current_user: User = Depends(get_current_user),
):
    service = CVMService()
    try:
        return await service.buscar_participantes(cnpj=request.cnpj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# BCB - Banco Central do Brasil (Gratuito, sem auth)
# ======================================================================


@router.get("/bcb/selic", summary="BCB - Taxa SELIC")
async def bcb_selic(current_user: User = Depends(get_current_user)):
    service = BCBService()
    try:
        return await service.consultar_selic()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bcb/ipca", summary="BCB - IPCA (inflação)")
async def bcb_ipca(current_user: User = Depends(get_current_user)):
    service = BCBService()
    try:
        return await service.consultar_ipca()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bcb/cdi", summary="BCB - CDI")
async def bcb_cdi(current_user: User = Depends(get_current_user)):
    service = BCBService()
    try:
        return await service.consultar_cdi()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bcb/cambio/{moeda}", summary="BCB - Taxa de câmbio PTAX")
async def bcb_cambio(moeda: str, data: Optional[str] = None, current_user: User = Depends(get_current_user)):
    service = BCBService()
    try:
        return await service.consultar_taxa_cambio(moeda, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bcb/pix/participantes", summary="BCB - Participantes PIX")
async def bcb_pix(current_user: User = Depends(get_current_user)):
    service = BCBService()
    try:
        return await service.consultar_pix_participantes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# dados.gov.br — Portal de Dados Abertos (Gratuito)
# ======================================================================


class DadosGovBuscaRequest(BaseModel):
    query: str
    pagina: int = 1


@router.post("/dados-gov/buscar", summary="dados.gov.br - Buscar datasets")
async def dados_gov_buscar(
    request: DadosGovBuscaRequest,
    current_user: User = Depends(get_current_user),
):
    service = DadosGovService()
    try:
        return await service.buscar_datasets(request.query, pagina=request.pagina)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dados-gov/rural", summary="dados.gov.br - Datasets rurais")
async def dados_gov_rural(
    pagina: int = 1,
    current_user: User = Depends(get_current_user),
):
    service = DadosGovService()
    try:
        return await service.buscar_rural(pagina=pagina)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dados-gov/ambiental", summary="dados.gov.br - Datasets ambientais")
async def dados_gov_ambiental(
    pagina: int = 1,
    current_user: User = Depends(get_current_user),
):
    service = DadosGovService()
    try:
        return await service.buscar_ambiental(pagina=pagina)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dados-gov/organizacoes", summary="dados.gov.br - Organizações")
async def dados_gov_organizacoes(
    query: str = "",
    current_user: User = Depends(get_current_user),
):
    service = DadosGovService()
    try:
        return await service.buscar_organizacoes(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# TJMG — Tribunal de Justiça de Minas Gerais
# ======================================================================


class TJMGConsultaRequest(BaseModel):
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    nome_parte: Optional[str] = None
    nome_advogado: Optional[str] = None
    numero_processo: Optional[str] = None
    investigation_id: Optional[int] = None


@router.post("/tjmg/processos", summary="TJMG - Consulta pública de processos")
async def tjmg_processos(
    request: TJMGConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Consulta processos no PJe do TJMG por CPF, CNPJ, nome ou número."""
    service = TJMGService()
    try:
        result = await service.consultar_completa(
            cpf=request.cpf,
            cnpj=request.cnpj,
            nome_parte=request.nome_parte,
            nome_advogado=request.nome_advogado,
            numero_processo=request.numero_processo,
        )
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            params = {k: v for k, v in request.model_dump().items() if v is not None and k != "investigation_id"}
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "tjmg",
                "query_type": "processos",
                "query_params": params,
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tjmg/processos/cpf", summary="TJMG - Processos por CPF")
async def tjmg_processos_cpf(
    request: TJMGConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not request.cpf:
        raise HTTPException(status_code=400, detail="CPF é obrigatório")
    service = TJMGService()
    try:
        result = await service.consultar_por_cpf(request.cpf)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "tjmg",
                "query_type": "processos_cpf",
                "query_params": {"cpf": request.cpf},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tjmg/processos/cnpj", summary="TJMG - Processos por CNPJ")
async def tjmg_processos_cnpj(
    request: TJMGConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not request.cnpj:
        raise HTTPException(status_code=400, detail="CNPJ é obrigatório")
    service = TJMGService()
    try:
        result = await service.consultar_por_cnpj(request.cnpj)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "tjmg",
                "query_type": "processos_cnpj",
                "query_params": {"cnpj": request.cnpj},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tjmg/processos/{numero_processo}", summary="TJMG - Processo por número")
async def tjmg_processo_numero(
    numero_processo: str,
    investigation_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TJMGService()
    try:
        result = await service.consultar_por_numero(numero_processo)
        if investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": investigation_id,
                "provider": "tjmg",
                "query_type": "processo_numero",
                "query_params": {"numero_processo": numero_processo},
                "result_count": _result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })
        return _conecta_standard_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tjmg/configuration", summary="TJMG - Configuração da API de Gestão de Acessos")
async def tjmg_configuration(current_user: User = Depends(get_current_user)):
    service = TJMGService()
    try:
        return await service.gestao_configuration()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# Antecedentes Criminais / MG — Polícia Civil de Minas Gerais
# ======================================================================


class AntecedentesMGRequest(BaseModel):
    cpf: str
    rg: str
    investigation_id: Optional[int] = None


@router.post("/antecedentes-mg/consultar", summary="Antecedentes Criminais MG - Consultar por CPF + RG")
async def antecedentes_mg_consultar(
    request: AntecedentesMGRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Consulta antecedentes criminais na Polícia Civil de MG (CPF + RG emitido em MG)."""
    service = AntecedentesMGService()
    try:
        result = await service.consultar(request.cpf, request.rg)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "antecedentes_mg",
                "query_type": "consulta",
                "query_params": {"cpf": request.cpf[:4] + "***", "rg": "***"},
                "result_count": 1 if result.get("conseguiu_emitir_certidao_negativa") is not None else 0,
                "response": result,
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/antecedentes-mg/disponibilidade", summary="Antecedentes Criminais MG - Verificar disponibilidade")
async def antecedentes_mg_disponibilidade(current_user: User = Depends(get_current_user)):
    service = AntecedentesMGService()
    try:
        return await service.verificar_disponibilidade()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# SICAR Público — Cadastro Ambiental Rural (Consulta Pública)
# ======================================================================


class SICARPublicoRequest(BaseModel):
    car: str
    investigation_id: Optional[int] = None


@router.post("/sicar-publico/imovel", summary="SICAR Público - Consultar imóvel por número CAR")
async def sicar_publico_imovel(
    request: SICARPublicoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Consulta dados de imóvel no SICAR pelo número do CAR (área, coordenadas, município, status, tipo)."""
    service = SICARPublicoService()
    try:
        result = await service.consultar_imovel_por_car(request.car)
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "sicar_publico",
                "query_type": "imovel_car",
                "query_params": {"car": request.car},
                "result_count": 1 if result.get("area") or result.get("municipio") else 0,
                "response": result,
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sicar-publico/municipio/{codigo_ibge}", summary="SICAR Público - Imóveis por município")
async def sicar_publico_municipio(
    codigo_ibge: str,
    current_user: User = Depends(get_current_user),
):
    service = SICARPublicoService()
    try:
        return await service.buscar_imoveis_municipio(codigo_ibge)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sicar-publico/disponibilidade", summary="SICAR Público - Verificar disponibilidade")
async def sicar_publico_disponibilidade(current_user: User = Depends(get_current_user)):
    service = SICARPublicoService()
    try:
        return await service.verificar_disponibilidade()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# Caixa — Regularidade do Empregador (FGTS / CRF)
# ======================================================================


class CaixaFGTSRequest(BaseModel):
    cnpj: Optional[str] = None
    cei: Optional[str] = None
    investigation_id: Optional[int] = None


@router.post("/caixa-fgts/consultar", summary="Caixa FGTS - Regularidade do Empregador (CRF)")
async def caixa_fgts_consultar(
    request: CaixaFGTSRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Consulta regularidade FGTS por CNPJ ou CEI. Retorna CRF, situação, razão social, validade."""
    service = CaixaFGTSService()
    try:
        if request.cnpj:
            result = await service.consultar_por_cnpj(request.cnpj)
        elif request.cei:
            result = await service.consultar_por_cei(request.cei)
        else:
            raise ValueError("Informe CNPJ ou CEI")

        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "caixa_fgts",
                "query_type": "regularidade",
                "query_params": {"cnpj": request.cnpj, "cei": request.cei},
                "result_count": 1 if result.get("situacao") else 0,
                "response": result,
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/caixa-fgts/disponibilidade", summary="Caixa FGTS - Verificar disponibilidade")
async def caixa_fgts_disponibilidade(current_user: User = Depends(get_current_user)):
    service = CaixaFGTSService()
    try:
        return await service.verificar_disponibilidade()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# BNMP — Banco Nacional de Mandados de Prisão (CNJ)
# ======================================================================


class BNMPConsultaRequest(BaseModel):
    cpf: Optional[str] = None
    nome: Optional[str] = None
    nome_mae: Optional[str] = None
    investigation_id: Optional[int] = None


@router.post("/bnmp/consultar", summary="BNMP/CNJ - Mandados de Prisão por CPF")
async def bnmp_consultar_cpf(
    request: BNMPConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta mandados de prisão vigentes no BNMP/CNJ por CPF ou Nome.
    Retorna até 30 resultados com situação "Aguardando Cumprimento".
    Dados: nome, CPF, processo, tribunal, órgão, tipificação penal, regime, pena, etc.
    """
    if not request.cpf and not request.nome:
        raise HTTPException(status_code=400, detail="Informe CPF ou Nome para consulta")

    service = BNMPService()
    try:
        if request.cpf:
            result = await service.consultar_por_cpf(request.cpf)
        else:
            result = await service.consultar_por_nome(request.nome, request.nome_mae)  # type: ignore[arg-type]
    except Exception as e:
        # Retorna resultado vazio com aviso em vez de 500 para não bloquear o Quick Scan
        result = {
            "total": 0,
            "mandados": [],
            "fonte": "BNMP/CNJ",
            "consulta": {"cpf": request.cpf, "nome": request.nome},
            "mensagem": f"Portal BNMP indisponível: {str(e)[:200]}",
            "portal_url": "https://portalbnmp.pdpj.jus.br/#/pesquisa-peca",
        }

    try:
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "bnmp_cnj",
                "query_type": "mandados_prisao",
                "query_params": {"cpf": request.cpf, "nome": request.nome},
                "result_count": result.get("total", 0),
                "response": result,
            })
    except Exception:
        pass  # Não bloquear resposta por erro de persistência

    return _conecta_standard_response(result, warnings=result.get("mensagem") and [result["mensagem"]] or [])


@router.get("/bnmp/disponibilidade", summary="BNMP/CNJ - Verificar disponibilidade")
async def bnmp_disponibilidade(current_user: User = Depends(get_current_user)):
    service = BNMPService()
    try:
        return await service.verificar_disponibilidade()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# SEEU — Sistema Eletrônico de Execução Unificado (CNJ)
# ======================================================================


class SEEUConsultaRequest(BaseModel):
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    nome_parte: Optional[str] = None
    nome_mae: Optional[str] = None
    numero_processo: Optional[str] = None
    investigation_id: Optional[int] = None


@router.post("/seeu/consultar", summary="SEEU/CNJ - Processos de Execução Penal")
async def seeu_consultar(
    request: SEEUConsultaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta processos no SEEU (Sistema Eletrônico de Execução Unificado) do CNJ.
    Aceita: CPF, CNPJ, nome da parte, ou número do processo.
    Retorna: processos encontrados, informações gerais, movimentações, partes.
    """
    service = SEEUService()
    try:
        if request.numero_processo:
            result = await service.consultar_por_processo(request.numero_processo)
        elif request.cpf:
            result = await service.consultar_por_cpf(request.cpf, request.nome_mae)
        elif request.cnpj:
            result = await service.consultar_por_cnpj(request.cnpj)
        elif request.nome_parte:
            result = await service.consultar_por_nome(request.nome_parte, request.nome_mae)
        else:
            raise ValueError("Informe CPF, CNPJ, nome da parte ou número do processo")

        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "seeu_cnj",
                "query_type": "processos_execucao",
                "query_params": {
                    "cpf": request.cpf,
                    "cnpj": request.cnpj,
                    "nome_parte": request.nome_parte,
                    "numero_processo": request.numero_processo,
                },
                "result_count": result.get("total", 0),
                "response": result,
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/seeu/disponibilidade", summary="SEEU/CNJ - Verificar disponibilidade")
async def seeu_disponibilidade(current_user: User = Depends(get_current_user)):
    service = SEEUService()
    try:
        return await service.verificar_disponibilidade()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# SIGEF Público — Parcelas INCRA (consulta direta)
# ======================================================================


class SIGEFPublicoRequest(BaseModel):
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    codigo_imovel: Optional[str] = None
    paginas: Optional[int] = 5
    investigation_id: Optional[int] = None


@router.post("/sigef-publico/parcelas", summary="SIGEF Público - Parcelas por CPF/CNPJ/Código")
async def sigef_publico_parcelas(
    request: SIGEFPublicoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta parcelas no portal público do SIGEF/INCRA.
    Aceita: CPF, CNPJ ou código do imóvel.
    Retorna até 5 páginas de resultados: parcelas com área, código, matrícula, detentor.
    Gratuito, sem credenciais.
    """
    if not request.cpf and not request.cnpj and not request.codigo_imovel:
        raise HTTPException(status_code=400, detail="Informe CPF, CNPJ ou código do imóvel")

    service = SIGEFPublicoService()
    warnings: list[str] = []
    try:
        paginas = min(request.paginas or 5, 5)
        if request.cpf:
            result = await service.consultar_por_cpf(request.cpf, paginas)
        elif request.cnpj:
            result = await service.consultar_por_cnpj(request.cnpj, paginas)
        else:
            result = await service.consultar_por_codigo_imovel(request.codigo_imovel)  # type: ignore[arg-type]
    except Exception as e:
        # Retorna resultado vazio com aviso em vez de 500
        result = {
            "parcelas": [],
            "paginas": 0,
            "paginas_retornadas": 0,
            "resultados": 0,
            "resultados_retornados": 0,
            "fonte": "SIGEF/INCRA",
        }
        warnings.append(f"Portal SIGEF indisponível: {str(e)[:200]}")

    try:
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "sigef_publico",
                "query_type": "parcelas",
                "query_params": {
                    "cpf": request.cpf,
                    "cnpj": request.cnpj,
                    "codigo_imovel": request.codigo_imovel,
                },
                "result_count": result.get("resultados_retornados", 0),
                "response": result,
            })
    except Exception:
        pass  # Não bloquear resposta

    return _conecta_standard_response(result, warnings=warnings)


@router.get("/sigef-publico/disponibilidade", summary="SIGEF Público - Verificar disponibilidade")
async def sigef_publico_disponibilidade(current_user: User = Depends(get_current_user)):
    service = SIGEFPublicoService()
    try:
        return await service.verificar_disponibilidade()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# Receita Federal — Consulta CPF (Situação Cadastral)
# ======================================================================


class ReceitaCPFRequest(BaseModel):
    cpf: str
    data_nascimento: Optional[str] = None
    investigation_id: Optional[int] = None


@router.post("/receita-cpf/consultar", summary="Receita Federal - Situação Cadastral CPF")
async def receita_cpf_consultar(
    request: ReceitaCPFRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta situação cadastral de CPF na Receita Federal.
    Retorna: nome, situação cadastral, data inscrição, ano óbito, dígito verificador.
    """
    service = ReceitaCPFService()
    try:
        result = await service.consultar(request.cpf, request.data_nascimento)

        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "receita_cpf",
                "query_type": "situacao_cadastral",
                "query_params": {"cpf": request.cpf},
                "result_count": 1 if result.get("situacao_cadastral") else 0,
                "response": result,
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/receita-cpf/disponibilidade", summary="Receita Federal CPF - Verificar disponibilidade")
async def receita_cpf_disponibilidade(current_user: User = Depends(get_current_user)):
    service = ReceitaCPFService()
    try:
        return await service.verificar_disponibilidade()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# Receita Federal — Consulta CNPJ (Dados Cadastrais PJ)
# ======================================================================


class ReceitaCNPJRequest(BaseModel):
    cnpj: str
    investigation_id: Optional[int] = None


@router.post("/receita-cnpj/consultar", summary="Receita Federal - Dados Cadastrais CNPJ")
async def receita_cnpj_consultar(
    request: ReceitaCNPJRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta dados cadastrais de CNPJ na Receita Federal.
    Tenta: Receita Federal (direto) → BrasilAPI → ReceitaWS → MinhaReceita.
    Retorna: razão social, situação cadastral, endereço, QSA (sócios), capital social,
    atividade econômica, natureza jurídica, porte, telefone, email, etc.
    """
    service = ReceitaCNPJService()
    try:
        result = await service.consultar(request.cnpj)

        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "receita_cnpj",
                "query_type": "dados_cadastrais_pj",
                "query_params": {"cnpj": request.cnpj},
                "result_count": 1 if result.get("razao_social") else 0,
                "response": result,
            })
        return _conecta_standard_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/receita-cnpj/disponibilidade", summary="Receita Federal CNPJ - Verificar disponibilidade")
async def receita_cnpj_disponibilidade(current_user: User = Depends(get_current_user)):
    service = ReceitaCNPJService()
    try:
        return await service.verificar_disponibilidade()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


# ======================================================================
# Birôs de Crédito — Serasa e Boa Vista
# ======================================================================

class CreditoBureauRequest(BaseModel):
    cpf_cnpj: str
    investigation_id: Optional[int] = None


@router.post("/credito/serasa/score", summary="Serasa - Consulta Score")
async def serasa_score(
    request: CreditoBureauRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta score de crédito no Serasa Experian
    
    ATENÇÃO: Requer credenciais comerciais (SERASA_CLIENT_ID, SERASA_CLIENT_SECRET)
    """
    from app.services.integrations.serasa_service import SerasaService
    
    try:
        async with SerasaService() as service:
            score = await service.consultar_score(request.cpf_cnpj)
        
        if not score:
            return {
                "success": False,
                "message": "Score não disponível ou credenciais não configuradas"
            }
        
        score_dict = {
            'score': score.score,
            'faixa': score.faixa,
            'probabilidade_inadimplencia': score.probabilidade_inadimplencia,
            'data_consulta': score.data_consulta.isoformat()
        }
        
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "serasa",
                "query_type": "score",
                "query_params": {"cpf_cnpj": request.cpf_cnpj},
                "result_count": 1,
                "response": score_dict,
            })
        
        return {
            "success": True,
            "score": score_dict
        }
    
    except Exception as e:
        logger.error(f"Erro ao consultar Serasa Score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credito/serasa/relatorio", summary="Serasa - Relatório Completo")
async def serasa_relatorio(
    request: CreditoBureauRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Busca relatório completo de crédito no Serasa
    
    Inclui: score, restrições, protestos, ações judiciais, cheques, dívidas, consultas
    """
    from app.services.integrations.serasa_service import SerasaService
    
    try:
        async with SerasaService() as service:
            report = await service.get_full_report(request.cpf_cnpj)
        
        if not report:
            return {
                "success": False,
                "message": "Relatório não disponível ou credenciais não configuradas"
            }
        
        # Converter para dict
        report_dict = {
            'cpf_cnpj': report.cpf_cnpj,
            'nome': report.nome,
            'score': {
                'score': report.score.score,
                'faixa': report.score.faixa,
                'probabilidade_inadimplencia': report.score.probabilidade_inadimplencia
            } if report.score else None,
            'restricoes': [
                {
                    'tipo': r.tipo,
                    'credor': r.credor,
                    'valor': r.valor,
                    'data_ocorrencia': r.data_ocorrencia.isoformat(),
                    'cidade': r.cidade,
                    'uf': r.uf,
                    'origem': r.origem
                }
                for r in report.restricoes
            ],
            'resumo': {
                'protestos_quantidade': report.protestos_quantidade,
                'protestos_valor_total': report.protestos_valor_total,
                'acoes_quantidade': report.acoes_quantidade,
                'acoes_valor_total': report.acoes_valor_total,
                'cheques_quantidade': report.cheques_quantidade,
                'dividas_quantidade': report.dividas_quantidade,
                'dividas_valor_total': report.dividas_valor_total,
                'consultas_ultimos_90_dias': report.consultas_ultimos_90_dias
            },
            'participacao_empresas': report.participacao_empresas,
            'data_consulta': report.data_consulta.isoformat()
        }
        
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "serasa",
                "query_type": "relatorio_completo",
                "query_params": {"cpf_cnpj": request.cpf_cnpj},
                "result_count": len(report.restricoes),
                "response": report_dict,
            })
        
        return {
            "success": True,
            "relatorio": report_dict
        }
    
    except Exception as e:
        logger.error(f"Erro ao consultar Serasa: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credito/boavista/score", summary="Boa Vista - Consulta Score")
async def boavista_score(
    request: CreditoBureauRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta score de crédito na Boa Vista SCPC
    
    ATENÇÃO: Requer credenciais comerciais (BOAVISTA_CLIENT_ID, BOAVISTA_CLIENT_SECRET)
    """
    from app.services.integrations.boavista_service import BoaVistaService
    
    try:
        async with BoaVistaService() as service:
            score = await service.consultar_score(request.cpf_cnpj)
        
        if not score:
            return {
                "success": False,
                "message": "Score não disponível ou credenciais não configuradas"
            }
        
        score_dict = {
            'score': score.score,
            'classificacao': score.classificacao,
            'data_consulta': score.data_consulta.isoformat()
        }
        
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "boavista",
                "query_type": "score",
                "query_params": {"cpf_cnpj": request.cpf_cnpj},
                "result_count": 1,
                "response": score_dict,
            })
        
        return {
            "success": True,
            "score": score_dict
        }
    
    except Exception as e:
        logger.error(f"Erro ao consultar Boa Vista Score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credito/boavista/relatorio", summary="Boa Vista - Relatório Completo")
async def boavista_relatorio(
    request: CreditoBureauRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Busca relatório completo na Boa Vista SCPC
    
    Inclui: score, restrições, protestos, cheques sem fundo, ações judiciais
    """
    from app.services.integrations.boavista_service import BoaVistaService
    
    try:
        async with BoaVistaService() as service:
            report = await service.get_full_report(request.cpf_cnpj)
        
        if not report:
            return {
                "success": False,
                "message": "Relatório não disponível ou credenciais não configuradas"
            }
        
        report_dict = {
            'cpf_cnpj': report.cpf_cnpj,
            'nome': report.nome,
            'score': {
                'score': report.score.score,
                'classificacao': report.score.classificacao
            } if report.score else None,
            'restricoes_financeiras': [
                {
                    'tipo': r.tipo,
                    'origem': r.origem,
                    'valor': r.valor,
                    'data_inclusao': r.data_inclusao.isoformat(),
                    'descricao': r.descricao
                }
                for r in report.restricoes_financeiras
            ],
            'protestos': [
                {
                    'cartorio': p.cartorio,
                    'cidade': p.cidade,
                    'uf': p.uf,
                    'data_protesto': p.data_protesto.isoformat(),
                    'valor': p.valor
                }
                for p in report.protestos
            ],
            'cheques_sem_fundo': [
                {
                    'banco': c.banco,
                    'agencia': c.agencia,
                    'numero_cheque': c.numero_cheque,
                    'data_ocorrencia': c.data_ocorrencia.isoformat(),
                    'valor': c.valor,
                    'motivo': c.motivo
                }
                for c in report.cheques_sem_fundo
            ],
            'acoes_judiciais': [
                {
                    'tribunal': a.tribunal,
                    'numero_processo': a.numero_processo,
                    'tipo': a.tipo,
                    'data_distribuicao': a.data_distribuicao.isoformat(),
                    'valor': a.valor
                }
                for a in report.acoes_judiciais
            ],
            'participacao_sociedades': report.participacao_sociedades,
            'consultas_recentes': report.consultas_recentes,
            'data_consulta': report.data_consulta.isoformat()
        }
        
        if request.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": request.investigation_id,
                "provider": "boavista",
                "query_type": "relatorio_completo",
                "query_params": {"cpf_cnpj": request.cpf_cnpj},
                "result_count": len(report.restricoes_financeiras),
                "response": report_dict,
            })
        
        return {
            "success": True,
            "relatorio": report_dict
        }
    
    except Exception as e:
        logger.error(f"Erro ao consultar Boa Vista: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# IBAMA - Integrações Ambientais
# ======================================================================

class IBAMAEmbargoRequest(BaseModel):
    cpf_cnpj: str
    investigation_id: Optional[int] = None


class IBAMACTFRequest(BaseModel):
    cpf_cnpj: str
    investigation_id: Optional[int] = None


class IBAMAAutoInfracaoRequest(BaseModel):
    numero_auto: str
    investigation_id: Optional[int] = None


@router.post("/ibama/embargos", summary="IBAMA - Consultar Embargos Ambientais")
async def ibama_consultar_embargos(
    request: IBAMAEmbargoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta embargos ambientais do IBAMA por CPF/CNPJ
    
    Retorna:
    - Lista de embargos ativos
    - Áreas embargadas
    - Valores de multas
    - Tipos de infrações
    """
    try:
        from app.services.integrations.ibama_service import IBAMAService
        
        async with IBAMAService() as service:
            embargos = await service.consultar_embargo(request.cpf_cnpj)
            
            # Converter para dict
            embargos_dict = [
                {
                    'numero_auto': e.numero_auto,
                    'cpf_cnpj': e.cpf_cnpj,
                    'nome_autuado': e.nome_autuado,
                    'data_autuacao': e.data_autuacao,
                    'tipo_infracao': e.tipo_infracao,
                    'descricao': e.descricao,
                    'valor_multa': e.valor_multa,
                    'municipio': e.municipio,
                    'uf': e.uf,
                    'status': e.status
                }
                for e in embargos
            ]
            
            # Log auditoria
            if request.investigation_id:
                repo = LegalQueryRepository(db)
                await repo.create({
                    "investigation_id": request.investigation_id,
                    "provider": "ibama",
                    "query_type": "embargos",
                    "query_params": {"cpf_cnpj": request.cpf_cnpj},
                    "result_count": len(embargos),
                    "response": {"embargos": embargos_dict},
                })
            
            return {
                'success': True,
                'total': len(embargos),
                'embargos': embargos_dict
            }
    
    except Exception as e:
        logger.error(f"Erro ao consultar embargos IBAMA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ibama/ctf", summary="IBAMA - Consultar CTF (Cadastro Técnico Federal)")
async def ibama_consultar_ctf(
    request: IBAMACTFRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta Cadastro Técnico Federal (CTF) do IBAMA
    
    Retorna:
    - Número do CTF
    - Situação cadastral
    - Atividades registradas
    - Validade
    """
    try:
        from app.services.integrations.ibama_service import IBAMAService
        
        async with IBAMAService() as service:
            ctf = await service.consultar_ctf(request.cpf_cnpj)
            
            if not ctf:
                return {
                    'success': True,
                    'found': False,
                    'message': 'CTF não encontrado'
                }
            
            ctf_dict = {
                'numero_ctf': ctf.numero_ctf,
                'cpf_cnpj': ctf.cpf_cnpj,
                'razao_social': ctf.razao_social,
                'situacao': ctf.situacao,
                'atividades': ctf.atividades,
                'tipo_pessoa': ctf.tipo_pessoa
            }
            
            # Log auditoria
            if request.investigation_id:
                repo = LegalQueryRepository(db)
                await repo.create({
                    "investigation_id": request.investigation_id,
                    "provider": "ibama",
                    "query_type": "ctf",
                    "query_params": {"cpf_cnpj": request.cpf_cnpj},
                    "result_count": 1,
                    "response": ctf_dict,
                })
            
            return {
                'success': True,
                'found': True,
                'ctf': ctf_dict
            }
    
    except Exception as e:
        logger.error(f"Erro ao consultar CTF IBAMA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ibama/auto-infracao", summary="IBAMA - Consultar Auto de Infração")
async def ibama_consultar_auto_infracao(
    request: IBAMAAutoInfracaoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta auto de infração específico do IBAMA
    """
    try:
        from app.services.integrations.ibama_service import IBAMAService
        
        async with IBAMAService() as service:
            auto = await service.consultar_auto_infracao(request.numero_auto)
            
            if not auto:
                return {
                    'success': True,
                    'found': False,
                    'message': 'Auto de infração não encontrado'
                }
            
            auto_dict = {
                'numero_auto': auto.numero_auto,
                'serie': auto.serie,
                'data_lavratura': auto.data_lavratura,
                'cpf_cnpj_autuado': auto.cpf_cnpj_autuado,
                'nome_autuado': auto.nome_autuado,
                'tipo_infracao': auto.tipo_infracao,
                'valor_auto': auto.valor_auto,
                'municipio': auto.municipio,
                'uf': auto.uf,
                'status': auto.status
            }
            
            return {
                'success': True,
                'found': True,
                'auto': auto_dict
            }
    
    except Exception as e:
        logger.error(f"Erro ao consultar auto de infração IBAMA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# FUNAI - Terras Indígenas
# ======================================================================

class FUNAITerrasRequest(BaseModel):
    municipio: Optional[str] = None
    uf: Optional[str] = None
    nome: Optional[str] = None
    investigation_id: Optional[int] = None


class FUNAISobreposicaoRequest(BaseModel):
    latitude: float
    longitude: float
    raio_km: float = 10.0
    investigation_id: Optional[int] = None


@router.post("/funai/terras-indigenas", summary="FUNAI - Consultar Terras Indígenas")
async def funai_consultar_terras(
    request: FUNAITerrasRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta terras indígenas da FUNAI
    
    Parâmetros:
    - municipio: Filtrar por município (opcional)
    - uf: Filtrar por UF (opcional)
    - nome: Buscar por nome da terra (opcional)
    """
    try:
        from app.services.integrations.funai_service import FUNAIService
        
        async with FUNAIService() as service:
            terras = await service.consultar_terras_indigenas(
                municipio=request.municipio,
                uf=request.uf,
                nome=request.nome
            )
            
            terras_dict = [
                {
                    'nome': t.nome,
                    'etnia': t.etnia,
                    'municipios': t.municipios,
                    'uf': t.uf,
                    'fase': t.fase,
                    'area_hectares': t.area_hectares,
                    'modalidade': t.modalidade,
                    'situacao_fundiaria': t.situacao_fundiaria
                }
                for t in terras
            ]
            
            # Log auditoria
            if request.investigation_id:
                repo = LegalQueryRepository(db)
                await repo.create({
                    "investigation_id": request.investigation_id,
                    "provider": "funai",
                    "query_type": "terras_indigenas",
                    "query_params": {
                        "municipio": request.municipio,
                        "uf": request.uf,
                        "nome": request.nome
                    },
                    "result_count": len(terras),
                    "response": {"terras": terras_dict},
                })
            
            return {
                'success': True,
                'total': len(terras),
                'terras': terras_dict
            }
    
    except Exception as e:
        logger.error(f"Erro ao consultar FUNAI: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/funai/verificar-sobreposicao", summary="FUNAI - Verificar Sobreposição com Terra Indígena")
async def funai_verificar_sobreposicao(
    request: FUNAISobreposicaoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verifica se coordenadas estão em ou próximas de terra indígena
    
    IMPORTANTE: Retorna alerta se houver sobreposição detectada
    """
    try:
        from app.services.integrations.funai_service import FUNAIService
        
        async with FUNAIService() as service:
            resultado = await service.verificar_sobreposicao_por_coordenadas(
                latitude=request.latitude,
                longitude=request.longitude,
                raio_km=request.raio_km
            )
            
            terras_dict = [
                {
                    'nome': t.nome,
                    'etnia': t.etnia,
                    'municipios': t.municipios,
                    'uf': t.uf,
                    'fase': t.fase,
                    'area_hectares': t.area_hectares
                }
                for t in resultado.terras_sobrepostas
            ]
            
            return {
                'success': True,
                'tem_sobreposicao': resultado.tem_sobreposicao,
                'total_terras': len(resultado.terras_sobrepostas),
                'terras_sobrepostas': terras_dict,
                'alerta': '⚠️ SOBREPOSIÇÃO COM TERRA INDÍGENA DETECTADA!' if resultado.tem_sobreposicao else None
            }
    
    except Exception as e:
        logger.error(f"Erro ao verificar sobreposição FUNAI: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# ICMBio - Unidades de Conservação
# ======================================================================

class ICMBioUnidadesRequest(BaseModel):
    municipio: Optional[str] = None
    uf: Optional[str] = None
    categoria: Optional[str] = None
    grupo: Optional[str] = None
    investigation_id: Optional[int] = None


class ICMBioSobreposicaoRequest(BaseModel):
    latitude: float
    longitude: float
    raio_km: float = 10.0
    investigation_id: Optional[int] = None


@router.post("/icmbio/unidades-conservacao", summary="ICMBio - Consultar Unidades de Conservação")
async def icmbio_consultar_unidades(
    request: ICMBioUnidadesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consulta unidades de conservação do ICMBio
    
    Parâmetros:
    - municipio: Filtrar por município (opcional)
    - uf: Filtrar por UF (opcional)
    - categoria: Categoria da UC (opcional)
    - grupo: "Proteção Integral" ou "Uso Sustentável" (opcional)
    """
    try:
        from app.services.integrations.icmbio_service import ICMBioService
        
        async with ICMBioService() as service:
            unidades = await service.consultar_unidades_conservacao(
                municipio=request.municipio,
                uf=request.uf,
                categoria=request.categoria,
                grupo=request.grupo
            )
            
            unidades_dict = [
                {
                    'nome': u.nome,
                    'categoria': u.categoria,
                    'grupo': u.grupo,
                    'esfera': u.esfera,
                    'municipios': u.municipios,
                    'uf': u.uf,
                    'area_hectares': u.area_hectares,
                    'ato_legal': u.ato_legal,
                    'ano_criacao': u.ano_criacao,
                    'bioma': u.bioma
                }
                for u in unidades
            ]
            
            # Log auditoria
            if request.investigation_id:
                repo = LegalQueryRepository(db)
                await repo.create({
                    "investigation_id": request.investigation_id,
                    "provider": "icmbio",
                    "query_type": "unidades_conservacao",
                    "query_params": {
                        "municipio": request.municipio,
                        "uf": request.uf,
                        "categoria": request.categoria,
                        "grupo": request.grupo
                    },
                    "result_count": len(unidades),
                    "response": {"unidades": unidades_dict},
                })
            
            return {
                'success': True,
                'total': len(unidades),
                'unidades': unidades_dict
            }
    
    except Exception as e:
        logger.error(f"Erro ao consultar ICMBio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/icmbio/verificar-sobreposicao", summary="ICMBio - Verificar Sobreposição com UC")
async def icmbio_verificar_sobreposicao(
    request: ICMBioSobreposicaoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verifica se coordenadas estão em ou próximas de unidade de conservação
    
    IMPORTANTE: Retorna alerta se houver sobreposição detectada
    """
    try:
        from app.services.integrations.icmbio_service import ICMBioService
        
        async with ICMBioService() as service:
            resultado = await service.verificar_sobreposicao_por_coordenadas(
                latitude=request.latitude,
                longitude=request.longitude,
                raio_km=request.raio_km
            )
            
            unidades_dict = [
                {
                    'nome': u.nome,
                    'categoria': u.categoria,
                    'grupo': u.grupo,
                    'municipios': u.municipios,
                    'uf': u.uf,
                    'area_hectares': u.area_hectares
                }
                for u in resultado.unidades_sobrepostas
            ]
            
            return {
                'success': True,
                'tem_sobreposicao': resultado.tem_sobreposicao,
                'total_unidades': len(resultado.unidades_sobrepostas),
                'unidades_sobrepostas': unidades_dict,
                'alerta': '⚠️ SOBREPOSIÇÃO COM UNIDADE DE CONSERVAÇÃO DETECTADA!' if resultado.tem_sobreposicao else None
            }
    
    except Exception as e:
        logger.error(f"Erro ao verificar sobreposição ICMBio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health Check

@router.get("/health", summary="Status das integrações")
async def integrations_health():
    """Verifica status de todas as integrações"""
    return {
        "car": {
            "status": "available",
            "states": 27
        },
        "tribunais": {
            "status": "available",
            "systems": ["esaj", "projudi", "pje"]
        },
        "orgaos_federais": {
            "status": "available",
            "services": ["ibama", "icmbio", "funai", "spu", "cvm"]
        },
        "bureaus": {
            "status": "requires_api_keys",
            "services": ["serasa", "boavista"]
        },
        "comunicacao": {
            "status": "requires_webhooks",
            "services": ["slack", "teams"]
        },
        "ocr": {
            "status": "available",
            "services": ["tesseract", "pdf2image"]
        },
        "environmental": {
            "status": "available",
            "services": ["ibama", "funai", "icmbio"]
        }
    }
