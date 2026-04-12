# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Asset Duplicates Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter wrapper that maps duplicate scanning to structured contracts."""

from __future__ import annotations

import hashlib
import os
from collections import defaultdict
from pathlib import Path

from unrealmate.adapters.assets.common import (
    ensure_directory_readable,
    format_details,
    normalize_scan_source,
    should_skip_path,
    sort_paths,
    sort_signals,
)
from unrealmate.contracts.asset_duplicates import (
    AssetDuplicatesError,
    AssetDuplicatesRequest,
    AssetDuplicatesResult,
    AssetDuplicatesWarning,
    DuplicateEntry,
    DuplicateGroup,
)
from unrealmate.contracts.asset_domain_policy import ASSET_DUPLICATES_CODES


class AssetDuplicatesAdapter:
    """Filesystem duplicate scanner with deterministic structured output."""

    def find_duplicates(self, request: AssetDuplicatesRequest) -> AssetDuplicatesResult:
        warnings: list[AssetDuplicatesWarning] = []
        grouped_entries: dict[str, list[DuplicateEntry]] = defaultdict(list)
        scanned_candidate_files = 0

        try:
            scan_files, scan_warnings = self._list_scan_files(
                request.scan_path,
                request.skip_patterns,
            )
            warnings.extend(scan_warnings)
        except Exception as exc:
            return AssetDuplicatesResult(
                scan_path=request.scan_path,
                by_content=request.by_content,
                grouping_mode=request.grouping_mode,
                hash_strategy=request.hash_strategy,
                errors=[
                    AssetDuplicatesError(
                        code=ASSET_DUPLICATES_CODES["path_unreadable"],
                        message="Scan path could not be read with current permissions.",
                        source=str(request.scan_path.resolve()),
                        details=format_details(
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                ],
            )

        try:
            for asset_file in scan_files:
                if asset_file.suffix.lower() not in request.asset_extensions:
                    continue

                scanned_candidate_files += 1
                size_bytes, size_warning = self._safe_file_size(asset_file)
                if size_warning is not None:
                    warnings.append(size_warning)

                if request.by_content:
                    group_key, hash_warning = self._hash_file(asset_file, request.hash_strategy)
                    if hash_warning is not None:
                        warnings.append(hash_warning)
                        continue
                    if group_key is None:
                        continue
                else:
                    group_key = asset_file.name.lower()

                grouped_entries[group_key].append(
                    DuplicateEntry(path=asset_file.resolve(), size_bytes=size_bytes)
                )
        except Exception as exc:
            return AssetDuplicatesResult(
                scan_path=request.scan_path,
                by_content=request.by_content,
                grouping_mode=request.grouping_mode,
                hash_strategy=request.hash_strategy,
                scanned_candidate_files=scanned_candidate_files,
                warnings=sort_signals(warnings),
                errors=[
                    AssetDuplicatesError(
                        code=ASSET_DUPLICATES_CODES["scan_failed"],
                        message="Duplicate scan failed while processing assets.",
                        source=str(request.scan_path.resolve()),
                        details=format_details(
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                ],
            )

        groups = self._build_groups(grouped_entries)
        total_duplicate_files = sum(group.duplicate_files for group in groups)
        total_wasted_size_bytes = sum(group.wasted_size_bytes for group in groups)

        if not groups:
            warnings.append(
                AssetDuplicatesWarning(
                    code=ASSET_DUPLICATES_CODES["no_data"],
                    message="No duplicate assets found.",
                    source=str(request.scan_path.resolve()),
                        details=format_details(
                            scanned_candidates=scanned_candidate_files,
                            grouping_mode=request.grouping_mode,
                            hash_strategy=request.hash_strategy if request.by_content else "none",
                    ),
                )
            )

        return AssetDuplicatesResult(
            scan_path=request.scan_path,
            by_content=request.by_content,
            grouping_mode=request.grouping_mode,
            hash_strategy=request.hash_strategy,
            groups=groups,
            total_groups=len(groups),
            total_duplicate_files=total_duplicate_files,
            total_wasted_size_bytes=total_wasted_size_bytes,
            scanned_candidate_files=scanned_candidate_files,
            warnings=sort_signals(warnings),
            errors=[],
        )

    def _build_groups(self, grouped_entries: dict[str, list[DuplicateEntry]]) -> list[DuplicateGroup]:
        groups: list[DuplicateGroup] = []
        for group_key, entries in grouped_entries.items():
            if len(entries) < 2:
                continue

            sorted_entries = sorted(
                entries,
                key=lambda entry: entry.path.as_posix().lower(),
            )
            retained_entry = sorted(
                sorted_entries,
                key=lambda entry: (-entry.size_bytes, entry.path.as_posix().lower()),
            )[0]
            representative = sorted_entries[0]
            copies = len(sorted_entries)
            duplicate_files = copies - 1
            total_group_size_bytes = sum(entry.size_bytes for entry in sorted_entries)
            wasted_size_bytes = max(0, total_group_size_bytes - retained_entry.size_bytes)

            groups.append(
                DuplicateGroup(
                    group_key=group_key,
                    representative_name=representative.path.name,
                    entries=sorted_entries,
                    copies=copies,
                    duplicate_files=duplicate_files,
                    retained_size_bytes=retained_entry.size_bytes,
                    total_group_size_bytes=total_group_size_bytes,
                    wasted_size_bytes=wasted_size_bytes,
                )
            )

        return sorted(
            groups,
            key=lambda group: (
                -group.wasted_size_bytes,
                group.representative_name.lower(),
                group.group_key.lower(),
            ),
        )

    def _list_scan_files(
        self,
        scan_path: Path,
        skip_patterns: tuple[str, ...],
    ) -> tuple[list[Path], list[AssetDuplicatesWarning]]:
        ensure_directory_readable(scan_path)
        files: list[Path] = []
        warnings: list[AssetDuplicatesWarning] = []

        def _on_walk_error(exc: OSError) -> None:
            source = normalize_scan_source(exc.filename, scan_path)
            warnings.append(
                AssetDuplicatesWarning(
                    code=ASSET_DUPLICATES_CODES["scan_partial_failed"],
                    message="Some subdirectories could not be scanned.",
                    source=source,
                    details=format_details(
                        stage="walk",
                        error_type=type(exc).__name__,
                        error=str(exc),
                    ),
                )
            )

        for root, dirs, file_names in os.walk(scan_path.resolve(), onerror=_on_walk_error):
            root_path = Path(root).resolve()
            dirs[:] = [
                name
                for name in dirs
                if not should_skip_path(root_path / name, skip_patterns)
            ]

            for file_name in file_names:
                candidate = (root_path / file_name).resolve()
                if should_skip_path(candidate, skip_patterns):
                    continue
                files.append(candidate)

        sorted_files = sort_paths(files)
        sorted_warnings = sort_signals(warnings)
        return sorted_files, sorted_warnings

    def _safe_file_size(self, asset_file: Path) -> tuple[int, AssetDuplicatesWarning | None]:
        try:
            return asset_file.stat().st_size, None
        except Exception as exc:
            return 0, AssetDuplicatesWarning(
                code=ASSET_DUPLICATES_CODES["stat_failed"],
                message="Asset metadata could not be read.",
                source=str(asset_file.resolve()),
                details=format_details(
                    operation="stat",
                    error_type=type(exc).__name__,
                    error=str(exc),
                ),
            )

    def _hash_file(
        self,
        asset_file: Path,
        hash_strategy: str,
    ) -> tuple[str | None, AssetDuplicatesWarning | None]:
        try:
            hasher = hashlib.new(hash_strategy)
            with open(asset_file, "rb") as file_stream:
                for chunk in iter(lambda: file_stream.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest(), None
        except Exception as exc:
            return None, AssetDuplicatesWarning(
                code=ASSET_DUPLICATES_CODES["stat_failed"],
                message="Asset content could not be read for duplicate comparison.",
                source=str(asset_file.resolve()),
                details=format_details(
                    operation="hash",
                    hash_strategy=hash_strategy,
                    error_type=type(exc).__name__,
                    error=str(exc),
                ),
            )
