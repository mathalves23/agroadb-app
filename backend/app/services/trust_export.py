"""
Pacote de evidência (trust bundle) por investigação: ZIP com PDF + manifest.json + README.

Destinado a auditorias, parceiros e RFPs: integridade do PDF (SHA-256), fingerprints das consultas
legais, linha temporal de eventos em audit_logs com resource_type=investigation, e referência
à política de retenção (configurável).
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Dict, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditLog, AuditLogger
from app.core.config import settings
from app.repositories.legal_query import LegalQueryRepository
from app.services.pdf_export import PDFExportService


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def titular_document_fingerprint_sha256(raw: str | None) -> str | None:
    """Hash do documento normalizado (só dígitos) — não expõe CPF/CNPJ no manifesto."""
    if not raw:
        return None
    normalized = "".join(c for c in str(raw) if c.isdigit())
    if not normalized:
        return None
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def fingerprint_legal_query(q: Any) -> Dict[str, Any]:
    created = q.created_at.isoformat() if getattr(q, "created_at", None) else None
    payload = {
        "id": q.id,
        "provider": q.provider,
        "query_type": q.query_type,
        "result_count": int(q.result_count or 0),
        "created_at": created,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {
        **payload,
        "integrity_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }


def _audit_timeline_entry(log: AuditLog) -> Dict[str, Any]:
    return {
        "id": log.id,
        "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        "user_id": log.user_id,
        "username": log.username,
        "action": log.action,
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
        "method": log.method,
        "endpoint": log.endpoint,
        "details": log.details,
        "success": log.success,
        "ip_address": log.ip_address,
    }


def _readme_pt() -> str:
    return """Pacote de evidência AgroADB (trust bundle)
============================================

Ficheiros:
- relatorio.pdf — relatório analítico da investigação (mesma geração que a exportação PDF da API).
- manifest.json — metadados, SHA-256 do PDF, fingerprints das consultas legais registadas na
  base de dados, linha temporal de audit_logs com resource_type=investigation para este ID,
  e referência à política de retenção indicada pelo responsável pelo tratamento.
- README_PACOTE.txt — este ficheiro.

Verificação de integridade:
- Compare o digest SHA-256 do ficheiro relatorio.pdf com o campo files.relatorio.pdf.sha256 em manifest.json.

Nota: respostas brutas das APIs externas não são duplicadas no manifesto por motivos de volume e
privacidade; os fingerprints das consultas legais permitem correlacionar com os registos internos
(legal_queries) e auditoria.
"""


def _build_pdf_payloads(
    investigation: Any, legal_queries: List[Any]
) -> Tuple[dict, list, list, list]:
    properties = investigation.properties or []
    companies = investigation.companies or []
    investigation_dict = {
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
    return investigation_dict, properties_list, companies_list, legal_queries_list


async def build_trust_bundle_zip(
    db: AsyncSession,
    *,
    investigation_id: int,
    investigation: Any,
    current_user_id: int,
    current_username: str | None,
) -> Tuple[BytesIO, str]:
    """
    Gera ZIP em memória e nome de ficheiro sugerido.
    `investigation` deve incluir relações (properties, companies) como na exportação PDF.
    """
    legal_query_repo = LegalQueryRepository(db)
    legal_queries = await legal_query_repo.list_by_investigation(investigation_id)

    inv_dict, props, comps, lq_pdf = _build_pdf_payloads(investigation, legal_queries)
    pdf_service = PDFExportService()
    pdf_buffer = pdf_service.generate_investigation_pdf(inv_dict, props, comps, lq_pdf)
    pdf_bytes = pdf_buffer.getvalue()
    pdf_sha256 = _sha256_bytes(pdf_bytes)

    cap = max(1, int(settings.TRUST_BUNDLE_AUDIT_LOG_CAP))
    audit_rows = await AuditLogger.get_resource_logs(
        db, "investigation", str(investigation_id), limit=cap
    )
    audit_sorted = sorted(
        audit_rows, key=lambda x: x.timestamp or datetime.min.replace(tzinfo=None)
    )

    manifest: Dict[str, Any] = {
        "schema_version": settings.TRUST_BUNDLE_MANIFEST_SCHEMA_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "application": {"name": settings.PROJECT_NAME, "version": settings.VERSION},
        "export": {
            "kind": "agroadb_investigation_trust_bundle",
            "investigation_id": investigation_id,
        },
        "generated_by": {"user_id": current_user_id, "username": current_username},
        "retention_and_legal_reference": settings.TRUST_BUNDLE_RETENTION_REFERENCE,
        "investigation_summary": {
            "id": investigation.id,
            "target_name": investigation.target_name,
            "status": investigation.status,
            "titular_document_fingerprint_sha256": titular_document_fingerprint_sha256(
                getattr(investigation, "target_cpf_cnpj", None)
            ),
            "created_at": inv_dict.get("created_at"),
            "updated_at": inv_dict.get("updated_at"),
            "counts": {
                "properties": inv_dict.get("properties_found", 0),
                "companies": inv_dict.get("companies_found", 0),
                "lease_contracts": inv_dict.get("lease_contracts_found", 0),
                "legal_queries": len(legal_queries),
            },
        },
        "files": {
            "relatorio.pdf": {
                "sha256": pdf_sha256,
                "media_type": "application/pdf",
                "bytes": len(pdf_bytes),
            },
        },
        "legal_queries": [fingerprint_legal_query(q) for q in legal_queries],
        "audit_timeline": [_audit_timeline_entry(log) for log in audit_sorted],
        "audit_timeline_note": (
            f"Inclui até {cap} eventos com resource_type=investigation e resource_id={investigation_id}, "
            "ordenados cronologicamente. Integrações podem registar acções adicionais noutros resource_type."
        ),
    }

    manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")

    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("relatorio.pdf", pdf_bytes)
        zf.writestr("manifest.json", manifest_bytes)
        zf.writestr("README_PACOTE.txt", _readme_pt().encode("utf-8"))

    zip_buf.seek(0)
    safe_name = (investigation.target_name or "investigacao").replace(" ", "_")[:80]
    created = (
        investigation.created_at.strftime("%Y%m%d") if investigation.created_at else "sem_data"
    )
    filename = f"agroadb_evidencia_inv_{investigation_id}_{safe_name}_{created}.zip"
    return zip_buf, filename
