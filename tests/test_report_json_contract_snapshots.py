# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Json Contract Snapshots
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Structured payload snapshots for report json extraction slice."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from unrealmate.adapters.report.report_json_adapter import ReportJsonAdapter
from unrealmate.contracts.report_json import ReportJsonRequest
from unrealmate.core.application.use_cases.generate_json_report import (
    GenerateJsonReportUseCase,
)


def _create_project(project_path: Path, with_uproject: bool = True) -> Path:
    project_path.mkdir(parents=True, exist_ok=True)
    if with_uproject:
        (project_path / "SnapshotGame.uproject").write_text(
            json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
            encoding="utf-8",
        )
    (project_path / "Source").mkdir(parents=True, exist_ok=True)
    (project_path / "Source" / "Game.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
    (project_path / "Source" / "Game.h").write_text("#pragma once\n", encoding="utf-8")
    (project_path / "Content").mkdir(parents=True, exist_ok=True)
    (project_path / "Content" / "BP_Test.uasset").write_bytes(b"UASSET")
    (project_path / "Content" / "Map_Test.umap").write_bytes(b"UMAP")
    return project_path


def test_report_json_payload_snapshot_for_normal_result(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "SnapshotProject", with_uproject=True)
    use_case = GenerateJsonReportUseCase()

    result = use_case.execute(
        ReportJsonRequest.from_cli(
            path=str(project),
            include_config=False,
            generated_at_iso_override="2026-04-03T12:34:56",
        )
    )

    assert result.to_payload() == {
        "project_name": "SnapshotGame",
        "project_path": str(project.resolve()),
        "generated_at_iso": "2026-04-03T12:34:56",
        "stats": {
            "uproject_files": 1,
            "cpp_source_files": 2,
            "blueprint_assets": 1,
            "scene_maps": 1,
        },
        "config_snapshot": None,
        "artifacts": [],
        "warnings": [],
        "errors": [],
    }


def test_report_json_payload_snapshot_for_missing_project_file(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "NoUProjectSnapshot", with_uproject=False)
    adapter = ReportJsonAdapter(
        config_loader=lambda _path: None,
        now_provider=lambda: datetime.fromisoformat("2026-04-03T09:00:00"),
    )
    use_case = GenerateJsonReportUseCase(adapter=adapter)
    result = use_case.execute(ReportJsonRequest.from_cli(path=str(project)))

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
        "artifacts": [],
        "warnings": [
            {
                "code": "report_json_config_unavailable",
                "message": "Configuration snapshot could not be loaded; report will continue without config.",
                "source": str(project.resolve()),
                "details": "operation=config_snapshot; error_type=TypeError; error=asdict() should be called on dataclass instances",
            },
            {
                "code": "report_json_project_missing",
                "message": "No .uproject file found; using folder name as project identifier.",
                "source": str(project.resolve()),
                "details": None,
            },
        ],
        "errors": [],
    }
