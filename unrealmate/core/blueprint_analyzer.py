"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Blueprint Analyzer                           ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Advanced Blueprint analysis and optimization tools                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class BlueprintNode:
    """Represents a node in a Blueprint graph."""
    node_id: str
    node_type: str
    name: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    connected_to: list[str] = field(default_factory=list)


@dataclass
class BlueprintFunction:
    """Represents a Blueprint function or event."""
    name: str
    nodes: list[BlueprintNode] = field(default_factory=list)
    is_event: bool = False
    is_pure: bool = False
    complexity: int = 0


@dataclass
class BlueprintInfo:
    """Information about a Blueprint asset."""
    path: Path
    name: str
    parent_class: str = ""
    interfaces: list[str] = field(default_factory=list)
    variables: list[dict[str, Any]] = field(default_factory=list)
    functions: list[BlueprintFunction] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)
    
    @property
    def total_nodes(self) -> int:
        return sum(len(f.nodes) for f in self.functions)
    
    @property
    def total_complexity(self) -> int:
        return sum(f.complexity for f in self.functions)


@dataclass
class DependencyEdge:
    """Represents a dependency between two assets."""
    source: str
    target: str
    dependency_type: str  # 'hard', 'soft', 'editor_only'


@dataclass
class CircularDependency:
    """Represents a circular dependency chain."""
    cycle: list[str]
    severity: str  # 'warning', 'error'
    
    def __str__(self) -> str:
        return " → ".join(self.cycle) + " → " + self.cycle[0]


# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY GRAPH
# ═══════════════════════════════════════════════════════════════════════════════


class DependencyGraph:
    """Graph structure for Blueprint dependencies."""
    
    def __init__(self):
        self._nodes: set[str] = set()
        self._edges: list[DependencyEdge] = []
        self._adjacency: dict[str, list[str]] = defaultdict(list)
        self._reverse_adjacency: dict[str, list[str]] = defaultdict(list)
    
    def add_node(self, node: str) -> None:
        """Add a node to the graph."""
        self._nodes.add(node)
    
    def add_edge(
        self,
        source: str,
        target: str,
        dependency_type: str = "hard",
    ) -> None:
        """Add an edge to the graph."""
        self._nodes.add(source)
        self._nodes.add(target)
        self._edges.append(DependencyEdge(source, target, dependency_type))
        self._adjacency[source].append(target)
        self._reverse_adjacency[target].append(source)
    
    def get_dependencies(self, node: str) -> list[str]:
        """Get all dependencies of a node."""
        return self._adjacency.get(node, [])
    
    def get_dependents(self, node: str) -> list[str]:
        """Get all nodes that depend on this node."""
        return self._reverse_adjacency.get(node, [])
    
    def find_circular_dependencies(self) -> list[CircularDependency]:
        """Find all circular dependencies in the graph using DFS."""
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: list[CircularDependency] = []
        path: list[str] = []
        
        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self._adjacency.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]
                    cycles.append(CircularDependency(
                        cycle=cycle,
                        severity="error" if len(cycle) > 2 else "warning"
                    ))
            
            path.pop()
            rec_stack.remove(node)
        
        for node in self._nodes:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def topological_sort(self) -> Optional[list[str]]:
        """Return nodes in topological order, or None if cycles exist."""
        in_degree: dict[str, int] = {node: 0 for node in self._nodes}
        
        for edge in self._edges:
            in_degree[edge.target] += 1
        
        queue = [node for node in self._nodes if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in self._adjacency.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self._nodes):
            return None  # Cycle detected
        
        return result
    
    def to_mermaid(self) -> str:
        """Export graph to Mermaid diagram format."""
        lines = ["graph TD"]
        
        for edge in self._edges:
            source = edge.source.replace("/", "_").replace(".", "_")
            target = edge.target.replace("/", "_").replace(".", "_")
            lines.append(f"    {source} --> {target}")
        
        return "\n".join(lines)
    
    def to_dot(self) -> str:
        """Export graph to GraphViz DOT format."""
        lines = ["digraph Dependencies {"]
        lines.append("    rankdir=LR;")
        lines.append("    node [shape=box];")
        
        for edge in self._edges:
            lines.append(f'    "{edge.source}" -> "{edge.target}";')
        
        lines.append("}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLEXITY METRICS
# ═══════════════════════════════════════════════════════════════════════════════


class ComplexityAnalyzer:
    """Analyze Blueprint complexity metrics."""
    
    # Node types that increase cyclomatic complexity
    BRANCHING_NODES = {
        "K2Node_IfThenElse",
        "K2Node_SwitchInteger",
        "K2Node_SwitchString",
        "K2Node_SwitchEnum",
        "K2Node_Select",
        "K2Node_MultiGate",
        "K2Node_DoOnceMultiInput",
    }
    
    # Node types that indicate loop structures
    LOOP_NODES = {
        "K2Node_ForEachLoop",
        "K2Node_ForLoop",
        "K2Node_WhileLoop",
        "K2Node_MacroInstance",
    }
    
    @classmethod
    def calculate_cyclomatic_complexity(
        cls,
        function: BlueprintFunction,
    ) -> int:
        """
        Calculate cyclomatic complexity of a Blueprint function.
        
        Cyclomatic complexity = E - N + 2P
        Where E = edges, N = nodes, P = connected components
        
        For Blueprints, we simplify:
        Complexity = 1 + number of decision points
        """
        complexity = 1  # Base complexity
        
        for node in function.nodes:
            if node.node_type in cls.BRANCHING_NODES:
                complexity += 1
            elif node.node_type in cls.LOOP_NODES:
                complexity += 1
        
        return complexity
    
    @classmethod
    def analyze_blueprint(cls, blueprint: BlueprintInfo) -> dict[str, Any]:
        """Analyze a Blueprint and return metrics."""
        metrics = {
            "name": blueprint.name,
            "total_functions": len(blueprint.functions),
            "total_nodes": blueprint.total_nodes,
            "total_complexity": 0,
            "average_complexity": 0.0,
            "max_complexity": 0,
            "most_complex_function": "",
            "complexity_rating": "Low",
            "suggestions": [],
        }
        
        if not blueprint.functions:
            return metrics
        
        complexities = []
        for func in blueprint.functions:
            func.complexity = cls.calculate_cyclomatic_complexity(func)
            complexities.append((func.name, func.complexity))
        
        metrics["total_complexity"] = sum(c for _, c in complexities)
        metrics["average_complexity"] = metrics["total_complexity"] / len(complexities)
        
        max_func = max(complexities, key=lambda x: x[1])
        metrics["max_complexity"] = max_func[1]
        metrics["most_complex_function"] = max_func[0]
        
        # Rate complexity
        avg = metrics["average_complexity"]
        if avg <= 5:
            metrics["complexity_rating"] = "Low"
        elif avg <= 10:
            metrics["complexity_rating"] = "Medium"
        elif avg <= 20:
            metrics["complexity_rating"] = "High"
        else:
            metrics["complexity_rating"] = "Very High"
        
        # Generate suggestions
        if metrics["max_complexity"] > 15:
            metrics["suggestions"].append(
                f"Consider breaking down '{max_func[0]}' into smaller functions"
            )
        
        if metrics["total_nodes"] > 200:
            metrics["suggestions"].append(
                "Blueprint has many nodes. Consider moving logic to C++"
            )
        
        if len(blueprint.dependencies) > 10:
            metrics["suggestions"].append(
                "High number of dependencies. Review for potential decoupling"
            )
        
        return metrics


# ═══════════════════════════════════════════════════════════════════════════════
# REFACTORING SUGGESTIONS
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class RefactoringSuggestion:
    """A suggested refactoring action."""
    category: str  # 'performance', 'maintainability', 'readability'
    severity: str  # 'info', 'warning', 'error'
    message: str
    location: str
    suggestion: str


class RefactoringAnalyzer:
    """Analyze Blueprints for refactoring opportunities."""
    
    @classmethod
    def analyze(cls, blueprint: BlueprintInfo) -> list[RefactoringSuggestion]:
        """Analyze a Blueprint and return refactoring suggestions."""
        suggestions = []
        
        # Check for large functions
        for func in blueprint.functions:
            if len(func.nodes) > 50:
                suggestions.append(RefactoringSuggestion(
                    category="maintainability",
                    severity="warning",
                    message=f"Function '{func.name}' has {len(func.nodes)} nodes",
                    location=func.name,
                    suggestion="Break down into smaller, focused functions",
                ))
        
        # Check for deep nesting (many branch nodes in sequence)
        # This is a simplified check
        for func in blueprint.functions:
            branch_count = sum(
                1 for n in func.nodes
                if n.node_type in ComplexityAnalyzer.BRANCHING_NODES
            )
            if branch_count > 5:
                suggestions.append(RefactoringSuggestion(
                    category="readability",
                    severity="info",
                    message=f"'{func.name}' has {branch_count} branch nodes",
                    location=func.name,
                    suggestion="Consider using switch statements or lookup tables",
                ))
        
        # Check for many dependencies
        if len(blueprint.dependencies) > 15:
            suggestions.append(RefactoringSuggestion(
                category="maintainability",
                severity="warning",
                message=f"Blueprint has {len(blueprint.dependencies)} dependencies",
                location=blueprint.name,
                suggestion="Consider using interfaces to reduce coupling",
            ))
        
        return suggestions


# ═══════════════════════════════════════════════════════════════════════════════
# C++ CONVERSION HELPER
# ═══════════════════════════════════════════════════════════════════════════════


class CppConversionHelper:
    """Helper for converting Blueprint logic to C++."""
    
    # Blueprint node to C++ mapping
    NODE_TO_CPP = {
        "K2Node_IfThenElse": "if ({condition}) {{ {then} }} else {{ {else} }}",
        "K2Node_ForLoop": "for (int32 i = {start}; i <= {end}; i++) {{ {body} }}",
        "K2Node_ForEachLoop": "for (auto& {element} : {array}) {{ {body} }}",
        "K2Node_CallFunction": "{target}->{function}({params});",
        "K2Node_VariableGet": "{variable}",
        "K2Node_VariableSet": "{variable} = {value};",
        "K2Node_SpawnActor": "GetWorld()->SpawnActor<{class}>({location}, {rotation});",
    }
    
    # Blueprint types to C++ types
    TYPE_MAPPING = {
        "Boolean": "bool",
        "Integer": "int32",
        "Float": "float",
        "String": "FString",
        "Name": "FName",
        "Text": "FText",
        "Vector": "FVector",
        "Rotator": "FRotator",
        "Transform": "FTransform",
        "Object": "UObject*",
        "Actor": "AActor*",
        "Class": "TSubclassOf<>",
    }
    
    @classmethod
    def generate_header(cls, blueprint: BlueprintInfo) -> str:
        """Generate C++ header file content."""
        lines = [
            "// Auto-generated by UnrealMate",
            f"// Original Blueprint: {blueprint.name}",
            "",
            "#pragma once",
            "",
            '#include "CoreMinimal.h"',
            f'#include "{blueprint.parent_class}.h"',
            f'#include "{blueprint.name}.generated.h"',
            "",
        ]
        
        # Class declaration
        lines.append("UCLASS()")
        lines.append(f"class {blueprint.name.upper()}_API A{blueprint.name} : public {blueprint.parent_class}")
        lines.append("{")
        lines.append("    GENERATED_BODY()")
        lines.append("")
        lines.append("public:")
        lines.append(f"    A{blueprint.name}();")
        lines.append("")
        
        # Variables
        for var in blueprint.variables:
            cpp_type = cls.TYPE_MAPPING.get(var.get("type", ""), "auto")
            lines.append("    UPROPERTY(EditAnywhere, BlueprintReadWrite)")
            lines.append(f"    {cpp_type} {var.get('name', 'Variable')};")
            lines.append("")
        
        # Functions
        for func in blueprint.functions:
            if func.is_event:
                lines.append(f"    virtual void {func.name}() override;")
            else:
                lines.append("    UFUNCTION(BlueprintCallable)")
                lines.append(f"    void {func.name}();")
            lines.append("")
        
        lines.append("};")
        
        return "\n".join(lines)
    
    @classmethod
    def generate_cpp(cls, blueprint: BlueprintInfo) -> str:
        """Generate C++ implementation file content."""
        lines = [
            "// Auto-generated by UnrealMate",
            f"// Original Blueprint: {blueprint.name}",
            "",
            f'#include "{blueprint.name}.h"',
            "",
            f"A{blueprint.name}::A{blueprint.name}()",
            "{",
            "    // Constructor",
            "}",
            "",
        ]
        
        # Function implementations
        for func in blueprint.functions:
            lines.append(f"void A{blueprint.name}::{func.name}()")
            lines.append("{")
            lines.append("    // TODO: Implement logic")
            lines.append(f"    // Original had {len(func.nodes)} nodes")
            lines.append("}")
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def get_conversion_report(cls, blueprint: BlueprintInfo) -> dict[str, Any]:
        """Generate a conversion feasibility report."""
        report = {
            "blueprint": blueprint.name,
            "feasibility": "High",
            "estimated_effort": "Low",
            "warnings": [],
            "recommendations": [],
        }
        
        # Analyze complexity
        total_nodes = blueprint.total_nodes
        
        if total_nodes > 500:
            report["feasibility"] = "Low"
            report["estimated_effort"] = "High"
            report["warnings"].append(
                f"Blueprint has {total_nodes} nodes - consider incremental conversion"
            )
        elif total_nodes > 200:
            report["feasibility"] = "Medium"
            report["estimated_effort"] = "Medium"
        
        # Check for hard-to-convert patterns
        for func in blueprint.functions:
            for node in func.nodes:
                if "Timeline" in node.node_type:
                    report["warnings"].append(
                        f"Timeline node in '{func.name}' requires manual conversion"
                    )
                if "Delay" in node.node_type:
                    report["recommendations"].append(
                        "Use FTimerHandle for delay logic in C++"
                    )
        
        return report


# ═══════════════════════════════════════════════════════════════════════════════
# BLUEPRINT ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════


class BlueprintAnalyzer:
    """Main class for Blueprint analysis."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.content_path = project_path / "Content"
        self.blueprints: list[BlueprintInfo] = []
        self.dependency_graph = DependencyGraph()
    
    def scan_blueprints(self) -> list[BlueprintInfo]:
        """Scan project for Blueprint assets."""
        blueprints = []
        
        if not self.content_path.exists():
            console.print("[yellow]Content folder not found[/yellow]")
            return blueprints
        
        for uasset in self.content_path.rglob("*.uasset"):
            # Check if it's a Blueprint (has corresponding .umap or specific patterns)
            blueprint_name = uasset.stem
            
            # Create basic info (in real implementation, parse the asset)
            info = BlueprintInfo(
                path=uasset,
                name=blueprint_name,
            )
            blueprints.append(info)
            self.dependency_graph.add_node(str(uasset.relative_to(self.project_path)))
        
        self.blueprints = blueprints
        return blueprints
    
    def analyze_dependencies(self) -> DependencyGraph:
        """Analyze dependencies between Blueprints."""
        # In real implementation, parse asset references
        # This is a simplified version
        return self.dependency_graph
    
    def find_circular_dependencies(self) -> list[CircularDependency]:
        """Find circular dependencies in the project."""
        return self.dependency_graph.find_circular_dependencies()
    
    def get_complexity_report(self) -> list[dict[str, Any]]:
        """Get complexity report for all Blueprints."""
        reports = []
        for bp in self.blueprints:
            report = ComplexityAnalyzer.analyze_blueprint(bp)
            reports.append(report)
        return reports
    
    def get_refactoring_suggestions(self) -> list[RefactoringSuggestion]:
        """Get refactoring suggestions for all Blueprints."""
        all_suggestions = []
        for bp in self.blueprints:
            suggestions = RefactoringAnalyzer.analyze(bp)
            all_suggestions.extend(suggestions)
        return all_suggestions
    
    def generate_cpp_conversion(
        self,
        blueprint: BlueprintInfo,
        output_dir: Path,
    ) -> tuple[Path, Path]:
        """Generate C++ files for a Blueprint."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        header_path = output_dir / f"{blueprint.name}.h"
        cpp_path = output_dir / f"{blueprint.name}.cpp"
        
        header_content = CppConversionHelper.generate_header(blueprint)
        cpp_content = CppConversionHelper.generate_cpp(blueprint)
        
        header_path.write_text(header_content, encoding="utf-8")
        cpp_path.write_text(cpp_content, encoding="utf-8")
        
        return header_path, cpp_path
    
    def print_dependency_tree(self, blueprint_name: str) -> None:
        """Print dependency tree for a Blueprint."""
        tree = Tree(f"[bold cyan]{blueprint_name}[/bold cyan]")
        
        deps = self.dependency_graph.get_dependencies(blueprint_name)
        for dep in deps:
            branch = tree.add(f"[green]→ {dep}[/green]")
            sub_deps = self.dependency_graph.get_dependencies(dep)
            for sub in sub_deps:
                branch.add(f"[dim]→ {sub}[/dim]")
        
        console.print(tree)
    
    def print_complexity_table(self) -> None:
        """Print complexity metrics as a table."""
        table = Table(title="Blueprint Complexity Report")
        table.add_column("Blueprint", style="cyan")
        table.add_column("Functions", justify="right")
        table.add_column("Nodes", justify="right")
        table.add_column("Complexity", justify="right")
        table.add_column("Rating", style="bold")
        
        for bp in self.blueprints:
            metrics = ComplexityAnalyzer.analyze_blueprint(bp)
            
            rating_style = {
                "Low": "green",
                "Medium": "yellow",
                "High": "red",
                "Very High": "bold red",
            }.get(metrics["complexity_rating"], "white")
            
            table.add_row(
                bp.name,
                str(metrics["total_functions"]),
                str(metrics["total_nodes"]),
                str(metrics["total_complexity"]),
                f"[{rating_style}]{metrics['complexity_rating']}[/{rating_style}]",
            )
        
        console.print(table)

