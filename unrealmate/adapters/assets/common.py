# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Common
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Shared low-risk helpers for asset-domain filesystem adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence, TypeVar

from unrealmate.contracts.asset_domain_common import format_signal_details, sort_signal_items


TSignal = TypeVar("TSignal")


def sort_paths(paths: Sequence[Path]) -> list[Path]:
    """Deterministically sort paths in a case-insensitive portable way."""
    return sorted(paths, key=lambda path: path.as_posix().lower())


def should_skip_path(path: Path, skip_patterns: tuple[str, ...]) -> bool:
    """Return whether path should be skipped based on normalized tokens."""
    normalized = path.as_posix().lower()
    return any(pattern in normalized for pattern in skip_patterns)


def ensure_directory_readable(scan_path: Path) -> None:
    """Raise PermissionError when scan directory cannot be iterated."""
    try:
        iterator = scan_path.resolve().iterdir()
        next(iterator, None)
    except Exception as exc:
        raise PermissionError(str(exc)) from exc


def normalize_scan_source(source: str | None, fallback_scan_path: Path) -> str:
    """Normalize warning/error source path safely for structured payloads."""
    if source:
        try:
            return str(Path(source).resolve())
        except Exception:
            return str(source)
    return str(fallback_scan_path.resolve())


def format_details(**fields: object) -> str:
    """Build deterministic key-value detail strings for warnings/errors."""
    return format_signal_details(**fields)


def sort_signals(items: Sequence[TSignal]) -> list[TSignal]:
    """Sort warnings/errors deterministically by shared signal fields."""
    return sort_signal_items(items)
