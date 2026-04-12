# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build Docker Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for build docker trust hardening."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def _create_project(tmp_path: Path) -> Path:
    project = tmp_path / "BuildDockerCliProject"
    project.mkdir(parents=True, exist_ok=True)
    return project


def test_build_docker_cli_dry_run_preview_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["build", "docker", "--path", str(project), "--dry-run"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "DRY RUN MODE" in result.output
    assert "Preview only: would write" in result.output
    assert "placeholder entry point './ProjectName'" in result.output
    assert not (project / "Dockerfile").exists()


def test_build_docker_cli_refuses_to_overwrite_without_force(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    dockerfile = project / "Dockerfile"
    dockerfile.write_text("FROM scratch\n", encoding="utf-8")
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["build", "docker", "--path", str(project)],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "FILE EXISTS" in result.output
    assert "Re-run with --force" in result.output
    assert dockerfile.read_text(encoding="utf-8") == "FROM scratch\n"


def test_build_docker_cli_success_uses_starter_template_language(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["build", "docker", "--path", str(project)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Starter Dockerfile created." in result.output
    assert "Manual edits are still required" in result.output
