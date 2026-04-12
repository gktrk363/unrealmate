# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Scan Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Presenter tests for stabilized asset scan rendering."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from rich import box
from rich.console import Console

from unrealmate.adapters.presenters.cli_asset_scan_presenter import render_asset_scan_result
from unrealmate.contracts.asset_scan import (
    AssetCategoryStat,
    AssetScanEntry,
    AssetScanResult,
    AssetScanWarning,
)


class _FakeVisuals:
    ROUNDED = box.ROUNDED
    MINIMAL = box.MINIMAL
    ASCII_MODE = False

    def __init__(self) -> None:
        self.warning_banner_calls: list[tuple[str, str]] = []

    def create_stats_panel(self, stats, title, color):  # type: ignore[no-untyped-def]
        return f"{title}: {stats['Total Assets']}"

    def print_warning_banner(self, title: str, message: str) -> None:
        self.warning_banner_calls.append((title, message))


def _build_console() -> tuple[Console, StringIO]:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, color_system=None, width=120)
    return console, stream


def test_asset_scan_presenter_renders_stable_sections_for_normal_result(tmp_path: Path) -> None:
    scan_path = tmp_path.resolve()
    visuals = _FakeVisuals()
    console, stream = _build_console()

    result = AssetScanResult(
        scan_path=scan_path,
        categories=[
            AssetCategoryStat(name="Blueprints", count=1, size_bytes=300),
            AssetCategoryStat(name="Textures", count=1, size_bytes=100),
        ],
        assets=[
            AssetScanEntry(path=scan_path / "BP_Player.uasset", category="Blueprints", size_bytes=300),
            AssetScanEntry(path=scan_path / "T_Albedo.png", category="Textures", size_bytes=100),
        ],
        largest_assets=[
            AssetScanEntry(path=scan_path / "BP_Player.uasset", category="Blueprints", size_bytes=300),
            AssetScanEntry(path=scan_path / "T_Albedo.png", category="Textures", size_bytes=100),
        ],
        total_assets=2,
        total_size_bytes=400,
    )

    rendered = render_asset_scan_result(result=result, console=console, visuals_module=visuals, show_all=True)
    output = stream.getvalue()

    assert rendered is True
    assert "Asset Inventory" in output
    assert "Scan Summary" in output
    assert "Detailed Asset List:" in output
    assert "Top 5 Largest Assets:" in output


def test_asset_scan_presenter_warning_rendering_is_deterministic(tmp_path: Path) -> None:
    scan_path = tmp_path.resolve()
    visuals = _FakeVisuals()
    console, stream = _build_console()

    result = AssetScanResult(
        scan_path=scan_path,
        categories=[AssetCategoryStat(name="Blueprints", count=1, size_bytes=1)],
        assets=[AssetScanEntry(path=scan_path / "BP_Test.uasset", category="Blueprints", size_bytes=1)],
        largest_assets=[AssetScanEntry(path=scan_path / "BP_Test.uasset", category="Blueprints", size_bytes=1)],
        total_assets=1,
        total_size_bytes=1,
        warnings=[
            AssetScanWarning(code="scan_pattern_failed", message="B", source="x", details="2"),
            AssetScanWarning(code="asset_stat_failed", message="A", source="x", details="1"),
        ],
    )

    render_asset_scan_result(result=result, console=console, visuals_module=visuals, show_all=True)
    output = stream.getvalue()

    first = output.find("A (x)")
    second = output.find("B (x)")
    assert first != -1 and second != -1
    assert first < second


def test_asset_scan_presenter_no_data_uses_warning_banner(tmp_path: Path) -> None:
    visuals = _FakeVisuals()
    console, _ = _build_console()
    result = AssetScanResult(scan_path=tmp_path.resolve())

    rendered = render_asset_scan_result(result=result, console=console, visuals_module=visuals, show_all=False)

    assert rendered is False
    assert visuals.warning_banner_calls == [
        ("NO ASSETS FOUND", "Target directory appears to contain no trackable assets.")
    ]
