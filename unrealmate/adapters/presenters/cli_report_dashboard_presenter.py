# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Cli Report Dashboard Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI presenter for report dashboard structured lifecycle results."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel

from unrealmate.contracts.report_dashboard import (
    DashboardError,
    DashboardStartResult,
    DashboardStatus,
    DashboardWarning,
)


def render_report_dashboard_start_result(
    result: DashboardStartResult,
    console: Console,
    visuals_module: Any,
) -> bool:
    """Render startup result; returns True when caller should keep process alive."""
    if result.errors:
        _render_errors(result.errors, console=console, visuals_module=visuals_module)
        _render_warnings(result.warnings, console=console)
        return False

    console.print(Panel("[cyan]Experimental local dashboard is running.[/cyan]", border_style="cyan"))
    console.print(f"[green]✅ Open at {result.url}[/green]")
    console.print("[dim]Secondary surface only: use report json or report html for stable local report artifacts.[/dim]")
    if result.status and not result.status.browser_opened:
        if any(warning.code == "report_dashboard_browser_open_failed" for warning in result.warnings):
            console.print("[yellow]Browser auto-open failed; the local dashboard is still ready at the URL above. Open it manually or rerun with --no-open in headless environments.[/yellow]")
        else:
            console.print("[dim]Headless mode active (--no-open); no browser was opened. The local dashboard is ready at the URL above.[/dim]")
    console.print("[dim]Press Ctrl+C to stop the local dashboard server[/dim]")
    _render_warnings(result.warnings, console=console)
    return True


def render_report_dashboard_stop_status(
    status: DashboardStatus,
    console: Console,
) -> None:
    """Render shutdown status for dashboard lifecycle."""
    if status.shutdown_status == "clean":
        console.print("[green]✅ Local dashboard stopped.[/green]")
        return
    if status.shutdown_status == "not_running":
        console.print("[yellow]ℹ Local dashboard is not running.[/yellow]")
        return
    if status.shutdown_status == "timeout":
        location = status.url or f"http://{status.host}:{status.port}"
        console.print(f"[yellow]⚠ Local dashboard stop timed out; server may still be listening at {location}.[/yellow]")
        return
    location = status.url or f"http://{status.host}:{status.port}"
    console.print(f"[red]❌ Local dashboard stop failed; server state is uncertain for {location}.[/red]")


def _render_errors(
    errors: list[DashboardError],
    console: Console,
    visuals_module: Any,
) -> None:
    primary_error = errors[0]
    if primary_error.code == "report_dashboard_path_not_found":
        visuals_module.print_error_banner("PATH NOT FOUND", primary_error.message)
        return
    if primary_error.code == "report_dashboard_not_directory":
        visuals_module.print_error_banner("INVALID PATH", primary_error.message)
        return
    if primary_error.code == "report_dashboard_port_in_use":
        visuals_module.print_error_banner("PORT IN USE", primary_error.message, primary_error.details)
        return
    if primary_error.code == "report_dashboard_dependency_missing":
        visuals_module.print_error_banner("DEPENDENCY MISSING", primary_error.message, primary_error.details)
        return
    if primary_error.code == "report_dashboard_startup_timeout":
        visuals_module.print_error_banner("STARTUP TIMEOUT", primary_error.message, primary_error.details)
        return
    if primary_error.code == "report_dashboard_startup_failed":
        visuals_module.print_error_banner("STARTUP FAILED", primary_error.message, primary_error.details)
        return
    console.print(f"[red]❌ {primary_error.message}[/red]")


def _render_warnings(warnings: list[DashboardWarning], console: Console) -> None:
    if not warnings:
        return
    console.print("[yellow]Warnings:[/yellow]")
    for warning in warnings:
        location = f" ({warning.source})" if warning.source else ""
        console.print(f"[yellow]• {warning.message}{location}[/yellow]")
        if warning.details:
            console.print(f"[dim]  details: {warning.details}[/dim]")
