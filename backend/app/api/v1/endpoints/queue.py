"""
Endpoints de WebSocket e Monitoramento de Filas
"""
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.websocket import connection_manager
from app.core.queue import queue_manager, ScraperType, TaskPriority
from app.workers.scraper_workers import (
    enqueue_investigation_scrapers,
    enqueue_single_scraper,
    get_task_status,
    cancel_investigation_scrapers
)
from app.api.v1.deps import get_current_user
from app.domain.user import User

router = APIRouter()


# ==================== WebSocket Endpoints ====================


@router.websocket("/ws/investigations/{investigation_id}")
async def investigation_websocket(
    websocket: WebSocket,
    investigation_id: str,
    # TODO: Adicionar autenticação via query param ou token
    # user_token: str = Query(...)
):
    """
    WebSocket para notificações em tempo real de uma investigação
    
    **Como usar:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/investigations/123?user_token=...');
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Notificação:', data);
        
        if (data.type === 'task_completed') {
            console.log(`Scraper ${data.scraper_type} concluído!`);
        }
    };
    ```
    
    **Tipos de mensagens recebidas:**
    - `connected`: Conexão estabelecida
    - `task_started`: Scraper iniciado
    - `task_completed`: Scraper concluído
    - `task_failed`: Scraper falhou
    - `task_retrying`: Scraper em retry
    - `investigation_progress`: Atualização de progresso
    - `circuit_breaker_opened`: Circuit breaker aberto
    - `system_alert`: Alerta do sistema
    """
    # TODO: Validar token e obter user_id
    user_id = "temp_user"  # Temporário
    
    await connection_manager.connect(websocket, investigation_id, user_id)
    
    try:
        while True:
            # Manter conexão ativa
            data = await websocket.receive_text()
            
            # Cliente pode enviar 'ping' para manter conexão
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, investigation_id)


# ==================== Queue Management Endpoints ====================


@router.post("/investigations/{investigation_id}/start")
async def start_investigation(
    investigation_id: str,
    target_name: Optional[str] = None,
    target_cpf_cnpj: Optional[str] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    priority: str = "normal",
    # current_user: User = Depends(get_current_user)
):
    """
    Inicia investigação enfileirando todos os scrapers
    
    **Prioridades disponíveis:**
    - `critical`: Urgente (prioridade 1)
    - `high`: Alta (prioridade 2)
    - `normal`: Normal (prioridade 3) - padrão
    - `low`: Baixa (prioridade 4)
    - `background`: Background (prioridade 5)
    
    **Exemplo:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/investigations/123/start" \\
         -H "Content-Type: application/json" \\
         -d '{
           "target_name": "João Silva",
           "target_cpf_cnpj": "123.456.789-00",
           "state": "MT",
           "priority": "high"
         }'
    ```
    """
    # Converter string de prioridade para enum
    priority_map = {
        "critical": TaskPriority.CRITICAL,
        "high": TaskPriority.HIGH,
        "normal": TaskPriority.NORMAL,
        "low": TaskPriority.LOW,
        "background": TaskPriority.BACKGROUND
    }
    
    task_priority = priority_map.get(priority.lower(), TaskPriority.NORMAL)
    
    # Enfileirar scrapers
    task_ids = await enqueue_investigation_scrapers(
        investigation_id=investigation_id,
        target_name=target_name,
        target_cpf_cnpj=target_cpf_cnpj,
        state=state,
        city=city,
        priority=task_priority
    )
    
    return {
        "status": "success",
        "message": f"{len(task_ids)} scrapers enfileirados",
        "investigation_id": investigation_id,
        "task_ids": task_ids,
        "priority": priority
    }


@router.post("/investigations/{investigation_id}/scrapers/{scraper_type}")
async def start_single_scraper(
    investigation_id: str,
    scraper_type: str,
    target_name: Optional[str] = None,
    target_cpf_cnpj: Optional[str] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    priority: str = "normal",
    max_retries: int = 3,
    # current_user: User = Depends(get_current_user)
):
    """
    Inicia um scraper específico
    
    **Scrapers disponíveis:**
    - `car`: CAR (Cadastro Ambiental Rural)
    - `incra`: INCRA (SNCR)
    - `receita`: Receita Federal
    - `diario_oficial`: Diários Oficiais
    - `cartorios`: Cartórios
    - `sigef_sicar`: SIGEF/SICAR
    
    **Exemplo:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/investigations/123/scrapers/receita" \\
         -H "Content-Type: application/json" \\
         -d '{
           "target_cpf_cnpj": "12.345.678/0001-90",
           "priority": "high"
         }'
    ```
    """
    try:
        scraper_enum = ScraperType(scraper_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de scraper inválido: {scraper_type}"
        )
    
    priority_map = {
        "critical": TaskPriority.CRITICAL,
        "high": TaskPriority.HIGH,
        "normal": TaskPriority.NORMAL,
        "low": TaskPriority.LOW,
        "background": TaskPriority.BACKGROUND
    }
    
    task_priority = priority_map.get(priority.lower(), TaskPriority.NORMAL)
    
    params = {
        "name": target_name,
        "cpf_cnpj": target_cpf_cnpj,
        "state": state,
        "city": city
    }
    
    task_id = await enqueue_single_scraper(
        investigation_id=investigation_id,
        scraper_type=scraper_enum,
        params=params,
        priority=task_priority,
        max_retries=max_retries
    )
    
    if task_id:
        return {
            "status": "success",
            "message": f"Scraper {scraper_type} enfileirado",
            "investigation_id": investigation_id,
            "scraper_type": scraper_type,
            "task_id": task_id
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Falha ao enfileirar scraper"
        )


@router.get("/investigations/{investigation_id}/progress")
async def get_investigation_progress(
    investigation_id: str,
    # current_user: User = Depends(get_current_user)
):
    """
    Retorna progresso de uma investigação
    
    **Exemplo de resposta:**
    ```json
    {
      "investigation_id": "123",
      "total_tasks": 6,
      "completed_tasks": 3,
      "failed_tasks": 1,
      "running_tasks": 1,
      "pending_tasks": 1,
      "percentage": 66.67,
      "tasks": {
        "123_car_abc123": "completed",
        "123_incra_def456": "completed",
        "123_receita_ghi789": "running",
        ...
      }
    }
    ```
    """
    await queue_manager.connect()
    
    progress = await queue_manager.get_investigation_progress(investigation_id)
    
    if not progress:
        raise HTTPException(
            status_code=404,
            detail="Investigação não encontrada ou sem progresso"
        )
    
    total = progress.get("total_tasks", 0)
    completed = progress.get("completed_tasks", 0)
    failed = progress.get("failed_tasks", 0)
    running = progress.get("running_tasks", 0)
    
    return {
        **progress,
        "pending_tasks": total - completed - failed - running,
        "percentage": round((completed + failed) / total * 100, 2) if total > 0 else 0
    }


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    # current_user: User = Depends(get_current_user)
):
    """
    Retorna status de uma task específica
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8000/api/v1/tasks/123_car_abc123"
    ```
    """
    status = await get_task_status(task_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail="Task não encontrada"
        )
    
    return status


@router.delete("/investigations/{investigation_id}/cancel")
async def cancel_investigation(
    investigation_id: str,
    # current_user: User = Depends(get_current_user)
):
    """
    Cancela todos os scrapers pendentes de uma investigação
    
    **Exemplo:**
    ```bash
    curl -X DELETE "http://localhost:8000/api/v1/investigations/123/cancel"
    ```
    """
    cancelled_count = await cancel_investigation_scrapers(investigation_id)
    
    return {
        "status": "success",
        "message": f"{cancelled_count} tasks canceladas",
        "investigation_id": investigation_id,
        "cancelled_count": cancelled_count
    }


# ==================== Monitoring Endpoints ====================


@router.get("/queue/stats")
async def get_queue_stats(
    scraper_type: Optional[str] = None,
    # current_user: User = Depends(get_current_user)
):
    """
    Retorna estatísticas das filas
    
    **Exemplo:**
    ```bash
    # Todas as filas
    curl "http://localhost:8000/api/v1/queue/stats"
    
    # Fila específica
    curl "http://localhost:8000/api/v1/queue/stats?scraper_type=car"
    ```
    
    **Resposta:**
    ```json
    {
      "car": {
        "total": 15,
        "by_priority": {
          "CRITICAL": 2,
          "HIGH": 5,
          "NORMAL": 6,
          "LOW": 2,
          "BACKGROUND": 0
        },
        "circuit_breaker": {
          "scraper_type": "car",
          "is_open": false,
          "failures": 0,
          "threshold": 5
        }
      },
      ...
    }
    ```
    """
    await queue_manager.connect()
    
    scraper_enum = None
    if scraper_type:
        try:
            scraper_enum = ScraperType(scraper_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de scraper inválido: {scraper_type}"
            )
    
    stats = await queue_manager.get_queue_stats(scraper_enum)
    
    return stats


@router.get("/websocket/stats")
async def get_websocket_stats(
    # current_user: User = Depends(get_current_user)
):
    """
    Retorna estatísticas de conexões WebSocket
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8000/api/v1/websocket/stats"
    ```
    
    **Resposta:**
    ```json
    {
      "total_connections": 12,
      "active_investigations": 5,
      "connections_by_investigation": {
        "123": 3,
        "456": 2,
        ...
      }
    }
    ```
    """
    return connection_manager.get_stats()


@router.get("/circuit-breaker/{scraper_type}")
async def get_circuit_breaker_status(
    scraper_type: str,
    # current_user: User = Depends(get_current_user)
):
    """
    Retorna status do circuit breaker de um scraper
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8000/api/v1/circuit-breaker/car"
    ```
    """
    try:
        scraper_enum = ScraperType(scraper_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de scraper inválido: {scraper_type}"
        )
    
    await queue_manager.connect()
    
    status = await queue_manager.get_circuit_status(scraper_enum)
    
    return status


@router.get("/health")
async def health_check():
    """
    Health check do sistema de filas
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8000/api/v1/health"
    ```
    """
    try:
        await queue_manager.connect()
        
        # Verificar conexão Redis
        stats = await queue_manager.get_queue_stats()
        
        return {
            "status": "healthy",
            "redis": "connected",
            "websocket_connections": connection_manager.get_connection_count(),
            "total_queued_tasks": sum(
                s["total"] for s in stats.values()
            )
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )
