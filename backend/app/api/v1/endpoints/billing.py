"""Checkout e webhooks de faturação (Stripe / Pagar.me)."""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.api.v1.deps import CurrentUser, DatabaseSession
from app.core.config import settings
from app.core.org_permissions import require_org_any_role
from app.services.billing.checkout import create_checkout_session

router = APIRouter(prefix="/billing", tags=["Billing"])


class CheckoutRequest(BaseModel):
    organization_id: int
    plan: str = Field(..., description="trial | free | starter | pro | enterprise")
    provider: Literal["stripe", "pagarme"]


@router.post("/checkout")
async def billing_checkout(
    body: CheckoutRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Dict[str, Any]:
    await require_org_any_role(
        db,
        current_user.id,
        body.organization_id,
        frozenset({"owner", "admin", "billing"}),
    )
    return create_checkout_session(
        organization_id=body.organization_id,
        plan=body.plan,
        provider=body.provider,
    )


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
) -> Dict[str, str]:
    """
    Webhook Stripe — valida assinatura quando STRIPE_WEBHOOK_SECRET está definido.
    """
    body = await request.body()
    if settings.STRIPE_WEBHOOK_SECRET:
        try:
            import stripe
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Pacote stripe necessário para validar webhooks",
            )
        try:
            stripe.Webhook.construct_event(
                body,
                stripe_signature or "",
                settings.STRIPE_WEBHOOK_SECRET,
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Assinatura inválida"
            )
    return {"status": "received"}


@router.post("/webhooks/pagarme")
async def pagarme_webhook(
    request: Request,
    x_hub_signature: Optional[str] = Header(None, alias="X-Hub-Signature"),
) -> Dict[str, str]:
    """Webhook Pagar.me — validação HMAC opcional com PAGARME_WEBHOOK_SECRET."""
    from app.core.webhook_hmac import verify_webhook_hmac

    body = await request.body()
    if settings.PAGARME_WEBHOOK_SECRET:
        if not verify_webhook_hmac(
            settings.PAGARME_WEBHOOK_SECRET,
            body,
            x_hub_signature,
            prefix="sha256=",
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Assinatura inválida"
            )
    return {"status": "received"}
