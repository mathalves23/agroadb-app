"""
Repository for LegalQuery
"""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.investigation import Investigation
from app.domain.legal_query import LegalQuery


class LegalQueryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, obj_in: dict) -> LegalQuery:
        db_obj = LegalQuery(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def list_by_investigation(self, investigation_id: int) -> List[LegalQuery]:
        result = await self.db.execute(
            select(LegalQuery)
            .where(LegalQuery.investigation_id == investigation_id)
            .order_by(LegalQuery.created_at.desc())
        )
        return list(result.scalars().all())

    async def summary_by_user(self, user_id: int) -> dict:
        result = await self.db.execute(
            select(
                LegalQuery.provider,
                func.sum(LegalQuery.result_count).label("total"),
                func.count(LegalQuery.id).label("queries"),
            )
            .join(Investigation, LegalQuery.investigation_id == Investigation.id)
            .where(Investigation.user_id == user_id)
            .group_by(LegalQuery.provider)
        )
        rows = result.all()
        summary = {row.provider: {"total": int(row.total or 0), "queries": int(row.queries or 0)} for row in rows}
        return summary
