"""Pacote de routers de integrações externas (sub-routers + restante)."""
from fastapi import APIRouter

from .biros_orgaos_notify import router as biros_router
from .conecta import router as conecta_router
from .remainder import router as remainder_router
from .tribunais import router as tribunais_router

router = APIRouter(prefix="/integrations", tags=["integrations"])
router.include_router(remainder_router)
router.include_router(conecta_router)
router.include_router(tribunais_router)
router.include_router(biros_router)
