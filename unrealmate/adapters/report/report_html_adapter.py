# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Report Html Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter wrapper for report html generation and file output."""

from __future__ import annotations

from pathlib import Path

from unrealmate.adapters.report.report_core import (
    ReportCoreCollector,
    error_code_for,
    format_report_details,
    sort_artifacts,
    sort_signals,
    warning_code_for,
)
from unrealmate.adapters.report.report_html_template import render_report_html_document
from unrealmate.contracts.report_html import (
    ReportHtmlError,
    ReportHtmlRequest,
    ReportHtmlResult,
    ReportHtmlWarning,
)
from unrealmate.contracts.report_json import ReportGeneratedArtifact


class ReportHtmlAdapter:
    """Filesystem-backed adapter for report html capability."""

    def __init__(self, collector: ReportCoreCollector | None = None) -> None:
        self._collector = collector or ReportCoreCollector()

    def collect(self, request: ReportHtmlRequest) -> ReportHtmlResult:
        core_snapshot = self._collector.collect(
            project_path=request.project_path,
            include_config=request.include_config,
            generated_at_iso_override=request.generated_at_iso_override,
        )

        warnings = [
            ReportHtmlWarning(
                code=warning_code_for("html", signal.reason),
                message=signal.message,
                source=signal.source,
                details=signal.details,
            )
            for signal in core_snapshot.warnings
        ]
        errors: list[ReportHtmlError] = []
        artifacts: list[ReportGeneratedArtifact] = []

        python_script_count, python_warnings = self._collector.collect_pattern_count(
            project_path=request.project_path,
            pattern="*.py",
            counter_key="python_script_count",
        )
        mapped_warnings = [
            ReportHtmlWarning(
                code=warning_code_for("html", signal.reason),
                message=signal.message,
                source=signal.source,
                details=signal.details,
            )
            for signal in python_warnings
        ]
        warnings.extend(mapped_warnings)

        output_path = request.output_path or (request.project_path / "unrealmate_report.html")
        try:
            html_content = render_report_html_document(
                project_name=core_snapshot.project_name,
                project_path=request.project_path,
                generated_at_iso=core_snapshot.generated_at_iso,
                stats_payload=core_snapshot.stats.to_payload(),
                python_script_count=python_script_count,
                config_snapshot=core_snapshot.config_snapshot,
            )
        except Exception as exc:
            errors.append(
                ReportHtmlError(
                    code=error_code_for("html", "template_failed"),
                    message=f"Failed to render HTML report: {exc}",
                    source=str(request.project_path.resolve()),
                    details=format_report_details(
                        operation="render_html",
                        error_type=type(exc).__name__,
                        error=str(exc),
                    ),
                )
            )
            return ReportHtmlResult(
                project_name=core_snapshot.project_name,
                project_path=core_snapshot.project_path,
                generated_at_iso=core_snapshot.generated_at_iso,
                stats=core_snapshot.stats,
                config_snapshot=core_snapshot.config_snapshot,
                python_script_count=python_script_count,
                artifacts=[],
                warnings=sort_signals(warnings),
                errors=sort_signals(errors),
            )

        artifact, write_error = self._write_html_output(
            output_path=output_path,
            html_content=html_content,
        )
        artifacts.append(artifact)
        if write_error is not None:
            errors.append(write_error)

        return ReportHtmlResult(
            project_name=core_snapshot.project_name,
            project_path=core_snapshot.project_path,
            generated_at_iso=core_snapshot.generated_at_iso,
            stats=core_snapshot.stats,
            config_snapshot=core_snapshot.config_snapshot,
            python_script_count=python_script_count,
            artifacts=sort_artifacts(artifacts),
            warnings=sort_signals(warnings),
            errors=sort_signals(errors),
        )

    def _write_html_output(
        self,
        output_path: Path,
        html_content: str,
    ) -> tuple[ReportGeneratedArtifact, ReportHtmlError | None]:
        resolved_output = output_path.resolve()
        preexisting = resolved_output.exists()
        encoded_size = len(html_content.encode("utf-8"))

        try:
            resolved_output.parent.mkdir(parents=True, exist_ok=True)
            resolved_output.write_text(html_content, encoding="utf-8")
            return (
                ReportGeneratedArtifact(
                    kind="html",
                    path=resolved_output,
                    status="updated" if preexisting else "created",
                    bytes_written=encoded_size,
                    content_type="text/html",
                ),
                None,
            )
        except Exception as exc:
            return (
                ReportGeneratedArtifact(
                    kind="html",
                    path=resolved_output,
                    status="failed",
                    bytes_written=0,
                    content_type="text/html",
                ),
                ReportHtmlError(
                    code=error_code_for("html", "write_failed"),
                    message=f"Failed to write HTML report: {exc}",
                    source=str(resolved_output),
                    details=format_report_details(
                        operation="write_output",
                        error_type=type(exc).__name__,
                        error=str(exc),
                    ),
                ),
            )
