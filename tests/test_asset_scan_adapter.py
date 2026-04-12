# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Scan Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter tests for asset scan extraction slice."""

from __future__ import annotations

from pathlib import Path

from unrealmate.adapters.assets.asset_scan_adapter import AssetScanAdapter
from unrealmate.contracts.asset_scan import AssetScanRequest


def _create_scan_root(tmp_path: Path, name: str = "ScanRoot") -> Path:
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_asset_scan_adapter_category_aggregation_and_deterministic_order(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="DeterministicAssetScan")
    (scan_root / "A").mkdir(parents=True, exist_ok=True)
    (scan_root / "B").mkdir(parents=True, exist_ok=True)
    (scan_root / "A" / "SM_Model.fbx").write_bytes(b"A" * 128)
    (scan_root / "B" / "T_Diffuse.png").write_bytes(b"B" * 64)
    (scan_root / "B" / "M_SurfaceMaterial.uasset").write_bytes(b"C" * 256)
    (scan_root / "A" / "BP_Player.uasset").write_bytes(b"D" * 192)

    adapter = AssetScanAdapter()
    request = AssetScanRequest.from_cli(str(scan_root))
    result = adapter.scan(request)

    assert result.total_assets == 4
    assert [category.name for category in result.categories] == [
        "Blueprints",
        "Textures",
        "3D Models",
        "Materials",
    ]
    assert [asset.path.name for asset in result.largest_assets] == [
        "M_SurfaceMaterial.uasset",
        "BP_Player.uasset",
        "SM_Model.fbx",
        "T_Diffuse.png",
    ]


def test_asset_scan_adapter_unreadable_scan_path_returns_structured_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    scan_root = _create_scan_root(tmp_path, name="UnreadableAssetScan")
    adapter = AssetScanAdapter()
    request = AssetScanRequest.from_cli(str(scan_root))

    def _raise_permission(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise PermissionError("denied")

    monkeypatch.setattr(adapter, "_glob_pattern", _raise_permission)
    result = adapter.scan(request)

    assert result.is_success is False
    assert result.errors[0].code == "scan_path_unreadable"
    assert result.errors[0].source == str(scan_root.resolve())
    assert result.errors[0].details == "pattern_failures=22; total_patterns=22"
    assert result.total_assets == 0


def test_asset_scan_adapter_stat_failure_surfaces_warning(tmp_path: Path, monkeypatch) -> None:
    scan_root = _create_scan_root(tmp_path, name="StatFailureAssetScan")
    asset_file = scan_root / "BP_Test.uasset"
    asset_file.write_bytes(b"UEASSET")

    adapter = AssetScanAdapter()
    request = AssetScanRequest.from_cli(str(scan_root))

    original_safe_file_size = adapter._safe_file_size

    def _patched_safe_file_size(path: Path):
        if path == asset_file.resolve():
            return 0, adapter._build_stat_warning(path, PermissionError("denied"))
        return original_safe_file_size(path)

    monkeypatch.setattr(adapter, "_safe_file_size", _patched_safe_file_size)

    result = adapter.scan(request)

    assert result.is_success is True
    warning = next(warning for warning in result.warnings if warning.code == "asset_stat_failed")
    assert warning.message == "Asset metadata could not be read."
    assert warning.details == "operation=stat; error_type=PermissionError; error=denied"


def test_asset_scan_adapter_empty_path_returns_no_assets_warning(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="EmptyAssetScan")
    adapter = AssetScanAdapter()
    request = AssetScanRequest.from_cli(str(scan_root))
    result = adapter.scan(request)

    assert result.is_success is True
    assert result.has_data is False
    assert result.errors == []
    warning = next(warning for warning in result.warnings if warning.code == "no_assets_found")
    assert warning.details == "matched_assets=0"


def test_asset_scan_adapter_default_skip_patterns_are_stable(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="SkipPatternAssetScan")
    (scan_root / "Textures").mkdir(parents=True, exist_ok=True)
    (scan_root / "node_modules").mkdir(parents=True, exist_ok=True)

    (scan_root / "Textures" / "T_Main.png").write_bytes(b"A" * 10)
    (scan_root / "node_modules" / "T_Ignored.png").write_bytes(b"B" * 999)

    adapter = AssetScanAdapter()
    request = AssetScanRequest.from_cli(str(scan_root))
    result = adapter.scan(request)

    assert result.total_assets == 1
    assert result.assets[0].path.name == "T_Main.png"
