"""Gestão de API keys e limite RPM por chave (Redis)."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from starlette.responses import Response
from pydantic import BaseModel, Field

from app.api.v1.deps import CurrentUser, DatabaseSession
from app.repositories.api_key import ApiKeyRepository
from app.services.api_key_cache import delete_api_key_rpm, set_api_key_rpm

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    rate_limit_rpm: int = Field(default=120, ge=5, le=10_000)


class ApiKeyCreatedResponse(BaseModel):
    id: int
    name: str
    plain_key: str
    rate_limit_rpm: int
    message: str = "Guarde a chave — não será mostrada novamente."


class ApiKeyListItem(BaseModel):
    id: int
    name: str
    rate_limit_rpm: int
    created_at: str
    revoked: bool


@router.post("", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    body: ApiKeyCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiKeyCreatedResponse:
    repo = ApiKeyRepository(db)
    row, plain = await repo.create(
        user_id=current_user.id,
        name=body.name,
        rate_limit_rpm=body.rate_limit_rpm,
    )
    await set_api_key_rpm(row.key_hash, row.rate_limit_rpm)
    return ApiKeyCreatedResponse(
        id=row.id,
        name=row.name,
        plain_key=plain,
        rate_limit_rpm=row.rate_limit_rpm,
    )


@router.get("", response_model=List[ApiKeyListItem])
async def list_api_keys(
    current_user: CurrentUser,
    db: DatabaseSession,
    include_revoked: bool = False,
) -> List[ApiKeyListItem]:
    repo = ApiKeyRepository(db)
    if include_revoked:
        rows = await repo.list_all(current_user.id)
    else:
        rows = await repo.list_active(current_user.id)
    out: List[ApiKeyListItem] = []
    for row in rows:
        out.append(
            ApiKeyListItem(
                id=row.id,
                name=row.name,
                rate_limit_rpm=row.rate_limit_rpm,
                created_at=row.created_at.isoformat(),
                revoked=row.revoked_at is not None,
            )
        )
    return out


@router.delete("/{api_key_id}")
async def revoke_api_key(
    api_key_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Response:
    repo = ApiKeyRepository(db)
    key_hash = await repo.revoke(current_user.id, api_key_id)
    if not key_hash:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chave não encontrada")
    await delete_api_key_rpm(key_hash)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
