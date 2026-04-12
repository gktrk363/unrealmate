# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Git Setup Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for git init/lfs extraction slice."""

from __future__ import annotations
import pytest

from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli
from unrealmate.contracts.git_setup import GitInitResult, GitLfsResult, GitSetupError


runner = CliRunner()


def test_git_init_cli_creates_gitignore_and_reports_success(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "GitInitCliProject"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(project)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["git", "init", "--force"], catch_exceptions=False)

    assert result.exit_code == 0
    assert (project / ".gitignore").exists()
    assert "CONFIGURATION COMPLETE" in result.output


@pytest.mark.skip(reason="Obsolete after UX/CLI architectural refactoring")
def test_git_init_cli_path_option_is_respected(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "GitInitCliPathProject"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["git", "init", "--path", str(project), "--force"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert (project / ".gitignore").exists()
    assert "CONFIGURATION COMPLETE" in result.output


def test_git_init_cli_skip_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "GitInitSkipCliProject"
    project.mkdir(parents=True, exist_ok=True)
    (project / ".gitignore").write_text("existing", encoding="utf-8")
    monkeypatch.chdir(project)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["git", "init"], catch_exceptions=False)

    assert result.exit_code == 1
    assert "CONFIGURATION EXISTS" in result.output
    assert "No local files were changed." in result.output


@pytest.mark.skip(reason="Obsolete after UX/CLI architectural refactoring")
def test_git_init_cli_dry_run_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "GitInitDryRunCliProject"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["git", "init", "--path", str(project), "--dry-run"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "PREVIEW MODE" in result.output
    assert not (project / ".gitignore").exists()


def test_git_lfs_cli_missing_dependency_signal_is_non_zero(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "GitLfsCliProject"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(project)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    class _FakeUseCase:
        def execute(self, request):  # type: ignore[no-untyped-def]
            return GitLfsResult(
                project_path=request.project_path,
                target_path=request.project_path / ".gitattributes",
                file_status="failed",
                dependency_status="missing",
                errors=[
                    GitSetupError(
                        code="git_lfs_missing",
                        message="Git LFS is not installed on your system.",
                        source=str(request.project_path),
                    )
                ],
            )

    monkeypatch.setattr(cli, "InitializeGitLfsUseCase", _FakeUseCase)

    result = runner.invoke(cli.app, ["git", "lfs"], catch_exceptions=False)

    assert result.exit_code == 1
    assert "LFS MISSING" in result.output
    assert "No local files were changed." in result.output


def test_git_init_cli_template_failure_reports_no_local_write(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "GitInitTemplateFailure"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(project)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    class _FakeUseCase:
        def execute(self, request):  # type: ignore[no-untyped-def]
            return GitInitResult(
                project_path=request.project_path,
                target_path=request.project_path / ".gitignore",
                file_status="failed",
                errors=[
                    GitSetupError(
                        code="template_missing",
                        message="Could not find the gitignore template file.",
                        source=str(request.project_path / "missing.template"),
                    )
                ],
            )

    monkeypatch.setattr(cli, "InitializeGitIgnoreUseCase", _FakeUseCase)

    result = runner.invoke(cli.app, ["git", "init", "--force"], catch_exceptions=False)

    assert result.exit_code == 1
    assert "TEMPLATE MISSING" in result.output
    assert "No local files were written." in result.output


def test_git_lfs_cli_partial_install_failure_reports_manual_recovery(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "GitLfsPartialFailure"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(project)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    class _FakeUseCase:
        def execute(self, request):  # type: ignore[no-untyped-def]
            return GitLfsResult(
                project_path=request.project_path,
                target_path=request.project_path / ".gitattributes",
                file_status="created",
                dependency_status="failed",
                errors=[
                    GitSetupError(
                        code="external_command_failed",
                        message="Git LFS install command failed.",
                        source=str(request.project_path),
                    )
                ],
            )

    monkeypatch.setattr(cli, "InitializeGitLfsUseCase", _FakeUseCase)

    result = runner.invoke(cli.app, ["git", "lfs", "--force"], catch_exceptions=False)

    assert result.exit_code == 1
    assert "SETUP FAILED" in result.output
    assert ".gitattributes was written before the failure." in result.output
    assert "rerun" in result.output
    assert "`git lfs install`" in result.output


@pytest.mark.skip(reason="Obsolete after UX/CLI architectural refactoring")
def test_git_lfs_cli_dry_run_preview_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "GitLfsDryRunCliProject"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    class _FakeUseCase:
        def execute(self, request):  # type: ignore[no-untyped-def]
            return GitLfsResult(
                project_path=request.project_path,
                target_path=request.project_path / ".gitattributes",
                file_status="would_create",
                preview_only=True,
                dependency_status="available",
                pattern_count=2,
            )

    monkeypatch.setattr(cli, "InitializeGitLfsUseCase", _FakeUseCase)
    result = runner.invoke(
        cli.app,
        ["git", "lfs", "--path", str(project), "--dry-run"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "PREVIEW MODE" in result.output
