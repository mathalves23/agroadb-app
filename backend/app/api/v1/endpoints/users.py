"""
Users Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.api.v1.deps import DatabaseSession, CurrentUser, CurrentSuperuser, get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.repositories.user import UserRepository
from app.repositories.user_settings import UserSettingsRepository
from app.core.security import get_password_hash, verify_password
from app.core.database import get_db

router = APIRouter()


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class NotificationSettingsRequest(BaseModel):
    email_investigations: bool = True
    email_reports: bool = True
    email_updates: bool = False
    email_marketing: bool = False


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: CurrentUser) -> UserResponse:
    """Get current user profile"""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> UserResponse:
    """Update current user profile"""
    user_repo = UserRepository(db)
    
    update_dict = user_data.model_dump(exclude_unset=True)
    
    # Don't allow password update through this endpoint
    if "password" in update_dict:
        update_dict.pop("password")
    
    updated_user = await user_repo.update(current_user.id, update_dict)
    return UserResponse.model_validate(updated_user)


@router.post("/me/password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """Change current user password"""
    user_repo = UserRepository(db)
    
    # Verify current password
    user = await user_repo.get(current_user.id)
    if not user or not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Update password
    new_hash = get_password_hash(data.new_password)
    await user_repo.update(current_user.id, {"hashed_password": new_hash})
    
    return {"message": "Senha alterada com sucesso"}


@router.get("/me/notifications")
async def get_notification_settings(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get user notification preferences"""
    settings_repo = UserSettingsRepository(db)
    
    # Get all notification settings
    email_investigations = await settings_repo.get_config(current_user.id, "email_investigations") == "true"
    email_reports = await settings_repo.get_config(current_user.id, "email_reports") == "true"
    email_updates = await settings_repo.get_config(current_user.id, "email_updates") == "true"
    email_marketing = await settings_repo.get_config(current_user.id, "email_marketing") == "true"
    
    return {
        "email_investigations": email_investigations,
        "email_reports": email_reports,
        "email_updates": email_updates,
        "email_marketing": email_marketing
    }


@router.put("/me/notifications")
async def update_notification_settings(
    settings: NotificationSettingsRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update user notification preferences"""
    settings_repo = UserSettingsRepository(db)
    
    # Save each setting
    await settings_repo.save_integration_configs(current_user.id, {
        "email_investigations": "true" if settings.email_investigations else "false",
        "email_reports": "true" if settings.email_reports else "false",
        "email_updates": "true" if settings.email_updates else "false",
        "email_marketing": "true" if settings.email_marketing else "false"
    })
    
    return {"message": "Preferências de notificação atualizadas"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: CurrentSuperuser,
    db: DatabaseSession,
) -> UserResponse:
    """Get user by ID (superuser only)"""
    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.model_validate(user)
