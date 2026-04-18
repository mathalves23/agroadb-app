"""Pacote de routers de integrações externas (sub-routers + restante)."""

from fastapi import APIRouter

from .biros_orgaos_notify import router as biros_router
from .conecta import router as conecta_router
from .remainder_environment import router as remainder_environment_router
from .remainder_open_data import router as remainder_open_data_router
from .remainder_supervision import router as remainder_supervision_router
from .remainder_transparency import router as remainder_transparency_router
from .tribunais import router as tribunais_router

router = APIRouter(prefix="/integrations", tags=["integrations"])
router.include_router(remainder_open_data_router)
router.include_router(remainder_transparency_router)
router.include_router(remainder_supervision_router)
router.include_router(remainder_environment_router)
router.include_router(conecta_router)
router.include_router(tribunais_router)
router.include_router(biros_router)
