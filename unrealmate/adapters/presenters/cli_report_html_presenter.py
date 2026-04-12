# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Cli Report Html Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI presenter for report html structured results."""

from __future__ import annotations

from typing import Any

from rich.console import Console

from unrealmate.contracts.report_html import (
    ReportHtmlError,
    ReportHtmlResult,
    ReportHtmlWarning,
)
from unrealmate.contracts.report_json import ReportGeneratedArtifact


def render_report_html_result(
    result: ReportHtmlResult,
    console: Console,
    visuals_module: Any,
) -> bool:
    """Render structured report html result without mutating domain data."""
    if result.errors:
        _render_errors(result.errors, console=console, visuals_module=visuals_module)
        _render_warnings(result.warnings, console=console, visuals_module=visuals_module)
        return True

    _render_artifacts(result.artifacts, console=console, visuals_module=visuals_module)

    stats = {
        ".uproject files": str(result.stats.uproject_files),
        "C++ source files": str(result.stats.cpp_source_files),
        "Blueprint assets": str(result.stats.blueprint_assets),
        "Scene maps": str(result.stats.scene_maps),
        "Python scripts": str(result.python_script_count),
    }
    console.print(visuals_module.create_stats_panel(stats, "Report Summary", "dark_orange"))
    _render_warnings(result.warnings, console=console, visuals_module=visuals_module)
    return True


def _render_errors(
    errors: list[ReportHtmlError],
    console: Console,
    visuals_module: Any,
) -> None:
    primary_error = errors[0]
    if primary_error.code == "report_html_path_not_found":
        visuals_module.print_error_banner("PATH NOT FOUND", primary_error.message)
        return
    if primary_error.code == "report_html_not_directory":
        visuals_module.print_error_banner("INVALID PATH", primary_error.message)
        return
    if primary_error.code == "report_html_template_failed":
        visuals_module.print_error_banner("TEMPLATE ERROR", primary_error.message, primary_error.details)
        return
    if primary_error.code == "report_html_write_failed":
        visuals_module.print_error_banner("WRITE ERROR", primary_error.message, primary_error.details)
        return
    visuals_module.print_error_banner("REPORT ERROR", primary_error.message)


def _render_artifacts(artifacts: list[ReportGeneratedArtifact], console: Console, visuals_module: Any) -> None:
    for artifact in artifacts:
        if artifact.status in {"created", "updated"}:
            console.print(
                visuals_module.create_message_panel(
                    "success",
                    "Local HTML report saved.",
                    body="This is a local filesystem snapshot; review before sharing.",
                    stats={"Location": artifact.path},
                )
            )
            continue

        if artifact.status == "failed":
            console.print(
                visuals_module.create_message_panel(
                    "error",
                    "Failed to save local HTML report.",
                    stats={"Target": artifact.path},
                )
            )


def _render_warnings(warnings: list[ReportHtmlWarning], console: Console, visuals_module: Any) -> None:
    if not warnings:
        return
    warning_lines: list[str] = []
    for warning in warnings:
        location = f" ({warning.source})" if warning.source else ""
        line = f"- {warning.message}{location}"
        if warning.details:
            line += f"\n  details: {warning.details}"
        warning_lines.append(line)
    console.print(
        visuals_module.create_message_panel(
            "warning",
            "Warnings",
            body="\n".join(warning_lines),
        )
    )

