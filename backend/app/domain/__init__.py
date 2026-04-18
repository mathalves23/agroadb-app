"""Domain models initialization"""

# Import all models here to ensure SQLAlchemy can resolve relationships
from app.domain.api_key import ApiKey
from app.domain.company import Company
from app.domain.investigation import Investigation, InvestigationStatus
from app.domain.lease_contract import LeaseContract
from app.domain.legal_integration_config import LegalIntegrationConfig
from app.domain.legal_query import LegalQuery
from app.domain.organization import Organization, OrganizationMember, OrganizationMemberRole
from app.domain.organization_subscription import (
    BillingProvider,
    OrganizationSubscription,
    PlanTier,
    SubscriptionStatus,
)
from app.domain.property import Property
from app.domain.user import User

__all__ = [
    "User",
    "Investigation",
    "InvestigationStatus",
    "Property",
    "Company",
    "LeaseContract",
    "LegalQuery",
    "Organization",
    "OrganizationMember",
    "OrganizationMemberRole",
    "OrganizationSubscription",
    "PlanTier",
    "SubscriptionStatus",
    "BillingProvider",
    "LegalIntegrationConfig",
    "ApiKey",
]
