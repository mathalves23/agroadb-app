"""
Investigation Repository
"""
from typing import List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.investigation import Investigation, InvestigationStatus
from app.repositories.base import BaseRepository


class InvestigationRepository(BaseRepository[Investigation]):
    """Repository for Investigation model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Investigation, db)
    
    async def get_with_relations(self, id: int) -> Investigation | None:
        """Get investigation with all relations loaded"""
        result = await self.db.execute(
            select(Investigation)
            .where(Investigation.id == id)
            .options(
                selectinload(Investigation.properties),
                selectinload(Investigation.lease_contracts),
                selectinload(Investigation.companies),
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Investigation]:
        """Get investigations by user"""
        result = await self.db.execute(
            select(Investigation)
            .where(Investigation.user_id == user_id)
            .order_by(desc(Investigation.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_by_user(self, user_id: int) -> int:
        """Count investigations by user"""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count(Investigation.id)).where(Investigation.user_id == user_id)
        )
        return result.scalar_one()
    
    async def get_pending(self) -> List[Investigation]:
        """Get all pending investigations"""
        result = await self.db.execute(
            select(Investigation)
            .where(Investigation.status == InvestigationStatus.PENDING)
            .order_by(desc(Investigation.priority), Investigation.created_at)
        )
        return list(result.scalars().all())
