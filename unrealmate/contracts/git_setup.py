# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Git Setup
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Git init/lfs capability request/response contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _normalize_cli_path(path: str) -> Path:
    raw_path = Path(path).expanduser()
    if raw_path.is_absolute():
        return raw_path.resolve()
    return (Path.cwd() / raw_path).resolve()


def _resolve_path_strategy(path: str) -> str:
    normalized = str(path).strip()
    return "cwd_fallback" if normalized in {"", "."} else "explicit"


@dataclass(frozen=True)
class GitProcessPolicy:
    """Execution policy for external git process calls."""

    timeout_seconds: float = 10.0
    max_retries: int = 0
    retry_backoff_seconds: float = 0.25

    def __post_init__(self) -> None:
        object.__setattr__(self, "timeout_seconds", max(0.1, float(self.timeout_seconds)))
        object.__setattr__(self, "max_retries", max(0, int(self.max_retries)))
        object.__setattr__(
            self,
            "retry_backoff_seconds",
            max(0.0, float(self.retry_backoff_seconds)),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "retry_backoff_seconds": self.retry_backoff_seconds,
        }


@dataclass(frozen=True)
class GitExternalCommandResult:
    """Normalized external command execution result."""

    command: tuple[str, ...]
    cwd: Path
    status: str  # success | failed | missing | timeout
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    attempts: int = 1
    timeout_seconds: float | None = None
    timed_out: bool = False

    def to_payload(self) -> dict[str, Any]:
        return {
            "command": list(self.command),
            "cwd": str(self.cwd),
            "status": self.status,
            "return_code": self.return_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "attempts": self.attempts,
            "timeout_seconds": self.timeout_seconds,
            "timed_out": self.timed_out,
        }


@dataclass(frozen=True)
class GitSetupWarning:
    """Non-fatal warning emitted by git setup flows."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class GitSetupError:
    """Fatal error emitted by git setup flows."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class GitInitRequest:
    """Request contract for gitignore initialization."""

    project_path: Path
    force: bool = False
    preview_only: bool = False
    path_strategy: str = "cwd_fallback"  # explicit | cwd_fallback
    target_filename: str = ".gitignore"
    template_filename: str = "gitignore.template"

    @classmethod
    def from_cli(
        cls,
        path: str = ".",
        force: bool = False,
        preview_only: bool = False,
    ) -> "GitInitRequest":
        normalized = _normalize_cli_path(path)
        return cls(
            project_path=normalized,
            force=force,
            preview_only=preview_only,
            path_strategy=_resolve_path_strategy(path),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "project_path": str(self.project_path),
            "force": self.force,
            "preview_only": self.preview_only,
            "path_strategy": self.path_strategy,
            "target_filename": self.target_filename,
            "template_filename": self.template_filename,
        }


@dataclass(frozen=True)
class GitInitResult:
    """Structured result for gitignore initialization."""

    project_path: Path
    target_path: Path
    template_path: Path | None = None
    file_status: str = "failed"  # created | updated | skipped | would_create | would_update | failed
    preview_only: bool = False
    bytes_written: int = 0
    warnings: list[GitSetupWarning] = field(default_factory=list)
    errors: list[GitSetupError] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return not self.errors

    def to_payload(self) -> dict[str, Any]:
        sorted_warnings = sorted(
            self.warnings,
            key=lambda warning: (warning.code, warning.source or "", warning.message, warning.details or ""),
        )
        sorted_errors = sorted(
            self.errors,
            key=lambda error: (error.code, error.source or "", error.message, error.details or ""),
        )
        return {
            "project_path": str(self.project_path),
            "target_path": str(self.target_path),
            "template_path": str(self.template_path) if self.template_path is not None else None,
            "file_status": self.file_status,
            "preview_only": self.preview_only,
            "bytes_written": self.bytes_written,
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


@dataclass(frozen=True)
class GitLfsRequest:
    """Request contract for git lfs initialization."""

    project_path: Path
    force: bool = False
    preview_only: bool = False
    path_strategy: str = "cwd_fallback"  # explicit | cwd_fallback
    process_policy: GitProcessPolicy = field(default_factory=GitProcessPolicy)
    target_filename: str = ".gitattributes"
    template_filename: str = "gitattributes.template"

    @classmethod
    def from_cli(
        cls,
        path: str = ".",
        force: bool = False,
        preview_only: bool = False,
        process_policy: GitProcessPolicy | None = None,
    ) -> "GitLfsRequest":
        normalized = _normalize_cli_path(path)
        return cls(
            project_path=normalized,
            force=force,
            preview_only=preview_only,
            path_strategy=_resolve_path_strategy(path),
            process_policy=process_policy or GitProcessPolicy(),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "project_path": str(self.project_path),
            "force": self.force,
            "preview_only": self.preview_only,
            "path_strategy": self.path_strategy,
            "process_policy": self.process_policy.to_payload(),
            "target_filename": self.target_filename,
            "template_filename": self.template_filename,
        }


@dataclass(frozen=True)
class GitLfsResult:
    """Structured result for git lfs initialization."""

    project_path: Path
    target_path: Path
    template_path: Path | None = None
    file_status: str = "failed"  # created | updated | skipped | would_create | would_update | dependency_missing | failed
    preview_only: bool = False
    dependency_status: str = "unknown"  # available | missing | failed | unknown
    bytes_written: int = 0
    pattern_count: int = 0
    version_command: GitExternalCommandResult | None = None
    install_command: GitExternalCommandResult | None = None
    warnings: list[GitSetupWarning] = field(default_factory=list)
    errors: list[GitSetupError] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return not self.errors

    def to_payload(self) -> dict[str, Any]:
        sorted_warnings = sorted(
            self.warnings,
            key=lambda warning: (warning.code, warning.source or "", warning.message, warning.details or ""),
        )
        sorted_errors = sorted(
            self.errors,
            key=lambda error: (error.code, error.source or "", error.message, error.details or ""),
        )
        return {
            "project_path": str(self.project_path),
            "target_path": str(self.target_path),
            "template_path": str(self.template_path) if self.template_path is not None else None,
            "file_status": self.file_status,
            "preview_only": self.preview_only,
            "dependency_status": self.dependency_status,
            "bytes_written": self.bytes_written,
            "pattern_count": self.pattern_count,
            "version_command": (
                self.version_command.to_payload() if self.version_command is not None else None
            ),
            "install_command": (
                self.install_command.to_payload() if self.install_command is not None else None
            ),
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
