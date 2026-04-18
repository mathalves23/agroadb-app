"""
Abstração de checkout / faturação — Stripe e Pagar.me.
Sem dependências obrigatórias: se as chaves não estiverem definidas, devolve URLs de demonstração.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Literal, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

Provider = Literal["stripe", "pagarme"]


def create_checkout_session(
    *,
    organization_id: int,
    plan: str,
    provider: Provider,
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Cria sessão de checkout (Stripe Checkout ou link Pagar.me).
    Em modo demonstração, devolve URLs fictícias com metadados.
    """
    success_url = success_url or f"{settings.FRONTEND_URL}/billing/success"
    cancel_url = cancel_url or f"{settings.FRONTEND_URL}/billing/cancel"
    ref = str(uuid.uuid4())

    if provider == "stripe" and settings.STRIPE_SECRET_KEY:
        try:
            import stripe
        except ImportError:
            logger.warning("Pacote 'stripe' não instalado — usar modo demo ou pip install stripe")
        else:
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                session = stripe.checkout.Session.create(
                    mode="subscription",
                    success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=cancel_url,
                    line_items=[
                        {
                            "price_data": {
                                "currency": "brl",
                                "product_data": {"name": f"AgroADB — {plan}"},
                                "unit_amount": 9900 if plan == "starter" else 29900,
                                "recurring": {"interval": "month"},
                            },
                            "quantity": 1,
                        }
                    ],
                    metadata={"organization_id": str(organization_id), "plan": plan},
                )
                return {
                    "provider": "stripe",
                    "url": session.url,
                    "session_id": session.id,
                    "mode": "live",
                }
            except Exception as exc:
                logger.exception("Stripe checkout falhou: %s", exc)

    if provider == "pagarme" and settings.PAGARME_SECRET_KEY:
        # Pagar.me v5 usa links ou orders — aqui apenas estrutura para o front tratar.
        return {
            "provider": "pagarme",
            "url": f"{settings.FRONTEND_URL}/billing/pagarme-placeholder?ref={ref}",
            "session_id": ref,
            "mode": "stub",
            "message": "Configure o fluxo Pagar.me (orders/links) com PAGARME_SECRET_KEY.",
        }

    logger.info(
        "Checkout em modo demonstração (org=%s plan=%s provider=%s)",
        organization_id,
        plan,
        provider,
    )
    return {
        "provider": provider,
        "url": f"{settings.FRONTEND_URL}/billing/demo?org={organization_id}&plan={plan}&ref={ref}",
        "session_id": f"demo_{ref}",
        "mode": "demo",
    }
