# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Terminal Fallback Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Regression tests for ASCII-safe CLI fallback on legacy terminals."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()
UNICODE_BOX_CHARS = ("╔", "╗", "╚", "╝", "║", "│", "─", "┌", "┐", "└", "┘", "┏", "┓", "┗", "┛", "━", "┃")


def _create_project(project_root: Path) -> Path:
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "FallbackProject.uproject").write_text(
        json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
        encoding="utf-8",
    )
    (project_root / ".gitignore").write_text("Saved/\nIntermediate/\n", encoding="utf-8")
    (project_root / ".gitattributes").write_text(
        "*.uasset filter=lfs diff=lfs merge=lfs -text\n",
        encoding="utf-8",
    )
    (project_root / "Content").mkdir(parents=True, exist_ok=True)
    (project_root / "Content" / "BP_Test.uasset").write_bytes(b"ASSET")
    (project_root / "Plugins" / "BasePlugin").mkdir(parents=True, exist_ok=True)
    (project_root / "Plugins" / "BasePlugin" / "BasePlugin.uplugin").write_text(
        json.dumps(
            {
                "FileVersion": 3,
                "VersionName": "1.0",
                "FriendlyName": "BasePlugin",
                "Description": "ASCII fallback plugin fixture",
                "Enabled": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return project_root


def _assert_ascii_fallback_output(output: str) -> None:
    assert "????????" not in output
    for char in UNICODE_BOX_CHARS:
        assert char not in output


def _run_in_ascii_mode(run_command) -> None:
    original_mode = cli.visuals.ASCII_MODE
    try:
        cli.visuals.apply_render_mode(True)
        run_command()
    finally:
        cli.visuals.apply_render_mode(original_mode)


def test_doctor_ascii_fallback_keeps_diagnostics_readable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path / "DoctorFallbackProject")
    monkeypatch.chdir(project)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result_holder = {}

    def _run() -> None:
        result_holder["result"] = runner.invoke(cli.app, ["doctor"], catch_exceptions=False)

    _run_in_ascii_mode(_run)
    result = result_holder["result"]

    assert result.exit_code == 0
    assert "DIAGNOSTIC RESULTS" in result.output
    assert "Health Score:" in result.output
    _assert_ascii_fallback_output(result.output)


def test_version_ascii_fallback_keeps_runtime_card_readable() -> None:
    result_holder = {}

    def _run() -> None:
        result_holder["result"] = runner.invoke(cli.app, ["version"], catch_exceptions=False)

    _run_in_ascii_mode(_run)
    result = result_holder["result"]

    assert result.exit_code == 0
    assert "UnrealMate" in result.output
    assert "1.1.4" in result.output
    _assert_ascii_fallback_output(result.output)


def test_root_help_ascii_fallback_keeps_onboarding_panels_readable() -> None:
    result_holder = {}

    def _run() -> None:
        result_holder["result"] = runner.invoke(cli.app, ["--help"], catch_exceptions=False)

    _run_in_ascii_mode(_run)
    result = result_holder["result"]

    assert result.exit_code == 0
    assert "UnrealMate" in result.output or "Unreal" in result.output
    assert "USAGE" in result.output
    assert "COMMANDS" in result.output
    _assert_ascii_fallback_output(result.output)


def test_help_all_ascii_fallback_keeps_opt_in_panels_readable() -> None:
    result_holder = {}

    def _run() -> None:
        result_holder["result"] = runner.invoke(cli.app, ["--help-all"], catch_exceptions=False)

    _run_in_ascii_mode(_run)
    result = result_holder["result"]

    assert result.exit_code == 0
    assert "report dashboard" in result.output
    _assert_ascii_fallback_output(result.output)


def test_config_help_ascii_fallback_keeps_curated_sections_readable() -> None:
    result_holder = {}

    def _run() -> None:
        result_holder["result"] = runner.invoke(cli.app, ["config", "--help"], catch_exceptions=False)

    _run_in_ascii_mode(_run)
    result = result_holder["result"]

    assert result.exit_code == 0
    assert "CONFIG" in result.output
    assert "Inspect & Validate" in result.output
    assert "Edit Local Config" in result.output
    _assert_ascii_fallback_output(result.output)


def test_report_help_ascii_fallback_keeps_curated_sections_readable() -> None:
    result_holder = {}

    def _run() -> None:
        result_holder["result"] = runner.invoke(cli.app, ["report", "--help"], catch_exceptions=False)

    _run_in_ascii_mode(_run)
    result = result_holder["result"]

    assert result.exit_code == 0
    assert "REPORT" in result.output
    assert "Stable Local Snapshots" in result.output
    assert "Local-only Utility" in result.output
    _assert_ascii_fallback_output(result.output)


def test_plugin_list_ascii_fallback_keeps_table_readable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path / "PluginFallbackProject")
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result_holder = {}

    def _run() -> None:
        result_holder["result"] = runner.invoke(
            cli.app,
            ["plugin", "list", str(project)],
            catch_exceptions=False,
        )

    _run_in_ascii_mode(_run)
    result = result_holder["result"]

    assert result.exit_code == 0
    assert "Installed Plugins" in result.output
    assert "BasePlugin" in result.output
    _assert_ascii_fallback_output(result.output)


def test_report_json_ascii_fallback_keeps_warning_and_panel_text_readable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path / "ReportJsonFallbackProject")
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result_holder = {}

    def _run() -> None:
        result_holder["result"] = runner.invoke(
            cli.app,
            ["report", "json", str(project)],
            catch_exceptions=False,
        )

    _run_in_ascii_mode(_run)
    result = result_holder["result"]

    assert result.exit_code == 0
    assert "Local JSON Snapshot" in result.output
    assert "\"project\": \"FallbackProject\"" in result.output
    _assert_ascii_fallback_output(result.output)
