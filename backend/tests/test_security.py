"""
Test Security Utilities
"""
import pytest
from datetime import timedelta

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestJWTTokens:
    """Test JWT token functions"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiry(self):
        """Test access token with custom expiry"""
        data = {"sub": "123"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        
        # Decode and verify expiry
        payload = decode_token(token)
        assert payload["type"] == "access"
        assert "exp" in payload
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "123"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify type
        payload = decode_token(token)
        assert payload["type"] == "refresh"
    
    def test_decode_token_valid(self):
        """Test decoding valid token"""
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
    
    def test_decode_token_invalid(self):
        """Test decoding invalid token"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(ValueError):
            decode_token(invalid_token)
    
    def test_token_contains_expiration(self):
        """Test that token contains expiration"""
        data = {"sub": "123"}
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
