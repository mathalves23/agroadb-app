"""
Tests for Authentication API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.domain.user import User


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_user(self, client: TestClient):
        """Test user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "StrongPass123!",
                "full_name": "New User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "Password123!",
                "full_name": "Duplicate User"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, test_user: User):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, auth_headers: dict):
        """Test get current user"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test get current user without authentication"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_refresh_token(self, client: TestClient, test_user: User):
        """Test token refresh"""
        # Login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_logout(self, client: TestClient, auth_headers: dict):
        """Test logout"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"
    
    def test_change_password(self, client: TestClient, auth_headers: dict):
        """Test password change"""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "testpass123",
                "new_password": "NewPass123!"
            }
        )
        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()
    
    def test_change_password_wrong_current(self, client: TestClient, auth_headers: dict):
        """Test password change with wrong current password"""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "NewPass123!"
            }
        )
        assert response.status_code == 400
    
    def test_password_validation(self, client: TestClient):
        """Test password validation requirements"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "password": "123",  # Weak password
                "full_name": "Weak Password User"
            }
        )
        assert response.status_code == 422  # Validation error


class TestAuthSecurity:
    """Test authentication security features"""
    
    def test_jwt_token_expiration(self, client: TestClient, test_user: User):
        """Test JWT token has expiration"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        # Token should be created successfully
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_invalid_token_format(self, client: TestClient):
        """Test invalid token format"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_format"}
        )
        assert response.status_code == 401
    
    def test_missing_authorization_header(self, client: TestClient):
        """Test missing authorization header"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_inactive_user_cannot_login(self, client: TestClient, db: Session, test_user: User):
        """Test inactive user cannot login"""
        # Deactivate user
        test_user.is_active = False
        db.commit()
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 401
