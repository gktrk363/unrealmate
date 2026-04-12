# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Organize Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter tests for asset organize extraction slice."""

from __future__ import annotations

from pathlib import Path

from unrealmate.adapters.assets.asset_organize_adapter import AssetOrganizeAdapter
from unrealmate.contracts.asset_organize import AssetOrganizeRequest, AssetOrganizeWarning


def _create_scan_root(tmp_path: Path, name: str = "OrganizeScanRoot") -> Path:
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_asset_organize_adapter_dry_run_plans_moves(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="DryRunProject")
    (scan_root / "LooseTexture.png").write_bytes(b"T" * 10)
    (scan_root / "LooseAudio.wav").write_bytes(b"A" * 20)

    adapter = AssetOrganizeAdapter()
    request = AssetOrganizeRequest.from_cli(str(scan_root), dry_run=True)
    result = adapter.organize(request)

    assert result.dry_run is True
    assert result.is_success is True
    assert result.has_changes is True
    assert len(result.planned_moves) == 2
    assert result.executed_moves == []
    assert {entry.category for entry in result.planned_moves} == {"Textures", "Audio"}


def test_asset_organize_adapter_detects_conflicts_in_plan(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="ConflictProject")
    source = scan_root / "LooseTexture.png"
    source.write_bytes(b"S" * 30)
    target_dir = scan_root / "Textures"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "LooseTexture.png").write_bytes(b"T" * 30)

    adapter = AssetOrganizeAdapter()
    request = AssetOrganizeRequest.from_cli(str(scan_root), dry_run=True)
    result = adapter.organize(request)

    assert result.has_changes is True
    assert len(result.conflicts) == 1
    assert result.conflicts[0].conflict_detected is True
    assert result.conflicts[0].final_target_path.name.startswith("LooseTexture_")
    warning_codes = [warning.code for warning in result.warnings]
    assert "organize_conflict_detected" in warning_codes


def test_asset_organize_adapter_no_changes_returns_warning(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="NoChangesProject")
    textures = scan_root / "Textures"
    textures.mkdir(parents=True, exist_ok=True)
    (textures / "AlreadyOrganized.png").write_bytes(b"O" * 10)

    adapter = AssetOrganizeAdapter()
    request = AssetOrganizeRequest.from_cli(str(scan_root), dry_run=True)
    result = adapter.organize(request)

    assert result.has_changes is False
    warning = next(w for w in result.warnings if w.code == "organize_no_changes")
    assert warning.details == "candidate_files=1"


def test_asset_organize_adapter_execution_moves_files(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="ExecutionProject")
    source = scan_root / "LooseTexture.png"
    source.write_bytes(b"T" * 15)

    adapter = AssetOrganizeAdapter()
    request = AssetOrganizeRequest.from_cli(str(scan_root), dry_run=False)
    result = adapter.organize(request)

    moved_target = scan_root / "Textures" / "LooseTexture.png"
    assert result.dry_run is False
    assert len(result.executed_moves) == 1
    assert result.failed_moves == []
    assert moved_target.exists()
    assert not source.exists()


def test_asset_organize_adapter_ordering_is_deterministic(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="OrderProject")
    (scan_root / "z_file.png").write_bytes(b"1")
    (scan_root / "a_file.png").write_bytes(b"2")
    (scan_root / "b_file.wav").write_bytes(b"3")

    adapter = AssetOrganizeAdapter()
    request = AssetOrganizeRequest.from_cli(str(scan_root), dry_run=True)
    result = adapter.organize(request)

    planned = [(entry.category, entry.source_path.name) for entry in result.planned_moves]
    assert planned == [
        ("Audio", "b_file.wav"),
        ("Textures", "a_file.png"),
        ("Textures", "z_file.png"),
    ]


def test_asset_organize_adapter_partial_scan_warning_surface(tmp_path: Path, monkeypatch) -> None:
    scan_root = _create_scan_root(tmp_path, name="PartialScanProject")
    (scan_root / "LooseTexture.png").write_bytes(b"T" * 10)
    adapter = AssetOrganizeAdapter()
    request = AssetOrganizeRequest.from_cli(str(scan_root), dry_run=True)
    original_list_files = adapter._list_files

    def _patched_list_files(path: Path, skip_patterns: tuple[str, ...]):
        files, warnings = original_list_files(path, skip_patterns)
        warnings.append(
            AssetOrganizeWarning(
                code="organize_scan_failed",
                message="Some subdirectories could not be scanned.",
                source=str((scan_root / "Restricted").resolve()),
                details="stage=walk; error_type=PermissionError; error=denied",
            )
        )
        return files, warnings

    monkeypatch.setattr(adapter, "_list_files", _patched_list_files)
    result = adapter.organize(request)

    warning = next(w for w in result.warnings if w.code == "organize_scan_failed")
    assert warning.details == "stage=walk; error_type=PermissionError; error=denied"
    assert len(result.planned_moves) == 1

