"""
Authentication Service
"""
from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, Token
from app.domain.user import User


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register(self, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        
        existing_email = await self.user_repo.get_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # Create user
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = get_password_hash(user_data.password)
        
        user = await self.user_repo.create(user_dict)
        return user
    
    async def login(self, username: str, password: str) -> Token:
        """Authenticate user and return tokens"""
        user = await self.user_repo.authenticate(username, password)
        
        if not user:
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
        
        # Create tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token"""
        try:
            payload = decode_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )
            
            user_id = int(payload.get("sub"))
            user = await self.user_repo.get(user_id)
            
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive",
                )
            
            # Create new tokens
            access_token = create_access_token({"sub": str(user.id)})
            new_refresh_token = create_refresh_token({"sub": str(user.id)})
            
            return Token(
                access_token=access_token,
                refresh_token=new_refresh_token,
            )
        
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from token"""
        try:
            payload = decode_token(token)
            
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )
            
            user_id = int(payload.get("sub"))
            user = await self.user_repo.get(user_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user",
                )
            
            return user
        
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
