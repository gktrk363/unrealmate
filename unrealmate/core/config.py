"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        UnrealMate - config.py                                ║
║                                                                              ║
║  Author: gktrk363                                                           ║
║  Purpose: Configuration management system                                   ║
║  Created: 2026-01-23                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Configuration management system for UnrealMate.
Handles .unrealmate.toml files and user preferences.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

import toml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class PerformanceConfig:
    """Performance-related configuration."""
    cache_enabled: bool = True
    cache_ttl_hours: int = 24
    max_cache_size_mb: int = 100
    parallel_processing: bool = True
    max_workers: int = 4


@dataclass
class SignatureConfig:
    """Signature and branding configuration."""
    show_banner: bool = True
    compact_banner: bool = False
    show_footer: bool = True
    color_theme: str = "cyan_magenta"  # cyan_magenta, monochrome, classic


@dataclass
class GitConfig:
    """Git-related configuration."""
    auto_lfs: bool = True
    commit_template_enabled: bool = True
    pre_commit_hooks: bool = True


@dataclass
class UnrealMateConfig:
    """Main UnrealMate configuration."""
    version: str = "1.0.0"
    performance: PerformanceConfig = None
    signature: SignatureConfig = None
    git: GitConfig = None
    
    def __post_init__(self):
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.signature is None:
            self.signature = SignatureConfig()
        if self.git is None:
            self.git = GitConfig()


DEFAULT_CONFIG = UnrealMateConfig()


def get_config_path(project_root: Optional[Path] = None) -> Path:
    """
    Get the path to the .unrealmate.toml configuration file.
    
    Args:
        project_root: Project root directory (default: current directory)
        
    Returns:
        Path: Path to configuration file
    """
    if project_root is None:
        project_root = Path.cwd()
    return project_root / ".unrealmate.toml"


def load_config(project_root: Optional[Path] = None) -> UnrealMateConfig:
    """
    Load configuration from .unrealmate.toml file.
    
    Args:
        project_root: Project root directory
        
    Returns:
        UnrealMateConfig: Loaded configuration (or default if not found)
    """
    config_path = get_config_path(project_root)
    
    if not config_path.exists():
        return DEFAULT_CONFIG
    
    try:
        data = toml.load(config_path)
        
        # Parse nested configs
        perf_data = data.get("performance", {})
        sig_data = data.get("signature", {})
        git_data = data.get("git", {})
        
        config = UnrealMateConfig(
            version=data.get("version", "1.0.0"),
            performance=PerformanceConfig(**perf_data),
            signature=SignatureConfig(**sig_data),
            git=GitConfig(**git_data)
        )
        
        return config
    except Exception as e:
        print(f"Warning: Failed to load config: {e}")
        return DEFAULT_CONFIG


def save_config(config: UnrealMateConfig, project_root: Optional[Path] = None) -> bool:
    """
    Save configuration to .unrealmate.toml file.
    
    Args:
        config: Configuration to save
        project_root: Project root directory
        
    Returns:
        bool: True if successful
    """
    config_path = get_config_path(project_root)
    
    try:
        data = {
            "version": config.version,
            "performance": asdict(config.performance),
            "signature": asdict(config.signature),
            "git": asdict(config.git)
        }
        
        with open(config_path, 'w') as f:
            toml.dump(data, f)
        
        return True
    except Exception as e:
        print(f"Error: Failed to save config: {e}")
        return False


def init_config(project_root: Optional[Path] = None, force: bool = False) -> bool:
    """
    Initialize a new .unrealmate.toml configuration file.
    
    Args:
        project_root: Project root directory
        force: Overwrite existing config
        
    Returns:
        bool: True if successful
    """
    config_path = get_config_path(project_root)
    
    if config_path.exists() and not force:
        print(f"Config already exists: {config_path}")
        return False
    
    return save_config(DEFAULT_CONFIG, project_root)


def get_config_value(key: str, project_root: Optional[Path] = None) -> Any:
    """
    Get a specific configuration value.
    
    Args:
        key: Config key in dot notation (e.g., "performance.cache_enabled")
        project_root: Project root directory
        
    Returns:
        Any: Configuration value
    """
    config = load_config(project_root)
    
    parts = key.split('.')
    value = config
    
    for part in parts:
        if hasattr(value, part):
            value = getattr(value, part)
        else:
            return None
    
    return value


def set_config_value(key: str, value: Any, project_root: Optional[Path] = None) -> bool:
    """
    Set a specific configuration value.
    
    Args:
        key: Config key in dot notation
        value: Value to set
        project_root: Project root directory
        
    Returns:
        bool: True if successful
    """
    config = load_config(project_root)
    
    parts = key.split('.')
    if len(parts) != 2:
        print("Error: Key must be in format 'section.key'")
        return False
    
    section, attr = parts
    
    if hasattr(config, section):
        section_obj = getattr(config, section)
        if hasattr(section_obj, attr):
            # Convert string values to appropriate types
            current_value = getattr(section_obj, attr)
            if isinstance(current_value, bool):
                value = value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(current_value, int):
                value = int(value)
            
            setattr(section_obj, attr, value)
            return save_config(config, project_root)
    
    print(f"Error: Invalid config key: {key}")
    return False


# © 2026 gktrk363 - Crafted with passion for Unreal Engine developers
