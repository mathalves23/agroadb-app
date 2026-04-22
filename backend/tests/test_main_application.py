from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

from app import main


def test_build_cors_origins_uses_local_hosts_outside_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(main.settings, "ENVIRONMENT", "development")
    monkeypatch.setattr(main.settings, "CORS_ORIGINS", ["https://app.example.com"])

    origins = main._build_cors_origins()

    assert origins == [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]


def test_build_cors_origins_respects_production_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(main.settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(main.settings, "CORS_ORIGINS", ["https://app.example.com"])

    origins = main._build_cors_origins()

    assert origins == ["https://app.example.com"]


def test_create_application_exposes_health_without_external_integrations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    startup_application = AsyncMock(return_value=Mock())
    shutdown_application = AsyncMock()
    mount_prometheus = Mock()
    instrument_fastapi = Mock()

    monkeypatch.setattr(main, "startup_application", startup_application)
    monkeypatch.setattr(main, "shutdown_application", shutdown_application)
    monkeypatch.setattr(main, "mount_prometheus_instrumentator", mount_prometheus)
    monkeypatch.setattr(main, "instrument_fastapi", instrument_fastapi)
    monkeypatch.setattr(main.settings, "ENVIRONMENT", "test")
    monkeypatch.setattr(main.settings, "VERSION", "9.9.9-test")

    app = main.create_application()

    mount_prometheus.assert_called_once_with(app)
    instrument_fastapi.assert_called_once_with(app)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "version": "9.9.9-test",
        "environment": "test",
    }
    startup_application.assert_awaited_once()
    shutdown_application.assert_awaited_once()


def test_create_application_uses_configured_cors_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    startup_application = AsyncMock(return_value=Mock())
    shutdown_application = AsyncMock()

    monkeypatch.setattr(main, "startup_application", startup_application)
    monkeypatch.setattr(main, "shutdown_application", shutdown_application)
    monkeypatch.setattr(main, "mount_prometheus_instrumentator", Mock())
    monkeypatch.setattr(main, "instrument_fastapi", Mock())
    monkeypatch.setattr(main.settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(main.settings, "CORS_ORIGINS", ["https://console.agroadb.com"])
    monkeypatch.setattr(main.settings, "CORS_ALLOW_CREDENTIALS", True)

    app = main.create_application()

    with TestClient(app) as client:
        response = client.options(
            "/health",
            headers={
                "Origin": "https://console.agroadb.com",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://console.agroadb.com"
    assert response.headers["access-control-allow-credentials"] == "true"
