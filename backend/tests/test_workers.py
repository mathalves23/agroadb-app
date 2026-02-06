"""
Testes dos Workers e Orquestrador
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from app.workers.scraper_workers import (
    ScraperWorker,
    WorkerOrchestrator,
    enqueue_investigation_scrapers,
    enqueue_single_scraper,
    get_task_status,
    cancel_investigation_scrapers
)
from app.core.queue import (
    queue_manager,
    Task,
    TaskPriority,
    TaskStatus,
    ScraperType
)


@pytest.fixture
async def clean_redis():
    """Limpa Redis antes de cada teste"""
    await queue_manager.connect()
    await queue_manager.redis_client.flushdb()
    yield
    await queue_manager.disconnect()


# ==================== Testes do ScraperWorker ====================


@pytest.mark.asyncio
async def test_scraper_worker_initialization():
    """Testa inicialização do worker"""
    worker = ScraperWorker(ScraperType.CAR)
    
    assert worker.scraper_type == ScraperType.CAR
    assert worker.is_running is False
    assert worker.scraper is not None


@pytest.mark.asyncio
async def test_worker_gets_correct_scraper():
    """Testa que worker obtém scraper correto"""
    from app.scrapers.car_scraper import CARScraper
    from app.scrapers.receita_scraper import ReceitaScraper
    
    car_worker = ScraperWorker(ScraperType.CAR)
    receita_worker = ScraperWorker(ScraperType.RECEITA)
    
    assert isinstance(car_worker.scraper, CARScraper)
    assert isinstance(receita_worker.scraper, ReceitaScraper)


@pytest.mark.asyncio
async def test_worker_timeout_configuration():
    """Testa configuração de timeouts"""
    worker = ScraperWorker(ScraperType.CAR)
    
    assert worker.TIMEOUTS[ScraperType.CAR] == 120
    assert worker.TIMEOUTS[ScraperType.RECEITA] == 60
    assert worker.TIMEOUTS[ScraperType.DIARIO_OFICIAL] == 180


@pytest.mark.asyncio
@patch('app.workers.scraper_workers.notify_task_started')
@patch('app.workers.scraper_workers.notify_task_completed')
async def test_worker_processes_task(mock_notify_completed, mock_notify_started, clean_redis):
    """Testa processamento de task pelo worker"""
    worker = ScraperWorker(ScraperType.CAR)
    
    # Mock do scraper
    worker.scraper.search = AsyncMock(return_value=[{"test": "data"}])
    
    # Criar e enfileirar task
    task = Task(
        id="test_task",
        type=ScraperType.CAR,
        priority=TaskPriority.NORMAL,
        investigation_id="inv_123",
        params={"name": "Test"}
    )
    
    await queue_manager.enqueue(task)
    
    # Processar task
    await worker._process_next_task()
    
    # Verificar que scraper foi chamado
    worker.scraper.search.assert_called_once()
    
    # Verificar notificações
    mock_notify_started.assert_called_once()
    mock_notify_completed.assert_called_once()
    
    # Verificar que task foi marcada como completa
    updated_task = await queue_manager.get_task("test_task")
    assert updated_task.status == TaskStatus.COMPLETED


@pytest.mark.asyncio
@patch('app.workers.scraper_workers.notify_task_failed')
async def test_worker_handles_task_failure(mock_notify_failed, clean_redis):
    """Testa tratamento de falha no worker"""
    worker = ScraperWorker(ScraperType.CAR)
    
    # Mock do scraper com erro
    worker.scraper.search = AsyncMock(side_effect=Exception("Test error"))
    
    # Criar e enfileirar task
    task = Task(
        id="test_task_fail",
        type=ScraperType.CAR,
        priority=TaskPriority.NORMAL,
        investigation_id="inv_123",
        params={"name": "Test"}
    )
    
    await queue_manager.enqueue(task)
    
    # Processar task
    await worker._process_next_task()
    
    # Verificar que falha foi notificada
    mock_notify_failed.assert_called_once()
    
    # Verificar que task está em retry
    updated_task = await queue_manager.get_task("test_task_fail")
    assert updated_task.status == TaskStatus.RETRYING
    assert updated_task.retry_count == 1


@pytest.mark.asyncio
async def test_worker_timeout(clean_redis):
    """Testa timeout de task"""
    worker = ScraperWorker(ScraperType.CAR)
    worker.TIMEOUTS[ScraperType.CAR] = 1  # 1 segundo
    
    # Mock do scraper que demora muito
    async def slow_search(*args, **kwargs):
        await asyncio.sleep(5)
        return []
    
    worker.scraper.search = slow_search
    
    # Criar e enfileirar task
    task = Task(
        id="test_task_timeout",
        type=ScraperType.CAR,
        priority=TaskPriority.NORMAL,
        investigation_id="inv_123",
        params={"name": "Test"}
    )
    
    await queue_manager.enqueue(task)
    
    # Processar task (deve dar timeout)
    await worker._process_next_task()
    
    # Verificar que task falhou por timeout
    updated_task = await queue_manager.get_task("test_task_timeout")
    assert "Timeout" in updated_task.error


# ==================== Testes do WorkerOrchestrator ====================


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Testa inicialização do orquestrador"""
    orchestrator = WorkerOrchestrator()
    
    assert len(orchestrator.workers) == 0
    assert orchestrator.retry_processor_running is False


@pytest.mark.asyncio
async def test_orchestrator_creates_all_workers():
    """Testa criação de todos os workers"""
    orchestrator = WorkerOrchestrator()
    
    # Iniciar com timeout curto para não travar o teste
    start_task = asyncio.create_task(orchestrator.start_all_workers())
    
    # Aguardar um pouco para workers iniciarem
    await asyncio.sleep(0.5)
    
    # Verificar que workers foram criados
    assert len(orchestrator.workers) == len(ScraperType)
    
    for scraper_type in ScraperType:
        assert scraper_type in orchestrator.workers
        assert orchestrator.workers[scraper_type].scraper_type == scraper_type
    
    # Parar workers
    await orchestrator.stop_all_workers()
    start_task.cancel()
    
    try:
        await start_task
    except asyncio.CancelledError:
        pass


# ==================== Testes de Funções Auxiliares ====================


@pytest.mark.asyncio
async def test_enqueue_investigation_scrapers(clean_redis):
    """Testa enfileiramento de todos os scrapers de uma investigação"""
    task_ids = await enqueue_investigation_scrapers(
        investigation_id="inv_test",
        target_name="João Silva",
        target_cpf_cnpj="123.456.789-00",
        priority=TaskPriority.HIGH
    )
    
    # Verificar que todos os scrapers foram enfileirados
    assert len(task_ids) == len(ScraperType)
    
    for scraper_type in ScraperType:
        assert scraper_type.value in task_ids
    
    # Verificar estatísticas
    stats = await queue_manager.get_queue_stats()
    total_tasks = sum(s["total"] for s in stats.values())
    assert total_tasks == len(ScraperType)


@pytest.mark.asyncio
async def test_enqueue_investigation_priority_adjustment(clean_redis):
    """Testa ajuste de prioridade por tipo de scraper"""
    task_ids = await enqueue_investigation_scrapers(
        investigation_id="inv_test",
        target_name="Test",
        priority=TaskPriority.NORMAL
    )
    
    # Verificar que Receita tem prioridade maior
    receita_task_id = task_ids["receita"]
    receita_task = await queue_manager.get_task(receita_task_id)
    
    # Diário Oficial tem prioridade menor
    diario_task_id = task_ids["diario_oficial"]
    diario_task = await queue_manager.get_task(diario_task_id)
    
    assert receita_task.priority.value < TaskPriority.NORMAL.value
    assert diario_task.priority.value > TaskPriority.NORMAL.value


@pytest.mark.asyncio
async def test_enqueue_single_scraper(clean_redis):
    """Testa enfileiramento de scraper único"""
    task_id = await enqueue_single_scraper(
        investigation_id="inv_test",
        scraper_type=ScraperType.CAR,
        params={"name": "Test"},
        priority=TaskPriority.HIGH
    )
    
    assert task_id is not None
    
    # Verificar task
    task = await queue_manager.get_task(task_id)
    assert task is not None
    assert task.type == ScraperType.CAR
    assert task.priority == TaskPriority.HIGH


@pytest.mark.asyncio
async def test_get_task_status(clean_redis):
    """Testa obtenção de status de task"""
    # Criar e enfileirar task
    task = Task(
        id="status_test",
        type=ScraperType.CAR,
        priority=TaskPriority.NORMAL,
        investigation_id="inv_test",
        params={}
    )
    
    await queue_manager.enqueue(task)
    
    # Obter status
    status = await get_task_status("status_test")
    
    assert status is not None
    assert status["id"] == "status_test"
    assert status["type"] == "car"
    assert status["status"] == "pending"


@pytest.mark.asyncio
async def test_cancel_investigation_scrapers(clean_redis):
    """Testa cancelamento de scrapers de uma investigação"""
    # Enfileirar scrapers
    task_ids = await enqueue_investigation_scrapers(
        investigation_id="inv_cancel",
        target_name="Test"
    )
    
    # Cancelar todos
    cancelled_count = await cancel_investigation_scrapers("inv_cancel")
    
    # Verificar que todos foram cancelados
    assert cancelled_count == len(task_ids)
    
    # Verificar que tasks estão canceladas
    for task_id in task_ids.values():
        task = await queue_manager.get_task(task_id)
        assert task.status == TaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_cancel_only_pending_tasks(clean_redis):
    """Testa que apenas tasks pendentes são canceladas"""
    # Enfileirar e processar uma task
    task_ids = await enqueue_investigation_scrapers(
        investigation_id="inv_cancel_partial",
        target_name="Test"
    )
    
    # Completar primeira task
    first_task_id = list(task_ids.values())[0]
    task = await queue_manager.dequeue(ScraperType.CAR)
    await queue_manager.complete_task(task.id, {})
    
    # Cancelar investigação
    cancelled_count = await cancel_investigation_scrapers("inv_cancel_partial")
    
    # Verificar que apenas tasks pendentes foram canceladas
    assert cancelled_count == len(task_ids) - 1


# ==================== Testes de Integração ====================


@pytest.mark.asyncio
async def test_full_worker_flow(clean_redis):
    """Testa fluxo completo: enfileirar -> processar -> completar"""
    worker = ScraperWorker(ScraperType.CAR)
    
    # Mock do scraper
    worker.scraper.search = AsyncMock(return_value=[{"data": "test"}])
    
    # Enfileirar
    task_ids = await enqueue_investigation_scrapers(
        investigation_id="inv_flow",
        target_name="Test"
    )
    
    car_task_id = task_ids["car"]
    
    # Processar
    await worker._process_next_task()
    
    # Verificar resultado
    status = await get_task_status(car_task_id)
    assert status["status"] == "completed"
    
    # Verificar progresso
    progress = await queue_manager.get_investigation_progress("inv_flow")
    assert progress["completed_tasks"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
