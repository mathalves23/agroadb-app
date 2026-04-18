"""Integrações — IBAMA, FUNAI, ICMBio (fiscalização ambiental)."""

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
                    "numero_auto": e.numero_auto,
                    "cpf_cnpj": e.cpf_cnpj,
                    "nome_autuado": e.nome_autuado,
                    "data_autuacao": e.data_autuacao,
                    "tipo_infracao": e.tipo_infracao,
                    "descricao": e.descricao,
                    "valor_multa": e.valor_multa,
                    "municipio": e.municipio,
                    "uf": e.uf,
                    "status": e.status,
                }
                for e in embargos
            ]

            await record_legal_query_if_investigation(
                db,
                request.investigation_id,
                provider="ibama",
                query_type="embargos",
                query_params={"cpf_cnpj": request.cpf_cnpj},
                result_count=len(embargos),
                response={"embargos": embargos_dict},
            )

            return {"success": True, "total": len(embargos), "embargos": embargos_dict}

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
                return {"success": True, "found": False, "message": "CTF não encontrado"}

            ctf_dict = {
                "numero_ctf": ctf.numero_ctf,
                "cpf_cnpj": ctf.cpf_cnpj,
                "razao_social": ctf.razao_social,
                "situacao": ctf.situacao,
                "atividades": ctf.atividades,
                "tipo_pessoa": ctf.tipo_pessoa,
            }

            await record_legal_query_if_investigation(
                db,
                request.investigation_id,
                provider="ibama",
                query_type="ctf",
                query_params={"cpf_cnpj": request.cpf_cnpj},
                result_count=1,
                response=ctf_dict,
            )

            return {"success": True, "found": True, "ctf": ctf_dict}

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
                    "success": True,
                    "found": False,
                    "message": "Auto de infração não encontrado",
                }

            auto_dict = {
                "numero_auto": auto.numero_auto,
                "serie": auto.serie,
                "data_lavratura": auto.data_lavratura,
                "cpf_cnpj_autuado": auto.cpf_cnpj_autuado,
                "nome_autuado": auto.nome_autuado,
                "tipo_infracao": auto.tipo_infracao,
                "valor_auto": auto.valor_auto,
                "municipio": auto.municipio,
                "uf": auto.uf,
                "status": auto.status,
            }

            return {"success": True, "found": True, "auto": auto_dict}

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
                municipio=request.municipio, uf=request.uf, nome=request.nome
            )

            terras_dict = [
                {
                    "nome": t.nome,
                    "etnia": t.etnia,
                    "municipios": t.municipios,
                    "uf": t.uf,
                    "fase": t.fase,
                    "area_hectares": t.area_hectares,
                    "modalidade": t.modalidade,
                    "situacao_fundiaria": t.situacao_fundiaria,
                }
                for t in terras
            ]

            await record_legal_query_if_investigation(
                db,
                request.investigation_id,
                provider="funai",
                query_type="terras_indigenas",
                query_params={
                    "municipio": request.municipio,
                    "uf": request.uf,
                    "nome": request.nome,
                },
                result_count=len(terras),
                response={"terras": terras_dict},
            )

            return {"success": True, "total": len(terras), "terras": terras_dict}

    except Exception as e:
        logger.error(f"Erro ao consultar FUNAI: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/funai/verificar-sobreposicao", summary="FUNAI - Verificar Sobreposição com Terra Indígena"
)
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
                latitude=request.latitude, longitude=request.longitude, raio_km=request.raio_km
            )

            terras_dict = [
                {
                    "nome": t.nome,
                    "etnia": t.etnia,
                    "municipios": t.municipios,
                    "uf": t.uf,
                    "fase": t.fase,
                    "area_hectares": t.area_hectares,
                }
                for t in resultado.terras_sobrepostas
            ]

            return {
                "success": True,
                "tem_sobreposicao": resultado.tem_sobreposicao,
                "total_terras": len(resultado.terras_sobrepostas),
                "terras_sobrepostas": terras_dict,
                "alerta": (
                    "⚠️ SOBREPOSIÇÃO COM TERRA INDÍGENA DETECTADA!"
                    if resultado.tem_sobreposicao
                    else None
                ),
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
                grupo=request.grupo,
            )

            unidades_dict = [
                {
                    "nome": u.nome,
                    "categoria": u.categoria,
                    "grupo": u.grupo,
                    "esfera": u.esfera,
                    "municipios": u.municipios,
                    "uf": u.uf,
                    "area_hectares": u.area_hectares,
                    "ato_legal": u.ato_legal,
                    "ano_criacao": u.ano_criacao,
                    "bioma": u.bioma,
                }
                for u in unidades
            ]

            await record_legal_query_if_investigation(
                db,
                request.investigation_id,
                provider="icmbio",
                query_type="unidades_conservacao",
                query_params={
                    "municipio": request.municipio,
                    "uf": request.uf,
                    "categoria": request.categoria,
                    "grupo": request.grupo,
                },
                result_count=len(unidades),
                response={"unidades": unidades_dict},
            )

            return {"success": True, "total": len(unidades), "unidades": unidades_dict}

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
                latitude=request.latitude, longitude=request.longitude, raio_km=request.raio_km
            )

            unidades_dict = [
                {
                    "nome": u.nome,
                    "categoria": u.categoria,
                    "grupo": u.grupo,
                    "municipios": u.municipios,
                    "uf": u.uf,
                    "area_hectares": u.area_hectares,
                }
                for u in resultado.unidades_sobrepostas
            ]

            return {
                "success": True,
                "tem_sobreposicao": resultado.tem_sobreposicao,
                "total_unidades": len(resultado.unidades_sobrepostas),
                "unidades_sobrepostas": unidades_dict,
                "alerta": (
                    "⚠️ SOBREPOSIÇÃO COM UNIDADE DE CONSERVAÇÃO DETECTADA!"
                    if resultado.tem_sobreposicao
                    else None
                ),
            }

    except Exception as e:
        logger.error(f"Erro ao verificar sobreposição ICMBio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
