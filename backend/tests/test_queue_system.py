"""
Testes Completos do Sistema de Filas e Workers
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.core.queue import (
    QueueManager,
    Task,
    TaskPriority,
    TaskStatus,
    ScraperType
)


@pytest.fixture
async def queue_manager():
    """Fixture do gerenciador de filas"""
    qm = QueueManager("redis://localhost:6379/1")  # DB 1 para testes
    await qm.connect()
    
    # Limpar todas as chaves de teste
    await qm.redis_client.flushdb()
    
    yield qm
    
    await qm.disconnect()


@pytest.fixture
def sample_task():
    """Fixture de task de exemplo"""
    return Task(
        id="test_task_123",
        type=ScraperType.CAR,
        priority=TaskPriority.NORMAL,
        investigation_id="inv_456",
        params={"name": "João Silva", "cpf_cnpj": "123.456.789-00"},
        max_retries=3
    )


# ==================== Testes de Task ====================


def test_task_creation(sample_task):
    """Testa criação de task"""
    assert sample_task.id == "test_task_123"
    assert sample_task.type == ScraperType.CAR
    assert sample_task.priority == TaskPriority.NORMAL
    assert sample_task.status == TaskStatus.PENDING
    assert sample_task.retry_count == 0
    assert sample_task.created_at is not None


def test_task_to_dict(sample_task):
    """Testa conversão de task para dict"""
    data = sample_task.to_dict()
    
    assert data["id"] == "test_task_123"
    assert data["type"] == "car"
    assert data["priority"] == 3
    assert data["status"] == "pending"
    assert "created_at" in data


def test_task_from_dict(sample_task):
    """Testa criação de task a partir de dict"""
    data = sample_task.to_dict()
    restored_task = Task.from_dict(data)
    
    assert restored_task.id == sample_task.id
    assert restored_task.type == sample_task.type
    assert restored_task.priority == sample_task.priority
    assert restored_task.status == sample_task.status


# ==================== Testes de Enfileiramento ====================


@pytest.mark.asyncio
async def test_enqueue_task(queue_manager, sample_task):
    """Testa enfileiramento de task"""
    success = await queue_manager.enqueue(sample_task)
    
    assert success is True
    
    # Verificar se task foi salva
    task_key = queue_manager._get_task_key(sample_task.id)
    task_data = await queue_manager.redis_client.get(task_key)
    
    assert task_data is not None
    
    # Verificar se foi adicionada à fila
    queue_key = queue_manager._get_queue_key(sample_task.type, sample_task.priority)
    queue_size = await queue_manager.redis_client.zcard(queue_key)
    
    assert queue_size == 1


@pytest.mark.asyncio
async def test_enqueue_multiple_priorities(queue_manager):
    """Testa enfileiramento com diferentes prioridades"""
    tasks = [
        Task(
            id=f"task_{i}",
            type=ScraperType.CAR,
            priority=priority,
            investigation_id="inv_123",
            params={}
        )
        for i, priority in enumerate(TaskPriority)
    ]
    
    for task in tasks:
        await queue_manager.enqueue(task)
    
    # Verificar estatísticas
    stats = await queue_manager.get_queue_stats(ScraperType.CAR)
    
    assert stats["car"]["total"] == 5
    assert stats["car"]["by_priority"]["CRITICAL"] == 1
    assert stats["car"]["by_priority"]["HIGH"] == 1
    assert stats["car"]["by_priority"]["NORMAL"] == 1


@pytest.mark.asyncio
async def test_dequeue_by_priority(queue_manager):
    """Testa desenfileiramento respeitando prioridade"""
    # Enfileirar tasks com diferentes prioridades
    low_task = Task(
        id="task_low",
        type=ScraperType.CAR,
        priority=TaskPriority.LOW,
        investigation_id="inv_123",
        params={}
    )
    
    high_task = Task(
        id="task_high",
        type=ScraperType.CAR,
        priority=TaskPriority.HIGH,
        investigation_id="inv_123",
        params={}
    )
    
    # Enfileirar primeiro a LOW
    await queue_manager.enqueue(low_task)
    await asyncio.sleep(0.1)  # Garantir timestamp diferente
    await queue_manager.enqueue(high_task)
    
    # Desenfileirar deve retornar a HIGH primeiro
    task = await queue_manager.dequeue(ScraperType.CAR)
    
    assert task is not None
    assert task.id == "task_high"
    assert task.status == TaskStatus.RUNNING


@pytest.mark.asyncio
async def test_dequeue_empty_queue(queue_manager):
    """Testa desenfileiramento de fila vazia"""
    task = await queue_manager.dequeue(ScraperType.CAR)
    
    assert task is None


# ==================== Testes de Conclusão e Falha ====================


@pytest.mark.asyncio
async def test_complete_task(queue_manager, sample_task):
    """Testa conclusão de task"""
    # Enfileirar e desenfileirar
    await queue_manager.enqueue(sample_task)
    task = await queue_manager.dequeue(ScraperType.CAR)
    
    # Completar
    result = {"data": "test_result"}
    success = await queue_manager.complete_task(task.id, result)
    
    assert success is True
    
    # Verificar task atualizada
    updated_task = await queue_manager.get_task(task.id)
    
    assert updated_task.status == TaskStatus.COMPLETED
    assert updated_task.result == result
    assert updated_task.completed_at is not None


@pytest.mark.asyncio
async def test_fail_task_with_retry(queue_manager, sample_task):
    """Testa falha de task com retry"""
    # Enfileirar e desenfileirar
    await queue_manager.enqueue(sample_task)
    task = await queue_manager.dequeue(ScraperType.CAR)
    
    # Falhar primeira vez
    will_retry = await queue_manager.fail_task(task.id, "Error de teste")
    
    assert will_retry is True
    
    # Verificar task
    updated_task = await queue_manager.get_task(task.id)
    
    assert updated_task.status == TaskStatus.RETRYING
    assert updated_task.retry_count == 1
    assert updated_task.error == "Error de teste"


@pytest.mark.asyncio
async def test_fail_task_max_retries(queue_manager, sample_task):
    """Testa falha definitiva após max retries"""
    sample_task.retry_count = 3  # Já no limite
    
    await queue_manager.enqueue(sample_task)
    task = await queue_manager.dequeue(ScraperType.CAR)
    
    # Falhar
    will_retry = await queue_manager.fail_task(task.id, "Final error")
    
    assert will_retry is False
    
    # Verificar task
    updated_task = await queue_manager.get_task(task.id)
    
    assert updated_task.status == TaskStatus.FAILED
    assert updated_task.retry_count == 4
    assert updated_task.completed_at is not None


# ==================== Testes de Retry ====================


@pytest.mark.asyncio
async def test_schedule_retry(queue_manager, sample_task):
    """Testa agendamento de retry"""
    await queue_manager.enqueue(sample_task)
    task = await queue_manager.dequeue(ScraperType.CAR)
    
    # Falhar (vai agendar retry)
    await queue_manager.fail_task(task.id, "Test error")
    
    # Verificar fila de retry
    retry_key = f"{queue_manager.QUEUE_PREFIX}retry"
    retry_count = await queue_manager.redis_client.zcard(retry_key)
    
    assert retry_count == 1


@pytest.mark.asyncio
async def test_process_retries(queue_manager, sample_task):
    """Testa processamento de retries"""
    await queue_manager.enqueue(sample_task)
    task = await queue_manager.dequeue(ScraperType.CAR)
    
    # Falhar
    await queue_manager.fail_task(task.id, "Test error")
    
    # Processar retries (não deve fazer nada pois delay não passou)
    await queue_manager.process_retries()
    
    # Verificar que task ainda está na fila de retry
    retry_key = f"{queue_manager.QUEUE_PREFIX}retry"
    retry_count = await queue_manager.redis_client.zcard(retry_key)
    
    assert retry_count == 1


# ==================== Testes de Circuit Breaker ====================


@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_failures(queue_manager):
    """Testa abertura do circuit breaker após falhas"""
    # Registrar falhas consecutivas
    for _ in range(5):
        await queue_manager._record_failure(ScraperType.CAR)
    
    # Verificar se circuit está aberto
    is_open = await queue_manager._is_circuit_open(ScraperType.CAR)
    
    assert is_open is True


@pytest.mark.asyncio
async def test_circuit_breaker_prevents_enqueue(queue_manager, sample_task):
    """Testa que circuit breaker aberto impede enfileiramento"""
    # Abrir circuit breaker
    for _ in range(5):
        await queue_manager._record_failure(ScraperType.CAR)
    
    # Tentar enfileirar
    success = await queue_manager.enqueue(sample_task)
    
    assert success is False


@pytest.mark.asyncio
async def test_circuit_breaker_resets_on_success(queue_manager):
    """Testa reset do circuit breaker em sucesso"""
    # Registrar algumas falhas
    await queue_manager._record_failure(ScraperType.CAR)
    await queue_manager._record_failure(ScraperType.CAR)
    
    # Registrar sucesso
    await queue_manager._record_success(ScraperType.CAR)
    
    # Verificar que failures foram resetadas
    status = await queue_manager.get_circuit_status(ScraperType.CAR)
    
    assert status["failures"] == 0
    assert status["is_open"] is False


@pytest.mark.asyncio
async def test_get_circuit_status(queue_manager):
    """Testa obtenção de status do circuit breaker"""
    # Registrar algumas falhas
    await queue_manager._record_failure(ScraperType.CAR)
    await queue_manager._record_failure(ScraperType.CAR)
    
    status = await queue_manager.get_circuit_status(ScraperType.CAR)
    
    assert status["scraper_type"] == "car"
    assert status["failures"] == 2
    assert status["threshold"] == 5
    assert status["is_open"] is False


# ==================== Testes de Progresso ====================


@pytest.mark.asyncio
async def test_update_investigation_progress(queue_manager, sample_task):
    """Testa atualização de progresso"""
    # Enfileirar e processar task
    await queue_manager.enqueue(sample_task)
    task = await queue_manager.dequeue(ScraperType.CAR)
    await queue_manager.complete_task(task.id, {"data": "test"})
    
    # Obter progresso
    progress = await queue_manager.get_investigation_progress(sample_task.investigation_id)
    
    assert progress is not None
    assert progress["total_tasks"] == 1
    assert progress["completed_tasks"] == 1
    assert sample_task.id in progress["tasks"]


@pytest.mark.asyncio
async def test_investigation_progress_multiple_tasks(queue_manager):
    """Testa progresso com múltiplas tasks"""
    investigation_id = "inv_multi"
    
    # Criar e processar várias tasks
    for i in range(3):
        task = Task(
            id=f"task_{i}",
            type=ScraperType.CAR,
            priority=TaskPriority.NORMAL,
            investigation_id=investigation_id,
            params={}
        )
        await queue_manager.enqueue(task)
    
    # Completar 2, falhar 1
    for i in range(2):
        task = await queue_manager.dequeue(ScraperType.CAR)
        await queue_manager.complete_task(task.id, {})
    
    task = await queue_manager.dequeue(ScraperType.CAR)
    task.retry_count = 3  # Forçar falha definitiva
    await queue_manager.fail_task(task.id, "Error")
    
    # Verificar progresso
    progress = await queue_manager.get_investigation_progress(investigation_id)
    
    assert progress["total_tasks"] == 3
    assert progress["completed_tasks"] == 2
    assert progress["failed_tasks"] == 1


# ==================== Testes de Cancelamento ====================


@pytest.mark.asyncio
async def test_cancel_task(queue_manager, sample_task):
    """Testa cancelamento de task"""
    await queue_manager.enqueue(sample_task)
    
    success = await queue_manager.cancel_task(sample_task.id)
    
    assert success is True
    
    # Verificar status
    task = await queue_manager.get_task(sample_task.id)
    
    assert task.status == TaskStatus.CANCELLED
    assert task.completed_at is not None


@pytest.mark.asyncio
async def test_cancel_removes_from_queue(queue_manager, sample_task):
    """Testa que cancelamento remove task da fila"""
    await queue_manager.enqueue(sample_task)
    await queue_manager.cancel_task(sample_task.id)
    
    # Tentar desenfileirar
    task = await queue_manager.dequeue(ScraperType.CAR)
    
    assert task is None


# ==================== Testes de Estatísticas ====================


@pytest.mark.asyncio
async def test_get_queue_stats(queue_manager):
    """Testa obtenção de estatísticas das filas"""
    # Enfileirar tasks de diferentes tipos
    for scraper_type in [ScraperType.CAR, ScraperType.INCRA]:
        task = Task(
            id=f"task_{scraper_type.value}",
            type=scraper_type,
            priority=TaskPriority.NORMAL,
            investigation_id="inv_123",
            params={}
        )
        await queue_manager.enqueue(task)
    
    # Obter estatísticas
    stats = await queue_manager.get_queue_stats()
    
    assert "car" in stats
    assert "incra" in stats
    assert stats["car"]["total"] == 1
    assert stats["incra"]["total"] == 1


@pytest.mark.asyncio
async def test_get_queue_stats_single_scraper(queue_manager, sample_task):
    """Testa estatísticas de um scraper específico"""
    await queue_manager.enqueue(sample_task)
    
    stats = await queue_manager.get_queue_stats(ScraperType.CAR)
    
    assert "car" in stats
    assert stats["car"]["total"] == 1
    assert "circuit_breaker" in stats["car"]


# ==================== Testes de Persistência ====================


@pytest.mark.asyncio
async def test_task_persists_in_redis(queue_manager, sample_task):
    """Testa que task persiste no Redis"""
    await queue_manager.enqueue(sample_task)
    
    # Desconectar e reconectar
    await queue_manager.disconnect()
    await queue_manager.connect()
    
    # Recuperar task
    task = await queue_manager.get_task(sample_task.id)
    
    assert task is not None
    assert task.id == sample_task.id


@pytest.mark.asyncio
async def test_task_ttl(queue_manager, sample_task):
    """Testa TTL da task no Redis"""
    await queue_manager.enqueue(sample_task)
    
    # Verificar TTL
    task_key = queue_manager._get_task_key(sample_task.id)
    ttl = await queue_manager.redis_client.ttl(task_key)
    
    # Deve ter ~7 dias (604800 segundos)
    assert ttl > 600000  # Mais de 6 dias
    assert ttl <= 604800  # No máximo 7 dias


# ==================== Testes de Integração ====================


@pytest.mark.asyncio
async def test_full_task_lifecycle(queue_manager):
    """Testa ciclo completo de uma task"""
    # 1. Criar e enfileirar
    task = Task(
        id="lifecycle_task",
        type=ScraperType.CAR,
        priority=TaskPriority.HIGH,
        investigation_id="inv_lifecycle",
        params={"name": "Test"}
    )
    
    await queue_manager.enqueue(task)
    
    # 2. Desenfileirar
    dequeued_task = await queue_manager.dequeue(ScraperType.CAR)
    assert dequeued_task.status == TaskStatus.RUNNING
    
    # 3. Completar
    result = {"data": "success"}
    await queue_manager.complete_task(dequeued_task.id, result)
    
    # 4. Verificar resultado final
    final_task = await queue_manager.get_task(dequeued_task.id)
    
    assert final_task.status == TaskStatus.COMPLETED
    assert final_task.result == result
    assert final_task.retry_count == 0
    
    # 5. Verificar progresso
    progress = await queue_manager.get_investigation_progress("inv_lifecycle")
    assert progress["completed_tasks"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
