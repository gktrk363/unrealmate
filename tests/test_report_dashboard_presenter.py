# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Dashboard Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Presenter tests for report dashboard rendering."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
import re

from rich.console import Console

from unrealmate.adapters.presenters.cli_report_dashboard_presenter import (
    render_report_dashboard_start_result,
    render_report_dashboard_stop_status,
)
from unrealmate.contracts.report_dashboard import (
    DashboardError,
    DashboardStartResult,
    DashboardStatus,
    DashboardWarning,
)


class _FakeVisuals:
    def __init__(self) -> None:
        self.errors: list[tuple[str, str, str]] = []

    def print_error_banner(self, title: str, message: str, *args) -> None:  # type: ignore[no-untyped-def]
        suggestion = (args[0] or "") if args else ""
        self.errors.append((title, message, suggestion))


def _build_console_buffer() -> tuple[Console, StringIO]:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, color_system=None, width=120)
    return console, stream


def test_dashboard_presenter_success_signal_is_stable(tmp_path: Path) -> None:
    result = DashboardStartResult(
        project_path=tmp_path.resolve(),
        startup_status="started",
        url="http://127.0.0.1:8080",
        status=DashboardStatus(
            state="running",
            host="127.0.0.1",
            port=8080,
            startup_status="started",
            url="http://127.0.0.1:8080",
            browser_opened=False,
        ),
    )
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()

    should_wait = render_report_dashboard_start_result(
        result=result,
        console=console,
        visuals_module=visuals,
    )
    output = stream.getvalue()
    normalized_output = re.sub(r"\s+", " ", output)

    assert should_wait is True
    assert "Experimental local dashboard is running." in output
    assert "Open at http://127.0.0.1:8080" in output
    assert "Secondary surface only: use report json" in normalized_output
    assert "stable local report artifacts." in normalized_output
    assert "Press Ctrl+C to stop the local dashboard server" in output
    assert "Headless mode active (--no-open);" in normalized_output
    assert "no browser was opened." in normalized_output


def test_dashboard_presenter_port_conflict_signal_is_stable(tmp_path: Path) -> None:
    result = DashboardStartResult(
        project_path=tmp_path.resolve(),
        startup_status="port_in_use",
        status=DashboardStatus(
            state="failed",
            host="127.0.0.1",
            port=8080,
            startup_status="port_in_use",
            url="http://127.0.0.1:8080",
        ),
        errors=[
            DashboardError(
                code="report_dashboard_port_in_use",
                message="Dashboard port is already in use: 127.0.0.1:8080",
                source="127.0.0.1:8080",
            )
        ],
    )
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()

    should_wait = render_report_dashboard_start_result(
        result=result,
        console=console,
        visuals_module=visuals,
    )

    assert should_wait is False
    assert visuals.errors == [("PORT IN USE", "Dashboard port is already in use: 127.0.0.1:8080", "")]
    assert "Experimental local dashboard is running." not in stream.getvalue()


def test_dashboard_presenter_stop_signal_is_stable() -> None:
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()
    status = DashboardStatus(
        state="stopped",
        host="127.0.0.1",
        port=8080,
        startup_status="stopped",
        url="http://127.0.0.1:8080",
        shutdown_status="clean",
    )

    render_report_dashboard_stop_status(status=status, console=console)
    output = stream.getvalue()

    assert visuals.errors == []
    assert "Local dashboard stopped." in output


def test_dashboard_presenter_browser_open_failure_is_explicit(tmp_path: Path) -> None:
    result = DashboardStartResult(
        project_path=tmp_path.resolve(),
        startup_status="started",
        url="http://127.0.0.1:8080",
        status=DashboardStatus(
            state="running",
            host="127.0.0.1",
            port=8080,
            startup_status="started",
            url="http://127.0.0.1:8080",
            browser_opened=False,
        ),
        warnings=[
            DashboardWarning(
                code="report_dashboard_browser_open_failed",
                message="Dashboard started, but browser could not be opened automatically.",
                source="http://127.0.0.1:8080",
            )
        ],
    )
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()

    should_wait = render_report_dashboard_start_result(
        result=result,
        console=console,
        visuals_module=visuals,
    )
    output = stream.getvalue()
    normalized_output = re.sub(r"\s+", " ", output)

    assert should_wait is True
    assert "Browser auto-open failed; the local dashboard is still ready at the URL above. Open it manually or rerun with --no-open in headless environments." in normalized_output
    assert "Warnings:" in output


def test_dashboard_presenter_stop_timeout_includes_runtime_location() -> None:
    console, stream = _build_console_buffer()
    status = DashboardStatus(
        state="failed",
        host="127.0.0.1",
        port=8080,
        startup_status="stopped",
        url="http://127.0.0.1:8080",
        shutdown_status="timeout",
    )

    render_report_dashboard_stop_status(status=status, console=console)

    assert "Local dashboard stop timed out; server may still be listening at http://127.0.0.1:8080." in stream.getvalue()


def test_dashboard_presenter_startup_timeout_passes_actionable_suggestion(tmp_path: Path) -> None:
    result = DashboardStartResult(
        project_path=tmp_path.resolve(),
        startup_status="startup_timeout",
        status=DashboardStatus(
            state="failed",
            host="127.0.0.1",
            port=8080,
            startup_status="startup_timeout",
            url="http://127.0.0.1:8080",
        ),
        errors=[
            DashboardError(
                code="report_dashboard_startup_timeout",
                message="Dashboard server did not become ready before timeout (0.10s).",
                source="127.0.0.1:8080",
                details="Retry with a larger --startup-timeout if this machine starts the dashboard slowly.",
            )
        ],
    )
    visuals = _FakeVisuals()
    console, _stream = _build_console_buffer()

    should_wait = render_report_dashboard_start_result(
        result=result,
        console=console,
        visuals_module=visuals,
    )

    assert should_wait is False
    assert visuals.errors == [
        (
            "STARTUP TIMEOUT",
            "Dashboard server did not become ready before timeout (0.10s).",
            "Retry with a larger --startup-timeout if this machine starts the dashboard slowly.",
        )
    ]
