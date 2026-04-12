# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Git Clean Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for git clean trust hardening."""

from __future__ import annotations

import shutil
from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def _create_cleanup_project(tmp_path: Path) -> Path:
    project = tmp_path / "GitCleanCliProject"
    (project / "Binaries" / "Win64").mkdir(parents=True, exist_ok=True)
    (project / "Intermediate" / "Build").mkdir(parents=True, exist_ok=True)
    (project / "Binaries" / "Win64" / "Game.bin").write_bytes(b"BIN")
    (project / "Intermediate" / "Build" / "temp.obj").write_bytes(b"OBJ")
    return project


def test_git_clean_cli_dry_run_warns_about_irreversible_deletion(monkeypatch, tmp_path: Path) -> None:
    project = _create_cleanup_project(tmp_path)
    monkeypatch.chdir(project)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["git", "clean", "--dry-run", "--yes"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "DRY RUN MODE" in result.output
    assert "Deleted folders are not recoverable through UnrealMate" in result.output
    assert (project / "Binaries").exists()


def test_git_clean_cli_partial_failure_exits_non_zero(monkeypatch, tmp_path: Path) -> None:
    project = _create_cleanup_project(tmp_path)
    monkeypatch.chdir(project)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)
    real_rmtree = shutil.rmtree

    def _patched_rmtree(path: Path | str):
        if Path(path).name == "Intermediate":
            raise PermissionError("locked")
        return real_rmtree(path)

    monkeypatch.setattr(cli.shutil, "rmtree", _patched_rmtree)

    result = runner.invoke(
        cli.app,
        ["git", "clean", "--yes"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "CLEANUP INCOMPLETE" in result.output
    assert "Some cleanup targets could not be removed." in result.output
    assert not (project / "Binaries").exists()
    assert (project / "Intermediate").exists()
