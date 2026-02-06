"""
Test User Repository
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user import User
from app.repositories.user import UserRepository
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating a user"""
    repo = UserRepository(db_session)
    
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": get_password_hash("password123"),
    }
    
    user = await repo.create(user_data)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_get_user_by_id(db_session: AsyncSession):
    """Test getting user by ID"""
    repo = UserRepository(db_session)
    
    # Create user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": get_password_hash("password123"),
    }
    created_user = await repo.create(user_data)
    await db_session.commit()
    
    # Get user
    user = await repo.get(created_user.id)
    
    assert user is not None
    assert user.id == created_user.id
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    """Test getting user by email"""
    repo = UserRepository(db_session)
    
    # Create user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": get_password_hash("password123"),
    }
    await repo.create(user_data)
    await db_session.commit()
    
    # Get by email
    user = await repo.get_by_email("test@example.com")
    
    assert user is not None
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_username(db_session: AsyncSession):
    """Test getting user by username"""
    repo = UserRepository(db_session)
    
    # Create user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": get_password_hash("password123"),
    }
    await repo.create(user_data)
    await db_session.commit()
    
    # Get by username
    user = await repo.get_by_username("testuser")
    
    assert user is not None
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session: AsyncSession):
    """Test successful user authentication"""
    repo = UserRepository(db_session)
    
    # Create user
    password = "password123"
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": get_password_hash(password),
    }
    await repo.create(user_data)
    await db_session.commit()
    
    # Authenticate
    user = await repo.authenticate("testuser", password)
    
    assert user is not None
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_session: AsyncSession):
    """Test authentication with wrong password"""
    repo = UserRepository(db_session)
    
    # Create user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": get_password_hash("password123"),
    }
    await repo.create(user_data)
    await db_session.commit()
    
    # Try to authenticate with wrong password
    user = await repo.authenticate("testuser", "wrongpassword")
    
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_nonexistent_user(db_session: AsyncSession):
    """Test authentication of non-existent user"""
    repo = UserRepository(db_session)
    
    user = await repo.authenticate("nonexistent", "password")
    
    assert user is None


@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    """Test updating user"""
    repo = UserRepository(db_session)
    
    # Create user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": get_password_hash("password123"),
    }
    user = await repo.create(user_data)
    await db_session.commit()
    
    # Update user
    updated = await repo.update(user.id, {"full_name": "Updated Name"})
    await db_session.commit()
    
    assert updated is not None
    assert updated.full_name == "Updated Name"
    assert updated.email == "test@example.com"  # Unchanged


@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession):
    """Test deleting user"""
    repo = UserRepository(db_session)
    
    # Create user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": get_password_hash("password123"),
    }
    user = await repo.create(user_data)
    await db_session.commit()
    
    # Delete user
    result = await repo.delete(user.id)
    await db_session.commit()
    
    assert result is True
    
    # Verify deletion
    deleted_user = await repo.get(user.id)
    assert deleted_user is None


@pytest.mark.asyncio
async def test_get_multi_users(db_session: AsyncSession):
    """Test getting multiple users"""
    repo = UserRepository(db_session)
    
    # Create multiple users
    for i in range(5):
        user_data = {
            "email": f"user{i}@example.com",
            "username": f"user{i}",
            "full_name": f"User {i}",
            "hashed_password": get_password_hash("password123"),
        }
        await repo.create(user_data)
    await db_session.commit()
    
    # Get all users
    users = await repo.get_multi(skip=0, limit=10)
    
    assert len(users) == 5


@pytest.mark.asyncio
async def test_count_users(db_session: AsyncSession):
    """Test counting users"""
    repo = UserRepository(db_session)
    
    # Create users
    for i in range(3):
        user_data = {
            "email": f"user{i}@example.com",
            "username": f"user{i}",
            "full_name": f"User {i}",
            "hashed_password": get_password_hash("password123"),
        }
        await repo.create(user_data)
    await db_session.commit()
    
    # Count
    count = await repo.count()
    
    assert count == 3
