# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Asset Organize
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Asset organize capability request/response contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from unrealmate.contracts.asset_domain_common import (
    normalize_cli_path,
    normalize_extensions,
    normalize_skip_patterns,
    sort_signal_items,
)
from unrealmate.contracts.asset_domain_policy import (
    DEFAULT_ASSET_ORGANIZE_POLICY,
    SUPPORTED_ASSET_ORGANIZE_PLACEMENT_MODES,
)


@dataclass(frozen=True)
class AssetOrganizeRule:
    """Organize rule that maps file extensions to a target folder."""

    category: str
    target_folder: str
    extensions: tuple[str, ...]

    def __post_init__(self) -> None:
        normalized_extensions = normalize_extensions(self.extensions)
        object.__setattr__(self, "extensions", normalized_extensions)

    def to_payload(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "target_folder": self.target_folder,
            "extensions": list(self.extensions),
        }


DEFAULT_ASSET_ORGANIZE_RULES: tuple[AssetOrganizeRule, ...] = tuple(
    AssetOrganizeRule(
        category=entry.category,
        target_folder=entry.target_folder,
        extensions=entry.extensions,
    )
    for entry in DEFAULT_ASSET_ORGANIZE_POLICY.rules
)

DEFAULT_ASSET_ORGANIZE_SKIP_PATTERNS: tuple[str, ...] = DEFAULT_ASSET_ORGANIZE_POLICY.skip_patterns


@dataclass(frozen=True)
class AssetOrganizePolicy:
    """Policy knobs for organize plan/execute behavior."""

    placement_mode: str = DEFAULT_ASSET_ORGANIZE_POLICY.placement_mode
    rules: tuple[AssetOrganizeRule, ...] = field(
        default_factory=lambda: DEFAULT_ASSET_ORGANIZE_RULES
    )
    skip_patterns: tuple[str, ...] = field(
        default_factory=lambda: DEFAULT_ASSET_ORGANIZE_SKIP_PATTERNS
    )
    conflict_suffix_separator: str = DEFAULT_ASSET_ORGANIZE_POLICY.conflict_suffix_separator
    details_format: str = DEFAULT_ASSET_ORGANIZE_POLICY.details_format

    def __post_init__(self) -> None:
        normalized_placement_mode = str(self.placement_mode).strip().lower()
        if normalized_placement_mode not in SUPPORTED_ASSET_ORGANIZE_PLACEMENT_MODES:
            raise ValueError(
                "placement_mode must be one of: "
                + ", ".join(SUPPORTED_ASSET_ORGANIZE_PLACEMENT_MODES)
            )
        normalized_skip_patterns = normalize_skip_patterns(self.skip_patterns)
        separator = str(self.conflict_suffix_separator).strip() or "_"
        object.__setattr__(self, "placement_mode", normalized_placement_mode)
        object.__setattr__(self, "skip_patterns", normalized_skip_patterns)
        object.__setattr__(self, "conflict_suffix_separator", separator)

    def to_payload(self) -> dict[str, Any]:
        return {
            "placement_mode": self.placement_mode,
            "rules": [rule.to_payload() for rule in self.rules],
            "skip_patterns": list(self.skip_patterns),
            "conflict_suffix_separator": self.conflict_suffix_separator,
            "details_format": self.details_format,
        }


@dataclass(frozen=True)
class AssetOrganizeRequest:
    """Normalized request contract for asset organize flow."""

    scan_path: Path
    dry_run: bool = False
    assume_yes: bool = False
    policy: AssetOrganizePolicy = field(default_factory=AssetOrganizePolicy)

    @classmethod
    def from_cli(
        cls,
        path: str = ".",
        dry_run: bool = False,
        yes: bool = False,
        policy: AssetOrganizePolicy | None = None,
    ) -> "AssetOrganizeRequest":
        normalized = normalize_cli_path(path)
        return cls(
            scan_path=normalized,
            dry_run=dry_run,
            assume_yes=yes,
            policy=policy or AssetOrganizePolicy(),
        )

    @property
    def organize_rules(self) -> tuple[AssetOrganizeRule, ...]:
        return self.policy.rules

    @property
    def skip_patterns(self) -> tuple[str, ...]:
        return self.policy.skip_patterns

    def to_payload(self) -> dict[str, Any]:
        return {
            "scan_path": str(self.scan_path),
            "dry_run": self.dry_run,
            "assume_yes": self.assume_yes,
            "policy": self.policy.to_payload(),
        }


@dataclass(frozen=True)
class AssetMovePlanEntry:
    """Planned source/target move entry."""

    source_path: Path
    requested_target_path: Path
    final_target_path: Path
    category: str
    conflict_detected: bool = False
    conflict_index: int = 0


@dataclass(frozen=True)
class AssetMoveResultEntry:
    """Executed move result entry."""

    source_path: Path
    requested_target_path: Path
    final_target_path: Path
    category: str
    status: str  # moved | skipped | failed
    details: str | None = None


@dataclass(frozen=True)
class AssetOrganizeWarning:
    """Non-fatal warning emitted by asset organize flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class AssetOrganizeError:
    """Fatal error emitted by asset organize flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class AssetOrganizeResult:
    """Structured organize output independent from terminal rendering."""

    scan_path: Path
    dry_run: bool
    planned_moves: list[AssetMovePlanEntry] = field(default_factory=list)
    executed_moves: list[AssetMoveResultEntry] = field(default_factory=list)
    skipped_moves: list[AssetMoveResultEntry] = field(default_factory=list)
    failed_moves: list[AssetMoveResultEntry] = field(default_factory=list)
    conflicts: list[AssetMovePlanEntry] = field(default_factory=list)
    warnings: list[AssetOrganizeWarning] = field(default_factory=list)
    errors: list[AssetOrganizeError] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.planned_moves)

    @property
    def is_success(self) -> bool:
        return not self.errors

    def to_payload(self) -> dict[str, Any]:
        sorted_planned = _sort_plan_entries(self.planned_moves)
        sorted_executed = _sort_result_entries(self.executed_moves)
        sorted_skipped = _sort_result_entries(self.skipped_moves)
        sorted_failed = _sort_result_entries(self.failed_moves)
        sorted_conflicts = _sort_plan_entries(self.conflicts)
        sorted_warnings = sort_signal_items(self.warnings)
        sorted_errors = sort_signal_items(self.errors)

        return {
            "scan_path": str(self.scan_path),
            "dry_run": self.dry_run,
            "planned_moves": [
                {
                    "source_path": str(item.source_path),
                    "requested_target_path": str(item.requested_target_path),
                    "final_target_path": str(item.final_target_path),
                    "category": item.category,
                    "conflict_detected": item.conflict_detected,
                    "conflict_index": item.conflict_index,
                }
                for item in sorted_planned
            ],
            "executed_moves": [
                {
                    "source_path": str(item.source_path),
                    "requested_target_path": str(item.requested_target_path),
                    "final_target_path": str(item.final_target_path),
                    "category": item.category,
                    "status": item.status,
                    "details": item.details,
                }
                for item in sorted_executed
            ],
            "skipped_moves": [
                {
                    "source_path": str(item.source_path),
                    "requested_target_path": str(item.requested_target_path),
                    "final_target_path": str(item.final_target_path),
                    "category": item.category,
                    "status": item.status,
                    "details": item.details,
                }
                for item in sorted_skipped
            ],
            "failed_moves": [
                {
                    "source_path": str(item.source_path),
                    "requested_target_path": str(item.requested_target_path),
                    "final_target_path": str(item.final_target_path),
                    "category": item.category,
                    "status": item.status,
                    "details": item.details,
                }
                for item in sorted_failed
            ],
            "conflicts": [
                {
                    "source_path": str(item.source_path),
                    "requested_target_path": str(item.requested_target_path),
                    "final_target_path": str(item.final_target_path),
                    "category": item.category,
                    "conflict_detected": item.conflict_detected,
                    "conflict_index": item.conflict_index,
                }
                for item in sorted_conflicts
            ],
            "totals": {
                "planned": len(sorted_planned),
                "executed": len(sorted_executed),
                "skipped": len(sorted_skipped),
                "failed": len(sorted_failed),
                "conflicts": len(sorted_conflicts),
            },
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


def _sort_plan_entries(entries: list[AssetMovePlanEntry]) -> list[AssetMovePlanEntry]:
    return sorted(
        entries,
        key=lambda item: (
            item.category.lower(),
            item.source_path.as_posix().lower(),
            item.final_target_path.as_posix().lower(),
        ),
    )


def _sort_result_entries(entries: list[AssetMoveResultEntry]) -> list[AssetMoveResultEntry]:
    return sorted(
        entries,
        key=lambda item: (
            item.category.lower(),
            item.source_path.as_posix().lower(),
            item.final_target_path.as_posix().lower(),
            item.status,
        ),
    )
