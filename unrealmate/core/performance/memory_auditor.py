"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - memory_auditor.py                            ║
║                                                                              ║
║  Author: G & E ZYNTH                                                           ║
║  Purpose: Memory usage tracking and leak detection                          ║
║  Created: 2026-01-23                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Memory auditing system for Unreal Engine projects.
Tracks asset memory usage and identifies potential leaks.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from rich.table import Table
from rich.console import Console


@dataclass
class MemoryAsset:
    """Asset memory information."""
    path: Path
    name: str
    size_bytes: int
    estimated_memory_mb: float
    category: str
    priority: str  # High, Medium, Low


class MemoryAuditor:
    """Unreal Engine memory auditor."""
    
    def __init__(self, project_root: Path):
        """
        Initialize memory auditor.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.content_dir = project_root / "Content"
        self.assets: List[MemoryAsset] = []
    
    def estimate_runtime_memory(self, file_path: Path) -> float:
        """
        Estimate runtime memory usage from file size.
        
        Args:
            file_path: Path to asset file
            
        Returns:
            float: Estimated memory in MB
        """
        size_bytes = file_path.stat().st_size
        ext = file_path.suffix.lower()
        
        # Estimation multipliers based on asset type
        multipliers = {
            '.uasset': 1.5,  # Blueprints, materials
            '.umap': 2.0,    # Maps load more into memory
            '.png': 4.0,     # Uncompressed in memory
            '.tga': 4.0,
            '.exr': 6.0,     # HDR textures
            '.hdr': 6.0,
            '.wav': 1.0,     # Audio roughly same size
            '.fbx': 3.0,     # Meshes with vertex data
        }
        
        multiplier = multipliers.get(ext, 1.0)
        estimated_mb = (size_bytes / (1024 * 1024)) * multiplier
        
        return estimated_mb
    
    def categorize_asset(self, file_path: Path) -> str:
        """Categorize asset by file extension."""
        ext = file_path.suffix.lower()
        
        if ext in ['.uasset', '.umap']:
            return 'Blueprint/Map'
        elif ext in ['.png', '.tga', '.jpg', '.jpeg', '.exr', '.hdr']:
            return 'Texture'
        elif ext in ['.wav', '.mp3', '.ogg']:
            return 'Audio'
        elif ext in ['.fbx', '.obj']:
            return 'Mesh'
        else:
            return 'Other'
    
    def assess_priority(self, estimated_mb: float) -> str:
        """Assess optimization priority based on memory usage."""
        if estimated_mb > 100:
            return 'High'
        elif estimated_mb > 50:
            return 'Medium'
        else:
            return 'Low'
    
    def scan_assets(self) -> List[MemoryAsset]:
        """
        Scan all assets and estimate memory usage.
        
        Returns:
            List[MemoryAsset]: List of assets with memory info
        """
        self.assets = []
        
        if not self.content_dir.exists():
            return self.assets
        
        # Scan for assets
        asset_extensions = [
            '*.uasset', '*.umap',
            '*.png', '*.tga', '*.jpg', '*.jpeg', '*.exr', '*.hdr',
            '*.wav', '*.mp3', '*.ogg',
            '*.fbx', '*.obj'
        ]
        
        for ext in asset_extensions:
            for file_path in self.content_dir.rglob(ext):
                estimated_mb = self.estimate_runtime_memory(file_path)
                category = self.categorize_asset(file_path)
                priority = self.assess_priority(estimated_mb)
                
                asset = MemoryAsset(
                    path=file_path,
                    name=file_path.name,
                    size_bytes=file_path.stat().st_size,
                    estimated_memory_mb=estimated_mb,
                    category=category,
                    priority=priority
                )
                self.assets.append(asset)
        
        # Sort by estimated memory
        self.assets.sort(key=lambda x: x.estimated_memory_mb, reverse=True)
        
        return self.assets
    
    def generate_report(self, console: Optional[Console] = None) -> None:
        """
        Generate and print memory audit report.
        
        Args:
            console: Rich Console instance
        """
        if console is None:
            console = Console()
        
        console.print("\n[bold cyan]Memory Audit Report[/]\n")
        
        if not self.assets:
            console.print("[yellow]No assets found to audit.[/]\n")
            return
        
        # Calculate statistics
        total_disk_mb = sum(a.size_bytes for a in self.assets) / (1024 * 1024)
        total_memory_mb = sum(a.estimated_memory_mb for a in self.assets)
        high_priority = [a for a in self.assets if a.priority == 'High']
        
        # Summary
        console.print(f"Total Assets: [cyan]{len(self.assets)}[/]")
        console.print(f"Disk Usage: [cyan]{total_disk_mb:.2f} MB[/]")
        console.print(f"Estimated Runtime Memory: [yellow]{total_memory_mb:.2f} MB[/]")
        console.print(f"High Priority Assets: [red]{len(high_priority)}[/]\n")
        
        # Top memory consumers
        console.print("[bold]🔝 Top 15 Memory Consumers[/]\n")
        
        table = Table()
        table.add_column("Asset", style="cyan", no_wrap=True)
        table.add_column("Category", style="magenta")
        table.add_column("Disk Size", justify="right")
        table.add_column("Est. Memory", justify="right")
        table.add_column("Priority", justify="center")
        
        for asset in self.assets[:15]:
            priority_color = {
                'High': 'red',
                'Medium': 'yellow',
                'Low': 'green'
            }.get(asset.priority, 'white')
            
            table.add_row(
                asset.name,
                asset.category,
                f"{asset.size_bytes / (1024 * 1024):.2f} MB",
                f"{asset.estimated_memory_mb:.2f} MB",
                f"[{priority_color}]{asset.priority}[/]"
            )
        
        console.print(table)
        
        # Optimization suggestions
        if high_priority:
            console.print("\n[bold yellow]💡 Optimization Suggestions[/]\n")
            
            texture_count = len([a for a in high_priority if a.category == 'Texture'])
            if texture_count > 0:
                console.print(f"• [yellow]{texture_count} large textures detected[/]")
                console.print("  → Enable texture streaming")
                console.print("  → Reduce texture resolution")
                console.print("  → Use texture compression\n")
            
            mesh_count = len([a for a in high_priority if a.category == 'Mesh'])
            if mesh_count > 0:
                console.print(f"• [yellow]{mesh_count} large meshes detected[/]")
                console.print("  → Use LODs (Level of Detail)")
                console.print("  → Reduce polygon count")
                console.print("  → Enable mesh streaming\n")
            
            audio_count = len([a for a in high_priority if a.category == 'Audio'])
            if audio_count > 0:
                console.print(f"• [yellow]{audio_count} large audio files detected[/]")
                console.print("  → Use audio compression")
                console.print("  → Enable audio streaming")
                console.print("  → Reduce sample rate\n")


# © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers

