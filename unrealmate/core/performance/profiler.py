"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      UnrealMate - profiler.py                                ║
║                                                                              ║
║  Author: G & E ZYNTH                                                           ║
║  Purpose: Performance profiling and bottleneck detection                    ║
║  Created: 2026-01-23                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Performance profiling system for Unreal Engine projects.
Analyzes CPU, GPU, and memory bottlenecks.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

import csv
from pathlib import Path
from typing import List, Tuple, Iterable
from dataclasses import dataclass, field


@dataclass
class PerformanceMetric:
    """Performance metric data."""
    name: str
    value: float
    unit: str
    category: str  # CPU, GPU, Memory, Network
    severity: str  # OK, Warning, Critical


@dataclass
class PerformanceBottleneck:
    """Identified performance bottleneck."""
    location: str
    issue: str
    impact: str  # High, Medium, Low
    suggestion: str


@dataclass(frozen=True)
class ProfilingParseIssue:
    """Structured parse issue for a profiling CSV report."""

    csv_file: Path
    code: str
    message: str
    row_number: int | None = None
    detail: str | None = None


@dataclass(frozen=True)
class ProfilerSeverityThresholds:
    """Severity classification thresholds for frame/memory metrics."""

    frame_time_warning_ms: float = 16.6
    frame_time_critical_ms: float = 33.3
    memory_warning_mb: float = 2000.0
    memory_critical_mb: float = 4000.0


@dataclass(frozen=True)
class ProfilerBottleneckThresholds:
    """Critical metric count thresholds required for bottleneck emission."""

    min_critical_cpu_metrics: int = 1
    min_critical_gpu_metrics: int = 1
    min_critical_memory_metrics: int = 1


@dataclass(frozen=True)
class ProfilerParseWarningPolicy:
    """Parse warning policy knobs for partial/no-metric signaling."""

    partial_parse_min_issues: int = 1
    partial_parse_min_issue_ratio: float = 0.0
    emit_no_metrics_warning: bool = True


@dataclass(frozen=True)
class ProfilerAnalysisPolicy:
    """Profiler-side analysis policy object."""

    severity: ProfilerSeverityThresholds = field(default_factory=ProfilerSeverityThresholds)
    bottleneck: ProfilerBottleneckThresholds = field(default_factory=ProfilerBottleneckThresholds)
    parse: ProfilerParseWarningPolicy = field(default_factory=ProfilerParseWarningPolicy)


@dataclass(frozen=True)
class ProfilerParseWarningEvaluation:
    """Core evaluation result for parse warning policy decisions."""

    issue_count: int
    metric_count: int
    report_count: int
    issue_ratio: float
    emit_partial_parse_warning: bool
    emit_no_metrics_warning: bool


@dataclass(frozen=True)
class ProfilerAnalysisResult:
    """Stateless structured output for profiler analysis."""

    csv_files: list[Path]
    metrics: list[PerformanceMetric]
    bottlenecks: list[PerformanceBottleneck]
    parse_issues: list[ProfilingParseIssue]
    parse_warning: ProfilerParseWarningEvaluation


DEFAULT_PROFILER_ANALYSIS_POLICY = ProfilerAnalysisPolicy()


class PerformanceProfiler:
    """Unreal Engine performance profiler focused on structured analysis."""
    
    def __init__(
        self,
        project_root: Path,
        policy: ProfilerAnalysisPolicy | None = None,
    ):
        """
        Initialize profiler.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.saved_dir = project_root / "Saved"
        self.profiling_dir = self.saved_dir / "Profiling"
        self.policy = policy or DEFAULT_PROFILER_ANALYSIS_POLICY
    
    def find_trace_files(self) -> List[Path]:
        """
        Find Unreal Insights trace files.
        
        Returns:
            List[Path]: List of .utrace files
        """
        if not self.profiling_dir.exists():
            return []
        
        return list(self.profiling_dir.glob("*.utrace"))
    
    def find_csv_reports(self) -> List[Path]:
        """
        Find CSV performance reports.
        
        Returns:
            List[Path]: List of .csv files
        """
        if not self.profiling_dir.exists():
            return []
        
        return list(self.profiling_dir.glob("*.csv"))
    
    def _create_metric(self, name: str, value: float, unit: str) -> PerformanceMetric:
        """Create a normalized metric instance from parsed row values."""
        category = self._categorize_metric(name)
        severity = self._assess_severity(name, value, unit)
        return PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            category=category,
            severity=severity,
        )

    def _validate_required_columns(
        self,
        fieldnames: Iterable[str] | None,
        csv_file: Path,
    ) -> list[ProfilingParseIssue]:
        if fieldnames is None:
            return [
                ProfilingParseIssue(
                    csv_file=csv_file,
                    code="missing_header",
                    message="CSV header row is missing.",
                )
            ]

        missing_columns = [column for column in ("Name", "Value") if column not in fieldnames]
        if missing_columns:
            return [
                ProfilingParseIssue(
                    csv_file=csv_file,
                    code="missing_columns",
                    message=f"CSV missing required columns: {', '.join(missing_columns)}.",
                    detail=f"Available columns: {', '.join(fieldnames)}",
                )
            ]

        return []

    def _parse_metric_row(
        self,
        csv_file: Path,
        row: dict[str, str | None],
        row_number: int,
    ) -> Tuple[PerformanceMetric | None, ProfilingParseIssue | None]:
        name = (row.get("Name") or "").strip()
        raw_value = (row.get("Value") or "").strip()

        if not name:
            return None, ProfilingParseIssue(
                csv_file=csv_file,
                code="row_missing_name",
                message="CSV row is missing Name value.",
                row_number=row_number,
            )

        if not raw_value:
            return None, ProfilingParseIssue(
                csv_file=csv_file,
                code="row_missing_value",
                message="CSV row is missing Value entry.",
                row_number=row_number,
            )

        try:
            value = float(raw_value)
        except ValueError:
            return None, ProfilingParseIssue(
                csv_file=csv_file,
                code="row_invalid_value",
                message="CSV row Value is not numeric.",
                row_number=row_number,
                detail=f"raw_value={raw_value}",
            )

        unit = (row.get("Unit") or "ms").strip() or "ms"
        return self._create_metric(name=name, value=value, unit=unit), None

    def parse_csv_report_detailed(
        self,
        csv_file: Path,
    ) -> Tuple[List[PerformanceMetric], List[ProfilingParseIssue]]:
        """
        Parse CSV report and return both metrics and structured parse issues.

        Args:
            csv_file: Path to CSV file

        Returns:
            Tuple[List[PerformanceMetric], List[ProfilingParseIssue]]
        """
        normalized_csv_file = csv_file.resolve()
        metrics: List[PerformanceMetric] = []
        parse_issues: List[ProfilingParseIssue] = []

        try:
            with open(normalized_csv_file, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)

                parse_issues.extend(
                    self._validate_required_columns(
                        fieldnames=reader.fieldnames,
                        csv_file=normalized_csv_file,
                    )
                )
                if parse_issues:
                    return metrics, parse_issues

                for row_number, row in enumerate(reader, start=2):
                    metric, parse_issue = self._parse_metric_row(
                        csv_file=normalized_csv_file,
                        row=row,
                        row_number=row_number,
                    )
                    if parse_issue is not None:
                        parse_issues.append(parse_issue)
                        continue
                    if metric is not None:
                        metrics.append(metric)

        except Exception as exc:
            parse_issues.append(
                ProfilingParseIssue(
                    csv_file=normalized_csv_file,
                    code="read_failed",
                    message="Failed to read CSV report.",
                    detail=f"{type(exc).__name__}: {exc}",
                )
            )

        return metrics, parse_issues

    def parse_csv_report(self, csv_file: Path) -> List[PerformanceMetric]:
        """
        Parse CSV performance report (legacy compatibility API).
        Prefer parse_csv_report_detailed for parse-issue visibility.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            List[PerformanceMetric]: Parsed metrics
        """
        metrics, _ = self.parse_csv_report_detailed(csv_file)
        return metrics
    
    def _categorize_metric(self, name: str) -> str:
        """Categorize metric by name."""
        name_lower = name.lower()
        
        if any(x in name_lower for x in ['cpu', 'thread', 'tick', 'game']):
            return 'CPU'
        elif any(x in name_lower for x in ['gpu', 'render', 'draw', 'shader']):
            return 'GPU'
        elif any(x in name_lower for x in ['memory', 'mem', 'alloc', 'heap']):
            return 'Memory'
        elif any(x in name_lower for x in ['network', 'net', 'packet']):
            return 'Network'
        else:
            return 'Other'
    
    def _assess_severity(self, name: str, value: float, unit: str) -> str:
        """Assess metric severity."""
        severity_policy = self.policy.severity
        unit_normalized = unit.strip().lower()

        # Frame time thresholds (ms)
        if 'frame' in name.lower() and unit_normalized == 'ms':
            if value > severity_policy.frame_time_critical_ms:
                return 'Critical'
            elif value > severity_policy.frame_time_warning_ms:
                return 'Warning'
            else:
                return 'OK'
        
        # Memory thresholds (MB)
        if 'memory' in name.lower() and unit_normalized == 'mb':
            if value > severity_policy.memory_critical_mb:
                return 'Critical'
            elif value > severity_policy.memory_warning_mb:
                return 'Warning'
            else:
                return 'OK'
        
        # Default: OK
        return 'OK'
    
    def detect_bottlenecks_for_metrics(
        self,
        metrics: List[PerformanceMetric],
    ) -> List[PerformanceBottleneck]:
        """
        Detect performance bottlenecks from an explicit metric list.
        
        Returns:
            List[PerformanceBottleneck]: Detected bottlenecks
        """
        bottlenecks = []
        bottleneck_policy = self.policy.bottleneck
        
        # Group metrics by category
        cpu_metrics = [m for m in metrics if m.category == 'CPU']
        gpu_metrics = [m for m in metrics if m.category == 'GPU']
        memory_metrics = [m for m in metrics if m.category == 'Memory']
        
        # Check CPU bottlenecks
        critical_cpu = [m for m in cpu_metrics if m.severity == 'Critical']
        if len(critical_cpu) >= bottleneck_policy.min_critical_cpu_metrics:
            bottleneck = PerformanceBottleneck(
                location='CPU',
                issue=f'{len(critical_cpu)} critical CPU metrics detected',
                impact='High',
                suggestion='Optimize game logic, reduce tick complexity, use async tasks'
            )
            bottlenecks.append(bottleneck)
        
        # Check GPU bottlenecks
        critical_gpu = [m for m in gpu_metrics if m.severity == 'Critical']
        if len(critical_gpu) >= bottleneck_policy.min_critical_gpu_metrics:
            bottleneck = PerformanceBottleneck(
                location='GPU',
                issue=f'{len(critical_gpu)} critical GPU metrics detected',
                impact='High',
                suggestion='Reduce draw calls, optimize shaders, use LODs, enable occlusion culling'
            )
            bottlenecks.append(bottleneck)
        
        # Check memory bottlenecks
        critical_memory = [m for m in memory_metrics if m.severity == 'Critical']
        if len(critical_memory) >= bottleneck_policy.min_critical_memory_metrics:
            bottleneck = PerformanceBottleneck(
                location='Memory',
                issue=f'{len(critical_memory)} critical memory metrics detected',
                impact='High',
                suggestion='Reduce texture sizes, enable texture streaming, optimize asset loading'
            )
            bottlenecks.append(bottleneck)
        
        return bottlenecks

    def detect_bottlenecks(self) -> List[PerformanceBottleneck]:
        """
        Legacy compatibility API.
        Prefer detect_bottlenecks_for_metrics(metrics) with explicit inputs.
        """
        _, bottlenecks = self.analyze()
        return bottlenecks

    def evaluate_parse_warning_policy(
        self,
        issue_count: int,
        metric_count: int,
        report_count: int,
    ) -> ProfilerParseWarningEvaluation:
        """Evaluate parse warning policy deterministically."""
        parse_policy = self.policy.parse
        total_rows = issue_count + metric_count
        issue_ratio = 1.0 if total_rows == 0 else (issue_count / total_rows)
        emit_partial = (
            issue_count >= parse_policy.partial_parse_min_issues
            and metric_count > 0
            and issue_ratio >= parse_policy.partial_parse_min_issue_ratio
        )
        emit_no_metrics = parse_policy.emit_no_metrics_warning and report_count > 0 and metric_count == 0
        return ProfilerParseWarningEvaluation(
            issue_count=issue_count,
            metric_count=metric_count,
            report_count=report_count,
            issue_ratio=issue_ratio,
            emit_partial_parse_warning=emit_partial,
            emit_no_metrics_warning=emit_no_metrics,
        )

    def analyze_csv_reports(self, csv_files: List[Path]) -> ProfilerAnalysisResult:
        """
        Stateless main analysis API.

        Args:
            csv_files: Explicit profiling CSV files to parse.

        Returns:
            ProfilerAnalysisResult: structured deterministic analysis output.
        """
        normalized_csv_files = sorted(
            [csv_file.resolve() for csv_file in csv_files],
            key=lambda path: path.as_posix().lower(),
        )
        metrics: List[PerformanceMetric] = []
        parse_issues: List[ProfilingParseIssue] = []

        for csv_file in normalized_csv_files:
            parsed_metrics, parsed_issues = self.parse_csv_report_detailed(csv_file)
            metrics.extend(parsed_metrics)
            parse_issues.extend(parsed_issues)

        bottlenecks = self.detect_bottlenecks_for_metrics(metrics)
        parse_warning = self.evaluate_parse_warning_policy(
            issue_count=len(parse_issues),
            metric_count=len(metrics),
            report_count=len(normalized_csv_files),
        )

        return ProfilerAnalysisResult(
            csv_files=normalized_csv_files,
            metrics=metrics,
            bottlenecks=bottlenecks,
            parse_issues=parse_issues,
            parse_warning=parse_warning,
        )
    
    def analyze_reports(
        self,
        csv_files: List[Path],
    ) -> Tuple[List[PerformanceMetric], List[PerformanceBottleneck], List[ProfilingParseIssue]]:
        """
        Legacy compatibility wrapper around analyze_csv_reports.

        Args:
            csv_files: CSV report files to parse

        Returns:
            Tuple: (metrics, bottlenecks, parse_issues)
        """
        analysis = self.analyze_csv_reports(csv_files)
        return analysis.metrics, analysis.bottlenecks, analysis.parse_issues

    def analyze(self) -> Tuple[List[PerformanceMetric], List[PerformanceBottleneck]]:
        """
        Legacy convenience API using default CSV discovery.
        Prefer analyze_csv_reports(csv_files) for structured/stateless flows.
        
        Returns:
            Tuple: (metrics, bottlenecks)
        """
        csv_files = self.find_csv_reports()
        analysis = self.analyze_csv_reports(csv_files)
        return analysis.metrics, analysis.bottlenecks


# © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers

