# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Analyze Performance Profile
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Use-case for structured performance profile analysis."""

from __future__ import annotations

from unrealmate.adapters.performance.profiler_adapter import PerformanceProfilerAdapter
from unrealmate.contracts.performance_profile import (
    PerformanceProfileError,
    PerformanceProfileRequest,
    PerformanceProfileResult,
)


class AnalyzePerformanceProfileUseCase:
    """Application use-case that orchestrates performance profile analysis."""

    def __init__(self, adapter: PerformanceProfilerAdapter | None = None) -> None:
        self._adapter = adapter or PerformanceProfilerAdapter()

    def execute(self, request: PerformanceProfileRequest) -> PerformanceProfileResult:
        if not request.project_path.exists():
            return PerformanceProfileResult(
                project_path=request.project_path,
                profiling_dir=request.project_path / "Saved" / "Profiling",
                errors=[
                    PerformanceProfileError(
                        code="project_path_not_found",
                        message=f"Project path does not exist: {request.project_path}",
                        source=str(request.project_path),
                    )
                ],
            )

        if not request.project_path.is_dir():
            return PerformanceProfileResult(
                project_path=request.project_path,
                profiling_dir=request.project_path / "Saved" / "Profiling",
                errors=[
                    PerformanceProfileError(
                        code="project_path_not_directory",
                        message=f"Project path is not a directory: {request.project_path}",
                        source=str(request.project_path),
                    )
                ],
            )

        return self._adapter.analyze(request)
