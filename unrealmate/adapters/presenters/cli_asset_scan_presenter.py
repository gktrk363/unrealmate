# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Cli Asset Scan Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI presenter for asset scan structured results."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from unrealmate.adapters.presenters.asset_presenter_utils import render_asset_warnings
from unrealmate.contracts.asset_scan import AssetCategoryStat, AssetScanResult, AssetScanWarning


def render_asset_scan_result(
    result: AssetScanResult,
    console: Console,
    visuals_module: Any,
    show_all: bool = False,
) -> bool:
    """Render structured asset scan result without mutating analysis data."""
    if not result.has_data:
        visuals_module.print_warning_banner(
            "NO ASSETS FOUND",
            "Target directory appears to contain no trackable assets.",
        )
        return False

    _render_category_inventory(
        result=result,
        console=console,
        visuals_module=visuals_module,
    )

    largest_category = (
        max(result.categories, key=lambda category: category.size_bytes).name if result.categories else "N/A"
    )
    stats = {
        "Total Assets": f"{result.total_assets} files",
        "Total Size": _format_size(result.total_size_bytes),
        "Asset Categories": str(len(result.categories)),
        "Largest Category": largest_category,
    }
    console.print(visuals_module.create_stats_panel(stats, "Scan Summary", "blue"))

    if show_all and result.assets:
        _render_detailed_assets(
            result=result,
            console=console,
            visuals_module=visuals_module,
        )

    if result.largest_assets:
        _render_largest_assets(
            result=result,
            console=console,
            visuals_module=visuals_module,
        )

    if show_all and result.warnings:
        _render_warnings(result.warnings, console)

    return True


def _render_category_inventory(
    result: AssetScanResult,
    console: Console,
    visuals_module: Any,
) -> None:
    table = Table(title="Asset Inventory", show_header=True, box=visuals_module.ROUNDED, border_style="blue")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="magenta", justify="right")
    table.add_column("Size", style="yellow", justify="right")
    table.add_column("Distribution", style="green", width=20)

    bar_char = "#" if getattr(visuals_module, "ASCII_MODE", False) else "█"
    for category in _ordered_categories(result.categories):
        percentage = (category.size_bytes / result.total_size_bytes * 100) if result.total_size_bytes > 0 else 0
        bar = bar_char * int(percentage / 5)
        table.add_row(category.name, str(category.count), _format_size(category.size_bytes), bar)

    console.print(table)


def _render_detailed_assets(
    result: AssetScanResult,
    console: Console,
    visuals_module: Any,
) -> None:
    console.print("\n[bold]Detailed Asset List:[/bold]\n")
    detail_table = Table(show_header=True, box=visuals_module.MINIMAL)
    detail_table.add_column("File", style="cyan")
    detail_table.add_column("Category", style="magenta")
    detail_table.add_column("Size", style="yellow", justify="right")

    for asset in result.assets[: result.detailed_assets_limit]:
        detail_table.add_row(asset.name, asset.category, _format_size(asset.size_bytes))

    if len(result.assets) > result.detailed_assets_limit:
        remaining = len(result.assets) - result.detailed_assets_limit
        detail_table.add_row(f"... and {remaining} more", "", "")

    console.print(detail_table)


def _render_largest_assets(
    result: AssetScanResult,
    console: Console,
    visuals_module: Any,
) -> None:
    console.print(f"\n[bold] Top {result.largest_assets_limit} Largest Assets:[/bold]\n")
    top_table = Table(show_header=True, box=visuals_module.MINIMAL)
    top_table.add_column("File Name", style="cyan")
    top_table.add_column("Path", style="dim")
    top_table.add_column("Size", style="yellow", justify="right")

    for asset in result.largest_assets:
        top_table.add_row(asset.name, _relative_parent(asset.path, result.scan_path), _format_size(asset.size_bytes))

    console.print(top_table)


def _render_warnings(warnings: list[AssetScanWarning], console: Console) -> None:
    console.print()
    render_asset_warnings(console=console, warnings=warnings, bullet="•")


def _ordered_categories(categories: list[AssetCategoryStat]) -> list[AssetCategoryStat]:
    return list(categories)


def _relative_parent(asset_path: Path, scan_path: Path) -> str:
    try:
        return str(asset_path.parent.relative_to(scan_path))
    except ValueError:
        return str(asset_path.parent)


def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes} B"
