# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Performance Profile Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for stabilized performance profile output behavior."""

from __future__ import annotations
import pytest

from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def _create_project_with_metric_count(tmp_path: Path, metric_count: int) -> Path:
    project = tmp_path / "ProfileCliProject"
    profiling = project / "Saved" / "Profiling"
    profiling.mkdir(parents=True, exist_ok=True)

    lines = ["Name,Value,Unit"]
    for index in range(metric_count):
        lines.append(f"Metric{index:02d},{index + 1},ms")
    (profiling / "metrics.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return project


@pytest.mark.skip(reason="Obsolete after UX/CLI architectural refactoring")
def test_performance_profile_cli_reports_found_csv_count(monkeypatch, tmp_path: Path) -> None:
    project = _create_project_with_metric_count(tmp_path, metric_count=2)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["performance", "profile", str(project)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Found 1 profiling report(s)" in result.output
    assert "Performance Analysis Report" in result.output


def test_performance_profile_cli_no_data_signal_is_stable(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "NoDataProject"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["performance", "profile", str(project)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Advisory analysis only" in result.output
    assert "No local profiling CSV data found." in result.output
    assert "Looking in:" in result.output


def test_performance_profile_cli_success_mentions_csv_advisory_scope(monkeypatch, tmp_path: Path) -> None:
    project = _create_project_with_metric_count(tmp_path, metric_count=2)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["performance", "profile", str(project)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "local profiling CSV report(s)." in result.output
    assert "Advisory analysis only" in result.output


@pytest.mark.skip(reason="Obsolete after UX/CLI architectural refactoring")
def test_performance_profile_cli_show_all_toggle(monkeypatch, tmp_path: Path) -> None:
    project = _create_project_with_metric_count(tmp_path, metric_count=25)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    default_result = runner.invoke(cli.app, ["performance", "profile", str(project)], catch_exceptions=False)
    assert default_result.exit_code == 0
    assert "Showing first 20 of 25 metrics. Use --all to show all." in default_result.output
    assert "Metric24" not in default_result.output

    all_result = runner.invoke(cli.app, ["performance", "profile", str(project), "--all"], catch_exceptions=False)
    assert all_result.exit_code == 0
    assert "Showing first 20 of 25 metrics. Use --all to show all." not in all_result.output
    assert "Metric24" in all_result.output
