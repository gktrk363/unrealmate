# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Get Build İnfo
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Use-case for structured build info metadata extraction."""

from __future__ import annotations

from unrealmate.adapters.build.build_info_adapter import BuildInfoAdapter
from unrealmate.contracts.build_info import (
    BuildInfoError,
    BuildInfoRequest,
    BuildInfoResult,
)


class GetBuildInfoUseCase:
    """Application use-case that orchestrates build metadata retrieval."""

    def __init__(self, adapter: BuildInfoAdapter | None = None) -> None:
        self._adapter = adapter or BuildInfoAdapter()

    def execute(self, request: BuildInfoRequest) -> BuildInfoResult:
        if not request.project_path.exists():
            return BuildInfoResult(
                project_path=request.project_path,
                errors=[
                    BuildInfoError(
                        code="build_info_path_not_found",
                        message=f"Project path does not exist: {request.project_path}",
                        source=str(request.project_path),
                    )
                ],
            )

        if not request.project_path.is_dir():
            return BuildInfoResult(
                project_path=request.project_path,
                errors=[
                    BuildInfoError(
                        code="build_info_not_directory",
                        message=f"Project path is not a directory: {request.project_path}",
                        source=str(request.project_path),
                    )
                ],
            )

        return self._adapter.collect(request)

