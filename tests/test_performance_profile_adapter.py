# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Performance Profile Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter hardening tests for performance profile capability."""

from __future__ import annotations

import builtins
from pathlib import Path

from unrealmate.adapters.performance.profiler_adapter import PerformanceProfilerAdapter
from unrealmate.contracts.performance_profile import PerformanceProfileRequest


def _create_project(tmp_path: Path, name: str = "AdapterProject") -> Path:
    project = tmp_path / name
    (project / "Saved" / "Profiling").mkdir(parents=True, exist_ok=True)
    return project


def _write_csv(csv_path: Path, content: str) -> Path:
    csv_path.write_text(content, encoding="utf-8")
    return csv_path


def test_adapter_collects_multi_source_reports_in_deterministic_order(tmp_path: Path) -> None:
    project = _create_project(tmp_path, name="MultiSourceProject")
    profiling = project / "Saved" / "Profiling"
    _write_csv(profiling / "z_metrics.csv", "Name,Value,Unit\nFrameTime,14.0,ms\n")
    _write_csv(profiling / "a_metrics.csv", "Name,Value,Unit\nDrawCalls,90,count\n")

    adapter = PerformanceProfilerAdapter()
    request = PerformanceProfileRequest.from_cli(str(project))
    result = adapter.analyze(request)

    assert result.has_data is True
    assert [path.name for path in result.data_sources] == ["a_metrics.csv", "z_metrics.csv"]
    assert {metric.name for metric in result.metrics} == {"FrameTime", "DrawCalls"}
    assert all(warning.code != "profiling_data_missing" for warning in result.warnings)


def test_adapter_partial_parse_emits_parse_and_partial_warnings(tmp_path: Path) -> None:
    project = _create_project(tmp_path, name="PartialParseProject")
    profiling = project / "Saved" / "Profiling"
    _write_csv(
        profiling / "metrics.csv",
        "Name,Value,Unit\nFrameTime,15.0,ms\nBadMetric,not-a-number,ms\n",
    )

    adapter = PerformanceProfilerAdapter()
    request = PerformanceProfileRequest.from_cli(str(project))
    result = adapter.analyze(request)

    warning_codes = [warning.code for warning in result.warnings]
    assert "csv_parse_error" in warning_codes
    assert "partial_parse" in warning_codes
    assert "no_metrics_parsed" not in warning_codes

    parse_warning = next(warning for warning in result.warnings if warning.code == "csv_parse_error")
    assert parse_warning.source == str((profiling / "metrics.csv").resolve())
    assert parse_warning.details is not None
    assert "issue_code=row_invalid_value" in parse_warning.details
    assert "row=3" in parse_warning.details

    partial_warning = next(warning for warning in result.warnings if warning.code == "partial_parse")
    assert partial_warning.details == "issues=1; parsed_metrics=1; reports=1"


def test_adapter_parse_warning_details_are_deterministic(tmp_path: Path) -> None:
    project = _create_project(tmp_path, name="DeterministicWarningProject")
    profiling = project / "Saved" / "Profiling"
    _write_csv(
        profiling / "metrics.csv",
        "Name,Value,Unit\n,10,ms\nMetricA,bad,ms\nMetricB,2,ms\n",
    )

    adapter = PerformanceProfilerAdapter()
    request = PerformanceProfileRequest.from_cli(str(project))
    result = adapter.analyze(request)

    parse_warnings = [warning for warning in result.warnings if warning.code == "csv_parse_error"]
    assert len(parse_warnings) == 2
    assert [warning.source for warning in parse_warnings] == [
        str((profiling / "metrics.csv").resolve()),
        str((profiling / "metrics.csv").resolve()),
    ]
    assert parse_warnings[0].details == (
        "issue_code=row_missing_name; row=2; message=CSV row is missing Name value."
    )
    assert parse_warnings[1].details == (
        "issue_code=row_invalid_value; row=3; message=CSV row Value is not numeric.; raw_value=bad"
    )


def test_adapter_empty_glob_falls_back_to_default_discovery(tmp_path: Path) -> None:
    project = _create_project(tmp_path, name="EmptyGlobProject")
    profiling = project / "Saved" / "Profiling"
    _write_csv(profiling / "metrics.csv", "Name,Value,Unit\nFrameTime,12.5,ms\n")

    adapter = PerformanceProfilerAdapter()
    request = PerformanceProfileRequest.from_cli(str(project), profiling_glob="")
    result = adapter.analyze(request)

    assert result.has_data is True
    assert len(result.data_sources) == 1
    assert all(warning.code != "profiling_glob_invalid" for warning in result.warnings)


def test_adapter_invalid_glob_returns_warning_without_crashing(tmp_path: Path) -> None:
    project = _create_project(tmp_path, name="BadGlobProject")
    adapter = PerformanceProfilerAdapter()
    request = PerformanceProfileRequest.from_cli(str(project), profiling_glob="[invalid")

    result = adapter.analyze(request)

    warning_codes = [warning.code for warning in result.warnings]
    assert warning_codes[0] == "profiling_glob_invalid"
    assert warning_codes[1] == "profiling_data_missing"
    assert result.has_data is False
    assert result.warnings[0].source == "[invalid"


def test_adapter_read_failure_is_normalized_as_parse_warning(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = _create_project(tmp_path, name="ReadFailureProject")
    csv_path = _write_csv(
        project / "Saved" / "Profiling" / "metrics.csv",
        "Name,Value,Unit\nFrameTime,16.0,ms\n",
    )

    real_open = builtins.open

    def _failing_open(file, *args, **kwargs):  # type: ignore[no-untyped-def]
        if Path(file).resolve() == csv_path.resolve():
            raise PermissionError("denied")
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr("builtins.open", _failing_open)

    adapter = PerformanceProfilerAdapter()
    request = PerformanceProfileRequest.from_cli(str(project))
    result = adapter.analyze(request)

    warning_codes = [warning.code for warning in result.warnings]
    assert "csv_parse_error" in warning_codes
    assert "no_metrics_parsed" in warning_codes
    parse_warning = next(warning for warning in result.warnings if warning.code == "csv_parse_error")
    assert parse_warning.details is not None
    assert "issue_code=read_failed" in parse_warning.details
    assert "PermissionError" in parse_warning.details
