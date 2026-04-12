# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - use_cases
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Application use-case entry points."""

from unrealmate.core.application.use_cases.analyze_performance_profile import (
    AnalyzePerformanceProfileUseCase,
)
from unrealmate.core.application.use_cases.find_duplicate_assets import (
    FindDuplicateAssetsUseCase,
)
from unrealmate.core.application.use_cases.initialize_git_setup import (
    InitializeGitIgnoreUseCase,
    InitializeGitLfsUseCase,
)
from unrealmate.core.application.use_cases.organize_assets import (
    OrganizeAssetsUseCase,
)
from unrealmate.core.application.use_cases.scan_assets import ScanAssetsUseCase
from unrealmate.core.application.use_cases.get_build_info import GetBuildInfoUseCase
from unrealmate.core.application.use_cases.initialize_build_ci import (
    InitializeBuildCiUseCase,
)
from unrealmate.core.application.use_cases.generate_json_report import (
    GenerateJsonReportUseCase,
)
from unrealmate.core.application.use_cases.generate_html_report import (
    GenerateHtmlReportUseCase,
)
from unrealmate.core.application.use_cases.start_report_dashboard import (
    StartReportDashboardUseCase,
)

__all__ = [
    "AnalyzePerformanceProfileUseCase",
    "FindDuplicateAssetsUseCase",
    "GenerateJsonReportUseCase",
    "GenerateHtmlReportUseCase",
    "StartReportDashboardUseCase",
    "GetBuildInfoUseCase",
    "InitializeBuildCiUseCase",
    "InitializeGitIgnoreUseCase",
    "InitializeGitLfsUseCase",
    "OrganizeAssetsUseCase",
    "ScanAssetsUseCase",
]
