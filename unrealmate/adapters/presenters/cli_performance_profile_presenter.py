# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Cli Performance Profile Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI presenter for performance profile structured results."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from unrealmate.contracts.performance_profile import PerformanceProfileResult
from unrealmate.core import visuals


def render_performance_profile_result(
    result: PerformanceProfileResult,
    console: Console,
    show_all: bool = False,
) -> None:
    """Render structured performance profile result without mutating business data."""
    console.print(
        visuals.create_section_title(
            "Performance Analysis",
            "Advisory local analysis from profiling exports.",
        )
    )
    console.print()

    if result.metrics:
        if not show_all and len(result.metrics) > 20:
            console.print(
                visuals.create_message_panel(
                    "info",
                    "Metric Window",
                    body=f"Showing first 20 of {len(result.metrics)} metrics. Use --all to show all.",
                )
            )
            console.print()

        table = Table(title="Performance Metrics")
        table.add_column("Category", style="cyan")
        table.add_column("Metric", style="white")
        table.add_column("Value", justify="right")
        table.add_column("Severity", justify="center")

        limit = len(result.metrics) if show_all else 20
        for metric in result.metrics[:limit]:
            severity_color = {
                "OK": "green",
                "Warning": "yellow",
                "Critical": "red",
            }.get(metric.severity, "white")
            table.add_row(
                metric.category,
                metric.name,
                f"{metric.value:.2f} {metric.unit}",
                f"[{severity_color}]{metric.severity}[/]",
            )

        console.print(Panel(table, border_style="cyan", box=visuals.ROUNDED, padding=(0, 1)))
    else:
        console.print(
            visuals.create_message_panel(
                "warning",
                "No Performance Metrics",
                body="No performance metrics found.",
                suggestion="Add local profiling CSV exports before running this advisory analysis again.",
            )
        )

    if result.bottlenecks:
        bottleneck_lines: list[str] = []
        for index, bottleneck in enumerate(result.bottlenecks, 1):
            bottleneck_lines.append(
                "\n".join(
                    [
                        f"{index}. {bottleneck.location}",
                        f"   Issue: {bottleneck.issue}",
                        f"   Impact: {bottleneck.impact}",
                        f"   Suggestion: {bottleneck.suggestion}",
                    ]
                )
            )
        console.print()
        console.print(
            visuals.create_message_panel(
                "warning",
                "Detected Bottlenecks",
                body="\n\n".join(bottleneck_lines),
            )
        )
    else:
        console.print()
        console.print(
            visuals.create_message_panel(
                "success",
                "Bottleneck Summary",
                body="No critical bottlenecks detected!",
            )
        )

    if result.warnings:
        warning_lines: list[str] = []
        for warning in result.warnings:
            location = f" ({warning.source})" if warning.source else ""
            line = f"- {warning.message}{location}"
            if show_all and warning.details:
                line += f"\n  details: {warning.details}"
            warning_lines.append(line)
        console.print()
        console.print(
            visuals.create_message_panel(
                "warning",
                "Analysis Warnings",
                body="\n".join(warning_lines),
            )
        )
        console.print()
