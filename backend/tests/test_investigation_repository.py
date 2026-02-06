"""
Test Investigation Repository
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.investigation import Investigation, InvestigationStatus
from app.domain.user import User
from app.repositories.investigation import InvestigationRepository
from app.repositories.user import UserRepository
from app.core.security import get_password_hash


async def create_test_user(db_session: AsyncSession) -> User:
    """Helper to create a test user"""
    repo = UserRepository(db_session)
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": get_password_hash("password123"),
    }
    user = await repo.create(user_data)
    await db_session.commit()
    return user


@pytest.mark.asyncio
async def test_create_investigation(db_session: AsyncSession):
    """Test creating an investigation"""
    user = await create_test_user(db_session)
    repo = InvestigationRepository(db_session)
    
    investigation_data = {
        "user_id": user.id,
        "target_name": "João Silva",
        "target_cpf_cnpj": "123.456.789-00",
        "priority": 3,
    }
    
    investigation = await repo.create(investigation_data)
    
    assert investigation.id is not None
    assert investigation.target_name == "João Silva"
    assert investigation.status == InvestigationStatus.PENDING
    assert investigation.priority == 3


@pytest.mark.asyncio
async def test_get_investigation_by_id(db_session: AsyncSession):
    """Test getting investigation by ID"""
    user = await create_test_user(db_session)
    repo = InvestigationRepository(db_session)
    
    # Create investigation
    investigation_data = {
        "user_id": user.id,
        "target_name": "João Silva",
        "priority": 3,
    }
    created = await repo.create(investigation_data)
    await db_session.commit()
    
    # Get investigation
    investigation = await repo.get(created.id)
    
    assert investigation is not None
    assert investigation.id == created.id
    assert investigation.target_name == "João Silva"


@pytest.mark.asyncio
async def test_get_investigations_by_user(db_session: AsyncSession):
    """Test getting investigations by user"""
    user = await create_test_user(db_session)
    repo = InvestigationRepository(db_session)
    
    # Create multiple investigations
    for i in range(3):
        investigation_data = {
            "user_id": user.id,
            "target_name": f"Target {i}",
            "priority": 3,
        }
        await repo.create(investigation_data)
    await db_session.commit()
    
    # Get investigations
    investigations = await repo.get_by_user(user.id)
    
    assert len(investigations) == 3


@pytest.mark.asyncio
async def test_count_investigations_by_user(db_session: AsyncSession):
    """Test counting investigations by user"""
    user = await create_test_user(db_session)
    repo = InvestigationRepository(db_session)
    
    # Create investigations
    for i in range(5):
        investigation_data = {
            "user_id": user.id,
            "target_name": f"Target {i}",
            "priority": 3,
        }
        await repo.create(investigation_data)
    await db_session.commit()
    
    # Count
    count = await repo.count_by_user(user.id)
    
    assert count == 5


@pytest.mark.asyncio
async def test_get_pending_investigations(db_session: AsyncSession):
    """Test getting pending investigations"""
    user = await create_test_user(db_session)
    repo = InvestigationRepository(db_session)
    
    # Create investigations with different statuses
    await repo.create({
        "user_id": user.id,
        "target_name": "Pending 1",
        "priority": 5,
        "status": InvestigationStatus.PENDING,
    })
    await repo.create({
        "user_id": user.id,
        "target_name": "Pending 2",
        "priority": 3,
        "status": InvestigationStatus.PENDING,
    })
    await repo.create({
        "user_id": user.id,
        "target_name": "Completed",
        "priority": 2,
        "status": InvestigationStatus.COMPLETED,
    })
    await db_session.commit()
    
    # Get pending
    pending = await repo.get_pending()
    
    assert len(pending) == 2
    # Check priority ordering (higher priority first)
    assert pending[0].priority >= pending[1].priority


@pytest.mark.asyncio
async def test_update_investigation(db_session: AsyncSession):
    """Test updating investigation"""
    user = await create_test_user(db_session)
    repo = InvestigationRepository(db_session)
    
    # Create investigation
    investigation_data = {
        "user_id": user.id,
        "target_name": "João Silva",
        "priority": 3,
    }
    investigation = await repo.create(investigation_data)
    await db_session.commit()
    
    # Update
    updated = await repo.update(investigation.id, {
        "status": InvestigationStatus.IN_PROGRESS,
        "properties_found": 5,
    })
    await db_session.commit()
    
    assert updated is not None
    assert updated.status == InvestigationStatus.IN_PROGRESS
    assert updated.properties_found == 5


@pytest.mark.asyncio
async def test_delete_investigation(db_session: AsyncSession):
    """Test deleting investigation"""
    user = await create_test_user(db_session)
    repo = InvestigationRepository(db_session)
    
    # Create investigation
    investigation_data = {
        "user_id": user.id,
        "target_name": "João Silva",
        "priority": 3,
    }
    investigation = await repo.create(investigation_data)
    await db_session.commit()
    
    # Delete
    result = await repo.delete(investigation.id)
    await db_session.commit()
    
    assert result is True
    
    # Verify deletion
    deleted = await repo.get(investigation.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_investigation_with_relations(db_session: AsyncSession):
    """Test getting investigation with relations loaded"""
    user = await create_test_user(db_session)
    repo = InvestigationRepository(db_session)
    
    # Create investigation
    investigation_data = {
        "user_id": user.id,
        "target_name": "João Silva",
        "priority": 3,
    }
    investigation = await repo.create(investigation_data)
    await db_session.commit()
    
    # Get with relations
    loaded = await repo.get_with_relations(investigation.id)
    
    assert loaded is not None
    assert loaded.id == investigation.id
    # Relations should be loaded (not None, even if empty)
    assert loaded.properties is not None
    assert loaded.lease_contracts is not None
    assert loaded.companies is not None
