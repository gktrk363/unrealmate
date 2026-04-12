# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Scan Assets
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Use-case for structured asset scan analysis."""

from __future__ import annotations

from unrealmate.adapters.assets.asset_scan_adapter import AssetScanAdapter
from unrealmate.contracts.asset_scan import AssetScanError, AssetScanRequest, AssetScanResult
from unrealmate.contracts.asset_domain_policy import ASSET_SCAN_CODES


class ScanAssetsUseCase:
    """Application use-case that orchestrates asset scan analysis."""

    def __init__(self, adapter: AssetScanAdapter | None = None) -> None:
        self._adapter = adapter or AssetScanAdapter()

    def execute(self, request: AssetScanRequest) -> AssetScanResult:
        if not request.scan_path.exists():
            return AssetScanResult(
                scan_path=request.scan_path,
                errors=[
                    AssetScanError(
                        code=ASSET_SCAN_CODES["path_not_found"],
                        message=f"Scan path does not exist: {request.scan_path}",
                        source=str(request.scan_path),
                    )
                ],
                detailed_assets_limit=request.detailed_assets_limit,
                largest_assets_limit=request.largest_assets_limit,
            )

        if not request.scan_path.is_dir():
            return AssetScanResult(
                scan_path=request.scan_path,
                errors=[
                    AssetScanError(
                        code=ASSET_SCAN_CODES["path_not_directory"],
                        message=f"Scan path is not a directory: {request.scan_path}",
                        source=str(request.scan_path),
                    )
                ],
                detailed_assets_limit=request.detailed_assets_limit,
                largest_assets_limit=request.largest_assets_limit,
            )

        return self._adapter.scan(request)
