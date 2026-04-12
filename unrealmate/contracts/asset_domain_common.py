# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Asset Domain Common
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Common normalization/sorting helpers for asset-domain contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence, TypeVar


ASSET_SKIP_PATTERNS_BASE: tuple[str, ...] = (
    "venv",
    ".venv",
    "site-packages",
    "node_modules",
    ".git",
    "Intermediate",
    "Saved",
    "__pycache__",
)

ASSET_SCAN_EXTRA_SKIP_PATTERNS: tuple[str, ...] = (
    "Binaries",
    "DerivedDataCache",
)

ASSET_SCAN_SKIP_PATTERNS: tuple[str, ...] = (
    *ASSET_SKIP_PATTERNS_BASE,
    *ASSET_SCAN_EXTRA_SKIP_PATTERNS,
)

_DETAIL_FIELD_ORDER: tuple[str, ...] = (
    "category",
    "pattern",
    "operation",
    "stage",
    "target",
    "candidate_files",
    "matched_assets",
    "scanned_candidates",
    "grouping_mode",
    "hash_strategy",
    "conflicts",
    "pattern_failures",
    "total_patterns",
    "error_type",
    "error",
)

TSignal = TypeVar("TSignal")


def normalize_cli_path(path: str) -> Path:
    """Return normalized absolute path from CLI input."""
    raw_path = Path(path).expanduser()
    if raw_path.is_absolute():
        return raw_path.resolve()
    return (Path.cwd() / raw_path).resolve()


def normalize_skip_patterns(patterns: Iterable[str]) -> tuple[str, ...]:
    """Normalize skip patterns as lowercase deterministic tuple."""
    return tuple(
        sorted(
            {
                str(pattern).strip().lower()
                for pattern in patterns
                if str(pattern).strip()
            }
        )
    )


def normalize_extensions(extensions: Iterable[str]) -> tuple[str, ...]:
    """Normalize extension values into deterministic dotted lowercase tuple."""
    return tuple(
        sorted(
            {
                _normalize_extension(extension)
                for extension in extensions
                if str(extension).strip()
            }
        )
    )


def format_signal_details(**fields: object) -> str:
    """Build deterministic details payload string for warning/error surfaces."""
    ordered_keys = [key for key in _DETAIL_FIELD_ORDER if key in fields]
    ordered_keys.extend(sorted(key for key in fields if key not in _DETAIL_FIELD_ORDER))
    return "; ".join(f"{key}={fields[key]}" for key in ordered_keys)


def sort_signal_items(items: Sequence[TSignal]) -> list[TSignal]:
    """Deterministically sort warning/error-like records by shared attributes."""
    return sorted(
        items,
        key=lambda item: (
            getattr(item, "code", ""),
            getattr(item, "source", "") or "",
            getattr(item, "message", ""),
            getattr(item, "details", "") or "",
        ),
    )


def _normalize_extension(value: str) -> str:
    normalized = str(value).strip().lower()
    if not normalized:
        return normalized
    if normalized.startswith("."):
        return normalized
    return f".{normalized}"
