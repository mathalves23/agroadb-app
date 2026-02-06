"""
Integration Tests for Investigations Endpoints
"""
import pytest
from httpx import AsyncClient


async def get_auth_headers(client: AsyncClient) -> dict:
    """Helper to get auth headers"""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "password123",
        },
    )
    
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"},
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_investigation_unauthorized(client: AsyncClient):
    """Test creating investigation without auth"""
    response = await client.post(
        "/api/v1/investigations",
        json={"target_name": "Test", "priority": 3},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_investigation_success(client: AsyncClient):
    """Test creating investigation"""
    headers = await get_auth_headers(client)
    
    response = await client.post(
        "/api/v1/investigations",
        json={
            "target_name": "João Silva",
            "target_cpf_cnpj": "123.456.789-00",
            "target_description": "Test investigation",
            "priority": 3,
        },
        headers=headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["target_name"] == "João Silva"
    assert data["target_cpf_cnpj"] == "123.456.789-00"
    assert data["status"] == "pending"
    assert data["priority"] == 3


@pytest.mark.asyncio
async def test_create_investigation_invalid_data(client: AsyncClient):
    """Test creating investigation with invalid data"""
    headers = await get_auth_headers(client)
    
    response = await client.post(
        "/api/v1/investigations",
        json={"priority": 3},  # Missing required target_name
        headers=headers,
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_investigations_empty(client: AsyncClient):
    """Test listing investigations when empty"""
    headers = await get_auth_headers(client)
    
    response = await client.get("/api/v1/investigations", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_investigations_with_data(client: AsyncClient):
    """Test listing investigations"""
    headers = await get_auth_headers(client)
    
    # Create investigations
    for i in range(3):
        await client.post(
            "/api/v1/investigations",
            json={"target_name": f"Target {i}", "priority": 3},
            headers=headers,
        )
    
    # List investigations
    response = await client.get("/api/v1/investigations", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_list_investigations_pagination(client: AsyncClient):
    """Test investigation list pagination"""
    headers = await get_auth_headers(client)
    
    # Create investigations
    for i in range(10):
        await client.post(
            "/api/v1/investigations",
            json={"target_name": f"Target {i}", "priority": 3},
            headers=headers,
        )
    
    # Get page 1
    response = await client.get(
        "/api/v1/investigations?page=1&page_size=5",
        headers=headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["total"] == 10
    assert data["page"] == 1
    assert data["total_pages"] == 2


@pytest.mark.asyncio
async def test_get_investigation_success(client: AsyncClient):
    """Test getting investigation details"""
    headers = await get_auth_headers(client)
    
    # Create investigation
    create_response = await client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]
    
    # Get investigation
    response = await client.get(
        f"/api/v1/investigations/{investigation_id}",
        headers=headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == investigation_id
    assert data["target_name"] == "João Silva"


@pytest.mark.asyncio
async def test_get_investigation_not_found(client: AsyncClient):
    """Test getting non-existent investigation"""
    headers = await get_auth_headers(client)
    
    response = await client.get("/api/v1/investigations/999", headers=headers)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_investigation_success(client: AsyncClient):
    """Test updating investigation"""
    headers = await get_auth_headers(client)
    
    # Create investigation
    create_response = await client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]
    
    # Update investigation
    response = await client.patch(
        f"/api/v1/investigations/{investigation_id}",
        json={"target_name": "João Silva Updated", "priority": 5},
        headers=headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["target_name"] == "João Silva Updated"
    assert data["priority"] == 5


@pytest.mark.asyncio
async def test_delete_investigation_success(client: AsyncClient):
    """Test deleting investigation"""
    headers = await get_auth_headers(client)
    
    # Create investigation
    create_response = await client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]
    
    # Delete investigation
    response = await client.delete(
        f"/api/v1/investigations/{investigation_id}",
        headers=headers,
    )
    
    assert response.status_code == 204
    
    # Verify deletion
    get_response = await client.get(
        f"/api/v1/investigations/{investigation_id}",
        headers=headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_investigation_properties(client: AsyncClient):
    """Test getting investigation properties"""
    headers = await get_auth_headers(client)
    
    # Create investigation
    create_response = await client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]
    
    # Get properties
    response = await client.get(
        f"/api/v1/investigations/{investigation_id}/properties",
        headers=headers,
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_investigation_companies(client: AsyncClient):
    """Test getting investigation companies"""
    headers = await get_auth_headers(client)
    
    # Create investigation
    create_response = await client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]
    
    # Get companies
    response = await client.get(
        f"/api/v1/investigations/{investigation_id}/companies",
        headers=headers,
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_investigation_lease_contracts(client: AsyncClient):
    """Test getting investigation lease contracts"""
    headers = await get_auth_headers(client)
    
    # Create investigation
    create_response = await client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]
    
    # Get lease contracts
    response = await client.get(
        f"/api/v1/investigations/{investigation_id}/lease-contracts",
        headers=headers,
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_investigation_ownership_isolation(client: AsyncClient):
    """Test that users can only access their own investigations"""
    # User 1
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user1@example.com",
            "username": "user1",
            "full_name": "User 1",
            "password": "password123",
        },
    )
    login1 = await client.post(
        "/api/v1/auth/login",
        data={"username": "user1", "password": "password123"},
    )
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    # Create investigation as user1
    create_response = await client.post(
        "/api/v1/investigations",
        json={"target_name": "Test", "priority": 3},
        headers=headers1,
    )
    investigation_id = create_response.json()["id"]
    
    # User 2
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user2@example.com",
            "username": "user2",
            "full_name": "User 2",
            "password": "password123",
        },
    )
    login2 = await client.post(
        "/api/v1/auth/login",
        data={"username": "user2", "password": "password123"},
    )
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Try to access user1's investigation as user2
    response = await client.get(
        f"/api/v1/investigations/{investigation_id}",
        headers=headers2,
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_export_investigation_pdf(client: AsyncClient):
    """Test exporting investigation to PDF"""
    headers = await get_auth_headers(client)
    
    # Create investigation
    create_response = await client.post(
        "/api/v1/investigations",
        json={
            "target_name": "João Silva",
            "target_cpf_cnpj": "123.456.789-00",
            "target_description": "Test investigation for PDF export",
            "priority": 3,
        },
        headers=headers,
    )
    investigation_id = create_response.json()["id"]
    
    # Export to PDF
    response = await client.get(
        f"/api/v1/investigations/{investigation_id}/export/pdf",
        headers=headers,
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert ".pdf" in response.headers["content-disposition"]
    
    # Verify PDF content is not empty
    content = response.content
    assert len(content) > 1000  # PDF should have reasonable size
    assert content.startswith(b"%PDF")  # PDF magic number


@pytest.mark.asyncio
async def test_export_investigation_pdf_unauthorized(client: AsyncClient):
    """Test exporting PDF without auth"""
    response = await client.get("/api/v1/investigations/999/export/pdf")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_export_investigation_pdf_not_found(client: AsyncClient):
    """Test exporting PDF for non-existent investigation"""
    headers = await get_auth_headers(client)
    
    response = await client.get(
        "/api/v1/investigations/99999/export/pdf",
        headers=headers,
    )
    
    assert response.status_code == 404

