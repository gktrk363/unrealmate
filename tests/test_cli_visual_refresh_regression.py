# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Cli Visual Refresh Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Regression coverage for the refreshed top-level CLI visual shell."""

from __future__ import annotations

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def test_version_surface_exposes_runtime_context() -> None:
    result = runner.invoke(cli.app, ["version"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "1.1.4" in result.output
    assert "UnrealMate" in result.output
    assert "github.com/gktrk363/unrealmate" in result.output or "Github" in result.output


def test_root_help_surface_is_panel_led_and_truthful() -> None:
    result = runner.invoke(cli.app, ["--help"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "UnrealMate" in result.output or "Unreal" in result.output
    assert "USAGE" in result.output
    assert "COMMANDS" in result.output
    assert "Inspect & Validate" in result.output
    assert "Change Local State" in result.output
    assert "Analyze & Export" in result.output
    assert "unrealmate --help-all" in result.output
    assert "report dashboard" not in result.output
    assert "marketplace search" not in result.output
    assert "Ultimate Developer Toolkit" not in result.output
    assert "All-in-one CLI toolkit" not in result.output


def test_help_all_surfaces_opt_in_commands_without_reframing_default_surface() -> None:
    result = runner.invoke(cli.app, ["--help-all"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "UnrealMate" in result.output or "Unreal" in result.output
    assert "report dashboard" in result.output
    assert "marketplace search" in result.output
    assert "health" in result.output
    assert "template create" in result.output
