"""
Leitura pública de investigação via link de convidado (sem JWT).

Rotas sob prefixo `/api/v1/public`.
"""

from __future__ import annotations

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditAction, audit_logger
from app.core.config import settings
from app.core.database import get_db
from app.repositories.investigation import InvestigationRepository
from app.repositories.legal_query import LegalQueryRepository
from app.schemas.investigation import InvestigationResponse
from app.services.investigation_guest_link import (
    get_guest_link_by_token,
    guest_link_is_valid,
    record_guest_access,
)
from app.services.pdf_export import PDFExportService

router = APIRouter()


def _legal_queries_guest_summary(queries: List[Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": q.id,
            "provider": q.provider,
            "query_type": q.query_type,
            "result_count": q.result_count,
            "created_at": q.created_at.isoformat() if q.created_at else None,
        }
        for q in queries
    ]


def _maybe_decrypt_investigation(inv: Any) -> None:
    if settings.ENCRYPTION_KEY and inv.target_cpf_cnpj:
        try:
            from app.core.encryption import data_encryption

            inv.target_cpf_cnpj = data_encryption.decrypt(inv.target_cpf_cnpj)
        except Exception:
            pass


@router.get("/guest/investigation", summary="Ver investigação com token de convidado")
async def guest_get_investigation(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: str = Query(
        ..., min_length=16, description="Token devolvido na criação do link (mostrado uma vez)"
    ),
):
    link = await get_guest_link_by_token(db, token)
    if not link or not guest_link_is_valid(link):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link inválido ou expirado"
        )

    repo = InvestigationRepository(db)
    investigation = await repo.get_with_relations(link.investigation_id)
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investigação não encontrada"
        )

    await record_guest_access(db, link)

    await audit_logger.log(
        db=db,
        action=AuditAction.INVESTIGATION_GUEST_ACCESSED,
        user_id=None,
        username="guest_link",
        resource_type="investigation",
        resource_id=str(investigation.id),
        details={"guest_link_id": link.id, "label": link.label},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        method=request.method,
        endpoint="/api/v1/public/guest/investigation",
    )

    lrepo = LegalQueryRepository(db)
    legal_queries = await lrepo.list_by_investigation(investigation.id)

    _maybe_decrypt_investigation(investigation)
    body = InvestigationResponse.model_validate(investigation).model_dump()
    return {
        "guest": True,
        "allow_downloads": link.allow_downloads,
        "guest_link_id": link.id,
        "label": link.label,
        "expires_at": link.expires_at.isoformat() if link.expires_at else None,
        "investigation": body,
        "legal_queries": _legal_queries_guest_summary(legal_queries),
    }


@router.get("/guest/investigation/export/pdf", summary="PDF só se o link permitir downloads")
async def guest_export_pdf(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: str = Query(..., min_length=16),
):
    link = await get_guest_link_by_token(db, token)
    if not link or not guest_link_is_valid(link):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link inválido ou expirado"
        )
    if not link.allow_downloads:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este link não permite exportação. Peça ao dono da investigação um link com downloads ou uma partilha registada.",
        )

    repo = InvestigationRepository(db)
    investigation = await repo.get_with_relations(link.investigation_id)
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investigação não encontrada"
        )

    lrepo = LegalQueryRepository(db)
    legal_queries = await lrepo.list_by_investigation(investigation.id)

    properties = investigation.properties or []
    companies = investigation.companies or []
    inv_dict = {
        "id": investigation.id,
        "target_name": investigation.target_name,
        "target_cpf_cnpj": investigation.target_cpf_cnpj,
        "target_description": investigation.target_description,
        "status": investigation.status,
        "created_at": investigation.created_at.isoformat() if investigation.created_at else None,
        "updated_at": investigation.updated_at.isoformat() if investigation.updated_at else None,
        "properties_found": len(properties),
        "companies_found": len(companies),
        "lease_contracts_found": investigation.lease_contracts_found or 0,
    }

    properties_list = [
        {
            "name": p.property_name or "N/A",
            "area_ha": p.area_hectares or 0,
            "location": f"{p.city or ''}, {p.state or ''}".strip(", "),
            "source": p.data_source,
            "registration_code": p.car_number or p.ccir_number or p.matricula or "N/A",
        }
        for p in properties
    ]
    companies_list = [
        {
            "name": c.trade_name or c.corporate_name or "N/A",
            "cnpj": c.cnpj,
            "registration_status": c.status or "N/A",
            "activity": c.main_activity or "N/A",
            "address": c.address or "N/A",
        }
        for c in companies
    ]
    legal_queries_list = [
        {
            "id": q.id,
            "provider": q.provider,
            "query_type": q.query_type,
            "result_count": q.result_count,
            "created_at": q.created_at.isoformat() if q.created_at else None,
        }
        for q in legal_queries
    ]

    if settings.ENCRYPTION_KEY and investigation.target_cpf_cnpj:
        try:
            from app.core.encryption import data_encryption

            inv_dict["target_cpf_cnpj"] = data_encryption.decrypt(investigation.target_cpf_cnpj)
        except Exception:
            inv_dict["target_cpf_cnpj"] = investigation.target_cpf_cnpj
    else:
        inv_dict["target_cpf_cnpj"] = investigation.target_cpf_cnpj

    pdf_service = PDFExportService()
    wm = [
        "AgroADB — leitura convidado",
        f"Investigação #{investigation.id}",
        "Confidencial — traço de auditoria",
    ]
    pdf_buffer = pdf_service.generate_investigation_pdf(
        inv_dict,
        properties_list,
        companies_list,
        legal_queries_list,
        watermark_lines=wm,
    )

    await audit_logger.log(
        db=db,
        action=AuditAction.INVESTIGATION_GUEST_EXPORTED,
        user_id=None,
        username="guest_link",
        resource_type="investigation",
        resource_id=str(investigation.id),
        details={"guest_link_id": link.id, "format": "pdf"},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        method=request.method,
        endpoint="/api/v1/public/guest/investigation/export/pdf",
    )

    target_name = (investigation.target_name or "investigacao").replace(" ", "_")
    created_date = (
        investigation.created_at.strftime("%Y%m%d") if investigation.created_at else "sem_data"
    )
    filename = f"relatorio_guest_{investigation.id}_{target_name}_{created_date}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
