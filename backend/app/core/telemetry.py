"""
OpenTelemetry — tracing distribuído (API FastAPI e workers Celery).
Activa com OTEL_ENABLED=true e OTEL_EXPORTER_OTLP_ENDPOINT (HTTP/protobuf).
"""

from __future__ import annotations

import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_tracer_provider: Optional[object] = None
_fastapi_apps_instrumented: set[int] = set()
_celery_apps_instrumented: set[int] = set()


def ensure_trace_provider() -> None:
    """
    Inicializa o TracerProvider uma vez por processo (API ou worker Celery).
    """
    global _tracer_provider
    if _tracer_provider is not None:
        return
    if not settings.OTEL_ENABLED:
        return
    if not settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        logger.warning("OTEL_ENABLED sem OTEL_EXPORTER_OTLP_ENDPOINT — tracing OTLP desactivado")
        return

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create(
        {
            "service.name": settings.OTEL_SERVICE_NAME,
            "deployment.environment": settings.ENVIRONMENT,
        }
    )
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    _tracer_provider = provider
    logger.info(
        "OpenTelemetry: TracerProvider configurado → %s", settings.OTEL_EXPORTER_OTLP_ENDPOINT
    )


def shutdown_trace_provider() -> None:
    global _tracer_provider
    if _tracer_provider is None:
        return
    try:
        _tracer_provider.shutdown()
    except Exception as exc:
        logger.warning("OpenTelemetry shutdown: %s", exc)
    _tracer_provider = None


def instrument_fastapi(app) -> None:
    """Instrumentação automática de pedidos HTTP."""
    if not settings.OTEL_ENABLED:
        return
    app_id = id(app)
    if app_id in _fastapi_apps_instrumented:
        return
    ensure_trace_provider()
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor().instrument_app(
        app,
        excluded_urls="/health,/metrics,/favicon.ico",
    )
    _fastapi_apps_instrumented.add(app_id)


def instrument_celery(celery_app) -> None:
    """Spans por tarefa Celery (requer TracerProvider inicializado no worker)."""
    if not settings.OTEL_ENABLED:
        return
    app_id = id(celery_app)
    if app_id in _celery_apps_instrumented:
        return
    ensure_trace_provider()
    try:
        from opentelemetry.instrumentation.celery import CeleryInstrumentor

        CeleryInstrumentor().instrument(celery_app)
        _celery_apps_instrumented.add(app_id)
        logger.info("OpenTelemetry: Celery instrumentado")
    except Exception as exc:
        logger.warning("OpenTelemetry Celery instrumentation falhou: %s", exc)
