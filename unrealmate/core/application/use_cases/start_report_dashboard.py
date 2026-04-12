# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Start Report Dashboard
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Use-case for structured report dashboard startup/shutdown."""

from __future__ import annotations

from unrealmate.adapters.report.report_dashboard_adapter import ReportDashboardAdapter
from unrealmate.contracts.report_dashboard import (
    DashboardError,
    DashboardStartRequest,
    DashboardStartResult,
    DashboardStatus,
)


class StartReportDashboardUseCase:
    """Application use-case that orchestrates dashboard lifecycle actions."""

    def __init__(self, adapter: ReportDashboardAdapter | None = None) -> None:
        self._adapter = adapter or ReportDashboardAdapter()

    def execute(self, request: DashboardStartRequest) -> DashboardStartResult:
        if not request.project_path.exists():
            return self._validation_error_result(
                request=request,
                code="report_dashboard_path_not_found",
                message=f"Project path does not exist: {request.project_path}",
            )

        if not request.project_path.is_dir():
            return self._validation_error_result(
                request=request,
                code="report_dashboard_not_directory",
                message=f"Project path is not a directory: {request.project_path}",
            )

        return self._adapter.start(request)

    def stop(self, request: DashboardStartRequest) -> DashboardStatus:
        return self._adapter.stop(host=request.host, port=request.port)

    def _validation_error_result(
        self,
        request: DashboardStartRequest,
        code: str,
        message: str,
    ) -> DashboardStartResult:
        return DashboardStartResult(
            project_path=request.project_path,
            startup_status="validation_failed",
            url=f"http://{request.host}:{request.port}",
            status=DashboardStatus(
                state="failed",
                host=request.host,
                port=request.port,
                startup_status="validation_failed",
                url=f"http://{request.host}:{request.port}",
            ),
            warnings=[],
            errors=[
                DashboardError(
                    code=code,
                    message=message,
                    source=str(request.project_path.resolve()),
                )
            ],
        )
