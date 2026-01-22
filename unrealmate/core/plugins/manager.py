"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      UnrealMate - manager.py                                 ║
║                                                                              ║
║  Author: gktrk363                                                           ║
║  Purpose: Plugin management and installation                                ║
║  Created: 2026-01-23                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Plugin management system for Unreal Engine projects.
Install, enable, disable, and manage UE plugins.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from rich.table import Table
from rich.console import Console


@dataclass
class PluginInfo:
    """Plugin information."""
    name: str
    version: str
    description: str
    enabled: bool
    path: Path
    engine_version: Optional[str] = None


class PluginManager:
    """Unreal Engine plugin manager."""
    
    def __init__(self, project_root: Path):
        """
        Initialize plugin manager.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.plugins_dir = project_root / "Plugins"
        self.uproject_file = self._find_uproject()
    
    def _find_uproject(self) -> Optional[Path]:
        """Find .uproject file in project root."""
        uproject_files = list(self.project_root.glob("*.uproject"))
        return uproject_files[0] if uproject_files else None
    
    def list_plugins(self) -> List[PluginInfo]:
        """
        List all installed plugins.
        
        Returns:
            List[PluginInfo]: List of installed plugins
        """
        plugins = []
        
        if not self.plugins_dir.exists():
            return plugins
        
        # Scan for .uplugin files
        for uplugin_file in self.plugins_dir.rglob("*.uplugin"):
            try:
                with open(uplugin_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                plugin = PluginInfo(
                    name=data.get('FriendlyName', uplugin_file.stem),
                    version=data.get('VersionName', '1.0'),
                    description=data.get('Description', 'No description'),
                    enabled=data.get('Enabled', True),
                    path=uplugin_file.parent,
                    engine_version=data.get('EngineVersion', None)
                )
                plugins.append(plugin)
            except Exception:
                continue
        
        return plugins
    
    def install_from_git(self, git_url: str, plugin_name: Optional[str] = None) -> bool:
        """
        Install plugin from Git repository.
        
        Args:
            git_url: Git repository URL
            plugin_name: Optional plugin name (auto-detected if None)
            
        Returns:
            bool: True if successful
        """
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True)
        
        # Extract plugin name from URL if not provided
        if plugin_name is None:
            plugin_name = git_url.rstrip('/').split('/')[-1].replace('.git', '')
        
        target_dir = self.plugins_dir / plugin_name
        
        if target_dir.exists():
            return False  # Already exists
        
        try:
            # Clone repository
            subprocess.run(
                ['git', 'clone', git_url, str(target_dir)],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def install_from_local(self, source_path: Path, plugin_name: Optional[str] = None) -> bool:
        """
        Install plugin from local directory.
        
        Args:
            source_path: Path to plugin directory
            plugin_name: Optional plugin name (uses source dir name if None)
            
        Returns:
            bool: True if successful
        """
        if not source_path.exists():
            return False
        
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True)
        
        if plugin_name is None:
            plugin_name = source_path.name
        
        target_dir = self.plugins_dir / plugin_name
        
        if target_dir.exists():
            return False  # Already exists
        
        try:
            shutil.copytree(source_path, target_dir)
            return True
        except Exception:
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a plugin in .uproject file.
        
        Args:
            plugin_name: Name of plugin to enable
            
        Returns:
            bool: True if successful
        """
        if not self.uproject_file:
            return False
        
        try:
            with open(self.uproject_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Find or add plugin entry
            plugins = data.get('Plugins', [])
            plugin_entry = next((p for p in plugins if p['Name'] == plugin_name), None)
            
            if plugin_entry:
                plugin_entry['Enabled'] = True
            else:
                plugins.append({'Name': plugin_name, 'Enabled': True})
            
            data['Plugins'] = plugins
            
            with open(self.uproject_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            return True
        except Exception:
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin in .uproject file.
        
        Args:
            plugin_name: Name of plugin to disable
            
        Returns:
            bool: True if successful
        """
        if not self.uproject_file:
            return False
        
        try:
            with open(self.uproject_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            plugins = data.get('Plugins', [])
            plugin_entry = next((p for p in plugins if p['Name'] == plugin_name), None)
            
            if plugin_entry:
                plugin_entry['Enabled'] = False
            
            data['Plugins'] = plugins
            
            with open(self.uproject_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            return True
        except Exception:
            return False
    
    def remove_plugin(self, plugin_name: str) -> bool:
        """
        Remove a plugin from project.
        
        Args:
            plugin_name: Name of plugin to remove
            
        Returns:
            bool: True if successful
        """
        plugins = self.list_plugins()
        plugin = next((p for p in plugins if p.name == plugin_name), None)
        
        if not plugin:
            return False
        
        try:
            shutil.rmtree(plugin.path)
            return True
        except Exception:
            return False
    
    def generate_report(self, console: Optional[Console] = None) -> None:
        """
        Generate and print plugin report.
        
        Args:
            console: Rich Console instance
        """
        if console is None:
            console = Console()
        
        plugins = self.list_plugins()
        
        console.print("\n[bold cyan]Installed Plugins[/]\n")
        
        if not plugins:
            console.print("[yellow]No plugins installed.[/]\n")
            return
        
        table = Table()
        table.add_column("Plugin", style="cyan")
        table.add_column("Version", style="magenta")
        table.add_column("Status", justify="center")
        table.add_column("Engine", style="dim")
        
        for plugin in plugins:
            status = "[green]Enabled[/]" if plugin.enabled else "[red]Disabled[/]"
            engine = plugin.engine_version or "Any"
            
            table.add_row(
                plugin.name,
                plugin.version,
                status,
                engine
            )
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(plugins)} plugins[/]\n")


# © 2026 gktrk363 - Crafted with passion for Unreal Engine developers
