"""
Testes de contrato na API pública: rotas estáveis, códigos HTTP e forma mínima do payload.

Expandir CONTRACT_PATHS à medida que novos contratos forem acordados com clientes.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


# (method, path, auth_required)
CONTRACT_PATHS: list[tuple[str, str, bool]] = [
    ("GET", "/health", False),
    ("GET", "/api/v1/ml/health", False),
    ("GET", "/api/v1/platform/proposition", False),
    ("GET", "/api/v1/platform/compliance-summary", False),
    ("GET", "/api/openapi.json", False),
]


@pytest.mark.parametrize("method,path,auth_required", CONTRACT_PATHS)
def test_public_routes_respond(client: TestClient, method: str, path: str, auth_required: bool) -> None:
    r = client.request(method, path)
    if auth_required:
        assert r.status_code in (401, 403)
    else:
        assert r.status_code == 200, f"{method} {path} -> {r.status_code} {r.text[:200]}"


def test_openapi_lists_platform_paths(client: TestClient) -> None:
    schema = client.get("/api/openapi.json").json()
    paths = schema.get("paths") or {}
    assert "/api/v1/platform/proposition" in paths
    assert "/api/v1/platform/compliance-summary" in paths


def test_platform_proposition_shape(client: TestClient) -> None:
    data = client.get("/api/v1/platform/proposition").json()
    assert data.get("product") == "AgroADB"
    assert "primary_segments" in data
    assert "differentiators" in data
    segs = data["primary_segments"]
    assert isinstance(segs, list) and len(segs) >= 1
    labels = " ".join(s.get("label", "") for s in segs).lower()
    assert "agronegócio" in labels or "crédito" in labels


def test_platform_compliance_shape(client: TestClient) -> None:
    data = client.get("/api/v1/platform/compliance-summary").json()
    assert "pillars" in data
    ids = {p.get("id") for p in data["pillars"]}
    assert "lgpd" in ids
    assert "audit" in ids
