# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Asset Organize Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter wrapper that maps asset organize logic to structured contracts."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from unrealmate.adapters.assets.common import (
    ensure_directory_readable,
    format_details,
    normalize_scan_source,
    should_skip_path,
    sort_paths,
    sort_signals,
)
from unrealmate.contracts.asset_organize import (
    AssetMovePlanEntry,
    AssetMoveResultEntry,
    AssetOrganizeError,
    AssetOrganizeRequest,
    AssetOrganizeResult,
    AssetOrganizeRule,
    AssetOrganizeWarning,
)
from unrealmate.contracts.asset_domain_policy import ASSET_ORGANIZE_CODES


class AssetOrganizeAdapter:
    """Filesystem-based planner/executor for asset organizing."""

    def organize(self, request: AssetOrganizeRequest) -> AssetOrganizeResult:
        try:
            candidate_files, scan_warnings = self._list_files(
                request.scan_path,
                request.skip_patterns,
            )
        except Exception as exc:
            return AssetOrganizeResult(
                scan_path=request.scan_path,
                dry_run=request.dry_run,
                errors=[
                    AssetOrganizeError(
                        code=ASSET_ORGANIZE_CODES["path_unreadable"],
                        message="Organize path could not be read with current permissions.",
                        source=str(request.scan_path.resolve()),
                        details=format_details(
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                ],
            )

        plan_entries = self._build_plan(request, candidate_files)
        conflicts = [entry for entry in plan_entries if entry.conflict_detected]
        warnings = list(scan_warnings)

        if conflicts:
            warnings.append(
                AssetOrganizeWarning(
                    code=ASSET_ORGANIZE_CODES["conflict_detected"],
                    message="Destination name conflicts detected; fallback names were planned.",
                    source=str(request.scan_path.resolve()),
                    details=format_details(conflicts=len(conflicts)),
                )
            )

        if not plan_entries:
            warnings.append(
                AssetOrganizeWarning(
                    code=ASSET_ORGANIZE_CODES["no_data"],
                    message="All assets are already organized.",
                    source=str(request.scan_path.resolve()),
                    details=format_details(candidate_files=len(candidate_files)),
                )
            )
            return AssetOrganizeResult(
                scan_path=request.scan_path,
                dry_run=request.dry_run,
                planned_moves=[],
                conflicts=[],
                warnings=sort_signals(warnings),
            )

        if request.dry_run:
            return AssetOrganizeResult(
                scan_path=request.scan_path,
                dry_run=True,
                planned_moves=self._sort_plan_entries(plan_entries),
                conflicts=self._sort_plan_entries(conflicts),
                warnings=sort_signals(warnings),
            )

        executed_moves: list[AssetMoveResultEntry] = []
        skipped_moves: list[AssetMoveResultEntry] = []
        failed_moves: list[AssetMoveResultEntry] = []
        errors: list[AssetOrganizeError] = []

        for plan in self._sort_plan_entries(plan_entries):
            source_path = plan.source_path.resolve()
            requested_target = plan.requested_target_path.resolve()
            final_target = plan.final_target_path.resolve()

            if not source_path.exists():
                skipped_moves.append(
                    AssetMoveResultEntry(
                        source_path=source_path,
                        requested_target_path=requested_target,
                        final_target_path=final_target,
                        category=plan.category,
                        status="skipped",
                        details="source_missing",
                    )
                )
                continue

            try:
                final_target.parent.mkdir(parents=True, exist_ok=True)
                resolved_target = self._resolve_runtime_conflict(
                    source_path=source_path,
                    target_path=final_target,
                    separator=request.policy.conflict_suffix_separator,
                )
                shutil.move(str(source_path), str(resolved_target))
                executed_moves.append(
                    AssetMoveResultEntry(
                        source_path=source_path,
                        requested_target_path=requested_target,
                        final_target_path=resolved_target,
                        category=plan.category,
                        status="moved",
                    )
                )
            except Exception as exc:
                failed_moves.append(
                    AssetMoveResultEntry(
                        source_path=source_path,
                        requested_target_path=requested_target,
                        final_target_path=final_target,
                        category=plan.category,
                        status="failed",
                        details=f"{type(exc).__name__}: {exc}",
                    )
                )
                errors.append(
                    AssetOrganizeError(
                        code=ASSET_ORGANIZE_CODES["move_failed"],
                        message="Failed to move asset to organized destination.",
                        source=str(source_path),
                        details=format_details(
                            target=str(final_target),
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                )

        return AssetOrganizeResult(
            scan_path=request.scan_path,
            dry_run=False,
            planned_moves=self._sort_plan_entries(plan_entries),
            executed_moves=self._sort_result_entries(executed_moves),
            skipped_moves=self._sort_result_entries(skipped_moves),
            failed_moves=self._sort_result_entries(failed_moves),
            conflicts=self._sort_plan_entries(conflicts),
            warnings=sort_signals(warnings),
            errors=sort_signals(errors),
        )

    def _build_plan(
        self,
        request: AssetOrganizeRequest,
        candidate_files: list[Path],
    ) -> list[AssetMovePlanEntry]:
        rule_by_extension: dict[str, tuple[int, AssetOrganizeRule]] = {}
        for index, rule in enumerate(request.organize_rules):
            for extension in rule.extensions:
                if extension not in rule_by_extension:
                    rule_by_extension[extension] = (index, rule)

        plan_entries: list[AssetMovePlanEntry] = []
        for file_path in sorted(candidate_files, key=lambda item: item.as_posix().lower()):
            extension = file_path.suffix.lower()
            if extension not in rule_by_extension:
                continue

            rule_index, rule = rule_by_extension[extension]
            if self._already_organized(file_path, request.scan_path, rule):
                continue

            requested_target = (request.scan_path / rule.target_folder / file_path.name).resolve()
            final_target, conflict_index = self._resolve_conflict_for_plan(
                source_path=file_path.resolve(),
                target_path=requested_target,
                separator=request.policy.conflict_suffix_separator,
            )
            plan_entries.append(
                AssetMovePlanEntry(
                    source_path=file_path.resolve(),
                    requested_target_path=requested_target,
                    final_target_path=final_target,
                    category=rule.category,
                    conflict_detected=conflict_index > 0,
                    conflict_index=conflict_index,
                )
            )

        return sorted(
            plan_entries,
            key=lambda item: (
                next(
                    (
                        index
                        for index, rule in enumerate(request.organize_rules)
                        if rule.category == item.category
                    ),
                    999,
                ),
                item.source_path.as_posix().lower(),
            ),
        )

    def _list_files(
        self,
        scan_path: Path,
        skip_patterns: tuple[str, ...],
    ) -> tuple[list[Path], list[AssetOrganizeWarning]]:
        ensure_directory_readable(scan_path)
        files: list[Path] = []
        warnings: list[AssetOrganizeWarning] = []

        def _on_walk_error(exc: OSError) -> None:
            source = normalize_scan_source(exc.filename, scan_path)
            warnings.append(
                AssetOrganizeWarning(
                    code=ASSET_ORGANIZE_CODES["scan_partial_failed"],
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

    def _already_organized(
        self,
        file_path: Path,
        scan_path: Path,
        rule: AssetOrganizeRule,
    ) -> bool:
        parent_text = str(file_path.parent).lower()
        folder_lower = rule.target_folder.lower()
        if folder_lower in parent_text:
            return True
        if file_path.parent.name.lower() == folder_lower:
            return True
        try:
            relative_parent = file_path.parent.resolve().relative_to(scan_path.resolve())
            if relative_parent.parts and relative_parent.parts[0].lower() == folder_lower:
                return True
        except ValueError:
            return False
        return False

    def _resolve_conflict_for_plan(
        self,
        source_path: Path,
        target_path: Path,
        separator: str,
    ) -> tuple[Path, int]:
        if not target_path.exists() or target_path.resolve() == source_path.resolve():
            return target_path.resolve(), 0

        base = target_path.stem
        suffix = target_path.suffix
        conflict_index = 1
        candidate = target_path
        while candidate.exists() and candidate.resolve() != source_path.resolve():
            candidate = target_path.parent / f"{base}{separator}{conflict_index}{suffix}"
            conflict_index += 1
        return candidate.resolve(), conflict_index - 1

    def _resolve_runtime_conflict(
        self,
        source_path: Path,
        target_path: Path,
        separator: str,
    ) -> Path:
        if not target_path.exists() or target_path.resolve() == source_path.resolve():
            return target_path.resolve()

        base = target_path.stem
        suffix = target_path.suffix
        conflict_index = 1
        candidate = target_path
        while candidate.exists() and candidate.resolve() != source_path.resolve():
            candidate = target_path.parent / f"{base}{separator}{conflict_index}{suffix}"
            conflict_index += 1
        return candidate.resolve()

    def _sort_plan_entries(self, entries: list[AssetMovePlanEntry]) -> list[AssetMovePlanEntry]:
        return sorted(
            entries,
            key=lambda item: (
                item.category.lower(),
                item.source_path.as_posix().lower(),
                item.final_target_path.as_posix().lower(),
            ),
        )

    def _sort_result_entries(self, entries: list[AssetMoveResultEntry]) -> list[AssetMoveResultEntry]:
        return sorted(
            entries,
            key=lambda item: (
                item.category.lower(),
                item.source_path.as_posix().lower(),
                item.final_target_path.as_posix().lower(),
                item.status,
            ),
        )
