"""
Configuração de Testes - conftest.py Isolado
=============================================

Este arquivo fornece fixtures para testes sem depender de configurações
completas do sistema.
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    """Mock completo do banco de dados SQLAlchemy"""
    db = Mock(spec=Session)
    
    # Mock métodos comuns
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    db.delete = Mock()
    db.rollback = Mock()
    db.close = Mock()
    db.flush = Mock()
    db.execute = Mock()
    
    # Mock query builder
    query_mock = Mock()
    query_mock.filter = Mock(return_value=query_mock)
    query_mock.filter_by = Mock(return_value=query_mock)
    query_mock.join = Mock(return_value=query_mock)
    query_mock.group_by = Mock(return_value=query_mock)
    query_mock.order_by = Mock(return_value=query_mock)
    query_mock.limit = Mock(return_value=query_mock)
    query_mock.offset = Mock(return_value=query_mock)
    query_mock.all = Mock(return_value=[])
    query_mock.first = Mock(return_value=None)
    query_mock.scalar = Mock(return_value=0)
    query_mock.count = Mock(return_value=0)
    
    db.query.return_value = query_mock
    
    return db


@pytest.fixture
def sample_date_range():
    """Datas de exemplo para testes"""
    from datetime import datetime, timedelta
    return {
        "start_date": datetime.utcnow() - timedelta(days=30),
        "end_date": datetime.utcnow()
    }


@pytest.fixture
def mock_investigation():
    """Mock de uma investigação"""
    from datetime import datetime
    
    inv = Mock()
    inv.id = 1
    inv.title = "Test Investigation"
    inv.description = "Test description"
    inv.status = "in_progress"
    inv.priority = "high"
    inv.category = "arrendamento"
    inv.created_at = datetime.utcnow()
    inv.updated_at = datetime.utcnow()
    inv.completed_at = None
    inv.created_by_id = 1
    
    return inv


@pytest.fixture
def mock_user():
    """Mock de um usuário"""
    from datetime import datetime
    
    user = Mock()
    user.id = 1
    user.name = "Test User"
    user.email = "test@test.com"
    user.role = "admin"
    user.is_active = True
    user.created_at = datetime.utcnow()
    user.last_login = datetime.utcnow()
    
    return user


@pytest.fixture
def mock_httpx_client():
    """Mock do cliente httpx"""
    import httpx
    
    client = Mock(spec=httpx.AsyncClient)
    
    # Mock métodos HTTP
    client.get = Mock()
    client.post = Mock()
    client.put = Mock()
    client.delete = Mock()
    client.aclose = Mock()
    
    return client
