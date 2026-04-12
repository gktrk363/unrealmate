# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Html Contract Snapshots
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Structured payload snapshots for report html extraction slice."""

from __future__ import annotations

import json
from pathlib import Path

from unrealmate.contracts.report_html import ReportHtmlRequest
from unrealmate.core.application.use_cases.generate_html_report import (
    GenerateHtmlReportUseCase,
)


def _create_project(project_path: Path, with_uproject: bool = True) -> Path:
    project_path.mkdir(parents=True, exist_ok=True)
    if with_uproject:
        (project_path / "SnapshotHtmlGame.uproject").write_text(
            json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
            encoding="utf-8",
        )
    (project_path / "Source").mkdir(parents=True, exist_ok=True)
    (project_path / "Source" / "Game.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
    (project_path / "Source" / "Game.h").write_text("#pragma once\n", encoding="utf-8")
    (project_path / "Content").mkdir(parents=True, exist_ok=True)
    (project_path / "Content" / "BP_Test.uasset").write_bytes(b"UASSET")
    (project_path / "Content" / "Map_Test.umap").write_bytes(b"UMAP")
    (project_path / "Scripts").mkdir(parents=True, exist_ok=True)
    (project_path / "Scripts" / "helper.py").write_text("print('helper')\n", encoding="utf-8")
    return project_path


def test_report_html_payload_snapshot_for_normal_result(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "SnapshotProject", with_uproject=True)
    output_path = tmp_path / "out" / "report.html"
    use_case = GenerateHtmlReportUseCase()

    result = use_case.execute(
        ReportHtmlRequest.from_cli(
            path=str(project),
            output=str(output_path),
            include_config=False,
            generated_at_iso_override="2026-04-03T12:34:56",
        )
    )
    payload = result.to_payload()

    assert payload["project_name"] == "SnapshotHtmlGame"
    assert payload["project_path"] == str(project.resolve())
    assert payload["generated_at_iso"] == "2026-04-03T12:34:56"
    assert payload["stats"] == {
        "uproject_files": 1,
        "cpp_source_files": 2,
        "blueprint_assets": 1,
        "scene_maps": 1,
    }
    assert payload["python_script_count"] == 1
    assert payload["config_snapshot"] is None
    assert payload["warnings"] == []
    assert payload["errors"] == []
    assert len(payload["artifacts"]) == 1
    assert payload["artifacts"][0]["kind"] == "html"
    assert payload["artifacts"][0]["path"] == str(output_path.resolve())
    assert payload["artifacts"][0]["status"] == "created"
    assert payload["artifacts"][0]["content_type"] == "text/html"
    assert payload["artifacts"][0]["bytes_written"] > 0


def test_report_html_payload_snapshot_for_missing_project_file(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "NoUProjectSnapshot", with_uproject=False)
    use_case = GenerateHtmlReportUseCase()
    result = use_case.execute(
        ReportHtmlRequest.from_cli(
            path=str(project),
            include_config=False,
            generated_at_iso_override="2026-04-03T09:00:00",
        )
    )

    assert result.to_payload() == {
        "project_name": "NoUProjectSnapshot",
        "project_path": str(project.resolve()),
        "generated_at_iso": "2026-04-03T09:00:00",
        "stats": {
            "uproject_files": 0,
            "cpp_source_files": 2,
            "blueprint_assets": 1,
            "scene_maps": 1,
        },
        "config_snapshot": None,
        "python_script_count": 1,
        "artifacts": [
            {
                "kind": "html",
                "path": str((project / "unrealmate_report.html").resolve()),
                "status": "created",
                "bytes_written": result.artifacts[0].bytes_written,
                "content_type": "text/html",
            }
        ],
        "warnings": [
            {
                "code": "report_html_project_missing",
                "message": "No .uproject file found; using folder name as project identifier.",
                "source": str(project.resolve()),
                "details": None,
            }
        ],
        "errors": [],
    }
