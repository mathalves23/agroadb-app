"""
Sistema de Paginação Cursor-Based
Implementa paginação eficiente para listas grandes
"""
from typing import Optional, List, TypeVar, Generic, Callable, Any
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import select, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
import base64
import json

T = TypeVar('T')


class CursorPage(BaseModel):
    """
    Modelo de resposta paginada com cursor
    
    Attributes:
        items: Lista de itens da página
        next_cursor: Cursor para próxima página (None se última)
        previous_cursor: Cursor para página anterior (None se primeira)
        has_next: Se existe próxima página
        has_previous: Se existe página anterior
        total_count: Total de itens (opcional, pode ser custoso)
    """
    model_config = {"arbitrary_types_allowed": True}
    
    items: List[Any]
    next_cursor: Optional[str] = None
    previous_cursor: Optional[str] = None
    has_next: bool = False
    has_previous: bool = False
    total_count: Optional[int] = None
    page_size: int


class CursorPagination:
    """
    Sistema de Paginação Cursor-Based
    
    Mais eficiente que offset-based para listas grandes
    """
    
    @staticmethod
    def encode_cursor(value: Any) -> str:
        """
        Codifica valor em cursor base64
        
        Args:
            value: Valor a codificar (datetime, int, str)
            
        Returns:
            Cursor codificado
        """
        if isinstance(value, datetime):
            value = value.isoformat()
        
        cursor_data = json.dumps({'v': value})
        return base64.b64encode(cursor_data.encode()).decode()
    
    @staticmethod
    def decode_cursor(cursor: str) -> Any:
        """
        Decodifica cursor base64
        
        Args:
            cursor: Cursor codificado
            
        Returns:
            Valor decodificado
        """
        try:
            cursor_data = base64.b64decode(cursor.encode()).decode()
            data = json.loads(cursor_data)
            value = data['v']
            
            # Tentar converter para datetime se for ISO string
            try:
                return datetime.fromisoformat(value)
            except:
                return value
                
        except Exception:
            return None
    
    @staticmethod
    async def paginate(
        db: AsyncSession,
        query,
        cursor_column,
        cursor: Optional[str] = None,
        limit: int = 20,
        direction: str = 'forward',
        order: str = 'desc',
        include_total: bool = False
    ) -> CursorPage:
        """
        Pagina query usando cursor
        
        Args:
            db: Sessão do banco
            query: Query SQLAlchemy
            cursor_column: Coluna usada como cursor (ex: created_at, id)
            cursor: Cursor atual (None para primeira página)
            limit: Número de itens por página
            direction: 'forward' ou 'backward'
            order: 'desc' ou 'asc'
            include_total: Se deve incluir contagem total (custoso!)
            
        Returns:
            CursorPage com resultados
        """
        # Decodificar cursor
        cursor_value = None
        if cursor:
            cursor_value = CursorPagination.decode_cursor(cursor)
        
        # Aplicar filtro do cursor
        if cursor_value:
            if direction == 'forward':
                if order == 'desc':
                    query = query.where(cursor_column < cursor_value)
                else:
                    query = query.where(cursor_column > cursor_value)
            else:  # backward
                if order == 'desc':
                    query = query.where(cursor_column > cursor_value)
                else:
                    query = query.where(cursor_column < cursor_value)
        
        # Ordenar
        if order == 'desc':
            query = query.order_by(desc(cursor_column))
        else:
            query = query.order_by(asc(cursor_column))
        
        # Buscar limit + 1 para saber se tem próxima página
        query = query.limit(limit + 1)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        # Verificar se tem próxima página
        has_more = len(items) > limit
        if has_more:
            items = items[:limit]
        
        # Gerar cursors
        next_cursor = None
        previous_cursor = None
        
        if items:
            if direction == 'forward':
                has_next = has_more
                has_previous = cursor is not None
                
                if has_next:
                    last_item = items[-1]
                    next_value = getattr(last_item, cursor_column.key)
                    next_cursor = CursorPagination.encode_cursor(next_value)
                
                if has_previous:
                    first_item = items[0]
                    prev_value = getattr(first_item, cursor_column.key)
                    previous_cursor = CursorPagination.encode_cursor(prev_value)
            else:
                has_next = cursor is not None
                has_previous = has_more
                
                if has_next:
                    first_item = items[0]
                    next_value = getattr(first_item, cursor_column.key)
                    next_cursor = CursorPagination.encode_cursor(next_value)
                
                if has_previous:
                    last_item = items[-1]
                    prev_value = getattr(last_item, cursor_column.key)
                    previous_cursor = CursorPagination.encode_cursor(prev_value)
                
                # Reverter ordem dos itens
                items = list(reversed(items))
        else:
            has_next = False
            has_previous = False
        
        # Contagem total (opcional, custoso!)
        total_count = None
        if include_total:
            count_query = select(func.count()).select_from(query.froms[0])
            count_result = await db.execute(count_query)
            total_count = count_result.scalar()
        
        return CursorPage(
            items=[item.to_dict() if hasattr(item, 'to_dict') else item for item in items],
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            has_next=has_next,
            has_previous=has_previous,
            total_count=total_count,
            page_size=len(items)
        )


# Helper function para simplificar uso
async def cursor_paginate(
    db: AsyncSession,
    model,
    cursor: Optional[str] = None,
    limit: int = 20,
    order_by: str = 'created_at',
    order: str = 'desc',
    filters: Optional[dict] = None
) -> CursorPage:
    """
    Helper function para paginar modelo
    
    Args:
        db: Sessão do banco
        model: Modelo SQLAlchemy
        cursor: Cursor atual
        limit: Itens por página
        order_by: Nome da coluna para ordenar
        order: 'desc' ou 'asc'
        filters: Filtros adicionais (dict)
        
    Returns:
        CursorPage com resultados
        
    Example:
        # Em um endpoint:
        @router.get("/investigations")
        async def list_investigations(
            cursor: Optional[str] = None,
            limit: int = 20,
            db = Depends(get_db)
        ):
            return await cursor_paginate(
                db,
                Investigation,
                cursor=cursor,
                limit=limit,
                order_by='created_at'
            )
    """
    from sqlalchemy import select
    
    query = select(model)
    
    # Aplicar filtros
    if filters:
        for key, value in filters.items():
            if hasattr(model, key):
                query = query.where(getattr(model, key) == value)
    
    # Obter coluna de cursor
    cursor_column = getattr(model, order_by)
    
    return await CursorPagination.paginate(
        db,
        query,
        cursor_column,
        cursor=cursor,
        limit=limit,
        order=order
    )


# Exemplo de resposta
"""
{
  "items": [
    { "id": 1, "name": "Investigation 1", "created_at": "2026-02-05T10:00:00" },
    { "id": 2, "name": "Investigation 2", "created_at": "2026-02-04T15:30:00" },
    ...
  ],
  "next_cursor": "eyJ2IjogIjIwMjYtMDItMDRUMTU6MzA6MDAifQ==",
  "previous_cursor": null,
  "has_next": true,
  "has_previous": false,
  "total_count": null,
  "page_size": 20
}

# Para próxima página:
GET /investigations?cursor=eyJ2IjogIjIwMjYtMDItMDRUMTU6MzA6MDAifQ==&limit=20
"""
