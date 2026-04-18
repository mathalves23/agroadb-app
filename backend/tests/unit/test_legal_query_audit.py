"""Testes do serviço de auditoria de consultas legais ligadas a investigações."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.legal_query_audit import record_legal_query_if_investigation


@pytest.mark.asyncio
async def test_record_skips_when_no_investigation_id() -> None:
    with patch("app.services.legal_query_audit.LegalQueryRepository") as Repo:
        await record_legal_query_if_investigation(
            MagicMock(),
            None,
            provider="ibama",
            query_type="embargos",
            query_params={"cpf_cnpj": "123"},
            result_count=0,
            response={},
        )
        Repo.assert_not_called()


@pytest.mark.asyncio
async def test_record_normalizes_non_dict_response() -> None:
    create = AsyncMock()
    inst = MagicMock()
    inst.create = create
    with patch("app.services.legal_query_audit.LegalQueryRepository", return_value=inst):
        await record_legal_query_if_investigation(
            MagicMock(),
            42,
            provider="tjmg",
            query_type="processos",
            query_params={"cpf": "x"},
            result_count=1,
            response=["lista"],
        )
    create.assert_awaited_once()
    payload = create.await_args.args[0]
    assert payload["response"] == {"result": ["lista"]}


@pytest.mark.asyncio
async def test_ignore_errors_swallows_repository_failure() -> None:
    with patch("app.services.legal_query_audit.LegalQueryRepository") as Repo:
        Repo.return_value.create = AsyncMock(side_effect=RuntimeError("db down"))
        await record_legal_query_if_investigation(
            MagicMock(),
            1,
            provider="bnmp_cnj",
            query_type="mandados_prisao",
            query_params={},
            result_count=0,
            response={},
            ignore_errors=True,
        )


@pytest.mark.asyncio
async def test_ignore_errors_false_propagates() -> None:
    with patch("app.services.legal_query_audit.LegalQueryRepository") as Repo:
        Repo.return_value.create = AsyncMock(side_effect=RuntimeError("db down"))
        with pytest.raises(RuntimeError):
            await record_legal_query_if_investigation(
                MagicMock(),
                1,
                provider="x",
                query_type="y",
                query_params={},
                result_count=0,
                response={},
                ignore_errors=False,
            )
