"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Asset Manager                                ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Advanced asset management and optimization tools                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import hashlib
import json
import shutil
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

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
class AssetInfo:
    """Information about a single asset."""
    path: Path
    name: str
    extension: str
    size_bytes: int
    asset_type: str = ""
    dependencies: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)
    is_used: bool = True
    hash: str = ""
    
    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)
    
    @property
    def size_formatted(self) -> str:
        if self.size_bytes < 1024:
            return f"{self.size_bytes} B"
        elif self.size_bytes < 1024 * 1024:
            return f"{self.size_bytes / 1024:.1f} KB"
        else:
            return f"{self.size_mb:.2f} MB"


@dataclass
class TextureInfo(AssetInfo):
    """Extended info for texture assets."""
    width: int = 0
    height: int = 0
    format: str = ""
    has_mipmaps: bool = False
    compression: str = ""
    
    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"
    
    @property
    def is_power_of_two(self) -> bool:
        return (self.width & (self.width - 1) == 0) and (self.height & (self.height - 1) == 0)


@dataclass
class DuplicateGroup:
    """Group of duplicate assets."""
    hash: str
    assets: list[AssetInfo]
    wasted_space_bytes: int
    
    @property
    def count(self) -> int:
        return len(self.assets)
    
    @property
    def wasted_space_mb(self) -> float:
        return self.wasted_space_bytes / (1024 * 1024)


@dataclass
class OptimizationSuggestion:
    """Asset optimization suggestion."""
    category: str  # 'size', 'compression', 'unused', 'duplicate'
    severity: str  # 'info', 'warning', 'error'
    asset: str
    current_value: str
    suggested_value: str
    potential_savings_bytes: int = 0
    
    @property
    def potential_savings_mb(self) -> float:
        return self.potential_savings_bytes / (1024 * 1024)


# ═══════════════════════════════════════════════════════════════════════════════
# ASSET DEPENDENCY TREE
# ═══════════════════════════════════════════════════════════════════════════════


class AssetDependencyTree:
    """Manages asset dependency relationships."""
    
    def __init__(self):
        self._assets: dict[str, AssetInfo] = {}
        self._dependencies: dict[str, set[str]] = defaultdict(set)
        self._dependents: dict[str, set[str]] = defaultdict(set)
    
    def add_asset(self, asset: AssetInfo) -> None:
        """Add an asset to the tree."""
        self._assets[str(asset.path)] = asset
    
    def add_dependency(self, source: str, target: str) -> None:
        """Add a dependency relationship."""
        self._dependencies[source].add(target)
        self._dependents[target].add(source)
    
    def get_dependencies(
        self,
        asset_path: str,
        recursive: bool = False,
    ) -> set[str]:
        """Get dependencies of an asset."""
        if not recursive:
            return self._dependencies.get(asset_path, set())
        
        visited = set()
        to_visit = list(self._dependencies.get(asset_path, set()))
        
        while to_visit:
            dep = to_visit.pop()
            if dep not in visited:
                visited.add(dep)
                to_visit.extend(self._dependencies.get(dep, set()))
        
        return visited
    
    def get_dependents(
        self,
        asset_path: str,
        recursive: bool = False,
    ) -> set[str]:
        """Get assets that depend on this asset."""
        if not recursive:
            return self._dependents.get(asset_path, set())
        
        visited = set()
        to_visit = list(self._dependents.get(asset_path, set()))
        
        while to_visit:
            dep = to_visit.pop()
            if dep not in visited:
                visited.add(dep)
                to_visit.extend(self._dependents.get(dep, set()))
        
        return visited
    
    def find_root_assets(self) -> list[str]:
        """Find assets with no dependents (root assets)."""
        roots = []
        for path in self._assets:
            if not self._dependents.get(path):
                roots.append(path)
        return roots
    
    def find_leaf_assets(self) -> list[str]:
        """Find assets with no dependencies (leaf assets)."""
        leaves = []
        for path in self._assets:
            if not self._dependencies.get(path):
                leaves.append(path)
        return leaves
    
    def visualize(self, root: str, max_depth: int = 3) -> Tree:
        """Create a Rich Tree visualization."""
        tree = Tree(f"[bold cyan]{Path(root).name}[/bold cyan]")
        
        def add_children(parent: Tree, path: str, depth: int) -> None:
            if depth >= max_depth:
                return
            
            deps = self._dependencies.get(path, set())
            for dep in list(deps)[:10]:  # Limit children
                child = parent.add(f"[green]{Path(dep).name}[/green]")
                add_children(child, dep, depth + 1)
            
            if len(deps) > 10:
                parent.add(f"[dim]... and {len(deps) - 10} more[/dim]")
        
        add_children(tree, root, 0)
        return tree


# ═══════════════════════════════════════════════════════════════════════════════
# UNUSED ASSET DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════


class UnusedAssetDetector:
    """Detect unused assets in the project."""
    
    # Files that are always considered "used"
    ALWAYS_USED = {
        "DefaultEngine.ini",
        "DefaultGame.ini",
        "DefaultInput.ini",
        "DefaultEditor.ini",
    }
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.content_path = project_path / "Content"
        self.dependency_tree = AssetDependencyTree()
    
    def scan(self) -> list[AssetInfo]:
        """Scan for all assets."""
        assets = []
        
        if not self.content_path.exists():
            return assets
        
        for file_path in self.content_path.rglob("*"):
            if file_path.is_file():
                asset = AssetInfo(
                    path=file_path,
                    name=file_path.stem,
                    extension=file_path.suffix,
                    size_bytes=file_path.stat().st_size,
                    asset_type=self._get_asset_type(file_path),
                )
                assets.append(asset)
                self.dependency_tree.add_asset(asset)
        
        return assets
    
    def _get_asset_type(self, path: Path) -> str:
        """Determine asset type from extension."""
        ext = path.suffix.lower()
        type_map = {
            ".uasset": "Asset",
            ".umap": "Map",
            ".png": "Texture",
            ".jpg": "Texture",
            ".tga": "Texture",
            ".wav": "Audio",
            ".mp3": "Audio",
            ".ogg": "Audio",
            ".fbx": "Mesh",
            ".obj": "Mesh",
        }
        return type_map.get(ext, "Other")
    
    def find_unused(self, reference_maps: Optional[list[Path]] = None) -> list[AssetInfo]:
        """Find assets that are not referenced by any map or other asset."""
        # Get all root assets (assets with no dependents)
        root_paths = set(self.dependency_tree.find_root_assets())
        
        # If we have reference maps, mark those as used
        used_paths: set[str] = set()
        
        if reference_maps:
            for map_path in reference_maps:
                used_paths.add(str(map_path))
                # Get all dependencies of this map
                deps = self.dependency_tree.get_dependencies(str(map_path), recursive=True)
                used_paths.update(deps)
        
        # Find unused assets
        unused = []
        for path, asset in self.dependency_tree._assets.items():
            if path not in used_paths and asset.name not in self.ALWAYS_USED:
                asset.is_used = False
                unused.append(asset)
        
        return unused
    
    def estimate_savings(self, unused_assets: list[AssetInfo]) -> int:
        """Estimate space savings from removing unused assets."""
        return sum(a.size_bytes for a in unused_assets)


# ═══════════════════════════════════════════════════════════════════════════════
# DUPLICATE ASSET FINDER
# ═══════════════════════════════════════════════════════════════════════════════


class DuplicateAssetFinder:
    """Find duplicate assets in the project."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.content_path = project_path / "Content"
    
    def find_duplicates(
        self,
        by_content: bool = True,
        by_name: bool = False,
    ) -> list[DuplicateGroup]:
        """Find duplicate assets."""
        if by_content:
            return self._find_by_content()
        elif by_name:
            return self._find_by_name()
        return []
    
    def _find_by_content(self) -> list[DuplicateGroup]:
        """Find duplicates by file content hash."""
        hash_map: dict[str, list[AssetInfo]] = defaultdict(list)
        
        if not self.content_path.exists():
            return []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Scanning for duplicates..."),
            console=console,
        ) as progress:
            task = progress.add_task("Hashing", total=None)
            
            for file_path in self.content_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in {".uasset", ".png", ".jpg", ".wav"}:
                    file_hash = self._hash_file(file_path)
                    
                    asset = AssetInfo(
                        path=file_path,
                        name=file_path.stem,
                        extension=file_path.suffix,
                        size_bytes=file_path.stat().st_size,
                        hash=file_hash,
                    )
                    hash_map[file_hash].append(asset)
        
        # Filter to only groups with duplicates
        duplicates = []
        for file_hash, assets in hash_map.items():
            if len(assets) > 1:
                wasted = sum(a.size_bytes for a in assets[1:])  # First one is "original"
                duplicates.append(DuplicateGroup(
                    hash=file_hash,
                    assets=assets,
                    wasted_space_bytes=wasted,
                ))
        
        return sorted(duplicates, key=lambda d: d.wasted_space_bytes, reverse=True)
    
    def _find_by_name(self) -> list[DuplicateGroup]:
        """Find duplicates by file name."""
        name_map: dict[str, list[AssetInfo]] = defaultdict(list)
        
        if not self.content_path.exists():
            return []
        
        for file_path in self.content_path.rglob("*"):
            if file_path.is_file():
                asset = AssetInfo(
                    path=file_path,
                    name=file_path.stem,
                    extension=file_path.suffix,
                    size_bytes=file_path.stat().st_size,
                )
                name_map[file_path.name].append(asset)
        
        duplicates = []
        for name, assets in name_map.items():
            if len(assets) > 1:
                wasted = sum(a.size_bytes for a in assets[1:])
                duplicates.append(DuplicateGroup(
                    hash=name,
                    assets=assets,
                    wasted_space_bytes=wasted,
                ))
        
        return sorted(duplicates, key=lambda d: d.wasted_space_bytes, reverse=True)
    
    def _hash_file(self, path: Path, chunk_size: int = 8192) -> str:
        """Calculate MD5 hash of a file."""
        hasher = hashlib.md5()
        
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        
        return hasher.hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# TEXTURE COMPRESSION ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════


class TextureCompressionAnalyzer:
    """Analyze texture compression and suggest optimizations."""
    
    # Recommended compression formats
    COMPRESSION_RECOMMENDATIONS = {
        "normal_map": "BC5",
        "diffuse": "BC1",
        "diffuse_alpha": "BC3",
        "hdr": "BC6H",
        "ui": "BC7",
        "mask": "BC4",
    }
    
    # Maximum recommended sizes
    SIZE_LIMITS = {
        "ui": 512,
        "icon": 256,
        "diffuse": 2048,
        "normal": 2048,
        "detail": 1024,
    }
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.content_path = project_path / "Content"
    
    def scan_textures(self) -> list[TextureInfo]:
        """Scan for texture assets."""
        textures = []
        
        if not self.content_path.exists():
            return textures
        
        texture_extensions = {".png", ".jpg", ".jpeg", ".tga", ".bmp", ".psd"}
        
        for file_path in self.content_path.rglob("*"):
            if file_path.suffix.lower() in texture_extensions:
                texture = TextureInfo(
                    path=file_path,
                    name=file_path.stem,
                    extension=file_path.suffix,
                    size_bytes=file_path.stat().st_size,
                    asset_type="Texture",
                )
                textures.append(texture)
        
        return textures
    
    def analyze(self, textures: list[TextureInfo]) -> list[OptimizationSuggestion]:
        """Analyze textures and generate optimization suggestions."""
        suggestions = []
        
        for texture in textures:
            # Check for non-power-of-two textures
            if texture.width > 0 and not texture.is_power_of_two:
                suggestions.append(OptimizationSuggestion(
                    category="compression",
                    severity="warning",
                    asset=texture.name,
                    current_value=texture.resolution,
                    suggested_value="Power of 2 (e.g., 1024x1024)",
                    potential_savings_bytes=0,
                ))
            
            # Check for oversized textures
            if texture.size_bytes > 50 * 1024 * 1024:  # > 50 MB
                suggestions.append(OptimizationSuggestion(
                    category="size",
                    severity="error",
                    asset=texture.name,
                    current_value=texture.size_formatted,
                    suggested_value="< 50 MB",
                    potential_savings_bytes=texture.size_bytes - (50 * 1024 * 1024),
                ))
            
            # Check for uncompressed textures (by file extension)
            if texture.extension.lower() in {".bmp", ".psd"}:
                suggestions.append(OptimizationSuggestion(
                    category="compression",
                    severity="warning",
                    asset=texture.name,
                    current_value=f"Uncompressed ({texture.extension})",
                    suggested_value="PNG or compressed format",
                    potential_savings_bytes=int(texture.size_bytes * 0.7),
                ))
        
        return sorted(suggestions, key=lambda s: s.potential_savings_bytes, reverse=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ASSET MIGRATION TOOL
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class MigrationResult:
    """Result of an asset migration operation."""
    source: Path
    destination: Path
    success: bool
    error: Optional[str] = None
    files_copied: int = 0
    total_size_bytes: int = 0


class AssetMigrationTool:
    """Migrate assets between projects."""
    
    def __init__(self, source_project: Path, target_project: Path):
        self.source_project = source_project
        self.target_project = target_project
        self.source_content = source_project / "Content"
        self.target_content = target_project / "Content"
    
    def migrate_asset(
        self,
        asset_path: Path,
        include_dependencies: bool = True,
        dry_run: bool = False,
    ) -> MigrationResult:
        """Migrate a single asset to the target project."""
        result = MigrationResult(
            source=asset_path,
            destination=self._get_target_path(asset_path),
            success=False,
        )
        
        if not asset_path.exists():
            result.error = "Source asset not found"
            return result
        
        try:
            if not dry_run:
                result.destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(asset_path, result.destination)
            
            result.success = True
            result.files_copied = 1
            result.total_size_bytes = asset_path.stat().st_size
            
        except Exception as e:
            result.error = str(e)
        
        return result
    
    def migrate_folder(
        self,
        folder_path: Path,
        dry_run: bool = False,
    ) -> list[MigrationResult]:
        """Migrate an entire folder of assets."""
        results = []
        
        if not folder_path.exists():
            return results
        
        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                result = self.migrate_asset(file_path, dry_run=dry_run)
                results.append(result)
        
        return results
    
    def _get_target_path(self, source_path: Path) -> Path:
        """Calculate target path for a source asset."""
        relative = source_path.relative_to(self.source_content)
        return self.target_content / relative
    
    def preview_migration(self, asset_paths: list[Path]) -> Table:
        """Create a preview table of the migration."""
        table = Table(title="Migration Preview")
        table.add_column("Source", style="cyan")
        table.add_column("Destination", style="green")
        table.add_column("Size")
        table.add_column("Status")
        
        for path in asset_paths:
            if path.exists():
                target = self._get_target_path(path)
                status = "✓ Ready" if not target.exists() else "⚠️ Exists"
                size = path.stat().st_size
                table.add_row(
                    path.name,
                    str(target.relative_to(self.target_project)),
                    f"{size / 1024:.1f} KB",
                    status,
                )
            else:
                table.add_row(path.name, "-", "-", "[red]✗ Not found[/red]")
        
        return table


# ═══════════════════════════════════════════════════════════════════════════════
# ASSET MANAGER (MAIN CLASS)
# ═══════════════════════════════════════════════════════════════════════════════


class AssetManager:
    """Main class for asset management operations."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.content_path = project_path / "Content"
        self.dependency_tree = AssetDependencyTree()
        self.assets: list[AssetInfo] = []
    
    def scan(self) -> list[AssetInfo]:
        """Scan all assets in the project."""
        self.assets = []
        
        if not self.content_path.exists():
            console.print("[yellow]Content folder not found[/yellow]")
            return self.assets
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Scanning assets..."),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning", total=None)
            
            for file_path in self.content_path.rglob("*"):
                if file_path.is_file():
                    asset = AssetInfo(
                        path=file_path,
                        name=file_path.stem,
                        extension=file_path.suffix,
                        size_bytes=file_path.stat().st_size,
                        asset_type=self._get_asset_type(file_path),
                    )
                    self.assets.append(asset)
                    self.dependency_tree.add_asset(asset)
        
        return self.assets
    
    def _get_asset_type(self, path: Path) -> str:
        """Determine asset type from extension."""
        ext = path.suffix.lower()
        type_map = {
            ".uasset": "Asset",
            ".umap": "Map",
            ".png": "Texture",
            ".jpg": "Texture",
            ".tga": "Texture",
            ".wav": "Audio",
            ".mp3": "Audio",
            ".ogg": "Audio",
            ".fbx": "Mesh",
            ".obj": "Mesh",
        }
        return type_map.get(ext, "Other")
    
    def find_unused(self) -> list[AssetInfo]:
        """Find unused assets."""
        detector = UnusedAssetDetector(self.project_path)
        detector.dependency_tree = self.dependency_tree
        return detector.find_unused()
    
    def find_duplicates(self) -> list[DuplicateGroup]:
        """Find duplicate assets."""
        finder = DuplicateAssetFinder(self.project_path)
        return finder.find_duplicates()
    
    def analyze_textures(self) -> list[OptimizationSuggestion]:
        """Analyze textures for optimization opportunities."""
        analyzer = TextureCompressionAnalyzer(self.project_path)
        textures = analyzer.scan_textures()
        return analyzer.analyze(textures)
    
    def get_size_report(self) -> dict[str, Any]:
        """Get a report of asset sizes by type."""
        size_by_type: dict[str, int] = defaultdict(int)
        count_by_type: dict[str, int] = defaultdict(int)
        
        for asset in self.assets:
            size_by_type[asset.asset_type] += asset.size_bytes
            count_by_type[asset.asset_type] += 1
        
        total_size = sum(size_by_type.values())
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "total_assets": len(self.assets),
            "by_type": {
                asset_type: {
                    "count": count_by_type[asset_type],
                    "size_bytes": size,
                    "size_mb": size / (1024 * 1024),
                    "percentage": (size / total_size * 100) if total_size > 0 else 0,
                }
                for asset_type, size in size_by_type.items()
            },
        }
    
    def print_size_table(self) -> None:
        """Print asset size breakdown as a table."""
        report = self.get_size_report()
        
        table = Table(title="Asset Size Report")
        table.add_column("Type", style="cyan")
        table.add_column("Count", justify="right")
        table.add_column("Size", justify="right")
        table.add_column("Percentage", justify="right")
        
        for asset_type, data in sorted(
            report["by_type"].items(),
            key=lambda x: x[1]["size_bytes"],
            reverse=True,
        ):
            table.add_row(
                asset_type,
                str(data["count"]),
                f"{data['size_mb']:.2f} MB",
                f"{data['percentage']:.1f}%",
            )
        
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{report['total_assets']}[/bold]",
            f"[bold]{report['total_size_mb']:.2f} MB[/bold]",
            "[bold]100%[/bold]",
        )
        
        console.print(table)
