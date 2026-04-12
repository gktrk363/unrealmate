# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Asset Scan
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Asset scan capability request/response contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from unrealmate.contracts.asset_domain_common import (
    normalize_cli_path,
    normalize_skip_patterns,
    sort_signal_items,
)
from unrealmate.contracts.asset_domain_policy import (
    DEFAULT_ASSET_SCAN_POLICY,
)


@dataclass(frozen=True)
class AssetScanCategoryRule:
    """Category rule describing glob patterns and optional uasset classifier."""

    name: str
    patterns: tuple[str, ...]
    uasset_classifier: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "patterns": list(self.patterns),
            "uasset_classifier": self.uasset_classifier,
        }


DEFAULT_ASSET_SCAN_CATEGORY_RULES: tuple[AssetScanCategoryRule, ...] = tuple(
    AssetScanCategoryRule(
        name=entry.name,
        patterns=entry.patterns,
        uasset_classifier=entry.uasset_classifier,
    )
    for entry in DEFAULT_ASSET_SCAN_POLICY.category_rules
)

DEFAULT_ASSET_SCAN_SKIP_PATTERNS: tuple[str, ...] = DEFAULT_ASSET_SCAN_POLICY.skip_patterns


@dataclass(frozen=True)
class AssetScanPolicy:
    """Policy knobs for asset scan behavior and output shaping."""

    category_rules: tuple[AssetScanCategoryRule, ...] = field(
        default_factory=lambda: DEFAULT_ASSET_SCAN_CATEGORY_RULES
    )
    skip_patterns: tuple[str, ...] = field(
        default_factory=lambda: DEFAULT_ASSET_SCAN_SKIP_PATTERNS
    )
    detailed_assets_limit: int = DEFAULT_ASSET_SCAN_POLICY.detailed_assets_limit
    largest_assets_limit: int = DEFAULT_ASSET_SCAN_POLICY.largest_assets_limit
    details_format: str = DEFAULT_ASSET_SCAN_POLICY.details_format

    def __post_init__(self) -> None:
        object.__setattr__(self, "skip_patterns", normalize_skip_patterns(self.skip_patterns))
        object.__setattr__(self, "detailed_assets_limit", max(1, int(self.detailed_assets_limit)))
        object.__setattr__(self, "largest_assets_limit", max(1, int(self.largest_assets_limit)))

    def to_payload(self) -> dict[str, Any]:
        return {
            "category_rules": [rule.to_payload() for rule in self.category_rules],
            "skip_patterns": list(self.skip_patterns),
            "detailed_assets_limit": self.detailed_assets_limit,
            "largest_assets_limit": self.largest_assets_limit,
            "details_format": self.details_format,
        }


@dataclass(frozen=True)
class AssetScanRequest:
    """Normalized request contract for asset scanning."""

    scan_path: Path
    policy: AssetScanPolicy = field(default_factory=AssetScanPolicy)

    @classmethod
    def from_cli(
        cls,
        path: str,
        category_rules: tuple[AssetScanCategoryRule, ...] | None = None,
        skip_patterns: tuple[str, ...] | None = None,
        detailed_assets_limit: int = 50,
        largest_assets_limit: int = 5,
    ) -> "AssetScanRequest":
        normalized = normalize_cli_path(path)
        policy = AssetScanPolicy(
            category_rules=category_rules or DEFAULT_ASSET_SCAN_CATEGORY_RULES,
            skip_patterns=skip_patterns or DEFAULT_ASSET_SCAN_SKIP_PATTERNS,
            detailed_assets_limit=detailed_assets_limit,
            largest_assets_limit=largest_assets_limit,
        )

        return cls(
            scan_path=normalized,
            policy=policy,
        )

    @property
    def category_rules(self) -> tuple[AssetScanCategoryRule, ...]:
        return self.policy.category_rules

    @property
    def skip_patterns(self) -> tuple[str, ...]:
        return self.policy.skip_patterns

    @property
    def detailed_assets_limit(self) -> int:
        return self.policy.detailed_assets_limit

    @property
    def largest_assets_limit(self) -> int:
        return self.policy.largest_assets_limit

    def to_payload(self) -> dict[str, Any]:
        return {
            "scan_path": str(self.scan_path),
            "category_rules": [rule.to_payload() for rule in self.category_rules],
            "skip_patterns": list(self.skip_patterns),
            "detailed_assets_limit": self.detailed_assets_limit,
            "largest_assets_limit": self.largest_assets_limit,
        }


@dataclass(frozen=True)
class AssetScanEntry:
    """Single scanned asset entry."""

    path: Path
    category: str
    size_bytes: int

    @property
    def name(self) -> str:
        return self.path.name


@dataclass(frozen=True)
class AssetCategoryStat:
    """Aggregated category totals."""

    name: str
    count: int
    size_bytes: int


@dataclass(frozen=True)
class AssetScanWarning:
    """Non-fatal warning emitted by asset scan flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class AssetScanError:
    """Fatal error emitted by asset scan flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class AssetScanResult:
    """Structured asset scan output independent from terminal rendering."""

    scan_path: Path
    categories: list[AssetCategoryStat] = field(default_factory=list)
    assets: list[AssetScanEntry] = field(default_factory=list)
    largest_assets: list[AssetScanEntry] = field(default_factory=list)
    total_assets: int = 0
    total_size_bytes: int = 0
    warnings: list[AssetScanWarning] = field(default_factory=list)
    errors: list[AssetScanError] = field(default_factory=list)
    detailed_assets_limit: int = 50
    largest_assets_limit: int = 5

    @property
    def has_data(self) -> bool:
        return self.total_assets > 0

    @property
    def is_success(self) -> bool:
        return not self.errors

    def to_payload(self) -> dict[str, Any]:
        sorted_categories = sorted(
            self.categories,
            key=lambda category: (
                category.name.lower(),
                category.count,
                category.size_bytes,
            ),
        )
        sorted_assets = sorted(
            self.assets,
            key=lambda entry: (-entry.size_bytes, entry.path.as_posix().lower(), entry.category),
        )
        sorted_largest_assets = sorted(
            self.largest_assets,
            key=lambda entry: (-entry.size_bytes, entry.path.as_posix().lower(), entry.category),
        )
        sorted_warnings = sort_signal_items(self.warnings)
        sorted_errors = sort_signal_items(self.errors)

        return {
            "scan_path": str(self.scan_path),
            "categories": [
                {
                    "name": category.name,
                    "count": category.count,
                    "size_bytes": category.size_bytes,
                }
                for category in sorted_categories
            ],
            "assets": [
                {
                    "path": str(entry.path),
                    "category": entry.category,
                    "size_bytes": entry.size_bytes,
                }
                for entry in sorted_assets
            ],
            "largest_assets": [
                {
                    "path": str(entry.path),
                    "category": entry.category,
                    "size_bytes": entry.size_bytes,
                }
                for entry in sorted_largest_assets
            ],
            "total_assets": self.total_assets,
            "total_size_bytes": self.total_size_bytes,
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
            "detailed_assets_limit": self.detailed_assets_limit,
            "largest_assets_limit": self.largest_assets_limit,
        }
