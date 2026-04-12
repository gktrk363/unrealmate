# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build İnfo Contract Snapshots
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Structured payload snapshots for build info extraction slice."""

from __future__ import annotations

import json
from pathlib import Path

from unrealmate.contracts.build_info import BuildInfoRequest
from unrealmate.core.application.use_cases.get_build_info import GetBuildInfoUseCase


def _write_uproject(project_path: Path, name: str, payload: dict[str, object]) -> Path:
    project_path.mkdir(parents=True, exist_ok=True)
    target = project_path / f"{name}.uproject"
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def test_build_info_payload_snapshot_for_normal_result(tmp_path: Path) -> None:
    project = tmp_path / "SnapshotProject"
    uproject_path = _write_uproject(
        project,
        "SnapshotGame",
        {
            "EngineAssociation": "5.4",
            "Category": "Games",
            "Description": "Snapshot fixture",
            "Plugins": [{"Name": "BasePlugin", "Enabled": True}],
        },
    )

    use_case = GetBuildInfoUseCase()
    result = use_case.execute(BuildInfoRequest.from_cli(str(project)))

    assert result.to_payload() == {
        "project_path": str(project.resolve()),
        "metadata": {
            "project_name": "SnapshotGame",
            "project_file": str(uproject_path.resolve()),
            "engine_version": "5.4",
            "category": "Games",
            "description": "Snapshot fixture",
            "plugin_count": 1,
        },
        "environment": {
            "has_git_repository": False,
            "has_plugins_directory": False,
            "ci_providers": [],
            "detected_ci_files": [],
        },
        "warnings": [],
        "errors": [],
    }


def test_build_info_payload_snapshot_for_partial_metadata_result(tmp_path: Path) -> None:
    project = tmp_path / "PartialSnapshotProject"
    uproject_path = _write_uproject(
        project,
        "PartialSnapshot",
        {
            "FileVersion": 3,
            "Plugins": {"unexpected": True},
        },
    )

    use_case = GetBuildInfoUseCase()
    result = use_case.execute(BuildInfoRequest.from_cli(str(project)))
    payload = result.to_payload()

    assert payload["project_path"] == str(project.resolve())
    assert payload["metadata"] == {
        "project_name": "PartialSnapshot",
        "project_file": str(uproject_path.resolve()),
        "engine_version": "Unknown",
        "category": "N/A",
        "description": "N/A",
        "plugin_count": 0,
    }
    assert payload["environment"] == {
        "has_git_repository": False,
        "has_plugins_directory": False,
        "ci_providers": [],
        "detected_ci_files": [],
    }
    assert payload["errors"] == []
    assert len(payload["warnings"]) == 1
    assert payload["warnings"][0]["code"] == "build_info_partial_metadata"
    assert payload["warnings"][0]["source"] == str(uproject_path.resolve())
    assert payload["warnings"][0]["details"] == (
        f"project_path={project.resolve()}; "
        f"project_file={uproject_path.resolve()}; "
        "project_name=PartialSnapshot; "
        "missing_fields=Category,Description,EngineAssociation; "
        "invalid_field=Plugins; expected_type=list; actual_type=dict"
    )
