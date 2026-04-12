# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build İnfo Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Presenter tests for build info rendering."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from rich.console import Console

from unrealmate.adapters.presenters.cli_build_info_presenter import render_build_info_result
from unrealmate.contracts.build_info import (
    BuildEnvironmentInfo,
    BuildInfoError,
    BuildInfoResult,
    BuildInfoWarning,
    BuildMetadata,
)
from unrealmate.core import visuals


class _FakeVisuals:
    def __init__(self) -> None:
        self.errors: list[tuple[str, str]] = []
        self.ROUNDED = visuals.ROUNDED

    def print_error_banner(self, title: str, message: str, *args) -> None:  # type: ignore[no-untyped-def]
        self.errors.append((title, message))

    def create_section_title(self, title: str, subtitle: str = ""):  # type: ignore[no-untyped-def]
        return visuals.create_section_title(title, subtitle)

    def create_key_value_panel(self, title: str, rows, accent: str = "cyan"):  # type: ignore[no-untyped-def]
        return visuals.create_key_value_panel(title, rows, accent)

    def create_message_panel(self, kind: str, title: str, body: str = "", suggestion: str = "", stats=None):  # type: ignore[no-untyped-def]
        return visuals.create_message_panel(kind, title, body, suggestion, stats)


def _build_console_buffer() -> tuple[Console, StringIO]:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, color_system=None, width=120)
    return console, stream


def test_build_info_presenter_renders_summary_and_recommendations(tmp_path: Path) -> None:
    project = tmp_path.resolve()
    metadata = BuildMetadata(
        project_name="PresenterGame",
        project_file=project / "PresenterGame.uproject",
        engine_version="5.4",
        category="Games",
        description="Presenter fixture",
        plugin_count=2,
    )
    result = BuildInfoResult(
        project_path=project,
        metadata=metadata,
        environment=BuildEnvironmentInfo(),
        warnings=[
            BuildInfoWarning(
                code="build_info_partial_metadata",
                message="Some project metadata fields are missing or invalid; defaults were applied.",
                source=str(metadata.project_file),
                details="missing_fields=Description",
            )
        ],
    )
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()

    should_footer = render_build_info_result(result=result, console=console, visuals_module=visuals)
    output = stream.getvalue()

    assert should_footer is True
    assert "Build Metadata" in output
    assert "Project Information" in output
    assert "PresenterGame" in output
    assert "Starter Build Guidance" in output
    assert "starter CI/CD pipeline file" in output
    assert "Build Metadata Warnings" in output


def test_build_info_presenter_missing_project_signal_is_stable(tmp_path: Path) -> None:
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()
    result = BuildInfoResult(
        project_path=tmp_path.resolve(),
        errors=[
            BuildInfoError(
                code="build_info_project_missing",
                message="No .uproject file found!",
                source=str(tmp_path.resolve()),
            )
        ],
    )

    should_footer = render_build_info_result(result=result, console=console, visuals_module=visuals)
    output = stream.getvalue()

    assert should_footer is False
    assert "No .uproject file found!" in output


def test_build_info_presenter_parse_error_signal_is_stable(tmp_path: Path) -> None:
    visuals = _FakeVisuals()
    console, stream = _build_console_buffer()
    result = BuildInfoResult(
        project_path=tmp_path.resolve(),
        errors=[
            BuildInfoError(
                code="build_info_parse_failed",
                message="Error reading project file: Expecting value: line 1 column 1 (char 0)",
                source=str((tmp_path / "Broken.uproject").resolve()),
            )
        ],
    )

    should_footer = render_build_info_result(result=result, console=console, visuals_module=visuals)
    output = stream.getvalue()

    assert should_footer is True
    assert "Error reading project file:" in output


def test_build_info_presenter_path_errors_use_error_banner(tmp_path: Path) -> None:
    visuals = _FakeVisuals()
    console, _ = _build_console_buffer()
    result = BuildInfoResult(
        project_path=tmp_path.resolve(),
        errors=[
            BuildInfoError(
                code="build_info_path_not_found",
                message=f"Project path does not exist: {tmp_path.resolve()}",
                source=str(tmp_path.resolve()),
            )
        ],
    )

    should_footer = render_build_info_result(result=result, console=console, visuals_module=visuals)

    assert should_footer is False
    assert visuals.errors == [("PATH NOT FOUND", f"Project path does not exist: {tmp_path.resolve()}")]
