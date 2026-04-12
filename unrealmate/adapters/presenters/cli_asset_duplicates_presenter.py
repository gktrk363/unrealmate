# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Cli Asset Duplicates Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI presenter for asset duplicates structured results."""

from __future__ import annotations

from typing import Any, Callable

from rich.console import Console

from unrealmate.adapters.presenters.asset_presenter_utils import render_asset_warnings
from unrealmate.contracts.asset_duplicates import (
    AssetDuplicatesResult,
    AssetDuplicatesWarning,
    DuplicateGroup,
)


def render_asset_duplicates_result(
    result: AssetDuplicatesResult,
    console: Console,
    visuals_module: Any,
    format_size: Callable[[int], str],
) -> bool:
    """Render structured duplicate scan result without mutating analysis data."""
    if not result.has_data:
        console.print("[green]No duplicate assets found!  Your project is clean.[/green]\n")
        _render_warnings(result.warnings, console)
        return False

    console.print(f"[bold yellow]Found {result.total_groups} duplicate groups:[/bold yellow]\n")

    for group in _ordered_groups(result.groups):
        console.print(
            "[bold cyan]{name}[/bold cyan] [dim]({copies} copies, wasting {wasted})[/dim]".format(
                name=group.representative_name,
                copies=group.copies,
                wasted=format_size(group.wasted_size_bytes),
            )
        )
        for entry in group.entries:
            console.print(f"   [dim]->[/dim] {entry.path}")
        console.print()

    separator = "-" * 50 if getattr(visuals_module, "ASCII_MODE", False) else "─" * 50
    console.print(separator)
    console.print("\n[bold yellow]Summary:[/bold yellow]")
    console.print(f"   [bold]{result.total_groups}[/bold] duplicate groups")
    console.print(f"   [bold]{result.total_duplicate_files}[/bold] extra files")
    console.print(f"   [bold red]{format_size(result.total_wasted_size_bytes)}[/bold red] wasted space\n")

    _render_warnings(result.warnings, console)
    console.print("[dim]Tip: Remove duplicate files to save space and avoid confusion![/dim]\n")
    return True


def _ordered_groups(groups: list[DuplicateGroup]) -> list[DuplicateGroup]:
    return list(groups)


def _render_warnings(warnings: list[AssetDuplicatesWarning], console: Console) -> None:
    render_asset_warnings(console=console, warnings=warnings, bullet="-")
