"""Integrações — tribunais estaduais, fiscalização cadastral, birôs de crédito, órgãos."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
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
from app.core.audit import AuditLogger
from app.services.legal_query_audit import record_legal_query_if_investigation
from app.api.v1.endpoints.integrations_helpers import (
    result_count as _result_count,
    is_credentials_missing as _is_credentials_missing,
    conecta_items as _conecta_items,
    conecta_standard_response as _conecta_standard_response,
)

logger = logging.getLogger(__name__)
audit_logger = AuditLogger()

router = APIRouter()

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
        params = {k: v for k, v in request.model_dump().items() if v is not None and k != "investigation_id"}
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="tjmg",
            query_type="processos",
            query_params=params,
            result_count=_result_count(result),
            response=result,
        )
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
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="tjmg",
            query_type="processos_cpf",
            query_params={"cpf": request.cpf},
            result_count=_result_count(result),
            response=result,
        )
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
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="tjmg",
            query_type="processos_cnpj",
            query_params={"cnpj": request.cnpj},
            result_count=_result_count(result),
            response=result,
        )
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
        await record_legal_query_if_investigation(
            db,
            investigation_id,
            provider="tjmg",
            query_type="processo_numero",
            query_params={"numero_processo": numero_processo},
            result_count=_result_count(result),
            response=result,
        )
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
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="antecedentes_mg",
            query_type="consulta",
            query_params={"cpf": request.cpf[:4] + "***", "rg": "***"},
            result_count=1 if result.get("conseguiu_emitir_certidao_negativa") is not None else 0,
            response=result,
        )
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
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="sicar_publico",
            query_type="imovel_car",
            query_params={"car": request.car},
            result_count=1 if result.get("area") or result.get("municipio") else 0,
            response=result,
        )
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

        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="caixa_fgts",
            query_type="regularidade",
            query_params={"cnpj": request.cnpj, "cei": request.cei},
            result_count=1 if result.get("situacao") else 0,
            response=result,
        )
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

    await record_legal_query_if_investigation(
        db,
        request.investigation_id,
        provider="bnmp_cnj",
        query_type="mandados_prisao",
        query_params={"cpf": request.cpf, "nome": request.nome},
        result_count=result.get("total", 0),
        response=result,
        ignore_errors=True,
    )

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

        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="seeu_cnj",
            query_type="processos_execucao",
            query_params={
                "cpf": request.cpf,
                "cnpj": request.cnpj,
                "nome_parte": request.nome_parte,
                "numero_processo": request.numero_processo,
            },
            result_count=result.get("total", 0),
            response=result,
        )
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

    await record_legal_query_if_investigation(
        db,
        request.investigation_id,
        provider="sigef_publico",
        query_type="parcelas",
        query_params={
            "cpf": request.cpf,
            "cnpj": request.cnpj,
            "codigo_imovel": request.codigo_imovel,
        },
        result_count=result.get("resultados_retornados", 0),
        response=result,
        ignore_errors=True,
    )

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

        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="receita_cpf",
            query_type="situacao_cadastral",
            query_params={"cpf": request.cpf},
            result_count=1 if result.get("situacao_cadastral") else 0,
            response=result,
        )
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

        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="receita_cnpj",
            query_type="dados_cadastrais_pj",
            query_params={"cnpj": request.cnpj},
            result_count=1 if result.get("razao_social") else 0,
            response=result,
        )
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
        
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="serasa",
            query_type="score",
            query_params={"cpf_cnpj": request.cpf_cnpj},
            result_count=1,
            response=score_dict,
        )

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
        
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="serasa",
            query_type="relatorio_completo",
            query_params={"cpf_cnpj": request.cpf_cnpj},
            result_count=len(report.restricoes),
            response=report_dict,
        )

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
        
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="boavista",
            query_type="score",
            query_params={"cpf_cnpj": request.cpf_cnpj},
            result_count=1,
            response=score_dict,
        )

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
        
        await record_legal_query_if_investigation(
            db,
            request.investigation_id,
            provider="boavista",
            query_type="relatorio_completo",
            query_params={"cpf_cnpj": request.cpf_cnpj},
            result_count=len(report.restricoes_financeiras),
            response=report_dict,
        )

        return {
            "success": True,
            "relatorio": report_dict
        }
    
    except Exception as e:
        logger.error(f"Erro ao consultar Boa Vista: {e}")
        raise HTTPException(status_code=500, detail=str(e))

