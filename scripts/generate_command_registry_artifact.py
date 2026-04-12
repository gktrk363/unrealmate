# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Generate Command Registry Artifact
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

#!/usr/bin/env python
"""Generate deterministic JSON artifact from canonical command registry."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from unrealmate.registry import (  # noqa: E402
    assert_registry_valid,
    check_registry_cli_parity,
    default_registry_path,
    load_command_registry,
)
from unrealmate.registry.artifact import (  # noqa: E402
    canonical_json,
    build_registry_artifact_payload,
    build_registry_manifest_payload,
    default_artifact_path,
    default_manifest_path,
    sha256_bytes,
)


def _sync_file(path: Path, expected_content: str, check_only: bool) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == expected_content:
        return False
    if check_only:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected_content, encoding="utf-8")
    return True


def _artifact_path_for_manifest(path: Path) -> Path:
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def _build_payloads(artifact_path: Path) -> tuple[str, str]:
    registry = load_command_registry()
    parity = check_registry_cli_parity(registry=registry, strict=True)
    assert_registry_valid(registry=registry, parity_report=parity)

    registry_checksum = sha256_bytes(default_registry_path().read_bytes())
    artifact_payload = build_registry_artifact_payload(
        registry=registry,
        parity_report=parity,
        registry_checksum=registry_checksum,
    )
    artifact_json = canonical_json(artifact_payload)
    artifact_checksum = sha256_bytes(artifact_json.encode("utf-8"))
    manifest_payload = build_registry_manifest_payload(
        registry=registry,
        artifact_path=_artifact_path_for_manifest(artifact_path),
        artifact_checksum=artifact_checksum,
        registry_checksum=registry_checksum,
    )
    manifest_json = canonical_json(manifest_payload)
    return artifact_json, manifest_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate command registry JSON artifact and manifest.")
    parser.add_argument(
        "--output",
        type=Path,
        default=default_artifact_path(ROOT),
        help="Artifact JSON output path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=default_manifest_path(ROOT),
        help="Artifact manifest output path.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if artifact/manifest are not up-to-date without writing files.",
    )
    args = parser.parse_args()

    output_path = args.output.resolve()
    manifest_path = args.manifest.resolve()
    artifact_json, manifest_json = _build_payloads(artifact_path=output_path)

    changed_paths: list[Path] = []
    if _sync_file(output_path, artifact_json, check_only=args.check):
        changed_paths.append(output_path)
    if _sync_file(manifest_path, manifest_json, check_only=args.check):
        changed_paths.append(manifest_path)

    if args.check and changed_paths:
        print("Command registry artifacts are out of date. Run:")
        cmd = f"python scripts/generate_command_registry_artifact.py --output {output_path} --manifest {manifest_path}"
        print(cmd)
        for path in changed_paths:
            print(f"- {path}")
        return 1

    if changed_paths:
        print("Updated command registry artifacts:")
        for path in changed_paths:
            print(f"- {path}")
    else:
        print("Command registry artifacts are already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
