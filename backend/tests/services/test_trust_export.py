"""Testes unitários do pacote de evidência (fingerprints, sem I/O)."""

from __future__ import annotations

from types import SimpleNamespace

from app.services.trust_export import fingerprint_legal_query, titular_document_fingerprint_sha256


def test_titular_document_fingerprint_normalizes_digits() -> None:
    h1 = titular_document_fingerprint_sha256("529.982.247-25")
    h2 = titular_document_fingerprint_sha256("52998224725")
    assert h1 == h2
    assert h1 and len(h1) == 64


def test_titular_document_fingerprint_none() -> None:
    assert titular_document_fingerprint_sha256(None) is None
    assert titular_document_fingerprint_sha256("") is None


def test_fingerprint_legal_query_stable() -> None:
    class DT:
        def isoformat(self) -> str:
            return "2024-06-01T12:00:00"

    q = SimpleNamespace(
        id=1,
        provider="datajud",
        query_type="proc",
        result_count=2,
        created_at=DT(),
    )
    fp = fingerprint_legal_query(q)
    assert fp["integrity_sha256"] == fingerprint_legal_query(q)["integrity_sha256"]
    assert fp["provider"] == "datajud"
