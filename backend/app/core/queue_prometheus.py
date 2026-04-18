"""
Métricas Prometheus para filas Redis e circuit breakers de scrapers.

Expõe gauges actualizados periodicamente pela API (lifespan) e contadores
em transições críticas. Requer PROMETHEUS_ENABLED e Redis ligado ao queue_manager.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from prometheus_client import Counter, Gauge

from app.core.config import settings

if TYPE_CHECKING:
    from app.core.queue import QueueManager

logger = logging.getLogger(__name__)

QUEUE_TASKS = Gauge(
    "agroadb_queue_tasks",
    "Número de tarefas pendentes na fila Redis por tipo de scraper e prioridade",
    ["scraper_type", "priority"],
)
SCRAPER_CIRCUIT_OPEN = Gauge(
    "agroadb_scraper_circuit_breaker_open",
    "1 se o circuit breaker Redis do scraper estiver aberto",
    ["scraper_type"],
)
SCRAPER_CIRCUIT_OPENED_TOTAL = Counter(
    "agroadb_scraper_circuit_breaker_opened_total",
    "Transições para circuito aberto (filas Redis)",
    ["scraper_type"],
)
EXTERNAL_CIRCUIT_OPEN = Gauge(
    "agroadb_external_circuit_breaker_open",
    "1 se o circuit breaker in-memory (HTTP/serviços externos) estiver OPEN",
    ["name"],
)


def scraper_circuit_opened(scraper_type: str) -> None:
    """Chamar quando o circuit Redis abrir (transição)."""
    if not settings.PROMETHEUS_ENABLED:
        return
    SCRAPER_CIRCUIT_OPENED_TOTAL.labels(scraper_type=scraper_type).inc()
    SCRAPER_CIRCUIT_OPEN.labels(scraper_type=scraper_type).set(1)


def scraper_circuit_closed(scraper_type: str) -> None:
    if not settings.PROMETHEUS_ENABLED:
        return
    SCRAPER_CIRCUIT_OPEN.labels(scraper_type=scraper_type).set(0)


async def refresh_queue_and_registry_gauges(queue_manager: QueueManager) -> None:
    """Actualiza gauges de filas, circuitos Redis e circuitos externos."""
    if not settings.PROMETHEUS_ENABLED:
        return
    try:
        from app.core.circuit_breaker import CircuitBreakerRegistry
        from app.core.queue import ScraperType, TaskPriority

        if queue_manager.redis_client:
            for st in ScraperType:
                for pr in TaskPriority:
                    qkey = queue_manager._get_queue_key(st, pr)
                    n = await queue_manager.redis_client.zcard(qkey)
                    QUEUE_TASKS.labels(scraper_type=st.value, priority=pr.name).set(float(n))
                circ = await queue_manager.get_circuit_status(st)
                SCRAPER_CIRCUIT_OPEN.labels(scraper_type=st.value).set(
                    1.0 if circ["is_open"] else 0.0
                )

        for row in CircuitBreakerRegistry.get_all_status():
            name = str(row.get("name", "unknown"))
            is_open = 1.0 if row.get("state") == "open" else 0.0
            EXTERNAL_CIRCUIT_OPEN.labels(name=name).set(is_open)
    except Exception as exc:
        logger.debug("refresh_queue_and_registry_gauges: %s", exc)


async def prometheus_gauge_refresh_loop(
    queue_manager: QueueManager, interval_seconds: float = 15.0
) -> None:
    """Loop em background até cancelado."""
    while True:
        await refresh_queue_and_registry_gauges(queue_manager)
        await asyncio.sleep(interval_seconds)
