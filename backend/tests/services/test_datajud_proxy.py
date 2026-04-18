"""Testes unitários do caso de uso proxy DataJud (sem HTTP externo nem DB real)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.datajud import datajud_result_count
from app.services.datajud_proxy import run_datajud_proxy


def test_datajud_result_count_hits() -> None:
    assert datajud_result_count({"hits": [{"a": 1}, {"a": 2}]}) == 2


def test_datajud_result_count_processos() -> None:
    assert datajud_result_count({"processos": [{}]}) == 1


def test_datajud_result_count_empty_or_non_dict() -> None:
    assert datajud_result_count({}) == 0
    assert datajud_result_count({"hits": "bad"}) == 0
    assert datajud_result_count("not-a-dict") == 0


async def test_run_datajud_proxy_persists_when_investigation_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: list[dict] = []

    class FakeRepo:
        def __init__(self, _db: object) -> None:
            pass

        async def create(self, row: dict) -> None:
            created.append(row)

    monkeypatch.setattr("app.services.datajud_proxy.LegalQueryRepository", FakeRepo)

    class FakeClient:
        async def request(
            self,
            method: str,
            path: str,
            params=None,
            payload=None,
        ):
            return {"hits": [{"id": 1}, {"id": 2}, {"id": 3}]}

    audit = MagicMock()
    audit.log_action = AsyncMock()

    class FakeDB:
        pass

    out = await run_datajud_proxy(
        FakeDB(),  # type: ignore[arg-type]
        audit,
        user_id=7,
        ip_address="127.0.0.1",
        method="POST",
        path="/tribunais/TRT2/_search",
        investigation_id=42,
        query_type="processos",
        datajud_client=FakeClient(),
    )

    assert out["hits"] and len(out["hits"]) == 3
    assert len(created) == 1
    assert created[0]["investigation_id"] == 42
    assert created[0]["provider"] == "datajud"
    assert created[0]["query_type"] == "processos"
    assert created[0]["result_count"] == 3
    assert isinstance(created[0]["response"], dict)

    audit.log_action.assert_awaited_once()
    call_kw = audit.log_action.await_args.kwargs
    assert call_kw["user_id"] == 7
    assert call_kw["action"] == "consulta_datajud"
    assert call_kw["resource_id"] == "/tribunais/TRT2/_search"


async def test_run_datajud_proxy_skips_repo_without_investigation_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[str] = []

    class FakeRepo:
        def __init__(self, _db: object) -> None:
            pass

        async def create(self, row: dict) -> None:
            called.append("create")

    monkeypatch.setattr("app.services.datajud_proxy.LegalQueryRepository", FakeRepo)

    class FakeClient:
        async def request(self, method: str, path: str, params=None, payload=None):
            return {"ok": True}

    audit = MagicMock()
    audit.log_action = AsyncMock()

    await run_datajud_proxy(
        object(),  # type: ignore[arg-type]
        audit,
        user_id=1,
        ip_address=None,
        method="GET",
        path="/x",
        investigation_id=None,
        datajud_client=FakeClient(),
    )
    assert called == []
    audit.log_action.assert_awaited_once()
