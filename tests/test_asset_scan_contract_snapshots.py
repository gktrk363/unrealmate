# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Scan Contract Snapshots
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Structured payload snapshot tests for asset scan stabilization."""

from __future__ import annotations

from pathlib import Path

from unrealmate.adapters.assets.asset_scan_adapter import AssetScanAdapter
from unrealmate.contracts.asset_scan import AssetScanCategoryRule, AssetScanRequest
from unrealmate.core.application.use_cases.scan_assets import ScanAssetsUseCase


def test_asset_scan_payload_snapshot_for_normal_result(tmp_path: Path) -> None:
    scan_path = tmp_path / "SnapshotNormal" / "Content"
    (scan_path / "Blueprints").mkdir(parents=True, exist_ok=True)
    (scan_path / "Materials").mkdir(parents=True, exist_ok=True)
    (scan_path / "Textures").mkdir(parents=True, exist_ok=True)
    (scan_path / "Meshes").mkdir(parents=True, exist_ok=True)

    bp = scan_path / "Blueprints" / "BP_Player.uasset"
    mat = scan_path / "Materials" / "M_MasterMaterial.uasset"
    tex = scan_path / "Textures" / "T_Albedo.png"
    mesh = scan_path / "Meshes" / "SM_Chair.fbx"
    bp.write_bytes(b"B" * 200)
    mat.write_bytes(b"M" * 300)
    tex.write_bytes(b"T" * 100)
    mesh.write_bytes(b"S" * 150)

    use_case = ScanAssetsUseCase()
    result = use_case.execute(AssetScanRequest.from_cli(str(scan_path)))

    assert result.to_payload() == {
        "scan_path": str(scan_path.resolve()),
        "categories": [
            {"name": "3D Models", "count": 1, "size_bytes": 150},
            {"name": "Blueprints", "count": 1, "size_bytes": 200},
            {"name": "Materials", "count": 1, "size_bytes": 300},
            {"name": "Textures", "count": 1, "size_bytes": 100},
        ],
        "assets": [
            {"path": str(mat.resolve()), "category": "Materials", "size_bytes": 300},
            {"path": str(bp.resolve()), "category": "Blueprints", "size_bytes": 200},
            {"path": str(mesh.resolve()), "category": "3D Models", "size_bytes": 150},
            {"path": str(tex.resolve()), "category": "Textures", "size_bytes": 100},
        ],
        "largest_assets": [
            {"path": str(mat.resolve()), "category": "Materials", "size_bytes": 300},
            {"path": str(bp.resolve()), "category": "Blueprints", "size_bytes": 200},
            {"path": str(mesh.resolve()), "category": "3D Models", "size_bytes": 150},
            {"path": str(tex.resolve()), "category": "Textures", "size_bytes": 100},
        ],
        "total_assets": 4,
        "total_size_bytes": 750,
        "warnings": [],
        "errors": [],
        "detailed_assets_limit": 50,
        "largest_assets_limit": 5,
    }


def test_asset_scan_payload_snapshot_for_no_assets_found(tmp_path: Path) -> None:
    scan_path = tmp_path / "SnapshotEmpty"
    scan_path.mkdir(parents=True, exist_ok=True)

    use_case = ScanAssetsUseCase()
    result = use_case.execute(AssetScanRequest.from_cli(str(scan_path)))

    assert result.to_payload() == {
        "scan_path": str(scan_path.resolve()),
        "categories": [],
        "assets": [],
        "largest_assets": [],
        "total_assets": 0,
        "total_size_bytes": 0,
        "warnings": [
            {
                "code": "no_assets_found",
                "message": "Target directory appears to contain no trackable assets.",
                "source": str(scan_path.resolve()),
                "details": "matched_assets=0",
            }
        ],
        "errors": [],
        "detailed_assets_limit": 50,
        "largest_assets_limit": 5,
    }


def test_asset_scan_payload_snapshot_for_unreadable_pattern_failure(tmp_path: Path, monkeypatch) -> None:
    scan_path = tmp_path / "SnapshotUnreadable"
    scan_path.mkdir(parents=True, exist_ok=True)
    adapter = AssetScanAdapter()

    def _raise_permission(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise PermissionError("denied")

    monkeypatch.setattr(adapter, "_glob_pattern", _raise_permission)
    request = AssetScanRequest.from_cli(
        str(scan_path),
        category_rules=(
            AssetScanCategoryRule(
                name="Textures",
                patterns=("*.png",),
            ),
        ),
    )
    result = adapter.scan(request)

    assert result.to_payload() == {
        "scan_path": str(scan_path.resolve()),
        "categories": [],
        "assets": [],
        "largest_assets": [],
        "total_assets": 0,
        "total_size_bytes": 0,
        "warnings": [
            {
                "code": "scan_pattern_failed",
                "message": "Asset scan failed for one category pattern.",
                "source": str(scan_path.resolve()),
                "details": "category=Textures; pattern=*.png; error_type=PermissionError; error=denied",
            }
        ],
        "errors": [
            {
                "code": "scan_path_unreadable",
                "message": "Scan path could not be read with current permissions.",
                "source": str(scan_path.resolve()),
                "details": "pattern_failures=1; total_patterns=1",
            }
        ],
        "detailed_assets_limit": 50,
        "largest_assets_limit": 5,
    }


def test_asset_scan_payload_snapshot_for_stat_failure_warning(tmp_path: Path, monkeypatch) -> None:
    scan_path = tmp_path / "SnapshotStatFailure"
    scan_path.mkdir(parents=True, exist_ok=True)
    asset_file = scan_path / "BP_Test.uasset"
    asset_file.write_bytes(b"UEASSET")

    adapter = AssetScanAdapter()
    request = AssetScanRequest.from_cli(str(scan_path))
    original_safe_file_size = adapter._safe_file_size

    def _patched_safe_file_size(path: Path):
        if path == asset_file.resolve():
            return 0, adapter._build_stat_warning(path, PermissionError("denied"))
        return original_safe_file_size(path)

    monkeypatch.setattr(adapter, "_safe_file_size", _patched_safe_file_size)
    result = adapter.scan(request)

    assert result.to_payload() == {
        "scan_path": str(scan_path.resolve()),
        "categories": [
            {"name": "Blueprints", "count": 1, "size_bytes": 0},
        ],
        "assets": [
            {"path": str(asset_file.resolve()), "category": "Blueprints", "size_bytes": 0},
        ],
        "largest_assets": [
            {"path": str(asset_file.resolve()), "category": "Blueprints", "size_bytes": 0},
        ],
        "total_assets": 1,
        "total_size_bytes": 0,
        "warnings": [
            {
                "code": "asset_stat_failed",
                "message": "Asset metadata could not be read.",
                "source": str(asset_file.resolve()),
                "details": "operation=stat; error_type=PermissionError; error=denied",
            }
        ],
        "errors": [],
        "detailed_assets_limit": 50,
        "largest_assets_limit": 5,
    }
