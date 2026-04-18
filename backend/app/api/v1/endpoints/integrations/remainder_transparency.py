"""Integrações — transparência federal, REDESIM, IBGE, TSE, CVM, BCB, dados.gov."""

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
            detail="Portal da Transparência não configurado. Configure PORTAL_TRANSPARENCIA_API_KEY no arquivo .env",
        )

    try:
        ceis = await service.consultar_ceis(request.cpf_cnpj)
        cnep = await service.consultar_cnep(request.cpf_cnpj)
        result = {"ceis": ceis, "cnep": cnep}
        total = (ceis.get("total", 0) or 0) + (cnep.get("total", 0) or 0)
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="portal_transparencia",
            query_type="sancoes",
            query_params={"cpf_cnpj": request.cpf_cnpj},
            result_count=total,
            response=result,
        )
        return _conecta_standard_response(result)
    except ValueError as e:
        error_msg = str(e)
        if "401" in error_msg or "Chave de API" in error_msg:
            raise HTTPException(
                status_code=401, detail="API Key do Portal da Transparência inválida ou expirada"
            )
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
            detail="Portal da Transparência não configurado. Configure PORTAL_TRANSPARENCIA_API_KEY no arquivo .env",
        )

    try:
        result = await service.consultar_contratos(request.cpf_cnpj)
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="portal_transparencia",
            query_type="contratos",
            query_params={"cpf_cnpj": request.cpf_cnpj},
            result_count=result.get("total", 0),
            response=result,
        )
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
            detail="Portal da Transparência não configurado. Configure PORTAL_TRANSPARENCIA_API_KEY no arquivo .env",
        )

    try:
        result = await service.consultar_servidores(request.cpf_cnpj)
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="portal_transparencia",
            query_type="servidores",
            query_params={"cpf": request.cpf_cnpj},
            result_count=result.get("total", 0),
            response=result,
        )
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
            detail="Portal da Transparência não configurado. Configure PORTAL_TRANSPARENCIA_API_KEY no arquivo .env",
        )

    try:
        result = await service.consultar_beneficios(request.cpf_cnpj)
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="portal_transparencia",
            query_type="beneficios",
            query_params={"cpf": request.cpf_cnpj},
            result_count=result.get("total", 0),
            response=result,
        )
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
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="portal_transparencia",
            query_type="despesas",
            query_params={"cpf_cnpj": request.cpf_cnpj},
            result_count=result.get("total", 0),
            response=result,
        )
        return _conecta_standard_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/transparencia/completa",
    summary="Transparência - Consulta completa (sanções + contratos + servidores + benefícios)",
)
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

    await record_legal_query_if_investigation(
        db,
        request.investigation_id,
        provider="portal_transparencia",
        query_type="completa",
        query_params={"cpf_cnpj": request.cpf_cnpj},
        result_count=total_count,
        response=result,
    )

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
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="redesim_cnpj",
            query_type="cnpj",
            query_params={"cnpj": request.cnpj},
            result_count=1 if not result.get("error") else 0,
            response=result,
        )
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
        count = result.get("result", {}).get("count", 0) if isinstance(result, dict) else 0
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="tse",
            query_type="busca",
            query_params={"query": request.query},
            result_count=count,
            response=result,
        )
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
        count = result.get("result", {}).get("count", 0) if isinstance(result, dict) else 0
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="cvm",
            query_type="fundos",
            query_params={"cnpj": request.cnpj, "nome": request.nome},
            result_count=count,
            response=result,
        )
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
        count = result.get("result", {}).get("count", 0) if isinstance(result, dict) else 0
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="cvm",
            query_type="fii",
            query_params={"cnpj": request.cnpj},
            result_count=count,
            response=result,
        )
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
async def bcb_cambio(
    moeda: str, data: Optional[str] = None, current_user: User = Depends(get_current_user)
):
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
