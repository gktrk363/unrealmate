# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Html Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter tests for report html extraction slice."""

from __future__ import annotations

import json
from pathlib import Path

import unrealmate.adapters.report.report_html_adapter as report_html_adapter_module
from unrealmate.adapters.report.report_html_adapter import ReportHtmlAdapter
from unrealmate.adapters.report.report_json_adapter import ReportJsonAdapter
from unrealmate.contracts.report_html import ReportHtmlRequest
from unrealmate.contracts.report_json import ReportJsonRequest


def _create_project(project_path: Path, with_uproject: bool = True) -> Path:
    project_path.mkdir(parents=True, exist_ok=True)
    if with_uproject:
        (project_path / "AdapterHtmlGame.uproject").write_text(
            json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
            encoding="utf-8",
        )
    (project_path / "Source").mkdir(parents=True, exist_ok=True)
    (project_path / "Source" / "Core.cpp").write_text("int x = 1;\n", encoding="utf-8")
    (project_path / "Source" / "Core.h").write_text("#pragma once\n", encoding="utf-8")
    (project_path / "Content").mkdir(parents=True, exist_ok=True)
    (project_path / "Content" / "AssetA.uasset").write_bytes(b"A")
    (project_path / "Content" / "MapA.umap").write_bytes(b"B")
    (project_path / "Scripts").mkdir(parents=True, exist_ok=True)
    (project_path / "Scripts" / "build.py").write_text("print('ok')\n", encoding="utf-8")
    return project_path


def test_adapter_generates_output_artifact_created_then_updated(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "ArtifactProject")
    output_path = tmp_path / "out" / "report.html"
    adapter = ReportHtmlAdapter()

    first = adapter.collect(
        ReportHtmlRequest.from_cli(
            path=str(project),
            output=str(output_path),
            include_config=False,
            generated_at_iso_override="2026-04-03T10:20:30",
        )
    )
    second = adapter.collect(
        ReportHtmlRequest.from_cli(
            path=str(project),
            output=str(output_path),
            include_config=False,
            generated_at_iso_override="2026-04-03T10:20:30",
        )
    )

    assert first.is_success is True
    assert first.artifacts[0].status == "created"
    assert first.artifacts[0].kind == "html"
    assert first.artifacts[0].content_type == "text/html"
    assert first.artifacts[0].bytes_written > 0
    assert output_path.exists()
    assert second.artifacts[0].status == "updated"
    html = output_path.read_text(encoding="utf-8")
    assert "<html" in html.lower()
    assert "Project Report" in html


def test_adapter_write_failure_is_structured(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "WriteFailureProject")
    blocked_parent = tmp_path / "not_a_directory"
    blocked_parent.write_text("blocking file", encoding="utf-8")
    output_path = blocked_parent / "report.html"
    adapter = ReportHtmlAdapter()

    result = adapter.collect(
        ReportHtmlRequest.from_cli(
            path=str(project),
            output=str(output_path),
            include_config=False,
            generated_at_iso_override="2026-04-03T10:00:00",
        )
    )

    assert result.is_success is False
    assert result.artifacts[0].status == "failed"
    assert result.errors[0].code == "report_html_write_failed"


def test_adapter_template_failure_is_structured(tmp_path: Path, monkeypatch) -> None:
    project = _create_project(tmp_path / "TemplateFailureProject")
    output_path = tmp_path / "out" / "report.html"
    adapter = ReportHtmlAdapter()
    original_renderer = report_html_adapter_module.render_report_html_document

    def _raise_template_failure(*_args, **_kwargs):
        raise ValueError("bad template")

    monkeypatch.setattr(report_html_adapter_module, "render_report_html_document", _raise_template_failure)

    try:
        result = adapter.collect(
            ReportHtmlRequest.from_cli(
                path=str(project),
                output=str(output_path),
                include_config=False,
                generated_at_iso_override="2026-04-03T10:00:00",
            )
        )
    finally:
        monkeypatch.setattr(report_html_adapter_module, "render_report_html_document", original_renderer)

    assert result.is_success is False
    assert result.errors[0].code == "report_html_template_failed"


def test_adapter_stats_are_aligned_with_report_json_core_payload(tmp_path: Path) -> None:
    project = _create_project(tmp_path / "SharedStatsProject")
    json_adapter = ReportJsonAdapter()
    html_adapter = ReportHtmlAdapter()
    generated = "2026-04-03T11:22:33"

    json_result = json_adapter.collect(
        ReportJsonRequest.from_cli(path=str(project), include_config=False, generated_at_iso_override=generated)
    )
    html_result = html_adapter.collect(
        ReportHtmlRequest.from_cli(path=str(project), include_config=False, generated_at_iso_override=generated)
    )

    assert html_result.project_name == json_result.project_name
    assert html_result.stats.to_payload() == json_result.stats.to_payload()
    assert html_result.generated_at_iso == json_result.generated_at_iso
