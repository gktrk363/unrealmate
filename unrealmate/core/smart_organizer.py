"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       UnrealMate - Smart Organizer                           ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  Purpose: Smart asset organization and management                            ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
Auto-categorizes, organizes, and enforces naming conventions.
"""

import re
import shutil
import logging
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class AssetCategory(Enum):
    """Asset categories for organization."""
    BLUEPRINTS = "Blueprints"
    MESHES = "Meshes"
    MATERIALS = "Materials"
    TEXTURES = "Textures"
    ANIMATIONS = "Animations"
    AUDIO = "Audio"
    UI = "UI"
    PARTICLES = "Particles"
    DATA = "Data"
    MISC = "Misc"


@dataclass
class AssetInfo:
    """Information about an asset."""
    path: Path
    name: str
    extension: str
    size_bytes: int
    category: AssetCategory
    suggested_folder: str
    needs_rename: bool = False
    suggested_name: Optional[str] = None
    
    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)
    
    def to_dict(self) -> Dict:
        return {
            "path": str(self.path),
            "name": self.name,
            "extension": self.extension,
            "size_mb": round(self.size_mb, 2),
            "category": self.category.value,
            "suggested_folder": self.suggested_folder,
            "needs_rename": self.needs_rename,
            "suggested_name": self.suggested_name,
        }


@dataclass
class OrganizationPlan:
    """Plan for organizing assets."""
    moves: List[Tuple[Path, Path]]
    renames: List[Tuple[Path, str]]
    new_folders: List[Path]
    total_assets: int
    assets_to_move: int
    assets_to_rename: int
    
    def to_dict(self) -> Dict:
        return {
            "total_assets": self.total_assets,
            "assets_to_move": self.assets_to_move,
            "assets_to_rename": self.assets_to_rename,
            "new_folders": [str(p) for p in self.new_folders],
            "moves": [(str(s), str(d)) for s, d in self.moves[:20]],  # Limit for readability
            "renames": [(str(p), n) for p, n in self.renames[:20]],
        }


class AssetCategorizer:
    """
    Categorizes assets based on file extensions and naming patterns.
    """
    
    # Extension to category mapping
    EXTENSION_MAP = {
        # Blueprints
        ".uasset": AssetCategory.BLUEPRINTS,
    }
    
    # Prefix to category mapping
    PREFIX_MAP = {
        "BP_": AssetCategory.BLUEPRINTS,
        "SM_": AssetCategory.MESHES,
        "SK_": AssetCategory.MESHES,
        "T_": AssetCategory.TEXTURES,
        "M_": AssetCategory.MATERIALS,
        "MI_": AssetCategory.MATERIALS,
        "ABP_": AssetCategory.ANIMATIONS,
        "A_": AssetCategory.ANIMATIONS,
        "AM_": AssetCategory.ANIMATIONS,
        "S_": AssetCategory.AUDIO,
        "SC_": AssetCategory.AUDIO,
        "WBP_": AssetCategory.UI,
        "W_": AssetCategory.UI,
        "PS_": AssetCategory.PARTICLES,
        "NS_": AssetCategory.PARTICLES,
        "P_": AssetCategory.PARTICLES,
        "DT_": AssetCategory.DATA,
        "DA_": AssetCategory.DATA,
        "E_": AssetCategory.DATA,
        "ST_": AssetCategory.DATA,
    }
    
    # Folder keywords that indicate category
    FOLDER_KEYWORDS = {
        AssetCategory.BLUEPRINTS: ["blueprint", "bp", "actor", "character", "player"],
        AssetCategory.MESHES: ["mesh", "static", "skeletal", "model", "3d"],
        AssetCategory.MATERIALS: ["material", "mat", "shader"],
        AssetCategory.TEXTURES: ["texture", "tex", "image"],
        AssetCategory.ANIMATIONS: ["animation", "anim", "montage", "sequence"],
        AssetCategory.AUDIO: ["audio", "sound", "music", "sfx", "voice"],
        AssetCategory.UI: ["ui", "widget", "hud", "menu", "interface"],
        AssetCategory.PARTICLES: ["particle", "vfx", "fx", "niagara", "effect"],
        AssetCategory.DATA: ["data", "table", "config", "setting"],
    }
    
    @classmethod
    def categorize(cls, asset_path: Path) -> AssetCategory:
        """Determine the category of an asset."""
        name = asset_path.stem
        folder = str(asset_path.parent).lower()
        
        # Check prefix first (most reliable)
        for prefix, category in cls.PREFIX_MAP.items():
            if name.startswith(prefix):
                return category
        
        # Check folder keywords
        for category, keywords in cls.FOLDER_KEYWORDS.items():
            for keyword in keywords:
                if keyword in folder:
                    return category
        
        # Check name keywords
        name_lower = name.lower()
        for category, keywords in cls.FOLDER_KEYWORDS.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return category
        
        return AssetCategory.MISC
    
    @classmethod
    def get_suggested_prefix(cls, category: AssetCategory) -> str:
        """Get the suggested prefix for a category."""
        prefix_map = {
            AssetCategory.BLUEPRINTS: "BP_",
            AssetCategory.MESHES: "SM_",
            AssetCategory.MATERIALS: "M_",
            AssetCategory.TEXTURES: "T_",
            AssetCategory.ANIMATIONS: "A_",
            AssetCategory.AUDIO: "S_",
            AssetCategory.UI: "WBP_",
            AssetCategory.PARTICLES: "PS_",
            AssetCategory.DATA: "DT_",
            AssetCategory.MISC: "",
        }
        return prefix_map.get(category, "")


class SmartOrganizer:
    """
    Main smart organization engine.
    Analyzes and organizes Unreal Engine project assets.
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.content_dir = self.project_path / "Content"
        self.assets: List[AssetInfo] = []
        self.categorizer = AssetCategorizer()
        logger.info(f"SmartOrganizer initialized for: {project_path}")
    
    def _get_suggested_folder(self, category: AssetCategory) -> str:
        """Get the suggested folder path for a category."""
        folder_map = {
            AssetCategory.BLUEPRINTS: "Blueprints",
            AssetCategory.MESHES: "Meshes",
            AssetCategory.MATERIALS: "Materials",
            AssetCategory.TEXTURES: "Textures",
            AssetCategory.ANIMATIONS: "Animations",
            AssetCategory.AUDIO: "Audio",
            AssetCategory.UI: "UI",
            AssetCategory.PARTICLES: "Particles",
            AssetCategory.DATA: "Data",
            AssetCategory.MISC: "Misc",
        }
        return folder_map.get(category, "Misc")
    
    def _should_have_prefix(self, name: str) -> bool:
        """Check if an asset name should have a prefix."""
        valid_prefixes = list(AssetCategorizer.PREFIX_MAP.keys())
        return not any(name.startswith(p) for p in valid_prefixes)
    
    def scan_assets(self) -> List[AssetInfo]:
        """Scan all assets in the project."""
        self.assets = []
        
        if not self.content_dir.exists():
            logger.warning("Content directory not found")
            return self.assets
        
        for asset_path in self.content_dir.rglob("*.uasset"):
            try:
                name = asset_path.stem
                category = self.categorizer.categorize(asset_path)
                suggested_folder = self._get_suggested_folder(category)
                
                needs_rename = self._should_have_prefix(name)
                suggested_name = None
                
                if needs_rename:
                    prefix = self.categorizer.get_suggested_prefix(category)
                    if prefix:
                        suggested_name = f"{prefix}{name}"
                
                asset = AssetInfo(
                    path=asset_path,
                    name=name,
                    extension=asset_path.suffix,
                    size_bytes=asset_path.stat().st_size,
                    category=category,
                    suggested_folder=suggested_folder,
                    needs_rename=needs_rename,
                    suggested_name=suggested_name,
                )
                self.assets.append(asset)
                
            except Exception as e:
                logger.warning(f"Error scanning {asset_path}: {e}")
        
        logger.info(f"Scanned {len(self.assets)} assets")
        return self.assets
    
    def analyze(self) -> Dict:
        """Analyze current asset organization."""
        if not self.assets:
            self.scan_assets()
        
        # Count by category
        by_category = defaultdict(list)
        for asset in self.assets:
            by_category[asset.category].append(asset)
        
        # Find misplaced assets
        misplaced = []
        for asset in self.assets:
            current_folder = asset.path.parent.name.lower()
            expected_folder = asset.suggested_folder.lower()
            
            if current_folder != expected_folder and expected_folder != "misc":
                misplaced.append(asset)
        
        # Find naming issues
        naming_issues = [a for a in self.assets if a.needs_rename]
        
        # Size analysis
        total_size = sum(a.size_bytes for a in self.assets)
        large_assets = [a for a in self.assets if a.size_mb > 100]
        
        return {
            "total_assets": len(self.assets),
            "by_category": {
                cat.value: len(assets) 
                for cat, assets in by_category.items()
            },
            "misplaced_assets": len(misplaced),
            "naming_issues": len(naming_issues),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "large_assets": len(large_assets),
            "recommendations": self._get_recommendations(misplaced, naming_issues),
        }
    
    def _get_recommendations(self, misplaced: List[AssetInfo], 
                            naming_issues: List[AssetInfo]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if len(misplaced) > 10:
            recommendations.append(
                f"Consider organizing {len(misplaced)} misplaced assets into proper folders"
            )
        
        if len(naming_issues) > 5:
            recommendations.append(
                f"Add standard prefixes to {len(naming_issues)} assets for better identification"
            )
        
        # Category-specific recommendations
        if not self.assets:
            return recommendations
            
        by_category = defaultdict(list)
        for asset in self.assets:
            by_category[asset.category].append(asset)
        
        if len(by_category.get(AssetCategory.MISC, [])) > len(self.assets) * 0.2:
            recommendations.append(
                "Many assets are uncategorized. Review naming conventions."
            )
        
        return recommendations
    
    def create_organization_plan(self, 
                                organize_folders: bool = True,
                                fix_naming: bool = True) -> OrganizationPlan:
        """Create a plan for organizing assets."""
        if not self.assets:
            self.scan_assets()
        
        moves: List[Tuple[Path, Path]] = []
        renames: List[Tuple[Path, str]] = []
        new_folders: Set[Path] = set()
        
        for asset in self.assets:
            current_folder = asset.path.parent
            target_folder = self.content_dir / asset.suggested_folder
            
            # Plan folder moves
            if organize_folders and current_folder != target_folder:
                if asset.suggested_folder != "Misc":
                    target_path = target_folder / asset.path.name
                    moves.append((asset.path, target_path))
                    new_folders.add(target_folder)
            
            # Plan renames
            if fix_naming and asset.needs_rename and asset.suggested_name:
                renames.append((asset.path, asset.suggested_name))
        
        return OrganizationPlan(
            moves=moves,
            renames=renames,
            new_folders=list(new_folders),
            total_assets=len(self.assets),
            assets_to_move=len(moves),
            assets_to_rename=len(renames),
        )
    
    def execute_plan(self, plan: OrganizationPlan, dry_run: bool = True) -> Dict:
        """Execute an organization plan."""
        results = {
            "folders_created": 0,
            "assets_moved": 0,
            "assets_renamed": 0,
            "errors": [],
        }
        
        if dry_run:
            logger.info("DRY RUN - No changes will be made")
            results["dry_run"] = True
            results["would_create_folders"] = len(plan.new_folders)
            results["would_move"] = len(plan.moves)
            results["would_rename"] = len(plan.renames)
            return results
        
        # Create new folders
        for folder in plan.new_folders:
            try:
                folder.mkdir(parents=True, exist_ok=True)
                results["folders_created"] += 1
            except Exception as e:
                results["errors"].append(f"Failed to create {folder}: {e}")
        
        # Execute moves
        for source, destination in plan.moves:
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(destination))
                results["assets_moved"] += 1
            except Exception as e:
                results["errors"].append(f"Failed to move {source.name}: {e}")
        
        # Execute renames
        for path, new_name in plan.renames:
            try:
                new_path = path.parent / f"{new_name}{path.suffix}"
                path.rename(new_path)
                results["assets_renamed"] += 1
            except Exception as e:
                results["errors"].append(f"Failed to rename {path.name}: {e}")
        
        logger.info(f"Organization complete: {results}")
        return results
    
    def bulk_rename(self, 
                   pattern: str, 
                   replacement: str,
                   category: Optional[AssetCategory] = None,
                   dry_run: bool = True) -> List[Tuple[str, str]]:
        """
        Bulk rename assets matching a pattern.
        
        Args:
            pattern: Regex pattern to match
            replacement: Replacement string (can use \1, \2, etc.)
            category: Optional category filter
            dry_run: If True, only show what would change
        
        Returns:
            List of (old_name, new_name) tuples
        """
        if not self.assets:
            self.scan_assets()
        
        changes = []
        regex = re.compile(pattern)
        
        for asset in self.assets:
            if category and asset.category != category:
                continue
            
            match = regex.search(asset.name)
            if match:
                new_name = regex.sub(replacement, asset.name)
                if new_name != asset.name:
                    changes.append((asset.name, new_name))
                    
                    if not dry_run:
                        try:
                            new_path = asset.path.parent / f"{new_name}{asset.extension}"
                            asset.path.rename(new_path)
                        except Exception as e:
                            logger.error(f"Rename failed for {asset.name}: {e}")
        
        return changes
    
    def get_size_report(self) -> Dict:
        """Get a report of asset sizes by category."""
        if not self.assets:
            self.scan_assets()
        
        by_category = defaultdict(lambda: {"count": 0, "size_mb": 0})
        
        for asset in self.assets:
            cat = asset.category.value
            by_category[cat]["count"] += 1
            by_category[cat]["size_mb"] += asset.size_mb
        
        # Round values
        for cat in by_category:
            by_category[cat]["size_mb"] = round(by_category[cat]["size_mb"], 2)
        
        # Sort by size
        sorted_cats = sorted(
            by_category.items(), 
            key=lambda x: x[1]["size_mb"], 
            reverse=True
        )
        
        return {
            "by_category": dict(sorted_cats),
            "total_assets": len(self.assets),
            "total_size_mb": round(sum(a.size_mb for a in self.assets), 2),
            "largest_assets": [
                {"name": a.name, "size_mb": round(a.size_mb, 2), "category": a.category.value}
                for a in sorted(self.assets, key=lambda x: x.size_bytes, reverse=True)[:10]
            ],
        }


# Developer signature
DEVELOPER_SIGNATURE = "G & E ZYNTH"
MODULE_VERSION = "1.0.0"

