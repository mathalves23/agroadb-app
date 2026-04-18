"""Verificação de assinaturas HMAC para webhooks (integrações genéricas)."""
from __future__ import annotations

import hashlib
import hmac
from typing import Optional


def compute_hmac_sha256_hex(secret: str, payload: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def verify_webhook_hmac(
    secret: str,
    payload: bytes,
    signature_header: Optional[str],
    *,
    prefix: str = "sha256=",
) -> bool:
    """
    Compara o header (ex.: ``sha256=<hex>`` ou só o hex) com HMAC-SHA256 do corpo.
    """
    if not secret or not signature_header:
        return False
    sig = signature_header.strip()
    if sig.startswith(prefix):
        sig = sig[len(prefix) :]
    expected = compute_hmac_sha256_hex(secret, payload)
    return hmac.compare_digest(sig.lower(), expected.lower())
