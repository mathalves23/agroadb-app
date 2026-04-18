"""Métricas Prometheus HTTP por endpoint (FastAPI)."""

from __future__ import annotations

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def mount_prometheus_instrumentator(app) -> None:
    if not settings.PROMETHEUS_ENABLED:
        logger.info("Prometheus HTTP metrics desactivadas (PROMETHEUS_ENABLED=false)")
        return
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        path = settings.PROMETHEUS_METRICS_PATH.strip() or "/metrics"
        if not path.startswith("/"):
            path = "/" + path
        Instrumentator(
            should_ignore_untemplated=True,
        ).instrument(
            app
        ).expose(app, endpoint=path, include_in_schema=False)
        logger.info("Prometheus: métricas HTTP em %s", path)
    except Exception as exc:
        logger.warning("Prometheus instrumentador não montado: %s", exc)
