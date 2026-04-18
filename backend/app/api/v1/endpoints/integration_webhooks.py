"""Webhooks assinados (HMAC) para integrações externas."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.core.config import settings
from app.core.webhook_hmac import verify_webhook_hmac

router = APIRouter(prefix="/webhooks", tags=["Integration Webhooks"])


@router.post("/integrations")
async def integration_events_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None, alias="X-Integration-Signature"),
) -> dict:
    """
    Recebe eventos de integrações com corpo bruto e assinatura HMAC-SHA256
    no header ``X-Integration-Signature`` (formato ``sha256=<hex>``).
    """
    if not settings.INTEGRATION_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="INTEGRATION_WEBHOOK_SECRET não configurado",
        )
    body = await request.body()
    if not verify_webhook_hmac(settings.INTEGRATION_WEBHOOK_SECRET, body, x_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Assinatura inválida")
    return {"ok": True, "bytes": len(body)}
