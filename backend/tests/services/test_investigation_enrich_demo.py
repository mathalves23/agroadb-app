"""Regras de dados MOCK_DEMO no enriquecimento (sem base de dados)."""

from __future__ import annotations

import pytest

from app.services.investigation_enrich_demo import enrich_demo_seed_enabled


def test_enrich_demo_never_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.investigation_enrich_demo.settings.ENVIRONMENT", "production")
    monkeypatch.setattr(
        "app.services.investigation_enrich_demo.settings.ENABLE_INVESTIGATION_ENRICH_DEMO_SEED",
        True,
    )
    assert enrich_demo_seed_enabled() is False


def test_enrich_demo_respects_flag_off_outside_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.services.investigation_enrich_demo.settings.ENVIRONMENT", "development"
    )
    monkeypatch.setattr(
        "app.services.investigation_enrich_demo.settings.ENABLE_INVESTIGATION_ENRICH_DEMO_SEED",
        False,
    )
    assert enrich_demo_seed_enabled() is False


def test_enrich_demo_allowed_when_flag_on_and_not_prod(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.investigation_enrich_demo.settings.ENVIRONMENT", "staging")
    monkeypatch.setattr(
        "app.services.investigation_enrich_demo.settings.ENABLE_INVESTIGATION_ENRICH_DEMO_SEED",
        True,
    )
    assert enrich_demo_seed_enabled() is True


def test_prod_alias_prod(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.investigation_enrich_demo.settings.ENVIRONMENT", "prod")
    monkeypatch.setattr(
        "app.services.investigation_enrich_demo.settings.ENABLE_INVESTIGATION_ENRICH_DEMO_SEED",
        True,
    )
    assert enrich_demo_seed_enabled() is False
