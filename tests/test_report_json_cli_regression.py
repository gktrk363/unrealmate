# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Json Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for report json extraction slice."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def _create_project(project_path: Path, with_uproject: bool = True) -> Path:
    project_path.mkdir(parents=True, exist_ok=True)
    if with_uproject:
        (project_path / "CliReportGame.uproject").write_text(
            json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
            encoding="utf-8",
        )
    (project_path / "Source").mkdir(parents=True, exist_ok=True)
    (project_path / "Source" / "Game.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
    (project_path / "Source" / "Game.h").write_text("#pragma once\n", encoding="utf-8")
    (project_path / "Content").mkdir(parents=True, exist_ok=True)
    (project_path / "Content" / "BP_Test.uasset").write_bytes(b"ASSET")
    (project_path / "Content" / "Map_Test.umap").write_bytes(b"MAP")
    return project_path


def test_report_json_cli_success_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path / "CliReportProject")
    output_path = tmp_path / "out" / "report.json"
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["report", "json", str(project), "--output", str(output_path)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Local JSON Snapshot" in result.output
    assert "Snapshot Data" in result.output
    assert "Local JSON snapshot saved." in result.output
    assert "local filesystem snapshot" in result.output
    assert "Location:" in result.output
    assert output_path.exists()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["project"] == "CliReportGame"
    assert payload["stats"]["uproject_files"] == 1


def test_report_json_cli_invalid_path_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    missing = tmp_path / "MissingReportProject"
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["report", "json", str(missing)],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "PATH NOT FOUND" in result.output


def test_report_json_cli_missing_uproject_warning_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path / "NoUProjectCli", with_uproject=False)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["report", "json", str(project)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "No .uproject file found; using folder name as the local project identifier." in result.output


def test_report_json_cli_refuses_to_overwrite_without_force(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path / "CliReportOverwrite")
    output_path = tmp_path / "out" / "report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("{\"existing\": true}\n", encoding="utf-8")
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["report", "json", str(project), "--output", str(output_path)],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "FILE EXISTS" in result.output
    assert "Re-run with --force" in result.output
    assert output_path.read_text(encoding="utf-8") == "{\"existing\": true}\n"
