# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Report Html
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Report HTML capability request/response contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from unrealmate.contracts.report_json import ReportGeneratedArtifact, ReportProjectStats


def _normalize_cli_path(path: str) -> Path:
    raw_path = Path(path).expanduser()
    if raw_path.is_absolute():
        return raw_path.resolve()
    return (Path.cwd() / raw_path).resolve()


def _sort_signal_items(items):
    return sorted(
        items,
        key=lambda item: (
            item.code,
            item.source or "",
            item.message,
            item.details or "",
        ),
    )


def _sort_artifacts(items):
    return sorted(
        items,
        key=lambda item: (
            item.kind,
            str(item.path),
            item.status,
            item.content_type,
        ),
    )


@dataclass(frozen=True)
class ReportHtmlRequest:
    """Request contract for HTML project report generation."""

    project_path: Path
    output_path: Path | None = None
    include_config: bool = True
    generated_at_iso_override: str | None = None

    @classmethod
    def from_cli(
        cls,
        path: str = ".",
        output: str | None = None,
        include_config: bool = True,
        generated_at_iso_override: str | None = None,
    ) -> "ReportHtmlRequest":
        return cls(
            project_path=_normalize_cli_path(path),
            output_path=_normalize_cli_path(output) if output else None,
            include_config=include_config,
            generated_at_iso_override=generated_at_iso_override,
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "project_path": str(self.project_path),
            "output_path": str(self.output_path) if self.output_path else None,
            "include_config": self.include_config,
            "generated_at_iso_override": self.generated_at_iso_override,
        }


@dataclass(frozen=True)
class ReportHtmlWarning:
    """Non-fatal warning emitted by report HTML flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class ReportHtmlError:
    """Fatal error emitted by report HTML flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class ReportHtmlResult:
    """Structured report HTML result independent from terminal rendering."""

    project_name: str
    project_path: Path
    generated_at_iso: str
    stats: ReportProjectStats = field(default_factory=ReportProjectStats)
    config_snapshot: dict[str, Any] | None = None
    python_script_count: int = 0
    artifacts: list[ReportGeneratedArtifact] = field(default_factory=list)
    warnings: list[ReportHtmlWarning] = field(default_factory=list)
    errors: list[ReportHtmlError] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return not self.errors

    def to_payload(self) -> dict[str, Any]:
        sorted_warnings = _sort_signal_items(self.warnings)
        sorted_errors = _sort_signal_items(self.errors)
        sorted_artifacts = _sort_artifacts(self.artifacts)
        return {
            "project_name": self.project_name,
            "project_path": str(self.project_path),
            "generated_at_iso": self.generated_at_iso,
            "stats": self.stats.to_payload(),
            "config_snapshot": self.config_snapshot,
            "python_script_count": self.python_script_count,
            "artifacts": [artifact.to_payload() for artifact in sorted_artifacts],
            "warnings": [
                {
                    "code": warning.code,
                    "message": warning.message,
                    "source": warning.source,
                    "details": warning.details,
                }
                for warning in sorted_warnings
            ],
            "errors": [
                {
                    "code": error.code,
                    "message": error.message,
                    "source": error.source,
                    "details": error.details,
                }
                for error in sorted_errors
            ],
        }
