"""
Testes do Sistema de WebSocket
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import WebSocket

from app.core.websocket import (
    ConnectionManager,
    notify_task_started,
    notify_task_completed,
    notify_task_failed,
    notify_investigation_progress
)
from app.core.queue import TaskStatus, ScraperType


@pytest.fixture
def connection_manager():
    """Fixture do gerenciador de conexões"""
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    """Fixture de WebSocket mockado"""
    ws = MagicMock(spec=WebSocket)
    ws.send_json = AsyncMock()
    ws.accept = AsyncMock()
    ws.receive_text = AsyncMock()
    return ws


# ==================== Testes de Conexão ====================


@pytest.mark.asyncio
async def test_connect_websocket(connection_manager, mock_websocket):
    """Testa conexão de WebSocket"""
    await connection_manager.connect(mock_websocket, "inv_123", "user_456")
    
    # Verificar que aceito foi chamado
    mock_websocket.accept.assert_called_once()
    
    # Verificar que foi adicionado às conexões ativas
    assert "inv_123" in connection_manager.active_connections
    assert mock_websocket in connection_manager.active_connections["inv_123"]
    
    # Verificar rastreamento de usuário
    assert connection_manager.websocket_users[mock_websocket] == "user_456"


@pytest.mark.asyncio
async def test_disconnect_websocket(connection_manager, mock_websocket):
    """Testa desconexão de WebSocket"""
    await connection_manager.connect(mock_websocket, "inv_123", "user_456")
    connection_manager.disconnect(mock_websocket, "inv_123")
    
    # Verificar que foi removido
    assert mock_websocket not in connection_manager.active_connections.get("inv_123", set())
    assert mock_websocket not in connection_manager.websocket_users


@pytest.mark.asyncio
async def test_multiple_connections_same_investigation(connection_manager):
    """Testa múltiplas conexões na mesma investigação"""
    ws1 = MagicMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()
    
    ws2 = MagicMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()
    
    await connection_manager.connect(ws1, "inv_123", "user_1")
    await connection_manager.connect(ws2, "inv_123", "user_2")
    
    # Verificar que ambas estão conectadas
    assert len(connection_manager.active_connections["inv_123"]) == 2
    assert connection_manager.get_connection_count("inv_123") == 2


# ==================== Testes de Envio de Mensagens ====================


@pytest.mark.asyncio
async def test_send_personal_message(connection_manager, mock_websocket):
    """Testa envio de mensagem pessoal"""
    await connection_manager.connect(mock_websocket, "inv_123", "user_456")
    
    message = {"type": "test", "data": "hello"}
    await connection_manager.send_personal_message(message, mock_websocket)
    
    # Verificar que send_json foi chamado
    mock_websocket.send_json.assert_called_with(message)


@pytest.mark.asyncio
async def test_broadcast_to_investigation(connection_manager):
    """Testa broadcast para investigação"""
    ws1 = MagicMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()
    
    ws2 = MagicMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()
    
    await connection_manager.connect(ws1, "inv_123", "user_1")
    await connection_manager.connect(ws2, "inv_123", "user_2")
    
    message = {"type": "broadcast", "data": "test"}
    await connection_manager.broadcast_to_investigation(message, "inv_123")
    
    # Verificar que ambos receberam
    ws1.send_json.assert_called_with(message)
    ws2.send_json.assert_called_with(message)


@pytest.mark.asyncio
async def test_broadcast_to_all(connection_manager):
    """Testa broadcast para todas as investigações"""
    ws1 = MagicMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()
    
    ws2 = MagicMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()
    
    await connection_manager.connect(ws1, "inv_123", "user_1")
    await connection_manager.connect(ws2, "inv_456", "user_2")
    
    message = {"type": "system_alert", "message": "test"}
    await connection_manager.broadcast_to_all(message)
    
    # Verificar que ambos receberam
    ws1.send_json.assert_called_with(message)
    ws2.send_json.assert_called_with(message)


@pytest.mark.asyncio
async def test_broadcast_handles_dead_connections(connection_manager):
    """Testa que broadcast remove conexões mortas"""
    ws_dead = MagicMock(spec=WebSocket)
    ws_dead.accept = AsyncMock()
    ws_dead.send_json = AsyncMock(side_effect=Exception("Connection closed"))
    
    ws_alive = MagicMock(spec=WebSocket)
    ws_alive.accept = AsyncMock()
    ws_alive.send_json = AsyncMock()
    
    await connection_manager.connect(ws_dead, "inv_123", "user_1")
    await connection_manager.connect(ws_alive, "inv_123", "user_2")
    
    message = {"type": "test"}
    await connection_manager.broadcast_to_investigation(message, "inv_123")
    
    # Verificar que conexão morta foi removida
    assert ws_dead not in connection_manager.active_connections["inv_123"]
    assert ws_alive in connection_manager.active_connections["inv_123"]


# ==================== Testes de Estatísticas ====================


@pytest.mark.asyncio
async def test_get_connection_count(connection_manager):
    """Testa contagem de conexões"""
    ws1 = MagicMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()
    
    ws2 = MagicMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()
    
    await connection_manager.connect(ws1, "inv_123", "user_1")
    await connection_manager.connect(ws2, "inv_456", "user_2")
    
    # Total
    assert connection_manager.get_connection_count() == 2
    
    # Por investigação
    assert connection_manager.get_connection_count("inv_123") == 1
    assert connection_manager.get_connection_count("inv_456") == 1


@pytest.mark.asyncio
async def test_get_stats(connection_manager):
    """Testa obtenção de estatísticas"""
    ws1 = MagicMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()
    
    ws2 = MagicMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()
    
    ws3 = MagicMock(spec=WebSocket)
    ws3.accept = AsyncMock()
    ws3.send_json = AsyncMock()
    
    await connection_manager.connect(ws1, "inv_123", "user_1")
    await connection_manager.connect(ws2, "inv_123", "user_2")
    await connection_manager.connect(ws3, "inv_456", "user_3")
    
    stats = connection_manager.get_stats()
    
    assert stats["total_connections"] == 3
    assert stats["active_investigations"] == 2
    assert stats["connections_by_investigation"]["inv_123"] == 2
    assert stats["connections_by_investigation"]["inv_456"] == 1


# ==================== Testes de Funções de Notificação ====================


@pytest.mark.asyncio
async def test_notify_task_started(connection_manager, mock_websocket):
    """Testa notificação de início de task"""
    await connection_manager.connect(mock_websocket, "inv_123", "user_456")
    
    await notify_task_started("inv_123", "task_abc", ScraperType.CAR)
    
    # Verificar que mensagem foi enviada
    assert mock_websocket.send_json.call_count >= 1
    
    # Verificar conteúdo da última mensagem
    last_call = mock_websocket.send_json.call_args_list[-1]
    message = last_call[0][0]
    
    assert message["type"] == "task_started"
    assert message["task_id"] == "task_abc"
    assert message["scraper_type"] == "car"


@pytest.mark.asyncio
async def test_notify_task_completed(connection_manager, mock_websocket):
    """Testa notificação de conclusão de task"""
    await connection_manager.connect(mock_websocket, "inv_123", "user_456")
    
    result = {"data": "success"}
    await notify_task_completed("inv_123", "task_abc", ScraperType.CAR, result)
    
    # Verificar mensagem
    last_call = mock_websocket.send_json.call_args_list[-1]
    message = last_call[0][0]
    
    assert message["type"] == "task_completed"
    assert message["result"] == result


@pytest.mark.asyncio
async def test_notify_task_failed(connection_manager, mock_websocket):
    """Testa notificação de falha de task"""
    await connection_manager.connect(mock_websocket, "inv_123", "user_456")
    
    await notify_task_failed(
        "inv_123",
        "task_abc",
        ScraperType.CAR,
        "Test error",
        retry_count=1,
        max_retries=3
    )
    
    # Verificar mensagem
    last_call = mock_websocket.send_json.call_args_list[-1]
    message = last_call[0][0]
    
    assert message["type"] == "task_retrying"
    assert message["error"] == "Test error"
    assert message["retry_count"] == 1
    assert message["will_retry"] is True


@pytest.mark.asyncio
async def test_notify_investigation_progress(connection_manager, mock_websocket):
    """Testa notificação de progresso"""
    await connection_manager.connect(mock_websocket, "inv_123", "user_456")
    
    progress = {
        "total_tasks": 6,
        "completed_tasks": 3,
        "failed_tasks": 1,
        "running_tasks": 1
    }
    
    await notify_investigation_progress("inv_123", progress)
    
    # Verificar mensagem
    last_call = mock_websocket.send_json.call_args_list[-1]
    message = last_call[0][0]
    
    assert message["type"] == "investigation_progress"
    assert message["total_tasks"] == 6
    assert message["completed_tasks"] == 3
    assert message["percentage"] == 66.67


# ==================== Testes de Isolamento ====================


@pytest.mark.asyncio
async def test_broadcast_only_to_correct_investigation(connection_manager):
    """Testa que broadcast vai apenas para investigação correta"""
    ws1 = MagicMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()
    
    ws2 = MagicMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()
    
    await connection_manager.connect(ws1, "inv_123", "user_1")
    await connection_manager.connect(ws2, "inv_456", "user_2")
    
    message = {"type": "test"}
    await connection_manager.broadcast_to_investigation(message, "inv_123")
    
    # Verificar que apenas ws1 recebeu
    ws1.send_json.assert_called_once()
    ws2.send_json.assert_not_called()


@pytest.mark.asyncio
async def test_disconnect_one_doesnt_affect_others(connection_manager):
    """Testa que desconectar um não afeta outros"""
    ws1 = MagicMock(spec=WebSocket)
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()
    
    ws2 = MagicMock(spec=WebSocket)
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()
    
    await connection_manager.connect(ws1, "inv_123", "user_1")
    await connection_manager.connect(ws2, "inv_123", "user_2")
    
    # Desconectar ws1
    connection_manager.disconnect(ws1, "inv_123")
    
    # Verificar que ws2 ainda está conectado
    assert ws2 in connection_manager.active_connections["inv_123"]
    assert connection_manager.get_connection_count("inv_123") == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
