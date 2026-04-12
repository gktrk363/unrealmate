# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Dashboard Use Case
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Contract and use-case tests for report dashboard extraction slice."""

from __future__ import annotations

from pathlib import Path

from unrealmate.contracts.report_dashboard import (
    DashboardStartRequest,
    DashboardStartResult,
    DashboardStatus,
)
from unrealmate.core.application.use_cases.start_report_dashboard import (
    StartReportDashboardUseCase,
)


class _FakeDashboardAdapter:
    def __init__(self) -> None:
        self.started_request: DashboardStartRequest | None = None
        self.stopped_host_port: tuple[str, int] | None = None

    def start(self, request: DashboardStartRequest) -> DashboardStartResult:
        self.started_request = request
        status = DashboardStatus(
            state="running",
            host=request.host,
            port=request.port,
            startup_status="started",
            url=f"http://{request.host}:{request.port}",
        )
        return DashboardStartResult(
            project_path=request.project_path,
            startup_status="started",
            url=status.url,
            status=status,
            warnings=[],
            errors=[],
        )

    def stop(self, host: str, port: int) -> DashboardStatus:
        self.stopped_host_port = (host, port)
        return DashboardStatus(
            state="stopped",
            host=host,
            port=port,
            startup_status="stopped",
            url=f"http://{host}:{port}",
            shutdown_status="clean",
        )


def test_report_dashboard_request_normalizes_cli_inputs(tmp_path: Path, monkeypatch) -> None:
    cwd = tmp_path / "cwd"
    cwd.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(cwd)

    request = DashboardStartRequest.from_cli(
        path=".",
        host="127.0.0.1",
        port=9999,
        auto_open_browser=False,
        startup_timeout_seconds=4.5,
    )

    assert request.project_path == cwd.resolve()
    assert request.host == "127.0.0.1"
    assert request.port == 9999
    assert request.auto_open_browser is False
    assert request.startup_timeout_seconds == 4.5


def test_report_dashboard_use_case_invalid_path_returns_structured_error(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    use_case = StartReportDashboardUseCase(adapter=_FakeDashboardAdapter())
    request = DashboardStartRequest.from_cli(path=str(missing))

    result = use_case.execute(request)

    assert result.is_success is False
    assert result.startup_status == "validation_failed"
    assert result.errors[0].code == "report_dashboard_path_not_found"
    assert result.errors[0].source == str(missing.resolve())


def test_report_dashboard_use_case_not_directory_returns_structured_error(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")
    use_case = StartReportDashboardUseCase(adapter=_FakeDashboardAdapter())
    request = DashboardStartRequest.from_cli(path=str(file_path))

    result = use_case.execute(request)

    assert result.is_success is False
    assert result.startup_status == "validation_failed"
    assert result.errors[0].code == "report_dashboard_not_directory"
    assert result.errors[0].source == str(file_path.resolve())


def test_report_dashboard_use_case_invokes_adapter_for_valid_request(tmp_path: Path) -> None:
    project = tmp_path / "ValidDashboardProject"
    project.mkdir(parents=True, exist_ok=True)
    fake_adapter = _FakeDashboardAdapter()
    use_case = StartReportDashboardUseCase(adapter=fake_adapter)
    request = DashboardStartRequest.from_cli(
        path=str(project),
        host="127.0.0.1",
        port=8899,
        auto_open_browser=False,
    )

    result = use_case.execute(request)

    assert result.is_success is True
    assert fake_adapter.started_request == request

    stop_status = use_case.stop(request)
    assert stop_status.shutdown_status == "clean"
    assert fake_adapter.stopped_host_port == ("127.0.0.1", 8899)
