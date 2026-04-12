# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Asset Presenter Utils
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Shared rendering utilities for asset-domain CLI presenters."""

from __future__ import annotations

from typing import Sequence, TypeVar

from rich.console import Console

from unrealmate.contracts.asset_domain_common import sort_signal_items


TSignal = TypeVar("TSignal")


def render_asset_warnings(
    *,
    console: Console,
    warnings: Sequence[TSignal],
    bullet: str = "•",
) -> None:
    """Render sorted asset-domain warnings with consistent details surface."""
    if not warnings:
        return

    console.print("[yellow]Warnings:[/yellow]")
    for warning in sort_signal_items(warnings):
        location = f" ({getattr(warning, 'source', None)})" if getattr(warning, "source", None) else ""
        console.print(f"[yellow]{bullet} {warning.message}{location}[/yellow]")
        details = getattr(warning, "details", None)
        if details:
            console.print(f"[dim]  details: {details}[/dim]")
    console.print()
