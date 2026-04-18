"""Organizações / equipas e visão da subscrição SaaS."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.v1.deps import CurrentUser, DatabaseSession
from app.repositories.organization import OrganizationRepository

router = APIRouter(prefix="/organizations", tags=["Organizations"])


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None


class OrganizationOut(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SubscriptionOut(BaseModel):
    plan: str
    status: str
    billing_provider: str
    trial_ends_at: Optional[str] = None
    limits: dict


@router.post("", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
async def create_organization(
    body: OrganizationCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> OrganizationOut:
    repo = OrganizationRepository(db)
    org = await repo.create_with_owner(
        name=body.name,
        owner_user_id=current_user.id,
        description=body.description,
    )
    return OrganizationOut.model_validate(org)


@router.get("/me", response_model=List[OrganizationOut])
async def list_my_organizations(
    current_user: CurrentUser,
    db: DatabaseSession,
) -> List[OrganizationOut]:
    repo = OrganizationRepository(db)
    orgs = await repo.list_for_user(current_user.id)
    return [OrganizationOut.model_validate(o) for o in orgs]


@router.get("/{organization_id}/subscription", response_model=SubscriptionOut)
async def get_organization_subscription(
    organization_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> SubscriptionOut:
    from app.core.org_permissions import get_member_role

    if not await get_member_role(db, current_user.id, organization_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada")

    repo = OrganizationRepository(db)
    org = await repo.get_with_subscription(organization_id)
    if not org or not org.subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscrição não encontrada")
    sub = org.subscription
    return SubscriptionOut(
        plan=sub.plan,
        status=sub.status,
        billing_provider=sub.billing_provider,
        trial_ends_at=sub.trial_ends_at.isoformat() if sub.trial_ends_at else None,
        limits=dict(sub.limits or {}),
    )
