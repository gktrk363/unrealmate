# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Runtime Truthfulness Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for advisory/runtime truth wording on stable commands."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def test_doctor_cli_mentions_advisory_scope(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "DoctorProject"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(project)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Advisory local readiness checks only" in result.output


def test_performance_memory_cli_mentions_estimate_scope(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "MemoryProject"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["performance", "memory", str(project)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Advisory estimate only" in result.output
    assert "No local assets found to estimate." in result.output


def test_performance_shaders_cli_mentions_heuristic_scope(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "ShaderProject"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["performance", "shaders", str(project)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Heuristic estimate only" in result.output
    assert "No local shader source files found." in result.output
