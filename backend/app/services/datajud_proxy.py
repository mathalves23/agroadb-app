"""
Caso de uso: proxy DataJud + registo opcional em legal_queries + auditoria.

Mantém o router `legal_integration` fino e concentra persistência/auditoria aqui.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.legal_query import LegalQueryRepository
from app.services.datajud import DataJudService, datajud_result_count


class _DataJudClient(Protocol):
    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Any: ...


class _AuditLogSink(Protocol):
    async def log_action(
        self,
        db: AsyncSession,
        user_id: Optional[int],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        method: Optional[str] = None,
        endpoint: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> Any: ...


async def run_datajud_proxy(
    db: AsyncSession,
    audit_logger: _AuditLogSink,
    *,
    user_id: int,
    ip_address: Optional[str],
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    payload: Optional[Dict[str, Any]] = None,
    investigation_id: Optional[int] = None,
    query_type: Optional[str] = None,
    datajud_client: Optional[_DataJudClient] = None,
) -> Any:
    """
    Chama o DataJud, grava legal_query se houver investigation_id e regista auditoria.
    Propaga ValueError (ex.: config ou HTTP do cliente) para o router mapear 400/500.
    """
    client = datajud_client or DataJudService()
    result = await client.request(
        method=method,
        path=path,
        params=params,
        payload=payload,
    )

    if investigation_id:
        repo = LegalQueryRepository(db)
        await repo.create(
            {
                "investigation_id": investigation_id,
                "provider": "datajud",
                "query_type": query_type or path,
                "query_params": {"params": params or {}, "payload": payload or {}},
                "result_count": datajud_result_count(result),
                "response": result if isinstance(result, dict) else {"result": result},
            }
        )

    await audit_logger.log_action(
        db=db,
        user_id=user_id,
        action="consulta_datajud",
        resource_type="datajud",
        resource_id=path,
        details={"method": method, "path": path},
        ip_address=ip_address,
    )

    return result
