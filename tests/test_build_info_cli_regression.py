# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build İnfo Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for build info extraction slice."""

from __future__ import annotations
import pytest

import json
from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def _create_build_project(tmp_path: Path) -> Path:
    project = tmp_path / "BuildInfoCliProject"
    project.mkdir(parents=True, exist_ok=True)
    payload = {
        "FileVersion": 3,
        "EngineAssociation": "5.4",
        "Category": "Games",
        "Description": "CLI regression project",
        "Plugins": [{"Name": "BasePlugin", "Enabled": True}],
    }
    (project / "BuildInfoCliProject.uproject").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return project


def test_build_info_cli_summary_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = _create_build_project(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["build", "info", str(project)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Project Information" in result.output
    assert "BuildInfoCliProject" in result.output
    assert "Advisory summary only" in result.output
    assert "Local Build Recommendations" in result.output


def test_build_info_cli_missing_uproject_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "NoProjectFileCli"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["build", "info", str(project)], catch_exceptions=False)

    assert result.exit_code == 1
    assert "PROJECT FILE NOT FOUND" in result.output
    assert "No .uproject file found in" in result.output


def test_build_info_cli_invalid_path_signal_is_non_zero(monkeypatch, tmp_path: Path) -> None:
    missing = tmp_path / "MissingCliProject"
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["build", "info", str(missing)], catch_exceptions=False)

    assert result.exit_code == 1
    assert "PROJECT PATH NOT FOUND" in result.output


def test_build_info_help_mentions_local_uproject_metadata() -> None:
    result = runner.invoke(cli.app, ["build", "info", "--help"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "local .uproject metadata" in result.output


@pytest.mark.skip(reason="Obsolete after UX/CLI architectural refactoring")
def test_build_info_cli_invalid_path_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    missing = tmp_path / "MissingCliProject"
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["build", "info", str(missing)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "PATH NOT FOUND" in result.output

