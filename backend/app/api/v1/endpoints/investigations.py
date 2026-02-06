"""
Investigations Endpoints
"""
from typing import List
from fastapi import APIRouter, HTTPException, Request, status, Query
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.api.v1.deps import DatabaseSession, CurrentUser
from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationUpdate,
    InvestigationResponse,
    InvestigationListResponse,
)
from app.schemas.property import PropertyResponse, LeaseContractResponse, CompanyResponse
from app.services.investigation import InvestigationService
from app.services.excel_export import ExcelExportService
from app.services.pdf_export import PDFExportService
from app.repositories.investigation import InvestigationRepository
from app.repositories.legal_query import LegalQueryRepository
from app.core.config import settings
from app.core.audit import audit_logger, AuditAction

router = APIRouter()


@router.post("", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    investigation_data: InvestigationCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
    request: Request,
) -> InvestigationResponse:
    """Create a new investigation"""
    investigation_repo = InvestigationRepository(db)
    investigation_service = InvestigationService(investigation_repo)
    
    investigation = await investigation_service.create_investigation(
        current_user.id, investigation_data
    )

    # Audit log
    await audit_logger.log(
        db=db,
        action=AuditAction.INVESTIGATION_CREATED,
        user_id=current_user.id,
        username=current_user.username,
        resource_type="investigation",
        resource_id=str(investigation.id),
        details={"target_name": investigation.target_name},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        method=request.method,
        endpoint=str(request.url.path),
    )

    return InvestigationResponse.model_validate(investigation)


@router.get("", response_model=InvestigationListResponse)
async def list_investigations(
    current_user: CurrentUser,
    db: DatabaseSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
) -> InvestigationListResponse:
    """List investigations for current user"""
    skip = (page - 1) * page_size
    
    investigation_repo = InvestigationRepository(db)
    investigation_service = InvestigationService(investigation_repo)
    
    investigations, total = await investigation_service.list_investigations(
        current_user.id,
        skip=skip,
        limit=page_size,
        is_superuser=current_user.is_superuser,
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return InvestigationListResponse(
        items=[InvestigationResponse.model_validate(inv) for inv in investigations],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/cursor", response_model=dict)
async def list_investigations_cursor(
    current_user: CurrentUser,
    db: DatabaseSession,
    cursor: str = Query(None, description="Cursor para paginação"),
    limit: int = Query(20, ge=1, le=100, description="Itens por página"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    status_filter: str = Query(None, alias="status"),
):
    """List investigations with cursor-based pagination (more efficient for large datasets)"""
    from app.core.pagination import cursor_paginate, CursorPage
    from app.domain.investigation import Investigation

    filters = {"user_id": current_user.id}
    if current_user.is_superuser:
        filters = {}
    if status_filter:
        filters["status"] = status_filter

    result = await cursor_paginate(
        db,
        Investigation,
        cursor=cursor,
        limit=limit,
        order_by="created_at",
        order=order,
        filters=filters,
    )

    # Convert items to response format
    result.items = [
        InvestigationResponse.model_validate(item).model_dump()
        if hasattr(item, '__dict__') and not isinstance(item, dict)
        else item
        for item in result.items
    ]

    return result.model_dump()


@router.get("/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(
    investigation_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> InvestigationResponse:
    """Get investigation by ID"""
    investigation_repo = InvestigationRepository(db)
    investigation_service = InvestigationService(investigation_repo)
    
    investigation = await investigation_service.get_investigation(
        investigation_id, current_user.id, current_user.is_superuser
    )
    
    return InvestigationResponse.model_validate(investigation)


@router.patch("/{investigation_id}", response_model=InvestigationResponse)
async def update_investigation(
    investigation_id: int,
    investigation_data: InvestigationUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
    request: Request,
) -> InvestigationResponse:
    """Update investigation"""
    investigation_repo = InvestigationRepository(db)
    investigation_service = InvestigationService(investigation_repo)
    
    investigation = await investigation_service.update_investigation(
        investigation_id,
        current_user.id,
        investigation_data,
        current_user.is_superuser,
    )

    # Audit log
    await audit_logger.log(
        db=db,
        action=AuditAction.INVESTIGATION_UPDATED,
        user_id=current_user.id,
        username=current_user.username,
        resource_type="investigation",
        resource_id=str(investigation_id),
        details={"updated_fields": list(investigation_data.model_dump(exclude_unset=True).keys())},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        method=request.method,
        endpoint=str(request.url.path),
    )

    return InvestigationResponse.model_validate(investigation)


@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investigation(
    investigation_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
    request: Request,
) -> None:
    """Delete investigation"""
    investigation_repo = InvestigationRepository(db)
    investigation_service = InvestigationService(investigation_repo)
    
    await investigation_service.delete_investigation(
        investigation_id, current_user.id, current_user.is_superuser
    )

    # Audit log
    await audit_logger.log(
        db=db,
        action=AuditAction.INVESTIGATION_DELETED,
        user_id=current_user.id,
        username=current_user.username,
        resource_type="investigation",
        resource_id=str(investigation_id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        method=request.method,
        endpoint=str(request.url.path),
    )


@router.post("/{investigation_id}/enrich", response_model=InvestigationResponse)
async def enrich_investigation(
    investigation_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> InvestigationResponse:
    """
    Enriquece a investigação buscando dados cadastrais automaticamente.
    - CPF: consulta Receita Federal (situação cadastral, nome, nascimento)
    - CNPJ: consulta Receita Federal / BrasilAPI (razão social, situação, endereço, QSA)
    Atualiza target_name e target_description com os dados encontrados.
    """
    investigation_repo = InvestigationRepository(db)
    investigation_service = InvestigationService(investigation_repo)

    investigation = await investigation_service.get_investigation(
        investigation_id, current_user.id, current_user.is_superuser
    )

    doc = (investigation.target_cpf_cnpj or "").replace(".", "").replace("-", "").replace("/", "").strip()
    if not doc:
        raise HTTPException(status_code=400, detail="Investigação não possui CPF/CNPJ para enriquecer")

    enriched: dict = {}
    description_parts: list[str] = []

    if len(doc) == 11:
        # --- CPF ---
        # 1) Receita Federal CPF (situação cadastral + nome)
        from app.services.receita_cpf import ReceitaCPFService
        try:
            cpf_svc = ReceitaCPFService()
            cpf_data = await cpf_svc.consultar(doc)
            if cpf_data.get("nome"):
                enriched["target_name"] = cpf_data["nome"]
            parts = []
            if cpf_data.get("situacao_cadastral"):
                parts.append(f"Situação: {cpf_data['situacao_cadastral']}")
            if cpf_data.get("data_nascimento"):
                parts.append(f"Nascimento: {cpf_data['data_nascimento']}")
            if cpf_data.get("data_inscricao"):
                parts.append(f"Inscrição: {cpf_data['data_inscricao']}")
            if cpf_data.get("ano_obito"):
                parts.append(f"Óbito: {cpf_data['ano_obito']}")
            if parts:
                description_parts.append("Receita Federal: " + " | ".join(parts))
        except Exception:
            pass

        # 2) BrasilAPI CNPJ lookup não se aplica a CPF, mas podemos buscar nome no IBGE
        from app.services.ibge_api import IBGEService
        try:
            ibge_svc = IBGEService()
            primeiro_nome = (enriched.get("target_name") or investigation.target_name or "").split()[0]
            if primeiro_nome and len(primeiro_nome) >= 2:
                nome_data = await ibge_svc.nomes(primeiro_nome)
                if nome_data and isinstance(nome_data, list) and len(nome_data) > 0:
                    freq = nome_data[0].get("res", [])
                    if freq:
                        total = sum(r.get("frequencia", 0) for r in freq if isinstance(r, dict))
                        if total > 0:
                            description_parts.append(f"IBGE: Nome '{primeiro_nome}' — {total:,} registros no Brasil")
        except Exception:
            pass

    elif len(doc) == 14:
        # --- CNPJ ---
        from app.services.receita_cnpj import ReceitaCNPJService
        try:
            cnpj_svc = ReceitaCNPJService()
            cnpj_data = await cnpj_svc.consultar(doc)
            if cnpj_data.get("razao_social"):
                enriched["target_name"] = cnpj_data["razao_social"]
            parts = []
            if cnpj_data.get("nome_fantasia"):
                parts.append(f"Fantasia: {cnpj_data['nome_fantasia']}")
            if cnpj_data.get("situacao_cadastral"):
                parts.append(f"Situação: {cnpj_data['situacao_cadastral']}")
            if cnpj_data.get("abertura_data"):
                parts.append(f"Abertura: {cnpj_data['abertura_data']}")
            if cnpj_data.get("natureza_juridica"):
                parts.append(f"Natureza: {cnpj_data['natureza_juridica']}")
            if cnpj_data.get("porte"):
                parts.append(f"Porte: {cnpj_data['porte']}")
            if cnpj_data.get("capital_social"):
                cap = cnpj_data["capital_social"]
                if isinstance(cap, (int, float)):
                    parts.append(f"Capital: R$ {cap:,.2f}")
                else:
                    parts.append(f"Capital: {cap}")
            atividade = cnpj_data.get("atividade_economica")
            if isinstance(atividade, dict) and atividade.get("descricao"):
                parts.append(f"CNAE: {atividade['descricao']}")
            endereco = cnpj_data.get("endereco")
            if isinstance(endereco, dict):
                end_parts = [endereco.get("logradouro"), endereco.get("numero"),
                             endereco.get("bairro"), endereco.get("municipio"),
                             endereco.get("uf")]
                end_str = ", ".join(p for p in end_parts if p)
                if end_str:
                    parts.append(f"Endereço: {end_str}")
            qsa = cnpj_data.get("qsa")
            if isinstance(qsa, list) and len(qsa) > 0:
                socios = [s.get("nome") for s in qsa[:5] if s.get("nome")]
                if socios:
                    parts.append(f"Sócios: {'; '.join(socios)}")
            if cnpj_data.get("telefone"):
                parts.append(f"Tel: {cnpj_data['telefone']}")
            if cnpj_data.get("email"):
                parts.append(f"Email: {cnpj_data['email']}")
            if parts:
                description_parts.append("Receita Federal: " + " | ".join(parts))
            if cnpj_data.get("fonte"):
                description_parts.append(f"Fonte: {cnpj_data['fonte']}")
        except Exception:
            pass

    # Montar descrição enriquecida
    if description_parts:
        existing_desc = investigation.target_description or ""
        new_desc = "\n".join(description_parts)
        if existing_desc:
            enriched["target_description"] = existing_desc + "\n\n--- Dados Enriquecidos ---\n" + new_desc
        else:
            enriched["target_description"] = new_desc

    if not enriched:
        # Retorna a investigação sem alterações (parcial) em vez de 404
        return InvestigationResponse.model_validate(investigation)

    # Não sobrescrever nome se já tem um nome real (não auto-gerado)
    current_name = investigation.target_name or ""
    is_auto_name = current_name.startswith("Investigação ") and any(c.isdigit() for c in current_name)
    if enriched.get("target_name") and (is_auto_name or not current_name.strip()):
        pass  # Manter o nome enriquecido
    else:
        enriched.pop("target_name", None)

    updated = await investigation_service.update_investigation(
        investigation_id,
        current_user.id,
        InvestigationUpdate(**enriched),
        current_user.is_superuser,
    )

    return InvestigationResponse.model_validate(updated)


@router.get("/{investigation_id}/properties", response_model=List[PropertyResponse])
async def get_investigation_properties(
    investigation_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> List[PropertyResponse]:
    """Get properties found in investigation"""
    investigation_repo = InvestigationRepository(db)
    investigation_service = InvestigationService(investigation_repo)
    
    investigation = await investigation_service.get_investigation(
        investigation_id, current_user.id, current_user.is_superuser
    )
    
    return [PropertyResponse.model_validate(prop) for prop in investigation.properties]


@router.get("/{investigation_id}/lease-contracts", response_model=List[LeaseContractResponse])
async def get_investigation_lease_contracts(
    investigation_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> List[LeaseContractResponse]:
    """Get lease contracts found in investigation"""
    investigation_repo = InvestigationRepository(db)
    investigation_service = InvestigationService(investigation_repo)
    
    investigation = await investigation_service.get_investigation(
        investigation_id, current_user.id, current_user.is_superuser
    )
    
    return [LeaseContractResponse.model_validate(lc) for lc in investigation.lease_contracts]


@router.get("/{investigation_id}/companies", response_model=List[CompanyResponse])
async def get_investigation_companies(
    investigation_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> List[CompanyResponse]:
    """Get companies found in investigation"""
    investigation_repo = InvestigationRepository(db)
    investigation_service = InvestigationService(investigation_repo)
    
    investigation = await investigation_service.get_investigation(
        investigation_id, current_user.id, current_user.is_superuser
    )
    
    return [CompanyResponse.model_validate(company) for company in investigation.companies]


@router.get("/{investigation_id}/export/excel")
async def export_investigation_excel(
    investigation_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> StreamingResponse:
    """
    Export investigation data to Excel file (.xlsx)
    
    Generates a multi-sheet Excel workbook with:
    - Resumo: Investigation summary and overview
    - Propriedades: Properties found
    - Empresas: Companies found
    - Consultas Legais: Legal queries executed
    """
    investigation_repo = InvestigationRepository(db)
    investigation_service = InvestigationService(investigation_repo)
    legal_query_repo = LegalQueryRepository(db)
    
    # Get investigation with all relations loaded
    investigation = await investigation_repo.get_with_relations(investigation_id)
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Verify access
    if investigation.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to access this investigation")
    
    # Get legal queries separately
    legal_queries = await legal_query_repo.list_by_investigation(investigation_id)
    
    # Generate Excel file
    excel_file = ExcelExportService.generate_investigation_excel(
        investigation, investigation.properties, investigation.companies, legal_queries
    )
    
    # Prepare filename
    filename = f"investigacao_{investigation.id}_{investigation.target_name.replace(' ', '_')}_{investigation.created_at.strftime('%Y%m%d')}.xlsx"
    
    # Return as streaming response
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )


@router.get("/{investigation_id}/export/csv")
async def export_investigation_csv(
    investigation_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> StreamingResponse:
    """
    Export investigation summary data to CSV file
    
    Generates a CSV file with main investigation data including:
    - Investigation details (name, CPF/CNPJ, status)
    - Summary counts (properties, companies, legal queries)
    - Dates (created, updated)
    """
    investigation_repo = InvestigationRepository(db)
    legal_query_repo = LegalQueryRepository(db)
    
    # Get investigation with all relations loaded
    investigation = await investigation_repo.get_with_relations(investigation_id)
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Verify access
    if investigation.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to access this investigation")
    
    # Get legal queries separately
    legal_queries = await legal_query_repo.list_by_investigation(investigation_id)
    
    # Generate CSV file
    csv_file = ExcelExportService.generate_investigation_csv(
        investigation, investigation.properties, investigation.companies, legal_queries
    )
    
    # Prepare filename
    filename = f"investigacao_{investigation.id}_{investigation.target_name.replace(' ', '_')}_{investigation.created_at.strftime('%Y%m%d')}.csv"
    
    # Return as streaming response
    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )


@router.get("/{investigation_id}/export/pdf")
async def export_investigation_pdf(
    investigation_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> StreamingResponse:
    """
    Export investigation to professional PDF report
    
    Generates a comprehensive PDF report with:
    - Professional cover page with logo
    - Table of contents
    - Executive summary with key statistics
    - Investigation details
    - Properties found
    - Companies found
    - Legal queries performed
    - Visual charts and analysis
    """
    investigation_repo = InvestigationRepository(db)
    legal_query_repo = LegalQueryRepository(db)
    
    # Get investigation with all relations loaded
    investigation = await investigation_repo.get_with_relations(investigation_id)
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Verify access
    if investigation.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to access this investigation")
    
    # Get related data (already loaded from get_with_relations)
    properties = investigation.properties or []
    companies = investigation.companies or []
    
    # Get legal queries for this investigation
    legal_queries = await legal_query_repo.find_by_investigation(investigation_id)
    
    # Convert to dictionaries for PDF generation
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
    
    # Generate PDF
    pdf_service = PDFExportService()
    pdf_buffer = pdf_service.generate_investigation_pdf(
        investigation_dict, properties_list, companies_list, legal_queries_list
    )
    
    # Prepare filename
    target_name = investigation.target_name.replace(" ", "_") if investigation.target_name else "investigacao"
    created_date = investigation.created_at.strftime("%Y%m%d") if investigation.created_at else "sem_data"
    filename = f"relatorio_{investigation.id}_{target_name}_{created_date}.pdf"
    
    # Audit log
    await audit_logger.log(
        db=db,
        action=AuditAction.INVESTIGATION_EXPORTED,
        user_id=current_user.id,
        username=current_user.username,
        resource_type="investigation",
        resource_id=str(investigation_id),
        details={"export_format": "pdf", "filename": filename},
        ip_address=None,
        user_agent=None,
        method="GET",
        endpoint=f"/investigations/{investigation_id}/export/pdf",
    )
    
    # Return as streaming response
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )

