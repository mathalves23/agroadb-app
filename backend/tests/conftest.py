"""
Configuração pytest — BD async alinhada à app + sessão síncrona para ML legado.
"""
from __future__ import annotations

import base64
import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "pytest-secret-key-at-least-32-characters!")
# Chave Fernet válida (32 bytes em base64 url-safe)
os.environ.setdefault(
    "ENCRYPTION_KEY",
    base64.urlsafe_b64encode(b"0" * 32).decode("ascii"),
)
os.environ.setdefault("REDIS_URL", os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"))
os.environ.setdefault("ENABLE_WORKERS", "false")
os.environ.setdefault("ENVIRONMENT", "test")

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import Session, sessionmaker

from app.main import app
from app.core.database import Base, engine, AsyncSessionLocal
from app.domain.user import User
from app.core.security import get_password_hash


@pytest_asyncio.fixture(autouse=True)
async def _reset_async_database() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app, lifespan="on")
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(client: TestClient) -> dict:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "testpass123",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture
def superuser(client: TestClient) -> None:
    async def _create() -> None:
        async with AsyncSessionLocal() as db:
            u = User(
                email="admin@example.com",
                username="admin",
                full_name="Admin User",
                hashed_password=get_password_hash("adminpass123"),
                is_active=True,
                is_superuser=True,
            )
            db.add(u)
            await db.commit()

    asyncio.run(_create())


@pytest.fixture
def auth_headers(client: TestClient, test_user: dict) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpass123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_headers(client: TestClient, superuser: None) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "adminpass123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def db() -> Generator[Session, None, None]:
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=pool.StaticPool,
    )
    Base.metadata.create_all(bind=eng)
    SessionLocal = sessionmaker(bind=eng, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=eng)
        eng.dispose()


@pytest.fixture
def mock_investigation_data():
    return {
        "name": "Test Investigation",
        "type": "property",
        "description": "Test description",
        "target_document": "12.345.678/0001-90",
    }


@pytest.fixture
def mock_property_data():
    return {
        "matricula": "12345",
        "area": 500.0,
        "estado": "SP",
        "municipio": "Ribeirão Preto",
        "valor_estimado": 5000000.00,
    }


@pytest.fixture
def mock_company_data():
    return {
        "cnpj": "12.345.678/0001-90",
        "razao_social": "Empresa Test Ltda",
        "capital_social": 1000000.00,
    }
