# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Duplicates Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Presenter tests for asset duplicates terminal rendering."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from rich.console import Console

from unrealmate.adapters.presenters.cli_asset_duplicates_presenter import (
    render_asset_duplicates_result,
)
from unrealmate.contracts.asset_duplicates import (
    AssetDuplicatesResult,
    AssetDuplicatesWarning,
    DuplicateEntry,
    DuplicateGroup,
)


class _FakeVisuals:
    ASCII_MODE = False


def _build_console_buffer() -> tuple[Console, StringIO]:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, color_system=None, width=120)
    return console, stream


def test_asset_duplicates_presenter_renders_summary_signals(tmp_path: Path) -> None:
    scan_path = tmp_path.resolve()
    result = AssetDuplicatesResult(
        scan_path=scan_path,
        by_content=False,
        groups=[
            DuplicateGroup(
                group_key="shared.png",
                representative_name="Shared.png",
                entries=[
                    DuplicateEntry(path=scan_path / "A" / "Shared.png", size_bytes=100),
                    DuplicateEntry(path=scan_path / "B" / "Shared.png", size_bytes=100),
                ],
                copies=2,
                duplicate_files=1,
                retained_size_bytes=100,
                total_group_size_bytes=200,
                wasted_size_bytes=100,
            )
        ],
        total_groups=1,
        total_duplicate_files=1,
        total_wasted_size_bytes=100,
        scanned_candidate_files=2,
    )

    console, stream = _build_console_buffer()
    rendered = render_asset_duplicates_result(
        result=result,
        console=console,
        visuals_module=_FakeVisuals(),
        format_size=lambda size: f"{size} B",
    )
    output = stream.getvalue()

    assert rendered is True
    assert "Found 1 duplicate groups:" in output
    assert "Summary:" in output
    assert "1 duplicate groups" in output
    assert "1 extra files" in output


def test_asset_duplicates_presenter_no_duplicates_signal_is_stable(tmp_path: Path) -> None:
    result = AssetDuplicatesResult(
        scan_path=tmp_path.resolve(),
        by_content=False,
        warnings=[
            AssetDuplicatesWarning(
                code="no_duplicates_found",
                message="No duplicate assets found.",
                source=str(tmp_path.resolve()),
                details="scanned_candidates=0",
            )
        ],
    )
    console, stream = _build_console_buffer()

    rendered = render_asset_duplicates_result(
        result=result,
        console=console,
        visuals_module=_FakeVisuals(),
        format_size=lambda size: f"{size} B",
    )
    output = stream.getvalue()

    assert rendered is False
    assert "No duplicate assets found!  Your project is clean." in output
    assert "Warnings:" in output
