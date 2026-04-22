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
async def test_startup_application_orchestrates_bootstrap_steps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepare_persistence = AsyncMock()
    maybe_start_workers = AsyncMock(return_value=True)
    maybe_connect_queue = AsyncMock(return_value=True)
    prometheus_task = object()
    maybe_start_prometheus_queue_refresh = AsyncMock(return_value=prometheus_task)

    class DummyEngine:
        pass

    monkeypatch.setattr(bootstrap, "prepare_persistence", prepare_persistence)
    monkeypatch.setattr(bootstrap, "maybe_start_workers", maybe_start_workers)
    monkeypatch.setattr(bootstrap, "maybe_connect_queue", maybe_connect_queue)
    monkeypatch.setattr(
        bootstrap,
        "maybe_start_prometheus_queue_refresh",
        maybe_start_prometheus_queue_refresh,
    )

    state = await bootstrap.startup_application(DummyEngine())  # type: ignore[arg-type]

    prepare_persistence.assert_awaited_once()
    maybe_start_workers.assert_awaited_once_with()
    maybe_connect_queue.assert_awaited_once_with()
    maybe_start_prometheus_queue_refresh.assert_awaited_once_with(True)
    assert state == bootstrap.StartupState(
        workers_started=True,
        queue_connected=True,
        prometheus_queue_task=prometheus_task,
    )


@pytest.mark.asyncio
async def test_maybe_start_workers_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap.settings, "ENABLE_WORKERS", False)
    started = await bootstrap.maybe_start_workers()
    assert started is False


@pytest.mark.asyncio
async def test_maybe_start_workers_enabled_starts_background_task(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_tasks: list[object] = []

    async def start_all_workers() -> None:
        return None

    def fake_create_task(coro):
        created_tasks.append(coro)
        coro.close()
        return object()

    monkeypatch.setattr(bootstrap.settings, "ENABLE_WORKERS", True)
    monkeypatch.setattr(bootstrap.orchestrator, "start_all_workers", start_all_workers)
    monkeypatch.setattr(bootstrap.asyncio, "create_task", fake_create_task)

    started = await bootstrap.maybe_start_workers()

    assert started is True
    assert len(created_tasks) == 1


@pytest.mark.asyncio
async def test_maybe_start_prometheus_queue_refresh_skips_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bootstrap.settings, "PROMETHEUS_ENABLED", False)
    task = await bootstrap.maybe_start_prometheus_queue_refresh(queue_connected=True)
    assert task is None


@pytest.mark.asyncio
async def test_maybe_start_prometheus_queue_refresh_runs_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    refresh_metrics = AsyncMock()
    created_tasks: list[object] = []
    sentinel_task = object()

    async def refresh_loop(_queue_manager) -> None:
        return None

    def fake_create_task(coro):
        created_tasks.append(coro)
        coro.close()
        return sentinel_task

    monkeypatch.setattr(bootstrap.settings, "PROMETHEUS_ENABLED", True)
    monkeypatch.setattr(bootstrap, "refresh_queue_and_registry_gauges", refresh_metrics)
    monkeypatch.setattr(bootstrap, "prometheus_gauge_refresh_loop", refresh_loop)
    monkeypatch.setattr(bootstrap.asyncio, "create_task", fake_create_task)

    task = await bootstrap.maybe_start_prometheus_queue_refresh(queue_connected=True)

    refresh_metrics.assert_awaited_once_with(bootstrap.queue_manager)
    assert task is sentinel_task
    assert len(created_tasks) == 1


@pytest.mark.asyncio
async def test_maybe_connect_queue_skips_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap.settings, "CONNECT_QUEUE_ON_STARTUP", False)
    connected = await bootstrap.maybe_connect_queue()
    assert connected is False


@pytest.mark.asyncio
async def test_maybe_connect_queue_handles_external_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def broken_connect() -> None:
        raise RuntimeError("redis down")

    monkeypatch.setattr(bootstrap.settings, "CONNECT_QUEUE_ON_STARTUP", True)
    monkeypatch.setattr(bootstrap.queue_manager, "connect", broken_connect)

    connected = await bootstrap.maybe_connect_queue()

    assert connected is False


@pytest.mark.asyncio
async def test_shutdown_application_stops_started_services(monkeypatch: pytest.MonkeyPatch) -> None:
    engine_dispose = AsyncMock()
    stop_workers = AsyncMock()
    disconnect_queue = AsyncMock()
    shutdown_trace_provider = Mock()

    class DummyEngine:
        dispose = engine_dispose

    async def sleepy() -> None:
        await asyncio.sleep(3600)

    task = asyncio.create_task(sleepy())
    monkeypatch.setattr(bootstrap.orchestrator, "stop_all_workers", stop_workers)
    monkeypatch.setattr(bootstrap.queue_manager, "disconnect", disconnect_queue)
    monkeypatch.setattr(
        "app.core.telemetry.shutdown_trace_provider",
        shutdown_trace_provider,
        raising=False,
    )

    await bootstrap.shutdown_application(
        DummyEngine(),
        bootstrap.StartupState(
            workers_started=True,
            queue_connected=True,
            prometheus_queue_task=task,
        ),
    )

    stop_workers.assert_awaited_once()
    disconnect_queue.assert_awaited_once()
    engine_dispose.assert_awaited_once()
    shutdown_trace_provider.assert_called_once()
    assert task.cancelled()
