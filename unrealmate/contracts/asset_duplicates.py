# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Asset Duplicates
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Asset duplicates capability request/response contracts."""

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
    DEFAULT_ASSET_DUPLICATES_POLICY,
    DEFAULT_ASSET_DUPLICATE_EXTENSIONS,
    SUPPORTED_ASSET_GROUPING_MODES,
    SUPPORTED_ASSET_HASH_STRATEGIES,
)


DEFAULT_ASSET_DUPLICATE_SKIP_PATTERNS: tuple[str, ...] = DEFAULT_ASSET_DUPLICATES_POLICY.skip_patterns
SUPPORTED_DUPLICATE_HASH_STRATEGIES: tuple[str, ...] = SUPPORTED_ASSET_HASH_STRATEGIES


@dataclass(frozen=True)
class AssetDuplicatesPolicy:
    """Duplicate detection policy knobs used by adapters/use-cases."""

    grouping_mode: str = DEFAULT_ASSET_DUPLICATES_POLICY.grouping_mode
    asset_extensions: tuple[str, ...] = field(
        default_factory=lambda: DEFAULT_ASSET_DUPLICATE_EXTENSIONS
    )
    skip_patterns: tuple[str, ...] = field(
        default_factory=lambda: DEFAULT_ASSET_DUPLICATE_SKIP_PATTERNS
    )
    hash_strategy: str = DEFAULT_ASSET_DUPLICATES_POLICY.hash_strategy
    details_format: str = DEFAULT_ASSET_DUPLICATES_POLICY.details_format

    def __post_init__(self) -> None:
        normalized_grouping_mode = str(self.grouping_mode).strip().lower()
        if normalized_grouping_mode not in SUPPORTED_ASSET_GROUPING_MODES:
            raise ValueError(
                "grouping_mode must be one of: " + ", ".join(SUPPORTED_ASSET_GROUPING_MODES)
            )

        normalized_extensions = normalize_extensions(self.asset_extensions)
        normalized_skip_patterns = normalize_skip_patterns(self.skip_patterns)
        normalized_hash_strategy = str(self.hash_strategy).strip().lower()
        if normalized_hash_strategy not in SUPPORTED_DUPLICATE_HASH_STRATEGIES:
            raise ValueError(
                "hash_strategy must be one of: "
                + ", ".join(SUPPORTED_DUPLICATE_HASH_STRATEGIES)
            )

        object.__setattr__(self, "grouping_mode", normalized_grouping_mode)
        object.__setattr__(self, "asset_extensions", normalized_extensions)
        object.__setattr__(self, "skip_patterns", normalized_skip_patterns)
        object.__setattr__(self, "hash_strategy", normalized_hash_strategy)

    def to_payload(self) -> dict[str, Any]:
        return {
            "grouping_mode": self.grouping_mode,
            "asset_extensions": list(self.asset_extensions),
            "skip_patterns": list(self.skip_patterns),
            "hash_strategy": self.hash_strategy,
            "details_format": self.details_format,
        }


@dataclass(frozen=True)
class AssetDuplicatesRequest:
    """Normalized request contract for duplicate detection."""

    scan_path: Path
    by_content: bool = False
    policy: AssetDuplicatesPolicy = field(default_factory=AssetDuplicatesPolicy)

    @classmethod
    def from_cli(
        cls,
        path: str = ".",
        by_content: bool = False,
        grouping_mode: str | None = None,
        asset_extensions: tuple[str, ...] | None = None,
        skip_patterns: tuple[str, ...] | None = None,
        hash_strategy: str = DEFAULT_ASSET_DUPLICATES_POLICY.hash_strategy,
    ) -> "AssetDuplicatesRequest":
        normalized = normalize_cli_path(path)
        resolved_grouping_mode = grouping_mode or (
            "content" if by_content else DEFAULT_ASSET_DUPLICATES_POLICY.grouping_mode
        )
        resolved_by_content = resolved_grouping_mode == "content"
        policy = AssetDuplicatesPolicy(
            grouping_mode=resolved_grouping_mode,
            asset_extensions=asset_extensions or DEFAULT_ASSET_DUPLICATE_EXTENSIONS,
            skip_patterns=skip_patterns or DEFAULT_ASSET_DUPLICATE_SKIP_PATTERNS,
            hash_strategy=hash_strategy,
        )
        return cls(
            scan_path=normalized,
            by_content=resolved_by_content,
            policy=policy,
        )

    @property
    def grouping_mode(self) -> str:
        return self.policy.grouping_mode

    @property
    def hash_strategy(self) -> str:
        return self.policy.hash_strategy

    @property
    def asset_extensions(self) -> tuple[str, ...]:
        return self.policy.asset_extensions

    @property
    def skip_patterns(self) -> tuple[str, ...]:
        return self.policy.skip_patterns

    def to_payload(self) -> dict[str, Any]:
        return {
            "scan_path": str(self.scan_path),
            "by_content": self.by_content,
            "grouping_mode": self.grouping_mode,
            "policy": self.policy.to_payload(),
        }


@dataclass(frozen=True)
class DuplicateEntry:
    """Single duplicate file entry."""

    path: Path
    size_bytes: int

    @property
    def name(self) -> str:
        return self.path.name


@dataclass(frozen=True)
class DuplicateGroup:
    """Duplicate group with deterministic ordering fields."""

    group_key: str
    representative_name: str
    entries: list[DuplicateEntry] = field(default_factory=list)
    copies: int = 0
    duplicate_files: int = 0
    retained_size_bytes: int = 0
    total_group_size_bytes: int = 0
    wasted_size_bytes: int = 0


@dataclass(frozen=True)
class AssetDuplicatesWarning:
    """Non-fatal warning emitted by duplicate scan flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class AssetDuplicatesError:
    """Fatal error emitted by duplicate scan flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class AssetDuplicatesResult:
    """Structured duplicate scan output independent from terminal rendering."""

    scan_path: Path
    by_content: bool
    grouping_mode: str = "filename"
    hash_strategy: str = "md5"
    groups: list[DuplicateGroup] = field(default_factory=list)
    total_groups: int = 0
    total_duplicate_files: int = 0
    total_wasted_size_bytes: int = 0
    scanned_candidate_files: int = 0
    warnings: list[AssetDuplicatesWarning] = field(default_factory=list)
    errors: list[AssetDuplicatesError] = field(default_factory=list)

    @property
    def has_data(self) -> bool:
        return self.total_groups > 0

    @property
    def is_success(self) -> bool:
        return not self.errors

    def to_payload(self) -> dict[str, Any]:
        sorted_groups = sorted(
            self.groups,
            key=lambda group: (
                -group.wasted_size_bytes,
                group.representative_name.lower(),
                group.group_key.lower(),
            ),
        )
        sorted_warnings = sort_signal_items(self.warnings)
        sorted_errors = sort_signal_items(self.errors)

        return {
            "scan_path": str(self.scan_path),
            "by_content": self.by_content,
            "grouping_mode": self.grouping_mode,
            "hash_strategy": self.hash_strategy,
            "groups": [
                {
                    "group_key": group.group_key,
                    "representative_name": group.representative_name,
                    "entries": [
                        {
                            "path": str(entry.path),
                            "size_bytes": entry.size_bytes,
                        }
                        for entry in sorted(
                            group.entries,
                            key=lambda item: item.path.as_posix().lower(),
                        )
                    ],
                    "copies": group.copies,
                    "duplicate_files": group.duplicate_files,
                    "retained_size_bytes": group.retained_size_bytes,
                    "total_group_size_bytes": group.total_group_size_bytes,
                    "wasted_size_bytes": group.wasted_size_bytes,
                }
                for group in sorted_groups
            ],
            "total_groups": self.total_groups,
            "total_duplicate_files": self.total_duplicate_files,
            "total_wasted_size_bytes": self.total_wasted_size_bytes,
            "scanned_candidate_files": self.scanned_candidate_files,
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
