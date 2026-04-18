"""Repositório de organizações e membros."""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.organization import Organization, OrganizationMember
from app.domain.organization_subscription import (
    BillingProvider,
    OrganizationSubscription,
    PlanTier,
    SubscriptionStatus,
)


def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return s[:100] or "org"


class OrganizationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, org_id: int) -> Optional[Organization]:
        r = await self.db.execute(select(Organization).where(Organization.id == org_id))
        return r.scalar_one_or_none()

    async def get_with_subscription(self, org_id: int) -> Optional[Organization]:
        r = await self.db.execute(
            select(Organization)
            .where(Organization.id == org_id)
            .options(selectinload(Organization.subscription))
        )
        return r.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        r = await self.db.execute(select(Organization).where(Organization.slug == slug))
        return r.scalar_one_or_none()

    async def list_for_user(self, user_id: int) -> Sequence[Organization]:
        r = await self.db.execute(
            select(Organization)
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
            .options(selectinload(Organization.subscription))
        )
        return r.scalars().all()

    async def create_with_owner(
        self,
        *,
        name: str,
        owner_user_id: int,
        description: Optional[str] = None,
        trial_days: int = 14,
    ) -> Organization:
        base = slugify(name)
        slug = base
        n = 1
        while await self.get_by_slug(slug):
            n += 1
            slug = f"{base}-{n}"

        org = Organization(name=name, slug=slug, description=description)
        self.db.add(org)
        await self.db.flush()

        member = OrganizationMember(
            organization_id=org.id,
            user_id=owner_user_id,
            role="owner",
        )
        self.db.add(member)

        trial_end = datetime.utcnow() + timedelta(days=trial_days)
        sub = OrganizationSubscription(
            organization_id=org.id,
            plan=PlanTier.TRIAL.value,
            status=SubscriptionStatus.TRIALING.value,
            billing_provider=BillingProvider.NONE.value,
            trial_ends_at=trial_end,
            limits={
                "max_investigations": 25,
                "max_org_members": 20,
            },
        )
        self.db.add(sub)
        await self.db.flush()
        await self.db.refresh(org)
        return org

    async def list_member_user_ids(self, organization_id: int) -> List[int]:
        r = await self.db.execute(
            select(OrganizationMember.user_id).where(
                OrganizationMember.organization_id == organization_id
            )
        )
        return [row[0] for row in r.all()]
