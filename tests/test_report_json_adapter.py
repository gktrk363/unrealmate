# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Json Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter tests for report json extraction slice."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from unrealmate.adapters.report.report_json_adapter import ReportJsonAdapter
from unrealmate.contracts.report_json import ReportJsonRequest


def _create_project(project_path: Path, with_uproject: bool = True) -> Path:
    project_path.mkdir(parents=True, exist_ok=True)
    if with_uproject:
        (project_path / "AdapterGame.uproject").write_text(
            json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
            encoding="utf-8",
        )
    (project_path / "Source").mkdir(parents=True, exist_ok=True)
    (project_path / "Source" / "Core.cpp").write_text("int x = 1;\n", encoding="utf-8")
    (project_path / "Source" / "Core.h").write_text("#pragma once\n", encoding="utf-8")
    (project_path / "Content").mkdir(parents=True, exist_ok=True)
    (project_path / "Content" / "AssetA.uasset").write_bytes(b"A")
    (project_path / "Content" / "MapA.umap").write_bytes(b"B")
    return project_path


def test_adapter_generates_output_artifact_created_then_updated(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "ArtifactProject")
    output_path = tmp_path / "out" / "report.json"
    fixed_time = datetime.fromisoformat("2026-04-03T10:20:30")
    adapter = ReportJsonAdapter(now_provider=lambda: fixed_time)

    first = adapter.collect(ReportJsonRequest.from_cli(path=str(project), output=str(output_path)))
    second = adapter.collect(ReportJsonRequest.from_cli(path=str(project), output=str(output_path)))

    assert first.is_success is True
    assert first.artifacts[0].status == "created"
    assert first.artifacts[0].bytes_written > 0
    assert output_path.exists()
    assert second.artifacts[0].status == "updated"


def test_adapter_emits_config_unavailable_warning(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "ConfigWarningProject")

    def _broken_loader(_project_path):
        raise RuntimeError("config loader unavailable")

    adapter = ReportJsonAdapter(
        config_loader=_broken_loader,
        now_provider=lambda: datetime.fromisoformat("2026-04-03T10:00:00"),
    )
    result = adapter.collect(ReportJsonRequest.from_cli(path=str(project)))

    assert result.is_success is True
    assert result.config_snapshot is None
    warning_codes = [warning.code for warning in result.warnings]
    assert "report_json_config_unavailable" in warning_codes


def test_adapter_write_failure_is_structured(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "WriteFailureProject")
    blocked_parent = tmp_path / "not_a_directory"
    blocked_parent.write_text("blocking file", encoding="utf-8")
    output_path = blocked_parent / "report.json"
    adapter = ReportJsonAdapter(now_provider=lambda: datetime.fromisoformat("2026-04-03T10:00:00"))

    result = adapter.collect(ReportJsonRequest.from_cli(path=str(project), output=str(output_path)))

    assert result.is_success is False
    assert result.artifacts[0].status == "failed"
    assert result.errors[0].code == "report_json_write_failed"


def test_adapter_partial_stats_warning_is_structured(tmp_path: Path, monkeypatch) -> None:
    project = _create_project(tmp_path / "PartialStatsProject")
    adapter = ReportJsonAdapter(now_provider=lambda: datetime.fromisoformat("2026-04-03T10:00:00"))
    original_count_pattern = adapter._collector._count_pattern

    def _patched_count_pattern(project_path: Path, pattern: str) -> int:
        if pattern == "*.umap":
            raise PermissionError("denied")
        return original_count_pattern(project_path, pattern)

    monkeypatch.setattr(adapter._collector, "_count_pattern", _patched_count_pattern)
    result = adapter.collect(ReportJsonRequest.from_cli(path=str(project)))

    assert result.is_success is True
    assert result.stats.scene_maps == 0
    warning_codes = [warning.code for warning in result.warnings]
    assert "report_json_partial_stats" in warning_codes
