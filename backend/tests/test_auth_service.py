"""
Test Auth Service
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.auth import AuthService
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_register_user_success(db_session: AsyncSession):
    """Test successful user registration"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password="password123",
    )
    
    user = await service.register(user_data)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_register_duplicate_username(db_session: AsyncSession):
    """Test registering user with duplicate username"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    user_data = UserCreate(
        email="test1@example.com",
        username="testuser",
        full_name="Test User",
        password="password123",
    )
    
    # First registration
    await service.register(user_data)
    
    # Second registration with same username
    user_data2 = UserCreate(
        email="test2@example.com",
        username="testuser",  # Same username
        full_name="Test User 2",
        password="password123",
    )
    
    with pytest.raises(HTTPException) as exc:
        await service.register(user_data2)
    
    assert exc.value.status_code == 400
    assert "already registered" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_register_duplicate_email(db_session: AsyncSession):
    """Test registering user with duplicate email"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    user_data = UserCreate(
        email="test@example.com",
        username="testuser1",
        full_name="Test User",
        password="password123",
    )
    
    # First registration
    await service.register(user_data)
    
    # Second registration with same email
    user_data2 = UserCreate(
        email="test@example.com",  # Same email
        username="testuser2",
        full_name="Test User 2",
        password="password123",
    )
    
    with pytest.raises(HTTPException) as exc:
        await service.register(user_data2)
    
    assert exc.value.status_code == 400
    assert "already registered" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_login_success(db_session: AsyncSession):
    """Test successful login"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    # Register user
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password="password123",
    )
    await service.register(user_data)
    
    # Login
    token = await service.login("testuser", "password123")
    
    assert token.access_token is not None
    assert token.refresh_token is not None
    assert token.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(db_session: AsyncSession):
    """Test login with wrong password"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    # Register user
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password="password123",
    )
    await service.register(user_data)
    
    # Try login with wrong password
    with pytest.raises(HTTPException) as exc:
        await service.login("testuser", "wrongpassword")
    
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(db_session: AsyncSession):
    """Test login with non-existent user"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    with pytest.raises(HTTPException) as exc:
        await service.login("nonexistent", "password")
    
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(db_session: AsyncSession):
    """Test login with inactive user"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    # Create inactive user directly
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": get_password_hash("password123"),
        "is_active": False,
    }
    await repo.create(user_data)
    await db_session.commit()
    
    # Try login
    with pytest.raises(HTTPException) as exc:
        await service.login("testuser", "password123")
    
    assert exc.value.status_code == 400
    assert "inactive" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_get_current_user(db_session: AsyncSession):
    """Test getting current user from token"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    # Register and login
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password="password123",
    )
    user = await service.register(user_data)
    token = await service.login("testuser", "password123")
    
    # Get current user
    current_user = await service.get_current_user(token.access_token)
    
    assert current_user.id == user.id
    assert current_user.username == user.username


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session: AsyncSession):
    """Test getting current user with invalid token"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    with pytest.raises(HTTPException) as exc:
        await service.get_current_user("invalid.token.here")
    
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(db_session: AsyncSession):
    """Test refreshing access token"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    # Register and login
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password="password123",
    )
    await service.register(user_data)
    token = await service.login("testuser", "password123")
    
    # Refresh token
    new_token = await service.refresh_token(token.refresh_token)
    
    assert new_token.access_token is not None
    assert new_token.refresh_token is not None
    assert new_token.access_token != token.access_token


@pytest.mark.asyncio
async def test_refresh_token_invalid(db_session: AsyncSession):
    """Test refreshing with invalid token"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    with pytest.raises(HTTPException) as exc:
        await service.refresh_token("invalid_token_here")
    
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_with_access_token(db_session: AsyncSession):
    """Test using access token for refresh (should fail)"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password="password123",
    )
    await service.register(user_data)
    token = await service.login("testuser", "password123")
    
    # Try to refresh with access token (wrong type)
    with pytest.raises(HTTPException) as exc:
        await service.refresh_token(token.access_token)
    
    assert exc.value.status_code == 401
    assert "Invalid token type" in exc.value.detail


@pytest.mark.asyncio
async def test_get_current_user_with_refresh_token(db_session: AsyncSession):
    """Test getting user with refresh token (should fail)"""
    repo = UserRepository(db_session)
    service = AuthService(repo)
    
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password="password123",
    )
    await service.register(user_data)
    token = await service.login("testuser", "password123")
    
    # Try to get user with refresh token (wrong type)
    with pytest.raises(HTTPException) as exc:
        await service.get_current_user(token.refresh_token)
    
    assert exc.value.status_code == 401
    assert "Invalid token type" in exc.value.detail
