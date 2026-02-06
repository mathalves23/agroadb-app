"""
Test Investigation Endpoints
"""
import pytest
from httpx import AsyncClient


async def get_auth_token(client: AsyncClient) -> str:
    """Helper function to get auth token"""
    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "testpassword123",
        },
    )
    
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword123"},
    )
    
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_investigation(client: AsyncClient):
    """Test creating an investigation"""
    token = await get_auth_token(client)
    
    response = await client.post(
        "/api/v1/investigations",
        json={
            "target_name": "João Silva",
            "target_cpf_cnpj": "123.456.789-00",
            "target_description": "Investigação de propriedades rurais",
            "priority": 3,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["target_name"] == "João Silva"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_investigations(client: AsyncClient):
    """Test listing investigations"""
    token = await get_auth_token(client)
    
    # Create an investigation
    await client.post(
        "/api/v1/investigations",
        json={
            "target_name": "João Silva",
            "priority": 3,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    # List investigations
    response = await client.get(
        "/api/v1/investigations",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_investigation(client: AsyncClient):
    """Test getting a specific investigation"""
    token = await get_auth_token(client)
    
    # Create an investigation
    create_response = await client.post(
        "/api/v1/investigations",
        json={
            "target_name": "João Silva",
            "priority": 3,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    investigation_id = create_response.json()["id"]
    
    # Get investigation
    response = await client.get(
        f"/api/v1/investigations/{investigation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == investigation_id
    assert data["target_name"] == "João Silva"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test unauthorized access to investigations"""
    response = await client.get("/api/v1/investigations")
    assert response.status_code == 401
