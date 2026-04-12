# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Cli Smoke Non Destructive
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Smoke coverage for non-destructive stable UnrealMate commands."""

from __future__ import annotations
import os
import pytest

from pathlib import Path

import unrealmate.cli as cli


def test_version_smoke(run_cli, assert_ok) -> None:
    result = run_cli(["version"])
    assert_ok(result)
    assert "UNREALMATE" in result.output.upper()


def test_doctor_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["doctor"], cwd=fixture_project)
    assert_ok(result)
    assert "DIAGNOSTIC RESULTS" in result.output
    assert "Health Score" in result.output


def test_config_show_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["config", "show"], cwd=fixture_project)
    assert_ok(result)
    assert "UnrealMate Configuration" in result.output
    assert "cache_enabled" in result.output


def test_config_get_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["config", "get", "performance.cache_enabled"], cwd=fixture_project)
    assert_ok(result)
    assert "performance.cache_enabled" in result.output


def test_config_validate_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["config", "validate"], cwd=fixture_project)
    assert_ok(result)
    assert "Validation passed with no schema issues." in result.output


def test_config_edit_smoke(
    fixture_project: Path,
    run_cli,
    assert_ok,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened_paths: list[str] = []
    monkeypatch.setattr(cli.platform, "system", lambda: "Windows")
    monkeypatch.setattr(os, "startfile", lambda path: opened_paths.append(path), raising=False)

    result = run_cli(["config", "edit"], cwd=fixture_project)

    assert_ok(result)
    assert opened_paths == [str((fixture_project / ".unrealmate.toml").resolve())]
    assert "Opened in default editor:" in result.output


def test_asset_scan_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["asset", "scan", str(fixture_project / "Content")], cwd=fixture_project)
    assert_ok(result)
    assert "Scan Summary" in result.output


def test_asset_duplicates_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["asset", "duplicates", str(fixture_project / "Content")], cwd=fixture_project)
    assert_ok(result)
    assert "duplicate groups" in result.output.lower()


@pytest.mark.skip(reason="Obsolete after UX/CLI architectural refactoring")
def test_performance_profile_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["performance", "profile", str(fixture_project)], cwd=fixture_project)
    assert_ok(result)
    assert "profiling report" in result.output.lower()


def test_performance_shaders_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["performance", "shaders", str(fixture_project)], cwd=fixture_project)
    assert_ok(result)
    assert "Shader Analysis Report" in result.output


def test_performance_memory_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["performance", "memory", str(fixture_project)], cwd=fixture_project)
    assert_ok(result)
    assert "Memory Audit Report" in result.output


def test_plugin_list_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["plugin", "list", str(fixture_project)], cwd=fixture_project)
    assert_ok(result)
    assert "Installed Plugins" in result.output
    assert "BasePlugin" in result.output


def test_build_info_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["build", "info", str(fixture_project)], cwd=fixture_project)
    assert_ok(result)
    assert "Project Information" in result.output
    assert "SmokeProject" in result.output
