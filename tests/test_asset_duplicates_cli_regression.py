# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Duplicates Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for asset duplicates extraction slice."""

from __future__ import annotations

import re
from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def _create_name_duplicate_project(tmp_path: Path) -> Path:
    content = tmp_path / "DuplicatesCliProject" / "Content"
    (content / "A").mkdir(parents=True, exist_ok=True)
    (content / "B").mkdir(parents=True, exist_ok=True)
    (content / "A" / "Shared.png").write_bytes(b"A" * 150)
    (content / "B" / "Shared.png").write_bytes(b"A" * 150)
    return content


def _create_content_duplicate_project(tmp_path: Path) -> Path:
    content = tmp_path / "DuplicatesContentCliProject" / "Content"
    (content / "A").mkdir(parents=True, exist_ok=True)
    (content / "B").mkdir(parents=True, exist_ok=True)
    (content / "A" / "Texture_A.png").write_bytes(b"IDENTICAL")
    (content / "B" / "Texture_B.png").write_bytes(b"IDENTICAL")
    return content


def test_asset_duplicates_cli_summary_signals_are_stable(monkeypatch, tmp_path: Path) -> None:
    scan_path = _create_name_duplicate_project(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["asset", "duplicates", str(scan_path)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Found 1 duplicate groups" in result.output
    assert "Summary:" in result.output
    assert "wasted space" in result.output


def test_asset_duplicates_cli_no_duplicates_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    empty_path = tmp_path / "NoDuplicatesCliProject"
    empty_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["asset", "duplicates", str(empty_path)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "No duplicate assets found!  Your project is clean." in result.output


def test_asset_duplicates_cli_by_content_mode_is_stable(monkeypatch, tmp_path: Path) -> None:
    scan_path = _create_content_duplicate_project(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["asset", "duplicates", str(scan_path), "--content"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Found 1 duplicate groups" in result.output
    squashed_output = re.sub(r"\s+", "", result.output)
    assert "Texture_A.png" in squashed_output
    assert "Texture_B.png" in squashed_output
