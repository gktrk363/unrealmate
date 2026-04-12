# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Duplicates Use Case
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Contract and use-case tests for asset duplicates extraction slice."""

from __future__ import annotations

from pathlib import Path

import pytest

from unrealmate.contracts.asset_duplicates import AssetDuplicatesRequest
from unrealmate.core.application.use_cases.find_duplicate_assets import (
    FindDuplicateAssetsUseCase,
)


def _create_duplicate_fixture(tmp_path: Path) -> Path:
    content = tmp_path / "AssetDuplicatesProject" / "Content"
    (content / "A").mkdir(parents=True, exist_ok=True)
    (content / "B").mkdir(parents=True, exist_ok=True)
    (content / "A" / "Shared.png").write_bytes(b"A" * 32)
    (content / "B" / "Shared.png").write_bytes(b"A" * 32)
    return content


def test_asset_duplicates_request_normalizes_relative_cli_path(tmp_path: Path, monkeypatch) -> None:
    content = _create_duplicate_fixture(tmp_path)
    monkeypatch.chdir(content)

    request = AssetDuplicatesRequest.from_cli(".")

    assert request.scan_path == content.resolve()
    assert request.scan_path.is_absolute()
    assert request.by_content is False
    assert request.grouping_mode == "filename"
    assert request.hash_strategy == "md5"
    assert ".png" in request.asset_extensions


def test_asset_duplicates_request_policy_normalization(tmp_path: Path) -> None:
    request = AssetDuplicatesRequest.from_cli(
        str(tmp_path),
        by_content=True,
        asset_extensions=("PNG", ".uasset", " .JPG "),
        skip_patterns=("Saved", "  Node_Modules "),
        hash_strategy="SHA256",
    )

    assert request.grouping_mode == "content"
    assert request.hash_strategy == "sha256"
    assert request.asset_extensions == (".jpg", ".png", ".uasset")
    assert request.skip_patterns == ("node_modules", "saved")


def test_asset_duplicates_request_rejects_unsupported_hash_strategy(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        AssetDuplicatesRequest.from_cli(
            str(tmp_path),
            by_content=True,
            hash_strategy="sha512",
        )


def test_asset_duplicates_use_case_returns_structured_result_shape(tmp_path: Path) -> None:
    content = _create_duplicate_fixture(tmp_path)
    use_case = FindDuplicateAssetsUseCase()
    request = AssetDuplicatesRequest.from_cli(str(content))

    result = use_case.execute(request)

    assert result.is_success is True
    assert result.has_data is True
    assert result.total_groups == 1
    assert result.total_duplicate_files == 1
    assert result.errors == []

    payload = result.to_payload()
    assert set(payload.keys()) == {
        "scan_path",
        "by_content",
        "grouping_mode",
        "hash_strategy",
        "groups",
        "total_groups",
        "total_duplicate_files",
        "total_wasted_size_bytes",
        "scanned_candidate_files",
        "warnings",
        "errors",
    }
    assert payload["groups"][0]["representative_name"] == "Shared.png"
    assert len(payload["groups"][0]["entries"]) == 2


def test_asset_duplicates_use_case_invalid_path_returns_structured_error(tmp_path: Path) -> None:
    missing = tmp_path / "MissingContent"
    use_case = FindDuplicateAssetsUseCase()
    request = AssetDuplicatesRequest.from_cli(str(missing))
    result = use_case.execute(request)

    assert result.is_success is False
    assert result.has_data is False
    assert result.errors[0].code == "duplicate_scan_path_not_found"
    assert result.errors[0].source == str(missing.resolve())
