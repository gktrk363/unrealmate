# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Cli Asset Organize Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI presenter for asset organize structured results."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from unrealmate.adapters.presenters.asset_presenter_utils import render_asset_warnings
from unrealmate.contracts.asset_organize import AssetOrganizeResult


def render_asset_organize_plan(
    result: AssetOrganizeResult,
    console: Console,
) -> bool:
    """Render organize plan preview and return whether there are planned moves."""
    if not result.has_changes:
        console.print("[green]✨ All assets are already organized![/green]\n")
        _render_warnings(result, console)
        return False

    table = Table(title="Files to Organize", show_header=True)
    table.add_column("📄 File", style="cyan")
    table.add_column("→", style="dim")
    table.add_column("📁 Destination", style="green")
    table.add_column("Category", style="magenta")

    for plan_entry in result.planned_moves:
        table.add_row(
            plan_entry.source_path.name,
            "→",
            f"{plan_entry.final_target_path.parent.name}/",
            plan_entry.category,
        )

    console.print(table)
    console.print(f"\n[bold]Total:  {len(result.planned_moves)} files to organize[/bold]\n")
    _render_warnings(result, console)
    return True


def render_asset_organize_dry_run_notice(console: Console) -> None:
    """Render dry-run completion message with stable signal."""
    console.print("[yellow]🔍 Dry run mode - no files were moved[/yellow]\n")


def render_asset_organize_execution(result: AssetOrganizeResult, console: Console) -> None:
    """Render execution completion summary for organized moves."""
    for failed in result.failed_moves:
        details = failed.details or "Unknown error"
        console.print(f"[red]❌ Failed to move {failed.source_path.name}: {details}[/red]")

    console.print("\n[bold green]🎉 Organization complete![/bold green]")
    console.print(
        f"[dim]Moved {len(result.executed_moves)} files, {len(result.failed_moves)} errors[/dim]\n"
    )
    _render_warnings(result, console)


def _render_warnings(result: AssetOrganizeResult, console: Console) -> None:
    render_asset_warnings(console=console, warnings=result.warnings, bullet="•")
