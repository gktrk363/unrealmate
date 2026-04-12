# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Report Json Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter wrapper for report json data collection and file output."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Callable

from unrealmate.adapters.report.report_core import (
    ReportCoreCollector,
    error_code_for,
    format_report_details,
    sort_artifacts,
    sort_signals,
    warning_code_for,
)
from unrealmate.contracts.report_json import (
    ReportGeneratedArtifact,
    ReportJsonError,
    ReportJsonRequest,
    ReportJsonResult,
    ReportJsonWarning,
)


class ReportJsonAdapter:
    """Filesystem/config adapter for report json capability."""

    def __init__(
        self,
        config_loader: Callable[[Path | None], object] | None = None,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._collector = ReportCoreCollector(
            config_loader=config_loader,
            now_provider=now_provider or datetime.now,
        )

    def collect(self, request: ReportJsonRequest) -> ReportJsonResult:
        core_snapshot = self._collector.collect(
            project_path=request.project_path,
            include_config=request.include_config,
            generated_at_iso_override=request.generated_at_iso_override,
        )
        warnings = [
            ReportJsonWarning(
                code=warning_code_for("json", signal.reason),
                message=signal.message,
                source=signal.source,
                details=signal.details,
            )
            for signal in core_snapshot.warnings
        ]
        errors: list[ReportJsonError] = []
        artifacts: list[ReportGeneratedArtifact] = []

        result = ReportJsonResult(
            project_name=core_snapshot.project_name,
            project_path=core_snapshot.project_path,
            generated_at_iso=core_snapshot.generated_at_iso,
            stats=core_snapshot.stats,
            config_snapshot=core_snapshot.config_snapshot,
            artifacts=artifacts,
            warnings=sort_signals(warnings),
            errors=sort_signals(errors),
        )

        if request.output_path is not None:
            artifact, write_error = self._write_output(
                output_path=request.output_path,
                document=result.to_report_document(),
            )
            artifacts.append(artifact)
            if write_error is not None:
                errors.append(write_error)

            result = ReportJsonResult(
                project_name=result.project_name,
                project_path=result.project_path,
                generated_at_iso=result.generated_at_iso,
                stats=result.stats,
                config_snapshot=result.config_snapshot,
                artifacts=sort_artifacts(artifacts),
                warnings=sort_signals(warnings),
                errors=sort_signals(errors),
            )

        return result

    def _write_output(
        self,
        output_path: Path,
        document: dict[str, object],
    ) -> tuple[ReportGeneratedArtifact, ReportJsonError | None]:
        resolved_output = output_path.resolve()
        preexisting = resolved_output.exists()
        serialized = json.dumps(document, indent=2, default=str)
        encoded_size = len(serialized.encode("utf-8"))

        try:
            resolved_output.parent.mkdir(parents=True, exist_ok=True)
            resolved_output.write_text(serialized, encoding="utf-8")
            return (
                ReportGeneratedArtifact(
                    kind="json",
                    path=resolved_output,
                    status="updated" if preexisting else "created",
                    bytes_written=encoded_size,
                    content_type="application/json",
                ),
                None,
            )
        except Exception as exc:
            return (
                ReportGeneratedArtifact(
                    kind="json",
                    path=resolved_output,
                    status="failed",
                    bytes_written=0,
                    content_type="application/json",
                ),
                ReportJsonError(
                    code=error_code_for("json", "write_failed"),
                    message=f"Failed to write JSON report: {exc}",
                    source=str(resolved_output),
                    details=format_report_details(
                        operation="write_output",
                        error_type=type(exc).__name__,
                        error=str(exc),
                    ),
                ),
            )
