# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Scan Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for asset scan extraction slice."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def _create_scan_project(tmp_path: Path) -> Path:
    content = tmp_path / "AssetCliProject" / "Content"
    (content / "Blueprints").mkdir(parents=True, exist_ok=True)
    (content / "Materials").mkdir(parents=True, exist_ok=True)
    (content / "Textures").mkdir(parents=True, exist_ok=True)
    (content / "Blueprints" / "BP_Player.uasset").write_bytes(b"A" * 200)
    (content / "Materials" / "M_BaseMaterial.uasset").write_bytes(b"B" * 300)
    (content / "Textures" / "T_Albedo.png").write_bytes(b"C" * 100)
    return content


def test_asset_scan_cli_shows_summary_signals(monkeypatch, tmp_path: Path) -> None:
    scan_path = _create_scan_project(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["asset", "scan", str(scan_path)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Scanning location:" in result.output
    assert "Asset Inventory" in result.output
    assert "Scan Summary" in result.output
    assert "Top 5 Largest Assets" in result.output


def test_asset_scan_cli_no_data_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    empty_path = tmp_path / "EmptyAssetCliProject"
    empty_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["asset", "scan", str(empty_path)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "NO ASSETS FOUND" in result.output


def test_asset_scan_cli_show_all_includes_detailed_list(monkeypatch, tmp_path: Path) -> None:
    scan_path = _create_scan_project(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["asset", "scan", str(scan_path), "--all"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Detailed Asset List:" in result.output
    assert "Warnings:" not in result.output
