"""Sub-router Conecta gov.br + SIGEF parcelas (WS)."""
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
from app.api.v1.endpoints.integrations_helpers import (
    result_count as _result_count,
    is_credentials_missing as _is_credentials_missing,
    conecta_items as _conecta_items,
    conecta_standard_response as _conecta_standard_response,
)

logger = logging.getLogger(__name__)
audit_logger = AuditLogger()
router = APIRouter()

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

