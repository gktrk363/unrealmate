"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Plugin Manager                               ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Manage Unreal Engine plugins - dependencies, conflicts, templates  ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import json
import shutil
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class PluginDependency:
    """A plugin dependency."""
    name: str
    version: str = ""
    is_optional: bool = False
    is_enabled: bool = True


@dataclass
class PluginInfo:
    """Information about an Unreal Engine plugin."""
    name: str
    path: Path
    version: str = "1.0.0"
    version_name: str = ""
    friendly_name: str = ""
    description: str = ""
    category: str = ""
    created_by: str = ""
    created_by_url: str = ""
    docs_url: str = ""
    marketplace_url: str = ""
    support_url: str = ""
    can_contain_content: bool = False
    is_beta_version: bool = False
    is_experimental: bool = False
    is_enabled_by_default: bool = True
    is_installed: bool = True
    modules: list[dict[str, Any]] = field(default_factory=list)
    plugins: list[PluginDependency] = field(default_factory=list)
    
    @classmethod
    def from_uplugin(cls, path: Path) -> "PluginInfo":
        """Parse a .uplugin file."""
        try:
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            
            plugins = []
            for dep in data.get("Plugins", []):
                plugins.append(PluginDependency(
                    name=dep.get("Name", ""),
                    version=dep.get("Version", ""),
                    is_optional=dep.get("Optional", False),
                    is_enabled=dep.get("Enabled", True),
                ))
            
            return cls(
                name=path.stem,
                path=path.parent,
                version=str(data.get("Version", 1)),
                version_name=data.get("VersionName", "1.0.0"),
                friendly_name=data.get("FriendlyName", path.stem),
                description=data.get("Description", ""),
                category=data.get("Category", ""),
                created_by=data.get("CreatedBy", ""),
                created_by_url=data.get("CreatedByURL", ""),
                docs_url=data.get("DocsURL", ""),
                marketplace_url=data.get("MarketplaceURL", ""),
                support_url=data.get("SupportURL", ""),
                can_contain_content=data.get("CanContainContent", False),
                is_beta_version=data.get("IsBetaVersion", False),
                is_experimental=data.get("IsExperimental", False),
                is_enabled_by_default=data.get("EnabledByDefault", True),
                modules=data.get("Modules", []),
                plugins=plugins,
            )
        except Exception as e:
            console.print(f"[red]Error parsing {path}: {e}[/red]")
            return cls(name=path.stem, path=path.parent)


@dataclass
class VersionConflict:
    """A version conflict between plugins."""
    plugin_name: str
    required_by: list[tuple[str, str]]  # (requirer_name, required_version)
    severity: str  # 'warning', 'error'
    
    @property
    def description(self) -> str:
        reqs = [f"{name} requires {ver}" for name, ver in self.required_by]
        return f"{self.plugin_name}: " + " vs ".join(reqs)


@dataclass
class DependencyIssue:
    """A dependency resolution issue."""
    issue_type: str  # 'missing', 'circular', 'conflict', 'disabled'
    related_plugins: list[str]
    message: str
    suggestion: str


# ═══════════════════════════════════════════════════════════════════════════════
# PLUGIN DEPENDENCY RESOLVER
# ═══════════════════════════════════════════════════════════════════════════════


class PluginDependencyResolver:
    """Resolve plugin dependencies."""
    
    def __init__(self):
        self.plugins: dict[str, PluginInfo] = {}
        self.dependency_graph: dict[str, set[str]] = defaultdict(set)
        self.reverse_graph: dict[str, set[str]] = defaultdict(set)
    
    def add_plugin(self, plugin: PluginInfo) -> None:
        """Add a plugin to the resolver."""
        self.plugins[plugin.name] = plugin
        
        for dep in plugin.plugins:
            if dep.is_enabled:
                self.dependency_graph[plugin.name].add(dep.name)
                self.reverse_graph[dep.name].add(plugin.name)
    
    def resolve(self, plugin_name: str) -> list[str]:
        """
        Resolve all dependencies for a plugin in load order.
        Returns empty list if resolution fails.
        """
        if plugin_name not in self.plugins:
            return []
        
        visited = set()
        result = []
        temp_mark = set()
        
        def visit(name: str) -> bool:
            if name in temp_mark:
                return False  # Circular dependency
            if name in visited:
                return True
            
            temp_mark.add(name)
            
            for dep in self.dependency_graph.get(name, set()):
                if not visit(dep):
                    return False
            
            temp_mark.remove(name)
            visited.add(name)
            result.append(name)
            return True
        
        if visit(plugin_name):
            return result
        return []
    
    def find_missing_dependencies(self) -> list[DependencyIssue]:
        """Find plugins with missing dependencies."""
        issues = []
        
        for name, plugin in self.plugins.items():
            for dep in plugin.plugins:
                if dep.is_enabled and dep.name not in self.plugins:
                    if not dep.is_optional:
                        issues.append(DependencyIssue(
                            issue_type="missing",
                            related_plugins=[name, dep.name],
                            message=f"'{name}' requires missing plugin '{dep.name}'",
                            suggestion=f"Install '{dep.name}' or disable '{name}'",
                        ))
        
        return issues
    
    def find_circular_dependencies(self) -> list[DependencyIssue]:
        """Find circular dependencies."""
        issues = []
        visited = set()
        
        def find_cycle(name: str, path: list[str]) -> Optional[list[str]]:
            if name in path:
                cycle_start = path.index(name)
                return path[cycle_start:]
            
            if name in visited:
                return None
            
            visited.add(name)
            path.append(name)
            
            for dep in self.dependency_graph.get(name, set()):
                cycle = find_cycle(dep, path.copy())
                if cycle:
                    return cycle
            
            return None
        
        for name in self.plugins:
            if name not in visited:
                cycle = find_cycle(name, [])
                if cycle:
                    issues.append(DependencyIssue(
                        issue_type="circular",
                        related_plugins=cycle,
                        message=f"Circular dependency: {' → '.join(cycle)} → {cycle[0]}",
                        suggestion="Break the cycle by removing one dependency",
                    ))
        
        return issues
    
    def get_load_order(self) -> list[str]:
        """Get the correct load order for all plugins."""
        all_resolved = []
        visited = set()
        
        for name in self.plugins:
            if name not in visited:
                order = self.resolve(name)
                for p in order:
                    if p not in visited:
                        all_resolved.append(p)
                        visited.add(p)
        
        return all_resolved
    
    def visualize(self, root: Optional[str] = None) -> Tree:
        """Create a dependency tree visualization."""
        if root:
            tree = Tree(f"[bold cyan]{root}[/bold cyan]")
            self._add_deps_to_tree(tree, root, set())
        else:
            tree = Tree("[bold]Plugin Dependencies[/bold]")
            # Find root plugins (no dependents)
            roots = [n for n in self.plugins if not self.reverse_graph.get(n)]
            for name in roots:
                branch = tree.add(f"[cyan]{name}[/cyan]")
                self._add_deps_to_tree(branch, name, set())
        
        return tree
    
    def _add_deps_to_tree(self, parent: Tree, name: str, visited: set[str]) -> None:
        """Recursively add dependencies to tree."""
        if name in visited:
            parent.add(f"[dim](circular: {name})[/dim]")
            return
        
        visited.add(name)
        
        deps = self.dependency_graph.get(name, set())
        for dep in deps:
            style = "green" if dep in self.plugins else "red"
            branch = parent.add(f"[{style}]{dep}[/{style}]")
            if dep in self.plugins:
                self._add_deps_to_tree(branch, dep, visited.copy())


# ═══════════════════════════════════════════════════════════════════════════════
# VERSION CONFLICT DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════


class VersionConflictDetector:
    """Detect version conflicts between plugins."""
    
    def __init__(self):
        self.plugins: dict[str, PluginInfo] = {}
        self.version_requirements: dict[str, list[tuple[str, str]]] = defaultdict(list)
    
    def add_plugin(self, plugin: PluginInfo) -> None:
        """Add a plugin and its version requirements."""
        self.plugins[plugin.name] = plugin
        
        for dep in plugin.plugins:
            if dep.version:
                self.version_requirements[dep.name].append((plugin.name, dep.version))
    
    def detect_conflicts(self) -> list[VersionConflict]:
        """Detect version conflicts."""
        conflicts = []
        
        for plugin_name, requirements in self.version_requirements.items():
            if len(requirements) > 1:
                # Check if versions are compatible
                versions = set(ver for _, ver in requirements)
                if len(versions) > 1:
                    conflicts.append(VersionConflict(
                        plugin_name=plugin_name,
                        required_by=requirements,
                        severity="error" if self._are_incompatible(versions) else "warning",
                    ))
        
        return conflicts
    
    def _are_incompatible(self, versions: set[str]) -> bool:
        """Check if versions are incompatible (different major versions)."""
        majors = set()
        for ver in versions:
            try:
                major = int(ver.split(".")[0])
                majors.add(major)
            except (ValueError, IndexError):
                pass
        return len(majors) > 1
    
    def get_version_matrix(self) -> Table:
        """Create a version requirement matrix table."""
        table = Table(title="Plugin Version Requirements")
        table.add_column("Plugin", style="cyan")
        table.add_column("Required By")
        table.add_column("Version")
        table.add_column("Status")
        
        for plugin_name in sorted(self.version_requirements.keys()):
            reqs = self.version_requirements[plugin_name]
            
            for i, (requirer, version) in enumerate(reqs):
                status = "[green]✓[/green]"
                if len(reqs) > 1:
                    versions = set(v for _, v in reqs)
                    if len(versions) > 1:
                        status = "[yellow]⚠ Version mismatch[/yellow]"
                
                table.add_row(
                    plugin_name if i == 0 else "",
                    requirer,
                    version or "any",
                    status if i == 0 else "",
                )
        
        return table


# ═══════════════════════════════════════════════════════════════════════════════
# PLUGIN TEMPLATE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════


class PluginTemplateGenerator:
    """Generate custom plugin templates."""
    
    TEMPLATES = {
        "blank": {
            "description": "A blank plugin with minimal structure",
            "has_content": False,
            "module_type": "Runtime",
        },
        "content_only": {
            "description": "A content-only plugin (no code)",
            "has_content": True,
            "module_type": None,
        },
        "editor": {
            "description": "An editor extension plugin",
            "has_content": False,
            "module_type": "Editor",
        },
        "gameplay": {
            "description": "A gameplay plugin with Blueprints support",
            "has_content": True,
            "module_type": "Runtime",
        },
        "third_party": {
            "description": "A third-party library wrapper",
            "has_content": False,
            "module_type": "ThirdParty",
        },
    }
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.plugins_path = project_path / "Plugins"
    
    def list_templates(self) -> Table:
        """List available templates."""
        table = Table(title="Available Plugin Templates")
        table.add_column("Template", style="cyan")
        table.add_column("Description")
        table.add_column("Has Content")
        table.add_column("Module Type")
        
        for name, info in self.TEMPLATES.items():
            table.add_row(
                name,
                info["description"],
                "Yes" if info["has_content"] else "No",
                info["module_type"] or "None",
            )
        
        return table
    
    def generate(
        self,
        plugin_name: str,
        template: str = "blank",
        author: str = "",
        description: str = "",
    ) -> Path:
        """Generate a new plugin from template."""
        if template not in self.TEMPLATES:
            raise ValueError(f"Unknown template: {template}")
        
        template_info = self.TEMPLATES[template]
        plugin_path = self.plugins_path / plugin_name
        
        # Create directory structure
        plugin_path.mkdir(parents=True, exist_ok=True)
        
        # Create .uplugin file
        uplugin_data = {
            "FileVersion": 3,
            "Version": 1,
            "VersionName": "1.0.0",
            "FriendlyName": plugin_name,
            "Description": description or f"A {template} plugin",
            "Category": "Other",
            "CreatedBy": author or "UnrealMate",
            "CreatedByURL": "",
            "DocsURL": "",
            "MarketplaceURL": "",
            "SupportURL": "",
            "CanContainContent": template_info["has_content"],
            "IsBetaVersion": False,
            "IsExperimentalVersion": False,
            "Installed": False,
        }
        
        # Add module if needed
        if template_info["module_type"]:
            uplugin_data["Modules"] = [{
                "Name": plugin_name,
                "Type": template_info["module_type"],
                "LoadingPhase": "Default",
            }]
            
            # Create Source directory
            source_path = plugin_path / "Source" / plugin_name
            source_path.mkdir(parents=True, exist_ok=True)
            
            # Create module files
            self._create_module_files(source_path, plugin_name, template_info["module_type"])
        
        # Create Content directory if needed
        if template_info["has_content"]:
            (plugin_path / "Content").mkdir(exist_ok=True)
        
        # Create Resources directory
        (plugin_path / "Resources").mkdir(exist_ok=True)
        
        # Write .uplugin file
        uplugin_path = plugin_path / f"{plugin_name}.uplugin"
        uplugin_path.write_text(json.dumps(uplugin_data, indent=2), encoding="utf-8")
        
        console.print(f"[green]✓ Created plugin: {plugin_path}[/green]")
        return plugin_path
    
    def _create_module_files(
        self,
        source_path: Path,
        module_name: str,
        module_type: str,
    ) -> None:
        """Create C++ module files."""
        # Build.cs file
        build_cs = f'''using UnrealBuildTool;

public class {module_name} : ModuleRules
{{
    public {module_name}(ReadOnlyTargetRules Target) : base(Target)
    {{
        PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;
        
        PublicDependencyModuleNames.AddRange(new string[] {{
            "Core",
        }});
        
        PrivateDependencyModuleNames.AddRange(new string[] {{
            "CoreUObject",
            "Engine",
        }});
    }}
}}
'''
        (source_path / f"{module_name}.Build.cs").write_text(build_cs, encoding="utf-8")
        
        # Module header
        header = f'''#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class F{module_name}Module : public IModuleInterface
{{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
}};
'''
        public_path = source_path / "Public"
        public_path.mkdir(exist_ok=True)
        (public_path / f"{module_name}.h").write_text(header, encoding="utf-8")
        
        # Module implementation
        impl = f'''#include "{module_name}.h"

#define LOCTEXT_NAMESPACE "F{module_name}Module"

void F{module_name}Module::StartupModule()
{{
    // Plugin startup logic
}}

void F{module_name}Module::ShutdownModule()
{{
    // Plugin shutdown logic
}}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(F{module_name}Module, {module_name})
'''
        private_path = source_path / "Private"
        private_path.mkdir(exist_ok=True)
        (private_path / f"{module_name}.cpp").write_text(impl, encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
# MARKETPLACE PLUGIN INSTALLER
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class MarketplacePlugin:
    """Information about a marketplace plugin."""
    name: str
    slug: str
    price: float
    rating: float
    downloads: int
    category: str
    description: str
    url: str
    is_free: bool = False


class MarketplaceInstaller:
    """Install plugins from marketplace or other sources."""
    
    VAULT_PATHS = {
        "windows": Path.home() / "AppData/Local/EpicGamesLauncher/Saved/Marketplace",
        "mac": Path.home() / "Library/Application Support/Epic/EpicGamesLauncher/Saved/Marketplace",
    }
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.plugins_path = project_path / "Plugins"
    
    def get_vault_plugins(self) -> list[PluginInfo]:
        """Get plugins from the Epic Games Vault."""
        vault_path = self.VAULT_PATHS.get("windows")  # Default to Windows
        
        if not vault_path or not vault_path.exists():
            return []
        
        plugins = []
        for uplugin in vault_path.rglob("*.uplugin"):
            try:
                plugin = PluginInfo.from_uplugin(uplugin)
                plugin.is_installed = False
                plugins.append(plugin)
            except Exception:
                pass
        
        return plugins
    
    def install_from_vault(
        self,
        plugin_name: str,
        vault_path: Optional[Path] = None,
    ) -> bool:
        """Install a plugin from the vault."""
        vault = vault_path or self.VAULT_PATHS.get("windows")
        
        if not vault or not vault.exists():
            console.print("[red]Vault path not found[/red]")
            return False
        
        # Find plugin in vault
        for uplugin in vault.rglob("*.uplugin"):
            if uplugin.stem.lower() == plugin_name.lower():
                source_dir = uplugin.parent
                target_dir = self.plugins_path / plugin_name
                
                try:
                    shutil.copytree(source_dir, target_dir)
                    console.print(f"[green]✓ Installed {plugin_name}[/green]")
                    return True
                except Exception as e:
                    console.print(f"[red]Failed to install: {e}[/red]")
                    return False
        
        console.print(f"[yellow]Plugin '{plugin_name}' not found in vault[/yellow]")
        return False
    
    def install_from_github(
        self,
        repo_url: str,
        branch: str = "main",
    ) -> bool:
        """Install a plugin from a GitHub repository."""
        # Parse URL
        parsed = urlparse(repo_url)
        if "github.com" not in parsed.netloc:
            console.print("[red]Invalid GitHub URL[/red]")
            return False
        
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            console.print("[red]Invalid repository path[/red]")
            return False
        
        owner, repo = path_parts[0], path_parts[1]
        plugin_name = repo.replace("-", "_")
        
        # Would typically use git clone here
        console.print(f"[yellow]Would clone: {owner}/{repo} (branch: {branch})[/yellow]")
        console.print(f"[dim]Target: {self.plugins_path / plugin_name}[/dim]")
        
        return True
    
    def list_installed(self) -> list[PluginInfo]:
        """List installed plugins in the project."""
        plugins = []
        
        if not self.plugins_path.exists():
            return plugins
        
        for uplugin in self.plugins_path.rglob("*.uplugin"):
            plugin = PluginInfo.from_uplugin(uplugin)
            plugins.append(plugin)
        
        return plugins
    
    def print_installed_table(self) -> None:
        """Print table of installed plugins."""
        plugins = self.list_installed()
        
        table = Table(title="Installed Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Version")
        table.add_column("Category")
        table.add_column("Has Content")
        table.add_column("Dependencies")
        
        for plugin in plugins:
            table.add_row(
                plugin.friendly_name or plugin.name,
                plugin.version_name,
                plugin.category or "-",
                "Yes" if plugin.can_contain_content else "No",
                str(len(plugin.plugins)),
            )
        
        console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
# PLUGIN MANAGER (MAIN CLASS)
# ═══════════════════════════════════════════════════════════════════════════════


class UEPluginManager:
    """Main class for managing Unreal Engine plugins."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.plugins_path = project_path / "Plugins"
        
        self.resolver = PluginDependencyResolver()
        self.conflict_detector = VersionConflictDetector()
        self.template_generator = PluginTemplateGenerator(project_path)
        self.installer = MarketplaceInstaller(project_path)
        
        self.plugins: list[PluginInfo] = []
    
    def scan(self) -> list[PluginInfo]:
        """Scan for all plugins in the project."""
        self.plugins = []
        
        if not self.plugins_path.exists():
            console.print("[yellow]No Plugins folder found[/yellow]")
            return self.plugins
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Scanning plugins..."),
            console=console,
        ) as progress:
            progress.add_task("Scanning", total=None)
            
            for uplugin in self.plugins_path.rglob("*.uplugin"):
                plugin = PluginInfo.from_uplugin(uplugin)
                self.plugins.append(plugin)
                self.resolver.add_plugin(plugin)
                self.conflict_detector.add_plugin(plugin)
        
        return self.plugins
    
    def check_dependencies(self) -> list[DependencyIssue]:
        """Check for dependency issues."""
        issues = []
        issues.extend(self.resolver.find_missing_dependencies())
        issues.extend(self.resolver.find_circular_dependencies())
        return issues
    
    def check_version_conflicts(self) -> list[VersionConflict]:
        """Check for version conflicts."""
        return self.conflict_detector.detect_conflicts()
    
    def get_load_order(self) -> list[str]:
        """Get the correct plugin load order."""
        return self.resolver.get_load_order()
    
    def create_plugin(
        self,
        name: str,
        template: str = "blank",
        author: str = "",
        description: str = "",
    ) -> Path:
        """Create a new plugin from template."""
        return self.template_generator.generate(
            plugin_name=name,
            template=template,
            author=author,
            description=description,
        )
    
    def install_plugin(
        self,
        source: str,
        source_type: str = "vault",
    ) -> bool:
        """Install a plugin from various sources."""
        if source_type == "vault":
            return self.installer.install_from_vault(source)
        elif source_type == "github":
            return self.installer.install_from_github(source)
        else:
            console.print(f"[red]Unknown source type: {source_type}[/red]")
            return False
    
    def print_summary(self) -> None:
        """Print a summary of all plugins."""
        console.print(Panel("[bold cyan]Plugin Summary[/bold cyan]", expand=False))
        
        # Basic stats
        console.print(f"\n[bold]Total Plugins:[/bold] {len(self.plugins)}")
        
        # Categorize
        by_category: dict[str, int] = defaultdict(int)
        for plugin in self.plugins:
            by_category[plugin.category or "Uncategorized"] += 1
        
        for category, count in sorted(by_category.items()):
            console.print(f"  {category}: {count}")
        
        # Check for issues
        dep_issues = self.check_dependencies()
        version_conflicts = self.check_version_conflicts()
        
        if dep_issues:
            console.print(f"\n[yellow]⚠ Dependency Issues: {len(dep_issues)}[/yellow]")
        
        if version_conflicts:
            console.print(f"[yellow]⚠ Version Conflicts: {len(version_conflicts)}[/yellow]")
        
        if not dep_issues and not version_conflicts:
            console.print("\n[green]✓ No issues detected[/green]")
    
    def print_dependency_tree(self) -> None:
        """Print the dependency tree."""
        tree = self.resolver.visualize()
        console.print(tree)

