# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build Ci İnit Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Presenter tests for build ci-init rendering."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from rich.console import Console

from unrealmate.adapters.presenters.cli_build_ci_presenter import (
    render_build_ci_init_result,
)
from unrealmate.contracts.build_ci_init import (
    BuildCiInitError,
    BuildCiInitResult,
    BuildCiInitWarning,
    GeneratedFileEntry,
)


class _FakeVisuals:
    def __init__(self) -> None:
        self.errors: list[tuple[str, str]] = []

    def print_error_banner(self, title: str, message: str, *args) -> None:  # type: ignore[no-untyped-def]
        self.errors.append((title, message))


def _build_console_buffer() -> tuple[Console, StringIO]:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, color_system=None, width=120)
    return console, stream


def test_build_ci_presenter_success_signal_is_stable(tmp_path: Path) -> None:
    target = (tmp_path / ".github" / "workflows" / "unreal-build.yml").resolve()
    result = BuildCiInitResult(
        project_path=tmp_path.resolve(),
        platform="github",
        generated_files=[GeneratedFileEntry(path=target, status="created", bytes_written=100, provider="github")],
    )
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()

    should_footer = render_build_ci_init_result(result=result, console=console, visuals_module=visuals)
    output = stream.getvalue()

    assert should_footer is True
    assert "GitHub Actions workflow created!" in output
    assert "Project: unknown" in output
    assert "Location:" in output
    assert "Next Steps:" in output


def test_build_ci_presenter_skip_signal_is_stable(tmp_path: Path) -> None:
    target = (tmp_path / ".gitlab-ci.yml").resolve()
    result = BuildCiInitResult(
        project_path=tmp_path.resolve(),
        platform="gitlab",
        generated_files=[GeneratedFileEntry(path=target, status="skipped", provider="gitlab")],
        warnings=[
            BuildCiInitWarning(
                code="build_ci_already_exists",
                message="CI configuration already exists and is up-to-date.",
                source=str(target),
            )
        ],
    )
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()

    should_footer = render_build_ci_init_result(result=result, console=console, visuals_module=visuals)
    output = stream.getvalue()

    assert should_footer is True
    assert "already exists (skipped)" in output
    assert "Project: unknown" in output
    assert "Warnings:" in output


def test_build_ci_presenter_unsupported_platform_signal_is_stable(tmp_path: Path) -> None:
    result = BuildCiInitResult(
        project_path=tmp_path.resolve(),
        platform="azure",
        errors=[
            BuildCiInitError(
                code="build_ci_provider_unsupported",
                message="Unknown platform: azure",
                source="azure",
            )
        ],
    )
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()

    should_footer = render_build_ci_init_result(result=result, console=console, visuals_module=visuals)
    output = stream.getvalue()

    assert should_footer is False
    assert "Unknown platform: azure" in output
    assert "Supported: github, gitlab, jenkins" in output


def test_build_ci_presenter_missing_project_signal_is_stable(tmp_path: Path) -> None:
    result = BuildCiInitResult(
        project_path=tmp_path.resolve(),
        platform="github",
        errors=[
            BuildCiInitError(
                code="build_ci_project_missing",
                message="No .uproject file found!",
                source=str(tmp_path.resolve()),
            )
        ],
    )
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()

    should_footer = render_build_ci_init_result(result=result, console=console, visuals_module=visuals)
    output = stream.getvalue()

    assert should_footer is False
    assert "No .uproject file found!" in output


def test_build_ci_presenter_preview_signal_is_stable(tmp_path: Path) -> None:
    target = (tmp_path / ".github" / "workflows" / "unreal-build.yml").resolve()
    result = BuildCiInitResult(
        project_path=tmp_path.resolve(),
        platform="github",
        selected_project_name="PreviewGame",
        generated_files=[
            GeneratedFileEntry(
                path=target,
                status="would_create",
                bytes_written=100,
                provider="github",
            )
        ],
        preview_only=True,
    )
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()

    should_footer = render_build_ci_init_result(result=result, console=console, visuals_module=visuals)
    output = stream.getvalue()

    assert should_footer is True
    assert "Preview mode" in output
    assert "would be created" in output
    assert "Project: PreviewGame" in output
