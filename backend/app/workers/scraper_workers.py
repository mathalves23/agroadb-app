"""
Workers Melhorados para Processamento de Scrapers
Com suporte a filas, retry, circuit breaker e notificações em tempo real
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from app.core.queue import (
    queue_manager,
    Task,
    TaskPriority,
    TaskStatus,
    ScraperType
)
from app.core.websocket import (
    notify_task_started,
    notify_task_completed,
    notify_task_failed,
    notify_investigation_progress
)
from app.scrapers.car_scraper import CARScraper
from app.scrapers.incra_scraper import INCRAScraper
from app.scrapers.receita_scraper import ReceitaScraper
from app.scrapers.diario_oficial_scraper import DiarioOficialScraper
from app.scrapers.cartorios_scraper import CartoriosScraper
from app.scrapers.sigef_sicar_scraper import SIGEFSICARScraper

logger = logging.getLogger(__name__)


class ScraperWorker:
    """
    Worker para processar tarefas de scraping
    
    Features:
    - Processa uma fila específica de scraper
    - Timeout configurável por scraper
    - Integração com circuit breaker
    - Notificações WebSocket em tempo real
    """
    
    def __init__(self, scraper_type: ScraperType):
        self.scraper_type = scraper_type
        self.is_running = False
        
        # Timeouts por tipo de scraper (segundos)
        self.TIMEOUTS = {
            ScraperType.CAR: 120,
            ScraperType.INCRA: 120,
            ScraperType.RECEITA: 60,
            ScraperType.DIARIO_OFICIAL: 180,
            ScraperType.CARTORIOS: 150,
            ScraperType.SIGEF_SICAR: 180,
        }
        
        # Instância do scraper
        self.scraper = self._get_scraper_instance()
    
    def _get_scraper_instance(self):
        """Retorna instância do scraper apropriado"""
        scrapers = {
            ScraperType.CAR: CARScraper,
            ScraperType.INCRA: INCRAScraper,
            ScraperType.RECEITA: ReceitaScraper,
            ScraperType.DIARIO_OFICIAL: DiarioOficialScraper,
            ScraperType.CARTORIOS: CartoriosScraper,
            ScraperType.SIGEF_SICAR: SIGEFSICARScraper,
        }
        return scrapers[self.scraper_type]()
    
    async def start(self):
        """Inicia worker (loop infinito)"""
        self.is_running = True
        logger.info(f"🚀 Worker {self.scraper_type.value} iniciado")
        
        await queue_manager.connect()
        
        try:
            while self.is_running:
                await self._process_next_task()
                await asyncio.sleep(1)  # Evitar loop muito rápido
        finally:
            await queue_manager.disconnect()
    
    async def stop(self):
        """Para worker"""
        self.is_running = False
        logger.info(f"🛑 Worker {self.scraper_type.value} parado")
    
    async def _process_next_task(self):
        """Processa próxima task da fila"""
        try:
            # Desenfileirar próxima task
            task = await queue_manager.dequeue(self.scraper_type)
            
            if not task:
                return  # Sem tasks na fila
            
            # Notificar início
            await notify_task_started(
                task.investigation_id,
                task.id,
                task.type
            )
            
            # Executar com timeout
            timeout = self.TIMEOUTS.get(self.scraper_type, 120)
            
            try:
                result = await asyncio.wait_for(
                    self._execute_scraper(task),
                    timeout=timeout
                )
                
                # Marcar como completa
                await queue_manager.complete_task(task.id, result)
                
                # Notificar conclusão
                await notify_task_completed(
                    task.investigation_id,
                    task.id,
                    task.type,
                    result
                )
                
                # Atualizar progresso geral
                progress = await queue_manager.get_investigation_progress(task.investigation_id)
                if progress:
                    await notify_investigation_progress(task.investigation_id, progress)
                
            except asyncio.TimeoutError:
                error_msg = f"Timeout após {timeout}s"
                logger.error(f"⏰ Task {task.id} excedeu timeout de {timeout}s")
                
                # Marcar como falha e tentar retry
                await queue_manager.fail_task(task.id, error_msg)
                
                # Notificar falha
                await notify_task_failed(
                    task.investigation_id,
                    task.id,
                    task.type,
                    error_msg,
                    task.retry_count + 1,
                    task.max_retries
                )
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Erro na task {task.id}: {error_msg}")
                
                # Marcar como falha e tentar retry
                await queue_manager.fail_task(task.id, error_msg)
                
                # Notificar falha
                await notify_task_failed(
                    task.investigation_id,
                    task.id,
                    task.type,
                    error_msg,
                    task.retry_count + 1,
                    task.max_retries
                )
        
        except Exception as e:
            logger.error(f"❌ Erro crítico no worker {self.scraper_type.value}: {e}")
    
    async def _execute_scraper(self, task: Task) -> Dict[str, Any]:
        """
        Executa scraper com os parâmetros da task
        
        Args:
            task: Task a ser executada
            
        Returns:
            Resultado do scraper
        """
        params = task.params
        
        # Executar método search do scraper
        if self.scraper_type == ScraperType.RECEITA:
            # Receita só usa CNPJ
            results = await self.scraper.search(params.get("cpf_cnpj", ""))
        else:
            # Outros scrapers usam múltiplos parâmetros
            results = await self.scraper.search(
                name=params.get("name"),
                cpf_cnpj=params.get("cpf_cnpj"),
                state=params.get("state"),
                city=params.get("city")
            )
        
        return {
            "scraper_type": self.scraper_type.value,
            "results": results,
            "count": len(results) if isinstance(results, list) else 1,
            "timestamp": datetime.utcnow().isoformat()
        }


class WorkerOrchestrator:
    """
    Orquestrador de Workers
    
    Gerencia múltiplos workers (um por tipo de scraper) e o processador de retries
    """
    
    def __init__(self):
        self.workers: Dict[ScraperType, ScraperWorker] = {}
        self.retry_processor_running = False
    
    async def start_all_workers(self):
        """Inicia todos os workers"""
        logger.info("🚀 Iniciando orquestrador de workers...")
        
        # Criar e iniciar um worker para cada tipo de scraper
        tasks = []
        for scraper_type in ScraperType:
            worker = ScraperWorker(scraper_type)
            self.workers[scraper_type] = worker
            tasks.append(asyncio.create_task(worker.start()))
        
        # Iniciar processador de retries
        self.retry_processor_running = True
        tasks.append(asyncio.create_task(self._retry_processor()))
        
        logger.info(f"✅ {len(self.workers)} workers iniciados + retry processor")
        
        # Aguardar todos os workers
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_all_workers(self):
        """Para todos os workers"""
        logger.info("🛑 Parando orquestrador de workers...")
        
        self.retry_processor_running = False
        
        for worker in self.workers.values():
            await worker.stop()
        
        logger.info("✅ Todos os workers parados")
    
    async def _retry_processor(self):
        """
        Processador de retries
        
        Verifica a cada 10s se há tasks prontas para retry
        """
        await queue_manager.connect()
        
        try:
            while self.retry_processor_running:
                await queue_manager.process_retries()
                await asyncio.sleep(10)  # Verificar a cada 10s
        finally:
            await queue_manager.disconnect()


# Instância global do orquestrador
orchestrator = WorkerOrchestrator()


# Funções auxiliares para enfileiramento


async def enqueue_investigation_scrapers(
    investigation_id: str,
    target_name: Optional[str] = None,
    target_cpf_cnpj: Optional[str] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    priority: TaskPriority = TaskPriority.NORMAL
) -> Dict[str, str]:
    """
    Enfileira todos os scrapers para uma investigação
    
    Args:
        investigation_id: ID da investigação
        target_name: Nome do alvo
        target_cpf_cnpj: CPF/CNPJ do alvo
        state: Estado
        city: Cidade
        priority: Prioridade das tasks
        
    Returns:
        Dicionário com task_ids por scraper
    """
    await queue_manager.connect()
    
    task_ids = {}
    
    # Parâmetros comuns
    params = {
        "name": target_name,
        "cpf_cnpj": target_cpf_cnpj,
        "state": state,
        "city": city
    }
    
    # Criar e enfileirar tasks para cada scraper
    for scraper_type in ScraperType:
        task_id = f"{investigation_id}_{scraper_type.value}_{uuid.uuid4().hex[:8]}"
        
        # Ajustar prioridade por tipo de scraper
        task_priority = priority
        if scraper_type == ScraperType.RECEITA:
            # Receita é mais rápido, maior prioridade
            task_priority = TaskPriority(max(1, priority.value - 1))
        elif scraper_type in [ScraperType.DIARIO_OFICIAL, ScraperType.CARTORIOS]:
            # Scrapers lentos, menor prioridade
            task_priority = TaskPriority(min(5, priority.value + 1))
        
        task = Task(
            id=task_id,
            type=scraper_type,
            priority=task_priority,
            investigation_id=investigation_id,
            params=params,
            max_retries=3
        )
        
        success = await queue_manager.enqueue(task)
        if success:
            task_ids[scraper_type.value] = task_id
    
    logger.info(
        f"📝 Enfileirados {len(task_ids)} scrapers para investigação {investigation_id}"
    )
    
    return task_ids


async def enqueue_single_scraper(
    investigation_id: str,
    scraper_type: ScraperType,
    params: Dict[str, Any],
    priority: TaskPriority = TaskPriority.NORMAL,
    max_retries: int = 3
) -> Optional[str]:
    """
    Enfileira um scraper específico
    
    Args:
        investigation_id: ID da investigação
        scraper_type: Tipo de scraper
        params: Parâmetros do scraper
        priority: Prioridade
        max_retries: Número máximo de tentativas
        
    Returns:
        ID da task ou None
    """
    await queue_manager.connect()
    
    task_id = f"{investigation_id}_{scraper_type.value}_{uuid.uuid4().hex[:8]}"
    
    task = Task(
        id=task_id,
        type=scraper_type,
        priority=priority,
        investigation_id=investigation_id,
        params=params,
        max_retries=max_retries
    )
    
    success = await queue_manager.enqueue(task)
    
    if success:
        logger.info(f"✅ Scraper {scraper_type.value} enfileirado: {task_id}")
        return task_id
    else:
        logger.error(f"❌ Falha ao enfileirar scraper {scraper_type.value}")
        return None


async def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Retorna status de uma task
    
    Args:
        task_id: ID da task
        
    Returns:
        Status da task
    """
    await queue_manager.connect()
    
    task = await queue_manager.get_task(task_id)
    
    if task:
        return {
            "id": task.id,
            "type": task.type.value,
            "status": task.status.value,
            "investigation_id": task.investigation_id,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries,
            "error": task.error,
            "result": task.result
        }
    
    return None


async def cancel_investigation_scrapers(investigation_id: str) -> int:
    """
    Cancela todos os scrapers de uma investigação
    
    Args:
        investigation_id: ID da investigação
        
    Returns:
        Número de tasks canceladas
    """
    await queue_manager.connect()
    
    # Buscar progresso para obter todas as tasks
    progress = await queue_manager.get_investigation_progress(investigation_id)
    
    if not progress:
        return 0
    
    cancelled_count = 0
    
    for task_id in progress["tasks"].keys():
        task = await queue_manager.get_task(task_id)
        
        # Cancelar apenas tasks pendentes ou com retry
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RETRYING]:
            success = await queue_manager.cancel_task(task_id)
            if success:
                cancelled_count += 1
    
    logger.info(f"🚫 {cancelled_count} tasks canceladas da investigação {investigation_id}")
    
    return cancelled_count
