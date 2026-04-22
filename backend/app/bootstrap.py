"""Funções de bootstrap da aplicação para reduzir side effects no app HTTP."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.circuit_breaker import CircuitBreakerRegistry
from app.core.config import settings
from app.core.database import Base
from app.core.indexes import create_optimized_indexes
from app.core.queue import queue_manager
from app.core.queue_prometheus import (
    prometheus_gauge_refresh_loop,
    refresh_queue_and_registry_gauges,
)
from app.workers.scraper_workers import orchestrator

logger = logging.getLogger(__name__)


@dataclass
class StartupState:
    workers_started: bool = False
    queue_connected: bool = False
    prometheus_queue_task: asyncio.Task | None = None


async def prepare_persistence(engine: AsyncEngine) -> None:
    """Executa tarefas de DB opcionais do startup web."""
    if settings.AUTO_CREATE_SCHEMA:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    if settings.AUTO_CREATE_INDEXES:
        await create_optimized_indexes(engine)


async def maybe_start_workers() -> bool:
    """Inicia workers em background apenas quando explicitamente habilitado."""
    if not settings.ENABLE_WORKERS:
        logger.info("Workers desabilitados (ENABLE_WORKERS=false)")
        return False

    asyncio.create_task(orchestrator.start_all_workers())
    logger.info("Workers iniciados em background")
    return True


async def maybe_connect_queue() -> bool:
    """Conecta Redis da fila apenas quando explicitamente permitido."""
    if not settings.CONNECT_QUEUE_ON_STARTUP:
        logger.info("Conexao com fila desabilitada no startup web (CONNECT_QUEUE_ON_STARTUP=false)")
        return False

    try:
        await queue_manager.connect()
        return True
    except Exception as exc:  # pragma: no cover - defensivo para ambiente externo
        logger.warning("Fila Redis indisponivel no startup web (%s)", exc)
        return False


async def maybe_start_prometheus_queue_refresh(queue_connected: bool) -> asyncio.Task | None:
    """Liga refresh de gauges de filas/circuit-breakers quando permitido."""
    if not settings.PROMETHEUS_ENABLED or not queue_connected:
        return None

    await refresh_queue_and_registry_gauges(queue_manager)
    logger.info("Metricas Prometheus de filas/circuitos: refresh periodico ativo")
    return asyncio.create_task(prometheus_gauge_refresh_loop(queue_manager))


async def startup_application(engine: AsyncEngine) -> StartupState:
    """Executa startup minimizando acoplamento com o app HTTP."""
    await prepare_persistence(engine)
    workers_started = await maybe_start_workers()
    queue_connected = await maybe_connect_queue()
    prometheus_queue_task = await maybe_start_prometheus_queue_refresh(queue_connected)
    return StartupState(
        workers_started=workers_started,
        queue_connected=queue_connected,
        prometheus_queue_task=prometheus_queue_task,
    )


async def shutdown_application(engine: AsyncEngine, state: StartupState) -> None:
    """Executa shutdown correspondente ao startup."""
    from app.core.telemetry import shutdown_trace_provider

    shutdown_trace_provider()

    if state.prometheus_queue_task is not None:
        state.prometheus_queue_task.cancel()
        try:
            await state.prometheus_queue_task
        except asyncio.CancelledError:
            pass

    if state.workers_started:
        await orchestrator.stop_all_workers()

    if state.queue_connected:
        await queue_manager.disconnect()

    await engine.dispose()


async def get_circuit_breaker_status() -> dict[str, dict]:
    """Mantém ponto único para expor estado dos circuit breakers."""
    return CircuitBreakerRegistry.get_all_status()
