"""Rotas e cabeçalhos relacionados com observabilidade e segurança HTTP."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def test_metrics_endpoint_exposes_prometheus_text(client: TestClient) -> None:
    r = client.get("/metrics")
    assert r.status_code == 200
    ct = (r.headers.get("content-type") or "").lower()
    assert "text/plain" in ct or "openmetrics" in ct
    body = r.text
    assert len(body) > 10
    assert "#" in body or "http" in body.lower()


def test_health_includes_security_headers(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
