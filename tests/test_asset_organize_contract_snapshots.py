# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Organize Contract Snapshots
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Structured payload snapshot tests for asset organize extraction slice."""

from __future__ import annotations

from pathlib import Path

from unrealmate.adapters.assets.asset_organize_adapter import AssetOrganizeAdapter
from unrealmate.contracts.asset_organize import AssetOrganizeRequest, AssetOrganizeWarning
from unrealmate.core.application.use_cases.organize_assets import OrganizeAssetsUseCase


def test_asset_organize_payload_snapshot_for_dry_run_plan(tmp_path: Path) -> None:
    scan_path = tmp_path / "SnapshotOrganize" / "Content"
    scan_path.mkdir(parents=True, exist_ok=True)
    texture = scan_path / "LooseTexture.png"
    texture.write_bytes(b"T" * 10)

    use_case = OrganizeAssetsUseCase()
    result = use_case.execute(AssetOrganizeRequest.from_cli(str(scan_path), dry_run=True))

    assert result.to_payload() == {
        "scan_path": str(scan_path.resolve()),
        "dry_run": True,
        "planned_moves": [
            {
                "source_path": str(texture.resolve()),
                "requested_target_path": str((scan_path / "Textures" / "LooseTexture.png").resolve()),
                "final_target_path": str((scan_path / "Textures" / "LooseTexture.png").resolve()),
                "category": "Textures",
                "conflict_detected": False,
                "conflict_index": 0,
            }
        ],
        "executed_moves": [],
        "skipped_moves": [],
        "failed_moves": [],
        "conflicts": [],
        "totals": {
            "planned": 1,
            "executed": 0,
            "skipped": 0,
            "failed": 0,
            "conflicts": 0,
        },
        "warnings": [],
        "errors": [],
    }


def test_asset_organize_payload_snapshot_for_no_changes(tmp_path: Path) -> None:
    scan_path = tmp_path / "SnapshotNoChanges"
    textures = scan_path / "Textures"
    textures.mkdir(parents=True, exist_ok=True)
    organized = textures / "AlreadyOrganized.png"
    organized.write_bytes(b"X")

    use_case = OrganizeAssetsUseCase()
    result = use_case.execute(AssetOrganizeRequest.from_cli(str(scan_path), dry_run=True))

    assert result.to_payload() == {
        "scan_path": str(scan_path.resolve()),
        "dry_run": True,
        "planned_moves": [],
        "executed_moves": [],
        "skipped_moves": [],
        "failed_moves": [],
        "conflicts": [],
        "totals": {
            "planned": 0,
            "executed": 0,
            "skipped": 0,
            "failed": 0,
            "conflicts": 0,
        },
        "warnings": [
            {
                "code": "organize_no_changes",
                "message": "All assets are already organized.",
                "source": str(scan_path.resolve()),
                "details": "candidate_files=1",
            }
        ],
        "errors": [],
    }


def test_asset_organize_payload_snapshot_for_partial_scan_warning(tmp_path: Path, monkeypatch) -> None:
    scan_path = tmp_path / "SnapshotPartialScan"
    scan_path.mkdir(parents=True, exist_ok=True)
    texture = scan_path / "LooseTexture.png"
    texture.write_bytes(b"T")

    adapter = AssetOrganizeAdapter()
    original_list_files = adapter._list_files

    def _patched_list_files(path: Path, skip_patterns: tuple[str, ...]):
        files, warnings = original_list_files(path, skip_patterns)
        warnings.append(
            AssetOrganizeWarning(
                code="organize_scan_failed",
                message="Some subdirectories could not be scanned.",
                source=str((scan_path / "Restricted").resolve()),
                details="stage=walk; error_type=PermissionError; error=denied",
            )
        )
        return files, warnings

    monkeypatch.setattr(adapter, "_list_files", _patched_list_files)
    use_case = OrganizeAssetsUseCase(adapter=adapter)
    result = use_case.execute(AssetOrganizeRequest.from_cli(str(scan_path), dry_run=True))
    payload = result.to_payload()

    assert payload["warnings"] == [
        {
            "code": "organize_scan_failed",
            "message": "Some subdirectories could not be scanned.",
            "source": str((scan_path / "Restricted").resolve()),
            "details": "stage=walk; error_type=PermissionError; error=denied",
        }
    ]
    assert payload["totals"]["planned"] == 1

