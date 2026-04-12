# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build İnfo Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter tests for build info extraction slice."""

from __future__ import annotations

import json
from pathlib import Path

from unrealmate.adapters.build.build_info_adapter import BuildInfoAdapter
from unrealmate.contracts.build_info import BuildInfoRequest


def _write_uproject(project_path: Path, name: str, payload: dict[str, object]) -> Path:
    project_path.mkdir(parents=True, exist_ok=True)
    target = project_path / f"{name}.uproject"
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def test_adapter_extracts_metadata_and_environment_signals(tmp_path: Path) -> None:
    project = tmp_path / "AdapterBuildProject"
    _write_uproject(
        project,
        "AdapterProject",
        {
            "EngineAssociation": "5.5",
            "Category": "Games",
            "Description": "Adapter extraction fixture",
            "Plugins": [{"Name": "Core", "Enabled": True}, {"Name": "Tools", "Enabled": False}],
        },
    )
    (project / ".git").mkdir(parents=True, exist_ok=True)
    (project / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (project / "Plugins").mkdir(parents=True, exist_ok=True)

    adapter = BuildInfoAdapter()
    result = adapter.collect(BuildInfoRequest.from_cli(str(project)))

    assert result.is_success is True
    assert result.errors == []
    assert result.metadata is not None
    assert result.metadata.project_name == "AdapterProject"
    assert result.metadata.plugin_count == 2
    assert result.environment.has_git_repository is True
    assert result.environment.has_plugins_directory is True
    assert result.environment.ci_providers == ("github",)
    assert result.environment.detected_ci_files == (".github/workflows",)


def test_adapter_partial_metadata_warning_is_structured(tmp_path: Path) -> None:
    project = tmp_path / "PartialMetadataProject"
    _write_uproject(
        project,
        "PartialProject",
        {
            "FileVersion": 3,
        },
    )

    adapter = BuildInfoAdapter()
    result = adapter.collect(BuildInfoRequest.from_cli(str(project)))

    assert result.is_success is True
    assert result.metadata is not None
    assert result.metadata.engine_version == "Unknown"
    assert result.metadata.category == "N/A"
    assert result.metadata.description == "N/A"
    assert result.warnings
    warning_codes = [warning.code for warning in result.warnings]
    assert "build_info_partial_metadata" in warning_codes
    assert any("missing_fields=Category,Description,EngineAssociation" in (warning.details or "") for warning in result.warnings)


def test_adapter_invalid_json_returns_parse_error(tmp_path: Path) -> None:
    project = tmp_path / "InvalidJsonProject"
    project.mkdir(parents=True, exist_ok=True)
    broken = project / "BrokenProject.uproject"
    broken.write_text("{ invalid json", encoding="utf-8")

    adapter = BuildInfoAdapter()
    result = adapter.collect(BuildInfoRequest.from_cli(str(project)))

    assert result.is_success is False
    assert result.has_data is False
    assert result.errors[0].code == "build_info_parse_failed"
    assert result.errors[0].source == str(broken.resolve())


def test_adapter_multiple_projects_are_deterministic(tmp_path: Path) -> None:
    project = tmp_path / "MultiProject"
    _write_uproject(
        project,
        "ZetaProject",
        {
            "EngineAssociation": "5.4",
            "Category": "Games",
            "Description": "Zeta",
            "Plugins": [],
        },
    )
    _write_uproject(
        project,
        "AlphaProject",
        {
            "EngineAssociation": "5.3",
            "Category": "Games",
            "Description": "Alpha",
            "Plugins": [],
        },
    )

    adapter = BuildInfoAdapter()
    result = adapter.collect(BuildInfoRequest.from_cli(str(project)))

    assert result.metadata is not None
    assert result.metadata.project_name == "AlphaProject"
    assert result.warnings
    assert result.warnings[0].code == "build_info_partial_metadata"
    details = result.warnings[0].details or ""
    assert "project_path=" in details
    assert "project_file=" in details
    assert "project_name=AlphaProject" in details
    assert "selection_strategy=alphabetical_first" in details
    assert "selected_project_file=AlphaProject.uproject" in details
    assert "candidate_projects=AlphaProject.uproject,ZetaProject.uproject" in details
