# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - İnitialize Git Setup
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Use-cases for structured git init / git lfs setup."""

from __future__ import annotations

from unrealmate.adapters.git.git_setup_adapter import GitSetupAdapter
from unrealmate.contracts.git_setup import (
    GitInitRequest,
    GitInitResult,
    GitLfsRequest,
    GitLfsResult,
    GitSetupError,
)


class InitializeGitIgnoreUseCase:
    """Application use-case that initializes project .gitignore."""

    def __init__(self, adapter: GitSetupAdapter | None = None) -> None:
        self._adapter = adapter or GitSetupAdapter()

    def execute(self, request: GitInitRequest) -> GitInitResult:
        if not request.project_path.exists():
            return GitInitResult(
                project_path=request.project_path,
                target_path=request.project_path / request.target_filename,
                file_status="failed",
                preview_only=request.preview_only,
                errors=[
                    GitSetupError(
                        code="project_path_not_found",
                        message=f"Project path does not exist: {request.project_path}",
                        source=str(request.project_path),
                    )
                ],
            )

        if not request.project_path.is_dir():
            return GitInitResult(
                project_path=request.project_path,
                target_path=request.project_path / request.target_filename,
                file_status="failed",
                preview_only=request.preview_only,
                errors=[
                    GitSetupError(
                        code="project_path_not_directory",
                        message=f"Project path is not a directory: {request.project_path}",
                        source=str(request.project_path),
                    )
                ],
            )

        return self._adapter.initialize_gitignore(request)


class InitializeGitLfsUseCase:
    """Application use-case that initializes project git lfs settings."""

    def __init__(self, adapter: GitSetupAdapter | None = None) -> None:
        self._adapter = adapter or GitSetupAdapter()

    def execute(self, request: GitLfsRequest) -> GitLfsResult:
        if not request.project_path.exists():
            return GitLfsResult(
                project_path=request.project_path,
                target_path=request.project_path / request.target_filename,
                file_status="failed",
                preview_only=request.preview_only,
                dependency_status="unknown",
                errors=[
                    GitSetupError(
                        code="project_path_not_found",
                        message=f"Project path does not exist: {request.project_path}",
                        source=str(request.project_path),
                    )
                ],
            )

        if not request.project_path.is_dir():
            return GitLfsResult(
                project_path=request.project_path,
                target_path=request.project_path / request.target_filename,
                file_status="failed",
                preview_only=request.preview_only,
                dependency_status="unknown",
                errors=[
                    GitSetupError(
                        code="project_path_not_directory",
                        message=f"Project path is not a directory: {request.project_path}",
                        source=str(request.project_path),
                    )
                ],
            )

        return self._adapter.initialize_git_lfs(request)
