"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Plugin Architecture                          ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Extensibility and plugin management                                ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import importlib.util
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Type

from rich.console import Console

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# PLUGIN BASE CLASS
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    author: str
    description: str
    requires: list[str] = field(default_factory=list)
    hooks: list[str] = field(default_factory=list)


class UnrealMatePlugin(ABC):
    """Base class for all UnrealMate plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    def on_load(self) -> None:
        """Called when plugin is loaded."""
        pass

    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        pass

    def on_command_start(self, command: str, args: dict[str, Any]) -> None:
        """Called before a command executes."""
        pass

    def on_command_end(self, command: str, result: Any) -> None:
        """Called after a command executes."""
        pass

    def register_commands(self) -> list[dict[str, Any]]:
        """Return list of commands to register."""
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# PLUGIN MANAGER
# ═══════════════════════════════════════════════════════════════════════════════


class PluginManager:
    """Manages plugin loading, unloading, and lifecycle."""

    def __init__(self, plugin_dir: Optional[Path] = None):
        self.plugin_dir = plugin_dir or Path.home() / ".unrealmate" / "plugins"
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self._plugins: dict[str, UnrealMatePlugin] = {}
        self._hooks: dict[str, list[Callable[..., Any]]] = {}

    def discover_plugins(self) -> list[Path]:
        """
        Discover available plugins.

        Returns:
            List of plugin file paths
        """
        plugins = []
        for path in self.plugin_dir.glob("*.py"):
            if not path.name.startswith("_"):
                plugins.append(path)

        # Also check for plugin packages
        for path in self.plugin_dir.iterdir():
            if path.is_dir() and (path / "__init__.py").exists():
                plugins.append(path / "__init__.py")

        return plugins

    def load_plugin(self, path: Path) -> Optional[UnrealMatePlugin]:
        """
        Load a plugin from a file.

        Args:
            path: Path to plugin file

        Returns:
            Loaded plugin instance or None
        """
        try:
            # Load module
            spec = importlib.util.spec_from_file_location(
                f"unrealmate_plugin_{path.stem}",
                path
            )
            if spec is None or spec.loader is None:
                console.print(f"[red]Could not load plugin: {path}[/red]")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # Find plugin class
            plugin_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (
                    isinstance(item, type)
                    and issubclass(item, UnrealMatePlugin)
                    and item is not UnrealMatePlugin
                ):
                    plugin_class = item
                    break

            if plugin_class is None:
                console.print(f"[yellow]No plugin class found in: {path}[/yellow]")
                return None

            # Instantiate plugin
            plugin = plugin_class()
            plugin.on_load()

            # Register plugin
            name = plugin.metadata.name
            self._plugins[name] = plugin

            # Register hooks
            for hook_name in plugin.metadata.hooks:
                if hook_name not in self._hooks:
                    self._hooks[hook_name] = []
                hook_method = getattr(plugin, f"on_{hook_name}", None)
                if hook_method:
                    self._hooks[hook_name].append(hook_method)

            console.print(f"[green]✓ Loaded plugin: {name} v{plugin.metadata.version}[/green]")
            return plugin

        except Exception as e:
            console.print(f"[red]Error loading plugin {path}: {e}[/red]")
            return None

    def unload_plugin(self, name: str) -> bool:
        """
        Unload a plugin by name.

        Args:
            name: Plugin name

        Returns:
            True if successful
        """
        if name not in self._plugins:
            return False

        plugin = self._plugins[name]
        plugin.on_unload()
        del self._plugins[name]

        console.print(f"[yellow]Unloaded plugin: {name}[/yellow]")
        return True

    def load_all(self) -> int:
        """
        Load all discovered plugins.

        Returns:
            Number of plugins loaded
        """
        count = 0
        for path in self.discover_plugins():
            if self.load_plugin(path):
                count += 1
        return count

    def unload_all(self) -> None:
        """Unload all plugins."""
        for name in list(self._plugins.keys()):
            self.unload_plugin(name)

    def get_plugin(self, name: str) -> Optional[UnrealMatePlugin]:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[PluginMetadata]:
        """List all loaded plugins."""
        return [p.metadata for p in self._plugins.values()]

    def trigger_hook(self, hook_name: str, *args: Any, **kwargs: Any) -> list[Any]:
        """
        Trigger a hook and collect results.

        Args:
            hook_name: Name of the hook
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            List of results from hook handlers
        """
        results = []
        for handler in self._hooks.get(hook_name, []):
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                console.print(f"[red]Hook error ({hook_name}): {e}[/red]")
        return results

    def register_hook(self, hook_name: str, handler: Callable[..., Any]) -> None:
        """
        Register a hook handler.

        Args:
            hook_name: Name of the hook
            handler: Handler function
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(handler)


# ═══════════════════════════════════════════════════════════════════════════════
# PLUGIN TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════════


PLUGIN_TEMPLATE = '''"""
UnrealMate Plugin: {name}

Author: {author}
Description: {description}
"""

from unrealmate.core.plugin_system import UnrealMatePlugin, PluginMetadata


class {class_name}(UnrealMatePlugin):
    """Custom plugin for UnrealMate."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="{name}",
            version="1.0.0",
            author="{author}",
            description="{description}",
            requires=[],
            hooks=["command_start", "command_end"],
        )

    def on_load(self) -> None:
        """Called when plugin is loaded."""
        print(f"Plugin {self.metadata.name} loaded!")

    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        print(f"Plugin {self.metadata.name} unloaded!")

    def on_command_start(self, command: str, args: dict) -> None:
        """Called before a command executes."""
        pass

    def on_command_end(self, command: str, result) -> None:
        """Called after a command executes."""
        pass
'''


def create_plugin_template(
    name: str,
    author: str = "gktrk363",
    description: str = "A custom UnrealMate plugin",
    output_dir: Optional[Path] = None,
) -> Path:
    """
    Create a plugin template file.

    Args:
        name: Plugin name
        author: Plugin author
        description: Plugin description
        output_dir: Output directory

    Returns:
        Path to created plugin file
    """
    output_dir = output_dir or Path.home() / ".unrealmate" / "plugins"
    output_dir.mkdir(parents=True, exist_ok=True)

    class_name = "".join(word.title() for word in name.split("_")) + "Plugin"
    content = PLUGIN_TEMPLATE.format(
        name=name,
        author=author,
        description=description,
        class_name=class_name,
    )

    output_path = output_dir / f"{name.lower().replace(' ', '_')}_plugin.py"
    output_path.write_text(content, encoding="utf-8")

    console.print(f"[green]✓ Created plugin template: {output_path}[/green]")
    return output_path


# Global plugin manager
plugin_manager = PluginManager()
