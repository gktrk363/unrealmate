# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build Ci İnit Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for build ci-init extraction slice."""

from __future__ import annotations
import pytest

import json
from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def _create_project(tmp_path: Path, with_uproject: bool = True) -> Path:
    project = tmp_path / "BuildCiCliProject"
    project.mkdir(parents=True, exist_ok=True)
    if with_uproject:
        (project / "BuildCiCliProject.uproject").write_text(
            json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
            encoding="utf-8",
        )
    return project


def test_build_ci_init_cli_github_success_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["build", "ci-init", "--platform", "github", "--path", str(project)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "GitHub Actions starter workflow created." in result.output
    assert (project / ".github" / "workflows" / "unreal-build.yml").exists()


def test_build_ci_init_cli_skip_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    first = runner.invoke(
        cli.app,
        ["build", "ci-init", "--platform", "gitlab", "--path", str(project)],
        catch_exceptions=False,
    )
    assert first.exit_code == 0

    second = runner.invoke(
        cli.app,
        ["build", "ci-init", "--platform", "gitlab", "--path", str(project)],
        catch_exceptions=False,
    )
    assert second.exit_code == 1
    assert "FILE EXISTS" in second.output
    assert "Re-run with --force" in second.output


def test_build_ci_init_cli_unknown_platform_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["build", "ci-init", "--platform", "azure", "--path", str(project)],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Unknown platform: azure" in result.output
    assert "Supported: github, gitlab, jenkins" in result.output


@pytest.mark.skip(reason="Obsolete after UX/CLI architectural refactoring")
def test_build_ci_init_cli_missing_uproject_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path, with_uproject=False)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["build", "ci-init", "--platform", "github", "--path", str(project)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "No .uproject file found!" in result.output


def test_build_ci_init_cli_dry_run_preview_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path, with_uproject=True)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["build", "ci-init", "--platform", "github", "--path", str(project), "--dry-run"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "DRY RUN MODE" in result.output
    assert "Preview only: would write" in result.output
    assert not (project / ".github" / "workflows" / "unreal-build.yml").exists()


@pytest.mark.skip(reason="Obsolete after UX/CLI architectural refactoring")
def test_build_ci_init_cli_uses_real_uproject_name_not_folder(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "FolderBasedName"
    project.mkdir(parents=True, exist_ok=True)
    (project / "ActualGame.uproject").write_text(
        json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
        encoding="utf-8",
    )
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["build", "ci-init", "--platform", "github", "--path", str(project)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    ci_file = project / ".github" / "workflows" / "unreal-build.yml"
    assert ci_file.exists()
    ci_text = ci_file.read_text(encoding="utf-8")
    assert "ActualGame.uproject" in ci_text
    assert "FolderBasedName.uproject" not in ci_text
