# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Organize Use Case
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Contract and use-case tests for asset organize extraction slice."""

from __future__ import annotations

from pathlib import Path

from unrealmate.contracts.asset_organize import AssetOrganizeRequest
from unrealmate.core.application.use_cases.organize_assets import OrganizeAssetsUseCase


def _create_organize_fixture(tmp_path: Path) -> Path:
    content = tmp_path / "AssetOrganizeProject" / "Content"
    content.mkdir(parents=True, exist_ok=True)
    (content / "LooseTexture.png").write_bytes(b"T" * 20)
    return content


def test_asset_organize_request_normalizes_relative_cli_path(tmp_path: Path, monkeypatch) -> None:
    content = _create_organize_fixture(tmp_path)
    monkeypatch.chdir(content)

    request = AssetOrganizeRequest.from_cli(".", dry_run=True, yes=False)

    assert request.scan_path == content.resolve()
    assert request.scan_path.is_absolute()
    assert request.dry_run is True
    assert request.assume_yes is False
    assert request.policy.conflict_suffix_separator == "_"


def test_asset_organize_use_case_invalid_path_returns_structured_error(tmp_path: Path) -> None:
    missing = tmp_path / "MissingContent"
    use_case = OrganizeAssetsUseCase()
    request = AssetOrganizeRequest.from_cli(str(missing), dry_run=True)
    result = use_case.execute(request)

    assert result.is_success is False
    assert result.errors[0].code == "organize_path_not_found"
    assert result.errors[0].source == str(missing.resolve())


def test_asset_organize_use_case_file_path_returns_structured_error(tmp_path: Path) -> None:
    file_path = tmp_path / "not_a_directory.txt"
    file_path.write_text("x", encoding="utf-8")

    use_case = OrganizeAssetsUseCase()
    request = AssetOrganizeRequest.from_cli(str(file_path), dry_run=True)
    result = use_case.execute(request)

    assert result.is_success is False
    assert result.errors[0].code == "organize_path_not_directory"
    assert result.errors[0].source == str(file_path.resolve())

