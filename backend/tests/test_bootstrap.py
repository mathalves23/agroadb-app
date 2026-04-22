from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from app import bootstrap


@pytest.mark.asyncio
async def test_prepare_persistence_respects_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    create_all = AsyncMock()
    create_indexes = AsyncMock()

    class DummyBegin:
        async def __aenter__(self):
            class DummyConn:
                async def run_sync(self, fn):
                    await create_all(fn)

            return DummyConn()

        async def __aexit__(self, exc_type, exc, tb):
            return None

    class DummyEngine:
        def begin(self):
            return DummyBegin()

    monkeypatch.setattr(bootstrap.settings, "AUTO_CREATE_SCHEMA", True)
    monkeypatch.setattr(bootstrap.settings, "AUTO_CREATE_INDEXES", True)
    monkeypatch.setattr(bootstrap, "create_optimized_indexes", create_indexes)

    await bootstrap.prepare_persistence(DummyEngine())  # type: ignore[arg-type]

    create_all.assert_awaited_once()
    create_indexes.assert_awaited_once()


@pytest.mark.asyncio
async def test_maybe_start_workers_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap.settings, "ENABLE_WORKERS", False)
    started = await bootstrap.maybe_start_workers()
    assert started is False


@pytest.mark.asyncio
async def test_maybe_start_prometheus_queue_refresh_skips_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bootstrap.settings, "PROMETHEUS_ENABLED", False)
    task = await bootstrap.maybe_start_prometheus_queue_refresh()
    assert task is None


@pytest.mark.asyncio
async def test_shutdown_application_stops_started_services(monkeypatch: pytest.MonkeyPatch) -> None:
    engine_dispose = AsyncMock()
    stop_workers = AsyncMock()
    shutdown_trace_provider = Mock()

    class DummyEngine:
        dispose = engine_dispose

    async def sleepy() -> None:
        await asyncio.sleep(3600)

    task = asyncio.create_task(sleepy())
    monkeypatch.setattr(bootstrap.orchestrator, "stop_all_workers", stop_workers)
    monkeypatch.setattr(
        "app.core.telemetry.shutdown_trace_provider",
        shutdown_trace_provider,
        raising=False,
    )

    await bootstrap.shutdown_application(
        DummyEngine(), bootstrap.StartupState(workers_started=True, prometheus_queue_task=task)
    )

    stop_workers.assert_awaited_once()
    engine_dispose.assert_awaited_once()
    shutdown_trace_provider.assert_called_once()
    assert task.cancelled()
