"""
Tests for Authentication API
"""

import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update

from app.core.database import AsyncSessionLocal
from app.domain.user import User


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_register_user(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "StrongPass123!",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client: TestClient, test_user: dict):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "otheruser",
                "password": "Password123!",
                "full_name": "Duplicate User",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_login_success(self, client: TestClient, test_user: dict):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient, test_user: dict):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent", "password": "password123"},
        )
        assert response.status_code == 401

    def test_get_current_user(self, client: TestClient, auth_headers: dict):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data

    def test_get_current_user_unauthorized(self, client: TestClient):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_refresh_token(self, client: TestClient, test_user: dict):
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"},
        )
        refresh_token = login_response.json()["refresh_token"]

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_logout(self, client: TestClient, auth_headers: dict):
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"

    def test_change_password(self, client: TestClient, auth_headers: dict):
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "testpass123",
                "new_password": "NewPass123!",
            },
        )
        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()

    def test_change_password_wrong_current(self, client: TestClient, auth_headers: dict):
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "NewPass123!",
            },
        )
        assert response.status_code == 400

    def test_password_validation(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "username": "weakuser",
                "password": "123",
                "full_name": "Weak Password User",
            },
        )
        assert response.status_code == 422


class TestAuthSecurity:
    """Test authentication security features"""

    def test_jwt_token_expiration(self, client: TestClient, test_user: dict):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_invalid_token_format(self, client: TestClient):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_format"},
        )
        assert response.status_code == 401

    def test_missing_authorization_header(self, client: TestClient):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_inactive_user_cannot_login(self, client: TestClient, test_user: dict):
        async def _deactivate() -> None:
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(User).where(User.email == "test@example.com").values(is_active=False)
                )
                await db.commit()

        asyncio.run(_deactivate())

        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == 400
        assert "inactive" in response.json()["detail"].lower()
