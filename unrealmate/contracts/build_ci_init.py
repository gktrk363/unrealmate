# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Build Ci İnit
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Build ci-init capability request/response contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SUPPORTED_BUILD_CI_PROVIDERS: tuple[str, ...] = ("github", "gitlab", "jenkins")


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
class BuildCiInitRequest:
    """Request contract for CI pipeline initialization."""

    project_path: Path
    platform: str = "github"
    preview_only: bool = False
    selected_project_file: Path | None = None
    selected_project_name: str | None = None
    selection_strategy: str = "alphabetical_first"

    @classmethod
    def from_cli(
        cls,
        path: str = ".",
        platform: str = "github",
        preview_only: bool = False,
    ) -> "BuildCiInitRequest":
        normalized_platform = str(platform).strip().lower() or "github"
        return cls(
            project_path=_normalize_cli_path(path),
            platform=normalized_platform,
            preview_only=preview_only,
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "project_path": str(self.project_path),
            "platform": self.platform,
            "preview_only": self.preview_only,
            "selected_project_file": (
                str(self.selected_project_file.resolve())
                if self.selected_project_file is not None
                else None
            ),
            "selected_project_name": self.selected_project_name,
            "selection_strategy": self.selection_strategy,
        }


@dataclass(frozen=True)
class GeneratedFileEntry:
    """Single generated/updated/skipped CI file entry."""

    path: Path
    status: str  # created | updated | skipped | failed | would_create | would_update
    bytes_written: int = 0
    provider: str = "github"
    details: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "status": self.status,
            "bytes_written": self.bytes_written,
            "provider": self.provider,
            "details": self.details,
        }


@dataclass(frozen=True)
class BuildArtifactEntry:
    """Produced artifact pointer for clients."""

    name: str
    path: Path
    provider: str = "github"

    def to_payload(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": str(self.path),
            "provider": self.provider,
        }


@dataclass(frozen=True)
class BuildCiInitWarning:
    """Non-fatal warning emitted by build ci-init flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class BuildCiInitError:
    """Fatal error emitted by build ci-init flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class BuildCiInitResult:
    """Structured build ci-init output independent from terminal rendering."""

    project_path: Path
    platform: str
    selected_project_file: Path | None = None
    selected_project_name: str | None = None
    selection_strategy: str = "alphabetical_first"
    generated_files: list[GeneratedFileEntry] = field(default_factory=list)
    artifacts: list[BuildArtifactEntry] = field(default_factory=list)
    preview_only: bool = False
    warnings: list[BuildCiInitWarning] = field(default_factory=list)
    errors: list[BuildCiInitError] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return not self.errors

    def to_payload(self) -> dict[str, Any]:
        sorted_files = sorted(
            self.generated_files,
            key=lambda entry: (
                entry.path.as_posix().lower(),
                entry.status,
                entry.provider,
            ),
        )
        sorted_artifacts = sorted(
            self.artifacts,
            key=lambda entry: (
                entry.name.lower(),
                entry.path.as_posix().lower(),
                entry.provider,
            ),
        )
        sorted_warnings = _sort_signal_items(self.warnings)
        sorted_errors = _sort_signal_items(self.errors)
        return {
            "project_path": str(self.project_path),
            "platform": self.platform,
            "selected_project_file": (
                str(self.selected_project_file.resolve())
                if self.selected_project_file is not None
                else None
            ),
            "selected_project_name": self.selected_project_name,
            "selection_strategy": self.selection_strategy,
            "preview_only": self.preview_only,
            "generated_files": [entry.to_payload() for entry in sorted_files],
            "artifacts": [entry.to_payload() for entry in sorted_artifacts],
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
