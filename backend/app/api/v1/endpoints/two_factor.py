"""
Two-Factor Authentication Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy import select

from app.api.v1.deps import DatabaseSession, CurrentUser
from app.core.two_factor import TwoFactorService, TwoFactorAuth

router = APIRouter()

two_factor_service = TwoFactorService()


class Enable2FARequest(BaseModel):
    """Request to enable 2FA — returns QR code and backup codes"""
    pass


class Verify2FARequest(BaseModel):
    token: str


class Disable2FARequest(BaseModel):
    token: str  # Current TOTP token to confirm identity


class TwoFactorStatusResponse(BaseModel):
    is_enabled: bool
    has_backup_codes: bool


@router.get("/status", response_model=TwoFactorStatusResponse)
async def get_2fa_status(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """Check if 2FA is enabled for current user"""
    result = await db.execute(
        select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id)
    )
    tfa = result.scalar_one_or_none()
    
    if not tfa:
        return TwoFactorStatusResponse(is_enabled=False, has_backup_codes=False)
    
    return TwoFactorStatusResponse(
        is_enabled=tfa.is_enabled,
        has_backup_codes=bool(tfa.backup_codes),
    )


@router.post("/enable")
async def enable_2fa(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """Enable 2FA — returns QR code and backup codes"""
    result = await db.execute(
        select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id)
    )
    existing = result.scalar_one_or_none()
    
    if existing and existing.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA já está habilitado",
        )
    
    # Generate secret
    secret = two_factor_service.generate_secret()
    backup_codes = two_factor_service.generate_backup_codes()
    
    # Generate QR code
    qr_code = two_factor_service.generate_qr_code(
        secret=secret,
        user_email=current_user.email,
    )
    
    if existing:
        existing.secret = secret
        existing.backup_codes = ",".join(backup_codes)
        existing.is_enabled = False  # Will be enabled after verification
    else:
        tfa = TwoFactorAuth(
            user_id=current_user.id,
            secret=secret,
            is_enabled=False,
            backup_codes=",".join(backup_codes),
        )
        db.add(tfa)
    
    await db.commit()
    
    return {
        "qr_code": qr_code,
        "secret": secret,
        "backup_codes": backup_codes,
        "message": "Escaneie o QR code com Google Authenticator ou Authy. Depois confirme com /verify.",
    }


@router.post("/verify")
async def verify_and_activate_2fa(
    request: Verify2FARequest,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """Verify TOTP token and activate 2FA"""
    result = await db.execute(
        select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id)
    )
    tfa = result.scalar_one_or_none()
    
    if not tfa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA não foi configurado. Use /enable primeiro.",
        )
    
    if not two_factor_service.verify_token(tfa.secret, request.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido. Tente novamente.",
        )
    
    tfa.is_enabled = True
    await db.commit()
    
    return {"message": "2FA habilitado com sucesso!", "is_enabled": True}


@router.post("/disable")
async def disable_2fa(
    request: Disable2FARequest,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """Disable 2FA (requires valid TOTP token)"""
    result = await db.execute(
        select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id)
    )
    tfa = result.scalar_one_or_none()
    
    if not tfa or not tfa.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA não está habilitado.",
        )
    
    if not two_factor_service.verify_token(tfa.secret, request.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido.",
        )
    
    tfa.is_enabled = False
    tfa.secret = two_factor_service.generate_secret()  # Invalidate old secret
    tfa.backup_codes = None
    await db.commit()
    
    return {"message": "2FA desabilitado.", "is_enabled": False}
