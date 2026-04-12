# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - contracts
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Typed contracts shared between CLI/application/adapters."""

from unrealmate.contracts.asset_scan import (
    AssetCategoryStat,
    AssetScanEntry,
    AssetScanError,
    AssetScanPolicy,
    AssetScanRequest,
    AssetScanResult,
    AssetScanWarning,
)
from unrealmate.contracts.asset_duplicates import (
    AssetDuplicatesError,
    AssetDuplicatesPolicy,
    AssetDuplicatesRequest,
    AssetDuplicatesResult,
    AssetDuplicatesWarning,
    DuplicateEntry,
    DuplicateGroup,
)
from unrealmate.contracts.asset_organize import (
    AssetMovePlanEntry,
    AssetMoveResultEntry,
    AssetOrganizeError,
    AssetOrganizePolicy,
    AssetOrganizeRequest,
    AssetOrganizeResult,
    AssetOrganizeRule,
    AssetOrganizeWarning,
)
from unrealmate.contracts.git_setup import (
    GitExternalCommandResult,
    GitInitRequest,
    GitInitResult,
    GitLfsRequest,
    GitLfsResult,
    GitProcessPolicy,
    GitSetupError,
    GitSetupWarning,
)
from unrealmate.contracts.performance_profile import (
    PerformanceBottleneckResult,
    PerformanceMetricResult,
    PerformanceProfileError,
    PerformanceProfileRequest,
    PerformanceProfileResult,
    PerformanceProfileWarning,
)
from unrealmate.contracts.build_info import (
    BuildEnvironmentInfo,
    BuildInfoError,
    BuildInfoRequest,
    BuildInfoResult,
    BuildInfoWarning,
    BuildMetadata,
)
from unrealmate.contracts.build_ci_init import (
    BuildArtifactEntry,
    BuildCiInitError,
    BuildCiInitRequest,
    BuildCiInitResult,
    BuildCiInitWarning,
    GeneratedFileEntry,
)
from unrealmate.contracts.report_json import (
    ReportGeneratedArtifact,
    ReportJsonError,
    ReportJsonRequest,
    ReportJsonResult,
    ReportJsonWarning,
    ReportProjectStats,
)
from unrealmate.contracts.report_html import (
    ReportHtmlError,
    ReportHtmlRequest,
    ReportHtmlResult,
    ReportHtmlWarning,
)
from unrealmate.contracts.report_dashboard import (
    DashboardDataSnapshot,
    DashboardError,
    DashboardStartRequest,
    DashboardStartResult,
    DashboardStatus,
    DashboardWarning,
)

__all__ = [
    "AssetCategoryStat",
    "AssetDuplicatesError",
    "AssetDuplicatesPolicy",
    "AssetDuplicatesRequest",
    "AssetDuplicatesResult",
    "AssetDuplicatesWarning",
    "AssetMovePlanEntry",
    "AssetMoveResultEntry",
    "AssetOrganizeError",
    "AssetOrganizePolicy",
    "AssetOrganizeRequest",
    "AssetOrganizeResult",
    "AssetOrganizeRule",
    "AssetOrganizeWarning",
    "AssetScanEntry",
    "AssetScanError",
    "AssetScanPolicy",
    "AssetScanRequest",
    "AssetScanResult",
    "AssetScanWarning",
    "DuplicateEntry",
    "DuplicateGroup",
    "GitExternalCommandResult",
    "GitInitRequest",
    "GitInitResult",
    "GitLfsRequest",
    "GitLfsResult",
    "GitProcessPolicy",
    "GitSetupError",
    "GitSetupWarning",
    "BuildEnvironmentInfo",
    "BuildInfoError",
    "BuildInfoRequest",
    "BuildInfoResult",
    "BuildInfoWarning",
    "BuildMetadata",
    "BuildArtifactEntry",
    "BuildCiInitError",
    "BuildCiInitRequest",
    "BuildCiInitResult",
    "BuildCiInitWarning",
    "GeneratedFileEntry",
    "DashboardDataSnapshot",
    "DashboardError",
    "DashboardStartRequest",
    "DashboardStartResult",
    "DashboardStatus",
    "DashboardWarning",
    "ReportGeneratedArtifact",
    "ReportHtmlError",
    "ReportHtmlRequest",
    "ReportHtmlResult",
    "ReportHtmlWarning",
    "ReportJsonError",
    "ReportJsonRequest",
    "ReportJsonResult",
    "ReportJsonWarning",
    "ReportProjectStats",
    "PerformanceBottleneckResult",
    "PerformanceMetricResult",
    "PerformanceProfileError",
    "PerformanceProfileRequest",
    "PerformanceProfileResult",
    "PerformanceProfileWarning",
]
