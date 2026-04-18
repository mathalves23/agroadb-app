"""
Integration Tests for Investigations Endpoints
"""

import io
import zipfile

import pytest
from httpx import AsyncClient


async def get_auth_headers(async_client: AsyncClient) -> dict:
    """Helper to get auth headers"""
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "password123",
        },
    )

    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"},
    )

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_investigation_unauthorized(async_client: AsyncClient):
    """Test creating investigation without auth"""
    response = await async_client.post(
        "/api/v1/investigations",
        json={"target_name": "Test", "priority": 3},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_investigation_success(async_client: AsyncClient):
    """Test creating investigation"""
    headers = await get_auth_headers(async_client)

    response = await async_client.post(
        "/api/v1/investigations",
        json={
            "target_name": "João Silva",
            "target_cpf_cnpj": "52998224725",
            "target_description": "Test investigation",
            "priority": 3,
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["target_name"] == "João Silva"
    assert data["target_cpf_cnpj"] == "52998224725"
    # Com workers desligados o fallback síncrono pode concluir antes da resposta HTTP.
    assert data["status"] in ("pending", "in_progress", "completed")
    assert data["priority"] == 3


@pytest.mark.asyncio
async def test_create_investigation_invalid_data(async_client: AsyncClient):
    """Test creating investigation with invalid data"""
    headers = await get_auth_headers(async_client)

    response = await async_client.post(
        "/api/v1/investigations",
        json={"priority": 3},  # Missing required target_name
        headers=headers,
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_investigations_empty(async_client: AsyncClient):
    """Test listing investigations when empty"""
    headers = await get_auth_headers(async_client)

    response = await async_client.get("/api/v1/investigations", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_investigations_with_data(async_client: AsyncClient):
    """Test listing investigations"""
    headers = await get_auth_headers(async_client)

    # Create investigations
    for i in range(3):
        await async_client.post(
            "/api/v1/investigations",
            json={"target_name": f"Target {i}", "priority": 3},
            headers=headers,
        )

    # List investigations
    response = await async_client.get("/api/v1/investigations", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_list_investigations_pagination(async_client: AsyncClient):
    """Test investigation list pagination"""
    headers = await get_auth_headers(async_client)

    # Create investigations
    for i in range(10):
        await async_client.post(
            "/api/v1/investigations",
            json={"target_name": f"Target {i}", "priority": 3},
            headers=headers,
        )

    # Get page 1
    response = await async_client.get(
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
async def test_get_investigation_success(async_client: AsyncClient):
    """Test getting investigation details"""
    headers = await get_auth_headers(async_client)

    # Create investigation
    create_response = await async_client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]

    # Get investigation
    response = await async_client.get(
        f"/api/v1/investigations/{investigation_id}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == investigation_id
    assert data["target_name"] == "João Silva"


@pytest.mark.asyncio
async def test_get_investigation_not_found(async_client: AsyncClient):
    """Test getting non-existent investigation"""
    headers = await get_auth_headers(async_client)

    response = await async_client.get("/api/v1/investigations/999", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_investigation_success(async_client: AsyncClient):
    """Test updating investigation"""
    headers = await get_auth_headers(async_client)

    # Create investigation
    create_response = await async_client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]

    # Update investigation
    response = await async_client.patch(
        f"/api/v1/investigations/{investigation_id}",
        json={"target_name": "João Silva Updated", "priority": 5},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["target_name"] == "João Silva Updated"
    assert data["priority"] == 5


@pytest.mark.asyncio
async def test_delete_investigation_success(async_client: AsyncClient):
    """Test deleting investigation"""
    headers = await get_auth_headers(async_client)

    # Create investigation
    create_response = await async_client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]

    # Delete investigation
    response = await async_client.delete(
        f"/api/v1/investigations/{investigation_id}",
        headers=headers,
    )

    assert response.status_code == 204

    # Verify deletion
    get_response = await async_client.get(
        f"/api/v1/investigations/{investigation_id}",
        headers=headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_investigation_properties(async_client: AsyncClient):
    """Test getting investigation properties"""
    headers = await get_auth_headers(async_client)

    # Create investigation
    create_response = await async_client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]

    # Get properties
    response = await async_client.get(
        f"/api/v1/investigations/{investigation_id}/properties",
        headers=headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_investigation_companies(async_client: AsyncClient):
    """Test getting investigation companies"""
    headers = await get_auth_headers(async_client)

    # Create investigation
    create_response = await async_client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]

    # Get companies
    response = await async_client.get(
        f"/api/v1/investigations/{investigation_id}/companies",
        headers=headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_investigation_lease_contracts(async_client: AsyncClient):
    """Test getting investigation lease contracts"""
    headers = await get_auth_headers(async_client)

    # Create investigation
    create_response = await async_client.post(
        "/api/v1/investigations",
        json={"target_name": "João Silva", "priority": 3},
        headers=headers,
    )
    investigation_id = create_response.json()["id"]

    # Get lease contracts
    response = await async_client.get(
        f"/api/v1/investigations/{investigation_id}/lease-contracts",
        headers=headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_investigation_ownership_isolation(async_client: AsyncClient):
    """Test that users can only access their own investigations"""
    # User 1
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "user1@example.com",
            "username": "user1",
            "full_name": "User 1",
            "password": "password123",
        },
    )
    login1 = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "user1", "password": "password123"},
    )
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Create investigation as user1
    create_response = await async_client.post(
        "/api/v1/investigations",
        json={"target_name": "Test", "priority": 3},
        headers=headers1,
    )
    investigation_id = create_response.json()["id"]

    # User 2
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "user2@example.com",
            "username": "user2",
            "full_name": "User 2",
            "password": "password123",
        },
    )
    login2 = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "user2", "password": "password123"},
    )
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Try to access user1's investigation as user2
    response = await async_client.get(
        f"/api/v1/investigations/{investigation_id}",
        headers=headers2,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_export_investigation_pdf(async_client: AsyncClient):
    """Test exporting investigation to PDF"""
    headers = await get_auth_headers(async_client)

    # Create investigation
    create_response = await async_client.post(
        "/api/v1/investigations",
        json={
            "target_name": "João Silva",
            "target_cpf_cnpj": "52998224725",
            "target_description": "Test investigation for PDF export",
            "priority": 3,
        },
        headers=headers,
    )
    investigation_id = create_response.json()["id"]

    # Export to PDF
    response = await async_client.get(
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
async def test_export_investigation_pdf_unauthorized(async_client: AsyncClient):
    """Test exporting PDF without auth"""
    response = await async_client.get("/api/v1/investigations/999/export/pdf")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_export_investigation_pdf_not_found(async_client: AsyncClient):
    """Test exporting PDF for non-existent investigation"""
    headers = await get_auth_headers(async_client)

    response = await async_client.get(
        "/api/v1/investigations/99999/export/pdf",
        headers=headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_export_investigation_trust_bundle(async_client: AsyncClient):
    """ZIP com PDF, manifest.json e README."""
    import hashlib
    import json

    headers = await get_auth_headers(async_client)

    create_response = await async_client.post(
        "/api/v1/investigations",
        json={
            "target_name": "Empresa Trust",
            "target_cpf_cnpj": "11222333000181",
            "target_description": "Pacote de evidência",
            "priority": 2,
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    investigation_id = create_response.json()["id"]

    response = await async_client.get(
        f"/api/v1/investigations/{investigation_id}/export/trust-bundle",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/zip"
    cd = response.headers.get("content-disposition", "")
    assert "attachment" in cd
    assert ".zip" in cd

    buf = io.BytesIO(response.content)
    with zipfile.ZipFile(buf, "r") as zf:
        names = set(zf.namelist())
        assert "relatorio.pdf" in names
        assert "manifest.json" in names
        assert "README_PACOTE.txt" in names
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        assert manifest.get("export", {}).get("kind") == "agroadb_investigation_trust_bundle"
        assert manifest.get("investigation_summary", {}).get("id") == investigation_id
        assert "files" in manifest and "relatorio.pdf" in manifest["files"]
        pdf_bytes = zf.read("relatorio.pdf")
        assert pdf_bytes.startswith(b"%PDF")
        assert manifest["files"]["relatorio.pdf"]["sha256"] == hashlib.sha256(pdf_bytes).hexdigest()


@pytest.mark.asyncio
async def test_export_trust_bundle_unauthorized(async_client: AsyncClient):
    r = await async_client.get("/api/v1/investigations/1/export/trust-bundle")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_shared_viewer_can_get_investigation_but_not_export_pdf(async_client: AsyncClient):
    """Utilizador com partilha VIEW lê a investigação mas não exporta PDF."""
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner_share@example.com",
            "username": "ownershare",
            "full_name": "Owner",
            "password": "password123",
        },
    )
    lo = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "ownershare", "password": "password123"},
    )
    h_owner = {"Authorization": f"Bearer {lo.json()['access_token']}"}

    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "viewer_share@example.com",
            "username": "viewershare",
            "full_name": "Viewer",
            "password": "password123",
        },
    )
    lv = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "viewershare", "password": "password123"},
    )
    h_viewer = {"Authorization": f"Bearer {lv.json()['access_token']}"}

    cr = await async_client.post(
        "/api/v1/investigations",
        json={"target_name": "Alvo Partilhado", "priority": 2},
        headers=h_owner,
    )
    inv_id = cr.json()["id"]

    shr = await async_client.post(
        f"/api/v1/collaboration/investigations/{inv_id}/share",
        headers=h_owner,
        json={"email": "viewer_share@example.com", "permission": "view"},
    )
    assert shr.status_code == 200, shr.text

    got = await async_client.get(f"/api/v1/investigations/{inv_id}", headers=h_viewer)
    assert got.status_code == 200
    assert got.json()["target_name"] == "Alvo Partilhado"

    pdf = await async_client.get(f"/api/v1/investigations/{inv_id}/export/pdf", headers=h_viewer)
    assert pdf.status_code == 403


@pytest.mark.asyncio
async def test_guest_link_create_and_public_view(async_client: AsyncClient):
    headers = await get_auth_headers(async_client)
    cr = await async_client.post(
        "/api/v1/investigations",
        json={"target_name": "Convidado Teste", "priority": 1},
        headers=headers,
    )
    inv_id = cr.json()["id"]

    gl = await async_client.post(
        f"/api/v1/investigations/{inv_id}/guest-links",
        headers=headers,
        json={"label": "Cliente", "allow_downloads": False},
    )
    assert gl.status_code == 200, gl.text
    token = gl.json()["token"]
    assert len(token) > 20

    pub = await async_client.get(
        "/api/v1/public/guest/investigation",
        params={"token": token},
    )
    assert pub.status_code == 200
    data = pub.json()
    assert data.get("guest") is True
    assert data["investigation"]["id"] == inv_id
    assert data["allow_downloads"] is False

    pdf = await async_client.get(
        "/api/v1/public/guest/investigation/export/pdf",
        params={"token": token},
    )
    assert pdf.status_code == 403

    lst = await async_client.get(f"/api/v1/investigations/{inv_id}/guest-links", headers=headers)
    assert lst.status_code == 200
    items = lst.json()["items"]
    assert len(items) >= 1
    link_id = items[0]["id"]

    rv = await async_client.delete(
        f"/api/v1/investigations/{inv_id}/guest-links/{link_id}",
        headers=headers,
    )
    assert rv.status_code == 204

    pub2 = await async_client.get("/api/v1/public/guest/investigation", params={"token": token})
    assert pub2.status_code == 404
