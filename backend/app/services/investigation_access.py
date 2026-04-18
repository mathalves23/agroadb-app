"""
Regras de acesso a investigações partilhadas por vários routers (legal, exportações).

- Dono e superuser: acesso total.
- Utilizadores com partilha activa (Collaboration): conforme `PermissionLevel`.
- Exportações binárias (PDF, Excel, CSV, trust bundle): apenas dono ou superuser.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.collaboration import PermissionLevel
from app.repositories.investigation import InvestigationRepository
from app.services.collaboration import collaboration_service

if TYPE_CHECKING:
    from app.domain.investigation import Investigation


AccessOutcome = Literal["ok", "missing", "forbidden"]


def classify_investigation_access(
    investigation: Optional["Investigation"],
    user_id: int,
    *,
    is_superuser: bool,
) -> AccessOutcome:
    """Classifica acesso de **dono** sem I/O (útil para testes unitários)."""
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
    min_collaboration_permission: PermissionLevel = PermissionLevel.VIEW,
) -> "Investigation":
    """
    Garante que a investigação existe e que o utilizador pode aceder-lhe (dono, superuser ou partilha).

    when_forbidden:
      - "403": não autorizado recebe 403 (padrão das exportações em investigations).
      - "404_not_found": não autorizado recebe 404 com o mesmo detail que «não existe»
        (padrão actual do router legal, para não revelar existência).
    """
    repo = InvestigationRepository(db)
    if with_relations:
        investigation = await repo.get_with_relations(investigation_id)
    else:
        investigation = await repo.get(investigation_id)

    if investigation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail)

    if is_superuser:
        return investigation

    if investigation.user_id == user_id:
        return investigation

    if await collaboration_service.check_permission(
        db, investigation_id, user_id, min_collaboration_permission
    ):
        return investigation

    if when_forbidden == "404_not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=forbidden_detail)


async def require_investigation_owner_or_superuser(
    db: AsyncSession,
    investigation_id: int,
    user_id: int,
    *,
    is_superuser: bool,
    with_relations: bool = False,
    not_found_detail: str = "Investigation not found",
    forbidden_detail: str = "Only the investigation owner can download or export this dossier",
) -> "Investigation":
    """Exportações e pacotes de evidência: apenas dono (ou superuser), não convidados com partilha VIEW."""
    repo = InvestigationRepository(db)
    if with_relations:
        investigation = await repo.get_with_relations(investigation_id)
    else:
        investigation = await repo.get(investigation_id)

    if investigation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail)

    if is_superuser:
        return investigation

    if investigation.user_id == user_id:
        return investigation

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=forbidden_detail)


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
