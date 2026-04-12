# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Organize Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Presenter tests for asset organize rendering."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from rich.console import Console

from unrealmate.adapters.presenters.cli_asset_organize_presenter import (
    render_asset_organize_dry_run_notice,
    render_asset_organize_execution,
    render_asset_organize_plan,
)
from unrealmate.contracts.asset_organize import (
    AssetMovePlanEntry,
    AssetMoveResultEntry,
    AssetOrganizeResult,
)


def _build_console_buffer() -> tuple[Console, StringIO]:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, color_system=None, width=120)
    return console, stream


def test_asset_organize_presenter_plan_signal_is_stable(tmp_path: Path) -> None:
    scan_path = tmp_path.resolve()
    result = AssetOrganizeResult(
        scan_path=scan_path,
        dry_run=True,
        planned_moves=[
            AssetMovePlanEntry(
                source_path=scan_path / "LooseTexture.png",
                requested_target_path=scan_path / "Textures" / "LooseTexture.png",
                final_target_path=scan_path / "Textures" / "LooseTexture.png",
                category="Textures",
            )
        ],
    )
    console, stream = _build_console_buffer()

    has_plan = render_asset_organize_plan(result=result, console=console)
    output = stream.getvalue()

    assert has_plan is True
    assert "Files to Organize" in output
    assert "Total:  1 files to organize" in output


def test_asset_organize_presenter_dry_run_notice_signal_is_stable() -> None:
    console, stream = _build_console_buffer()
    render_asset_organize_dry_run_notice(console)
    output = stream.getvalue()

    assert "Dry run mode - no files were moved" in output


def test_asset_organize_presenter_execution_summary_signal_is_stable(tmp_path: Path) -> None:
    scan_path = tmp_path.resolve()
    result = AssetOrganizeResult(
        scan_path=scan_path,
        dry_run=False,
        executed_moves=[
            AssetMoveResultEntry(
                source_path=scan_path / "LooseTexture.png",
                requested_target_path=scan_path / "Textures" / "LooseTexture.png",
                final_target_path=scan_path / "Textures" / "LooseTexture.png",
                category="Textures",
                status="moved",
            )
        ],
        failed_moves=[],
    )
    console, stream = _build_console_buffer()

    render_asset_organize_execution(result=result, console=console)
    output = stream.getvalue()

    assert "Organization complete!" in output
    assert "Moved 1 files, 0 errors" in output

