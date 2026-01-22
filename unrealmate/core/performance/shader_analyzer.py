"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - shader_analyzer.py                           ║
║                                                                              ║
║  Author: gktrk363                                                           ║
║  Purpose: Shader complexity analysis and optimization                       ║
║  Created: 2026-01-23                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Shader analysis system for detecting complexity issues and optimization opportunities.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from rich.table import Table
from rich.console import Console


@dataclass
class ShaderInfo:
    """Shader file information."""
    path: Path
    name: str
    instruction_count: int
    complexity_score: int  # 0-100
    issues: List[str]
    suggestions: List[str]


class ShaderAnalyzer:
    """Unreal Engine shader analyzer."""
    
    def __init__(self, project_root: Path):
        """
        Initialize shader analyzer.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.shaders_dir = project_root / "Shaders"
        self.shader_files: List[ShaderInfo] = []
    
    def find_shader_files(self) -> List[Path]:
        """
        Find all shader files in project.
        
        Returns:
            List[Path]: List of shader files (.usf, .ush)
        """
        shader_files = []
        
        # Search in Shaders directory
        if self.shaders_dir.exists():
            shader_files.extend(self.shaders_dir.glob("**/*.usf"))
            shader_files.extend(self.shaders_dir.glob("**/*.ush"))
        
        # Search in Plugins
        plugins_dir = self.project_root / "Plugins"
        if plugins_dir.exists():
            shader_files.extend(plugins_dir.glob("**/Shaders/**/*.usf"))
            shader_files.extend(plugins_dir.glob("**/Shaders/**/*.ush"))
        
        return shader_files
    
    def analyze_shader(self, shader_path: Path) -> ShaderInfo:
        """
        Analyze a single shader file.
        
        Args:
            shader_path: Path to shader file
            
        Returns:
            ShaderInfo: Analysis results
        """
        issues = []
        suggestions = []
        instruction_count = 0
        
        try:
            content = shader_path.read_text(encoding='utf-8', errors='ignore')
            
            # Count approximate instructions
            instruction_count = self._count_instructions(content)
            
            # Detect issues
            if 'for' in content or 'while' in content:
                loop_count = content.count('for') + content.count('while')
                if loop_count > 3:
                    issues.append(f'Many loops detected ({loop_count})')
                    suggestions.append('Consider unrolling loops or using lookup textures')
            
            if 'tex2D' in content or 'SampleTexture' in content:
                sample_count = content.count('tex2D') + content.count('SampleTexture')
                if sample_count > 8:
                    issues.append(f'Many texture samples ({sample_count})')
                    suggestions.append('Reduce texture samples or combine textures')
            
            if 'normalize' in content:
                normalize_count = content.count('normalize')
                if normalize_count > 5:
                    issues.append(f'Frequent normalize calls ({normalize_count})')
                    suggestions.append('Cache normalized vectors when possible')
            
            if 'pow' in content or 'exp' in content or 'log' in content:
                math_count = content.count('pow') + content.count('exp') + content.count('log')
                if math_count > 3:
                    issues.append(f'Expensive math operations ({math_count})')
                    suggestions.append('Use approximations or lookup tables')
            
            # Calculate complexity score
            complexity_score = min(100, instruction_count // 10 + len(issues) * 10)
            
        except Exception as e:
            issues.append(f'Failed to analyze: {e}')
            complexity_score = 0
        
        return ShaderInfo(
            path=shader_path,
            name=shader_path.name,
            instruction_count=instruction_count,
            complexity_score=complexity_score,
            issues=issues,
            suggestions=suggestions
        )
    
    def _count_instructions(self, content: str) -> int:
        """
        Estimate instruction count from shader code.
        
        Args:
            content: Shader source code
            
        Returns:
            int: Estimated instruction count
        """
        # Remove comments
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Count statements (rough estimate)
        statements = content.count(';')
        
        # Weight expensive operations
        expensive_ops = (
            content.count('tex2D') * 4 +
            content.count('SampleTexture') * 4 +
            content.count('normalize') * 3 +
            content.count('pow') * 5 +
            content.count('exp') * 5 +
            content.count('log') * 5 +
            content.count('sqrt') * 2
        )
        
        return statements + expensive_ops
    
    def analyze_all(self) -> List[ShaderInfo]:
        """
        Analyze all shader files in project.
        
        Returns:
            List[ShaderInfo]: Analysis results for all shaders
        """
        shader_files = self.find_shader_files()
        self.shader_files = []
        
        for shader_path in shader_files:
            shader_info = self.analyze_shader(shader_path)
            self.shader_files.append(shader_info)
        
        # Sort by complexity
        self.shader_files.sort(key=lambda x: x.complexity_score, reverse=True)
        
        return self.shader_files
    
    def generate_report(self, console: Optional[Console] = None, show_all: bool = False) -> None:
        """
        Generate and print shader analysis report.
        
        Args:
            console: Rich Console instance
            show_all: Show all shaders (default: top 10)
        """
        if console is None:
            console = Console()
        
        console.print("\n[bold cyan]Shader Analysis Report[/]\n")
        
        if not self.shader_files:
            console.print("[yellow]No shader files found.[/]")
            return
        
        # Summary
        total_shaders = len(self.shader_files)
        complex_shaders = len([s for s in self.shader_files if s.complexity_score > 50])
        avg_complexity = sum(s.complexity_score for s in self.shader_files) / total_shaders
        
        console.print(f"Total Shaders: [cyan]{total_shaders}[/]")
        console.print(f"Complex Shaders (>50): [yellow]{complex_shaders}[/]")
        console.print(f"Average Complexity: [cyan]{avg_complexity:.1f}[/]\n")
        
        # Shaders table
        table = Table(title="Shader Complexity")
        table.add_column("Shader", style="cyan", no_wrap=True)
        table.add_column("Instructions", justify="right")
        table.add_column("Complexity", justify="right")
        table.add_column("Issues", justify="center")
        
        shaders_to_show = self.shader_files if show_all else self.shader_files[:10]
        
        for shader in shaders_to_show:
            complexity_color = 'green' if shader.complexity_score < 30 else 'yellow' if shader.complexity_score < 70 else 'red'
            
            table.add_row(
                shader.name,
                str(shader.instruction_count),
                f"[{complexity_color}]{shader.complexity_score}[/]",
                f"[red]{len(shader.issues)}[/]" if shader.issues else "[green]0[/]"
            )
        
        console.print(table)
        
        # Show issues for complex shaders
        complex_with_issues = [s for s in self.shader_files[:5] if s.issues]
        if complex_with_issues:
            console.print("\n[bold yellow]⚠️  Top Issues[/]\n")
            
            for shader in complex_with_issues:
                console.print(f"[bold]{shader.name}[/] (Complexity: {shader.complexity_score})")
                for issue in shader.issues:
                    console.print(f"  ❌ {issue}")
                for suggestion in shader.suggestions:
                    console.print(f"  💡 [italic]{suggestion}[/]")
                console.print()


# © 2026 gktrk363 - Crafted with passion for Unreal Engine developers
