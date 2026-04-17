"""
API Endpoints - Integrações Jurídicas
Endpoints para integração com sistemas processuais e exportação de due diligence
"""
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db, get_current_user
from app.domain.user import User
from app.services.legal_integration import (
    legal_integration_service,
    PJeCase,
    DueDiligenceExport,
    LegalSystemIntegration
)
from app.services.datajud import DataJudService
from app.repositories.legal_query import LegalQueryRepository
from app.core.audit import AuditLogger

# Inicializar o audit logger
audit_logger = AuditLogger()

router = APIRouter()

# ==================== Pydantic Models ====================

class PJeConsultaRequest(BaseModel):
    """Request para consulta de processo no PJe"""
    numero_processo: str = Field(..., description="Número do processo CNJ")
    tribunal: str = Field(..., description="Código do tribunal")

class PJePartConsultaRequest(BaseModel):
    """Request para consulta de processos por parte"""
    cpf_cnpj: str = Field(..., description="CPF ou CNPJ")
    tipo_parte: str = Field(default="qualquer", description="Tipo de participação")

class SincronizarProcessosRequest(BaseModel):
    """Request para sincronização de processos"""
    cpf_cnpj: str = Field(..., description="CPF ou CNPJ")
    investigation_id: Optional[int] = Field(None, description="ID da investigação")

class ExportDueDiligenceRequest(BaseModel):
    """Request para exportação de due diligence"""
    investigation_id: int = Field(..., description="ID da investigação")
    target_system: Optional[LegalSystemIntegration] = None

class IntegrationConfigRequest(BaseModel):
    """Request para configurar integração"""
    system_name: str
    api_endpoint: str
    api_key: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None
    enabled: bool = True


class DataJudProxyRequest(BaseModel):
    """Request genérico para DataJud"""
    path: str = Field(..., description="Path relativo da API DataJud (ex: /tribunais/TRT2/_search)")
    method: Literal["GET", "POST"] = "POST"
    params: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None
    investigation_id: Optional[int] = Field(None, description="ID da investigação")
    query_type: Optional[str] = Field(None, description="Tipo de consulta (ex: processos, movimentacoes)")


def _datajud_result_count(result: Dict[str, Any]) -> int:
    if isinstance(result, dict):
        if isinstance(result.get("hits"), list):
            return len(result["hits"])
        if isinstance(result.get("processos"), list):
            return len(result["processos"])
    return 0

# ==================== Endpoints PJe ====================

@router.post("/pje/consultar-processo", response_model=Optional[PJeCase])
async def consultar_processo_pje(
    data: PJeConsultaRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🔍 Consulta processo no PJe por número
    
    Permite consultar um processo específico no sistema PJe
    """
    try:
        # Consultar processo
        processo = await legal_integration_service.pje_service.consultar_processo(
            data.numero_processo,
            data.tribunal
        )
        
        # Log de auditoria
        await audit_logger.log_action(
            db=db,
            user_id=current_user.id,
            action="consulta_processo_pje",
            resource_type="pje",
            resource_id=data.numero_processo,
            details={
                "numero_processo": data.numero_processo,
                "tribunal": data.tribunal,
                "encontrado": processo is not None
            },
            ip_address=request.client.host
        )
        
        if not processo:
            raise HTTPException(status_code=404, detail="Processo não encontrado")
        
        return processo
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar PJe: {str(e)}")

@router.post("/pje/consultar-processos-parte")
async def consultar_processos_parte(
    data: PJePartConsultaRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    👤 Consulta processos de uma parte (CPF/CNPJ)
    
    Retorna todos os processos em que a pessoa/empresa é parte
    """
    try:
        # Consultar processos
        processos = await legal_integration_service.pje_service.consultar_processos_parte(
            data.cpf_cnpj,
            data.tipo_parte
        )
        
        # Log de auditoria
        await audit_logger.log_action(
            db=db,
            user_id=current_user.id,
            action="consulta_processos_parte",
            resource_type="pje",
            resource_id=data.cpf_cnpj,
            details={
                "cpf_cnpj": data.cpf_cnpj,
                "tipo_parte": data.tipo_parte,
                "total_encontrados": len(processos)
            },
            ip_address=request.client.host
        )
        
        return {
            "success": True,
            "total": len(processos),
            "processos": [p.dict() for p in processos]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar processos: {str(e)}")

@router.get("/pje/movimentacoes/{numero_processo}")
async def obter_movimentacoes(
    numero_processo: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📋 Obtém movimentações de um processo
    
    Retorna todas as movimentações e andamentos do processo
    """
    try:
        # Obter movimentações
        movimentacoes = await legal_integration_service.pje_service.obter_movimentacoes(
            numero_processo
        )
        
        # Log de auditoria
        await audit_logger.log_action(
            db=db,
            user_id=current_user.id,
            action="consulta_movimentacoes",
            resource_type="pje",
            resource_id=numero_processo,
            details={
                "numero_processo": numero_processo,
                "total_movimentacoes": len(movimentacoes)
            },
            ip_address=request.client.host
        )
        
        return {
            "success": True,
            "numero_processo": numero_processo,
            "total": len(movimentacoes),
            "movimentacoes": movimentacoes
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter movimentações: {str(e)}")


# ==================== DataJud (CNJ) ====================

@router.post("/datajud/proxy")
async def datajud_proxy(
    data: DataJudProxyRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🔎 Proxy para API Pública do DataJud (CNJ)
    """
    try:
        service = DataJudService()
        result = await service.request(
            method=data.method,
            path=data.path,
            params=data.params,
            payload=data.payload,
        )

        if data.investigation_id:
            repo = LegalQueryRepository(db)
            await repo.create({
                "investigation_id": data.investigation_id,
                "provider": "datajud",
                "query_type": data.query_type or data.path,
                "query_params": {"params": data.params or {}, "payload": data.payload or {}},
                "result_count": _datajud_result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            })

        await audit_logger.log_action(
            db=db,
            user_id=current_user.id,
            action="consulta_datajud",
            resource_type="datajud",
            resource_id=data.path,
            details={"method": data.method, "path": data.path},
            ip_address=request.client.host
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro DataJud: {str(e)}")


@router.get("/queries/summary")
async def get_legal_queries_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = LegalQueryRepository(db)
    summary = await repo.summary_by_user(current_user.id)
    return {
        "summary": summary,
        "updated_at": datetime.utcnow().isoformat(),
    }


@router.get("/queries/investigation/{investigation_id}")
async def list_legal_queries_by_investigation(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = LegalQueryRepository(db)
    queries = await repo.list_by_investigation(investigation_id)
    return [
        {
            "id": q.id,
            "provider": q.provider,
            "query_type": q.query_type,
            "query_params": q.query_params,
            "result_count": q.result_count,
            "response": q.response,
            "created_at": q.created_at.isoformat(),
        }
        for q in queries
    ]

# ==================== Endpoints Due Diligence ====================

@router.post("/due-diligence/gerar")
async def gerar_due_diligence(
    investigation_id: int = Query(..., description="ID da investigação"),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📊 Gera relatório de due diligence
    
    Cria um relatório completo de due diligence para a investigação
    """
    try:
        # Gerar relatório
        report = await legal_integration_service.due_diligence_service.gerar_relatorio_completo(
            db, investigation_id
        )
        
        # Log de auditoria
        await audit_logger.log_action(
            db=db,
            user_id=current_user.id,
            action="gerar_due_diligence",
            resource_type="investigation",
            resource_id=str(investigation_id),
            details={
                "investigation_id": investigation_id,
                "target_name": report.target_name,
                "risk_level": report.risk_analysis.get("overall_risk")
            },
            ip_address=request.client.host if request else None
        )
        
        return {
            "success": True,
            "report": report.dict()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar due diligence: {str(e)}")

@router.post("/due-diligence/exportar")
async def exportar_due_diligence(
    data: ExportDueDiligenceRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📤 Exporta due diligence para sistema externo
    
    Envia relatório de due diligence para ferramenta jurídica integrada
    """
    try:
        # Gerar e exportar
        result = await legal_integration_service.gerar_e_exportar_due_diligence(
            db,
            data.investigation_id,
            data.target_system
        )
        
        # Log de auditoria
        await audit_logger.log_action(
            db=db,
            user_id=current_user.id,
            action="exportar_due_diligence",
            resource_type="investigation",
            resource_id=str(data.investigation_id),
            details={
                "investigation_id": data.investigation_id,
                "target_system": data.target_system.system_name if data.target_system else None,
                "success": result.get("success", False)
            },
            ip_address=request.client.host
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar: {str(e)}")

# ==================== Endpoints de Sincronização ====================

@router.post("/sincronizar-processos")
async def sincronizar_processos(
    data: SincronizarProcessosRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🔄 Sincroniza processos judiciais
    
    Busca e sincroniza processos de uma parte no PJe com o banco de dados
    """
    try:
        # Sincronizar
        result = await legal_integration_service.sincronizar_processos(
            db,
            data.cpf_cnpj,
            data.investigation_id
        )
        
        # Log de auditoria
        await audit_logger.log_action(
            db=db,
            user_id=current_user.id,
            action="sincronizar_processos",
            resource_type="pje",
            resource_id=data.cpf_cnpj,
            details={
                "cpf_cnpj": data.cpf_cnpj,
                "investigation_id": data.investigation_id,
                "total_processos": result.get("total_processos", 0),
                "success": result.get("success", False)
            },
            ip_address=request.client.host
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao sincronizar: {str(e)}")

# ==================== Endpoints de Configuração ====================

@router.post("/integrations/configure")
async def configurar_integracao(
    data: IntegrationConfigRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ⚙️ Configura integração com sistema jurídico
    
    Define configurações para integração com sistema externo
    """
    # TODO: Salvar configuração no banco de dados
    # integration = LegalIntegration(**data.dict(), user_id=current_user.id)
    # db.add(integration)
    # db.commit()
    
    # Log de auditoria
    await audit_logger.log_action(
        db=db,
        user_id=current_user.id,
        action="configurar_integracao",
        resource_type="integration",
        resource_id=data.system_name,
        details={
            "system_name": data.system_name,
            "api_endpoint": data.api_endpoint,
            "enabled": data.enabled
        },
        ip_address=request.client.host
    )
    
    return {
        "success": True,
        "message": "Integração configurada com sucesso",
        "integration": data.dict()
    }

@router.get("/integrations/list")
async def listar_integracoes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📋 Lista integrações configuradas
    
    Retorna todas as integrações jurídicas configuradas pelo usuário
    """
    # TODO: Buscar integrações do banco de dados
    # integrations = db.query(LegalIntegration).filter_by(user_id=current_user.id).all()
    
    # Exemplo mockado
    integrations = [
        {
            "system_name": "PJe",
            "enabled": True,
            "description": "Processo Judicial Eletrônico"
        },
        {
            "system_name": "Thomson Reuters",
            "enabled": False,
            "description": "Plataforma de due diligence"
        }
    ]
    
    return {
        "success": True,
        "total": len(integrations),
        "integrations": integrations
    }
