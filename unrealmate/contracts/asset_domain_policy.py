# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Asset Domain Policy
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Shared policy contracts and code alignment for asset domain capabilities."""

from __future__ import annotations

from dataclasses import dataclass, field

from unrealmate.contracts.asset_domain_common import (
    ASSET_SCAN_SKIP_PATTERNS,
    ASSET_SKIP_PATTERNS_BASE,
)


ASSET_DOMAIN_POLICY_VERSION = "phase1-policy-extraction-v1"
ASSET_DETAILS_FORMAT = "kv-v1"

SUPPORTED_ASSET_GROUPING_MODES: tuple[str, ...] = ("filename", "content")
SUPPORTED_ASSET_HASH_STRATEGIES: tuple[str, ...] = ("md5", "sha1", "sha256")
SUPPORTED_ASSET_ORGANIZE_PLACEMENT_MODES: tuple[str, ...] = ("by_extension",)


@dataclass(frozen=True)
class AssetScanCategoryPolicyEntry:
    name: str
    patterns: tuple[str, ...]
    uasset_classifier: str | None = None


@dataclass(frozen=True)
class AssetOrganizeRulePolicyEntry:
    category: str
    target_folder: str
    extensions: tuple[str, ...]


@dataclass(frozen=True)
class AssetScanPolicyDefaults:
    category_rules: tuple[AssetScanCategoryPolicyEntry, ...]
    skip_patterns: tuple[str, ...] = ASSET_SCAN_SKIP_PATTERNS
    detailed_assets_limit: int = 50
    largest_assets_limit: int = 5
    details_format: str = ASSET_DETAILS_FORMAT


@dataclass(frozen=True)
class AssetDuplicatesPolicyDefaults:
    grouping_mode: str = "filename"
    hash_strategy: str = "md5"
    asset_extensions: tuple[str, ...] = field(default_factory=tuple)
    skip_patterns: tuple[str, ...] = ASSET_SKIP_PATTERNS_BASE
    details_format: str = ASSET_DETAILS_FORMAT


@dataclass(frozen=True)
class AssetOrganizePolicyDefaults:
    placement_mode: str = "by_extension"
    rules: tuple[AssetOrganizeRulePolicyEntry, ...] = field(default_factory=tuple)
    skip_patterns: tuple[str, ...] = ASSET_SKIP_PATTERNS_BASE
    conflict_suffix_separator: str = "_"
    details_format: str = ASSET_DETAILS_FORMAT


DEFAULT_ASSET_DUPLICATE_EXTENSIONS: tuple[str, ...] = (
    ".png",
    ".tga",
    ".psd",
    ".exr",
    ".hdr",
    ".jpg",
    ".jpeg",
    ".wav",
    ".mp3",
    ".ogg",
    ".flac",
    ".fbx",
    ".obj",
    ".blend",
    ".mp4",
    ".mov",
    ".avi",
    ".uasset",
    ".umap",
    ".ttf",
    ".otf",
)

DEFAULT_ASSET_SCAN_POLICY = AssetScanPolicyDefaults(
    category_rules=(
        AssetScanCategoryPolicyEntry(name="Blueprints", patterns=("*.uasset",), uasset_classifier="blueprints"),
        AssetScanCategoryPolicyEntry(name="Maps", patterns=("*.umap",)),
        AssetScanCategoryPolicyEntry(name="Textures", patterns=("*.png", "*.tga", "*.psd", "*.exr", "*.hdr")),
        AssetScanCategoryPolicyEntry(name="Audio", patterns=("*.wav", "*.mp3", "*.ogg")),
        AssetScanCategoryPolicyEntry(name="3D Models", patterns=("*.fbx", "*.obj", "*.glTF", "*.glb")),
        AssetScanCategoryPolicyEntry(name="Materials", patterns=("*.uasset",), uasset_classifier="materials"),
        AssetScanCategoryPolicyEntry(name="Videos", patterns=("*.mp4", "*.mov", "*.avi")),
        AssetScanCategoryPolicyEntry(name="Source Code", patterns=("*.cpp", "*.h", "*.cs")),
        AssetScanCategoryPolicyEntry(name="Config", patterns=("*.ini",)),
    )
)

DEFAULT_ASSET_DUPLICATES_POLICY = AssetDuplicatesPolicyDefaults(
    grouping_mode="filename",
    hash_strategy="md5",
    asset_extensions=DEFAULT_ASSET_DUPLICATE_EXTENSIONS,
    skip_patterns=ASSET_SKIP_PATTERNS_BASE,
)

DEFAULT_ASSET_ORGANIZE_POLICY = AssetOrganizePolicyDefaults(
    placement_mode="by_extension",
    rules=(
        AssetOrganizeRulePolicyEntry(
            category="Textures",
            target_folder="Textures",
            extensions=(".png", ".tga", ".psd", ".exr", ".hdr", ".jpg", ".jpeg"),
        ),
        AssetOrganizeRulePolicyEntry(
            category="Audio",
            target_folder="Audio",
            extensions=(".wav", ".mp3", ".ogg", ".flac"),
        ),
        AssetOrganizeRulePolicyEntry(
            category="Models",
            target_folder="Models",
            extensions=(".fbx", ".obj", ".blend", ".3ds", ".dae"),
        ),
        AssetOrganizeRulePolicyEntry(
            category="Videos",
            target_folder="Videos",
            extensions=(".mp4", ".mov", ".avi", ".mkv", ".webm"),
        ),
        AssetOrganizeRulePolicyEntry(
            category="Fonts",
            target_folder="Fonts",
            extensions=(".ttf", ".otf", ".woff", ".woff2"),
        ),
        AssetOrganizeRulePolicyEntry(
            category="Data",
            target_folder="Data",
            extensions=(".json", ".csv", ".xml", ".ini"),
        ),
    ),
    skip_patterns=ASSET_SKIP_PATTERNS_BASE,
    conflict_suffix_separator="_",
)


ASSET_SCAN_CODES: dict[str, str] = {
    "path_not_found": "scan_path_not_found",
    "path_not_directory": "scan_path_not_directory",
    "path_unreadable": "scan_path_unreadable",
    "pattern_failed": "scan_pattern_failed",
    "stat_failed": "asset_stat_failed",
    "no_data": "no_assets_found",
}

ASSET_DUPLICATES_CODES: dict[str, str] = {
    "path_not_found": "duplicate_scan_path_not_found",
    "path_not_directory": "duplicate_scan_path_not_directory",
    "path_unreadable": "duplicate_scan_path_unreadable",
    "scan_failed": "duplicate_scan_failed",
    "scan_partial_failed": "duplicate_scan_partial_failed",
    "stat_failed": "duplicate_stat_failed",
    "no_data": "no_duplicates_found",
}

ASSET_ORGANIZE_CODES: dict[str, str] = {
    "path_not_found": "organize_path_not_found",
    "path_not_directory": "organize_path_not_directory",
    "path_unreadable": "organize_path_unreadable",
    "scan_partial_failed": "organize_scan_failed",
    "move_failed": "organize_move_failed",
    "conflict_detected": "organize_conflict_detected",
    "no_data": "organize_no_changes",
}


# Compatibility aliases for older/internal code tokens. Values resolve to emitted codes above.
ASSET_CODE_COMPATIBILITY_ALIASES: dict[str, str] = {
    "duplicate_scan_failed_partial": ASSET_DUPLICATES_CODES["scan_partial_failed"],
}


ASSET_CODE_CANONICAL_NAMES: dict[str, str] = {
    ASSET_SCAN_CODES["path_not_found"]: "asset.scan.path_not_found",
    ASSET_SCAN_CODES["path_not_directory"]: "asset.scan.path_not_directory",
    ASSET_SCAN_CODES["path_unreadable"]: "asset.scan.path_unreadable",
    ASSET_SCAN_CODES["pattern_failed"]: "asset.scan.pattern_failed",
    ASSET_SCAN_CODES["stat_failed"]: "asset.scan.stat_failed",
    ASSET_SCAN_CODES["no_data"]: "asset.scan.no_data",
    ASSET_DUPLICATES_CODES["path_not_found"]: "asset.duplicates.path_not_found",
    ASSET_DUPLICATES_CODES["path_not_directory"]: "asset.duplicates.path_not_directory",
    ASSET_DUPLICATES_CODES["path_unreadable"]: "asset.duplicates.path_unreadable",
    ASSET_DUPLICATES_CODES["scan_failed"]: "asset.duplicates.scan_failed",
    ASSET_DUPLICATES_CODES["scan_partial_failed"]: "asset.duplicates.scan_partial_failed",
    ASSET_DUPLICATES_CODES["stat_failed"]: "asset.duplicates.stat_failed",
    ASSET_DUPLICATES_CODES["no_data"]: "asset.duplicates.no_data",
    ASSET_ORGANIZE_CODES["path_not_found"]: "asset.organize.path_not_found",
    ASSET_ORGANIZE_CODES["path_not_directory"]: "asset.organize.path_not_directory",
    ASSET_ORGANIZE_CODES["path_unreadable"]: "asset.organize.path_unreadable",
    ASSET_ORGANIZE_CODES["scan_partial_failed"]: "asset.organize.scan_partial_failed",
    ASSET_ORGANIZE_CODES["move_failed"]: "asset.organize.move_failed",
    ASSET_ORGANIZE_CODES["conflict_detected"]: "asset.organize.conflict_detected",
    ASSET_ORGANIZE_CODES["no_data"]: "asset.organize.no_data",
}


def normalize_asset_code(code: str) -> str:
    """Normalize legacy code aliases to current emitted asset-domain code."""
    return ASSET_CODE_COMPATIBILITY_ALIASES.get(code, code)


def canonical_asset_code(code: str) -> str:
    """Return canonical dotted name for emitted/legacy asset-domain code."""
    normalized = normalize_asset_code(code)
    return ASSET_CODE_CANONICAL_NAMES.get(normalized, normalized)


def is_known_asset_code(code: str) -> bool:
    """Whether code exists in current asset-domain code vocabulary."""
    normalized = normalize_asset_code(code)
    return normalized in ASSET_CODE_CANONICAL_NAMES
