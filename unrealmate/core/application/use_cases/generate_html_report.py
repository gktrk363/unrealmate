# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Generate Html Report
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Use-case for structured report html generation."""

from __future__ import annotations

from datetime import datetime

from unrealmate.adapters.report.report_html_adapter import ReportHtmlAdapter
from unrealmate.contracts.report_html import (
    ReportHtmlError,
    ReportHtmlRequest,
    ReportHtmlResult,
)
from unrealmate.contracts.report_json import ReportProjectStats


class GenerateHtmlReportUseCase:
    """Application use-case that orchestrates HTML report generation."""

    def __init__(self, adapter: ReportHtmlAdapter | None = None) -> None:
        self._adapter = adapter or ReportHtmlAdapter()

    def execute(self, request: ReportHtmlRequest) -> ReportHtmlResult:
        if not request.project_path.exists():
            return ReportHtmlResult(
                project_name=request.project_path.name,
                project_path=request.project_path,
                generated_at_iso=_generated_at_iso(request),
                stats=ReportProjectStats(),
                errors=[
                    ReportHtmlError(
                        code="report_html_path_not_found",
                        message=f"Project path does not exist: {request.project_path}",
                        source=str(request.project_path.resolve()),
                    )
                ],
            )

        if not request.project_path.is_dir():
            return ReportHtmlResult(
                project_name=request.project_path.name,
                project_path=request.project_path,
                generated_at_iso=_generated_at_iso(request),
                stats=ReportProjectStats(),
                errors=[
                    ReportHtmlError(
                        code="report_html_not_directory",
                        message=f"Project path is not a directory: {request.project_path}",
                        source=str(request.project_path.resolve()),
                    )
                ],
            )

        return self._adapter.collect(request)


def _generated_at_iso(request: ReportHtmlRequest) -> str:
    return request.generated_at_iso_override or datetime.now().isoformat()
