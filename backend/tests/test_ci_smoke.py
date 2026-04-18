"""
Testes mínimos para CI: garantem que a aplicação sobe e expõe rotas públicas.

Não substituem a suíte completa de integração (muitos testes legacy exigem
revisão de fixtures async/sync). Para cobertura local: pytest --cov=app tests/
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body.get("status") == "healthy"


def test_root_ok(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "AgroADB" in (data.get("message") or "")


def test_platform_proposition_public(client: TestClient) -> None:
    r = client.get("/api/v1/platform/proposition")
    assert r.status_code == 200
    body = r.json()
    assert body.get("product")
    assert any("LGPD" in str(x) for x in body.get("differentiators", []))
