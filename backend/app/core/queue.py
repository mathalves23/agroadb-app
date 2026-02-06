"""
Sistema de Filas com Redis - Priorização e Retry Logic
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import asyncio
import logging
from dataclasses import dataclass, asdict
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Prioridades de tarefas"""
    CRITICAL = 1  # Investigações urgentes
    HIGH = 2      # Scrapers rápidos (Receita, CPF)
    NORMAL = 3    # Scrapers médios (CAR, INCRA)
    LOW = 4       # Scrapers lentos (Diários, Cartórios)
    BACKGROUND = 5  # Tarefas de manutenção


class TaskStatus(Enum):
    """Status de tarefas"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class ScraperType(Enum):
    """Tipos de scrapers"""
    CAR = "car"
    INCRA = "incra"
    RECEITA = "receita"
    DIARIO_OFICIAL = "diario_oficial"
    CARTORIOS = "cartorios"
    SIGEF_SICAR = "sigef_sicar"


@dataclass
class Task:
    """Modelo de tarefa na fila"""
    id: str
    type: ScraperType
    priority: TaskPriority
    investigation_id: str
    params: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        data = asdict(self)
        data['type'] = self.type.value
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Cria task a partir de dicionário"""
        data['type'] = ScraperType(data['type'])
        data['priority'] = TaskPriority(data['priority'])
        data['status'] = TaskStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('started_at'):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)


class QueueManager:
    """
    Gerenciador de Filas com Redis
    
    Features:
    - Priorização de tarefas (5 níveis)
    - Retry logic com backoff exponencial
    - Filas separadas por tipo de scraper
    - Monitoramento de progresso
    - Circuit breaker para scrapers lentos
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        
        # Prefixos de chaves Redis
        self.QUEUE_PREFIX = "queue:"
        self.TASK_PREFIX = "task:"
        self.PROGRESS_PREFIX = "progress:"
        self.CIRCUIT_BREAKER_PREFIX = "circuit:"
        
        # Configurações de retry
        self.RETRY_DELAYS = {
            0: 0,       # Primeira tentativa: imediata
            1: 30,      # 30 segundos
            2: 300,     # 5 minutos
            3: 1800,    # 30 minutos
        }
        
        # Circuit breaker config
        self.CIRCUIT_BREAKER_THRESHOLD = 5  # falhas consecutivas
        self.CIRCUIT_BREAKER_TIMEOUT = 300  # 5 minutos
    
    async def connect(self):
        """Conecta ao Redis"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("✅ Conectado ao Redis")
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("🔌 Desconectado do Redis")
    
    def _get_queue_key(self, scraper_type: ScraperType, priority: TaskPriority) -> str:
        """Gera chave da fila por tipo e prioridade"""
        return f"{self.QUEUE_PREFIX}{scraper_type.value}:{priority.value}"
    
    def _get_task_key(self, task_id: str) -> str:
        """Gera chave de armazenamento da task"""
        return f"{self.TASK_PREFIX}{task_id}"
    
    def _get_progress_key(self, investigation_id: str) -> str:
        """Gera chave de progresso da investigação"""
        return f"{self.PROGRESS_PREFIX}{investigation_id}"
    
    def _get_circuit_breaker_key(self, scraper_type: ScraperType) -> str:
        """Gera chave do circuit breaker"""
        return f"{self.CIRCUIT_BREAKER_PREFIX}{scraper_type.value}"
    
    async def enqueue(self, task: Task) -> bool:
        """
        Adiciona task na fila com prioridade
        
        Args:
            task: Task a ser enfileirada
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            # Verificar circuit breaker
            if await self._is_circuit_open(task.type):
                logger.warning(f"⚡ Circuit breaker ABERTO para {task.type.value} - task não enfileirada")
                return False
            
            # Salvar dados da task
            task_key = self._get_task_key(task.id)
            await self.redis_client.setex(
                task_key,
                timedelta(days=7),  # TTL de 7 dias
                json.dumps(task.to_dict())
            )
            
            # Adicionar à fila com score baseado em prioridade e timestamp
            queue_key = self._get_queue_key(task.type, task.priority)
            score = task.priority.value * 1000000 + task.created_at.timestamp()
            
            await self.redis_client.zadd(queue_key, {task.id: score})
            
            # Atualizar progresso da investigação
            await self._update_investigation_progress(
                task.investigation_id,
                task.id,
                TaskStatus.PENDING
            )
            
            logger.info(f"✅ Task {task.id} enfileirada: {task.type.value} (prioridade: {task.priority.name})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao enfileirar task {task.id}: {e}")
            return False
    
    async def dequeue(self, scraper_type: ScraperType) -> Optional[Task]:
        """
        Remove e retorna próxima task da fila (por prioridade)
        
        Args:
            scraper_type: Tipo de scraper
            
        Returns:
            Task ou None
        """
        try:
            # Verificar circuit breaker
            if await self._is_circuit_open(scraper_type):
                logger.warning(f"⚡ Circuit breaker ABERTO para {scraper_type.value}")
                return None
            
            # Buscar em todas as filas de prioridade (CRITICAL -> BACKGROUND)
            for priority in TaskPriority:
                queue_key = self._get_queue_key(scraper_type, priority)
                
                # Pegar task com menor score (maior prioridade + mais antiga)
                result = await self.redis_client.zpopmin(queue_key, count=1)
                
                if result:
                    task_id = result[0][0]
                    task_data = await self.redis_client.get(self._get_task_key(task_id))
                    
                    if task_data:
                        task = Task.from_dict(json.loads(task_data))
                        task.status = TaskStatus.RUNNING
                        task.started_at = datetime.utcnow()
                        
                        # Atualizar task
                        await self._save_task(task)
                        
                        # Atualizar progresso
                        await self._update_investigation_progress(
                            task.investigation_id,
                            task.id,
                            TaskStatus.RUNNING
                        )
                        
                        logger.info(f"🎯 Task {task.id} iniciada: {task.type.value}")
                        return task
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao desenfileirar task de {scraper_type.value}: {e}")
            return None
    
    async def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """
        Marca task como completa
        
        Args:
            task_id: ID da task
            result: Resultado da execução
            
        Returns:
            bool: Sucesso
        """
        try:
            task = await self.get_task(task_id)
            if not task:
                return False
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            
            await self._save_task(task)
            
            # Atualizar progresso
            await self._update_investigation_progress(
                task.investigation_id,
                task.id,
                TaskStatus.COMPLETED
            )
            
            # Resetar circuit breaker em caso de sucesso
            await self._record_success(task.type)
            
            logger.info(f"✅ Task {task_id} concluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao completar task {task_id}: {e}")
            return False
    
    async def fail_task(self, task_id: str, error: str) -> bool:
        """
        Marca task como falha e agenda retry se aplicável
        
        Args:
            task_id: ID da task
            error: Mensagem de erro
            
        Returns:
            bool: True se vai tentar novamente, False se falhou definitivamente
        """
        try:
            task = await self.get_task(task_id)
            if not task:
                return False
            
            task.retry_count += 1
            task.error = error
            
            # Registrar falha no circuit breaker
            await self._record_failure(task.type)
            
            # Verificar se deve tentar novamente
            if task.retry_count <= task.max_retries:
                task.status = TaskStatus.RETRYING
                
                # Calcular delay com backoff exponencial
                delay = self.RETRY_DELAYS.get(task.retry_count, 3600)
                retry_at = datetime.utcnow() + timedelta(seconds=delay)
                
                await self._save_task(task)
                
                # Re-enfileirar com delay
                await self._schedule_retry(task, delay)
                
                logger.warning(
                    f"🔄 Task {task_id} falhou (tentativa {task.retry_count}/{task.max_retries}). "
                    f"Retry em {delay}s às {retry_at.strftime('%H:%M:%S')}"
                )
                
                return True
            else:
                # Falha definitiva
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                
                await self._save_task(task)
                
                # Atualizar progresso
                await self._update_investigation_progress(
                    task.investigation_id,
                    task.id,
                    TaskStatus.FAILED
                )
                
                logger.error(
                    f"❌ Task {task_id} FALHOU definitivamente após {task.retry_count} tentativas: {error}"
                )
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar falha da task {task_id}: {e}")
            return False
    
    async def _schedule_retry(self, task: Task, delay: int):
        """Agenda retry da task após delay"""
        retry_time = datetime.utcnow() + timedelta(seconds=delay)
        
        # Adicionar à fila de retry com timestamp futuro
        retry_key = f"{self.QUEUE_PREFIX}retry"
        await self.redis_client.zadd(
            retry_key,
            {task.id: retry_time.timestamp()}
        )
    
    async def process_retries(self):
        """
        Processa tasks agendadas para retry
        
        Deve ser executado periodicamente (a cada 10s)
        """
        try:
            retry_key = f"{self.QUEUE_PREFIX}retry"
            now = datetime.utcnow().timestamp()
            
            # Buscar tasks cujo timestamp de retry já passou
            ready_tasks = await self.redis_client.zrangebyscore(
                retry_key,
                min=0,
                max=now
            )
            
            for task_id in ready_tasks:
                task = await self.get_task(task_id)
                if task:
                    # Re-enfileirar
                    task.status = TaskStatus.PENDING
                    await self.enqueue(task)
                    
                    # Remover da fila de retry
                    await self.redis_client.zrem(retry_key, task_id)
                    
                    logger.info(f"🔄 Task {task_id} re-enfileirada após retry")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar retries: {e}")
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Recupera task por ID"""
        try:
            task_data = await self.redis_client.get(self._get_task_key(task_id))
            if task_data:
                return Task.from_dict(json.loads(task_data))
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar task {task_id}: {e}")
            return None
    
    async def _save_task(self, task: Task):
        """Salva task no Redis"""
        task_key = self._get_task_key(task.id)
        await self.redis_client.setex(
            task_key,
            timedelta(days=7),
            json.dumps(task.to_dict())
        )
    
    async def _update_investigation_progress(
        self,
        investigation_id: str,
        task_id: str,
        status: TaskStatus
    ):
        """Atualiza progresso da investigação"""
        progress_key = self._get_progress_key(investigation_id)
        
        # Buscar progresso atual
        progress_data = await self.redis_client.get(progress_key)
        if progress_data:
            progress = json.loads(progress_data)
        else:
            progress = {
                "investigation_id": investigation_id,
                "total_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "running_tasks": 0,
                "tasks": {},
                "updated_at": None
            }
        
        # Atualizar contadores
        if task_id not in progress["tasks"]:
            progress["total_tasks"] += 1
        
        old_status = progress["tasks"].get(task_id)
        progress["tasks"][task_id] = status.value
        
        # Atualizar contadores específicos
        if old_status == TaskStatus.RUNNING.value:
            progress["running_tasks"] -= 1
        
        if status == TaskStatus.COMPLETED:
            progress["completed_tasks"] += 1
        elif status == TaskStatus.FAILED:
            progress["failed_tasks"] += 1
        elif status == TaskStatus.RUNNING:
            progress["running_tasks"] += 1
        
        progress["updated_at"] = datetime.utcnow().isoformat()
        
        # Salvar progresso
        await self.redis_client.setex(
            progress_key,
            timedelta(days=30),
            json.dumps(progress)
        )
    
    async def get_investigation_progress(self, investigation_id: str) -> Optional[dict]:
        """Recupera progresso de uma investigação"""
        progress_key = self._get_progress_key(investigation_id)
        progress_data = await self.redis_client.get(progress_key)
        
        if progress_data:
            return json.loads(progress_data)
        return None
    
    # Circuit Breaker Implementation
    
    async def _record_failure(self, scraper_type: ScraperType):
        """Registra falha no circuit breaker"""
        key = self._get_circuit_breaker_key(scraper_type)
        failures = await self.redis_client.incr(f"{key}:failures")
        
        if failures >= self.CIRCUIT_BREAKER_THRESHOLD:
            # Abrir circuit breaker
            await self.redis_client.setex(
                f"{key}:open",
                timedelta(seconds=self.CIRCUIT_BREAKER_TIMEOUT),
                "1"
            )
            logger.error(
                f"⚡ CIRCUIT BREAKER ABERTO para {scraper_type.value} "
                f"após {failures} falhas consecutivas"
            )
    
    async def _record_success(self, scraper_type: ScraperType):
        """Registra sucesso e reseta circuit breaker"""
        key = self._get_circuit_breaker_key(scraper_type)
        await self.redis_client.delete(f"{key}:failures")
        await self.redis_client.delete(f"{key}:open")
    
    async def _is_circuit_open(self, scraper_type: ScraperType) -> bool:
        """Verifica se circuit breaker está aberto"""
        key = self._get_circuit_breaker_key(scraper_type)
        is_open = await self.redis_client.exists(f"{key}:open")
        return bool(is_open)
    
    async def get_circuit_status(self, scraper_type: ScraperType) -> dict:
        """Retorna status do circuit breaker"""
        key = self._get_circuit_breaker_key(scraper_type)
        is_open = await self._is_circuit_open(scraper_type)
        failures = await self.redis_client.get(f"{key}:failures") or 0
        
        return {
            "scraper_type": scraper_type.value,
            "is_open": is_open,
            "failures": int(failures),
            "threshold": self.CIRCUIT_BREAKER_THRESHOLD
        }
    
    # Monitoramento e Estatísticas
    
    async def get_queue_stats(self, scraper_type: Optional[ScraperType] = None) -> dict:
        """Retorna estatísticas das filas"""
        stats = {}
        
        scraper_types = [scraper_type] if scraper_type else list(ScraperType)
        
        for stype in scraper_types:
            type_stats = {
                "total": 0,
                "by_priority": {}
            }
            
            for priority in TaskPriority:
                queue_key = self._get_queue_key(stype, priority)
                count = await self.redis_client.zcard(queue_key)
                
                type_stats["by_priority"][priority.name] = count
                type_stats["total"] += count
            
            # Circuit breaker status
            type_stats["circuit_breaker"] = await self.get_circuit_status(stype)
            
            stats[stype.value] = type_stats
        
        return stats
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancela uma task"""
        try:
            task = await self.get_task(task_id)
            if not task:
                return False
            
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            
            await self._save_task(task)
            
            # Remover de todas as filas
            for priority in TaskPriority:
                queue_key = self._get_queue_key(task.type, priority)
                await self.redis_client.zrem(queue_key, task_id)
            
            logger.info(f"🚫 Task {task_id} cancelada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao cancelar task {task_id}: {e}")
            return False


# Instância global do gerenciador de filas
queue_manager = QueueManager()
