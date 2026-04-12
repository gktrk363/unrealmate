# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Performance Profile Use Case
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Contract and use-case tests for performance profile extraction slice."""

from __future__ import annotations

from pathlib import Path

from unrealmate.contracts.performance_profile import PerformanceProfileRequest
from unrealmate.core.application.use_cases.analyze_performance_profile import (
    AnalyzePerformanceProfileUseCase,
)


def _create_project_with_csv(tmp_path: Path) -> Path:
    project = tmp_path / "ContractProject"
    profiling = project / "Saved" / "Profiling"
    profiling.mkdir(parents=True, exist_ok=True)
    (profiling / "frame_metrics.csv").write_text(
        "Name,Value,Unit\nFrameTime,16.5,ms\nDrawCalls,120,count\n",
        encoding="utf-8",
    )
    return project


def test_performance_profile_request_normalizes_relative_cli_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = _create_project_with_csv(tmp_path)
    monkeypatch.chdir(project)

    request = PerformanceProfileRequest.from_cli(".")

    assert request.project_path == project.resolve()
    assert request.project_path.is_absolute()
    assert request.profiling_glob == "Saved/Profiling/*.csv"


def test_use_case_returns_structured_result_shape_for_valid_csv_data(tmp_path: Path) -> None:
    project = _create_project_with_csv(tmp_path)
    use_case = AnalyzePerformanceProfileUseCase()
    request = PerformanceProfileRequest.from_cli(str(project))

    result = use_case.execute(request)

    assert result.is_success is True
    assert result.has_data is True
    assert len(result.data_sources) == 1
    assert len(result.metrics) >= 2
    assert result.errors == []

    payload = result.to_payload()
    assert set(payload.keys()) == {
        "project_path",
        "profiling_dir",
        "data_sources",
        "metrics",
        "bottlenecks",
        "warnings",
        "errors",
    }
    assert payload["data_sources"][0].endswith("frame_metrics.csv")
    assert all("category" in metric for metric in payload["metrics"])
    assert all("severity" in metric for metric in payload["metrics"])


def test_use_case_payload_snapshot_for_valid_csv_data(tmp_path: Path) -> None:
    project = _create_project_with_csv(tmp_path)
    use_case = AnalyzePerformanceProfileUseCase()
    request = PerformanceProfileRequest.from_cli(str(project))
    result = use_case.execute(request)

    assert result.to_payload() == {
        "project_path": str(project.resolve()),
        "profiling_dir": str((project / "Saved" / "Profiling").resolve()),
        "data_sources": [str((project / "Saved" / "Profiling" / "frame_metrics.csv").resolve())],
        "metrics": [
            {
                "name": "DrawCalls",
                "value": 120.0,
                "unit": "count",
                "category": "GPU",
                "severity": "OK",
            },
            {
                "name": "FrameTime",
                "value": 16.5,
                "unit": "ms",
                "category": "Other",
                "severity": "OK",
            },
        ],
        "bottlenecks": [],
        "warnings": [],
        "errors": [],
    }


def test_use_case_returns_structured_warning_when_no_csv_data(tmp_path: Path) -> None:
    project = tmp_path / "NoCsvProject"
    project.mkdir(parents=True, exist_ok=True)
    use_case = AnalyzePerformanceProfileUseCase()
    request = PerformanceProfileRequest.from_cli(str(project))

    result = use_case.execute(request)

    assert result.is_success is True
    assert result.has_data is False
    assert result.errors == []
    assert any(warning.code == "profiling_data_missing" for warning in result.warnings)


def test_use_case_payload_snapshot_for_no_data(tmp_path: Path) -> None:
    project = tmp_path / "NoCsvProject"
    project.mkdir(parents=True, exist_ok=True)

    use_case = AnalyzePerformanceProfileUseCase()
    request = PerformanceProfileRequest.from_cli(str(project))
    result = use_case.execute(request)

    assert result.to_payload() == {
        "project_path": str(project.resolve()),
        "profiling_dir": str((project / "Saved" / "Profiling").resolve()),
        "data_sources": [],
        "metrics": [],
        "bottlenecks": [],
        "warnings": [
            {
                "code": "profiling_data_missing",
                "message": "No profiling CSV reports found.",
                "source": str((project / "Saved" / "Profiling").resolve()),
                "details": "reports=0",
            }
        ],
        "errors": [],
    }


def test_use_case_surfaces_parse_issues_as_structured_warnings(tmp_path: Path) -> None:
    project = tmp_path / "BadCsvProject"
    profiling = project / "Saved" / "Profiling"
    profiling.mkdir(parents=True, exist_ok=True)
    (profiling / "broken_metrics.csv").write_bytes(b"\xff\xfe\xfd")

    use_case = AnalyzePerformanceProfileUseCase()
    request = PerformanceProfileRequest.from_cli(str(project))
    result = use_case.execute(request)

    warning_codes = {warning.code for warning in result.warnings}
    assert "csv_parse_error" in warning_codes
    assert "no_metrics_parsed" in warning_codes
    assert result.errors == []


def test_use_case_payload_snapshot_for_parse_warning_shape(tmp_path: Path) -> None:
    project = tmp_path / "BadCsvProject"
    profiling = project / "Saved" / "Profiling"
    profiling.mkdir(parents=True, exist_ok=True)
    broken_csv = profiling / "broken_metrics.csv"
    broken_csv.write_bytes(b"\xff\xfe\xfd")

    use_case = AnalyzePerformanceProfileUseCase()
    request = PerformanceProfileRequest.from_cli(str(project))
    result = use_case.execute(request)
    payload = result.to_payload()

    assert payload["project_path"] == str(project.resolve())
    assert payload["profiling_dir"] == str(profiling.resolve())
    assert payload["data_sources"] == [str(broken_csv.resolve())]
    assert payload["metrics"] == []
    assert payload["bottlenecks"] == []
    assert payload["errors"] == []
    assert payload["warnings"][0] == {
        "code": "csv_parse_error",
        "message": "Failed to parse CSV report.",
        "source": str(broken_csv.resolve()),
        "details": payload["warnings"][0]["details"],
    }
    assert payload["warnings"][1] == {
        "code": "no_metrics_parsed",
        "message": "Profiling files were found but no usable metrics were parsed.",
        "source": str(profiling.resolve()),
        "details": "reports=1; parse_issues=1",
    }
    assert isinstance(payload["warnings"][0]["details"], str)
    assert payload["warnings"][0]["details"]
