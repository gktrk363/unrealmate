# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - presenters
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Presentation helpers for client-specific rendering."""

from unrealmate.adapters.presenters.cli_asset_scan_presenter import (
    render_asset_scan_result,
)
from unrealmate.adapters.presenters.cli_asset_organize_presenter import (
    render_asset_organize_dry_run_notice,
    render_asset_organize_execution,
    render_asset_organize_plan,
)
from unrealmate.adapters.presenters.cli_asset_duplicates_presenter import (
    render_asset_duplicates_result,
)
from unrealmate.adapters.presenters.cli_git_setup_presenter import (
    render_git_init_result,
    render_git_lfs_result,
)
from unrealmate.adapters.presenters.cli_performance_profile_presenter import (
    render_performance_profile_result,
)
from unrealmate.adapters.presenters.cli_build_info_presenter import (
    render_build_info_result,
)
from unrealmate.adapters.presenters.cli_build_ci_presenter import (
    render_build_ci_init_result,
)
from unrealmate.adapters.presenters.cli_report_json_presenter import (
    render_report_json_result,
)
from unrealmate.adapters.presenters.cli_report_html_presenter import (
    render_report_html_result,
)

__all__ = [
    "render_performance_profile_result",
    "render_asset_scan_result",
    "render_asset_organize_plan",
    "render_asset_organize_dry_run_notice",
    "render_asset_organize_execution",
    "render_asset_duplicates_result",
    "render_git_init_result",
    "render_git_lfs_result",
    "render_build_info_result",
    "render_build_ci_init_result",
    "render_report_json_result",
    "render_report_html_result",
]
