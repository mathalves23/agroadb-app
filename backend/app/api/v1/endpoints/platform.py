"""
Plataforma — proposta de valor B2B e resumo de conformidade (API pública de marketing/compliance).
"""
from __future__ import annotations

from fastapi import APIRouter

from app.contexts.commercial import build_compliance_summary, build_value_proposition

router = APIRouter(prefix="/platform", tags=["Platform — B2B & compliance"])


@router.get("/proposition", summary="Proposta de valor B2B (segmentos, LGPD, auditoria, exportações)")
async def get_value_proposition():
    """Conteúdo estável para sites, CRM e integradores (sem dados sensíveis)."""
    return build_value_proposition()


@router.get("/compliance-summary", summary="Resumo de pilares de conformidade e exportações")
async def get_compliance_summary():
    return build_compliance_summary()
