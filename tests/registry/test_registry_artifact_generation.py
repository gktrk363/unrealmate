# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Registry Artifact Generation
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Tests for command registry artifact generation script."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from unrealmate.registry import load_command_registry
from unrealmate.registry.artifact import sha256_bytes


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "generate_command_registry_artifact.py"


def _run_generator(output_path: Path, manifest_path: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCRIPT_PATH),
        "--output",
        str(output_path),
        "--manifest",
        str(manifest_path),
    ]
    if check:
        command.append("--check")
    return subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)


def test_artifact_generation_writes_json_and_manifest(tmp_path: Path) -> None:
    output_path = tmp_path / "command_registry.json"
    manifest_path = tmp_path / "command_registry.manifest.json"

    proc = _run_generator(output_path=output_path, manifest_path=manifest_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert output_path.exists()
    assert manifest_path.exists()

    registry = load_command_registry()
    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["registry"]["version"] == registry.meta.version
    assert artifact["registry"]["source"] == registry.meta.source
    assert artifact["command_count"] == len(registry.commands)
    assert len(artifact["commands"]) == len(registry.commands)
    assert artifact["parity"]["is_full_match"] is True
    assert artifact["parity"]["registry_count"] == artifact["parity"]["cli_count"]

    assert manifest["schema_version"] == 1
    assert manifest["registry_version"] == registry.meta.version
    assert manifest["source"] == registry.meta.source
    assert manifest["command_count"] == len(registry.commands)
    assert manifest["artifact_path"] == output_path.as_posix()
    assert manifest["generated_at"] is None


def test_artifact_serializes_visibility_maturity_and_status_fields(tmp_path: Path) -> None:
    output_path = tmp_path / "command_registry.json"
    manifest_path = tmp_path / "command_registry.manifest.json"

    proc = _run_generator(output_path=output_path, manifest_path=manifest_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    by_command = {item["full_command"]: item for item in artifact["commands"]}

    version = by_command["unrealmate version"]
    doctor = by_command["unrealmate doctor"]
    marketplace_install = by_command["unrealmate marketplace install"]
    report_notify = by_command["unrealmate report notify"]

    assert version["maturity"] == "stable"
    assert version["status"] == "production-ready"
    assert version["visibility"] == "default"
    assert version["default_help_included"] is True
    assert version["completion_included"] is True

    assert doctor["maturity"] == "stable"
    assert doctor["status"] == "risky"
    assert doctor["visibility"] == "default"

    assert marketplace_install["maturity"] == "mock"
    assert marketplace_install["status"] == "partially-implemented"
    assert marketplace_install["visibility"] == "opt-in"
    assert marketplace_install["default_help_included"] is False

    assert report_notify["maturity"] == "local-only"
    assert report_notify["local_only"] is True
    assert report_notify["destructive"] is True
    assert report_notify["smoke_test_tier"] == "none"


def test_artifact_manifest_checksum_matches_artifact_content(tmp_path: Path) -> None:
    output_path = tmp_path / "command_registry.json"
    manifest_path = tmp_path / "command_registry.manifest.json"

    proc = _run_generator(output_path=output_path, manifest_path=manifest_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    artifact_text = output_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["checksum_sha256"] == sha256_bytes(artifact_text.encode("utf-8"))


def test_artifact_generator_check_mode_passes_when_up_to_date(tmp_path: Path) -> None:
    output_path = tmp_path / "command_registry.json"
    manifest_path = tmp_path / "command_registry.manifest.json"

    first = _run_generator(output_path=output_path, manifest_path=manifest_path)
    assert first.returncode == 0, first.stdout + first.stderr

    second = _run_generator(output_path=output_path, manifest_path=manifest_path, check=True)
    assert second.returncode == 0, second.stdout + second.stderr
    assert "already up to date" in second.stdout.lower()


def test_artifact_generator_check_mode_detects_stale_artifact(tmp_path: Path) -> None:
    output_path = tmp_path / "command_registry.json"
    manifest_path = tmp_path / "command_registry.manifest.json"

    proc = _run_generator(output_path=output_path, manifest_path=manifest_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    stale = json.loads(output_path.read_text(encoding="utf-8"))
    stale["command_count"] = stale["command_count"] - 1
    output_path.write_text(json.dumps(stale, indent=2) + "\n", encoding="utf-8")

    check_proc = _run_generator(output_path=output_path, manifest_path=manifest_path, check=True)
    assert check_proc.returncode == 1
    assert "out of date" in check_proc.stdout.lower()
    assert str(output_path) in check_proc.stdout
