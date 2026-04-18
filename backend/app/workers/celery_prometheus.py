"""
Métricas Prometheus por tarefa Celery + HTTP opcional no worker.

- ``celery_task_runs_total{task_name,state}``
- ``celery_task_duration_seconds_bucket`` (histograma)
- Com ``CELERY_METRICS_PORT > 0``, expõe ``/metrics`` no processo worker.
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from celery import signals
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

_CELERY_TASK_RUNS = Counter(
    "celery_task_runs_total",
    "Total de execuções de tarefas Celery",
    ["task_name", "state"],
)
_CELERY_TASK_DURATION = Histogram(
    "celery_task_duration_seconds",
    "Duração das tarefas Celery",
    ["task_name"],
    buckets=(0.5, 1, 2, 5, 15, 30, 60, 120, 300, float("inf")),
)

_http_started = False


@signals.task_prerun.connect
def _task_prerun(sender=None, task_id=None, task=None, **kwargs):
    if task is not None:
        task._prom_start = time.perf_counter()


@signals.task_postrun.connect
def _task_postrun(sender=None, task_id=None, task=None, state=None, **kwargs):
    if task is None:
        return
    name = getattr(task, "name", None) or getattr(sender, "name", "unknown")
    st = state or "UNKNOWN"
    _CELERY_TASK_RUNS.labels(task_name=name, state=st).inc()
    start = getattr(task, "_prom_start", None)
    if start is not None:
        _CELERY_TASK_DURATION.labels(task_name=name).observe(time.perf_counter() - start)


@signals.worker_init.connect
def _worker_init_prometheus(**kwargs):
    global _http_started
    from app.core.config import settings

    if settings.CELERY_METRICS_PORT <= 0 or _http_started:
        return
    try:
        from prometheus_client import start_http_server

        start_http_server(settings.CELERY_METRICS_PORT)
        _http_started = True
        logger.info(
            "Prometheus: worker a expor métricas em 0.0.0.0:%s/metrics",
            settings.CELERY_METRICS_PORT,
        )
    except Exception as exc:
        logger.warning("Prometheus worker HTTP não iniciado: %s", exc)
