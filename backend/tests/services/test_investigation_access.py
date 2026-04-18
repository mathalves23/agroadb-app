"""Testes unitários para regras de acesso a investigações (sem base de dados)."""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.investigation_access import (
    classify_investigation_access,
    legal_queries_to_public_list,
    require_investigation_for_user,
)


def test_classify_missing() -> None:
    assert classify_investigation_access(None, user_id=1, is_superuser=False) == "missing"


def test_classify_ok_owner() -> None:
    inv = SimpleNamespace(user_id=42)
    assert classify_investigation_access(inv, user_id=42, is_superuser=False) == "ok"


def test_classify_forbidden_other_user() -> None:
    inv = SimpleNamespace(user_id=99)
    assert classify_investigation_access(inv, user_id=1, is_superuser=False) == "forbidden"


def test_classify_ok_superuser_even_if_not_owner() -> None:
    inv = SimpleNamespace(user_id=99)
    assert classify_investigation_access(inv, user_id=1, is_superuser=True) == "ok"


def test_legal_queries_to_public_list_shape() -> None:
    class FixedDT:
        def isoformat(self) -> str:
            return "2024-01-01T00:00:00"

    q = SimpleNamespace(
        id=1,
        provider="datajud",
        query_type="search",
        query_params={"a": 1},
        result_count=3,
        response={"hits": []},
        created_at=FixedDT(),
    )
    out = legal_queries_to_public_list([q])
    assert len(out) == 1
    assert out[0]["id"] == 1
    assert out[0]["provider"] == "datajud"
    assert out[0]["created_at"] == "2024-01-01T00:00:00"


async def test_require_investigation_for_user_raises_404_when_missing(monkeypatch) -> None:
    class FakeRepo:
        def __init__(self, _db):
            pass

        async def get(self, _id):
            return None

        async def get_with_relations(self, _id):
            return None

    monkeypatch.setattr(
        "app.services.investigation_access.InvestigationRepository",
        FakeRepo,
    )

    class FakeSession:
        pass

    with pytest.raises(HTTPException) as exc:
        await require_investigation_for_user(
            FakeSession(),  # type: ignore[arg-type]
            999,
            1,
            is_superuser=False,
            with_relations=False,
            not_found_detail="não existe",
        )
    assert exc.value.status_code == 404
    assert exc.value.detail == "não existe"
