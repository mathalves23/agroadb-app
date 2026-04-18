"""
Casos de uso PJe + auditoria (evita repetir chamadas ao serviço + log_action no router).
"""

from __future__ import annotations

from typing import Any, List, Optional, Protocol

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.legal_integration import PJeCase, legal_integration_service


class PJeAuditSink(Protocol):
    async def log_action(
        self,
        db: AsyncSession,
        user_id: Optional[int],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        method: Optional[str] = None,
        endpoint: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> Any: ...


async def consultar_processo_pje_com_audit(
    db: AsyncSession,
    audit_logger: PJeAuditSink,
    *,
    user_id: int,
    ip_address: Optional[str],
    numero_processo: str,
    tribunal: str,
) -> PJeCase:
    processo = await legal_integration_service.pje_service.consultar_processo(
        numero_processo, tribunal
    )
    await audit_logger.log_action(
        db=db,
        user_id=user_id,
        action="consulta_processo_pje",
        resource_type="pje",
        resource_id=numero_processo,
        details={
            "numero_processo": numero_processo,
            "tribunal": tribunal,
            "encontrado": processo is not None,
        },
        ip_address=ip_address,
    )
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return processo


async def consultar_processos_parte_com_audit(
    db: AsyncSession,
    audit_logger: PJeAuditSink,
    *,
    user_id: int,
    ip_address: Optional[str],
    cpf_cnpj: str,
    tipo_parte: str,
) -> List[Any]:
    processos = await legal_integration_service.pje_service.consultar_processos_parte(
        cpf_cnpj, tipo_parte
    )
    await audit_logger.log_action(
        db=db,
        user_id=user_id,
        action="consulta_processos_parte",
        resource_type="pje",
        resource_id=cpf_cnpj,
        details={
            "cpf_cnpj": cpf_cnpj,
            "tipo_parte": tipo_parte,
            "total_encontrados": len(processos),
        },
        ip_address=ip_address,
    )
    return processos


async def obter_movimentacoes_com_audit(
    db: AsyncSession,
    audit_logger: PJeAuditSink,
    *,
    user_id: int,
    ip_address: Optional[str],
    numero_processo: str,
) -> list:
    movimentacoes = await legal_integration_service.pje_service.obter_movimentacoes(numero_processo)
    await audit_logger.log_action(
        db=db,
        user_id=user_id,
        action="consulta_movimentacoes",
        resource_type="pje",
        resource_id=numero_processo,
        details={
            "numero_processo": numero_processo,
            "total_movimentacoes": len(movimentacoes),
        },
        ip_address=ip_address,
    )
    return movimentacoes
