# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Git Setup Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Presenter tests for git init/lfs structured render flow."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from rich.console import Console

from unrealmate.adapters.presenters.cli_git_setup_presenter import (
    render_git_init_result,
    render_git_lfs_result,
)
from unrealmate.contracts.git_setup import (
    GitInitResult,
    GitLfsResult,
    GitSetupError,
    GitSetupWarning,
)


class _FakeVisuals:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def print_success_banner(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        self.calls.append(("success", args, kwargs))

    def print_warning_banner(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        self.calls.append(("warning", args, kwargs))

    def print_error_banner(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        self.calls.append(("error", args, kwargs))

    def print_tip(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        self.calls.append(("tip", args, kwargs))


def _console_buffer() -> tuple[Console, StringIO]:
    stream = StringIO()
    return Console(file=stream, force_terminal=False, color_system=None), stream


def test_git_init_presenter_renders_success_banner() -> None:
    visuals = _FakeVisuals()
    project = Path("C:/tmp/project")
    result = GitInitResult(
        project_path=project,
        target_path=project / ".gitignore",
        file_status="created",
        bytes_written=128,
    )

    render_git_init_result(result=result, visuals_module=visuals, format_size=lambda size: f"{size} B")

    assert visuals.calls[0][0] == "success"
    assert visuals.calls[0][1][0] == "CONFIGURATION COMPLETE"
    assert visuals.calls[0][1][2]["File Created"] == ".gitignore"


def test_git_init_presenter_renders_existing_file_warning() -> None:
    visuals = _FakeVisuals()
    project = Path("C:/tmp/project")
    result = GitInitResult(
        project_path=project,
        target_path=project / ".gitignore",
        file_status="skipped",
    )

    render_git_init_result(result=result, visuals_module=visuals, format_size=lambda size: f"{size} B")

    assert visuals.calls[0][0] == "warning"
    assert visuals.calls[0][1][0] == "CONFIGURATION EXISTS"


def test_git_lfs_presenter_renders_missing_dependency_error() -> None:
    visuals = _FakeVisuals()
    project = Path("C:/tmp/project")
    result = GitLfsResult(
        project_path=project,
        target_path=project / ".gitattributes",
        file_status="failed",
        dependency_status="missing",
        errors=[
            GitSetupError(
                code="git_lfs_missing",
                message="Git LFS is not installed on your system.",
                source=str(project),
            )
        ],
    )

    render_git_lfs_result(result=result, visuals_module=visuals)

    assert visuals.calls[0][0] == "error"
    assert visuals.calls[0][1][0] == "LFS MISSING"


def test_git_init_presenter_preview_signal_is_stable() -> None:
    visuals = _FakeVisuals()
    project = Path("C:/tmp/project")
    console, stream = _console_buffer()
    result = GitInitResult(
        project_path=project,
        target_path=project / ".gitignore",
        file_status="would_create",
        preview_only=True,
        bytes_written=64,
        warnings=[
            GitSetupWarning(
                code="preview_only",
                message="Preview mode enabled; no files were written.",
                source=str(project / ".gitignore"),
                details="action=preview; preexisting=False",
            )
        ],
    )

    render_git_init_result(result=result, visuals_module=visuals, format_size=lambda size: f"{size} B", console=console)

    assert visuals.calls[0][0] == "warning"
    assert visuals.calls[0][1][0] == "PREVIEW MODE"
    assert "Warnings:" in stream.getvalue()


def test_git_lfs_presenter_renders_additional_errors_and_warnings() -> None:
    visuals = _FakeVisuals()
    project = Path("C:/tmp/project")
    console, stream = _console_buffer()
    result = GitLfsResult(
        project_path=project,
        target_path=project / ".gitattributes",
        file_status="failed",
        dependency_status="failed",
        errors=[
            GitSetupError(
                code="external_command_failed",
                message="Git LFS version command failed.",
                source=str(project),
                details="status=failed",
            ),
            GitSetupError(
                code="external_command_failed",
                message="Git LFS install command failed.",
                source=str(project),
                details="status=failed",
            ),
        ],
        warnings=[
            GitSetupWarning(
                code="preview_only",
                message="Preview mode enabled.",
                source=str(project),
                details="action=preview",
            )
        ],
    )

    render_git_lfs_result(result=result, visuals_module=visuals, console=console)

    output = stream.getvalue()
    assert visuals.calls[0][0] == "error"
    assert "Additional errors:" in output
    assert "Warnings:" in output
