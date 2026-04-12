# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Performance Profiler Core
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Core analysis tests for performance profiler without rendering concerns."""

from __future__ import annotations

import inspect
from pathlib import Path

from unrealmate.core.performance import profiler as profiler_module
from unrealmate.core.performance.profiler import (
    PerformanceProfiler,
    ProfilerAnalysisResult,
    ProfilingParseIssue,
)


def test_profiler_core_no_longer_exposes_legacy_renderer() -> None:
    assert not hasattr(PerformanceProfiler, "generate_report")


def test_profiler_analyze_reports_returns_structured_parse_issues(tmp_path: Path) -> None:
    project = tmp_path / "CoreProfilerProject"
    profiling = project / "Saved" / "Profiling"
    profiling.mkdir(parents=True, exist_ok=True)

    valid_csv = profiling / "valid_metrics.csv"
    valid_csv.write_text("Name,Value,Unit\nFrameTime,17.1,ms\n", encoding="utf-8")

    partial_csv = profiling / "partial_metrics.csv"
    partial_csv.write_text(
        "Name,Value,Unit\nDrawCalls,110,count\nBrokenMetric,not-a-number,ms\n",
        encoding="utf-8",
    )

    profiler = PerformanceProfiler(project)
    analysis = profiler.analyze_csv_reports([valid_csv.resolve(), partial_csv.resolve()])

    assert isinstance(analysis, ProfilerAnalysisResult)
    assert len(analysis.metrics) == 2
    assert isinstance(analysis.parse_issues, list)
    assert all(isinstance(issue, ProfilingParseIssue) for issue in analysis.parse_issues)
    assert any(issue.code == "row_invalid_value" for issue in analysis.parse_issues)
    assert isinstance(analysis.bottlenecks, list)


def test_profiler_analysis_is_deterministic_for_same_input(tmp_path: Path) -> None:
    project = tmp_path / "DeterministicCoreProject"
    profiling = project / "Saved" / "Profiling"
    profiling.mkdir(parents=True, exist_ok=True)
    report = profiling / "metrics.csv"
    report.write_text(
        "Name,Value,Unit\nCPUFrame,17.1,ms\nBrokenMetric,not-a-number,ms\n",
        encoding="utf-8",
    )

    profiler = PerformanceProfiler(project)
    first = profiler.analyze_csv_reports([report.resolve()])
    second = profiler.analyze_csv_reports([report.resolve()])

    assert [metric.__dict__ for metric in first.metrics] == [metric.__dict__ for metric in second.metrics]
    assert [bottleneck.__dict__ for bottleneck in first.bottlenecks] == [
        bottleneck.__dict__ for bottleneck in second.bottlenecks
    ]
    assert [issue.__dict__ for issue in first.parse_issues] == [issue.__dict__ for issue in second.parse_issues]
    assert first.parse_warning == second.parse_warning


def test_profiler_parse_issue_state_does_not_leak_between_calls(tmp_path: Path) -> None:
    project = tmp_path / "NoLeakCoreProject"
    profiling = project / "Saved" / "Profiling"
    profiling.mkdir(parents=True, exist_ok=True)

    bad_report = profiling / "bad.csv"
    bad_report.write_text("Name,Value,Unit\nBrokenMetric,not-a-number,ms\n", encoding="utf-8")
    good_report = profiling / "good.csv"
    good_report.write_text("Name,Value,Unit\nCPUFrame,12.0,ms\n", encoding="utf-8")

    profiler = PerformanceProfiler(project)

    first = profiler.analyze_csv_reports([bad_report.resolve()])
    assert len(first.parse_issues) == 1

    second = profiler.analyze_csv_reports([good_report.resolve()])
    assert second.parse_issues == []
    assert second.parse_warning.issue_count == 0
    assert second.parse_warning.metric_count == 1


def test_profiler_analyze_reports_compatibility_wrapper(tmp_path: Path) -> None:
    project = tmp_path / "CompatWrapperProject"
    profiling = project / "Saved" / "Profiling"
    profiling.mkdir(parents=True, exist_ok=True)
    csv_file = profiling / "metrics.csv"
    csv_file.write_text("Name,Value,Unit\nCPUFrame,20,ms\n", encoding="utf-8")

    profiler = PerformanceProfiler(project)
    analysis = profiler.analyze_csv_reports([csv_file.resolve()])
    metrics, bottlenecks, parse_issues = profiler.analyze_reports([csv_file.resolve()])

    assert metrics == analysis.metrics
    assert bottlenecks == analysis.bottlenecks
    assert parse_issues == analysis.parse_issues


def test_profiler_module_has_no_rich_render_imports() -> None:
    source = inspect.getsource(profiler_module)
    assert "rich.console" not in source
    assert "rich.table" not in source
    assert "generate_report(" not in source
