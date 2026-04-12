# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Help Surface Binding
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Tests for registry-bound CLI help surface behavior."""

from __future__ import annotations

import re
from collections import defaultdict

import typer
from typer.testing import CliRunner

import unrealmate.cli as cli
from unrealmate.registry import load_command_registry


runner = CliRunner()


def _expected_default_help_surface() -> tuple[set[str], dict[str, set[str]]]:
    registry = load_command_registry()
    visible_root_commands: set[str] = set()
    visible_group_subcommands: dict[str, set[str]] = defaultdict(set)

    for entry in registry.commands:
        if not entry.default_help_included:
            continue
        if entry.command_group == "root":
            visible_root_commands.add(entry.subcommand)
            continue
        visible_root_commands.add(entry.command_group)
        visible_group_subcommands[entry.command_group].add(entry.subcommand)

    return visible_root_commands, dict(visible_group_subcommands)


def _visible_group_subcommand_order(group_name: str) -> list[str]:
    click_root = typer.main.get_command(cli.app)
    group_command = click_root.commands[group_name]
    return [
        sub_name
        for sub_name, subcommand in group_command.commands.items()
        if not getattr(subcommand, "hidden", False)
    ]


def test_click_help_visibility_matches_registry_default_surface() -> None:
    expected_root, expected_subcommands = _expected_default_help_surface()
    click_root = typer.main.get_command(cli.app)

    actual_root = {
        command_name
        for command_name, command in click_root.commands.items()
        if not getattr(command, "hidden", False)
    }
    assert actual_root == expected_root

    for group_name, expected_group_subcommands in expected_subcommands.items():
        group_command = click_root.commands[group_name]
        actual_subcommands = {
            sub_name
            for sub_name, subcommand in group_command.commands.items()
            if not getattr(subcommand, "hidden", False)
        }
        assert actual_subcommands == expected_group_subcommands


def test_default_premium_help_tracks_registry_truth_and_caution_labels() -> None:
    result = runner.invoke(cli.app, ["--help"])
    assert result.exit_code == 0

    output = result.output
    assert "marketplace search" not in output
    assert "blueprint analyze" not in output
    assert "ai nlp" not in output
    assert "report dashboard" not in output
    assert "security-scan" not in output
    assert "UnrealMate" in output or "Unreal" in output
    assert "USAGE" in output
    assert "COMMANDS" in output
    assert "Inspect & Validate" in output
    assert "Change Local State" in output
    assert "Analyze & Export" in output
    assert "doctor" in output
    assert "config show" in output
    assert "asset scan" in output
    assert "build info" in output
    assert "plugin list" in output
    assert "analytics" in output
    assert "local-only" in output
    assert "build ci-init" in output
    assert "partially implemented" in output
    assert "git clean" in output
    assert "writes local state" in output
    assert "EXPLORE" in output
    assert "Use unrealmate --help-all" in output


def test_help_all_exposes_opt_in_surfaces_with_truthful_labels() -> None:
    result = runner.invoke(cli.app, ["--help-all"])
    assert result.exit_code == 0

    normalized_output = re.sub(r"\s+", " ", result.output)
    assert "report dashboard" in result.output
    assert "marketplace search" in result.output
    assert "health" in result.output
    assert "template create" in result.output
    assert "experimental" in normalized_output
    assert "mock" in normalized_output
    assert "placeholder" in normalized_output
    assert "stable/default product surface" in normalized_output


def test_group_help_exposes_only_registry_default_subcommands() -> None:
    report_help = runner.invoke(cli.app, ["report", "--help"])
    assert report_help.exit_code == 0
    normalized_report_help = re.sub(r"\s+", " ", report_help.output)
    assert "REPORT" in report_help.output
    assert "html" in report_help.output
    assert "json" in report_help.output
    assert "notify" in report_help.output
    assert "local-only" in report_help.output
    assert "writes local state" in report_help.output
    assert "Start with json or html for stable local snapshots" in normalized_report_help
    assert "unrealmate --help-all" in normalized_report_help
    assert "report dashboard --help" in normalized_report_help
    assert "Stable Local Snapshots" in report_help.output
    assert "Local-only Utility" in report_help.output

    git_help = runner.invoke(cli.app, ["git", "--help"])
    assert git_help.exit_code == 0
    normalized_git_help = re.sub(r"\s+", " ", git_help.output)
    assert "GIT" in git_help.output
    assert "init" in git_help.output
    assert "lfs" in git_help.output
    assert "clean" in git_help.output
    assert "status" not in git_help.output
    assert "Start after inspection steps" in normalized_git_help
    assert "all subcommands write local state" in normalized_git_help
    assert "Project Setup" in git_help.output
    assert "Cleanup" in git_help.output

    performance_help = runner.invoke(cli.app, ["performance", "--help"])
    assert performance_help.exit_code == 0
    normalized_performance_help = re.sub(r"\s+", " ", performance_help.output)
    assert "memory" in performance_help.output
    assert "profile" in performance_help.output
    assert "shaders" in performance_help.output
    assert "drawcalls" not in performance_help.output
    assert "network" not in performance_help.output
    assert "authoritative runtime truth" in normalized_performance_help
    assert "Advisory Analysis" in performance_help.output

    config_help = runner.invoke(cli.app, ["config", "--help"])
    assert config_help.exit_code == 0
    normalized_config_help = re.sub(r"\s+", " ", config_help.output)
    assert "Start with show or validate" in normalized_config_help
    assert "Inspect & Validate" in config_help.output
    assert "Edit Local Config" in config_help.output

    asset_help = runner.invoke(cli.app, ["asset", "--help"])
    assert asset_help.exit_code == 0
    assert "Start with scan or duplicates" in re.sub(r"\s+", " ", asset_help.output)
    assert "Inspect Inventory" in asset_help.output
    assert "Writes Local State" in asset_help.output

    build_help = runner.invoke(cli.app, ["build", "--help"])
    assert build_help.exit_code == 0
    assert "Start with info" in re.sub(r"\s+", " ", build_help.output)
    assert "Inspect Current Project" in build_help.output
    assert "Starter Generators" in build_help.output

    plugin_help = runner.invoke(cli.app, ["plugin", "--help"])
    assert plugin_help.exit_code == 0
    assert "Start with list" in re.sub(r"\s+", " ", plugin_help.output)
    assert "Inspect" in plugin_help.output
    assert "Mutate Plugin State" in plugin_help.output


def test_group_help_orders_safe_first_subcommands() -> None:
    config_order = _visible_group_subcommand_order("config")
    assert config_order.index("show") < config_order.index("init")

    asset_order = _visible_group_subcommand_order("asset")
    assert asset_order.index("scan") < asset_order.index("organize")

    git_order = _visible_group_subcommand_order("git")
    assert git_order.index("init") < git_order.index("clean")

    performance_order = _visible_group_subcommand_order("performance")
    assert performance_order.index("profile") < performance_order.index("shaders")

    build_order = _visible_group_subcommand_order("build")
    assert build_order.index("info") < build_order.index("ci-init")

    plugin_order = _visible_group_subcommand_order("plugin")
    assert plugin_order.index("list") < plugin_order.index("install")

    report_order = _visible_group_subcommand_order("report")
    assert report_order.index("json") < report_order.index("html")


def test_direct_help_for_hidden_or_truth_sensitive_commands_remains_truthful() -> None:
    marketplace_help = runner.invoke(cli.app, ["marketplace", "install", "--help"])
    assert marketplace_help.exit_code == 0
    assert "mock" in marketplace_help.output
    assert "simulated" in marketplace_help.output
    assert "product-real" in marketplace_help.output

    dashboard_help = runner.invoke(cli.app, ["report", "dashboard", "--help"])
    assert dashboard_help.exit_code == 0
    normalized_dashboard_help = re.sub(r"\s+", " ", dashboard_help.output)
    assert "experimental" in normalized_dashboard_help
    assert "secondary view over project report data" in normalized_dashboard_help
    assert "Use report json" in normalized_dashboard_help
    assert "stable local report artifacts" in normalized_dashboard_help

    notify_help = runner.invoke(cli.app, ["report", "notify", "--help"])
    assert notify_help.exit_code == 0
    assert "local-only" in notify_help.output
    assert "No remote service or remote delivery is performed" in notify_help.output


def test_default_help_has_no_stale_alias_or_removed_command_tokens() -> None:
    output = runner.invoke(cli.app, ["--help"]).output
    stale_patterns = [
        r"\bbp\b",
        r"\bperf\b",
        r"\bcfg\b",
        r"\bgit status\b",
        r"\basset validate\b",
        r"\bbuild generate\b",
        r"\bbuild validate\b",
    ]
    for pattern in stale_patterns:
        assert re.search(pattern, output) is None
