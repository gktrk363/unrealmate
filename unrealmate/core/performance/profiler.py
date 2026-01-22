"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      UnrealMate - profiler.py                                ║
║                                                                              ║
║  Author: gktrk363                                                           ║
║  Purpose: Performance profiling and bottleneck detection                    ║
║  Created: 2026-01-23                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Performance profiling system for Unreal Engine projects.
Analyzes CPU, GPU, and memory bottlenecks.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from rich.table import Table
from rich.console import Console


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


class PerformanceProfiler:
    """Unreal Engine performance profiler."""
    
    def __init__(self, project_root: Path):
        """
        Initialize profiler.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.saved_dir = project_root / "Saved"
        self.profiling_dir = self.saved_dir / "Profiling"
        self.metrics: List[PerformanceMetric] = []
        self.bottlenecks: List[PerformanceBottleneck] = []
    
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
    
    def parse_csv_report(self, csv_file: Path) -> List[PerformanceMetric]:
        """
        Parse CSV performance report.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            List[PerformanceMetric]: Parsed metrics
        """
        metrics = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Try to extract metric info
                    if 'Name' in row and 'Value' in row:
                        name = row['Name']
                        try:
                            value = float(row['Value'])
                        except ValueError:
                            continue
                        
                        unit = row.get('Unit', 'ms')
                        category = self._categorize_metric(name)
                        severity = self._assess_severity(name, value, unit)
                        
                        metric = PerformanceMetric(
                            name=name,
                            value=value,
                            unit=unit,
                            category=category,
                            severity=severity
                        )
                        metrics.append(metric)
        except Exception as e:
            print(f"Error parsing CSV: {e}")
        
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
        # Frame time thresholds (ms)
        if 'frame' in name.lower() and unit == 'ms':
            if value > 33.3:  # < 30 FPS
                return 'Critical'
            elif value > 16.6:  # < 60 FPS
                return 'Warning'
            else:
                return 'OK'
        
        # Memory thresholds (MB)
        if 'memory' in name.lower() and unit == 'MB':
            if value > 4000:  # > 4GB
                return 'Critical'
            elif value > 2000:  # > 2GB
                return 'Warning'
            else:
                return 'OK'
        
        # Default: OK
        return 'OK'
    
    def detect_bottlenecks(self) -> List[PerformanceBottleneck]:
        """
        Detect performance bottlenecks from metrics.
        
        Returns:
            List[PerformanceBottleneck]: Detected bottlenecks
        """
        bottlenecks = []
        
        # Group metrics by category
        cpu_metrics = [m for m in self.metrics if m.category == 'CPU']
        gpu_metrics = [m for m in self.metrics if m.category == 'GPU']
        memory_metrics = [m for m in self.metrics if m.category == 'Memory']
        
        # Check CPU bottlenecks
        critical_cpu = [m for m in cpu_metrics if m.severity == 'Critical']
        if critical_cpu:
            bottleneck = PerformanceBottleneck(
                location='CPU',
                issue=f'{len(critical_cpu)} critical CPU metrics detected',
                impact='High',
                suggestion='Optimize game logic, reduce tick complexity, use async tasks'
            )
            bottlenecks.append(bottleneck)
        
        # Check GPU bottlenecks
        critical_gpu = [m for m in gpu_metrics if m.severity == 'Critical']
        if critical_gpu:
            bottleneck = PerformanceBottleneck(
                location='GPU',
                issue=f'{len(critical_gpu)} critical GPU metrics detected',
                impact='High',
                suggestion='Reduce draw calls, optimize shaders, use LODs, enable occlusion culling'
            )
            bottlenecks.append(bottleneck)
        
        # Check memory bottlenecks
        critical_memory = [m for m in memory_metrics if m.severity == 'Critical']
        if critical_memory:
            bottleneck = PerformanceBottleneck(
                location='Memory',
                issue=f'{len(critical_memory)} critical memory metrics detected',
                impact='High',
                suggestion='Reduce texture sizes, enable texture streaming, optimize asset loading'
            )
            bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def analyze(self) -> Tuple[List[PerformanceMetric], List[PerformanceBottleneck]]:
        """
        Run full performance analysis.
        
        Returns:
            Tuple: (metrics, bottlenecks)
        """
        self.metrics = []
        self.bottlenecks = []
        
        # Parse CSV reports
        csv_files = self.find_csv_reports()
        for csv_file in csv_files:
            metrics = self.parse_csv_report(csv_file)
            self.metrics.extend(metrics)
        
        # Detect bottlenecks
        self.bottlenecks = self.detect_bottlenecks()
        
        return self.metrics, self.bottlenecks
    
    def generate_report(self, console: Optional[Console] = None) -> None:
        """
        Generate and print performance report.
        
        Args:
            console: Rich Console instance
        """
        if console is None:
            console = Console()
        
        console.print("\n[bold cyan]Performance Analysis Report[/]\n")
        
        # Metrics table
        if self.metrics:
            table = Table(title="Performance Metrics")
            table.add_column("Category", style="cyan")
            table.add_column("Metric", style="white")
            table.add_column("Value", justify="right")
            table.add_column("Severity", justify="center")
            
            for metric in self.metrics[:20]:  # Show top 20
                severity_color = {
                    'OK': 'green',
                    'Warning': 'yellow',
                    'Critical': 'red'
                }.get(metric.severity, 'white')
                
                table.add_row(
                    metric.category,
                    metric.name,
                    f"{metric.value:.2f} {metric.unit}",
                    f"[{severity_color}]{metric.severity}[/]"
                )
            
            console.print(table)
        else:
            console.print("[yellow]No performance metrics found.[/]")
        
        # Bottlenecks
        if self.bottlenecks:
            console.print("\n[bold red]⚠️  Detected Bottlenecks[/]\n")
            
            for i, bottleneck in enumerate(self.bottlenecks, 1):
                impact_color = {
                    'High': 'red',
                    'Medium': 'yellow',
                    'Low': 'green'
                }.get(bottleneck.impact, 'white')
                
                console.print(f"[bold]{i}. {bottleneck.location}[/]")
                console.print(f"   Issue: {bottleneck.issue}")
                console.print(f"   Impact: [{impact_color}]{bottleneck.impact}[/]")
                console.print(f"   💡 Suggestion: [italic]{bottleneck.suggestion}[/]\n")
        else:
            console.print("\n[green]✅ No critical bottlenecks detected![/]\n")


# © 2026 gktrk363 - Crafted with passion for Unreal Engine developers
