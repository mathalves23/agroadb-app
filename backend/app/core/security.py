"""Security utilities for authentication and authorization."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import uuid
import warnings
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

PBKDF2_PREFIX = "$agroadb$pbkdf2-sha256$"
PBKDF2_ROUNDS = 390000
PBKDF2_SALT_BYTES = 16
BCRYPT_PREFIXES = ("$2a$", "$2b$", "$2y$")
SHA256_CRYPT_PREFIX = "$5$"


def _truncate_bcrypt_input(password: str) -> bytes:
    raw = password.encode("utf-8")
    if len(raw) > 72:
        raw = raw[:72]
    return raw


def _hash_with_pbkdf2(password: str) -> str:
    salt = secrets.token_bytes(PBKDF2_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS)
    salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
    digest_b64 = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"{PBKDF2_PREFIX}{PBKDF2_ROUNDS}${salt_b64}${digest_b64}"


def _verify_pbkdf2(password: str, hashed_password: str) -> bool:
    try:
        payload = hashed_password.removeprefix(PBKDF2_PREFIX)
        rounds_raw, salt_b64, digest_b64 = payload.split("$", 2)
        rounds = int(rounds_raw)
        salt = base64.urlsafe_b64decode(salt_b64 + "=" * (-len(salt_b64) % 4))
        expected = base64.urlsafe_b64decode(digest_b64 + "=" * (-len(digest_b64) % 4))
    except (TypeError, ValueError):
        return False

    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return hmac.compare_digest(actual, expected)


def _verify_legacy_sha256_crypt(password: str, hashed_password: str) -> bool:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            import crypt
    except ImportError:
        return False

    return hmac.compare_digest(crypt.crypt(password, hashed_password), hashed_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against current or legacy hash formats."""
    if hashed_password.startswith(PBKDF2_PREFIX):
        return _verify_pbkdf2(plain_password, hashed_password)
    if hashed_password.startswith(BCRYPT_PREFIXES):
        return bcrypt.checkpw(
            _truncate_bcrypt_input(plain_password), hashed_password.encode("utf-8")
        )
    if hashed_password.startswith(SHA256_CRYPT_PREFIX):
        return _verify_legacy_sha256_crypt(plain_password, hashed_password)
    return False


def get_password_hash(password: str) -> str:
    """Hash a password using the default application format."""
    return _hash_with_pbkdf2(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access", "jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")
