# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Report Dashboard
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Report dashboard capability request/response contracts."""

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
class DashboardStartRequest:
    """Request contract for starting the report dashboard runtime."""

    project_path: Path
    host: str = "127.0.0.1"
    port: int = 8080
    auto_open_browser: bool = True
    startup_timeout_seconds: float = 3.0

    @classmethod
    def from_cli(
        cls,
        path: str = ".",
        host: str = "127.0.0.1",
        port: int = 8080,
        auto_open_browser: bool = True,
        startup_timeout_seconds: float = 3.0,
    ) -> "DashboardStartRequest":
        return cls(
            project_path=_normalize_cli_path(path),
            host=host.strip() or "127.0.0.1",
            port=int(port),
            auto_open_browser=auto_open_browser,
            startup_timeout_seconds=float(startup_timeout_seconds),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "project_path": str(self.project_path),
            "host": self.host,
            "port": self.port,
            "auto_open_browser": self.auto_open_browser,
            "startup_timeout_seconds": self.startup_timeout_seconds,
        }


@dataclass(frozen=True)
class DashboardWarning:
    """Non-fatal dashboard runtime warning."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class DashboardError:
    """Fatal dashboard runtime error."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class DashboardDataSnapshot:
    """Canonical data snapshot consumed by the dashboard runtime."""

    project_name: str
    project_path: Path
    generated_at_iso: str
    stats: dict[str, int] = field(default_factory=dict)
    config_snapshot: dict[str, Any] | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "project_path": str(self.project_path),
            "generated_at_iso": self.generated_at_iso,
            "stats": {key: self.stats[key] for key in sorted(self.stats)},
            "config_snapshot": self.config_snapshot,
        }


@dataclass(frozen=True)
class DashboardStatus:
    """Runtime state for the local dashboard server."""

    state: str  # starting | running | stopping | stopped | failed
    host: str
    port: int
    startup_status: str
    url: str | None = None
    shutdown_status: str | None = None
    thread_name: str | None = None
    browser_opened: bool = False
    started_at_iso: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "host": self.host,
            "port": self.port,
            "startup_status": self.startup_status,
            "url": self.url,
            "shutdown_status": self.shutdown_status,
            "thread_name": self.thread_name,
            "browser_opened": self.browser_opened,
            "started_at_iso": self.started_at_iso,
        }


@dataclass(frozen=True)
class DashboardStartResult:
    """Structured startup result for report dashboard capability."""

    project_path: Path
    startup_status: str  # started | port_in_use | dependency_missing | startup_timeout | startup_failed | validation_failed
    url: str | None = None
    status: DashboardStatus | None = None
    snapshot: DashboardDataSnapshot | None = None
    warnings: list[DashboardWarning] = field(default_factory=list)
    errors: list[DashboardError] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.startup_status == "started" and not self.errors

    def to_payload(self) -> dict[str, Any]:
        sorted_warnings = _sort_signal_items(self.warnings)
        sorted_errors = _sort_signal_items(self.errors)
        return {
            "project_path": str(self.project_path),
            "startup_status": self.startup_status,
            "url": self.url,
            "status": self.status.to_payload() if self.status else None,
            "snapshot": self.snapshot.to_payload() if self.snapshot else None,
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
