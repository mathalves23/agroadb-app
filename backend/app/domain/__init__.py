"""Domain models initialization"""

# Import all models here to ensure SQLAlchemy can resolve relationships
from app.domain.user import User
from app.domain.investigation import Investigation, InvestigationStatus
from app.domain.property import Property
from app.domain.company import Company
from app.domain.lease_contract import LeaseContract
from app.domain.legal_query import LegalQuery
from app.domain.organization import Organization, OrganizationMember, OrganizationMemberRole
from app.domain.organization_subscription import (
    OrganizationSubscription,
    PlanTier,
    SubscriptionStatus,
    BillingProvider,
)
from app.domain.legal_integration_config import LegalIntegrationConfig
from app.domain.api_key import ApiKey

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
