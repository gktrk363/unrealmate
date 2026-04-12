# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Cli Git Setup Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI presenters for structured git setup results."""

from __future__ import annotations

from typing import Any, Callable

from rich.console import Console

from unrealmate.contracts.git_setup import GitInitResult, GitLfsResult


def render_git_init_result(
    result: GitInitResult,
    visuals_module: Any,
    format_size: Callable[[int], str],
    console: Console | None = None,
) -> None:
    """Render git init result on CLI without mutating business data."""
    if result.errors:
        _render_git_init_error(result, visuals_module, console)
        return

    if result.file_status == "skipped":
        visuals_module.print_warning_banner(
            "CONFIGURATION EXISTS",
            ".gitignore already exists in this directory.",
            "Use --force to overwrite the existing configuration.",
        )
        _render_warnings(result.warnings, console)
        return

    if result.file_status in {"would_create", "would_update"}:
        preview_label = "Would Update" if result.file_status == "would_update" else "Would Create"
        stats = {
            preview_label: ".gitignore",
            "Location": str(result.project_path),
            "Template Size": format_size(result.bytes_written),
            "Mode": "Preview",
        }
        visuals_module.print_warning_banner(
            "PREVIEW MODE",
            "No files were written to disk.",
            "Run without --dry-run to apply changes.",
        )
        if console is not None:
            _render_stats_table(stats, console)
        _render_warnings(result.warnings, console)
        return

    created_label = "File Updated" if result.file_status == "updated" else "File Created"
    stats = {
        created_label: ".gitignore",
        "Location": str(result.project_path),
        "Template Size": format_size(result.bytes_written),
    }
    visuals_module.print_success_banner(
        "CONFIGURATION COMPLETE",
        "Unreal Engine optimized .gitignore has been created.",
        stats,
    )
    _render_warnings(result.warnings, console)


def render_git_lfs_result(
    result: GitLfsResult,
    visuals_module: Any,
    console: Console | None = None,
) -> None:
    """Render git lfs result on CLI without mutating business data."""
    if result.errors:
        _render_git_lfs_error(result, visuals_module, console)
        return

    if result.file_status == "skipped":
        visuals_module.print_warning_banner(
            "LFS CONFIGURED",
            ".gitattributes already exists.",
            "Use --force to overwrite current LFS settings.",
        )
        _render_warnings(result.warnings, console)
        return

    if result.file_status in {"would_create", "would_update"}:
        attributes_label = "Would Update" if result.file_status == "would_update" else "Would Create"
        stats = {
            "LFS Status": "Dependency Check Passed",
            "Attributes": attributes_label,
            "Pattern Count": str(result.pattern_count),
            "Mode": "Preview",
        }
        visuals_module.print_warning_banner(
            "PREVIEW MODE",
            "No files were written and no git lfs install command was executed.",
            "Run without --dry-run to apply LFS setup.",
        )
        if console is not None:
            _render_stats_table(stats, console)
        _render_warnings(result.warnings, console)
        return

    attributes_label = "Updated" if result.file_status == "updated" else "Created"
    stats = {
        "LFS Status": "Initialized",
        "Attributes": attributes_label,
        "Pattern Count": str(result.pattern_count),
    }
    visuals_module.print_success_banner(
        "LFS ENABLED",
        "Git Large File Storage has been configured for this project.",
        stats,
    )
    _render_warnings(result.warnings, console)
    visuals_module.print_tip("Large binary files (uasset, umap) will now be properly versioned!")


def _render_git_init_error(result: GitInitResult, visuals_module: Any, console: Console | None) -> None:
    first_error = result.errors[0]
    if first_error.code == "template_missing":
        visuals_module.print_error_banner(
            "TEMPLATE MISSING",
            "Could not find the gitignore template file.",
            f"Expected location: {first_error.source}",
        )
        return
    if first_error.code in {"project_path_not_found", "project_path_not_directory"}:
        visuals_module.print_error_banner("INVALID PROJECT PATH", first_error.message)
        return
    if first_error.code == "write_failed":
        visuals_module.print_error_banner("WRITE ERROR", first_error.message, first_error.details)
    else:
        visuals_module.print_error_banner("SETUP FAILED", first_error.message, first_error.details)
    _render_errors(result.errors[1:], console)
    _render_warnings(result.warnings, console)


def _render_git_lfs_error(result: GitLfsResult, visuals_module: Any, console: Console | None) -> None:
    first_error = result.errors[0]
    if first_error.code == "git_lfs_missing":
        visuals_module.print_error_banner(
            "LFS MISSING",
            "Git LFS is not installed on your system.",
            "Install it from: https://git-lfs.github.com",
        )
    elif first_error.code == "template_missing":
        visuals_module.print_error_banner(
            "TEMPLATE MISSING",
            "Could not find gitattributes template.",
            f"Expected location: {first_error.source}",
        )
    elif first_error.code in {"project_path_not_found", "project_path_not_directory"}:
        visuals_module.print_error_banner("INVALID PROJECT PATH", first_error.message)
    elif first_error.code == "write_failed":
        visuals_module.print_error_banner("WRITE ERROR", first_error.message, first_error.details)
    elif first_error.code == "external_command_failed":
        visuals_module.print_error_banner("SETUP FAILED", first_error.message, first_error.details)
    else:
        visuals_module.print_error_banner("SETUP FAILED", first_error.message, first_error.details)
    _render_errors(result.errors[1:], console)
    _render_warnings(result.warnings, console)


def _render_warnings(warnings, console: Console | None) -> None:
    if not warnings or console is None:
        return
    console.print("[yellow]Warnings:[/yellow]")
    for warning in warnings:
        location = f" ({warning.source})" if warning.source else ""
        console.print(f"[yellow]- {warning.message}{location}[/yellow]")
        if warning.details:
            console.print(f"[dim]  details: {warning.details}[/dim]")
    console.print()


def _render_errors(errors, console: Console | None) -> None:
    if not errors or console is None:
        return
    console.print("[red]Additional errors:[/red]")
    for error in errors:
        location = f" ({error.source})" if error.source else ""
        console.print(f"[red]- {error.message}{location}[/red]")
        if error.details:
            console.print(f"[dim]  details: {error.details}[/dim]")
    console.print()


def _render_stats_table(stats: dict[str, str], console: Console) -> None:
    for key, value in stats.items():
        console.print(f"[dim]{key}:[/dim] {value}")
    console.print()
