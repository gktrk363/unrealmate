# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Cli Build İnfo Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI presenter for build info structured results."""

from __future__ import annotations

from typing import Any

from rich.console import Console

from unrealmate.contracts.build_info import BuildInfoError, BuildInfoResult, BuildInfoWarning


_BUILD_RECOMMENDATIONS: tuple[str, ...] = (
    "Use `unrealmate build ci-init` to generate a starter CI/CD pipeline file",
    "Enable parallel compilation for faster builds",
    "Use incremental builds during development",
    "Configure build configurations (Development, Shipping, etc.)",
)


def render_build_info_result(
    result: BuildInfoResult,
    console: Console,
    visuals_module: Any,
) -> bool:
    """
    Render structured build info result without mutating business data.

    Returns:
        bool: True if caller should print command footer, False otherwise.
    """
    if result.errors:
        return _render_error(result.errors[0], console=console, visuals_module=visuals_module)

    if result.metadata is None:
        console.print(
            visuals_module.create_message_panel(
                "error",
                "Project File Missing",
                body="No .uproject file found in the given path.",
            )
        )
        return False

    console.print(
        visuals_module.create_section_title(
            "Build Metadata",
            "Advisory summary from local .uproject metadata.",
        )
    )
    console.print(
        visuals_module.create_key_value_panel(
            "Project Information",
            [
                ("Project Name", result.metadata.project_name),
                ("Engine Version", result.metadata.engine_version),
                ("Category", result.metadata.category),
                ("Description", result.metadata.description),
                ("Plugins", result.metadata.plugin_count),
            ],
            accent="yellow",
        )
    )
    console.print()

    _render_warnings(result.warnings, console=console, visuals_module=visuals_module)

    recommendation_lines = "\n".join(f"- {recommendation}" for recommendation in _BUILD_RECOMMENDATIONS)
    console.print(
        visuals_module.create_message_panel(
            "info",
            "Starter Build Guidance",
            body=recommendation_lines,
        )
    )
    console.print()
    return True


def _render_error(error: BuildInfoError, console: Console, visuals_module: Any) -> bool:
    if error.code == "build_info_path_not_found":
        visuals_module.print_error_banner("PATH NOT FOUND", error.message)
        return False
    if error.code == "build_info_not_directory":
        visuals_module.print_error_banner("INVALID PATH", error.message)
        return False
    if error.code == "build_info_project_missing":
        console.print(
            visuals_module.create_message_panel(
                "error",
                "Project File Missing",
                body=error.message,
            )
        )
        return False
    if error.code == "build_info_parse_failed":
        console.print(
            visuals_module.create_message_panel(
                "error",
                "Parse Error",
                body=error.message,
            )
        )
        return True

    console.print(
        visuals_module.create_message_panel(
            "error",
            "Build Info Error",
            body=error.message,
        )
    )
    return True


def _render_warnings(warnings: list[BuildInfoWarning], console: Console, visuals_module: Any) -> None:
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
            "Build Metadata Warnings",
            body="\n".join(warning_lines),
        )
    )
    console.print()

