# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - İnitialize Build Ci
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Use-case for structured build ci-init orchestration."""

from __future__ import annotations

from unrealmate.adapters.build.build_ci_adapter import BuildCiAdapter
from unrealmate.contracts.build_ci_init import (
    BuildCiInitError,
    BuildCiInitRequest,
    BuildCiInitResult,
    SUPPORTED_BUILD_CI_PROVIDERS,
)


class InitializeBuildCiUseCase:
    """Application use-case that orchestrates CI pipeline initialization."""

    def __init__(self, adapter: BuildCiAdapter | None = None) -> None:
        self._adapter = adapter or BuildCiAdapter()

    def execute(self, request: BuildCiInitRequest) -> BuildCiInitResult:
        if not request.project_path.exists():
            return BuildCiInitResult(
                project_path=request.project_path,
                platform=request.platform,
                preview_only=request.preview_only,
                errors=[
                    BuildCiInitError(
                        code="build_ci_path_not_found",
                        message=f"Project path does not exist: {request.project_path}",
                        source=str(request.project_path),
                    )
                ],
            )

        if not request.project_path.is_dir():
            return BuildCiInitResult(
                project_path=request.project_path,
                platform=request.platform,
                preview_only=request.preview_only,
                errors=[
                    BuildCiInitError(
                        code="build_ci_not_directory",
                        message=f"Project path is not a directory: {request.project_path}",
                        source=str(request.project_path),
                    )
                ],
            )

        if request.platform not in SUPPORTED_BUILD_CI_PROVIDERS:
            return BuildCiInitResult(
                project_path=request.project_path,
                platform=request.platform,
                preview_only=request.preview_only,
                errors=[
                    BuildCiInitError(
                        code="build_ci_provider_unsupported",
                        message=f"Unknown platform: {request.platform}",
                        source=request.platform,
                        details=f"supported={','.join(SUPPORTED_BUILD_CI_PROVIDERS)}",
                    )
                ],
            )

        uproject_files = sorted(request.project_path.glob("*.uproject"), key=lambda item: item.name.lower())
        if not uproject_files:
            return BuildCiInitResult(
                project_path=request.project_path,
                platform=request.platform,
                preview_only=request.preview_only,
                errors=[
                    BuildCiInitError(
                        code="build_ci_project_missing",
                        message="No .uproject file found!",
                        source=str(request.project_path),
                    )
                ],
            )

        selected_project_file = uproject_files[0].resolve()
        resolved_request = BuildCiInitRequest(
            project_path=request.project_path,
            platform=request.platform,
            preview_only=request.preview_only,
            selected_project_file=selected_project_file,
            selected_project_name=selected_project_file.stem,
            selection_strategy="alphabetical_first",
        )

        return self._adapter.initialize(resolved_request)
