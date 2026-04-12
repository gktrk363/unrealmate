# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Performance Profile
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Performance profile capability request/response contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PerformanceSeverityThresholdPolicy:
    """Severity classification thresholds for profiling metrics."""

    frame_time_warning_ms: float = 16.6
    frame_time_critical_ms: float = 33.3
    memory_warning_mb: float = 2000.0
    memory_critical_mb: float = 4000.0

    def __post_init__(self) -> None:
        if self.frame_time_warning_ms < 0 or self.frame_time_critical_ms < 0:
            raise ValueError("frame time thresholds must be >= 0")
        if self.memory_warning_mb < 0 or self.memory_critical_mb < 0:
            raise ValueError("memory thresholds must be >= 0")
        if self.frame_time_critical_ms < self.frame_time_warning_ms:
            raise ValueError("frame_time_critical_ms must be >= frame_time_warning_ms")
        if self.memory_critical_mb < self.memory_warning_mb:
            raise ValueError("memory_critical_mb must be >= memory_warning_mb")

    def to_payload(self) -> dict[str, Any]:
        return {
            "frame_time_warning_ms": self.frame_time_warning_ms,
            "frame_time_critical_ms": self.frame_time_critical_ms,
            "memory_warning_mb": self.memory_warning_mb,
            "memory_critical_mb": self.memory_critical_mb,
        }


@dataclass(frozen=True)
class PerformanceBottleneckThresholdPolicy:
    """Bottleneck detection thresholds by category."""

    min_critical_cpu_metrics: int = 1
    min_critical_gpu_metrics: int = 1
    min_critical_memory_metrics: int = 1

    def __post_init__(self) -> None:
        if self.min_critical_cpu_metrics < 1:
            raise ValueError("min_critical_cpu_metrics must be >= 1")
        if self.min_critical_gpu_metrics < 1:
            raise ValueError("min_critical_gpu_metrics must be >= 1")
        if self.min_critical_memory_metrics < 1:
            raise ValueError("min_critical_memory_metrics must be >= 1")

    def to_payload(self) -> dict[str, Any]:
        return {
            "min_critical_cpu_metrics": self.min_critical_cpu_metrics,
            "min_critical_gpu_metrics": self.min_critical_gpu_metrics,
            "min_critical_memory_metrics": self.min_critical_memory_metrics,
        }


@dataclass(frozen=True)
class PerformanceParseWarningPolicy:
    """Parse warning policy knobs for partial parse/no-data signaling."""

    partial_parse_min_issues: int = 1
    partial_parse_min_issue_ratio: float = 0.0
    emit_no_metrics_warning: bool = True

    def __post_init__(self) -> None:
        if self.partial_parse_min_issues < 1:
            raise ValueError("partial_parse_min_issues must be >= 1")
        if not 0.0 <= self.partial_parse_min_issue_ratio <= 1.0:
            raise ValueError("partial_parse_min_issue_ratio must be between 0.0 and 1.0")

    def to_payload(self) -> dict[str, Any]:
        return {
            "partial_parse_min_issues": self.partial_parse_min_issues,
            "partial_parse_min_issue_ratio": self.partial_parse_min_issue_ratio,
            "emit_no_metrics_warning": self.emit_no_metrics_warning,
        }


@dataclass(frozen=True)
class PerformanceProfilePolicy:
    """Top-level policy bundle used by use-case and adapters."""

    severity: PerformanceSeverityThresholdPolicy = field(
        default_factory=PerformanceSeverityThresholdPolicy
    )
    bottleneck: PerformanceBottleneckThresholdPolicy = field(
        default_factory=PerformanceBottleneckThresholdPolicy
    )
    parse: PerformanceParseWarningPolicy = field(
        default_factory=PerformanceParseWarningPolicy
    )

    def to_payload(self) -> dict[str, Any]:
        return {
            "severity": self.severity.to_payload(),
            "bottleneck": self.bottleneck.to_payload(),
            "parse": self.parse.to_payload(),
        }


DEFAULT_PERFORMANCE_PROFILE_POLICY = PerformanceProfilePolicy()


@dataclass(frozen=True)
class PerformanceProfileRequest:
    """Normalized request contract for performance profile analysis."""

    project_path: Path
    profiling_glob: str = "Saved/Profiling/*.csv"
    max_metrics: int | None = None
    policy: PerformanceProfilePolicy = field(
        default_factory=lambda: DEFAULT_PERFORMANCE_PROFILE_POLICY
    )

    @classmethod
    def from_cli(
        cls,
        path: str,
        profiling_glob: str = "Saved/Profiling/*.csv",
        max_metrics: int | None = None,
        policy: PerformanceProfilePolicy | None = None,
    ) -> "PerformanceProfileRequest":
        raw_path = Path(path).expanduser()
        if raw_path.is_absolute():
            normalized = raw_path.resolve()
        else:
            normalized = (Path.cwd() / raw_path).resolve()
        return cls(
            project_path=normalized,
            profiling_glob=profiling_glob,
            max_metrics=max_metrics,
            policy=policy or DEFAULT_PERFORMANCE_PROFILE_POLICY,
        )

    def to_payload(self) -> dict[str, Any]:
        """Serialize request for deterministic contract assertions."""
        return {
            "project_path": str(self.project_path),
            "profiling_glob": self.profiling_glob,
            "max_metrics": self.max_metrics,
            "policy": self.policy.to_payload(),
        }


@dataclass(frozen=True)
class PerformanceMetricResult:
    """Normalized metric result independent from CLI rendering."""

    name: str
    value: float
    unit: str
    category: str
    severity: str


@dataclass(frozen=True)
class PerformanceBottleneckResult:
    """Normalized bottleneck result independent from CLI rendering."""

    location: str
    issue: str
    impact: str
    suggestion: str


@dataclass(frozen=True)
class PerformanceProfileWarning:
    """Non-fatal warning emitted by performance profile flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class PerformanceProfileError:
    """Fatal error emitted by performance profile flow."""

    code: str
    message: str
    source: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class PerformanceProfileResult:
    """Structured performance profile analysis output."""

    project_path: Path
    profiling_dir: Path
    data_sources: list[Path] = field(default_factory=list)
    metrics: list[PerformanceMetricResult] = field(default_factory=list)
    bottlenecks: list[PerformanceBottleneckResult] = field(default_factory=list)
    warnings: list[PerformanceProfileWarning] = field(default_factory=list)
    errors: list[PerformanceProfileError] = field(default_factory=list)

    @property
    def has_data(self) -> bool:
        return bool(self.data_sources)

    @property
    def is_success(self) -> bool:
        return not self.errors

    def to_payload(self) -> dict[str, Any]:
        """Serialize to deterministic dictionary shape for contract tests."""
        sorted_data_sources = sorted(str(path) for path in self.data_sources)
        sorted_metrics = sorted(
            self.metrics,
            key=lambda metric: (
                metric.category,
                metric.name,
                metric.unit,
                metric.value,
                metric.severity,
            ),
        )
        sorted_bottlenecks = sorted(
            self.bottlenecks,
            key=lambda bottleneck: (
                bottleneck.location,
                bottleneck.impact,
                bottleneck.issue,
                bottleneck.suggestion,
            ),
        )
        sorted_warnings = sorted(
            self.warnings,
            key=lambda warning: (warning.code, warning.source or "", warning.message, warning.details or ""),
        )
        sorted_errors = sorted(
            self.errors,
            key=lambda error: (error.code, error.source or "", error.message, error.details or ""),
        )

        return {
            "project_path": str(self.project_path),
            "profiling_dir": str(self.profiling_dir),
            "data_sources": sorted_data_sources,
            "metrics": [
                {
                    "name": metric.name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "category": metric.category,
                    "severity": metric.severity,
                }
                for metric in sorted_metrics
            ],
            "bottlenecks": [
                {
                    "location": bottleneck.location,
                    "issue": bottleneck.issue,
                    "impact": bottleneck.impact,
                    "suggestion": bottleneck.suggestion,
                }
                for bottleneck in sorted_bottlenecks
            ],
            "warnings": [
                {
                    "code": warning.code,
                    "message": warning.message,
                    "source": warning.source,
                    "details": warning.details,
                }
                for warning in sorted_warnings
            ],
            "errors": [
                {
                    "code": error.code,
                    "message": error.message,
                    "source": error.source,
                    "details": error.details,
                }
                for error in sorted_errors
            ],
        }
