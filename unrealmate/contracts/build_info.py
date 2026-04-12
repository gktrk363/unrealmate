# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Build İnfo
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Build info capability request/response contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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


@dataclass(frozen=True)
class BuildInfoRequest:
    """Request contract for build metadata inspection."""

    project_path: Path

    @classmethod
    def from_cli(cls, path: str = ".") -> "BuildInfoRequest":
        return cls(project_path=_normalize_cli_path(path))

    def to_payload(self) -> dict[str, Any]:
        return {
            "project_path": str(self.project_path),
        }


@dataclass(frozen=True)
class BuildMetadata:
    """Normalized project metadata extracted from .uproject."""

    project_name: str
    project_file: Path
    engine_version: str
    category: str
    description: str
    plugin_count: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "project_file": str(self.project_file),
            "engine_version": self.engine_version,
            "category": self.category,
            "description": self.description,
            "plugin_count": self.plugin_count,
        }


@dataclass(frozen=True)
class BuildEnvironmentInfo:
    """Build environment hints derived from project layout."""

    has_git_repository: bool = False
    has_plugins_directory: bool = False
    ci_providers: tuple[str, ...] = field(default_factory=tuple)
    detected_ci_files: tuple[str, ...] = field(default_factory=tuple)

    def to_payload(self) -> dict[str, Any]:
        return {
            "has_git_repository": self.has_git_repository,
            "has_plugins_directory": self.has_plugins_directory,
            "ci_providers": list(self.ci_providers),
            "detected_ci_files": list(self.detected_ci_files),
        }


@dataclass(frozen=True)
class BuildInfoWarning:
    """Non-fatal warning emitted by build info flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class BuildInfoError:
    """Fatal error emitted by build info flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class BuildInfoResult:
    """Structured build info output independent from terminal rendering."""

    project_path: Path
    metadata: BuildMetadata | None = None
    environment: BuildEnvironmentInfo = field(default_factory=BuildEnvironmentInfo)
    warnings: list[BuildInfoWarning] = field(default_factory=list)
    errors: list[BuildInfoError] = field(default_factory=list)

    @property
    def has_data(self) -> bool:
        return self.metadata is not None

    @property
    def is_success(self) -> bool:
        return not self.errors

    def to_payload(self) -> dict[str, Any]:
        sorted_warnings = _sort_signal_items(self.warnings)
        sorted_errors = _sort_signal_items(self.errors)
        return {
            "project_path": str(self.project_path),
            "metadata": self.metadata.to_payload() if self.metadata is not None else None,
            "environment": self.environment.to_payload(),
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

