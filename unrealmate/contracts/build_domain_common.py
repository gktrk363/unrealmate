# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Build Domain Common
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Common build-domain normalization/detail helpers."""

from __future__ import annotations


_BUILD_DETAIL_KEY_ORDER: tuple[str, ...] = (
    "project_path",
    "project_file",
    "project_name",
    "platform",
    "selection_strategy",
    "selected_project_file",
    "selected_project_name",
    "candidate_projects",
    "stage",
    "status",
    "reason",
    "mode",
    "operation",
    "renderer",
    "missing_fields",
    "invalid_field",
    "expected_type",
    "actual_type",
    "error_type",
    "error",
)


def format_build_details(**fields: object) -> str:
    """Build deterministic details payload string for build-domain signals."""
    ordered_keys = [key for key in _BUILD_DETAIL_KEY_ORDER if key in fields]
    ordered_keys.extend(sorted(key for key in fields if key not in _BUILD_DETAIL_KEY_ORDER))
    return "; ".join(f"{key}={fields[key]}" for key in ordered_keys)

