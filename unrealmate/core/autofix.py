"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          UnrealMate - Auto Fix                               ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  Purpose: Automatic fixing of common Unreal Engine project issues            ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Auto-fix system for common Unreal Engine project issues.
Supports dry-run mode, backup before changes, and rollback.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

import re
import shutil
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class FixCategory(Enum):
    """Categories of auto-fixes."""
    REFERENCE = "reference"
    NAMING = "naming"
    CONFIG = "config"
    CLEANUP = "cleanup"
    CODE = "code"


class FixStatus(Enum):
    """Status of a fix operation."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class FixAction:
    """Represents a single fix action."""
    id: str
    title: str
    description: str
    category: FixCategory
    file_path: str
    status: FixStatus = FixStatus.PENDING
    original_value: Optional[str] = None
    new_value: Optional[str] = None
    backup_path: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "file_path": self.file_path,
            "status": self.status.value,
            "error_message": self.error_message,
        }


@dataclass
class FixReport:
    """Report of fix operations."""
    total_issues: int
    fixed: int
    failed: int
    skipped: int
    actions: List[FixAction]
    dry_run: bool
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "summary": {
                "total": self.total_issues,
                "fixed": self.fixed,
                "failed": self.failed,
                "skipped": self.skipped,
            },
            "dry_run": self.dry_run,
            "timestamp": self.timestamp.isoformat(),
            "actions": [a.to_dict() for a in self.actions],
        }
    
    def __str__(self) -> str:
        mode = "DRY RUN" if self.dry_run else "APPLIED"
        return f"Fix Report ({mode}): {self.fixed}/{self.total_issues} fixed, {self.failed} failed, {self.skipped} skipped"


class AutoFixer:
    """
    Main auto-fix engine for Unreal Engine projects.
    Automatically detects and fixes common issues.
    """
    
    def __init__(self, project_path: str, backup_dir: Optional[str] = None):
        self.project_path = Path(project_path)
        self.backup_dir = Path(backup_dir) if backup_dir else self.project_path / ".unrealmate" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.actions: List[FixAction] = []
        logger.info(f"AutoFixer initialized for: {project_path}")
    
    def _create_backup(self, file_path: Path) -> Optional[str]:
        """Create a backup of a file before modifying it."""
        if not file_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(file_path, backup_path)
            return str(backup_path)
        except Exception as e:
            logger.error(f"Backup failed for {file_path}: {e}")
            return None
    
    def _restore_backup(self, backup_path: str, original_path: str) -> bool:
        """Restore a file from backup."""
        try:
            shutil.copy2(backup_path, original_path)
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

    # ==================== NAMING FIXES ====================
    
    def fix_asset_naming(self, dry_run: bool = True) -> List[FixAction]:
        """Fix asset naming convention violations."""
        actions = []
        content_dir = self.project_path / "Content"
        
        if not content_dir.exists():
            return actions
        
        # Prefix mapping based on asset type
        prefix_rules = {
            "Blueprint": "BP_",
            "StaticMesh": "SM_",
            "SkeletalMesh": "SK_",
            "Texture": "T_",
            "Material": "M_",
            "MaterialInstance": "MI_",
            "ParticleSystem": "PS_",
            "NiagaraSystem": "NS_",
            "WidgetBlueprint": "WBP_",
            "AnimBlueprint": "ABP_",
            "SoundWave": "S_",
            "SoundCue": "SC_",
            "DataTable": "DT_",
        }
        
        valid_prefixes = list(prefix_rules.values()) + ["Default", "B_"]
        
        for asset_path in content_dir.rglob("*.uasset"):
            name = asset_path.stem
            
            # Check if already has valid prefix
            has_prefix = any(name.startswith(p) for p in valid_prefixes)
            
            if not has_prefix:
                # Determine appropriate prefix (simplified)
                suggested_prefix = "BP_"  # Default to Blueprint
                folder_name = asset_path.parent.name.lower()
                
                if "mesh" in folder_name or "static" in folder_name:
                    suggested_prefix = "SM_"
                elif "material" in folder_name:
                    suggested_prefix = "M_"
                elif "texture" in folder_name:
                    suggested_prefix = "T_"
                elif "widget" in folder_name or "ui" in folder_name:
                    suggested_prefix = "WBP_"
                elif "animation" in folder_name or "anim" in folder_name:
                    suggested_prefix = "ABP_"
                
                new_name = f"{suggested_prefix}{name}"
                new_path = asset_path.parent / f"{new_name}.uasset"
                
                action = FixAction(
                    id=f"NAMING_{len(actions)}",
                    title="Add prefix to asset",
                    description=f"Rename '{name}' to '{new_name}'",
                    category=FixCategory.NAMING,
                    file_path=str(asset_path),
                    original_value=name,
                    new_value=new_name,
                )
                
                if not dry_run:
                    try:
                        backup = self._create_backup(asset_path)
                        action.backup_path = backup
                        asset_path.rename(new_path)
                        action.status = FixStatus.SUCCESS
                    except Exception as e:
                        action.status = FixStatus.FAILED
                        action.error_message = str(e)
                
                actions.append(action)
        
        return actions

    # ==================== CONFIG FIXES ====================
    
    def fix_config_issues(self, dry_run: bool = True) -> List[FixAction]:
        """Fix configuration file issues."""
        actions = []
        config_dir = self.project_path / "Config"
        
        if not config_dir.exists():
            return actions
        
        # Check DefaultEngine.ini for recommended settings
        engine_ini = config_dir / "DefaultEngine.ini"
        if engine_ini.exists():
            try:
                with open(engine_ini, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                recommended_settings = [
                    ("[/Script/Engine.GarbageCollectionSettings]", "gc.MaxObjectsInGame=2162688"),
                    ("[/Script/Engine.StreamingSettings]", "s.AsyncLoadingThreadEnabled=True"),
                ]
                
                new_content = content
                modified = False
                
                for section, setting in recommended_settings:
                    if setting not in content:
                        # Check if section exists
                        if section not in content:
                            new_content += f"\n\n{section}\n{setting}\n"
                        else:
                            # Add to existing section
                            new_content = new_content.replace(
                                section,
                                f"{section}\n{setting}"
                            )
                        modified = True
                        
                        action = FixAction(
                            id=f"CONFIG_{len(actions)}",
                            title="Add recommended config setting",
                            description=f"Add: {setting}",
                            category=FixCategory.CONFIG,
                            file_path=str(engine_ini),
                            original_value=section,
                            new_value=setting,
                        )
                        actions.append(action)
                
                if modified and not dry_run:
                    for action in actions:
                        if action.file_path == str(engine_ini):
                            try:
                                backup = self._create_backup(engine_ini)
                                action.backup_path = backup
                                with open(engine_ini, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                action.status = FixStatus.SUCCESS
                            except Exception as e:
                                action.status = FixStatus.FAILED
                                action.error_message = str(e)
                                
            except Exception as e:
                logger.error(f"Error reading config: {e}")
        
        return actions

    # ==================== CLEANUP FIXES ====================
    
    def cleanup_orphaned_files(self, dry_run: bool = True) -> List[FixAction]:
        """Clean up orphaned and temporary files."""
        actions = []
        
        # Patterns for files that can be safely deleted
        cleanup_patterns = [
            "*.log",
            "*.tmp",
            "*.bak",
            "Thumbs.db",
            ".DS_Store",
            "*.pyc",
            "__pycache__",
        ]
        
        # Directories to skip
        skip_dirs = {"Binaries", "Intermediate", ".git", "node_modules"}
        
        for pattern in cleanup_patterns:
            if "*" in pattern:
                files = self.project_path.rglob(pattern)
            else:
                files = self.project_path.rglob(pattern)
            
            for file_path in files:
                # Skip if in excluded directory
                if any(skip in file_path.parts for skip in skip_dirs):
                    continue
                
                action = FixAction(
                    id=f"CLEANUP_{len(actions)}",
                    title="Remove orphaned file",
                    description=f"Delete: {file_path.name}",
                    category=FixCategory.CLEANUP,
                    file_path=str(file_path),
                )
                
                if not dry_run:
                    try:
                        if file_path.is_dir():
                            shutil.rmtree(file_path)
                        else:
                            file_path.unlink()
                        action.status = FixStatus.SUCCESS
                    except Exception as e:
                        action.status = FixStatus.FAILED
                        action.error_message = str(e)
                
                actions.append(action)
        
        return actions

    # ==================== CODE FIXES ====================
    
    def fix_cpp_issues(self, dry_run: bool = True) -> List[FixAction]:
        """Fix common C++ code issues."""
        actions = []
        source_dir = self.project_path / "Source"
        
        if not source_dir.exists():
            return actions
        
        for cpp_file in source_dir.rglob("*.cpp"):
            try:
                with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                modified = False
                
                # Fix 1: Add missing Super:: calls
                super_pattern = r"(void\s+\w+::(BeginPlay|EndPlay)\s*\([^)]*\)[^{]*\{)(?!\s*Super::)"
                if re.search(super_pattern, content):
                    def add_super(match):
                        func_name = match.group(2)
                        return f"{match.group(1)}\n\tSuper::{func_name}();"
                    
                    new_content = re.sub(super_pattern, add_super, content)
                    if new_content != content:
                        content = new_content
                        modified = True
                        
                        action = FixAction(
                            id=f"CODE_SUPER_{len(actions)}",
                            title="Add missing Super:: call",
                            description=f"Added Super:: call in {cpp_file.name}",
                            category=FixCategory.CODE,
                            file_path=str(cpp_file),
                        )
                        actions.append(action)
                
                # Fix 2: Remove trailing whitespace
                if re.search(r'[ \t]+$', content, re.MULTILINE):
                    new_content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
                    if new_content != content:
                        content = new_content
                        modified = True
                        
                        action = FixAction(
                            id=f"CODE_WHITESPACE_{len(actions)}",
                            title="Remove trailing whitespace",
                            description=f"Cleaned whitespace in {cpp_file.name}",
                            category=FixCategory.CODE,
                            file_path=str(cpp_file),
                        )
                        actions.append(action)
                
                if modified and not dry_run:
                    for action in [a for a in actions if a.file_path == str(cpp_file)]:
                        try:
                            backup = self._create_backup(cpp_file)
                            action.backup_path = backup
                            with open(cpp_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            action.status = FixStatus.SUCCESS
                        except Exception as e:
                            action.status = FixStatus.FAILED
                            action.error_message = str(e)
                            
            except Exception as e:
                logger.error(f"Error processing {cpp_file}: {e}")
        
        return actions

    # ==================== MAIN INTERFACE ====================
    
    def scan_all(self) -> List[FixAction]:
        """Scan for all fixable issues without making changes."""
        self.actions = []
        
        self.actions.extend(self.fix_asset_naming(dry_run=True))
        self.actions.extend(self.fix_config_issues(dry_run=True))
        self.actions.extend(self.cleanup_orphaned_files(dry_run=True))
        self.actions.extend(self.fix_cpp_issues(dry_run=True))
        
        logger.info(f"Found {len(self.actions)} fixable issues")
        return self.actions
    
    def fix_all(self, dry_run: bool = False, 
                categories: Optional[List[FixCategory]] = None) -> FixReport:
        """
        Fix all detected issues.
        
        Args:
            dry_run: If True, only report what would be done
            categories: Optional list of categories to fix (None = all)
        
        Returns:
            FixReport with results
        """
        all_actions = []
        
        # Run all fix functions
        all_actions.extend(self.fix_asset_naming(dry_run=dry_run))
        all_actions.extend(self.fix_config_issues(dry_run=dry_run))
        all_actions.extend(self.cleanup_orphaned_files(dry_run=dry_run))
        all_actions.extend(self.fix_cpp_issues(dry_run=dry_run))
        
        # Filter by category if specified
        if categories:
            all_actions = [a for a in all_actions if a.category in categories]
        
        # Count results
        fixed = sum(1 for a in all_actions if a.status == FixStatus.SUCCESS)
        failed = sum(1 for a in all_actions if a.status == FixStatus.FAILED)
        skipped = sum(1 for a in all_actions if a.status == FixStatus.SKIPPED)
        
        report = FixReport(
            total_issues=len(all_actions),
            fixed=fixed,
            failed=failed,
            skipped=skipped,
            actions=all_actions,
            dry_run=dry_run,
        )
        
        logger.info(str(report))
        return report
    
    def rollback(self, action_id: str) -> bool:
        """Rollback a specific fix action."""
        for action in self.actions:
            if action.id == action_id and action.backup_path:
                return self._restore_backup(action.backup_path, action.file_path)
        return False
    
    def rollback_all(self) -> int:
        """Rollback all fixes that have backups."""
        count = 0
        for action in reversed(self.actions):
            if action.backup_path and action.status == FixStatus.SUCCESS:
                if self._restore_backup(action.backup_path, action.file_path):
                    count += 1
        return count


# Developer signature
DEVELOPER_SIGNATURE = "G & E ZYNTH"
MODULE_VERSION = "1.0.0"

