# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build İnfo Use Case
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Contract and use-case tests for build info extraction slice."""

from __future__ import annotations

import json
from pathlib import Path

from unrealmate.contracts.build_info import BuildInfoRequest
from unrealmate.core.application.use_cases.get_build_info import GetBuildInfoUseCase


def _write_uproject(project_path: Path, payload: dict[str, object], name: str = "BuildInfoProject") -> Path:
    project_path.mkdir(parents=True, exist_ok=True)
    uproject_path = project_path / f"{name}.uproject"
    uproject_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return uproject_path


def test_build_info_request_normalizes_relative_cli_path(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "RequestProject"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(project)

    request = BuildInfoRequest.from_cli(".")

    assert request.project_path == project.resolve()
    assert request.project_path.is_absolute()


def test_build_info_use_case_invalid_path_returns_structured_error(tmp_path: Path) -> None:
    missing = tmp_path / "MissingProject"
    use_case = GetBuildInfoUseCase()
    request = BuildInfoRequest.from_cli(str(missing))

    result = use_case.execute(request)

    assert result.is_success is False
    assert result.errors[0].code == "build_info_path_not_found"
    assert result.errors[0].source == str(missing.resolve())


def test_build_info_use_case_not_directory_returns_structured_error(tmp_path: Path) -> None:
    file_path = tmp_path / "not_a_directory.txt"
    file_path.write_text("x", encoding="utf-8")

    use_case = GetBuildInfoUseCase()
    request = BuildInfoRequest.from_cli(str(file_path))
    result = use_case.execute(request)

    assert result.is_success is False
    assert result.errors[0].code == "build_info_not_directory"
    assert result.errors[0].source == str(file_path.resolve())


def test_build_info_use_case_missing_uproject_returns_structured_error(tmp_path: Path) -> None:
    project = tmp_path / "NoUprojectProject"
    project.mkdir(parents=True, exist_ok=True)
    use_case = GetBuildInfoUseCase()
    request = BuildInfoRequest.from_cli(str(project))

    result = use_case.execute(request)

    assert result.is_success is False
    assert result.has_data is False
    assert result.errors[0].code == "build_info_project_missing"
    assert result.errors[0].source == str(project.resolve())


def test_build_info_use_case_returns_structured_metadata_payload(tmp_path: Path) -> None:
    project = tmp_path / "ValidProject"
    _write_uproject(
        project,
        {
            "FileVersion": 3,
            "EngineAssociation": "5.4",
            "Category": "Games",
            "Description": "Build info extraction test project",
            "Plugins": [{"Name": "BasePlugin", "Enabled": True}],
        },
        name="SmokeProject",
    )
    use_case = GetBuildInfoUseCase()
    request = BuildInfoRequest.from_cli(str(project))

    result = use_case.execute(request)

    assert result.is_success is True
    assert result.has_data is True
    assert result.errors == []
    assert result.metadata is not None
    assert result.metadata.project_name == "SmokeProject"
    assert result.metadata.engine_version == "5.4"
    assert result.metadata.plugin_count == 1

    payload = result.to_payload()
    assert set(payload.keys()) == {"project_path", "metadata", "environment", "warnings", "errors"}
    assert payload["project_path"] == str(project.resolve())
    assert payload["metadata"]["project_name"] == "SmokeProject"
    assert payload["metadata"]["engine_version"] == "5.4"
    assert payload["metadata"]["plugin_count"] == 1

