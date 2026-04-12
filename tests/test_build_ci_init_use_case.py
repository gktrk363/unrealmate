# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build Ci İnit Use Case
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Contract and use-case tests for build ci-init extraction slice."""

from __future__ import annotations

import json
from pathlib import Path

from unrealmate.contracts.build_ci_init import BuildCiInitRequest
from unrealmate.core.application.use_cases.initialize_build_ci import (
    InitializeBuildCiUseCase,
)


def _create_project(tmp_path: Path, with_uproject: bool = True) -> Path:
    project = tmp_path / "BuildCiUseCaseProject"
    project.mkdir(parents=True, exist_ok=True)
    if with_uproject:
        (project / "BuildCiUseCaseProject.uproject").write_text(
            json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
            encoding="utf-8",
        )
    return project


def test_build_ci_init_request_normalizes_cli_inputs(tmp_path: Path, monkeypatch) -> None:
    project = _create_project(tmp_path)
    monkeypatch.chdir(project)

    request = BuildCiInitRequest.from_cli(path=".", platform="GITHUB")

    assert request.project_path == project.resolve()
    assert request.platform == "github"
    assert request.preview_only is False
    assert request.selected_project_file is None
    assert request.selected_project_name is None
    assert request.selection_strategy == "alphabetical_first"


def test_build_ci_init_use_case_invalid_path_returns_structured_error(tmp_path: Path) -> None:
    missing = tmp_path / "MissingProject"
    use_case = InitializeBuildCiUseCase()
    request = BuildCiInitRequest.from_cli(path=str(missing), platform="github")

    result = use_case.execute(request)

    assert result.is_success is False
    assert result.errors[0].code == "build_ci_path_not_found"
    assert result.errors[0].source == str(missing.resolve())


def test_build_ci_init_use_case_not_directory_returns_structured_error(tmp_path: Path) -> None:
    file_path = tmp_path / "not_a_dir.txt"
    file_path.write_text("x", encoding="utf-8")

    use_case = InitializeBuildCiUseCase()
    request = BuildCiInitRequest.from_cli(path=str(file_path), platform="github")
    result = use_case.execute(request)

    assert result.is_success is False
    assert result.errors[0].code == "build_ci_not_directory"
    assert result.errors[0].source == str(file_path.resolve())


def test_build_ci_init_use_case_missing_uproject_returns_structured_error(tmp_path: Path) -> None:
    project = _create_project(tmp_path, with_uproject=False)
    use_case = InitializeBuildCiUseCase()
    request = BuildCiInitRequest.from_cli(path=str(project), platform="github")

    result = use_case.execute(request)

    assert result.is_success is False
    assert result.errors[0].code == "build_ci_project_missing"
    assert result.errors[0].source == str(project.resolve())


def test_build_ci_init_use_case_unsupported_platform_returns_structured_error(tmp_path: Path) -> None:
    project = _create_project(tmp_path, with_uproject=True)
    use_case = InitializeBuildCiUseCase()
    request = BuildCiInitRequest.from_cli(path=str(project), platform="azure")

    result = use_case.execute(request)

    assert result.is_success is False
    assert result.errors[0].code == "build_ci_provider_unsupported"
    assert result.errors[0].source == "azure"


def test_build_ci_init_use_case_resolves_real_uproject_name(tmp_path: Path) -> None:
    project = tmp_path / "FolderNameDifferentFromProject"
    project.mkdir(parents=True, exist_ok=True)
    (project / "RealGame.uproject").write_text(
        json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
        encoding="utf-8",
    )

    use_case = InitializeBuildCiUseCase()
    request = BuildCiInitRequest.from_cli(path=str(project), platform="github")
    result = use_case.execute(request)

    assert result.is_success is True
    assert result.selected_project_name == "RealGame"
    assert result.selected_project_file == (project / "RealGame.uproject").resolve()
    generated_file = project / ".github" / "workflows" / "unreal-build.yml"
    assert generated_file.exists()
    generated_text = generated_file.read_text(encoding="utf-8")
    assert "RealGame.uproject" in generated_text
    assert "FolderNameDifferentFromProject.uproject" not in generated_text


def test_build_ci_init_use_case_multiple_uproject_selection_is_deterministic(tmp_path: Path) -> None:
    project = tmp_path / "MultiProjectSelection"
    project.mkdir(parents=True, exist_ok=True)
    (project / "ZetaGame.uproject").write_text(
        json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
        encoding="utf-8",
    )
    (project / "AlphaGame.uproject").write_text(
        json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
        encoding="utf-8",
    )

    use_case = InitializeBuildCiUseCase()
    request = BuildCiInitRequest.from_cli(path=str(project), platform="gitlab")
    result = use_case.execute(request)

    assert result.is_success is True
    assert result.selected_project_name == "AlphaGame"
    assert result.selected_project_file == (project / "AlphaGame.uproject").resolve()
    warning_codes = [warning.code for warning in result.warnings]
    assert "build_ci_project_selection" in warning_codes
