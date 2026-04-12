# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Core Collector
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Shared report core collector and code normalization tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from unrealmate.adapters.report.report_core import (
    ReportCoreCollector,
    error_code_for,
    format_report_details,
    warning_code_for,
)


def _create_project(project_path: Path, with_uproject: bool = True) -> Path:
    project_path.mkdir(parents=True, exist_ok=True)
    if with_uproject:
        (project_path / "CoreReportGame.uproject").write_text(
            json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
            encoding="utf-8",
        )
    (project_path / "Source").mkdir(parents=True, exist_ok=True)
    (project_path / "Source" / "Core.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
    (project_path / "Source" / "Core.h").write_text("#pragma once\n", encoding="utf-8")
    (project_path / "Content").mkdir(parents=True, exist_ok=True)
    (project_path / "Content" / "AssetA.uasset").write_bytes(b"A")
    (project_path / "Content" / "MapA.umap").write_bytes(b"B")
    return project_path


def test_shared_collector_is_consistent_for_same_input(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "ConsistentProject", with_uproject=True)
    collector = ReportCoreCollector(now_provider=lambda: datetime.fromisoformat("2026-04-03T10:00:00"))

    first = collector.collect(project_path=project, include_config=False)
    second = collector.collect(project_path=project, include_config=False)

    assert first.project_name == second.project_name
    assert first.project_path == second.project_path
    assert first.generated_at_iso == second.generated_at_iso
    assert first.stats.to_payload() == second.stats.to_payload()
    assert [warning.reason for warning in first.warnings] == [warning.reason for warning in second.warnings]


def test_warning_and_error_code_normalization_is_aligned() -> None:
    assert warning_code_for("json", "project_missing") == "report_json_project_missing"
    assert warning_code_for("html", "project_missing") == "report_html_project_missing"
    assert warning_code_for("json", "config_unavailable") == "report_json_config_unavailable"
    assert warning_code_for("html", "partial_stats") == "report_html_partial_stats"

    assert error_code_for("json", "write_failed") == "report_json_write_failed"
    assert error_code_for("html", "write_failed") == "report_html_write_failed"
    assert error_code_for("html", "template_failed") == "report_html_template_failed"


def test_format_report_details_is_deterministic() -> None:
    details = format_report_details(
        error="boom",
        operation="write_output",
        counter_key="stats",
        pattern="*.uasset",
        error_type="RuntimeError",
    )
    assert details == (
        "operation=write_output; pattern=*.uasset; counter_key=stats; "
        "error_type=RuntimeError; error=boom"
    )
