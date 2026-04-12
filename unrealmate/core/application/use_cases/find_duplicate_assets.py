# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Find Duplicate Assets
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Use-case for structured asset duplicate analysis."""

from __future__ import annotations

from unrealmate.adapters.assets.asset_duplicates_adapter import AssetDuplicatesAdapter
from unrealmate.contracts.asset_duplicates import (
    AssetDuplicatesError,
    AssetDuplicatesRequest,
    AssetDuplicatesResult,
)
from unrealmate.contracts.asset_domain_policy import ASSET_DUPLICATES_CODES


class FindDuplicateAssetsUseCase:
    """Application use-case that orchestrates duplicate asset scanning."""

    def __init__(self, adapter: AssetDuplicatesAdapter | None = None) -> None:
        self._adapter = adapter or AssetDuplicatesAdapter()

    def execute(self, request: AssetDuplicatesRequest) -> AssetDuplicatesResult:
        if not request.scan_path.exists():
            return AssetDuplicatesResult(
                scan_path=request.scan_path,
                by_content=request.by_content,
                grouping_mode=request.grouping_mode,
                hash_strategy=request.hash_strategy,
                errors=[
                    AssetDuplicatesError(
                        code=ASSET_DUPLICATES_CODES["path_not_found"],
                        message=f"Scan path does not exist: {request.scan_path}",
                        source=str(request.scan_path),
                    )
                ],
            )

        if not request.scan_path.is_dir():
            return AssetDuplicatesResult(
                scan_path=request.scan_path,
                by_content=request.by_content,
                grouping_mode=request.grouping_mode,
                hash_strategy=request.hash_strategy,
                errors=[
                    AssetDuplicatesError(
                        code=ASSET_DUPLICATES_CODES["path_not_directory"],
                        message=f"Scan path is not a directory: {request.scan_path}",
                        source=str(request.scan_path),
                    )
                ],
            )

        return self._adapter.find_duplicates(request)
