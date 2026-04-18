"""Sub-router órgãos federais, birôs e notificações (Slack/Teams)."""
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

