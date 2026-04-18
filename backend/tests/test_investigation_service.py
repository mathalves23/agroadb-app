"""
Testes do InvestigationService (async, repositório real em SQLite em memória).

O serviço legado síncrono (`db=Session`) foi substituído por `InvestigationRepository`
+ métodos async; o fallback de scrapers é isolado com mock para não aceder à rede.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.security import get_password_hash
from app.domain.investigation import InvestigationStatus
from app.domain.user import User
from app.repositories.investigation import InvestigationRepository
from app.schemas.investigation import InvestigationCreate, InvestigationUpdate
from app.services.investigation import InvestigationService

VALID_CNPJ = "11222333000181"


@pytest.fixture
async def investigation_user(db_session):
    u = User(
        email="svc-inv@example.com",
        username="svcinv",
        full_name="Inv User",
        hashed_password=get_password_hash("pass12345"),
        is_active=True,
    )
    db_session.add(u)
    await db_session.flush()
    await db_session.refresh(u)
    return u


def _make_service(db_session) -> InvestigationService:
    return InvestigationService(InvestigationRepository(db_session))


@pytest.mark.asyncio
@patch.object(InvestigationService, "_run_sync_fallback", new_callable=AsyncMock)
async def test_create_investigation(mock_fallback, db_session, investigation_user):
    svc = _make_service(db_session)
    payload = InvestigationCreate(
        target_name="Fazenda Teste",
        target_cpf_cnpj=VALID_CNPJ,
        target_description="Descrição",
        priority=1,
    )
    inv = await svc.create_investigation(investigation_user.id, payload)
    assert inv.id is not None
    assert inv.target_name == "Fazenda Teste"
    assert inv.user_id == investigation_user.id
    assert inv.status == InvestigationStatus.PENDING
    mock_fallback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_investigation_not_found(db_session, investigation_user):
    svc = _make_service(db_session)
    with pytest.raises(HTTPException) as exc:
        await svc.get_investigation(999_999, investigation_user.id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
@patch.object(InvestigationService, "_run_sync_fallback", new_callable=AsyncMock)
async def test_get_investigation_success(mock_fallback, db_session, investigation_user):
    svc = _make_service(db_session)
    created = await svc.create_investigation(
        investigation_user.id,
        InvestigationCreate(target_name="Alvo", target_cpf_cnpj=VALID_CNPJ, priority=2),
    )
    got = await svc.get_investigation(created.id, investigation_user.id)
    assert got.id == created.id
    assert got.target_name == "Alvo"


@pytest.mark.asyncio
@patch.object(InvestigationService, "_run_sync_fallback", new_callable=AsyncMock)
async def test_list_investigations(mock_fallback, db_session, investigation_user):
    svc = _make_service(db_session)
    for i in range(3):
        await svc.create_investigation(
            investigation_user.id,
            InvestigationCreate(
                target_name=f"Inv {i}",
                target_cpf_cnpj=VALID_CNPJ,
                priority=1,
            ),
        )
    items, total = await svc.list_investigations(investigation_user.id, skip=0, limit=10)
    assert total == 3
    assert len(items) == 3
    assert all(x.user_id == investigation_user.id for x in items)


@pytest.mark.asyncio
@patch.object(InvestigationService, "_run_sync_fallback", new_callable=AsyncMock)
async def test_update_investigation(mock_fallback, db_session, investigation_user):
    svc = _make_service(db_session)
    inv = await svc.create_investigation(
        investigation_user.id,
        InvestigationCreate(target_name="Original", target_cpf_cnpj=VALID_CNPJ, priority=1),
    )
    updated = await svc.update_investigation(
        inv.id,
        investigation_user.id,
        InvestigationUpdate(target_name="Atualizado", priority=3),
    )
    assert updated.target_name == "Atualizado"
    assert updated.priority == 3


@pytest.mark.asyncio
@patch.object(InvestigationService, "_run_sync_fallback", new_callable=AsyncMock)
async def test_delete_investigation(mock_fallback, db_session, investigation_user):
    svc = _make_service(db_session)
    inv = await svc.create_investigation(
        investigation_user.id,
        InvestigationCreate(target_name="Apagar", target_cpf_cnpj=VALID_CNPJ, priority=1),
    )
    ok = await svc.delete_investigation(inv.id, investigation_user.id)
    assert ok is True
    with pytest.raises(HTTPException):
        await svc.get_investigation(inv.id, investigation_user.id)


def test_investigation_create_schema_rejects_invalid_cnpj():
    with pytest.raises(ValidationError):
        InvestigationCreate(
            target_name="X",
            target_cpf_cnpj="123",
            priority=1,
        )


def test_investigation_create_schema_rejects_empty_name():
    with pytest.raises(ValidationError):
        InvestigationCreate(
            target_name="",
            target_cpf_cnpj=VALID_CNPJ,
            priority=1,
        )
