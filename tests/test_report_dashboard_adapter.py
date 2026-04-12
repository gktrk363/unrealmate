# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Dashboard Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter tests for report dashboard extraction slice."""

from __future__ import annotations

import errno
import json
import socket
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

import pytest

from unrealmate.adapters.report.report_core import ReportCoreCollector
from unrealmate.adapters.report.report_dashboard_adapter import ReportDashboardAdapter
from unrealmate.contracts.report_dashboard import DashboardStartRequest


pytest.importorskip("flask")
pytest.importorskip("werkzeug")


def _create_project(tmp_path: Path) -> Path:
    project = tmp_path / "DashboardAdapterProject"
    project.mkdir(parents=True, exist_ok=True)
    (project / "DashboardAdapterProject.uproject").write_text(
        json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
        encoding="utf-8",
    )
    (project / "Source").mkdir(parents=True, exist_ok=True)
    (project / "Source" / "Game.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
    (project / "Source" / "Game.h").write_text("#pragma once\n", encoding="utf-8")
    (project / "Content").mkdir(parents=True, exist_ok=True)
    (project / "Content" / "BP_Test.uasset").write_bytes(b"ASSET")
    (project / "Content" / "Map_Test.umap").write_bytes(b"MAP")
    return project


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def test_dashboard_adapter_no_browser_mode_is_supported(tmp_path: Path) -> None:
    project = _create_project(tmp_path)

    def _should_not_open(_url: str) -> bool:
        raise AssertionError("browser_open should not be called when auto_open_browser=False")

    adapter = ReportDashboardAdapter(browser_open=_should_not_open)
    request = DashboardStartRequest.from_cli(
        path=str(project),
        port=_get_free_port(),
        auto_open_browser=False,
    )

    start_result = adapter.start(request)
    stop_status = adapter.stop(request.host, request.port)

    assert start_result.is_success is True
    assert start_result.startup_status == "started"
    assert start_result.status is not None
    assert start_result.status.browser_opened is False
    assert stop_status.shutdown_status == "clean"


def test_dashboard_adapter_port_conflict_returns_structured_error(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    adapter = ReportDashboardAdapter()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as blocker:
        blocker.bind(("127.0.0.1", 0))
        blocker.listen(1)
        port = int(blocker.getsockname()[1])
        request = DashboardStartRequest.from_cli(
            path=str(project),
            host="127.0.0.1",
            port=port,
            auto_open_browser=False,
        )

        result = adapter.start(request)

    assert result.is_success is False
    assert result.startup_status == "port_in_use"
    assert result.errors[0].code == "report_dashboard_port_in_use"
    assert result.errors[0].message == f"Dashboard could not start because 127.0.0.1:{port} is already in use."
    assert result.errors[0].details == "Stop the existing listener or retry with --port <free-port>."


def test_dashboard_adapter_invalid_host_bind_failure_is_actionable(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = _create_project(tmp_path)
    adapter = ReportDashboardAdapter()
    request = DashboardStartRequest.from_cli(
        path=str(project),
        host="203.0.113.10",
        port=8080,
        auto_open_browser=False,
    )
    monkeypatch.setattr(
        adapter,
        "_probe_socket_bind_error",
        lambda host, port: OSError(errno.EADDRNOTAVAIL, "Cannot assign requested address"),
    )

    result = adapter.start(request)

    assert result.is_success is False
    assert result.startup_status == "startup_failed"
    assert result.errors[0].code == "report_dashboard_startup_failed"
    assert "Dashboard could not bind to 203.0.113.10:8080:" in result.errors[0].message
    assert "Cannot assign requested address" in result.errors[0].message
    assert "--host 127.0.0.1" in result.errors[0].details


def test_dashboard_adapter_startup_timeout_returns_structured_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = _create_project(tmp_path)
    adapter = ReportDashboardAdapter(browser_open=lambda _url: False)
    monkeypatch.setattr(
        adapter,
        "_wait_until_health_ready",
        lambda host, port, timeout_seconds: False,
    )
    request = DashboardStartRequest.from_cli(
        path=str(project),
        port=_get_free_port(),
        auto_open_browser=False,
        startup_timeout_seconds=0.1,
    )

    result = adapter.start(request)

    assert result.is_success is False
    assert result.startup_status == "startup_timeout"
    assert result.errors
    assert result.errors[0].code == "report_dashboard_startup_timeout"
    assert result.errors[0].details == "Retry with a larger --startup-timeout if this machine starts the dashboard slowly."
    assert adapter.stop(request.host, request.port).shutdown_status == "not_running"


def test_dashboard_adapter_startup_payload_is_deterministic_with_fixed_clock(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    fixed_now = datetime(2026, 4, 3, 12, 0, 0)
    collector = ReportCoreCollector(now_provider=lambda: fixed_now)
    adapter = ReportDashboardAdapter(
        collector=collector,
        now_provider=lambda: fixed_now,
        browser_open=lambda _url: True,
    )
    request = DashboardStartRequest.from_cli(
        path=str(project),
        port=_get_free_port(),
        auto_open_browser=True,
    )

    result = adapter.start(request)
    payload = result.to_payload()
    adapter.stop(request.host, request.port)

    assert result.is_success is True
    assert payload["startup_status"] == "started"
    assert payload["status"]["started_at_iso"] == "2026-04-03T12:00:00"
    assert payload["status"]["startup_status"] == "started"
    assert payload["snapshot"]["generated_at_iso"] == "2026-04-03T12:00:00"
    assert payload["snapshot"]["project_name"] == "DashboardAdapterProject"
    assert payload["snapshot"]["stats"] == {
        "blueprint_assets": 1,
        "cpp_source_files": 2,
        "scene_maps": 1,
        "uproject_files": 1,
    }


def test_dashboard_adapter_report_core_snapshot_is_exposed_to_dashboard_api(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    adapter = ReportDashboardAdapter(browser_open=lambda _url: False)
    request = DashboardStartRequest.from_cli(
        path=str(project),
        port=_get_free_port(),
        auto_open_browser=False,
    )

    result = adapter.start(request)
    assert result.is_success is True
    assert result.url is not None
    try:
        with urlopen(f"{result.url}/api/health", timeout=2) as response:
            payload = json.loads(response.read().decode("utf-8"))
    finally:
        adapter.stop(request.host, request.port)

    assert "report_core" in payload
    assert payload["report_core"]["project_name"] == "DashboardAdapterProject"
    assert payload["report_core"]["project_path"] == str(project.resolve())
    assert payload["report_core"]["stats"]["uproject_files"] == 1


def test_dashboard_adapter_lifecycle_start_stop_status_is_consistent(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    adapter = ReportDashboardAdapter(browser_open=lambda _url: False)
    request = DashboardStartRequest.from_cli(
        path=str(project),
        port=_get_free_port(),
        auto_open_browser=False,
    )

    started = adapter.start(request)
    stopped = adapter.stop(request.host, request.port)
    stopped_again = adapter.stop(request.host, request.port)

    assert started.is_success is True
    assert started.status is not None
    assert started.status.state == "running"
    assert stopped.state == "stopped"
    assert stopped.shutdown_status == "clean"
    assert stopped_again.shutdown_status == "not_running"


def test_dashboard_adapter_browser_open_monkeypatch_path(tmp_path: Path, monkeypatch) -> None:
    project = _create_project(tmp_path)
    calls: list[str] = []

    def _fake_open(url: str) -> bool:
        calls.append(url)
        return True

    monkeypatch.setattr(
        "unrealmate.adapters.report.report_dashboard_adapter.webbrowser.open",
        _fake_open,
    )

    adapter = ReportDashboardAdapter()
    request = DashboardStartRequest.from_cli(
        path=str(project),
        port=_get_free_port(),
        auto_open_browser=True,
    )

    result = adapter.start(request)
    adapter.stop(request.host, request.port)

    assert result.is_success is True
    assert result.status is not None
    assert result.status.browser_opened is True
    assert calls == [result.url]


def test_dashboard_adapter_browser_open_failure_is_warning_not_fatal(tmp_path: Path) -> None:
    project = _create_project(tmp_path)

    def _raise_browser_error(_url: str) -> bool:
        raise RuntimeError("headless environment")

    adapter = ReportDashboardAdapter(browser_open=_raise_browser_error)
    request = DashboardStartRequest.from_cli(
        path=str(project),
        port=_get_free_port(),
        auto_open_browser=True,
    )

    result = adapter.start(request)
    adapter.stop(request.host, request.port)

    assert result.is_success is True
    assert result.status is not None
    assert result.status.browser_opened is False
    assert result.warnings
    assert any(w.code == "report_dashboard_browser_open_failed" for w in result.warnings)
    assert any("--no-open" in w.message for w in result.warnings)


def test_dashboard_adapter_stop_timeout_status_is_reported(tmp_path: Path, monkeypatch) -> None:
    project = _create_project(tmp_path)
    adapter = ReportDashboardAdapter(browser_open=lambda _url: False)
    request = DashboardStartRequest.from_cli(
        path=str(project),
        port=_get_free_port(),
        auto_open_browser=False,
    )

    started = adapter.start(request)
    assert started.is_success is True

    monkeypatch.setattr(
        adapter,
        "_shutdown_runtime_server",
        lambda server, thread, timeout_seconds: "timeout",
    )
    stop_status = adapter.stop(request.host, request.port)

    assert stop_status.shutdown_status == "timeout"
    assert stop_status.state == "failed"


def test_dashboard_adapter_stop_failed_keeps_runtime_for_retry(tmp_path: Path, monkeypatch) -> None:
    project = _create_project(tmp_path)
    adapter = ReportDashboardAdapter(browser_open=lambda _url: False)
    request = DashboardStartRequest.from_cli(
        path=str(project),
        port=_get_free_port(),
        auto_open_browser=False,
    )

    started = adapter.start(request)
    assert started.is_success is True

    original_shutdown = adapter._shutdown_runtime_server
    call_count = {"value": 0}

    def _flaky_shutdown(server, thread, timeout_seconds):
        call_count["value"] += 1
        if call_count["value"] == 1:
            return "failed"
        return original_shutdown(server=server, thread=thread, timeout_seconds=timeout_seconds)

    monkeypatch.setattr(adapter, "_shutdown_runtime_server", _flaky_shutdown)

    first_stop = adapter.stop(request.host, request.port)
    second_stop = adapter.stop(request.host, request.port)

    assert first_stop.shutdown_status == "failed"
    assert second_stop.shutdown_status == "clean"
    assert call_count["value"] == 2
