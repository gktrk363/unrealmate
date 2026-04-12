# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Report Core
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Shared report-domain collector, code mapping, and normalization helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from unrealmate.contracts.report_json import ReportProjectStats
from unrealmate.core.config import load_config


_DETAIL_KEY_ORDER: tuple[str, ...] = (
    "operation",
    "pattern",
    "counter_key",
    "error_type",
    "error",
)

_WARNING_CODE_MAP: dict[str, dict[str, str]] = {
    "project_missing": {
        "json": "report_json_project_missing",
        "html": "report_html_project_missing",
    },
    "config_unavailable": {
        "json": "report_json_config_unavailable",
        "html": "report_html_config_unavailable",
    },
    "partial_stats": {
        "json": "report_json_partial_stats",
        "html": "report_html_partial_stats",
    },
}

_ERROR_CODE_MAP: dict[str, dict[str, str]] = {
    "write_failed": {
        "json": "report_json_write_failed",
        "html": "report_html_write_failed",
    },
    "template_failed": {
        "html": "report_html_template_failed",
    },
}


def warning_code_for(capability: str, reason: str) -> str:
    codes = _WARNING_CODE_MAP.get(reason)
    if codes is not None and capability in codes:
        return codes[capability]
    return _fallback_code(capability=capability, reason=reason)


def error_code_for(capability: str, reason: str) -> str:
    codes = _ERROR_CODE_MAP.get(reason)
    if codes is not None and capability in codes:
        return codes[capability]
    return _fallback_code(capability=capability, reason=reason)


def format_report_details(**fields: object) -> str:
    keys = [key for key in _DETAIL_KEY_ORDER if key in fields]
    keys.extend(sorted(key for key in fields if key not in _DETAIL_KEY_ORDER))
    return "; ".join(f"{key}={fields[key]}" for key in keys)


def sort_signals(items):
    return sorted(
        items,
        key=lambda item: (
            item.code,
            item.source or "",
            item.message,
            item.details or "",
        ),
    )


def sort_artifacts(items):
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
class ReportCoreSignal:
    """Shared warning signal emitted by report core collector."""

    reason: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class ReportCoreSnapshot:
    """Canonical report snapshot shared by report formats."""

    project_name: str
    project_path: Path
    generated_at_iso: str
    stats: ReportProjectStats
    config_snapshot: dict[str, Any] | None
    warnings: list[ReportCoreSignal]


class ReportCoreCollector:
    """Collect canonical report stats/config/project metadata for report adapters."""

    def __init__(
        self,
        config_loader: Callable[[Path | None], object] | None = None,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._config_loader = config_loader or load_config
        self._now_provider = now_provider or datetime.now

    def collect(
        self,
        project_path: Path,
        include_config: bool = True,
        generated_at_iso_override: str | None = None,
    ) -> ReportCoreSnapshot:
        warnings: list[ReportCoreSignal] = []
        generated_at_iso = generated_at_iso_override or self._now_provider().isoformat()

        count_map: dict[str, int] = {}
        pattern_map: tuple[tuple[str, str], ...] = (
            ("uproject_files", "*.uproject"),
            ("cpp_files", "*.cpp"),
            ("header_files", "*.h"),
            ("blueprint_assets", "*.uasset"),
            ("scene_maps", "*.umap"),
        )
        for counter_key, pattern in pattern_map:
            count, count_warnings = self.collect_pattern_count(
                project_path=project_path,
                pattern=pattern,
                counter_key=counter_key,
            )
            count_map[counter_key] = count
            warnings.extend(count_warnings)

        project_name, project_warnings = self._resolve_project_name(
            project_path=project_path,
            uproject_count=count_map.get("uproject_files", 0),
        )
        warnings.extend(project_warnings)

        config_snapshot = None
        if include_config:
            try:
                config_snapshot = asdict(self._config_loader(project_path))
            except Exception as exc:
                warnings.append(
                    ReportCoreSignal(
                        reason="config_unavailable",
                        message="Configuration snapshot could not be loaded; report will continue without config.",
                        source=str(project_path.resolve()),
                        details=format_report_details(
                            operation="config_snapshot",
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                )

        return ReportCoreSnapshot(
            project_name=project_name,
            project_path=project_path,
            generated_at_iso=generated_at_iso,
            stats=ReportProjectStats(
                uproject_files=count_map.get("uproject_files", 0),
                cpp_source_files=count_map.get("cpp_files", 0) + count_map.get("header_files", 0),
                blueprint_assets=count_map.get("blueprint_assets", 0),
                scene_maps=count_map.get("scene_maps", 0),
            ),
            config_snapshot=config_snapshot,
            warnings=sorted(
                warnings,
                key=lambda warning: (
                    warning.reason,
                    warning.source or "",
                    warning.message,
                    warning.details or "",
                ),
            ),
        )

    def collect_pattern_count(
        self,
        project_path: Path,
        pattern: str,
        counter_key: str,
    ) -> tuple[int, list[ReportCoreSignal]]:
        try:
            return self._count_pattern(project_path, pattern), []
        except Exception as exc:
            return (
                0,
                [
                    ReportCoreSignal(
                        reason="partial_stats",
                        message=f"Could not complete file count for pattern {pattern}; defaulting to 0.",
                        source=str(project_path.resolve()),
                        details=format_report_details(
                            operation="count_pattern",
                            pattern=pattern,
                            counter_key=counter_key,
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                ],
            )

    def _resolve_project_name(
        self,
        project_path: Path,
        uproject_count: int,
    ) -> tuple[str, list[ReportCoreSignal]]:
        if uproject_count <= 0:
            return (
                project_path.name,
                [
                    ReportCoreSignal(
                        reason="project_missing",
                        message="No .uproject file found; using folder name as project identifier.",
                        source=str(project_path.resolve()),
                    )
                ],
            )

        try:
            first_project = next(
                iter(
                    sorted(
                        (path for path in project_path.rglob("*.uproject") if path.is_file()),
                        key=lambda path: str(path).lower(),
                    )
                )
            )
            return first_project.stem, []
        except Exception as exc:
            return (
                project_path.name,
                [
                    ReportCoreSignal(
                        reason="partial_stats",
                        message="Could not resolve project name from .uproject files; folder name was used.",
                        source=str(project_path.resolve()),
                        details=format_report_details(
                            operation="project_name_resolution",
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                ],
            )

    def _count_pattern(self, project_path: Path, pattern: str) -> int:
        return sum(1 for path in project_path.rglob(pattern) if path.is_file())


def _fallback_code(capability: str, reason: str) -> str:
    normalized_reason = reason.replace("-", "_").strip("_") or "unknown"
    return f"report_{capability}_{normalized_reason}"
