# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Json Use Case
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Contract and use-case tests for report json extraction slice."""

from __future__ import annotations

import json
from pathlib import Path

from unrealmate.contracts.report_json import ReportJsonRequest
from unrealmate.core.application.use_cases.generate_json_report import (
    GenerateJsonReportUseCase,
)


def _create_project(project_path: Path, with_uproject: bool = True) -> Path:
    project_path.mkdir(parents=True, exist_ok=True)
    if with_uproject:
        (project_path / "ReportGame.uproject").write_text(
            json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
            encoding="utf-8",
        )
    (project_path / "Source").mkdir(parents=True, exist_ok=True)
    (project_path / "Source" / "Game.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
    (project_path / "Source" / "Game.h").write_text("#pragma once\n", encoding="utf-8")
    (project_path / "Content").mkdir(parents=True, exist_ok=True)
    (project_path / "Content" / "BP_Test.uasset").write_bytes(b"ASSET")
    (project_path / "Content" / "Map_Test.umap").write_bytes(b"MAP")
    return project_path


def test_report_json_request_normalizes_relative_path_and_output(tmp_path: Path, monkeypatch) -> None:
    cwd = tmp_path / "cwd"
    cwd.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(cwd)

    request = ReportJsonRequest.from_cli(path=".", output="out/report.json")

    assert request.project_path == cwd.resolve()
    assert request.output_path == (cwd / "out" / "report.json").resolve()


def test_report_json_use_case_invalid_path_returns_structured_error(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    use_case = GenerateJsonReportUseCase()
    request = ReportJsonRequest.from_cli(path=str(missing), generated_at_iso_override="2026-04-03T00:00:00")

    result = use_case.execute(request)

    assert result.is_success is False
    assert result.errors[0].code == "report_json_path_not_found"
    assert result.errors[0].source == str(missing.resolve())


def test_report_json_use_case_not_directory_returns_structured_error(tmp_path: Path) -> None:
    not_directory = tmp_path / "file.txt"
    not_directory.write_text("x", encoding="utf-8")
    use_case = GenerateJsonReportUseCase()

    result = use_case.execute(
        ReportJsonRequest.from_cli(path=str(not_directory), generated_at_iso_override="2026-04-03T00:00:00")
    )

    assert result.is_success is False
    assert result.errors[0].code == "report_json_not_directory"
    assert result.errors[0].source == str(not_directory.resolve())


def test_report_json_use_case_missing_uproject_emits_warning(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "NoUproject", with_uproject=False)
    use_case = GenerateJsonReportUseCase()
    result = use_case.execute(
        ReportJsonRequest.from_cli(path=str(project), generated_at_iso_override="2026-04-03T00:00:00")
    )

    assert result.is_success is True
    warning_codes = [warning.code for warning in result.warnings]
    assert "report_json_project_missing" in warning_codes
    assert result.project_name == project.name


def test_report_json_use_case_extracts_basic_stats(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "ValidProject", with_uproject=True)
    use_case = GenerateJsonReportUseCase()
    result = use_case.execute(
        ReportJsonRequest.from_cli(path=str(project), generated_at_iso_override="2026-04-03T00:00:00")
    )

    assert result.is_success is True
    assert result.stats.uproject_files == 1
    assert result.stats.cpp_source_files == 2
    assert result.stats.blueprint_assets == 1
    assert result.stats.scene_maps == 1
    assert result.project_name == "ReportGame"
