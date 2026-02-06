"""
Sistema de WebSockets para Notificações em Tempo Real
"""
from typing import Dict, Set, Optional, Any
import json
import logging
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from app.core.queue import TaskStatus, ScraperType

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Gerenciador de Conexões WebSocket
    
    Features:
    - Conexões por investigação (usuários recebem updates apenas de suas investigações)
    - Broadcast para todos os clientes
    - Notificações em tempo real de progresso
    - Reconexão automática
    """
    
    def __init__(self):
        # {investigation_id: {websocket1, websocket2, ...}}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # {websocket: user_id} para rastreamento
        self.websocket_users: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, investigation_id: str, user_id: str):
        """
        Conecta cliente WebSocket
        
        Args:
            websocket: Conexão WebSocket
            investigation_id: ID da investigação
            user_id: ID do usuário
        """
        await websocket.accept()
        
        if investigation_id not in self.active_connections:
            self.active_connections[investigation_id] = set()
        
        self.active_connections[investigation_id].add(websocket)
        self.websocket_users[websocket] = user_id
        
        logger.info(
            f"🔌 WebSocket conectado: user={user_id}, investigation={investigation_id}. "
            f"Total: {len(self.active_connections[investigation_id])} conexões"
        )
        
        # Enviar mensagem de boas-vindas
        await self.send_personal_message(
            {
                "type": "connected",
                "message": "Conectado ao sistema de notificações em tempo real",
                "investigation_id": investigation_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            websocket
        )
    
    def disconnect(self, websocket: WebSocket, investigation_id: str):
        """
        Desconecta cliente WebSocket
        
        Args:
            websocket: Conexão WebSocket
            investigation_id: ID da investigação
        """
        if investigation_id in self.active_connections:
            self.active_connections[investigation_id].discard(websocket)
            
            # Remover investigação se não houver mais conexões
            if not self.active_connections[investigation_id]:
                del self.active_connections[investigation_id]
        
        user_id = self.websocket_users.pop(websocket, "unknown")
        
        logger.info(
            f"🔌 WebSocket desconectado: user={user_id}, investigation={investigation_id}"
        )
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Envia mensagem para um cliente específico
        
        Args:
            message: Dados da mensagem
            websocket: Conexão WebSocket destino
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem pessoal: {e}")
    
    async def broadcast_to_investigation(self, message: dict, investigation_id: str):
        """
        Envia mensagem para todos os clientes de uma investigação
        
        Args:
            message: Dados da mensagem
            investigation_id: ID da investigação
        """
        if investigation_id not in self.active_connections:
            return
        
        disconnected = set()
        
        for websocket in self.active_connections[investigation_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"❌ Erro ao enviar mensagem broadcast: {e}")
                disconnected.add(websocket)
        
        # Remover conexões mortas
        for websocket in disconnected:
            self.disconnect(websocket, investigation_id)
    
    async def broadcast_to_all(self, message: dict):
        """
        Envia mensagem para TODOS os clientes conectados
        
        Args:
            message: Dados da mensagem
        """
        for investigation_id in list(self.active_connections.keys()):
            await self.broadcast_to_investigation(message, investigation_id)
    
    def get_connection_count(self, investigation_id: Optional[str] = None) -> int:
        """
        Retorna número de conexões ativas
        
        Args:
            investigation_id: ID da investigação (None = todas)
            
        Returns:
            Número de conexões
        """
        if investigation_id:
            return len(self.active_connections.get(investigation_id, set()))
        
        return sum(len(conns) for conns in self.active_connections.values())
    
    def get_stats(self) -> dict:
        """Retorna estatísticas de conexões"""
        return {
            "total_connections": self.get_connection_count(),
            "active_investigations": len(self.active_connections),
            "connections_by_investigation": {
                inv_id: len(conns)
                for inv_id, conns in self.active_connections.items()
            }
        }


# Instância global do gerenciador de conexões
connection_manager = ConnectionManager()


# Funções auxiliares para envio de notificações


async def notify_task_started(investigation_id: str, task_id: str, scraper_type: ScraperType):
    """Notifica início de tarefa"""
    await connection_manager.broadcast_to_investigation(
        {
            "type": "task_started",
            "investigation_id": investigation_id,
            "task_id": task_id,
            "scraper_type": scraper_type.value,
            "status": TaskStatus.RUNNING.value,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"🎯 Iniciando scraper {scraper_type.value}..."
        },
        investigation_id
    )


async def notify_task_completed(
    investigation_id: str,
    task_id: str,
    scraper_type: ScraperType,
    result: Optional[Dict[str, Any]] = None
):
    """Notifica conclusão de tarefa"""
    await connection_manager.broadcast_to_investigation(
        {
            "type": "task_completed",
            "investigation_id": investigation_id,
            "task_id": task_id,
            "scraper_type": scraper_type.value,
            "status": TaskStatus.COMPLETED.value,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"✅ Scraper {scraper_type.value} concluído com sucesso!"
        },
        investigation_id
    )


async def notify_task_failed(
    investigation_id: str,
    task_id: str,
    scraper_type: ScraperType,
    error: str,
    retry_count: int,
    max_retries: int
):
    """Notifica falha de tarefa"""
    will_retry = retry_count < max_retries
    
    await connection_manager.broadcast_to_investigation(
        {
            "type": "task_failed" if not will_retry else "task_retrying",
            "investigation_id": investigation_id,
            "task_id": task_id,
            "scraper_type": scraper_type.value,
            "status": TaskStatus.RETRYING.value if will_retry else TaskStatus.FAILED.value,
            "error": error,
            "retry_count": retry_count,
            "max_retries": max_retries,
            "will_retry": will_retry,
            "timestamp": datetime.utcnow().isoformat(),
            "message": (
                f"🔄 Scraper {scraper_type.value} falhou. Tentando novamente ({retry_count}/{max_retries})..."
                if will_retry
                else f"❌ Scraper {scraper_type.value} falhou após {retry_count} tentativas: {error}"
            )
        },
        investigation_id
    )


async def notify_investigation_progress(investigation_id: str, progress: dict):
    """Notifica progresso geral da investigação"""
    total = progress.get("total_tasks", 0)
    completed = progress.get("completed_tasks", 0)
    failed = progress.get("failed_tasks", 0)
    running = progress.get("running_tasks", 0)
    
    percentage = (completed + failed) / total * 100 if total > 0 else 0
    
    await connection_manager.broadcast_to_investigation(
        {
            "type": "investigation_progress",
            "investigation_id": investigation_id,
            "total_tasks": total,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "running_tasks": running,
            "pending_tasks": total - completed - failed - running,
            "percentage": round(percentage, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"📊 Progresso: {completed}/{total} tarefas concluídas ({percentage:.0f}%)"
        },
        investigation_id
    )


async def notify_circuit_breaker_opened(scraper_type: ScraperType, failures: int):
    """Notifica abertura de circuit breaker"""
    await connection_manager.broadcast_to_all(
        {
            "type": "circuit_breaker_opened",
            "scraper_type": scraper_type.value,
            "failures": failures,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"⚡ ALERTA: Circuit breaker aberto para {scraper_type.value} após {failures} falhas consecutivas"
        }
    )


async def notify_system_alert(message: str, level: str = "warning"):
    """Notifica alerta do sistema para todos os usuários"""
    await connection_manager.broadcast_to_all(
        {
            "type": "system_alert",
            "level": level,  # info, warning, error
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
