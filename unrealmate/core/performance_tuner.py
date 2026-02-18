"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      UnrealMate - Performance Tuner                          ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Automated performance tuning for Unreal Engine projects            ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Automated performance optimization and tuning system.
Analyzes project settings and suggests/applies optimizations.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

import os
import re
import json
import configparser
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class OptimizationCategory(Enum):
    """Categories of performance optimizations."""
    RENDERING = "rendering"
    MEMORY = "memory"
    LOADING = "loading"
    PHYSICS = "physics"
    AUDIO = "audio"
    NETWORKING = "networking"
    GARBAGE_COLLECTION = "garbage_collection"


class OptimizationImpact(Enum):
    """Impact level of an optimization."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class OptimizationSuggestion:
    """A performance optimization suggestion."""
    id: str
    title: str
    description: str
    category: OptimizationCategory
    impact: OptimizationImpact
    config_file: str
    config_section: str
    config_key: str
    current_value: Optional[str]
    suggested_value: str
    rationale: str
    auto_applicable: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "impact": self.impact.value,
            "config_file": self.config_file,
            "config_section": self.config_section,
            "config_key": self.config_key,
            "current_value": self.current_value,
            "suggested_value": self.suggested_value,
            "rationale": self.rationale,
        }


@dataclass
class TuningProfile:
    """A collection of optimizations for a specific use case."""
    name: str
    description: str
    target_platform: str  # PC, Mobile, Console
    target_quality: str  # Low, Medium, High, Ultra
    suggestions: List[OptimizationSuggestion] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "target_platform": self.target_platform,
            "target_quality": self.target_quality,
            "suggestions_count": len(self.suggestions),
        }


class ConfigAnalyzer:
    """
    Analyzes Unreal Engine configuration files.
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.config_dir = self.project_path / "Config"
    
    def read_ini_file(self, filename: str) -> Dict[str, Dict[str, str]]:
        """Read and parse an INI file."""
        config_path = self.config_dir / filename
        config = {}
        
        if not config_path.exists():
            return config
        
        current_section = ""
        
        try:
            with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith(';') or line.startswith('#'):
                        continue
                    
                    # Section header
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        if current_section not in config:
                            config[current_section] = {}
                        continue
                    
                    # Key=Value
                    if '=' in line and current_section:
                        key, value = line.split('=', 1)
                        config[current_section][key.strip()] = value.strip()
        
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
        
        return config
    
    def get_value(self, filename: str, section: str, key: str) -> Optional[str]:
        """Get a specific value from a config file."""
        config = self.read_ini_file(filename)
        return config.get(section, {}).get(key)


class PerformanceTuner:
    """
    Main performance tuning engine.
    Analyzes project and suggests/applies optimizations.
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.config_analyzer = ConfigAnalyzer(project_path)
        self.suggestions: List[OptimizationSuggestion] = []
        logger.info(f"PerformanceTuner initialized for: {project_path}")
    
    def _create_optimization_rules(self) -> List[Dict]:
        """Define optimization rules."""
        return [
            # Garbage Collection
            {
                "id": "GC001",
                "title": "Increase GC Object Pool Size",
                "category": OptimizationCategory.GARBAGE_COLLECTION,
                "impact": OptimizationImpact.HIGH,
                "file": "DefaultEngine.ini",
                "section": "/Script/Engine.GarbageCollectionSettings",
                "key": "gc.MaxObjectsInGame",
                "default": "2162688",
                "suggested": "4194304",
                "rationale": "Larger pool reduces GC frequency in large games",
            },
            {
                "id": "GC002",
                "title": "Enable Incremental GC",
                "category": OptimizationCategory.GARBAGE_COLLECTION,
                "impact": OptimizationImpact.MEDIUM,
                "file": "DefaultEngine.ini",
                "section": "/Script/Engine.GarbageCollectionSettings",
                "key": "gc.AllowParallelGC",
                "default": "False",
                "suggested": "True",
                "rationale": "Parallel GC reduces frame hitches",
            },
            
            # Streaming
            {
                "id": "LOAD001",
                "title": "Enable Async Loading",
                "category": OptimizationCategory.LOADING,
                "impact": OptimizationImpact.HIGH,
                "file": "DefaultEngine.ini",
                "section": "/Script/Engine.StreamingSettings",
                "key": "s.AsyncLoadingThreadEnabled",
                "default": "False",
                "suggested": "True",
                "rationale": "Async loading prevents main thread blocking",
            },
            {
                "id": "LOAD002",
                "title": "Increase IO Dispatch Latency",
                "category": OptimizationCategory.LOADING,
                "impact": OptimizationImpact.MEDIUM,
                "file": "DefaultEngine.ini",
                "section": "/Script/Engine.StreamingSettings",
                "key": "s.IoDispatcherCacheSizeMB",
                "default": "256",
                "suggested": "512",
                "rationale": "Larger cache reduces disk IO operations",
            },
            
            # Rendering
            {
                "id": "RENDER001",
                "title": "Enable Occlusion Culling",
                "category": OptimizationCategory.RENDERING,
                "impact": OptimizationImpact.HIGH,
                "file": "DefaultEngine.ini",
                "section": "/Script/Engine.RendererSettings",
                "key": "r.AllowOcclusionQueries",
                "default": "False",
                "suggested": "True",
                "rationale": "Occlusion culling reduces draw calls significantly",
            },
            {
                "id": "RENDER002",
                "title": "Set Shadow Quality",
                "category": OptimizationCategory.RENDERING,
                "impact": OptimizationImpact.MEDIUM,
                "file": "DefaultEngine.ini",
                "section": "/Script/Engine.RendererSettings",
                "key": "r.Shadow.MaxResolution",
                "default": "2048",
                "suggested": "1024",
                "rationale": "Lower shadow resolution improves GPU performance",
            },
            {
                "id": "RENDER003",
                "title": "Enable Level Streaming",
                "category": OptimizationCategory.MEMORY,
                "impact": OptimizationImpact.HIGH,
                "file": "DefaultEngine.ini",
                "section": "/Script/Engine.LevelStreaming",
                "key": "s.LevelStreamingActorsUpdateTimeLimit",
                "default": "5.0",
                "suggested": "2.0",
                "rationale": "Faster level streaming updates reduce pop-in",
            },
            
            # Physics
            {
                "id": "PHYS001",
                "title": "Optimize Physics Substeps",
                "category": OptimizationCategory.PHYSICS,
                "impact": OptimizationImpact.MEDIUM,
                "file": "DefaultEngine.ini",
                "section": "/Script/Engine.PhysicsSettings",
                "key": "MaxSubstepDeltaTime",
                "default": "0.016667",
                "suggested": "0.033333",
                "rationale": "Larger substep reduces physics calculations per frame",
            },
            
            # Audio
            {
                "id": "AUDIO001",
                "title": "Limit Max Concurrent Sounds",
                "category": OptimizationCategory.AUDIO,
                "impact": OptimizationImpact.LOW,
                "file": "DefaultEngine.ini",
                "section": "/Script/Engine.AudioSettings",
                "key": "MaxChannels",
                "default": "128",
                "suggested": "64",
                "rationale": "Fewer concurrent sounds reduces CPU audio overhead",
            },
            
            # Networking
            {
                "id": "NET001",
                "title": "Optimize Net Update Frequency",
                "category": OptimizationCategory.NETWORKING,
                "impact": OptimizationImpact.MEDIUM,
                "file": "DefaultEngine.ini",
                "section": "/Script/Engine.GameNetworkManager",
                "key": "TotalNetBandwidth",
                "default": "32000",
                "suggested": "64000",
                "rationale": "Higher bandwidth improves multiplayer smoothness",
            },
        ]
    
    def analyze(self) -> List[OptimizationSuggestion]:
        """Analyze project and generate optimization suggestions."""
        self.suggestions = []
        rules = self._create_optimization_rules()
        
        for rule in rules:
            current_value = self.config_analyzer.get_value(
                rule["file"],
                rule["section"],
                rule["key"]
            )
            
            # Only suggest if current value differs from suggested
            if current_value != rule["suggested"]:
                suggestion = OptimizationSuggestion(
                    id=rule["id"],
                    title=rule["title"],
                    description=f"Change {rule['key']} to optimize {rule['category'].value}",
                    category=rule["category"],
                    impact=rule["impact"],
                    config_file=rule["file"],
                    config_section=rule["section"],
                    config_key=rule["key"],
                    current_value=current_value,
                    suggested_value=rule["suggested"],
                    rationale=rule["rationale"],
                )
                self.suggestions.append(suggestion)
        
        logger.info(f"Found {len(self.suggestions)} optimization opportunities")
        return self.suggestions
    
    def apply_suggestion(self, suggestion_id: str, dry_run: bool = True) -> bool:
        """Apply a specific optimization suggestion."""
        suggestion = next((s for s in self.suggestions if s.id == suggestion_id), None)
        
        if not suggestion:
            logger.error(f"Suggestion not found: {suggestion_id}")
            return False
        
        if dry_run:
            logger.info(f"DRY RUN: Would apply {suggestion.title}")
            return True
        
        config_path = self.project_path / "Config" / suggestion.config_file
        
        try:
            # Read existing content
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = ""
            
            # Check if section exists
            section = suggestion.config_section
            key = suggestion.config_key
            value = suggestion.suggested_value
            
            if section not in content:
                # Add new section
                content += f"\n\n[{section}]\n{key}={value}\n"
            elif f"{key}=" in content:
                # Update existing key
                pattern = rf"({re.escape(key)})=([^\n]*)"
                content = re.sub(pattern, f"\\1={value}", content)
            else:
                # Add key to existing section
                content = content.replace(
                    f"[{section}]",
                    f"[{section}]\n{key}={value}"
                )
            
            # Write back
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Applied: {suggestion.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply {suggestion.title}: {e}")
            return False
    
    def apply_all(self, 
                  categories: Optional[List[OptimizationCategory]] = None,
                  min_impact: OptimizationImpact = OptimizationImpact.LOW,
                  dry_run: bool = True) -> Dict:
        """
        Apply all matching optimization suggestions.
        
        Args:
            categories: Only apply optimizations from these categories
            min_impact: Minimum impact level to apply
            dry_run: If True, only show what would be done
        
        Returns:
            Summary of applied optimizations
        """
        impact_order = [
            OptimizationImpact.LOW,
            OptimizationImpact.MEDIUM,
            OptimizationImpact.HIGH,
            OptimizationImpact.CRITICAL,
        ]
        
        min_impact_idx = impact_order.index(min_impact)
        
        applied = 0
        skipped = 0
        failed = 0
        
        for suggestion in self.suggestions:
            # Filter by category
            if categories and suggestion.category not in categories:
                skipped += 1
                continue
            
            # Filter by impact
            suggestion_impact_idx = impact_order.index(suggestion.impact)
            if suggestion_impact_idx < min_impact_idx:
                skipped += 1
                continue
            
            # Apply
            if self.apply_suggestion(suggestion.id, dry_run=dry_run):
                applied += 1
            else:
                failed += 1
        
        return {
            "dry_run": dry_run,
            "applied": applied,
            "skipped": skipped,
            "failed": failed,
        }
    
    def get_profile(self, platform: str = "PC", quality: str = "High") -> TuningProfile:
        """Get a tuning profile for a specific platform and quality target."""
        
        # Define platform-specific overrides
        platform_settings = {
            "Mobile": {
                "r.Shadow.MaxResolution": "512",
                "gc.MaxObjectsInGame": "1048576",
                "MaxChannels": "32",
            },
            "Console": {
                "r.Shadow.MaxResolution": "1024",
                "gc.MaxObjectsInGame": "2162688",
            },
            "PC": {
                "r.Shadow.MaxResolution": "2048",
                "gc.MaxObjectsInGame": "4194304",
            },
        }
        
        quality_settings = {
            "Low": {
                "r.Shadow.MaxResolution": "512",
                "r.AllowOcclusionQueries": "True",
            },
            "Medium": {
                "r.Shadow.MaxResolution": "1024",
            },
            "High": {
                "r.Shadow.MaxResolution": "2048",
            },
            "Ultra": {
                "r.Shadow.MaxResolution": "4096",
            },
        }
        
        profile = TuningProfile(
            name=f"{platform}_{quality}",
            description=f"Optimized for {platform} at {quality} quality",
            target_platform=platform,
            target_quality=quality,
        )
        
        # Generate suggestions based on profile
        if not self.suggestions:
            self.analyze()
        
        for suggestion in self.suggestions:
            # Check if this suggestion applies to the profile
            key = suggestion.config_key
            
            # Override with platform-specific values
            if platform in platform_settings:
                if key in platform_settings[platform]:
                    suggestion.suggested_value = platform_settings[platform][key]
            
            # Override with quality settings
            if quality in quality_settings:
                if key in quality_settings[quality]:
                    suggestion.suggested_value = quality_settings[quality][key]
            
            profile.suggestions.append(suggestion)
        
        return profile
    
    def generate_report(self) -> str:
        """Generate a human-readable optimization report."""
        if not self.suggestions:
            self.analyze()
        
        report = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     Performance Optimization Report                          ║
║                           by gktrk363                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

"""
        
        # Group by category
        by_category: Dict[OptimizationCategory, List[OptimizationSuggestion]] = {}
        for s in self.suggestions:
            if s.category not in by_category:
                by_category[s.category] = []
            by_category[s.category].append(s)
        
        for category, suggestions in by_category.items():
            report += f"\n━━━ {category.value.upper()} ━━━\n\n"
            
            for s in suggestions:
                impact_icon = {
                    OptimizationImpact.LOW: "🟢",
                    OptimizationImpact.MEDIUM: "🟡",
                    OptimizationImpact.HIGH: "🟠",
                    OptimizationImpact.CRITICAL: "🔴",
                }[s.impact]
                
                report += f"{impact_icon} {s.title}\n"
                report += f"   📁 {s.config_file} → [{s.config_section}]\n"
                report += f"   🔧 {s.config_key}: {s.current_value or 'Not set'} → {s.suggested_value}\n"
                report += f"   💡 {s.rationale}\n\n"
        
        report += f"\n{'='*78}\n"
        report += f"Total Suggestions: {len(self.suggestions)}\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report


# Developer signature
DEVELOPER_SIGNATURE = "gktrk363"
MODULE_VERSION = "1.0.0"
