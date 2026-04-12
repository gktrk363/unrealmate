# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Performance Profile Presenter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Presenter tests for performance profile terminal rendering."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from rich.console import Console

from unrealmate.adapters.presenters.cli_performance_profile_presenter import (
    render_performance_profile_result,
)
from unrealmate.contracts.performance_profile import (
    PerformanceBottleneckResult,
    PerformanceMetricResult,
    PerformanceProfileResult,
    PerformanceProfileWarning,
)


def _build_console_buffer() -> tuple[Console, StringIO]:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, color_system=None, width=120)
    return console, stream


def _build_result(tmp_path: Path, metric_count: int = 0) -> PerformanceProfileResult:
    profiling_dir = (tmp_path / "Saved" / "Profiling").resolve()
    project_path = tmp_path.resolve()
    metrics = [
        PerformanceMetricResult(
            name=f"Metric{index:02d}",
            value=float(index + 1),
            unit="ms",
            category="Other",
            severity="OK",
        )
        for index in range(metric_count)
    ]
    return PerformanceProfileResult(
        project_path=project_path,
        profiling_dir=profiling_dir,
        data_sources=[(profiling_dir / "metrics.csv").resolve()],
        metrics=metrics,
        bottlenecks=[
            PerformanceBottleneckResult(
                location="CPU",
                issue="1 critical CPU metrics detected",
                impact="High",
                suggestion="Optimize game thread hotspots",
            )
        ]
        if metric_count
        else [],
        warnings=[],
    )


def test_presenter_show_all_false_keeps_truncation_signal(tmp_path: Path) -> None:
    result = _build_result(tmp_path, metric_count=25)
    console, stream = _build_console_buffer()

    render_performance_profile_result(result=result, console=console, show_all=False)
    output = stream.getvalue()

    assert "Showing first 20 of 25 metrics. Use --all to show all." in output
    assert "Metric Window" in output
    assert "Metric24" not in output
    assert "Metric00" in output


def test_presenter_show_all_true_displays_full_metric_set(tmp_path: Path) -> None:
    result = _build_result(tmp_path, metric_count=25)
    console, stream = _build_console_buffer()

    render_performance_profile_result(result=result, console=console, show_all=True)
    output = stream.getvalue()

    assert "Showing first 20 of 25 metrics. Use --all to show all." not in output
    assert "Metric24" in output


def test_presenter_warning_details_are_opt_in_with_show_all(tmp_path: Path) -> None:
    result = _build_result(tmp_path, metric_count=1)
    warning = PerformanceProfileWarning(
        code="partial_parse",
        message="Some profiling rows could not be parsed; results may be incomplete.",
        source=str((tmp_path / "Saved" / "Profiling").resolve()),
        details="issues=1; parsed_metrics=1; reports=1",
    )
    result_with_warning = PerformanceProfileResult(
        project_path=result.project_path,
        profiling_dir=result.profiling_dir,
        data_sources=result.data_sources,
        metrics=result.metrics,
        bottlenecks=result.bottlenecks,
        warnings=[warning],
    )

    default_console, default_stream = _build_console_buffer()
    render_performance_profile_result(
        result=result_with_warning,
        console=default_console,
        show_all=False,
    )
    default_output = default_stream.getvalue()
    assert "Analysis Warnings" in default_output
    assert "issues=1; parsed_metrics=1; reports=1" not in default_output

    all_console, all_stream = _build_console_buffer()
    render_performance_profile_result(
        result=result_with_warning,
        console=all_console,
        show_all=True,
    )
    all_output = all_stream.getvalue()
    assert "issues=1; parsed_metrics=1; reports=1" in all_output


def test_presenter_no_data_messages_are_stable(tmp_path: Path) -> None:
    result = PerformanceProfileResult(
        project_path=tmp_path.resolve(),
        profiling_dir=(tmp_path / "Saved" / "Profiling").resolve(),
    )
    console, stream = _build_console_buffer()

    render_performance_profile_result(result=result, console=console, show_all=False)
    output = stream.getvalue()

    assert "Performance Analysis" in output
    assert "No Performance Metrics" in output
    assert "No performance metrics found." in output
    assert "No critical bottlenecks detected!" in output
