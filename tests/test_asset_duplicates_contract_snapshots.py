# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Duplicates Contract Snapshots
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Structured payload snapshot tests for asset duplicates extraction slice."""

from __future__ import annotations

from pathlib import Path

from unrealmate.adapters.assets.asset_duplicates_adapter import AssetDuplicatesAdapter
from unrealmate.contracts.asset_duplicates import AssetDuplicatesRequest, AssetDuplicatesWarning
from unrealmate.core.application.use_cases.find_duplicate_assets import (
    FindDuplicateAssetsUseCase,
)


def test_asset_duplicates_payload_snapshot_for_name_grouping(tmp_path: Path) -> None:
    scan_path = tmp_path / "SnapshotDuplicates" / "Content"
    (scan_path / "A").mkdir(parents=True, exist_ok=True)
    (scan_path / "B").mkdir(parents=True, exist_ok=True)

    first = scan_path / "A" / "Shared.png"
    second = scan_path / "B" / "Shared.png"
    first.write_bytes(b"S" * 120)
    second.write_bytes(b"T" * 90)

    use_case = FindDuplicateAssetsUseCase()
    result = use_case.execute(AssetDuplicatesRequest.from_cli(str(scan_path)))

    assert result.to_payload() == {
        "scan_path": str(scan_path.resolve()),
        "by_content": False,
        "grouping_mode": "filename",
        "hash_strategy": "md5",
        "groups": [
            {
                "group_key": "shared.png",
                "representative_name": "Shared.png",
                "entries": [
                    {"path": str(first.resolve()), "size_bytes": 120},
                    {"path": str(second.resolve()), "size_bytes": 90},
                ],
                "copies": 2,
                "duplicate_files": 1,
                "retained_size_bytes": 120,
                "total_group_size_bytes": 210,
                "wasted_size_bytes": 90,
            }
        ],
        "total_groups": 1,
        "total_duplicate_files": 1,
        "total_wasted_size_bytes": 90,
        "scanned_candidate_files": 2,
        "warnings": [],
        "errors": [],
    }


def test_asset_duplicates_payload_snapshot_for_no_duplicates(tmp_path: Path) -> None:
    scan_path = tmp_path / "SnapshotNoDuplicates"
    scan_path.mkdir(parents=True, exist_ok=True)
    lone = scan_path / "Solo.png"
    lone.write_bytes(b"X")

    use_case = FindDuplicateAssetsUseCase()
    result = use_case.execute(AssetDuplicatesRequest.from_cli(str(scan_path)))

    assert result.to_payload() == {
        "scan_path": str(scan_path.resolve()),
        "by_content": False,
        "grouping_mode": "filename",
        "hash_strategy": "md5",
        "groups": [],
        "total_groups": 0,
        "total_duplicate_files": 0,
        "total_wasted_size_bytes": 0,
        "scanned_candidate_files": 1,
        "warnings": [
            {
                "code": "no_duplicates_found",
                "message": "No duplicate assets found.",
                "source": str(scan_path.resolve()),
                "details": "scanned_candidates=1; grouping_mode=filename; hash_strategy=none",
            }
        ],
        "errors": [],
    }


def test_asset_duplicates_payload_snapshot_for_unreadable_scan_path(tmp_path: Path, monkeypatch) -> None:
    scan_path = tmp_path / "SnapshotUnreadableDuplicates"
    scan_path.mkdir(parents=True, exist_ok=True)
    adapter = AssetDuplicatesAdapter()

    def _raise_permission(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise PermissionError("denied")

    monkeypatch.setattr(adapter, "_list_scan_files", _raise_permission)
    request = AssetDuplicatesRequest.from_cli(str(scan_path))
    result = adapter.find_duplicates(request)

    assert result.to_payload() == {
        "scan_path": str(scan_path.resolve()),
        "by_content": False,
        "grouping_mode": "filename",
        "hash_strategy": "md5",
        "groups": [],
        "total_groups": 0,
        "total_duplicate_files": 0,
        "total_wasted_size_bytes": 0,
        "scanned_candidate_files": 0,
        "warnings": [],
        "errors": [
            {
                "code": "duplicate_scan_path_unreadable",
                "message": "Scan path could not be read with current permissions.",
                "source": str(scan_path.resolve()),
                "details": "error_type=PermissionError; error=denied",
            }
        ],
    }


def test_asset_duplicates_payload_snapshot_for_partial_scan_warning(tmp_path: Path, monkeypatch) -> None:
    scan_path = tmp_path / "SnapshotPartialDuplicates"
    (scan_path / "A").mkdir(parents=True, exist_ok=True)
    (scan_path / "B").mkdir(parents=True, exist_ok=True)
    a_file = scan_path / "A" / "Shared.png"
    b_file = scan_path / "B" / "Shared.png"
    a_file.write_bytes(b"A" * 10)
    b_file.write_bytes(b"B" * 10)

    adapter = AssetDuplicatesAdapter()
    original_list_scan_files = adapter._list_scan_files

    def _patched_list_scan_files(scan_root: Path, skip_patterns: tuple[str, ...]):
        files, warnings = original_list_scan_files(scan_root, skip_patterns)
        warnings.append(
            AssetDuplicatesWarning(
                code="duplicate_scan_partial_failed",
                message="Some subdirectories could not be scanned.",
                source=str((scan_path / "Restricted").resolve()),
                details="stage=walk; error_type=PermissionError; error=denied",
            )
        )
        return files, warnings

    monkeypatch.setattr(adapter, "_list_scan_files", _patched_list_scan_files)
    request = AssetDuplicatesRequest.from_cli(str(scan_path))
    result = adapter.find_duplicates(request)
    payload = result.to_payload()

    assert payload["warnings"] == [
        {
            "code": "duplicate_scan_partial_failed",
            "message": "Some subdirectories could not be scanned.",
            "source": str((scan_path / "Restricted").resolve()),
            "details": "stage=walk; error_type=PermissionError; error=denied",
        }
    ]
    assert payload["total_groups"] == 1


def test_asset_duplicates_payload_snapshot_for_content_hash_strategy(tmp_path: Path) -> None:
    scan_path = tmp_path / "SnapshotContentHash"
    (scan_path / "A").mkdir(parents=True, exist_ok=True)
    (scan_path / "B").mkdir(parents=True, exist_ok=True)
    a_file = scan_path / "A" / "Texture_A.png"
    b_file = scan_path / "B" / "Texture_B.png"
    a_file.write_bytes(b"IDENTICAL_DATA")
    b_file.write_bytes(b"IDENTICAL_DATA")

    use_case = FindDuplicateAssetsUseCase()
    request = AssetDuplicatesRequest.from_cli(
        str(scan_path),
        by_content=True,
        hash_strategy="sha256",
    )
    result = use_case.execute(request)
    payload = result.to_payload()

    assert payload["grouping_mode"] == "content"
    assert payload["hash_strategy"] == "sha256"
    assert len(payload["groups"][0]["group_key"]) == 64
