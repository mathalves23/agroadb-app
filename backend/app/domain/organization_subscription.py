"""
Planos SaaS, trial e referências Stripe / Pagar.me por organização.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.domain.organization import Organization


def _default_plan_limits() -> Dict[str, Any]:
    return {"max_investigations": 50, "max_org_members": 20}


class PlanTier(str, Enum):
    TRIAL = "trial"
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"


class BillingProvider(str, Enum):
    NONE = "none"
    STRIPE = "stripe"
    PAGARME = "pagarme"


class OrganizationSubscription(Base):
    __tablename__ = "organization_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    plan: Mapped[str] = mapped_column(String(32), nullable=False, default=PlanTier.TRIAL.value)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=SubscriptionStatus.TRIALING.value)
    billing_provider: Mapped[str] = mapped_column(String(16), nullable=False, default=BillingProvider.NONE.value)

    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    pagarme_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pagarme_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    limits: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        insert_default=_default_plan_limits,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    organization: Mapped["Organization"] = relationship("Organization", back_populates="subscription")
