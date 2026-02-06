"""
Authentication Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.v1.deps import DatabaseSession, CurrentUser
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth import AuthService
from app.repositories.user import UserRepository
from app.core.audit import audit_logger, AuditAction

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: DatabaseSession,
    request: Request,
) -> UserResponse:
    """Register a new user"""
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    user = await auth_service.register(user_data)

    # Audit log
    await audit_logger.log(
        db=db,
        action=AuditAction.USER_CREATED,
        user_id=user.id,
        username=user.username,
        resource_type="auth",
        resource_id=str(user.id),
        details={"username": user_data.username, "email": user_data.email},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        method=request.method,
        endpoint=str(request.url.path),
    )

    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    db: DatabaseSession,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """Login and get access token"""
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    # Authenticate — get user for audit before generating token
    user = await user_repo.authenticate(form_data.username, form_data.password)
    if not user:
        # Log failed login attempt
        await audit_logger.log(
            db=db,
            action=AuditAction.LOGIN_FAILED,
            resource_type="auth",
            details={"username": form_data.username},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            method=request.method,
            endpoint=str(request.url.path),
            success=False,
            error_message="Incorrect username or password",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    token = await auth_service.login(form_data.username, form_data.password)

    # Audit log — successful login
    await audit_logger.log(
        db=db,
        action=AuditAction.LOGIN,
        user_id=user.id,
        username=user.username,
        resource_type="auth",
        resource_id=str(user.id),
        details={"username": form_data.username},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        method=request.method,
        endpoint=str(request.url.path),
    )

    return token


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: DatabaseSession,
) -> Token:
    """Refresh access token"""
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    return await auth_service.refresh_token(refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """Get current user"""
    return UserResponse.model_validate(current_user)
