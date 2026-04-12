# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Generate Json Report
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Use-case for structured report json generation."""

from __future__ import annotations

from datetime import datetime

from unrealmate.adapters.report.report_json_adapter import ReportJsonAdapter
from unrealmate.contracts.report_json import (
    ReportJsonError,
    ReportJsonRequest,
    ReportJsonResult,
    ReportProjectStats,
)


class GenerateJsonReportUseCase:
    """Application use-case that orchestrates JSON report generation."""

    def __init__(self, adapter: ReportJsonAdapter | None = None) -> None:
        self._adapter = adapter or ReportJsonAdapter()

    def execute(self, request: ReportJsonRequest) -> ReportJsonResult:
        if not request.project_path.exists():
            return ReportJsonResult(
                project_name=request.project_path.name,
                project_path=request.project_path,
                generated_at_iso=_generated_at_iso(request),
                stats=ReportProjectStats(),
                config_snapshot=None,
                artifacts=[],
                warnings=[],
                errors=[
                    ReportJsonError(
                        code="report_json_path_not_found",
                        message=f"Project path does not exist: {request.project_path}",
                        source=str(request.project_path.resolve()),
                    )
                ],
            )

        if not request.project_path.is_dir():
            return ReportJsonResult(
                project_name=request.project_path.name,
                project_path=request.project_path,
                generated_at_iso=_generated_at_iso(request),
                stats=ReportProjectStats(),
                config_snapshot=None,
                artifacts=[],
                warnings=[],
                errors=[
                    ReportJsonError(
                        code="report_json_not_directory",
                        message=f"Project path is not a directory: {request.project_path}",
                        source=str(request.project_path.resolve()),
                    )
                ],
            )

        return self._adapter.collect(request)


def _generated_at_iso(request: ReportJsonRequest) -> str:
    return request.generated_at_iso_override or datetime.now().isoformat()
