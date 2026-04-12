# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Profiler Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter wrapper that maps existing profiler logic to structured contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from unrealmate.contracts.performance_profile import (
    PerformanceBottleneckResult,
    PerformanceBottleneckThresholdPolicy,
    PerformanceMetricResult,
    PerformanceParseWarningPolicy,
    PerformanceProfileRequest,
    PerformanceProfileResult,
    PerformanceSeverityThresholdPolicy,
    PerformanceProfileWarning,
)
from unrealmate.core.performance.profiler import (
    PerformanceProfiler,
    ProfilerAnalysisPolicy,
    ProfilerBottleneckThresholds,
    ProfilerParseWarningEvaluation,
    ProfilerParseWarningPolicy,
    ProfilerSeverityThresholds,
    ProfilingParseIssue,
)


class PerformanceProfilerAdapter:
    """Read profiling data via existing core profiler and map to contracts."""

    def analyze(self, request: PerformanceProfileRequest) -> PerformanceProfileResult:
        profiler = PerformanceProfiler(
            request.project_path,
            policy=self._to_profiler_policy(
                severity_policy=request.policy.severity,
                bottleneck_policy=request.policy.bottleneck,
                parse_policy=request.policy.parse,
            ),
        )
        csv_files, discovery_warnings = self._resolve_csv_files(request=request, profiler=profiler)
        normalized_profiling_dir = self._normalize_path(profiler.profiling_dir)

        if not csv_files:
            warnings = list(discovery_warnings)
            return PerformanceProfileResult(
                project_path=request.project_path,
                profiling_dir=profiler.profiling_dir,
                warnings=warnings + [
                    PerformanceProfileWarning(
                        code="profiling_data_missing",
                        message="No profiling CSV reports found.",
                        source=normalized_profiling_dir,
                        details="reports=0",
                    )
                ],
            )

        analysis = profiler.analyze_csv_reports(csv_files)
        warnings = discovery_warnings + self._build_warnings(
            parse_issues=analysis.parse_issues,
            parse_warning=analysis.parse_warning,
            profiling_dir=profiler.profiling_dir,
        )

        mapped_metrics = [
            PerformanceMetricResult(
                name=metric.name,
                value=metric.value,
                unit=metric.unit,
                category=metric.category,
                severity=metric.severity,
            )
            for metric in analysis.metrics
        ]
        if request.max_metrics is not None and request.max_metrics >= 0:
            mapped_metrics = mapped_metrics[: request.max_metrics]

        mapped_bottlenecks = [
            PerformanceBottleneckResult(
                location=bottleneck.location,
                issue=bottleneck.issue,
                impact=bottleneck.impact,
                suggestion=bottleneck.suggestion,
            )
            for bottleneck in analysis.bottlenecks
        ]

        return PerformanceProfileResult(
            project_path=request.project_path,
            profiling_dir=profiler.profiling_dir,
            data_sources=analysis.csv_files,
            metrics=mapped_metrics,
            bottlenecks=mapped_bottlenecks,
            warnings=warnings,
        )

    def _resolve_csv_files(
        self,
        request: PerformanceProfileRequest,
        profiler: PerformanceProfiler,
    ) -> tuple[list[Path], list[PerformanceProfileWarning]]:
        warnings: list[PerformanceProfileWarning] = []
        profiling_glob = (request.profiling_glob or "").strip()

        if profiling_glob:
            glob_validation_error = self._validate_glob_pattern(profiling_glob)
            if glob_validation_error is not None:
                warnings.append(
                    PerformanceProfileWarning(
                        code="profiling_glob_invalid",
                        message="Profiling glob pattern could not be evaluated.",
                        source=profiling_glob,
                        details=glob_validation_error,
                    )
                )
                return [], warnings

            try:
                csv_files = [
                    path.resolve()
                    for path in request.project_path.glob(profiling_glob)
                    if path.is_file()
                ]
            except Exception as exc:
                warnings.append(
                    PerformanceProfileWarning(
                        code="profiling_glob_invalid",
                        message="Profiling glob pattern could not be evaluated.",
                        source=profiling_glob,
                        details=f"{type(exc).__name__}: {exc}",
                    )
                )
                return [], warnings
        else:
            csv_files = [path.resolve() for path in profiler.find_csv_reports()]

        return sorted(csv_files, key=lambda path: path.as_posix().lower()), warnings

    def _build_warnings(
        self,
        parse_issues: list[ProfilingParseIssue],
        parse_warning: ProfilerParseWarningEvaluation,
        profiling_dir: Path,
    ) -> list[PerformanceProfileWarning]:
        warnings: list[PerformanceProfileWarning] = []

        sorted_issues = self._sort_parse_issues(parse_issues)
        warnings.extend(self._map_parse_warnings(sorted_issues))

        if parse_warning.emit_partial_parse_warning:
            warnings.append(
                PerformanceProfileWarning(
                    code="partial_parse",
                    message="Some profiling rows could not be parsed; results may be incomplete.",
                    source=self._normalize_path(profiling_dir),
                    details=(
                        f"issues={parse_warning.issue_count}; "
                        f"parsed_metrics={parse_warning.metric_count}; reports={parse_warning.report_count}"
                    ),
                )
            )

        if parse_warning.emit_no_metrics_warning:
            warnings.append(
                PerformanceProfileWarning(
                    code="no_metrics_parsed",
                    message="Profiling files were found but no usable metrics were parsed.",
                    source=self._normalize_path(profiling_dir),
                    details=(
                        f"reports={parse_warning.report_count}; "
                        f"parse_issues={parse_warning.issue_count}"
                    ),
                )
            )

        return warnings

    def _sort_parse_issues(
        self,
        parse_issues: Iterable[ProfilingParseIssue],
    ) -> list[ProfilingParseIssue]:
        return sorted(
            parse_issues,
            key=lambda issue: (
                issue.csv_file.as_posix().lower(),
                issue.row_number if issue.row_number is not None else -1,
                issue.code,
                issue.message,
                issue.detail or "",
            ),
        )

    def _map_parse_warnings(
        self,
        parse_issues: Iterable[ProfilingParseIssue],
    ) -> list[PerformanceProfileWarning]:
        warnings: list[PerformanceProfileWarning] = []
        for parse_issue in parse_issues:
            details = [f"issue_code={parse_issue.code}"]
            if parse_issue.row_number is not None:
                details.append(f"row={parse_issue.row_number}")
            details.append(f"message={parse_issue.message}")
            if parse_issue.detail:
                details.append(parse_issue.detail)

            warnings.append(
                PerformanceProfileWarning(
                    code="csv_parse_error",
                    message="Failed to parse CSV report.",
                    source=self._normalize_path(parse_issue.csv_file),
                    details="; ".join(details),
                )
            )
        return warnings

    def _normalize_path(self, value: Path) -> str:
        return str(value.resolve())

    def _validate_glob_pattern(self, pattern: str) -> str | None:
        if pattern.count("[") != pattern.count("]"):
            return "ValueError: unbalanced character class brackets"
        return None

    def _to_profiler_policy(
        self,
        severity_policy: PerformanceSeverityThresholdPolicy,
        bottleneck_policy: PerformanceBottleneckThresholdPolicy,
        parse_policy: PerformanceParseWarningPolicy,
    ) -> ProfilerAnalysisPolicy:
        return ProfilerAnalysisPolicy(
            severity=ProfilerSeverityThresholds(
                frame_time_warning_ms=severity_policy.frame_time_warning_ms,
                frame_time_critical_ms=severity_policy.frame_time_critical_ms,
                memory_warning_mb=severity_policy.memory_warning_mb,
                memory_critical_mb=severity_policy.memory_critical_mb,
            ),
            bottleneck=ProfilerBottleneckThresholds(
                min_critical_cpu_metrics=bottleneck_policy.min_critical_cpu_metrics,
                min_critical_gpu_metrics=bottleneck_policy.min_critical_gpu_metrics,
                min_critical_memory_metrics=bottleneck_policy.min_critical_memory_metrics,
            ),
            parse=ProfilerParseWarningPolicy(
                partial_parse_min_issues=parse_policy.partial_parse_min_issues,
                partial_parse_min_issue_ratio=parse_policy.partial_parse_min_issue_ratio,
                emit_no_metrics_warning=parse_policy.emit_no_metrics_warning,
            ),
        )
