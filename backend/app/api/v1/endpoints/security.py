"""
Endpoints de Segurança e LGPD
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime, date

from app.api.v1.deps import get_current_user, get_db
from app.domain.user import User
from app.core.audit import audit_logger, AuditAction
from app.core.lgpd import lgpd_service, ConsentType
from app.core.two_factor import two_factor_service
from pydantic import BaseModel, EmailStr

router = APIRouter()


# ==================== Schemas ====================


class Enable2FARequest(BaseModel):
    password: str  # Requer senha para ativação


class Verify2FARequest(BaseModel):
    token: str


class ConsentRequest(BaseModel):
    consent_type: ConsentType
    accept: bool


class DataDeletionRequestModel(BaseModel):
    reason: Optional[str] = None


# ==================== 2FA Endpoints ====================


@router.post("/2fa/enable")
async def enable_two_factor_auth(
    request: Request,
    data: Enable2FARequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Habilita autenticação de dois fatores
    
    **Retorna**:
    - QR Code para escanear no app autenticador
    - Secret manual (caso não consiga escanear)
    - Códigos de backup para emergências
    
    **Apps Compatíveis**:
    - Google Authenticator
    - Microsoft Authenticator
    - Authy
    - 1Password
    """
    # TODO: Verificar senha do usuário
    # if not verify_password(data.password, current_user.hashed_password):
    #     raise HTTPException(status_code=401, detail="Senha incorreta")
    
    result = await two_factor_service.enable_2fa(db, current_user.id, current_user.email)
    
    # Audit log
    await audit_logger.log(
        db,
        action=AuditAction.TWO_FA_ENABLED,
        user_id=current_user.id,
        username=current_user.email,
        ip_address=request.client.host if request.client else None,
        details={"step": "initiated"}
    )
    
    return {
        "status": "initiated",
        "message": "Escaneie o QR Code no seu app autenticador e confirme com o código gerado",
        "qr_code": result["qr_code"],
        "secret": result["secret"],
        "backup_codes": result["backup_codes"],
        "backup_codes_warning": "Guarde estes códigos em local seguro. Eles só serão mostrados uma vez!"
    }


@router.post("/2fa/confirm")
async def confirm_two_factor_auth(
    request: Request,
    data: Verify2FARequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Confirma e ativa 2FA
    
    Após escanear o QR Code, use o código do app para confirmar
    """
    success = await two_factor_service.confirm_and_enable_2fa(
        db,
        current_user.id,
        data.token
    )
    
    if not success:
        await audit_logger.log(
            db,
            action=AuditAction.TWO_FA_FAILED,
            user_id=current_user.id,
            username=current_user.email,
            ip_address=request.client.host if request.client else None,
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido. Tente novamente."
        )
    
    await audit_logger.log(
        db,
        action=AuditAction.TWO_FA_ENABLED,
        user_id=current_user.id,
        username=current_user.email,
        ip_address=request.client.host if request.client else None,
        details={"step": "confirmed"}
    )
    
    return {
        "status": "enabled",
        "message": "Autenticação de dois fatores ativada com sucesso!"
    }


@router.post("/2fa/disable")
async def disable_two_factor_auth(
    request: Request,
    data: Verify2FARequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Desabilita autenticação de dois fatores
    
    Requer código do app autenticador para confirmar
    """
    success = await two_factor_service.disable_2fa(
        db,
        current_user.id,
        data.token
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido ou 2FA não está habilitado"
        )
    
    await audit_logger.log(
        db,
        action=AuditAction.TWO_FA_DISABLED,
        user_id=current_user.id,
        username=current_user.email,
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "status": "disabled",
        "message": "Autenticação de dois fatores desabilitada"
    }


@router.get("/2fa/status")
async def get_2fa_status(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Retorna status do 2FA"""
    status = await two_factor_service.get_status(db, current_user.id)
    
    return {
        "is_enabled": status["is_enabled"] if status else False,
        "has_backup_codes": status["has_backup_codes"] if status else False
    }


# ==================== LGPD Endpoints ====================


@router.post("/lgpd/consent")
async def record_user_consent(
    request: Request,
    data: ConsentRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Registra consentimento do usuário (Art. 8 LGPD)
    
    **Tipos de consentimento**:
    - `terms_of_service`: Termos de Uso
    - `privacy_policy`: Política de Privacidade
    - `data_processing`: Tratamento de Dados
    - `marketing`: Comunicações de Marketing (opcional)
    - `third_party_sharing`: Compartilhamento com Terceiros (opcional)
    """
    if data.accept:
        consent = await lgpd_service.record_consent(
            db,
            current_user.id,
            data.consent_type,
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        
        await audit_logger.log(
            db,
            action=AuditAction.CONSENT_GIVEN,
            user_id=current_user.id,
            username=current_user.email,
            details={"consent_type": data.consent_type.value}
        )
        
        return {
            "status": "success",
            "message": "Consentimento registrado",
            "consent": consent.to_dict()
        }
    else:
        await lgpd_service.revoke_consent(db, current_user.id, data.consent_type)
        
        await audit_logger.log(
            db,
            action=AuditAction.CONSENT_REVOKED,
            user_id=current_user.id,
            username=current_user.email,
            details={"consent_type": data.consent_type.value}
        )
        
        return {
            "status": "revoked",
            "message": "Consentimento revogado"
        }


@router.get("/lgpd/my-data")
async def get_my_personal_data(
    request: Request,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Retorna relatório completo de dados pessoais (Direito de Acesso - Art. 18, II)
    
    Inclui:
    - Dados cadastrais
    - Consentimentos dados
    - Histórico de acessos
    - Políticas de retenção
    - Lista de direitos LGPD
    """
    report = await lgpd_service.generate_personal_data_report(db, current_user.id)
    
    await audit_logger.log(
        db,
        action=AuditAction.PERSONAL_DATA_ACCESSED,
        user_id=current_user.id,
        username=current_user.email,
        ip_address=request.client.host if request.client else None,
        details={"type": "full_report"}
    )
    
    return report


@router.post("/lgpd/delete-my-data")
async def request_data_deletion(
    request: Request,
    data: DataDeletionRequestModel,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Solicita exclusão de dados pessoais (Direito à Exclusão - Art. 18, VI)
    
    **Importante**:
    - A solicitação será analisada em até 15 dias úteis
    - Alguns dados podem ser mantidos por obrigação legal (5 anos para fins fiscais)
    - Você receberá confirmação por email quando processado
    - Dados de investigações podem ser anonimizados ao invés de excluídos
    """
    deletion_request = await lgpd_service.request_data_deletion(
        db,
        current_user.id,
        data.reason
    )
    
    await audit_logger.log(
        db,
        action=AuditAction.PERSONAL_DATA_DELETED,
        user_id=current_user.id,
        username=current_user.email,
        ip_address=request.client.host if request.client else None,
        details={"request_id": deletion_request.id, "reason": data.reason}
    )
    
    return {
        "status": "pending",
        "message": "Solicitação de exclusão registrada. Você receberá um email em até 15 dias úteis.",
        "request_id": deletion_request.id,
        "requested_at": deletion_request.requested_at.isoformat(),
        "important_note": "Alguns dados podem ser mantidos por obrigação legal (5 anos para fins fiscais)"
    }


@router.get("/lgpd/export-data")
async def export_my_data(
    request: Request,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Exporta dados pessoais em formato JSON (Direito à Portabilidade - Art. 18, V)
    
    Permite transferir seus dados para outra plataforma
    """
    report = await lgpd_service.generate_personal_data_report(db, current_user.id)
    
    await audit_logger.log(
        db,
        action=AuditAction.PERSONAL_DATA_EXPORTED,
        user_id=current_user.id,
        username=current_user.email,
        ip_address=request.client.host if request.client else None,
        details={"format": "json"}
    )
    
    return JSONResponse(
        content=report,
        headers={
            "Content-Disposition": f"attachment; filename=my_data_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
        }
    )


# ==================== Audit Log Endpoints ====================


@router.get("/audit/my-activity")
async def get_my_audit_logs(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Retorna histórico de atividades do usuário logado
    
    **Útil para**:
    - Ver histórico de acessos
    - Detectar atividades suspeitas
    - Auditoria pessoal
    """
    logs = await audit_logger.get_user_logs(db, current_user.id, limit, offset)
    
    return {
        "total": len(logs),
        "limit": limit,
        "offset": offset,
        "logs": [log.to_dict() for log in logs]
    }


@router.get("/audit/statistics")
async def get_audit_statistics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Retorna estatísticas de auditoria do usuário"""
    stats = await audit_logger.get_statistics(
        db,
        user_id=current_user.id,
        start_date=datetime.combine(start_date, datetime.min.time()) if start_date else None,
        end_date=datetime.combine(end_date, datetime.max.time()) if end_date else None
    )
    
    return stats


# ==================== Admin Endpoints (Proteger com permissão admin) ====================


@router.get("/admin/audit/search")
async def search_audit_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Busca avançada em audit logs (Admin apenas)
    
    **Requer**: Permissão de administrador
    """
    # TODO: Verificar se usuário é admin
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    logs, total = await audit_logger.search_logs(
        db,
        user_id=user_id,
        action=action,
        start_date=datetime.combine(start_date, datetime.min.time()) if start_date else None,
        end_date=datetime.combine(end_date, datetime.max.time()) if end_date else None,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": [log.to_dict() for log in logs]
    }


@router.get("/admin/lgpd/deletion-requests")
async def get_deletion_requests(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Lista solicitações de exclusão de dados (Admin apenas)
    
    **Requer**: Permissão de administrador
    """
    # TODO: Verificar se usuário é admin
    # TODO: Implementar query de deletion requests
    
    return {
        "message": "Endpoint em desenvolvimento",
        "requests": []
    }
