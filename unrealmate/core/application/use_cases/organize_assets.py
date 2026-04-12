# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Organize Assets
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Use-case for structured asset organize planning and execution."""

from __future__ import annotations

from unrealmate.adapters.assets.asset_organize_adapter import AssetOrganizeAdapter
from unrealmate.contracts.asset_organize import (
    AssetOrganizeError,
    AssetOrganizeRequest,
    AssetOrganizeResult,
)
from unrealmate.contracts.asset_domain_policy import ASSET_ORGANIZE_CODES


class OrganizeAssetsUseCase:
    """Application use-case that orchestrates asset organize flow."""

    def __init__(self, adapter: AssetOrganizeAdapter | None = None) -> None:
        self._adapter = adapter or AssetOrganizeAdapter()

    def execute(self, request: AssetOrganizeRequest) -> AssetOrganizeResult:
        if not request.scan_path.exists():
            return AssetOrganizeResult(
                scan_path=request.scan_path,
                dry_run=request.dry_run,
                errors=[
                    AssetOrganizeError(
                        code=ASSET_ORGANIZE_CODES["path_not_found"],
                        message=f"Organize path does not exist: {request.scan_path}",
                        source=str(request.scan_path),
                    )
                ],
            )

        if not request.scan_path.is_dir():
            return AssetOrganizeResult(
                scan_path=request.scan_path,
                dry_run=request.dry_run,
                errors=[
                    AssetOrganizeError(
                        code=ASSET_ORGANIZE_CODES["path_not_directory"],
                        message=f"Organize path is not a directory: {request.scan_path}",
                        source=str(request.scan_path),
                    )
                ],
            )

        return self._adapter.organize(request)
