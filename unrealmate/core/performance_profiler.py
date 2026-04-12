"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Performance Profiler                         ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Advanced performance profiling and analysis utilities              ║
║  Created: 2026-01-23                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS AND DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════


class ProfileCategory(Enum):
    """Categories for profiling data."""
    BLUEPRINT = auto()
    RENDERING = auto()
    MEMORY = auto()
    NETWORK = auto()
    LOADING = auto()
    GARBAGE_COLLECTION = auto()


class Severity(Enum):
    """Severity levels for performance issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ProfileSample:
    """A single profiling sample."""
    timestamp: float
    category: ProfileCategory
    name: str
    duration_ms: float
    call_count: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceIssue:
    """A detected performance issue."""
    category: ProfileCategory
    severity: Severity
    title: str
    description: str
    location: str
    suggestion: str
    impact_score: float = 0.0  # 0-100


@dataclass
class BlueprintProfile:
    """Profiling data for a Blueprint."""
    name: str
    total_time_ms: float = 0.0
    call_count: int = 0
    functions: dict[str, float] = field(default_factory=dict)
    events: dict[str, float] = field(default_factory=dict)
    
    @property
    def average_time_ms(self) -> float:
        return self.total_time_ms / self.call_count if self.call_count > 0 else 0


@dataclass
class MemoryProfile:
    """Memory profiling data."""
    timestamp: datetime
    total_physical_mb: float
    used_physical_mb: float
    virtual_mb: float
    gpu_memory_mb: float = 0
    texture_memory_mb: float = 0
    mesh_memory_mb: float = 0
    
    @property
    def usage_percentage(self) -> float:
        return (self.used_physical_mb / self.total_physical_mb * 100) if self.total_physical_mb > 0 else 0


@dataclass
class DrawCallInfo:
    """Information about draw calls."""
    frame_number: int
    total_draw_calls: int
    primitive_count: int
    triangle_count: int
    by_pass: dict[str, int] = field(default_factory=dict)


@dataclass 
class ShaderComplexityData:
    """Shader complexity information."""
    material_name: str
    instruction_count: int
    texture_samples: int
    interpolators: int
    complexity_score: float
    suggestions: list[str] = field(default_factory=list)


@dataclass
class NetworkProfile:
    """Network replication profiling data."""
    actor_name: str
    bytes_per_second: float
    replicated_properties: int
    rpc_calls_per_second: float
    relevancy_checks: int


# ═══════════════════════════════════════════════════════════════════════════════
# BLUEPRINT EXECUTION PROFILER
# ═══════════════════════════════════════════════════════════════════════════════


class BlueprintProfiler:
    """Profile Blueprint execution."""
    
    # Thresholds for performance issues (in milliseconds)
    THRESHOLDS = {
        "tick": 0.5,  # Tick should be < 0.5ms
        "event": 1.0,  # Events should be < 1ms
        "function": 2.0,  # Functions should be < 2ms
        "construction": 5.0,  # Construction should be < 5ms
    }
    
    def __init__(self):
        self.profiles: dict[str, BlueprintProfile] = {}
        self.samples: list[ProfileSample] = []
    
    def record_sample(
        self,
        blueprint_name: str,
        function_name: str,
        duration_ms: float,
        is_event: bool = False,
    ) -> None:
        """Record a profiling sample."""
        if blueprint_name not in self.profiles:
            self.profiles[blueprint_name] = BlueprintProfile(name=blueprint_name)
        
        profile = self.profiles[blueprint_name]
        profile.total_time_ms += duration_ms
        profile.call_count += 1
        
        if is_event:
            profile.events[function_name] = profile.events.get(function_name, 0) + duration_ms
        else:
            profile.functions[function_name] = profile.functions.get(function_name, 0) + duration_ms
        
        self.samples.append(ProfileSample(
            timestamp=time.time(),
            category=ProfileCategory.BLUEPRINT,
            name=f"{blueprint_name}::{function_name}",
            duration_ms=duration_ms,
        ))
    
    def analyze(self) -> list[PerformanceIssue]:
        """Analyze collected data and find performance issues."""
        issues = []
        
        for name, profile in self.profiles.items():
            # Check tick performance
            if "Tick" in profile.functions:
                tick_time = profile.functions["Tick"] / max(profile.call_count, 1)
                if tick_time > self.THRESHOLDS["tick"]:
                    issues.append(PerformanceIssue(
                        category=ProfileCategory.BLUEPRINT,
                        severity=Severity.WARNING if tick_time < 2 else Severity.ERROR,
                        title=f"Slow Tick in {name}",
                        description=f"Average tick time: {tick_time:.2f}ms",
                        location=name,
                        suggestion="Move heavy logic out of Tick, use Timers instead",
                        impact_score=min(tick_time * 20, 100),
                    ))
            
            # Check for expensive events
            for event_name, total_time in profile.events.items():
                avg_time = total_time / max(profile.call_count, 1)
                if avg_time > self.THRESHOLDS["event"]:
                    issues.append(PerformanceIssue(
                        category=ProfileCategory.BLUEPRINT,
                        severity=Severity.WARNING,
                        title=f"Expensive Event: {event_name}",
                        description=f"Average time: {avg_time:.2f}ms in {name}",
                        location=f"{name}::{event_name}",
                        suggestion="Consider caching results or reducing frequency",
                        impact_score=min(avg_time * 10, 100),
                    ))
        
        return sorted(issues, key=lambda i: i.impact_score, reverse=True)
    
    def get_hotspots(self, top_n: int = 10) -> list[tuple[str, float]]:
        """Get the top N hotspots (most expensive functions)."""
        all_functions: list[tuple[str, float]] = []
        
        for name, profile in self.profiles.items():
            for func_name, time_ms in profile.functions.items():
                all_functions.append((f"{name}::{func_name}", time_ms))
            for event_name, time_ms in profile.events.items():
                all_functions.append((f"{name}::{event_name}", time_ms))
        
        return sorted(all_functions, key=lambda x: x[1], reverse=True)[:top_n]
    
    def print_report(self) -> None:
        """Print profiling report."""
        table = Table(title="Blueprint Performance Report")
        table.add_column("Blueprint", style="cyan")
        table.add_column("Total Time", justify="right")
        table.add_column("Calls", justify="right")
        table.add_column("Avg Time", justify="right")
        table.add_column("Status")
        
        for name, profile in sorted(
            self.profiles.items(),
            key=lambda x: x[1].total_time_ms,
            reverse=True,
        ):
            avg = profile.average_time_ms
            status = "[green]OK[/green]"
            if avg > 1.0:
                status = "[yellow]⚠ Slow[/yellow]"
            if avg > 5.0:
                status = "[red]✗ Critical[/red]"
            
            table.add_row(
                name,
                f"{profile.total_time_ms:.2f}ms",
                str(profile.call_count),
                f"{avg:.2f}ms",
                status,
            )
        
        console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY LEAK DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════


class MemoryLeakDetector:
    """Detect potential memory leaks."""
    
    # Growth thresholds
    GROWTH_WARNING_MB = 50  # Warn if memory grows by 50MB
    GROWTH_ERROR_MB = 200  # Error if memory grows by 200MB
    
    def __init__(self):
        self.snapshots: list[MemoryProfile] = []
        self.object_counts: dict[str, list[int]] = defaultdict(list)
    
    def take_snapshot(
        self,
        total_mb: float,
        used_mb: float,
        virtual_mb: float = 0,
    ) -> MemoryProfile:
        """Take a memory snapshot."""
        snapshot = MemoryProfile(
            timestamp=datetime.now(),
            total_physical_mb=total_mb,
            used_physical_mb=used_mb,
            virtual_mb=virtual_mb,
        )
        self.snapshots.append(snapshot)
        return snapshot
    
    def record_object_count(self, class_name: str, count: int) -> None:
        """Record object count for a class."""
        self.object_counts[class_name].append(count)
    
    def analyze(self) -> list[PerformanceIssue]:
        """Analyze memory data for leaks."""
        issues = []
        
        if len(self.snapshots) < 2:
            return issues
        
        # Check overall memory growth
        first = self.snapshots[0]
        last = self.snapshots[-1]
        growth_mb = last.used_physical_mb - first.used_physical_mb
        
        if growth_mb > self.GROWTH_ERROR_MB:
            issues.append(PerformanceIssue(
                category=ProfileCategory.MEMORY,
                severity=Severity.ERROR,
                title="Significant Memory Growth",
                description=f"Memory grew by {growth_mb:.1f}MB during session",
                location="Global",
                suggestion="Check for unreleased references and circular dependencies",
                impact_score=min(growth_mb / 2, 100),
            ))
        elif growth_mb > self.GROWTH_WARNING_MB:
            issues.append(PerformanceIssue(
                category=ProfileCategory.MEMORY,
                severity=Severity.WARNING,
                title="Memory Growth Detected",
                description=f"Memory grew by {growth_mb:.1f}MB during session",
                location="Global",
                suggestion="Monitor memory allocation patterns",
                impact_score=min(growth_mb / 4, 100),
            ))
        
        # Check for growing object counts
        for class_name, counts in self.object_counts.items():
            if len(counts) >= 3:
                # Check if consistently growing
                is_growing = all(counts[i] <= counts[i+1] for i in range(len(counts)-1))
                growth = counts[-1] - counts[0]
                
                if is_growing and growth > 100:
                    issues.append(PerformanceIssue(
                        category=ProfileCategory.MEMORY,
                        severity=Severity.WARNING,
                        title=f"Growing Object Count: {class_name}",
                        description=f"Count grew from {counts[0]} to {counts[-1]}",
                        location=class_name,
                        suggestion="Verify objects are being properly destroyed",
                        impact_score=min(growth / 10, 100),
                    ))
        
        return issues
    
    def get_memory_trend(self) -> list[tuple[datetime, float]]:
        """Get memory usage trend over time."""
        return [(s.timestamp, s.used_physical_mb) for s in self.snapshots]


# ═══════════════════════════════════════════════════════════════════════════════
# DRAW CALL ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════


class DrawCallAnalyzer:
    """Analyze draw calls and rendering performance."""
    
    # Recommended limits
    DRAW_CALL_WARNING = 2000
    DRAW_CALL_ERROR = 5000
    TRIANGLE_WARNING = 2_000_000
    TRIANGLE_ERROR = 5_000_000
    
    def __init__(self):
        self.frames: list[DrawCallInfo] = []
    
    def record_frame(
        self,
        draw_calls: int,
        primitives: int,
        triangles: int,
        by_pass: Optional[dict[str, int]] = None,
    ) -> DrawCallInfo:
        """Record a frame's draw call data."""
        info = DrawCallInfo(
            frame_number=len(self.frames),
            total_draw_calls=draw_calls,
            primitive_count=primitives,
            triangle_count=triangles,
            by_pass=by_pass or {},
        )
        self.frames.append(info)
        return info
    
    def analyze(self) -> list[PerformanceIssue]:
        """Analyze draw call data."""
        issues = []
        
        if not self.frames:
            return issues
        
        # Calculate averages
        avg_draws = sum(f.total_draw_calls for f in self.frames) / len(self.frames)
        avg_tris = sum(f.triangle_count for f in self.frames) / len(self.frames)
        max_draws = max(f.total_draw_calls for f in self.frames)
        max(f.triangle_count for f in self.frames)
        
        # Check draw calls
        if avg_draws > self.DRAW_CALL_ERROR:
            issues.append(PerformanceIssue(
                category=ProfileCategory.RENDERING,
                severity=Severity.ERROR,
                title="Excessive Draw Calls",
                description=f"Average: {avg_draws:.0f}, Max: {max_draws}",
                location="Rendering",
                suggestion="Use instancing, merge meshes, or implement LODs",
                impact_score=90,
            ))
        elif avg_draws > self.DRAW_CALL_WARNING:
            issues.append(PerformanceIssue(
                category=ProfileCategory.RENDERING,
                severity=Severity.WARNING,
                title="High Draw Call Count",
                description=f"Average: {avg_draws:.0f}, Max: {max_draws}",
                location="Rendering",
                suggestion="Consider batching similar materials",
                impact_score=60,
            ))
        
        # Check triangles
        if avg_tris > self.TRIANGLE_ERROR:
            issues.append(PerformanceIssue(
                category=ProfileCategory.RENDERING,
                severity=Severity.ERROR,
                title="Excessive Triangle Count",
                description=f"Average: {avg_tris/1_000_000:.1f}M triangles",
                location="Rendering",
                suggestion="Implement aggressive LOD system",
                impact_score=85,
            ))
        elif avg_tris > self.TRIANGLE_WARNING:
            issues.append(PerformanceIssue(
                category=ProfileCategory.RENDERING,
                severity=Severity.WARNING,
                title="High Triangle Count",
                description=f"Average: {avg_tris/1_000_000:.1f}M triangles",
                location="Rendering",
                suggestion="Review mesh complexity and LOD settings",
                impact_score=50,
            ))
        
        return issues
    
    def get_breakdown_by_pass(self) -> dict[str, float]:
        """Get average draw calls by render pass."""
        if not self.frames:
            return {}
        
        totals: dict[str, int] = defaultdict(int)
        for frame in self.frames:
            for pass_name, count in frame.by_pass.items():
                totals[pass_name] += count
        
        return {k: v / len(self.frames) for k, v in totals.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# SHADER COMPLEXITY ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════


class ShaderComplexityAnalyzer:
    """Analyze shader/material complexity."""
    
    # Complexity thresholds
    INSTRUCTION_WARNING = 200
    INSTRUCTION_ERROR = 500
    TEXTURE_SAMPLE_WARNING = 8
    TEXTURE_SAMPLE_ERROR = 16
    
    def __init__(self):
        self.materials: list[ShaderComplexityData] = []
    
    def analyze_material(
        self,
        name: str,
        instructions: int,
        texture_samples: int,
        interpolators: int = 0,
    ) -> ShaderComplexityData:
        """Analyze a single material."""
        # Calculate complexity score (0-100)
        score = 0
        score += min(instructions / 5, 40)  # Up to 40 points for instructions
        score += min(texture_samples * 3, 30)  # Up to 30 points for textures
        score += min(interpolators * 2, 30)  # Up to 30 points for interpolators
        
        suggestions = []
        
        if instructions > self.INSTRUCTION_ERROR:
            suggestions.append("Reduce shader complexity - consider baking calculations")
        elif instructions > self.INSTRUCTION_WARNING:
            suggestions.append("Shader has many instructions - optimize math operations")
        
        if texture_samples > self.TEXTURE_SAMPLE_ERROR:
            suggestions.append("Too many texture samples - use texture atlases")
        elif texture_samples > self.TEXTURE_SAMPLE_WARNING:
            suggestions.append("Consider reducing texture samples")
        
        data = ShaderComplexityData(
            material_name=name,
            instruction_count=instructions,
            texture_samples=texture_samples,
            interpolators=interpolators,
            complexity_score=score,
            suggestions=suggestions,
        )
        self.materials.append(data)
        return data
    
    def get_issues(self) -> list[PerformanceIssue]:
        """Convert material analysis to performance issues."""
        issues = []
        
        for mat in self.materials:
            if mat.instruction_count > self.INSTRUCTION_ERROR:
                issues.append(PerformanceIssue(
                    category=ProfileCategory.RENDERING,
                    severity=Severity.ERROR,
                    title=f"Complex Shader: {mat.material_name}",
                    description=f"{mat.instruction_count} instructions, {mat.texture_samples} samples",
                    location=mat.material_name,
                    suggestion=mat.suggestions[0] if mat.suggestions else "Optimize shader",
                    impact_score=mat.complexity_score,
                ))
            elif mat.instruction_count > self.INSTRUCTION_WARNING:
                issues.append(PerformanceIssue(
                    category=ProfileCategory.RENDERING,
                    severity=Severity.WARNING,
                    title=f"Moderately Complex Shader: {mat.material_name}",
                    description=f"{mat.instruction_count} instructions",
                    location=mat.material_name,
                    suggestion=mat.suggestions[0] if mat.suggestions else "Review shader",
                    impact_score=mat.complexity_score,
                ))
        
        return sorted(issues, key=lambda i: i.impact_score, reverse=True)
    
    def print_report(self) -> None:
        """Print shader complexity report."""
        table = Table(title="Shader Complexity Report")
        table.add_column("Material", style="cyan")
        table.add_column("Instructions", justify="right")
        table.add_column("Samples", justify="right")
        table.add_column("Score", justify="right")
        table.add_column("Status")
        
        for mat in sorted(self.materials, key=lambda m: m.complexity_score, reverse=True):
            if mat.complexity_score > 70:
                status = "[red]✗ Complex[/red]"
            elif mat.complexity_score > 40:
                status = "[yellow]⚠ Moderate[/yellow]"
            else:
                status = "[green]✓ OK[/green]"
            
            table.add_row(
                mat.material_name,
                str(mat.instruction_count),
                str(mat.texture_samples),
                f"{mat.complexity_score:.0f}",
                status,
            )
        
        console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
# NETWORK REPLICATION PROFILER
# ═══════════════════════════════════════════════════════════════════════════════


class NetworkProfiler:
    """Profile network replication performance."""
    
    # Thresholds
    BYTES_PER_SEC_WARNING = 10_000  # 10 KB/s per actor
    BYTES_PER_SEC_ERROR = 50_000  # 50 KB/s per actor
    RPC_PER_SEC_WARNING = 10
    RPC_PER_SEC_ERROR = 50
    
    def __init__(self):
        self.actors: dict[str, NetworkProfile] = {}
    
    def record_actor(
        self,
        actor_name: str,
        bytes_per_sec: float,
        replicated_props: int,
        rpcs_per_sec: float = 0,
        relevancy_checks: int = 0,
    ) -> NetworkProfile:
        """Record network data for an actor."""
        profile = NetworkProfile(
            actor_name=actor_name,
            bytes_per_second=bytes_per_sec,
            replicated_properties=replicated_props,
            rpc_calls_per_second=rpcs_per_sec,
            relevancy_checks=relevancy_checks,
        )
        self.actors[actor_name] = profile
        return profile
    
    def analyze(self) -> list[PerformanceIssue]:
        """Analyze network replication data."""
        issues = []
        
        for name, profile in self.actors.items():
            # Check bandwidth
            if profile.bytes_per_second > self.BYTES_PER_SEC_ERROR:
                issues.append(PerformanceIssue(
                    category=ProfileCategory.NETWORK,
                    severity=Severity.ERROR,
                    title=f"High Bandwidth Actor: {name}",
                    description=f"{profile.bytes_per_second/1000:.1f} KB/s",
                    location=name,
                    suggestion="Reduce replication frequency or property count",
                    impact_score=80,
                ))
            elif profile.bytes_per_second > self.BYTES_PER_SEC_WARNING:
                issues.append(PerformanceIssue(
                    category=ProfileCategory.NETWORK,
                    severity=Severity.WARNING,
                    title=f"Moderate Bandwidth Actor: {name}",
                    description=f"{profile.bytes_per_second/1000:.1f} KB/s",
                    location=name,
                    suggestion="Review replicated properties",
                    impact_score=50,
                ))
            
            # Check RPC frequency
            if profile.rpc_calls_per_second > self.RPC_PER_SEC_ERROR:
                issues.append(PerformanceIssue(
                    category=ProfileCategory.NETWORK,
                    severity=Severity.ERROR,
                    title=f"RPC Spam: {name}",
                    description=f"{profile.rpc_calls_per_second:.1f} RPCs/s",
                    location=name,
                    suggestion="Batch RPCs or reduce call frequency",
                    impact_score=75,
                ))
        
        return issues
    
    def get_total_bandwidth(self) -> float:
        """Get total bandwidth usage in bytes/second."""
        return sum(p.bytes_per_second for p in self.actors.values())
    
    def print_report(self) -> None:
        """Print network profiling report."""
        table = Table(title="Network Replication Report")
        table.add_column("Actor", style="cyan")
        table.add_column("Bandwidth", justify="right")
        table.add_column("Properties", justify="right")
        table.add_column("RPCs/s", justify="right")
        table.add_column("Status")
        
        for name, profile in sorted(
            self.actors.items(),
            key=lambda x: x[1].bytes_per_second,
            reverse=True,
        ):
            if profile.bytes_per_second > self.BYTES_PER_SEC_ERROR:
                status = "[red]✗ High[/red]"
            elif profile.bytes_per_second > self.BYTES_PER_SEC_WARNING:
                status = "[yellow]⚠ Moderate[/yellow]"
            else:
                status = "[green]✓ OK[/green]"
            
            table.add_row(
                name,
                f"{profile.bytes_per_second/1000:.1f} KB/s",
                str(profile.replicated_properties),
                f"{profile.rpc_calls_per_second:.1f}",
                status,
            )
        
        total = self.get_total_bandwidth()
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{total/1000:.1f} KB/s[/bold]",
            "",
            "",
            "",
        )
        
        console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE PROFILER (MAIN CLASS)
# ═══════════════════════════════════════════════════════════════════════════════


class PerformanceProfiler:
    """Main class for performance profiling."""
    
    def __init__(self):
        self.blueprint_profiler = BlueprintProfiler()
        self.memory_detector = MemoryLeakDetector()
        self.draw_call_analyzer = DrawCallAnalyzer()
        self.shader_analyzer = ShaderComplexityAnalyzer()
        self.network_profiler = NetworkProfiler()
        self.all_issues: list[PerformanceIssue] = []
    
    def run_full_analysis(self) -> list[PerformanceIssue]:
        """Run all analyzers and collect issues."""
        self.all_issues = []
        
        self.all_issues.extend(self.blueprint_profiler.analyze())
        self.all_issues.extend(self.memory_detector.analyze())
        self.all_issues.extend(self.draw_call_analyzer.analyze())
        self.all_issues.extend(self.shader_analyzer.get_issues())
        self.all_issues.extend(self.network_profiler.analyze())
        
        return sorted(self.all_issues, key=lambda i: i.impact_score, reverse=True)
    
    def get_issues_by_category(
        self,
        category: ProfileCategory,
    ) -> list[PerformanceIssue]:
        """Get issues filtered by category."""
        return [i for i in self.all_issues if i.category == category]
    
    def get_issues_by_severity(
        self,
        severity: Severity,
    ) -> list[PerformanceIssue]:
        """Get issues filtered by severity."""
        return [i for i in self.all_issues if i.severity == severity]
    
    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all performance data."""
        return {
            "total_issues": len(self.all_issues),
            "critical_issues": len(self.get_issues_by_severity(Severity.CRITICAL)),
            "error_issues": len(self.get_issues_by_severity(Severity.ERROR)),
            "warning_issues": len(self.get_issues_by_severity(Severity.WARNING)),
            "by_category": {
                cat.name: len(self.get_issues_by_category(cat))
                for cat in ProfileCategory
            },
            "top_issues": [
                {"title": i.title, "score": i.impact_score}
                for i in self.all_issues[:5]
            ],
        }
    
    def print_full_report(self) -> None:
        """Print a full performance report."""
        console.print(Panel("[bold cyan]Performance Report[/bold cyan]", expand=False))
        
        # Summary
        summary = self.get_summary()
        console.print(f"\n[bold]Total Issues:[/bold] {summary['total_issues']}")
        console.print(f"  [red]Critical:[/red] {summary['critical_issues']}")
        console.print(f"  [red]Errors:[/red] {summary['error_issues']}")
        console.print(f"  [yellow]Warnings:[/yellow] {summary['warning_issues']}")
        
        # Issues table
        if self.all_issues:
            console.print("\n[bold]Top Issues:[/bold]")
            table = Table()
            table.add_column("Category", style="cyan")
            table.add_column("Severity")
            table.add_column("Title")
            table.add_column("Impact", justify="right")
            
            for issue in self.all_issues[:10]:
                severity_style = {
                    Severity.CRITICAL: "bold red",
                    Severity.ERROR: "red",
                    Severity.WARNING: "yellow",
                    Severity.INFO: "dim",
                }.get(issue.severity, "white")
                
                table.add_row(
                    issue.category.name,
                    f"[{severity_style}]{issue.severity.value}[/{severity_style}]",
                    issue.title,
                    f"{issue.impact_score:.0f}",
                )
            
            console.print(table)
    
    def export_report(self, output_path: Path) -> None:
        """Export report to JSON file."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "generator": "UnrealMate Performance Profiler by G & E ZYNTH",
            "summary": self.get_summary(),
            "issues": [
                {
                    "category": i.category.name,
                    "severity": i.severity.value,
                    "title": i.title,
                    "description": i.description,
                    "location": i.location,
                    "suggestion": i.suggestion,
                    "impact_score": i.impact_score,
                }
                for i in self.all_issues
            ],
        }
        
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        console.print(f"[green]✓ Report exported to {output_path}[/green]")

