"""
Agregador da API v1: monta todos os routers em /api/v1.

O router de notificações é o mesmo módulo montado duas vezes: prefixo legacy
e montagem canónica (compatibilidade de URLs antigas).
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    api_keys,
    auth,
    billing,
    collaboration,
    integration_webhooks,
    integrations,
    investigations,
    legal_integration,
    lgpd,
    ml,
    notifications,
    ocr,
    organizations,
    platform,
    queue,
    security,
    settings,
    two_factor,
    users,
)

api_router = APIRouter()

api_router.include_router(platform.router)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["Investigations"])
api_router.include_router(queue.router, tags=["Queue & WebSocket"])
api_router.include_router(security.router, prefix="/security", tags=["Security & LGPD"])
api_router.include_router(
    notifications.router,
    prefix="/notifications-legacy",
    tags=["Notifications & Reports (Legacy)"],
)
api_router.include_router(notifications.router, tags=["Notifications"])
api_router.include_router(collaboration.router, prefix="/collaboration", tags=["Collaboration"])
api_router.include_router(legal_integration.router, prefix="/legal", tags=["Legal Integration"])
api_router.include_router(ml.router, tags=["Machine Learning"])
api_router.include_router(integrations.router, tags=["External Integrations"])
api_router.include_router(ocr.router, tags=["OCR"])
api_router.include_router(settings.router, tags=["Settings"])
api_router.include_router(two_factor.router, prefix="/auth/2fa", tags=["2FA"])
api_router.include_router(lgpd.router, prefix="/lgpd", tags=["LGPD"])
api_router.include_router(organizations.router, tags=["Organizations"])
api_router.include_router(billing.router, tags=["Billing"])
api_router.include_router(integration_webhooks.router, tags=["Webhooks"])
api_router.include_router(api_keys.router, tags=["API Keys"])
