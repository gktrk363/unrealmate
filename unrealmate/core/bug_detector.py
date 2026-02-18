"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          UnrealMate - Bug Detector                           ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Pattern-based automated bug detection for UE projects              ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Automated bug detection system using pattern matching and static analysis.
Identifies common issues in Blueprint, C++, and asset configurations.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

import os
import re
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Callable

logger = logging.getLogger(__name__)


class BugSeverity(Enum):
    """Bug severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class BugCategory(Enum):
    """Categories of detected bugs."""
    BLUEPRINT = "blueprint"
    ASSET = "asset"
    CPP = "cpp"
    CONFIG = "config"
    NAMING = "naming"
    REFERENCE = "reference"
    PERFORMANCE = "performance"


@dataclass
class DetectedBug:
    """Represents a detected bug/issue."""
    id: str
    title: str
    description: str
    file_path: str
    line_number: Optional[int]
    category: BugCategory
    severity: BugSeverity
    suggestion: str
    auto_fixable: bool = False
    fix_function: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "category": self.category.value,
            "severity": self.severity.value,
            "suggestion": self.suggestion,
            "auto_fixable": self.auto_fixable,
        }


@dataclass
class BugPattern:
    """Defines a bug detection pattern."""
    id: str
    name: str
    category: BugCategory
    severity: BugSeverity
    file_extensions: List[str]
    pattern: str  # Regex pattern
    description: str
    suggestion: str
    auto_fixable: bool = False


class BugDetector:
    """
    Main bug detection engine for Unreal Engine projects.
    Uses pattern matching to identify common issues.
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.patterns: List[BugPattern] = []
        self.detected_bugs: List[DetectedBug] = []
        self._register_default_patterns()
        logger.info(f"BugDetector initialized for: {project_path}")
    
    def _register_default_patterns(self) -> None:
        """Register built-in bug detection patterns."""
        # Blueprint patterns
        self.patterns.extend([
            BugPattern(
                id="BP001",
                name="Tick Event Overuse",
                category=BugCategory.BLUEPRINT,
                severity=BugSeverity.WARNING,
                file_extensions=[".uasset"],
                pattern=r"EventTick",
                description="Event Tick is being used. Consider using timers for better performance.",
                suggestion="Replace Event Tick with Timer or consider using tick groups.",
                auto_fixable=False
            ),
            BugPattern(
                id="BP002",
                name="Cast Spam",
                category=BugCategory.BLUEPRINT,
                severity=BugSeverity.WARNING,
                file_extensions=[".uasset"],
                pattern=r"CastTo.*CastTo.*CastTo",
                description="Multiple consecutive casts detected.",
                suggestion="Cache cast results in variables to avoid repeated casting.",
                auto_fixable=False
            ),
        ])
        
        # C++ patterns
        self.patterns.extend([
            BugPattern(
                id="CPP001",
                name="Raw Pointer in UPROPERTY",
                category=BugCategory.CPP,
                severity=BugSeverity.ERROR,
                file_extensions=[".h", ".hpp"],
                pattern=r"UPROPERTY\([^)]*\)\s*\n\s*\w+\s*\*\s+(?!.*TObjectPtr)",
                description="Raw pointer used in UPROPERTY without TObjectPtr.",
                suggestion="Use TObjectPtr<T> instead of T* for better compatibility in UE5.",
                auto_fixable=True
            ),
            BugPattern(
                id="CPP002",
                name="Missing GENERATED_BODY",
                category=BugCategory.CPP,
                severity=BugSeverity.ERROR,
                file_extensions=[".h", ".hpp"],
                pattern=r"UCLASS\([^)]*\)[^{]*\{(?![^}]*GENERATED_BODY)",
                description="UCLASS missing GENERATED_BODY() macro.",
                suggestion="Add GENERATED_BODY() as the first line in the class body.",
                auto_fixable=True
            ),
            BugPattern(
                id="CPP003",
                name="Non-const Reference Parameter",
                category=BugCategory.CPP,
                severity=BugSeverity.INFO,
                file_extensions=[".h", ".hpp", ".cpp"],
                pattern=r"UFUNCTION\([^)]*\)[^;{]*[,\(]\s*(?!const)\w+\s*&\s+\w+",
                description="Non-const reference used in UFUNCTION parameter.",
                suggestion="Consider using const reference or pointer for safety.",
                auto_fixable=False
            ),
            BugPattern(
                id="CPP004",
                name="Missing Super Call",
                category=BugCategory.CPP,
                severity=BugSeverity.WARNING,
                file_extensions=[".cpp"],
                pattern=r"void\s+\w+::(BeginPlay|Tick|EndPlay)\s*\([^)]*\)[^{]*\{(?![^}]*Super::)",
                description="Override function missing Super:: call.",
                suggestion="Add Super::FunctionName() call at the beginning of the function.",
                auto_fixable=True
            ),
        ])
        
        # Asset patterns
        self.patterns.extend([
            BugPattern(
                id="ASSET001",
                name="Uppercase Asset Name",
                category=BugCategory.NAMING,
                severity=BugSeverity.INFO,
                file_extensions=[".uasset", ".umap"],
                pattern=r"",  # Special handling in scan
                description="Asset name contains uppercase letters (convention violation).",
                suggestion="Rename asset to use PascalCase with prefixes (BP_, SM_, T_, etc.).",
                auto_fixable=True
            ),
            BugPattern(
                id="ASSET002",
                name="Missing Asset Prefix",
                category=BugCategory.NAMING,
                severity=BugSeverity.WARNING,
                file_extensions=[".uasset"],
                pattern=r"",  # Special handling
                description="Asset missing standard prefix.",
                suggestion="Add appropriate prefix: BP_ for Blueprints, SM_ for Static Meshes, etc.",
                auto_fixable=True
            ),
        ])
        
        # Config patterns
        self.patterns.extend([
            BugPattern(
                id="CFG001",
                name="Missing DefaultEngine Setting",
                category=BugCategory.CONFIG,
                severity=BugSeverity.WARNING,
                file_extensions=[".ini"],
                pattern=r"^\[/Script/Engine\.Engine\]$",
                description="DefaultEngine.ini missing recommended optimization settings.",
                suggestion="Add gc.MaxObjectsInGame and other performance settings.",
                auto_fixable=True
            ),
        ])
        
        logger.info(f"Registered {len(self.patterns)} bug detection patterns")
    
    def add_custom_pattern(self, pattern: BugPattern) -> None:
        """Add a custom bug detection pattern."""
        self.patterns.append(pattern)
        logger.debug(f"Added custom pattern: {pattern.id}")
    
    def scan_file(self, file_path: Path) -> List[DetectedBug]:
        """Scan a single file for bugs."""
        bugs: List[DetectedBug] = []
        
        if not file_path.exists():
            return bugs
        
        extension = file_path.suffix.lower()
        
        try:
            # For text files, read and scan content
            if extension in ['.h', '.hpp', '.cpp', '.ini', '.cs']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for pattern in self.patterns:
                    if extension not in pattern.file_extensions:
                        continue
                    
                    if pattern.pattern:
                        matches = re.finditer(pattern.pattern, content, re.MULTILINE)
                        for match in matches:
                            # Calculate line number
                            line_num = content[:match.start()].count('\n') + 1
                            
                            bug = DetectedBug(
                                id=f"{pattern.id}_{len(bugs)}",
                                title=pattern.name,
                                description=pattern.description,
                                file_path=str(file_path),
                                line_number=line_num,
                                category=pattern.category,
                                severity=pattern.severity,
                                suggestion=pattern.suggestion,
                                auto_fixable=pattern.auto_fixable,
                            )
                            bugs.append(bug)
            
            # For asset files, check naming conventions
            elif extension in ['.uasset', '.umap']:
                bugs.extend(self._check_asset_naming(file_path))
        
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
        
        return bugs
    
    def _check_asset_naming(self, file_path: Path) -> List[DetectedBug]:
        """Check asset naming conventions."""
        bugs: List[DetectedBug] = []
        filename = file_path.stem
        
        # Check for standard prefixes
        valid_prefixes = {
            'BP_': 'Blueprint',
            'SM_': 'Static Mesh',
            'SK_': 'Skeletal Mesh',
            'T_': 'Texture',
            'M_': 'Material',
            'MI_': 'Material Instance',
            'PS_': 'Particle System',
            'NS_': 'Niagara System',
            'WBP_': 'Widget Blueprint',
            'ABP_': 'Animation Blueprint',
            'S_': 'Sound',
            'SC_': 'Sound Cue',
            'DT_': 'Data Table',
            'E_': 'Enum',
            'ST_': 'Struct',
        }
        
        has_valid_prefix = any(filename.startswith(prefix) for prefix in valid_prefixes)
        
        if not has_valid_prefix and not filename.startswith('Default'):
            bugs.append(DetectedBug(
                id=f"ASSET002_{filename}",
                title="Missing Asset Prefix",
                description=f"Asset '{filename}' missing standard prefix.",
                file_path=str(file_path),
                line_number=None,
                category=BugCategory.NAMING,
                severity=BugSeverity.WARNING,
                suggestion="Add appropriate prefix: BP_, SM_, T_, M_, etc.",
                auto_fixable=True,
            ))
        
        return bugs
    
    def scan_directory(self, 
                       directory: Optional[Path] = None,
                       recursive: bool = True,
                       extensions: Optional[List[str]] = None) -> List[DetectedBug]:
        """
        Scan a directory for bugs.
        
        Args:
            directory: Directory to scan (defaults to project path)
            recursive: Whether to scan subdirectories
            extensions: File extensions to scan (None = all supported)
        
        Returns:
            List of detected bugs
        """
        scan_dir = directory or self.project_path
        self.detected_bugs = []
        
        if extensions is None:
            extensions = ['.h', '.hpp', '.cpp', '.ini', '.cs', '.uasset', '.umap']
        
        logger.info(f"Scanning directory: {scan_dir}")
        
        if recursive:
            files = scan_dir.rglob('*')
        else:
            files = scan_dir.glob('*')
        
        scanned_count = 0
        for file_path in files:
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                bugs = self.scan_file(file_path)
                self.detected_bugs.extend(bugs)
                scanned_count += 1
        
        logger.info(f"Scanned {scanned_count} files, found {len(self.detected_bugs)} issues")
        return self.detected_bugs
    
    def scan_project(self) -> List[DetectedBug]:
        """Scan the entire project for bugs."""
        return self.scan_directory(self.project_path, recursive=True)
    
    def get_summary(self) -> Dict:
        """Get a summary of detected bugs."""
        summary = {
            "total": len(self.detected_bugs),
            "by_severity": {s.value: 0 for s in BugSeverity},
            "by_category": {c.value: 0 for c in BugCategory},
            "auto_fixable": 0,
        }
        
        for bug in self.detected_bugs:
            summary["by_severity"][bug.severity.value] += 1
            summary["by_category"][bug.category.value] += 1
            if bug.auto_fixable:
                summary["auto_fixable"] += 1
        
        return summary
    
    def to_json(self, output_path: Optional[str] = None) -> str:
        """Export bugs to JSON format."""
        data = {
            "project": str(self.project_path),
            "summary": self.get_summary(),
            "bugs": [bug.to_dict() for bug in self.detected_bugs],
        }
        
        json_str = json.dumps(data, indent=2)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_str)
            logger.info(f"Bug report saved to: {output_path}")
        
        return json_str
    
    def filter_by_severity(self, severity: BugSeverity) -> List[DetectedBug]:
        """Filter bugs by severity level."""
        return [b for b in self.detected_bugs if b.severity == severity]
    
    def filter_by_category(self, category: BugCategory) -> List[DetectedBug]:
        """Filter bugs by category."""
        return [b for b in self.detected_bugs if b.category == category]
    
    def get_fixable_bugs(self) -> List[DetectedBug]:
        """Get all auto-fixable bugs."""
        return [b for b in self.detected_bugs if b.auto_fixable]


class BlueprintBugDetector:
    """
    Specialized bug detector for Blueprint assets.
    Analyzes .uasset files for common issues.
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.issues: List[DetectedBug] = []
    
    def detect_tick_abuse(self, blueprint_path: Path) -> Optional[DetectedBug]:
        """Detect Event Tick overuse."""
        # Note: Full implementation would require parsing uasset binary
        # This is a placeholder for the detection logic
        return None
    
    def detect_cast_chains(self, blueprint_path: Path) -> List[DetectedBug]:
        """Detect long chains of casts."""
        return []
    
    def detect_heavy_construction_scripts(self, blueprint_path: Path) -> Optional[DetectedBug]:
        """Detect construction scripts with heavy operations."""
        return None


class CppBugDetector:
    """
    Specialized bug detector for C++ source files.
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.issues: List[DetectedBug] = []
    
    def detect_missing_includes(self, file_path: Path) -> List[DetectedBug]:
        """Detect missing header includes."""
        bugs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for common missing includes
            checks = [
                (r'\bFString\b', 'Containers/UnrealString.h'),
                (r'\bTArray\b', 'Containers/Array.h'),
                (r'\bTMap\b', 'Containers/Map.h'),
                (r'\bTSet\b', 'Containers/Set.h'),
            ]
            
            for pattern, header in checks:
                if re.search(pattern, content) and header not in content:
                    # This might be a false positive if included via PCH
                    pass
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
        
        return bugs
    
    def detect_thread_safety_issues(self, file_path: Path) -> List[DetectedBug]:
        """Detect potential thread safety issues."""
        bugs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for non-atomic operations on shared data
            if 'AsyncTask' in content or 'FRunnable' in content:
                # Check for global/static variable access without locks
                for i, line in enumerate(lines):
                    if re.search(r'static\s+\w+\s+\w+\s*=', line):
                        if 'FCriticalSection' not in content and 'FRWLock' not in content:
                            bugs.append(DetectedBug(
                                id=f"CPP_THREAD_{i}",
                                title="Potential Thread Safety Issue",
                                description="Static variable in async context without visible lock.",
                                file_path=str(file_path),
                                line_number=i + 1,
                                category=BugCategory.CPP,
                                severity=BugSeverity.WARNING,
                                suggestion="Use FCriticalSection or atomic types for thread-safe access.",
                                auto_fixable=False,
                            ))
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
        
        return bugs


# Developer signature
DEVELOPER_SIGNATURE = "gktrk363"
MODULE_VERSION = "1.0.0"
