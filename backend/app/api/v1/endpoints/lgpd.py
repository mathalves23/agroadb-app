"""
LGPD Compliance Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select

from app.api.v1.deps import DatabaseSession, CurrentUser
from app.core.lgpd import (
    LGPDService,
    UserConsent,
    DataDeletionRequest,
    PersonalDataAccess,
    ConsentType,
)

router = APIRouter()

lgpd_service = LGPDService()


class ConsentRequest(BaseModel):
    consent_type: str
    version: str = "1.0"


class DataDeletionRequestModel(BaseModel):
    reason: Optional[str] = None


class ConsentResponse(BaseModel):
    id: int
    consent_type: str
    version: str
    is_active: bool
    consented_at: Optional[str] = None
    revoked_at: Optional[str] = None


@router.get("/consents")
async def list_consents(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """List all consents for the current user"""
    result = await db.execute(
        select(UserConsent)
        .where(UserConsent.user_id == current_user.id)
        .order_by(UserConsent.consented_at.desc())
    )
    consents = result.scalars().all()
    return [c.to_dict() for c in consents]


@router.post("/consents")
async def record_consent(
    consent_data: ConsentRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
    request: Request,
):
    """Record user consent (LGPD Art. 8)"""
    result = await lgpd_service.record_consent(
        db=db,
        user_id=current_user.id,
        consent_type=consent_data.consent_type,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return result


@router.delete("/consents/{consent_type}")
async def revoke_consent(
    consent_type: str,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """Revoke consent (LGPD Art. 8, § 5)"""
    result = await lgpd_service.revoke_consent(
        db=db,
        user_id=current_user.id,
        consent_type=consent_type,
    )
    return result


@router.get("/data-report")
async def get_personal_data_report(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """Export all personal data (LGPD Art. 18, II - Portabilidade)"""
    report = await lgpd_service.generate_personal_data_report(
        db=db,
        user_id=current_user.id,
    )
    return report


@router.post("/data-deletion")
async def request_data_deletion(
    deletion_data: DataDeletionRequestModel,
    current_user: CurrentUser,
    db: DatabaseSession,
    request: Request,
):
    """Request data deletion (LGPD Art. 18, VI)"""
    result = await lgpd_service.request_data_deletion(
        db=db,
        user_id=current_user.id,
        reason=deletion_data.reason,
    )
    return result


@router.get("/data-access-log")
async def get_data_access_log(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """View log of who accessed your personal data"""
    result = await db.execute(
        select(PersonalDataAccess)
        .where(PersonalDataAccess.user_id == current_user.id)
        .order_by(PersonalDataAccess.accessed_at.desc())
        .limit(50)
    )
    accesses = result.scalars().all()
    return [a.to_dict() for a in accesses]


@router.get("/privacy-policy")
async def get_privacy_policy():
    """Return current privacy policy"""
    return {
        "version": "1.0",
        "effective_date": "2026-02-01",
        "title": "Política de Privacidade — AgroADB",
        "sections": [
            {
                "title": "1. Dados Coletados",
                "content": "Coletamos dados pessoais necessários para a prestação do serviço de inteligência patrimonial: nome completo, CPF/CNPJ, e-mail, organização e número da OAB (quando aplicável)."
            },
            {
                "title": "2. Finalidade do Tratamento",
                "content": "Os dados são tratados exclusivamente para (a) autenticação e controle de acesso; (b) realização de consultas em bases públicas governamentais; (c) geração de relatórios de investigação patrimonial."
            },
            {
                "title": "3. Base Legal",
                "content": "O tratamento é fundamentado no consentimento do titular (Art. 7, I da LGPD) e na execução de contrato (Art. 7, V da LGPD)."
            },
            {
                "title": "4. Compartilhamento",
                "content": "Os dados não são compartilhados com terceiros. As consultas às bases governamentais são realizadas diretamente via APIs oficiais."
            },
            {
                "title": "5. Retenção",
                "content": "Dados de investigação são retidos por 5 anos. Logs de auditoria por 2 anos. Dados de usuários inativos são anonimizados após 1 ano."
            },
            {
                "title": "6. Direitos do Titular (Art. 18)",
                "content": "Você pode: solicitar acesso a seus dados (/data-report), revogar consentimento (/consents), solicitar exclusão (/data-deletion), e verificar acessos a seus dados (/data-access-log)."
            },
            {
                "title": "7. Segurança",
                "content": "Dados sensíveis são criptografados em repouso (AES-256). A comunicação é protegida por TLS 1.2+. Autenticação de dois fatores (2FA) está disponível."
            },
            {
                "title": "8. Encarregado de Dados (DPO)",
                "content": "Para exercer seus direitos ou esclarecer dúvidas, contate o encarregado de dados pelo e-mail dpo@agroadb.com.br."
            },
        ],
    }
