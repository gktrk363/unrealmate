# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Performance Profile Policy
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Threshold/config extraction tests for performance profile capability."""

from __future__ import annotations

from pathlib import Path

from unrealmate.contracts.performance_profile import (
    PerformanceBottleneckThresholdPolicy,
    PerformanceParseWarningPolicy,
    PerformanceProfilePolicy,
    PerformanceProfileRequest,
    PerformanceSeverityThresholdPolicy,
)
from unrealmate.core.application.use_cases.analyze_performance_profile import (
    AnalyzePerformanceProfileUseCase,
)


def _create_project_with_csv(tmp_path: Path, rows: list[str], name: str) -> Path:
    project = tmp_path / name
    profiling = project / "Saved" / "Profiling"
    profiling.mkdir(parents=True, exist_ok=True)
    content = "\n".join(["Name,Value,Unit", *rows]) + "\n"
    (profiling / "metrics.csv").write_text(content, encoding="utf-8")
    return project


def _metric_by_name(result, name: str):
    for metric in result.metrics:
        if metric.name == name:
            return metric
    raise AssertionError(f"metric not found: {name}")


def test_default_threshold_policy_preserves_baseline_classification(tmp_path: Path) -> None:
    project = _create_project_with_csv(tmp_path, ["CPUFrame,20,ms"], name="DefaultPolicyProject")
    use_case = AnalyzePerformanceProfileUseCase()
    request = PerformanceProfileRequest.from_cli(str(project))

    result = use_case.execute(request)
    metric = _metric_by_name(result, "CPUFrame")

    assert metric.severity == "Warning"
    assert result.bottlenecks == []


def test_custom_severity_policy_changes_metric_classification(tmp_path: Path) -> None:
    project = _create_project_with_csv(tmp_path, ["CPUFrame,20,ms"], name="CustomSeverityProject")
    use_case = AnalyzePerformanceProfileUseCase()
    custom_policy = PerformanceProfilePolicy(
        severity=PerformanceSeverityThresholdPolicy(
            frame_time_warning_ms=8.0,
            frame_time_critical_ms=15.0,
            memory_warning_mb=2000.0,
            memory_critical_mb=4000.0,
        )
    )
    request = PerformanceProfileRequest.from_cli(str(project), policy=custom_policy)

    result = use_case.execute(request)
    metric = _metric_by_name(result, "CPUFrame")

    assert metric.severity == "Critical"
    assert any(bottleneck.location == "CPU" for bottleneck in result.bottlenecks)


def test_custom_bottleneck_threshold_policy_changes_detection(tmp_path: Path) -> None:
    project = _create_project_with_csv(tmp_path, ["CPUFrame,40,ms"], name="CustomBottleneckProject")
    use_case = AnalyzePerformanceProfileUseCase()

    default_request = PerformanceProfileRequest.from_cli(str(project))
    default_result = use_case.execute(default_request)
    assert any(bottleneck.location == "CPU" for bottleneck in default_result.bottlenecks)

    strict_policy = PerformanceProfilePolicy(
        bottleneck=PerformanceBottleneckThresholdPolicy(
            min_critical_cpu_metrics=2,
            min_critical_gpu_metrics=1,
            min_critical_memory_metrics=1,
        )
    )
    strict_request = PerformanceProfileRequest.from_cli(str(project), policy=strict_policy)
    strict_result = use_case.execute(strict_request)

    assert strict_result.bottlenecks == []


def test_request_policy_payload_is_deterministic(tmp_path: Path) -> None:
    project = _create_project_with_csv(tmp_path, ["CPUFrame,20,ms"], name="PayloadProject")
    policy = PerformanceProfilePolicy(
        severity=PerformanceSeverityThresholdPolicy(
            frame_time_warning_ms=10.0,
            frame_time_critical_ms=30.0,
            memory_warning_mb=1000.0,
            memory_critical_mb=2500.0,
        ),
        bottleneck=PerformanceBottleneckThresholdPolicy(
            min_critical_cpu_metrics=1,
            min_critical_gpu_metrics=2,
            min_critical_memory_metrics=3,
        ),
        parse=PerformanceParseWarningPolicy(
            partial_parse_min_issues=2,
            partial_parse_min_issue_ratio=0.4,
            emit_no_metrics_warning=False,
        ),
    )
    request = PerformanceProfileRequest.from_cli(str(project), policy=policy)

    assert request.to_payload() == {
        "project_path": str(project.resolve()),
        "profiling_glob": "Saved/Profiling/*.csv",
        "max_metrics": None,
        "policy": {
            "severity": {
                "frame_time_warning_ms": 10.0,
                "frame_time_critical_ms": 30.0,
                "memory_warning_mb": 1000.0,
                "memory_critical_mb": 2500.0,
            },
            "bottleneck": {
                "min_critical_cpu_metrics": 1,
                "min_critical_gpu_metrics": 2,
                "min_critical_memory_metrics": 3,
            },
            "parse": {
                "partial_parse_min_issues": 2,
                "partial_parse_min_issue_ratio": 0.4,
                "emit_no_metrics_warning": False,
            },
        },
    }


def test_parse_warning_policy_controls_partial_parse_signal(tmp_path: Path) -> None:
    project = _create_project_with_csv(
        tmp_path,
        ["CPUFrame,16,ms", "BrokenMetric,not-a-number,ms"],
        name="ParsePolicyProject",
    )
    use_case = AnalyzePerformanceProfileUseCase()

    default_request = PerformanceProfileRequest.from_cli(str(project))
    default_result = use_case.execute(default_request)
    assert any(warning.code == "partial_parse" for warning in default_result.warnings)

    strict_parse_policy = PerformanceProfilePolicy(
        parse=PerformanceParseWarningPolicy(
            partial_parse_min_issues=2,
            partial_parse_min_issue_ratio=0.6,
            emit_no_metrics_warning=True,
        )
    )
    strict_request = PerformanceProfileRequest.from_cli(str(project), policy=strict_parse_policy)
    strict_result = use_case.execute(strict_request)
    strict_warning_codes = {warning.code for warning in strict_result.warnings}

    assert "csv_parse_error" in strict_warning_codes
    assert "partial_parse" not in strict_warning_codes
