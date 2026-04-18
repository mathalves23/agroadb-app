"""Testes unitários dos helpers de integrações (bounded context)."""

from __future__ import annotations

from app.api.v1.endpoints.integrations_helpers import (
    conecta_items,
    conecta_standard_response,
    is_credentials_missing,
    result_count,
)


def test_result_count_list():
    assert result_count([1, 2, 3]) == 3


def test_result_count_dict_nested():
    assert result_count({"parcelas": [1, 2]}) == 2


def test_conecta_standard_response_shape():
    r = conecta_standard_response({"items": [1]}, warnings=["w"])
    assert r["success"] is True
    assert r["items"] == [1]
    assert r["warnings"] == ["w"]


def test_is_credentials_missing():
    assert is_credentials_missing(Exception("Credenciais Conecta não configuradas")) is True
    assert is_credentials_missing(Exception("timeout")) is False
