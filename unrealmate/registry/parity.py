# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Parity
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Parity checks between CLI command inventory and command registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import typer

from unrealmate.registry.models import CommandRegistry, RegistryValidationError


@dataclass(frozen=True)
class ParityReport:
    """Result of comparing registry entries with CLI-discovered commands."""

    registry_count: int
    cli_count: int
    matched_commands: tuple[str, ...]
    missing_in_registry: tuple[str, ...]
    orphaned_in_registry: tuple[str, ...]

    @property
    def is_full_match(self) -> bool:
        return not self.missing_in_registry and not self.orphaned_in_registry


def _sorted_tuple(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(values))


def collect_cli_command_inventory(cli_app: typer.Typer | None = None) -> set[str]:
    """Discover canonical command strings from the current Typer app."""
    if cli_app is None:
        from unrealmate.cli import app as default_cli_app  # local import to avoid import cycles

        cli_app = default_cli_app

    click_root = typer.main.get_command(cli_app)
    inventory: set[str] = set()
    for command_name, command in click_root.commands.items():
        if hasattr(command, "commands"):
            for subcommand_name in command.commands.keys():
                inventory.add(f"unrealmate {command_name} {subcommand_name}")
        else:
            inventory.add(f"unrealmate {command_name}")
    return inventory


def check_registry_cli_parity(
    registry: CommandRegistry,
    cli_app: typer.Typer | None = None,
    strict: bool = False,
) -> ParityReport:
    """Compare registry full commands against CLI inventory."""
    registry_commands = {entry.full_command for entry in registry.commands}
    cli_commands = collect_cli_command_inventory(cli_app=cli_app)

    missing_in_registry = cli_commands - registry_commands
    orphaned_in_registry = registry_commands - cli_commands
    matched = cli_commands & registry_commands

    report = ParityReport(
        registry_count=len(registry_commands),
        cli_count=len(cli_commands),
        matched_commands=_sorted_tuple(matched),
        missing_in_registry=_sorted_tuple(missing_in_registry),
        orphaned_in_registry=_sorted_tuple(orphaned_in_registry),
    )

    if strict and not report.is_full_match:
        errors: list[str] = []
        if report.missing_in_registry:
            errors.append(
                "Missing registry entries for CLI commands: "
                + ", ".join(report.missing_in_registry)
            )
        if report.orphaned_in_registry:
            errors.append(
                "Registry contains commands not present in CLI: "
                + ", ".join(report.orphaned_in_registry)
            )
        raise RegistryValidationError(errors)

    return report
