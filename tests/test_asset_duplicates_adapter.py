# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Duplicates Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter tests for asset duplicates extraction slice."""

from __future__ import annotations

from pathlib import Path

from unrealmate.adapters.assets.asset_duplicates_adapter import AssetDuplicatesAdapter
from unrealmate.contracts.asset_duplicates import AssetDuplicatesRequest, AssetDuplicatesWarning


def _create_scan_root(tmp_path: Path, name: str = "DuplicatesScanRoot") -> Path:
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_asset_duplicates_adapter_groups_by_name_and_is_deterministic(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="ByNameProject")
    (scan_root / "A").mkdir(parents=True, exist_ok=True)
    (scan_root / "B").mkdir(parents=True, exist_ok=True)
    (scan_root / "A" / "Shared.png").write_bytes(b"A" * 100)
    (scan_root / "B" / "Shared.png").write_bytes(b"B" * 80)
    (scan_root / "A" / "Unique.png").write_bytes(b"B" * 20)

    adapter = AssetDuplicatesAdapter()
    request = AssetDuplicatesRequest.from_cli(str(scan_root), by_content=False)
    result = adapter.find_duplicates(request)

    assert result.has_data is True
    assert result.total_groups == 1
    assert result.total_duplicate_files == 1
    assert result.groups[0].representative_name == "Shared.png"
    assert [entry.path.name for entry in result.groups[0].entries] == ["Shared.png", "Shared.png"]
    assert result.groups[0].retained_size_bytes == 100
    assert result.groups[0].total_group_size_bytes == 180
    assert result.groups[0].wasted_size_bytes == 80


def test_asset_duplicates_adapter_groups_by_content(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="ByContentProject")
    (scan_root / "A").mkdir(parents=True, exist_ok=True)
    (scan_root / "B").mkdir(parents=True, exist_ok=True)
    (scan_root / "A" / "Texture_A.png").write_bytes(b"IDENTICAL_DATA")
    (scan_root / "B" / "Texture_B.png").write_bytes(b"IDENTICAL_DATA")

    adapter = AssetDuplicatesAdapter()
    request = AssetDuplicatesRequest.from_cli(str(scan_root), by_content=True)
    result = adapter.find_duplicates(request)

    assert result.has_data is True
    assert result.total_groups == 1
    assert result.total_duplicate_files == 1
    assert result.groups[0].copies == 2
    assert [entry.path.name for entry in result.groups[0].entries] == ["Texture_A.png", "Texture_B.png"]
    assert len(result.groups[0].group_key) == 32


def test_asset_duplicates_adapter_respects_hash_strategy_policy(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="HashStrategyProject")
    (scan_root / "A").mkdir(parents=True, exist_ok=True)
    (scan_root / "B").mkdir(parents=True, exist_ok=True)
    (scan_root / "A" / "Texture_A.png").write_bytes(b"IDENTICAL_DATA")
    (scan_root / "B" / "Texture_B.png").write_bytes(b"IDENTICAL_DATA")

    adapter = AssetDuplicatesAdapter()
    request = AssetDuplicatesRequest.from_cli(
        str(scan_root),
        by_content=True,
        hash_strategy="sha256",
    )
    result = adapter.find_duplicates(request)

    assert result.hash_strategy == "sha256"
    assert result.grouping_mode == "content"
    assert result.total_groups == 1
    assert len(result.groups[0].group_key) == 64


def test_asset_duplicates_adapter_group_and_entry_ordering_is_deterministic(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="DeterministicDuplicatesProject")
    (scan_root / "G1" / "A").mkdir(parents=True, exist_ok=True)
    (scan_root / "G1" / "B").mkdir(parents=True, exist_ok=True)
    (scan_root / "G2" / "A").mkdir(parents=True, exist_ok=True)
    (scan_root / "G2" / "B").mkdir(parents=True, exist_ok=True)

    (scan_root / "G1" / "B" / "SharedBig.png").write_bytes(b"X" * 200)
    (scan_root / "G1" / "A" / "SharedBig.png").write_bytes(b"X" * 200)
    (scan_root / "G2" / "B" / "SharedSmall.png").write_bytes(b"Y" * 50)
    (scan_root / "G2" / "A" / "SharedSmall.png").write_bytes(b"Y" * 50)

    adapter = AssetDuplicatesAdapter()
    request = AssetDuplicatesRequest.from_cli(str(scan_root))
    result = adapter.find_duplicates(request)

    assert [group.representative_name for group in result.groups] == ["SharedBig.png", "SharedSmall.png"]
    assert [entry.path.as_posix().lower() for entry in result.groups[0].entries] == sorted(
        [entry.path.as_posix().lower() for entry in result.groups[0].entries]
    )
    assert [entry.path.as_posix().lower() for entry in result.groups[1].entries] == sorted(
        [entry.path.as_posix().lower() for entry in result.groups[1].entries]
    )


def test_asset_duplicates_adapter_unreadable_scan_path_returns_structured_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    scan_root = _create_scan_root(tmp_path, name="UnreadableDuplicatesProject")
    adapter = AssetDuplicatesAdapter()
    request = AssetDuplicatesRequest.from_cli(str(scan_root))

    def _raise_permission(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise PermissionError("denied")

    monkeypatch.setattr(adapter, "_list_scan_files", _raise_permission)
    result = adapter.find_duplicates(request)

    assert result.is_success is False
    assert result.errors[0].code == "duplicate_scan_path_unreadable"
    assert result.errors[0].source == str(scan_root.resolve())


def test_asset_duplicates_adapter_no_duplicates_returns_warning(tmp_path: Path) -> None:
    scan_root = _create_scan_root(tmp_path, name="NoDuplicatesProject")
    (scan_root / "OnlyOne.png").write_bytes(b"NO_DUP")

    adapter = AssetDuplicatesAdapter()
    request = AssetDuplicatesRequest.from_cli(str(scan_root))
    result = adapter.find_duplicates(request)

    assert result.is_success is True
    assert result.has_data is False
    assert result.total_groups == 0
    warning = next(warning for warning in result.warnings if warning.code == "no_duplicates_found")
    assert warning.details == "scanned_candidates=1; grouping_mode=filename; hash_strategy=none"


def test_asset_duplicates_adapter_stat_failure_emits_warning(tmp_path: Path, monkeypatch) -> None:
    scan_root = _create_scan_root(tmp_path, name="StatFailureDuplicatesProject")
    asset_file = scan_root / "Shared.png"
    asset_file.write_bytes(b"ASSET")

    adapter = AssetDuplicatesAdapter()
    request = AssetDuplicatesRequest.from_cli(str(scan_root))

    original_safe_file_size = adapter._safe_file_size

    def _forced_safe_file_size(path: Path):
        if path == asset_file.resolve():
            return 0, AssetDuplicatesWarning(
                code="duplicate_stat_failed",
                message="Asset metadata could not be read.",
                source=str(path.resolve()),
                details="operation=stat; error_type=PermissionError; error=denied",
            )
        return original_safe_file_size(path)

    monkeypatch.setattr(adapter, "_safe_file_size", _forced_safe_file_size)
    result = adapter.find_duplicates(request)

    warning = next(warning for warning in result.warnings if warning.code == "duplicate_stat_failed")
    assert warning.message == "Asset metadata could not be read."
    assert warning.details == "operation=stat; error_type=PermissionError; error=denied"


def test_asset_duplicates_adapter_partial_scan_failure_is_warning(tmp_path: Path, monkeypatch) -> None:
    scan_root = _create_scan_root(tmp_path, name="PartialFailureProject")
    duplicate_a = scan_root / "A" / "Shared.png"
    duplicate_b = scan_root / "B" / "Shared.png"
    duplicate_a.parent.mkdir(parents=True, exist_ok=True)
    duplicate_b.parent.mkdir(parents=True, exist_ok=True)
    duplicate_a.write_bytes(b"X" * 10)
    duplicate_b.write_bytes(b"Y" * 10)

    adapter = AssetDuplicatesAdapter()
    request = AssetDuplicatesRequest.from_cli(str(scan_root))
    original_list_scan_files = adapter._list_scan_files

    def _patched_list_scan_files(scan_path: Path, skip_patterns: tuple[str, ...]):
        files, warnings = original_list_scan_files(scan_path, skip_patterns)
        warnings.append(
            AssetDuplicatesWarning(
                code="duplicate_scan_partial_failed",
                message="Some subdirectories could not be scanned.",
                source=str((scan_root / "Restricted").resolve()),
                details="stage=walk; error_type=PermissionError; error=denied",
            )
        )
        return files, warnings

    monkeypatch.setattr(adapter, "_list_scan_files", _patched_list_scan_files)
    result = adapter.find_duplicates(request)

    warning = next(
        warning for warning in result.warnings if warning.code == "duplicate_scan_partial_failed"
    )
    assert warning.details == "stage=walk; error_type=PermissionError; error=denied"
    assert result.total_groups == 1
