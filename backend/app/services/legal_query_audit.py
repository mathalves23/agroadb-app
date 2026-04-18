"""
Persistência de consultas legais/integrações ligadas a uma investigação (auditoria).

Centraliza o padrão «se investigation_id, gravar em legal_queries» usado nos routers
de integrações, alinhado ao estilo de `investigation_access` e `legal_pje_workflows`.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.legal_query import LegalQueryRepository


def _normalize_response_payload(response: Any) -> Dict[str, Any]:
    if isinstance(response, dict):
        return response
    return {"result": response}


async def record_legal_query_if_investigation(
    db: AsyncSession,
    investigation_id: Optional[int],
    *,
    provider: str,
    query_type: str,
    query_params: Dict[str, Any],
    result_count: int,
    response: Any,
    ignore_errors: bool = False,
) -> None:
    if investigation_id is None:
        return
    try:
        repo = LegalQueryRepository(db)
        await repo.create(
            {
                "investigation_id": investigation_id,
                "provider": provider,
                "query_type": query_type,
                "query_params": query_params,
                "result_count": result_count,
                "response": _normalize_response_payload(response),
            }
        )
    except Exception:
        if not ignore_errors:
            raise
