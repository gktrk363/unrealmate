# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Cli Build Ci Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI presenter for build ci-init structured results."""

from __future__ import annotations

from typing import Any

from rich.console import Console

from unrealmate.contracts.build_ci_init import BuildCiInitResult


def render_build_ci_init_result(
    result: BuildCiInitResult,
    console: Console,
    visuals_module: Any,
) -> bool:
    """
    Render structured build ci-init result without mutating business data.

    Returns:
        bool: True if command footer should be rendered by caller.
    """
    if result.errors:
        return _render_error(result=result, console=console, visuals_module=visuals_module)

    if not result.generated_files:
        console.print("[yellow]⚠️ No CI files were generated.[/yellow]\n")
        _render_warnings(result=result, console=console)
        return True

    primary_file = result.generated_files[0]
    provider_label = _provider_label(result.platform)
    selected_project_label = result.selected_project_name or "unknown"

    if primary_file.status in {"created", "updated"}:
        noun = "workflow created!" if result.platform == "github" else "configuration created!"
        if result.platform == "jenkins":
            noun = "Jenkinsfile created!"
            console.print(f"[green]✅ {noun}[/green]")
        else:
            console.print(f"[green]✅ {provider_label} {noun}[/green]")
    elif primary_file.status == "skipped":
        console.print(f"[yellow]⚠️ {provider_label} configuration already exists (skipped).[/yellow]")
    elif primary_file.status in {"would_create", "would_update"}:
        preview_action = "would be updated" if primary_file.status == "would_update" else "would be created"
        console.print(
            f"[yellow]⚠️ Preview mode: {provider_label} configuration {preview_action} (no files written).[/yellow]"
        )

    console.print(f"[dim]Project: {selected_project_label}[/dim]")
    console.print(f"[dim]Location: {primary_file.path}[/dim]\n")
    _render_warnings(result=result, console=console)
    console.print("[bold]Next Steps:[/bold]")
    console.print("1. Review and customize the generated configuration")
    console.print("2. Commit and push to your repository")
    console.print("3. Configure CI/CD runners/agents\n")
    return True


def _render_error(result: BuildCiInitResult, console: Console, visuals_module: Any) -> bool:
    error = result.errors[0]
    if error.code == "build_ci_provider_unsupported":
        console.print(f"[red]❌ Unknown platform: {result.platform}[/red]")
        console.print("[dim]Supported: github, gitlab, jenkins[/dim]\n")
        return False
    if error.code == "build_ci_path_not_found":
        visuals_module.print_error_banner("PATH NOT FOUND", error.message)
        return False
    if error.code == "build_ci_not_directory":
        visuals_module.print_error_banner("INVALID PATH", error.message)
        return False
    if error.code == "build_ci_project_missing":
        console.print("[red]❌ No .uproject file found![/red]\n")
        return False
    if error.code == "build_ci_template_missing":
        visuals_module.print_error_banner("TEMPLATE ERROR", error.message, error.details)
        return True
    if error.code == "build_ci_write_failed":
        visuals_module.print_error_banner("WRITE ERROR", error.message, error.details)
        return True

    visuals_module.print_error_banner("CI INIT FAILED", error.message, error.details)
    return True


def _render_warnings(result: BuildCiInitResult, console: Console) -> None:
    if not result.warnings:
        return
    console.print("[yellow]Warnings:[/yellow]")
    for warning in result.warnings:
        location = f" ({warning.source})" if warning.source else ""
        console.print(f"[yellow]• {warning.message}{location}[/yellow]")
        if warning.details:
            console.print(f"[dim]  details: {warning.details}[/dim]")
    console.print()


def _provider_label(platform: str) -> str:
    if platform == "github":
        return "GitHub Actions"
    if platform == "gitlab":
        return "GitLab CI"
    if platform == "jenkins":
        return "Jenkins"
    return platform
