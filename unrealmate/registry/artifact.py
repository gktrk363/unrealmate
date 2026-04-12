# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Artifact
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Helpers for generating deterministic command registry artifacts."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from unrealmate.registry.models import CommandEntry, CommandRegistry
from unrealmate.registry.parity import ParityReport


ARTIFACT_SCHEMA_VERSION = 1
DEFAULT_ARTIFACT_RELATIVE_PATH = Path("unrealmate/registry/generated/command_registry.json")
DEFAULT_MANIFEST_RELATIVE_PATH = Path("unrealmate/registry/generated/command_registry.manifest.json")


def default_artifact_path(root: Path) -> Path:
    """Return default JSON artifact path for a given repository root."""
    return root / DEFAULT_ARTIFACT_RELATIVE_PATH


def default_manifest_path(root: Path) -> Path:
    """Return default manifest path for a given repository root."""
    return root / DEFAULT_MANIFEST_RELATIVE_PATH


def sha256_bytes(payload: bytes) -> str:
    """Return stable SHA256 checksum hex for bytes payload."""
    return hashlib.sha256(payload).hexdigest()


def canonical_json(payload: dict[str, Any]) -> str:
    """Serialize JSON with deterministic formatting and key order."""
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def serialize_command_entry(entry: CommandEntry) -> dict[str, Any]:
    """Normalize command entry into client-agnostic JSON payload."""
    return {
        "command_group": entry.command_group,
        "subcommand": entry.subcommand,
        "full_command": entry.full_command,
        "aliases": sorted(entry.aliases),
        "maturity": entry.maturity.value,
        "status": entry.status.value,
        "visibility": entry.visibility.value,
        "destructive": entry.destructive,
        "supports_dry_run": entry.supports_dry_run,
        "requires_project_path": entry.requires_project_path,
        "requires_fixture_or_external_dependency": entry.requires_fixture_or_external_dependency,
        "local_only": entry.local_only,
        "category": entry.category,
        "short_help": entry.short_help,
        "long_help_source": entry.long_help_source,
        "docs_included": entry.docs_included,
        "completion_included": entry.completion_included,
        "default_help_included": entry.default_help_included,
        "deprecation_state": entry.deprecation_state.value,
        "replacement_command": entry.replacement_command,
        "owner_module": entry.owner_module,
        "notes": entry.notes,
        "external_dependencies": sorted(entry.external_dependencies),
        "smoke_test_tier": entry.smoke_test_tier.value,
        "source_refs": sorted(entry.source_refs),
        "introduced_in": entry.introduced_in,
    }


def build_registry_artifact_payload(
    registry: CommandRegistry,
    parity_report: ParityReport,
    registry_checksum: str,
) -> dict[str, Any]:
    """Build deterministic artifact payload from typed registry."""
    commands = [
        serialize_command_entry(entry)
        for entry in sorted(
            registry.commands,
            key=lambda item: (item.command_group, item.subcommand, item.full_command),
        )
    ]
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "registry": {
            "version": registry.meta.version,
            "source": registry.meta.source,
            "coverage": registry.meta.coverage,
            "checksum_sha256": registry_checksum,
        },
        "parity": {
            "registry_count": parity_report.registry_count,
            "cli_count": parity_report.cli_count,
            "is_full_match": parity_report.is_full_match,
        },
        "command_count": len(commands),
        "commands": commands,
    }


def _source_date_epoch_iso8601() -> str | None:
    """Return SOURCE_DATE_EPOCH as ISO8601 UTC timestamp when available."""
    raw_epoch = os.getenv("SOURCE_DATE_EPOCH")
    if raw_epoch is None:
        return None
    try:
        epoch = int(raw_epoch)
    except ValueError:
        return None

    dt = datetime.fromtimestamp(epoch, tz=timezone.utc).replace(microsecond=0)
    return dt.isoformat().replace("+00:00", "Z")


def build_registry_manifest_payload(
    registry: CommandRegistry,
    artifact_path: Path,
    artifact_checksum: str,
    registry_checksum: str,
) -> dict[str, Any]:
    """Build deterministic manifest payload for client consumption and CI checks."""
    generated_at = _source_date_epoch_iso8601()
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "registry_version": registry.meta.version,
        "source": registry.meta.source,
        "artifact_path": artifact_path.as_posix(),
        "command_count": len(registry.commands),
        "checksum_sha256": artifact_checksum,
        "registry_checksum_sha256": registry_checksum,
        "generated_at": generated_at,
    }
