# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Asset Domain Consolidation
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Consolidation tests for shared asset-domain conventions and helpers."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from rich.console import Console

import unrealmate.adapters.assets.asset_duplicates_adapter as duplicates_adapter_module
from unrealmate.adapters.assets.asset_duplicates_adapter import AssetDuplicatesAdapter
from unrealmate.adapters.presenters.asset_presenter_utils import render_asset_warnings
from unrealmate.contracts.asset_domain_common import (
    ASSET_SKIP_PATTERNS_BASE,
    format_signal_details,
)
from unrealmate.contracts.asset_domain_policy import (
    ASSET_DOMAIN_POLICY_VERSION,
    ASSET_DUPLICATES_CODES,
    ASSET_ORGANIZE_CODES,
    ASSET_SCAN_CODES,
    DEFAULT_ASSET_DUPLICATES_POLICY,
    DEFAULT_ASSET_ORGANIZE_POLICY,
    DEFAULT_ASSET_SCAN_POLICY,
    canonical_asset_code,
    is_known_asset_code,
    normalize_asset_code,
)
from unrealmate.contracts.asset_duplicates import (
    AssetDuplicatesPolicy,
    AssetDuplicatesRequest,
    DEFAULT_ASSET_DUPLICATE_SKIP_PATTERNS,
)
from unrealmate.contracts.asset_organize import (
    AssetOrganizePolicy,
    AssetOrganizeRequest,
    DEFAULT_ASSET_ORGANIZE_SKIP_PATTERNS,
)
from unrealmate.contracts.asset_scan import AssetScanPolicy, AssetScanRequest


def test_asset_domain_requests_share_path_normalization(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "AssetDomainPathNormalization"
    root.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(root)

    scan_request = AssetScanRequest.from_cli(".")
    duplicates_request = AssetDuplicatesRequest.from_cli(".")
    organize_request = AssetOrganizeRequest.from_cli(".")

    assert scan_request.scan_path == root.resolve()
    assert duplicates_request.scan_path == root.resolve()
    assert organize_request.scan_path == root.resolve()


def test_asset_domain_skip_baseline_is_consistent(tmp_path: Path) -> None:
    assert set(DEFAULT_ASSET_DUPLICATE_SKIP_PATTERNS) == set(ASSET_SKIP_PATTERNS_BASE)
    assert set(DEFAULT_ASSET_ORGANIZE_SKIP_PATTERNS) == set(ASSET_SKIP_PATTERNS_BASE)

    scan_request = AssetScanRequest.from_cli(str(tmp_path))
    duplicates_request = AssetDuplicatesRequest.from_cli(str(tmp_path))
    organize_request = AssetOrganizeRequest.from_cli(str(tmp_path))

    assert set(duplicates_request.skip_patterns) == set(organize_request.skip_patterns)
    assert set(scan_request.skip_patterns).issuperset(set(duplicates_request.skip_patterns))
    assert "binaries" in scan_request.skip_patterns
    assert "deriveddatacache" in scan_request.skip_patterns


def test_asset_domain_policy_models_align_with_capability_defaults() -> None:
    scan_policy = AssetScanPolicy()
    duplicates_policy = AssetDuplicatesPolicy()
    organize_policy = AssetOrganizePolicy()

    assert scan_policy.details_format == DEFAULT_ASSET_SCAN_POLICY.details_format
    assert duplicates_policy.details_format == DEFAULT_ASSET_DUPLICATES_POLICY.details_format
    assert organize_policy.details_format == DEFAULT_ASSET_ORGANIZE_POLICY.details_format
    assert scan_policy.detailed_assets_limit == DEFAULT_ASSET_SCAN_POLICY.detailed_assets_limit
    assert duplicates_policy.grouping_mode == DEFAULT_ASSET_DUPLICATES_POLICY.grouping_mode
    assert organize_policy.placement_mode == DEFAULT_ASSET_ORGANIZE_POLICY.placement_mode
    assert ASSET_DOMAIN_POLICY_VERSION == "phase1-policy-extraction-v1"


def test_asset_domain_details_formatting_is_deterministic() -> None:
    details = format_signal_details(
        error="denied",
        stage="walk",
        error_type="PermissionError",
        custom="value",
    )
    assert details == "stage=walk; error_type=PermissionError; error=denied; custom=value"


def test_asset_domain_code_vocabulary_is_known_and_canonicalized() -> None:
    emitted_codes = [
        ASSET_SCAN_CODES["path_not_found"],
        ASSET_SCAN_CODES["path_not_directory"],
        ASSET_SCAN_CODES["path_unreadable"],
        ASSET_DUPLICATES_CODES["path_not_found"],
        ASSET_DUPLICATES_CODES["scan_failed"],
        ASSET_DUPLICATES_CODES["scan_partial_failed"],
        ASSET_ORGANIZE_CODES["path_not_found"],
        ASSET_ORGANIZE_CODES["scan_partial_failed"],
        ASSET_ORGANIZE_CODES["no_data"],
    ]

    for code in emitted_codes:
        assert is_known_asset_code(code) is True
        assert canonical_asset_code(code).startswith("asset.")

    assert normalize_asset_code("duplicate_scan_failed_partial") == "duplicate_scan_partial_failed"
    assert canonical_asset_code("duplicate_scan_failed_partial") == "asset.duplicates.scan_partial_failed"


def test_asset_duplicates_partial_scan_uses_aligned_warning_code(
    tmp_path: Path,
    monkeypatch,
) -> None:
    scan_root = tmp_path / "PartialWarningProject"
    scan_root.mkdir(parents=True, exist_ok=True)
    (scan_root / "A.png").write_bytes(b"SAME")
    (scan_root / "B.png").write_bytes(b"SAME")

    adapter = AssetDuplicatesAdapter()
    original_walk = duplicates_adapter_module.os.walk

    def _walk_with_partial_failure(path, onerror=None):  # type: ignore[no-untyped-def]
        if onerror is not None:
            onerror(PermissionError(13, "denied", str(Path(path) / "Restricted")))
        yield str(Path(path).resolve()), [], ["A.png", "B.png"]

    monkeypatch.setattr(duplicates_adapter_module.os, "walk", _walk_with_partial_failure)
    result = adapter.find_duplicates(AssetDuplicatesRequest.from_cli(str(scan_root), by_content=True))

    warning_codes = [warning.code for warning in result.warnings]
    assert "duplicate_scan_partial_failed" in warning_codes
    assert ASSET_DUPLICATES_CODES["scan_failed"] not in warning_codes
    monkeypatch.setattr(duplicates_adapter_module.os, "walk", original_walk)


def test_asset_duplicates_request_policy_grouping_alignment(tmp_path: Path) -> None:
    request = AssetDuplicatesRequest.from_cli(str(tmp_path), grouping_mode="content")
    assert request.grouping_mode == "content"
    assert request.by_content is True


def test_asset_presenter_warning_helper_is_deterministic() -> None:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, color_system=None, width=120)

    warnings = [
        type("Signal", (), {"code": "z_code", "message": "Z", "source": "x", "details": "2"})(),
        type("Signal", (), {"code": "a_code", "message": "A", "source": "x", "details": "1"})(),
    ]

    render_asset_warnings(console=console, warnings=warnings, bullet="*")
    output = stream.getvalue()

    assert output.find("* A (x)") < output.find("* Z (x)")
