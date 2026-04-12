# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Asset Scan Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter wrapper that maps asset scanning logic to structured contracts."""

from __future__ import annotations

from pathlib import Path

from unrealmate.adapters.assets.common import (
    format_details,
    should_skip_path,
    sort_paths,
    sort_signals,
)
from unrealmate.contracts.asset_scan import (
    AssetCategoryStat,
    AssetScanCategoryRule,
    AssetScanEntry,
    AssetScanError,
    AssetScanRequest,
    AssetScanResult,
    AssetScanWarning,
)
from unrealmate.contracts.asset_domain_policy import ASSET_SCAN_CODES


class AssetScanAdapter:
    """Filesystem-based asset scanner with deterministic structured output."""

    def scan(self, request: AssetScanRequest) -> AssetScanResult:
        categories: list[AssetCategoryStat] = []
        all_entries: list[AssetScanEntry] = []
        warnings: list[AssetScanWarning] = []
        category_order = {rule.name: index for index, rule in enumerate(request.category_rules)}
        total_pattern_count = sum(len(rule.patterns) for rule in request.category_rules)
        pattern_failure_count = 0

        for rule in request.category_rules:
            category_entries: list[AssetScanEntry] = []
            seen_paths: set[Path] = set()

            for pattern in rule.patterns:
                try:
                    matched_files = self._glob_pattern(request.scan_path, pattern)
                except Exception as exc:
                    pattern_failure_count += 1
                    warnings.append(
                        AssetScanWarning(
                            code=ASSET_SCAN_CODES["pattern_failed"],
                            message="Asset scan failed for one category pattern.",
                            source=str(request.scan_path.resolve()),
                            details=format_details(
                                category=rule.name,
                                pattern=pattern,
                                error_type=type(exc).__name__,
                                error=str(exc),
                            ),
                        )
                    )
                    continue

                for asset_file in matched_files:
                    if asset_file in seen_paths:
                        continue
                    if should_skip_path(asset_file, request.skip_patterns):
                        continue
                    if not self._matches_uasset_classifier(asset_file, rule):
                        continue

                    size_bytes, size_warning = self._safe_file_size(asset_file)
                    if size_warning is not None:
                        warnings.append(size_warning)

                    entry = AssetScanEntry(
                        path=asset_file.resolve(),
                        category=rule.name,
                        size_bytes=size_bytes,
                    )
                    seen_paths.add(asset_file)
                    category_entries.append(entry)
                    all_entries.append(entry)

            if category_entries:
                category_total_size = sum(entry.size_bytes for entry in category_entries)
                categories.append(
                    AssetCategoryStat(
                        name=rule.name,
                        count=len(category_entries),
                        size_bytes=category_total_size,
                    )
                )

        sorted_entries = sorted(
            all_entries,
            key=lambda entry: (-entry.size_bytes, entry.path.as_posix().lower(), entry.category),
        )
        largest_assets = sorted_entries[: request.largest_assets_limit]
        sorted_categories = sorted(
            categories,
            key=lambda category: (category_order.get(category.name, 999), category.name.lower()),
        )
        total_assets = len(sorted_entries)
        total_size_bytes = sum(entry.size_bytes for entry in sorted_entries)

        errors: list[AssetScanError] = []
        if total_assets == 0:
            if pattern_failure_count == total_pattern_count and total_pattern_count > 0:
                errors.append(
                    AssetScanError(
                        code=ASSET_SCAN_CODES["path_unreadable"],
                        message="Scan path could not be read with current permissions.",
                        source=str(request.scan_path),
                        details=format_details(
                            pattern_failures=pattern_failure_count,
                            total_patterns=total_pattern_count,
                        ),
                    )
                )
            else:
                warnings.append(
                    AssetScanWarning(
                        code=ASSET_SCAN_CODES["no_data"],
                        message="Target directory appears to contain no trackable assets.",
                        source=str(request.scan_path),
                        details=format_details(matched_assets=0),
                    )
                )

        sorted_warnings = sort_signals(warnings)
        sorted_errors = sort_signals(errors)

        return AssetScanResult(
            scan_path=request.scan_path,
            categories=sorted_categories,
            assets=sorted_entries,
            largest_assets=largest_assets,
            total_assets=total_assets,
            total_size_bytes=total_size_bytes,
            warnings=sorted_warnings,
            errors=sorted_errors,
            detailed_assets_limit=request.detailed_assets_limit,
            largest_assets_limit=request.largest_assets_limit,
        )

    def _glob_pattern(self, scan_path: Path, pattern: str) -> list[Path]:
        return sort_paths([entry.resolve() for entry in scan_path.rglob(pattern) if entry.is_file()])

    def _matches_uasset_classifier(self, asset_file: Path, rule: AssetScanCategoryRule) -> bool:
        if rule.uasset_classifier is None:
            return True

        normalized = asset_file.as_posix().lower()
        if rule.uasset_classifier == "materials":
            return "material" in normalized
        if rule.uasset_classifier == "blueprints":
            return "material" not in normalized
        return True

    def _safe_file_size(self, asset_file: Path) -> tuple[int, AssetScanWarning | None]:
        try:
            return asset_file.stat().st_size, None
        except Exception as exc:
            return 0, self._build_stat_warning(asset_file, exc)

    def _build_stat_warning(self, asset_file: Path, exc: Exception) -> AssetScanWarning:
        return AssetScanWarning(
            code=ASSET_SCAN_CODES["stat_failed"],
            message="Asset metadata could not be read.",
            source=str(asset_file.resolve()),
            details=format_details(
                operation="stat",
                error_type=type(exc).__name__,
                error=str(exc),
            ),
        )
