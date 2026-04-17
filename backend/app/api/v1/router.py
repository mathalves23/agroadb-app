"""
API Router - combines all API endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, 
    investigations, 
    users, 
    queue, 
    security, 
    notifications as notifications_old,
    collaboration,
    legal_integration,
    ml,
    integrations,
    settings,
    two_factor,
    lgpd,
    ocr,
)
from app.api.v1.endpoints import notifications as notifications_new

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["Investigations"])
api_router.include_router(queue.router, tags=["Queue & WebSocket"])
api_router.include_router(security.router, prefix="/security", tags=["Security & LGPD"])
api_router.include_router(notifications_old.router, prefix="/notifications-legacy", tags=["Notifications & Reports (Legacy)"])
api_router.include_router(notifications_new.router, tags=["Notifications"])
api_router.include_router(collaboration.router, prefix="/collaboration", tags=["Collaboration"])
api_router.include_router(legal_integration.router, prefix="/legal", tags=["Legal Integration"])
api_router.include_router(ml.router, tags=["Machine Learning"])
api_router.include_router(integrations.router, tags=["External Integrations"])
api_router.include_router(ocr.router, tags=["OCR"])
api_router.include_router(settings.router, tags=["Settings"])
api_router.include_router(two_factor.router, prefix="/auth/2fa", tags=["2FA"])
api_router.include_router(lgpd.router, prefix="/lgpd", tags=["LGPD"])