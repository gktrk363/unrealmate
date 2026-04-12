# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Dashboard Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for report dashboard extraction slice."""

from __future__ import annotations

from pathlib import Path
import re

from typer.testing import CliRunner

import unrealmate.cli as cli
from unrealmate.contracts.report_dashboard import (
    DashboardError,
    DashboardStartRequest,
    DashboardStartResult,
    DashboardStatus,
)


runner = CliRunner()


def test_report_dashboard_cli_no_open_and_keyboard_interrupt_stop_signal_is_stable(
    monkeypatch,
    tmp_path: Path,
) -> None:
    project = tmp_path / "DashboardCliProject"
    project.mkdir(parents=True, exist_ok=True)
    captured: dict[str, DashboardStartRequest] = {}

    class _FakeUseCase:
        def execute(self, request: DashboardStartRequest) -> DashboardStartResult:
            captured["start_request"] = request
            return DashboardStartResult(
                project_path=request.project_path,
                startup_status="started",
                url=f"http://{request.host}:{request.port}",
                status=DashboardStatus(
                    state="running",
                    host=request.host,
                    port=request.port,
                    startup_status="started",
                    url=f"http://{request.host}:{request.port}",
                    browser_opened=False,
                ),
            )

        def stop(self, request: DashboardStartRequest) -> DashboardStatus:
            captured["stop_request"] = request
            return DashboardStatus(
                state="stopped",
                host=request.host,
                port=request.port,
                startup_status="stopped",
                url=f"http://{request.host}:{request.port}",
                shutdown_status="clean",
            )

    monkeypatch.setattr(cli, "StartReportDashboardUseCase", _FakeUseCase)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli.time, "sleep", lambda _seconds: (_ for _ in ()).throw(KeyboardInterrupt()))

    result = runner.invoke(
        cli.app,
        ["report", "dashboard", str(project), "--port", "8899", "--no-open"],
        catch_exceptions=False,
    )

    normalized_output = re.sub(r"\s+", " ", result.output)
    assert result.exit_code == 0
    assert "Experimental local dashboard is running." in result.output
    assert "Open at http://127.0.0.1:8899" in result.output
    assert "Secondary surface only: use report json" in normalized_output
    assert "stable local report artifacts." in normalized_output
    assert "Headless mode active (--no-open);" in normalized_output
    assert "no browser was opened." in normalized_output
    assert "Press Ctrl+C to stop the local dashboard server" in result.output
    assert "Stopping dashboard..." in result.output
    assert "Local dashboard stopped." in result.output
    assert captured["start_request"].auto_open_browser is False
    assert captured["start_request"].port == 8899
    assert captured["stop_request"].port == 8899


def test_report_dashboard_cli_help_truth_is_stable() -> None:
    result = runner.invoke(
        cli.app,
        ["report", "dashboard", "--help"],
        catch_exceptions=False,
    )

    normalized_output = re.sub(r"\s+", " ", result.output)
    assert result.exit_code == 0
    assert "experimental" in normalized_output
    assert "secondary view over project report data" in normalized_output
    assert "Use report json" in normalized_output
    assert "stable local report artifacts" in normalized_output


def test_report_dashboard_cli_port_conflict_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "DashboardCliPortConflict"
    project.mkdir(parents=True, exist_ok=True)

    class _FakeUseCase:
        def execute(self, request: DashboardStartRequest) -> DashboardStartResult:
            return DashboardStartResult(
                project_path=request.project_path,
                startup_status="port_in_use",
                url=f"http://{request.host}:{request.port}",
                status=DashboardStatus(
                    state="failed",
                    host=request.host,
                    port=request.port,
                    startup_status="port_in_use",
                    url=f"http://{request.host}:{request.port}",
                ),
                errors=[
                    DashboardError(
                        code="report_dashboard_port_in_use",
                        message=f"Dashboard could not start because {request.host}:{request.port} is already in use.",
                        source=f"{request.host}:{request.port}",
                        details="Stop the existing listener or retry with --port <free-port>.",
                    )
                ],
            )

        def stop(self, request: DashboardStartRequest) -> DashboardStatus:
            return DashboardStatus(
                state="stopped",
                host=request.host,
                port=request.port,
                startup_status="stopped",
                url=f"http://{request.host}:{request.port}",
                shutdown_status="not_running",
            )

    monkeypatch.setattr(cli, "StartReportDashboardUseCase", _FakeUseCase)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["report", "dashboard", str(project)],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "PORT IN USE" in result.output
    assert "Dashboard could not start because 127.0.0.1:8080 is already in use." in result.output


def test_report_dashboard_cli_startup_timeout_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "DashboardCliTimeout"
    project.mkdir(parents=True, exist_ok=True)

    class _FakeUseCase:
        def execute(self, request: DashboardStartRequest) -> DashboardStartResult:
            return DashboardStartResult(
                project_path=request.project_path,
                startup_status="startup_timeout",
                url=f"http://{request.host}:{request.port}",
                status=DashboardStatus(
                    state="failed",
                    host=request.host,
                    port=request.port,
                    startup_status="startup_timeout",
                    url=f"http://{request.host}:{request.port}",
                ),
                errors=[
                    DashboardError(
                        code="report_dashboard_startup_timeout",
                        message="Dashboard server did not become ready before timeout (0.10s).",
                        source=f"{request.host}:{request.port}",
                        details="Retry with a larger --startup-timeout if this machine starts the dashboard slowly.",
                    )
                ],
            )

        def stop(self, request: DashboardStartRequest) -> DashboardStatus:
            return DashboardStatus(
                state="stopped",
                host=request.host,
                port=request.port,
                startup_status="stopped",
                url=f"http://{request.host}:{request.port}",
                shutdown_status="not_running",
            )

    monkeypatch.setattr(cli, "StartReportDashboardUseCase", _FakeUseCase)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["report", "dashboard", str(project), "--startup-timeout", "0.1", "--no-open"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "STARTUP TIMEOUT" in result.output


def test_report_dashboard_cli_invalid_path_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    missing = tmp_path / "MissingDashboardProject"
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["report", "dashboard", str(missing), "--no-open"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "PATH NOT FOUND" in result.output


def test_report_dashboard_cli_shutdown_timeout_returns_non_zero(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "DashboardCliStopTimeout"
    project.mkdir(parents=True, exist_ok=True)

    class _FakeUseCase:
        def execute(self, request: DashboardStartRequest) -> DashboardStartResult:
            return DashboardStartResult(
                project_path=request.project_path,
                startup_status="started",
                url=f"http://{request.host}:{request.port}",
                status=DashboardStatus(
                    state="running",
                    host=request.host,
                    port=request.port,
                    startup_status="started",
                    url=f"http://{request.host}:{request.port}",
                    browser_opened=False,
                ),
            )

        def stop(self, request: DashboardStartRequest) -> DashboardStatus:
            return DashboardStatus(
                state="failed",
                host=request.host,
                port=request.port,
                startup_status="stopped",
                url=f"http://{request.host}:{request.port}",
                shutdown_status="timeout",
            )

    monkeypatch.setattr(cli, "StartReportDashboardUseCase", _FakeUseCase)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli.time, "sleep", lambda _seconds: (_ for _ in ()).throw(KeyboardInterrupt()))

    result = runner.invoke(
        cli.app,
        ["report", "dashboard", str(project), "--port", "8898", "--no-open"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Stopping dashboard..." in result.output
    assert "Local dashboard stop timed out; server may still be listening at" in result.output
    assert "http://127.0.0.1:8898." in result.output
