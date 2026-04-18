"""
Regras de acesso a investigações partilhadas por vários routers (legal, exportações).

Centraliza o padrão «carregar investigação + validar dono ou superuser» para reduzir
duplicação entre `investigations` e `legal_integration`.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.investigation import InvestigationRepository

if TYPE_CHECKING:
    from app.domain.investigation import Investigation


AccessOutcome = Literal["ok", "missing", "forbidden"]


def classify_investigation_access(
    investigation: Optional["Investigation"],
    user_id: int,
    *,
    is_superuser: bool,
) -> AccessOutcome:
    """Classifica acesso sem I/O (útil para testes unitários)."""
    if investigation is None:
        return "missing"
    if not is_superuser and investigation.user_id != user_id:
        return "forbidden"
    return "ok"


async def require_investigation_for_user(
    db: AsyncSession,
    investigation_id: int,
    user_id: int,
    *,
    is_superuser: bool,
    with_relations: bool = False,
    when_forbidden: Literal["403", "404_not_found"] = "403",
    not_found_detail: str = "Investigation not found",
    forbidden_detail: str = "Not authorized to access this investigation",
) -> "Investigation":
    """
    Garante que a investigação existe e que o utilizador pode aceder-lhe.

    when_forbidden:
      - "403": não-dono recebe 403 (padrão das exportações em investigations).
      - "404_not_found": não-dono recebe 404 com o mesmo detail que «não existe»
        (padrão actual do router legal, para não revelar existência).
    """
    repo = InvestigationRepository(db)
    if with_relations:
        investigation = await repo.get_with_relations(investigation_id)
    else:
        investigation = await repo.get(investigation_id)

    outcome = classify_investigation_access(investigation, user_id, is_superuser=is_superuser)
    if outcome == "missing":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail)
    if outcome == "forbidden":
        if when_forbidden == "404_not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=forbidden_detail)
    assert investigation is not None
    return investigation


def legal_queries_to_public_list(queries: Sequence[Any]) -> list[dict[str, Any]]:
    """Forma canónica das consultas legais nas respostas JSON públicas."""
    return [
        {
            "id": q.id,
            "provider": q.provider,
            "query_type": q.query_type,
            "query_params": q.query_params,
            "result_count": q.result_count,
            "response": q.response,
            "created_at": q.created_at.isoformat(),
        }
        for q in queries
    ]
