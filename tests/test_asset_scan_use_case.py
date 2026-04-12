# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Scan Use Case
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Contract and use-case tests for asset scan extraction slice."""

from __future__ import annotations

from pathlib import Path

from unrealmate.contracts.asset_scan import AssetScanRequest
from unrealmate.core.application.use_cases.scan_assets import ScanAssetsUseCase


def _create_asset_fixture(tmp_path: Path) -> Path:
    project = tmp_path / "AssetScanProject"
    content = project / "Content"
    (content / "Blueprints").mkdir(parents=True, exist_ok=True)
    (content / "Materials").mkdir(parents=True, exist_ok=True)
    (content / "Textures").mkdir(parents=True, exist_ok=True)

    (content / "Blueprints" / "BP_Test.uasset").write_bytes(b"UEASSET_BP")
    (content / "Materials" / "M_MasterMaterial.uasset").write_bytes(b"UEASSET_MAT")
    (content / "Textures" / "T_Albedo.png").write_bytes(b"\x89PNG\r\n")
    return content


def test_asset_scan_request_normalizes_relative_cli_path(tmp_path: Path, monkeypatch) -> None:
    content = _create_asset_fixture(tmp_path)
    monkeypatch.chdir(content)

    request = AssetScanRequest.from_cli(".")

    assert request.scan_path == content.resolve()
    assert request.scan_path.is_absolute()
    assert request.detailed_assets_limit == 50
    assert request.largest_assets_limit == 5


def test_asset_scan_use_case_returns_structured_result_shape(tmp_path: Path) -> None:
    content = _create_asset_fixture(tmp_path)
    use_case = ScanAssetsUseCase()
    request = AssetScanRequest.from_cli(str(content))

    result = use_case.execute(request)

    assert result.is_success is True
    assert result.has_data is True
    assert result.total_assets == 3
    assert result.total_size_bytes > 0
    assert len(result.categories) >= 2
    assert len(result.largest_assets) <= request.largest_assets_limit
    assert result.errors == []

    payload = result.to_payload()
    assert set(payload.keys()) == {
        "scan_path",
        "categories",
        "assets",
        "largest_assets",
        "total_assets",
        "total_size_bytes",
        "warnings",
        "errors",
        "detailed_assets_limit",
        "largest_assets_limit",
    }
    assert payload["total_assets"] == 3
    assert payload["scan_path"] == str(content.resolve())
    assert any(category["name"] == "Blueprints" for category in payload["categories"])


def test_asset_scan_use_case_invalid_path_returns_structured_error(tmp_path: Path) -> None:
    missing = tmp_path / "MissingContent"
    use_case = ScanAssetsUseCase()
    request = AssetScanRequest.from_cli(str(missing))

    result = use_case.execute(request)

    assert result.is_success is False
    assert result.has_data is False
    assert result.total_assets == 0
    assert result.errors[0].code == "scan_path_not_found"
    assert result.errors[0].source == str(missing.resolve())


def test_asset_scan_use_case_file_path_returns_structured_error(tmp_path: Path) -> None:
    file_path = tmp_path / "not_a_dir.txt"
    file_path.write_text("x", encoding="utf-8")

    use_case = ScanAssetsUseCase()
    request = AssetScanRequest.from_cli(str(file_path))
    result = use_case.execute(request)

    assert result.is_success is False
    assert result.errors[0].code == "scan_path_not_directory"
    assert result.errors[0].source == str(file_path.resolve())
