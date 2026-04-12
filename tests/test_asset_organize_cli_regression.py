# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Organize Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for asset organize extraction slice."""

from __future__ import annotations

import shutil
from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def _create_loose_assets_project(tmp_path: Path) -> Path:
    content = tmp_path / "OrganizeCliProject" / "Content"
    content.mkdir(parents=True, exist_ok=True)
    (content / "LooseTexture.png").write_bytes(b"T" * 100)
    (content / "LooseAudio.wav").write_bytes(b"A" * 200)
    return content


def test_asset_organize_cli_dry_run_signals_are_stable(monkeypatch, tmp_path: Path) -> None:
    scan_path = _create_loose_assets_project(tmp_path)
    texture = scan_path / "LooseTexture.png"
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["asset", "organize", str(scan_path), "--dry-run", "--yes"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Files to Organize" in result.output
    assert "Dry run mode - no files were moved" in result.output
    assert "rollback snapshot" in result.output
    assert texture.exists()


def test_asset_organize_cli_no_changes_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    scan_path = tmp_path / "OrganizeCliNoChanges" / "Content" / "Textures"
    scan_path.mkdir(parents=True, exist_ok=True)
    (scan_path / "AlreadyOrganized.png").write_bytes(b"X")
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["asset", "organize", str(scan_path.parent), "--dry-run", "--yes"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "All assets are already organized!" in result.output


def test_asset_organize_cli_execution_moves_files(monkeypatch, tmp_path: Path) -> None:
    scan_path = _create_loose_assets_project(tmp_path)
    source = scan_path / "LooseTexture.png"
    target = scan_path / "Textures" / "LooseTexture.png"
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["asset", "organize", str(scan_path), "--yes"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Organization complete!" in result.output
    assert "Moved 2 files, 0 errors" in result.output
    assert not source.exists()
    assert target.exists()


def test_asset_organize_cli_partial_failure_exits_non_zero(monkeypatch, tmp_path: Path) -> None:
    scan_path = _create_loose_assets_project(tmp_path)
    real_move = shutil.move
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    def _patched_move(src: str, dst: str):
        if src.endswith("LooseAudio.wav"):
            raise PermissionError("locked")
        return real_move(src, dst)

    monkeypatch.setattr(cli.shutil, "move", _patched_move)

    result = runner.invoke(
        cli.app,
        ["asset", "organize", str(scan_path), "--yes"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "ORGANIZATION INCOMPLETE" in result.output
    assert "Some files could not be moved." in result.output
