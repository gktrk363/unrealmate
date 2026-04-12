# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Cli Report Json Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI presenter for report json structured results."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.panel import Panel

from unrealmate.contracts.report_json import (
    ReportGeneratedArtifact,
    ReportJsonError,
    ReportJsonResult,
    ReportJsonWarning,
)


def render_report_json_result(
    result: ReportJsonResult,
    console: Console,
    visuals_module: Any,
) -> bool:
    """Render structured report json result without mutating domain data."""
    if result.errors:
        _render_errors(result.errors, console=console, visuals_module=visuals_module)
        _render_warnings(result.warnings, console=console, visuals_module=visuals_module)
        return True

    document = result.to_report_document()
    json_str = json.dumps(document, indent=2, default=str)
    console.print(
        visuals_module.create_section_title(
            "Local JSON Snapshot",
            "Local filesystem snapshot only; not live editor or runtime state.",
        )
    )
    console.print(Panel(json_str, title="Snapshot Data", border_style="cyan", box=visuals_module.ROUNDED))

    _render_artifacts(result.artifacts, console=console, visuals_module=visuals_module)
    _render_warnings(result.warnings, console=console, visuals_module=visuals_module)

    return True


def _render_errors(
    errors: list[ReportJsonError],
    console: Console,
    visuals_module: Any,
) -> None:
    primary_error = errors[0]
    if primary_error.code == "report_json_path_not_found":
        console.print(visuals_module.create_message_panel("error", "PATH NOT FOUND", body=primary_error.message))
        return
    if primary_error.code == "report_json_not_directory":
        console.print(visuals_module.create_message_panel("error", "INVALID PATH", body=primary_error.message))
        return

    console.print(visuals_module.create_message_panel("error", "REPORT JSON ERROR", body=primary_error.message))


def _render_artifacts(artifacts: list[ReportGeneratedArtifact], console: Console, visuals_module: Any) -> None:
    for artifact in artifacts:
        if artifact.status in {"created", "updated"}:
            console.print(
                visuals_module.create_message_panel(
                    "success",
                    "Local JSON snapshot saved.",
                    body="This remains a local filesystem snapshot; review it before sharing.",
                    stats={"Location": artifact.path},
                )
            )
            continue

        if artifact.status == "failed":
            console.print(
                visuals_module.create_message_panel(
                    "error",
                    "Failed to save local JSON snapshot.",
                    stats={"Target": artifact.path},
                )
            )


def _render_warnings(warnings: list[ReportJsonWarning], console: Console, visuals_module: Any) -> None:
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
