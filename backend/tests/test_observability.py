"""Rotas e cabeçalhos relacionados com observabilidade e segurança HTTP."""

from __future__ import annotations

import os

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


@pytest.mark.skipif(
    os.environ.get("AGROADB_CI_QUEUE_METRICS", "") != "1",
    reason="Defina AGROADB_CI_QUEUE_METRICS=1 quando Redis estiver disponível (smoke CI).",
)
def test_metrics_includes_agroadb_queue_tasks_when_ci_redis_smoke_enabled(client: TestClient) -> None:
    """Gauges de fila Redis expostos após lifespan + refresh (ver queue_prometheus)."""
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "agroadb_queue_tasks" in r.text


def test_health_includes_security_headers(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
