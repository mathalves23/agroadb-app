"""
Integration Tests for Users Endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(async_client: AsyncClient):
    """Test getting current user without auth"""
    response = await async_client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_success(async_client: AsyncClient):
    """Test getting current user"""
    # Register
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "password123",
        },
    )
    
    # Login
    login_response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_update_current_user(async_client: AsyncClient):
    """Test updating current user"""
    # Register and login
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "password123",
        },
    )
    
    login_response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    
    # Update user
    response = await async_client.patch(
        "/api/v1/users/me",
        json={"full_name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_current_user_password(async_client: AsyncClient):
    """Test updating current user password"""
    # Register and login
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "oldpassword",
        },
    )
    
    login_response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "oldpassword"},
    )
    token = login_response.json()["access_token"]
    
    # Update password
    response = await async_client.patch(
        "/api/v1/users/me",
        json={"password": "newpassword123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    
    # Try login with new password
    new_login = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "newpassword123"},
    )
    assert new_login.status_code == 200
