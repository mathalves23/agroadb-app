"""Organizações / equipas e visão da subscrição SaaS."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.deps import CurrentUser, DatabaseSession
from app.core.audit import AuditAction, audit_logger
from app.core.org_permissions import require_org_role
from app.repositories.organization import OrganizationRepository

router = APIRouter(prefix="/organizations", tags=["Organizations"])


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    risk_ai_human_review_required: bool = False
    risk_ai_governance_reference_url: Optional[str] = None


class OrganizationAIGovernancePatch(BaseModel):
    """Política de governança do score de risco automatizado (RIPD / diligência)."""

    risk_ai_human_review_required: Optional[bool] = None
    risk_ai_governance_reference_url: Optional[str] = Field(
        None,
        max_length=4096,
        description="URL ou texto curto para DPIA/RIPD ou registo interno",
    )


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada"
        )

    repo = OrganizationRepository(db)
    org = await repo.get_with_subscription(organization_id)
    if not org or not org.subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subscrição não encontrada"
        )
    sub = org.subscription
    return SubscriptionOut(
        plan=sub.plan,
        status=sub.status,
        billing_provider=sub.billing_provider,
        trial_ends_at=sub.trial_ends_at.isoformat() if sub.trial_ends_at else None,
        limits=dict(sub.limits or {}),
    )


@router.patch(
    "/{organization_id}/ai-governance",
    response_model=OrganizationOut,
    summary="Atualizar política de IA (score de risco)",
)
async def patch_organization_ai_governance(
    organization_id: int,
    body: OrganizationAIGovernancePatch,
    request: Request,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> OrganizationOut:
    await require_org_role(db, current_user.id, organization_id, "admin")
    patch = body.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie pelo menos um campo a atualizar.",
        )
    repo = OrganizationRepository(db)
    org = await repo.update_ai_governance(organization_id, patch)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada"
        )
    await audit_logger.log(
        db=db,
        action=AuditAction.ORGANIZATION_AI_GOVERNANCE_UPDATED,
        user_id=current_user.id,
        username=getattr(current_user, "username", None),
        resource_type="organization",
        resource_id=str(organization_id),
        details={
            "risk_ai_human_review_required": org.risk_ai_human_review_required,
            "has_governance_reference_url": bool(org.risk_ai_governance_reference_url),
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        method=request.method,
        endpoint=str(request.url.path),
    )
    return OrganizationOut.model_validate(org)
