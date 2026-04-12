"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      UnrealMate - manager.py                                 ║
║                                                                              ║
║  Author: G & E ZYNTH                                                           ║
║  Purpose: Plugin management and installation                                ║
║  Created: 2026-01-23                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Plugin management system for Unreal Engine projects.
Install, enable, disable, and manage UE plugins.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
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


@dataclass
class PluginMutationResult:
    """Structured result for plugin mutations."""

    success: bool
    summary: str
    detail: str = ""
    plugin_state: str = ""
    uproject_state: str = ""
    manual_recovery: str = ""
    plugin_path: Optional[Path] = None
    uproject_path: Optional[Path] = None
    partial_state_possible: bool = False


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

    def _plugin_descriptor_exists(self, plugin_root: Path) -> bool:
        """Return True when the directory contains at least one .uplugin file."""
        return any(plugin_root.rglob("*.uplugin"))

    def _load_uproject_data(self) -> dict:
        """Load the current .uproject payload."""
        if not self.uproject_file:
            raise FileNotFoundError("No .uproject file found in the project root.")

        with open(self.uproject_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_uproject_data(self, data: dict) -> None:
        """Write .uproject data atomically to avoid truncation on failure."""
        if not self.uproject_file:
            raise FileNotFoundError("No .uproject file found in the project root.")

        temp_file = self.uproject_file.with_name(f"{self.uproject_file.name}.tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            temp_file.replace(self.uproject_file)
        finally:
            if temp_file.exists():
                temp_file.unlink()

    def _uproject_references_plugin(self, plugin_name: str) -> bool:
        """Check whether the current .uproject references the named plugin."""
        if not self.uproject_file:
            return False

        try:
            data = self._load_uproject_data()
        except Exception:
            return False

        plugins = data.get("Plugins", [])
        if not isinstance(plugins, list):
            return False

        for entry in plugins:
            if isinstance(entry, dict) and entry.get("Name") == plugin_name:
                return True
        return False
    
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
    
    def install_from_git(self, git_url: str, plugin_name: Optional[str] = None) -> PluginMutationResult:
        """
        Install plugin from Git repository.
        
        Args:
            git_url: Git repository URL
            plugin_name: Optional plugin name (auto-detected if None)
            
        Returns:
            PluginMutationResult: Structured mutation outcome
        """
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True)
        
        # Extract plugin name from URL if not provided
        if plugin_name is None:
            plugin_name = git_url.rstrip('/').split('/')[-1].replace('.git', '')
        
        target_dir = self.plugins_dir / plugin_name
        
        if target_dir.exists():
            return PluginMutationResult(
                success=False,
                summary="Plugin install refused.",
                detail=f"A local plugin directory already exists at {target_dir}.",
                plugin_state="No plugin files were copied.",
                uproject_state=".uproject was not modified.",
                manual_recovery="Remove or rename the existing plugin directory, or re-run with a different --name.",
                plugin_path=target_dir,
                uproject_path=self.uproject_file,
            )
        
        try:
            # Clone repository
            subprocess.run(
                ['git', 'clone', git_url, str(target_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            return PluginMutationResult(
                success=False,
                summary="Plugin install failed.",
                detail="Git is not available on this system, so the repository could not be cloned.",
                plugin_state="No plugin files were copied.",
                uproject_state=".uproject was not modified.",
                manual_recovery="Install Git or use a local plugin directory instead.",
                plugin_path=target_dir,
                uproject_path=self.uproject_file,
            )
        except subprocess.CalledProcessError as exc:
            partial_state = target_dir.exists()
            stderr = (exc.stderr or exc.stdout or "").strip()
            return PluginMutationResult(
                success=False,
                summary="Plugin install failed.",
                detail=stderr or f"`git clone` exited with code {exc.returncode}.",
                plugin_state=(
                    f"Partial local plugin files may remain at {target_dir}."
                    if partial_state
                    else "No plugin files were copied."
                ),
                uproject_state=".uproject was not modified.",
                manual_recovery=(
                    "Remove the partially cloned plugin directory and retry."
                    if partial_state
                    else "Verify the repository URL and try again."
                ),
                plugin_path=target_dir,
                uproject_path=self.uproject_file,
                partial_state_possible=partial_state,
            )

        if not self._plugin_descriptor_exists(target_dir):
            return PluginMutationResult(
                success=False,
                summary="Plugin install failed.",
                detail="The cloned repository does not contain a .uplugin descriptor, so UnrealMate cannot treat it as a plugin install.",
                plugin_state=f"Local files were cloned to {target_dir}.",
                uproject_state=".uproject was not modified.",
                manual_recovery="Delete the cloned directory manually if you do not want to keep it.",
                plugin_path=target_dir,
                uproject_path=self.uproject_file,
                partial_state_possible=True,
            )

        return PluginMutationResult(
            success=True,
            summary="Plugin installed.",
            detail=f"Cloned plugin files into {target_dir}.",
            plugin_state="Plugin files were written under the local Plugins directory.",
            uproject_state=".uproject was not modified. Enable the plugin separately if needed.",
            plugin_path=target_dir,
            uproject_path=self.uproject_file,
        )
    
    def install_from_local(self, source_path: Path, plugin_name: Optional[str] = None) -> PluginMutationResult:
        """
        Install plugin from local directory.
        
        Args:
            source_path: Path to plugin directory
            plugin_name: Optional plugin name (uses source dir name if None)
            
        Returns:
            PluginMutationResult: Structured mutation outcome
        """
        if not source_path.exists():
            return PluginMutationResult(
                success=False,
                summary="Plugin install failed.",
                detail=f"Source plugin directory was not found: {source_path}.",
                plugin_state="No plugin files were copied.",
                uproject_state=".uproject was not modified.",
                manual_recovery="Point to an existing local plugin directory and retry.",
                uproject_path=self.uproject_file,
            )

        if not source_path.is_dir():
            return PluginMutationResult(
                success=False,
                summary="Plugin install failed.",
                detail=f"Expected a plugin directory, but received a file path: {source_path}.",
                plugin_state="No plugin files were copied.",
                uproject_state=".uproject was not modified.",
                manual_recovery="Provide the path to the plugin directory that contains the .uplugin file.",
                uproject_path=self.uproject_file,
            )

        if not self._plugin_descriptor_exists(source_path):
            return PluginMutationResult(
                success=False,
                summary="Plugin install failed.",
                detail=f"No .uplugin descriptor was found under {source_path}.",
                plugin_state="No plugin files were copied.",
                uproject_state=".uproject was not modified.",
                manual_recovery="Use a plugin source directory that contains a .uplugin descriptor.",
                uproject_path=self.uproject_file,
            )
        
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True)
        
        if plugin_name is None:
            plugin_name = source_path.name
        
        target_dir = self.plugins_dir / plugin_name
        
        if target_dir.exists():
            return PluginMutationResult(
                success=False,
                summary="Plugin install refused.",
                detail=f"A local plugin directory already exists at {target_dir}.",
                plugin_state="No plugin files were copied.",
                uproject_state=".uproject was not modified.",
                manual_recovery="Remove or rename the existing plugin directory, or re-run with a different --name.",
                plugin_path=target_dir,
                uproject_path=self.uproject_file,
            )
        
        try:
            shutil.copytree(source_path, target_dir)
        except Exception as exc:
            partial_state = target_dir.exists()
            return PluginMutationResult(
                success=False,
                summary="Plugin install failed.",
                detail=f"Copy operation failed: {exc}",
                plugin_state=(
                    f"Partial local plugin files may remain at {target_dir}."
                    if partial_state
                    else "No plugin files were copied."
                ),
                uproject_state=".uproject was not modified.",
                manual_recovery=(
                    "Delete the partially copied plugin directory and retry."
                    if partial_state
                    else "Verify the source path is readable and try again."
                ),
                plugin_path=target_dir,
                uproject_path=self.uproject_file,
                partial_state_possible=partial_state,
            )

        return PluginMutationResult(
            success=True,
            summary="Plugin installed.",
            detail=f"Copied plugin files into {target_dir}.",
            plugin_state="Plugin files were written under the local Plugins directory.",
            uproject_state=".uproject was not modified. Enable the plugin separately if needed.",
            plugin_path=target_dir,
            uproject_path=self.uproject_file,
        )
    
    def enable_plugin(self, plugin_name: str) -> PluginMutationResult:
        """
        Enable a plugin in .uproject file.
        
        Args:
            plugin_name: Name of plugin to enable
            
        Returns:
            PluginMutationResult: Structured mutation outcome
        """
        if not self.uproject_file:
            return PluginMutationResult(
                success=False,
                summary="Plugin enable failed.",
                detail="No .uproject file was found in the project root.",
                plugin_state="No plugin files were copied or deleted.",
                uproject_state=".uproject could not be updated because no project file was found.",
                manual_recovery="Run this command from a valid Unreal project root or pass --path to one.",
            )
        
        try:
            data = self._load_uproject_data()
            
            # Find or add plugin entry
            plugins = data.get('Plugins', [])
            if not isinstance(plugins, list):
                return PluginMutationResult(
                    success=False,
                    summary="Plugin enable failed.",
                    detail=f"The Plugins section in {self.uproject_file.name} is not a list.",
                    plugin_state="No plugin files were copied or deleted.",
                    uproject_state=".uproject was not modified.",
                    manual_recovery="Repair the Plugins section in the .uproject file and retry.",
                    uproject_path=self.uproject_file,
                )

            plugin_entry = next(
                (p for p in plugins if isinstance(p, dict) and p.get('Name') == plugin_name),
                None,
            )
            
            if plugin_entry:
                if plugin_entry.get('Enabled') is True:
                    return PluginMutationResult(
                        success=True,
                        summary=f"Plugin '{plugin_name}' is already enabled.",
                        detail="No additional .uproject changes were required.",
                        plugin_state="No plugin files were copied or deleted.",
                        uproject_state=f"{self.uproject_file.name} was not modified.",
                        uproject_path=self.uproject_file,
                    )
                plugin_entry['Enabled'] = True
            else:
                plugins.append({'Name': plugin_name, 'Enabled': True})
            
            data['Plugins'] = plugins
            self._write_uproject_data(data)

            return PluginMutationResult(
                success=True,
                summary=f"Enabled plugin: {plugin_name}",
                detail=f"Updated {self.uproject_file.name}.",
                plugin_state="No plugin files were copied or deleted.",
                uproject_state=".uproject was modified locally only.",
                uproject_path=self.uproject_file,
            )
        except json.JSONDecodeError as exc:
            return PluginMutationResult(
                success=False,
                summary="Plugin enable failed.",
                detail=f"Could not parse {self.uproject_file.name}: {exc}",
                plugin_state="No plugin files were copied or deleted.",
                uproject_state=".uproject was not modified.",
                manual_recovery="Fix the JSON syntax in the .uproject file and retry.",
                uproject_path=self.uproject_file,
            )
        except Exception as exc:
            return PluginMutationResult(
                success=False,
                summary="Plugin enable failed.",
                detail=f"Failed while updating {self.uproject_file.name}: {exc}",
                plugin_state="No plugin files were copied or deleted.",
                uproject_state=".uproject may be unchanged; UnrealMate uses an atomic rewrite to reduce partial writes.",
                manual_recovery="Check filesystem permissions and retry.",
                uproject_path=self.uproject_file,
            )
    
    def disable_plugin(self, plugin_name: str) -> PluginMutationResult:
        """
        Disable a plugin in .uproject file.
        
        Args:
            plugin_name: Name of plugin to disable
            
        Returns:
            PluginMutationResult: Structured mutation outcome
        """
        if not self.uproject_file:
            return PluginMutationResult(
                success=False,
                summary="Plugin disable failed.",
                detail="No .uproject file was found in the project root.",
                plugin_state="No plugin files were copied or deleted.",
                uproject_state=".uproject could not be updated because no project file was found.",
                manual_recovery="Run this command from a valid Unreal project root or pass --path to one.",
            )
        
        try:
            data = self._load_uproject_data()
            
            plugins = data.get('Plugins', [])
            if not isinstance(plugins, list):
                return PluginMutationResult(
                    success=False,
                    summary="Plugin disable failed.",
                    detail=f"The Plugins section in {self.uproject_file.name} is not a list.",
                    plugin_state="No plugin files were copied or deleted.",
                    uproject_state=".uproject was not modified.",
                    manual_recovery="Repair the Plugins section in the .uproject file and retry.",
                    uproject_path=self.uproject_file,
                )

            plugin_entry = next(
                (p for p in plugins if isinstance(p, dict) and p.get('Name') == plugin_name),
                None,
            )
            
            if plugin_entry is None:
                return PluginMutationResult(
                    success=False,
                    summary="Plugin disable failed.",
                    detail=f"No .uproject entry for '{plugin_name}' was found, so nothing was disabled.",
                    plugin_state="No plugin files were copied or deleted.",
                    uproject_state=f"{self.uproject_file.name} was not modified.",
                    manual_recovery="Add or edit the plugin entry in the .uproject file manually if you need it explicitly disabled.",
                    uproject_path=self.uproject_file,
                )

            if plugin_entry.get('Enabled') is False:
                return PluginMutationResult(
                    success=True,
                    summary=f"Plugin '{plugin_name}' is already disabled.",
                    detail="No additional .uproject changes were required.",
                    plugin_state="No plugin files were copied or deleted.",
                    uproject_state=f"{self.uproject_file.name} was not modified.",
                    uproject_path=self.uproject_file,
                )

            plugin_entry['Enabled'] = False
            
            data['Plugins'] = plugins
            self._write_uproject_data(data)

            return PluginMutationResult(
                success=True,
                summary=f"Disabled plugin: {plugin_name}",
                detail=f"Updated {self.uproject_file.name}.",
                plugin_state="No plugin files were copied or deleted.",
                uproject_state=".uproject was modified locally only.",
                uproject_path=self.uproject_file,
            )
        except json.JSONDecodeError as exc:
            return PluginMutationResult(
                success=False,
                summary="Plugin disable failed.",
                detail=f"Could not parse {self.uproject_file.name}: {exc}",
                plugin_state="No plugin files were copied or deleted.",
                uproject_state=".uproject was not modified.",
                manual_recovery="Fix the JSON syntax in the .uproject file and retry.",
                uproject_path=self.uproject_file,
            )
        except Exception as exc:
            return PluginMutationResult(
                success=False,
                summary="Plugin disable failed.",
                detail=f"Failed while updating {self.uproject_file.name}: {exc}",
                plugin_state="No plugin files were copied or deleted.",
                uproject_state=".uproject may be unchanged; UnrealMate uses an atomic rewrite to reduce partial writes.",
                manual_recovery="Check filesystem permissions and retry.",
                uproject_path=self.uproject_file,
            )
    
    def remove_plugin(self, plugin_name: str) -> PluginMutationResult:
        """
        Remove a plugin from project.
        
        Args:
            plugin_name: Name of plugin to remove
            
        Returns:
            PluginMutationResult: Structured mutation outcome
        """
        plugins = self.list_plugins()
        plugin = next(
            (
                p
                for p in plugins
                if p.name == plugin_name or p.path.name == plugin_name
            ),
            None,
        )
        uproject_reference = self._uproject_references_plugin(plugin_name)
        
        if not plugin:
            return PluginMutationResult(
                success=False,
                summary="Plugin remove failed.",
                detail=f"No local plugin directory named '{plugin_name}' was found.",
                plugin_state="No plugin files were deleted.",
                uproject_state=(
                    f".uproject plugin references are not removed automatically; {self.uproject_file.name} may still reference this plugin."
                    if uproject_reference and self.uproject_file
                    else ".uproject was not modified."
                ),
                manual_recovery=(
                    f"Remove or edit the '{plugin_name}' entry in {self.uproject_file.name} manually."
                    if uproject_reference and self.uproject_file
                    else "Verify the plugin name or inspect the Plugins directory manually."
                ),
                uproject_path=self.uproject_file,
            )
        
        try:
            shutil.rmtree(plugin.path)
            return PluginMutationResult(
                success=True,
                summary=f"Removed plugin: {plugin_name}",
                detail=f"Deleted local plugin files from {plugin.path}.",
                plugin_state="The local plugin directory was deleted.",
                uproject_state=(
                    f".uproject plugin references are not removed automatically; {self.uproject_file.name} may still reference this plugin."
                    if uproject_reference and self.uproject_file
                    else ".uproject plugin references are not removed automatically; no matching reference was found."
                ),
                manual_recovery=(
                    f"Update {self.uproject_file.name} manually if you also want to remove the plugin reference."
                    if uproject_reference and self.uproject_file
                    else ""
                ),
                plugin_path=plugin.path,
                uproject_path=self.uproject_file,
            )
        except Exception as exc:
            partial_state = plugin.path.exists()
            return PluginMutationResult(
                success=False,
                summary="Plugin remove failed.",
                detail=f"Could not delete {plugin.path}: {exc}",
                plugin_state=(
                    f"Plugin files may still remain under {plugin.path}."
                    if partial_state
                    else "Plugin file deletion did not complete."
                ),
                uproject_state=".uproject was not modified.",
                manual_recovery="Inspect the plugin directory, remove any remaining files manually, and retry.",
                plugin_path=plugin.path,
                uproject_path=self.uproject_file,
                partial_state_possible=partial_state,
            )
    
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
        
        from unrealmate.core import visuals

        table = Table(box=visuals.ROUNDED)
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


# © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers

