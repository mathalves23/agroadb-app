"""
Base Repository with common CRUD operations
"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID"""
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, *, skip: int = 0, limit: int = 100, order_by=None
    ) -> List[ModelType]:
        """Get multiple records with pagination"""
        query = select(self.model).offset(skip).limit(limit)
        
        if order_by is not None:
            query = query.order_by(order_by)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Count total records"""
        result = await self.db.execute(select(func.count(self.model.id)))
        return result.scalar_one()
    
    async def create(self, obj_in: dict) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        """Update an existing record"""
        db_obj = await self.get(id)
        if not db_obj:
            return None
        
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)
        
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: int) -> bool:
        """Delete a record"""
        db_obj = await self.get(id)
        if not db_obj:
            return False
        
        await self.db.delete(db_obj)
        await self.db.flush()
        return True
