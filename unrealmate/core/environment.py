"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Environment Configuration                    ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Environment-based configuration (dev, staging, prod)               ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

console = Console()


class Environment(Enum):
    """Available environments."""
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"
    CI = "ci"


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration."""

    name: str
    debug: bool = False
    verbose: bool = False
    cache_enabled: bool = True
    show_banner: bool = True
    color_output: bool = True
    max_workers: int = 4
    log_level: str = "INFO"
    extra: dict[str, Any] = field(default_factory=dict)


# Default configurations for each environment
ENV_CONFIGS: dict[Environment, EnvironmentConfig] = {
    Environment.DEVELOPMENT: EnvironmentConfig(
        name="development",
        debug=True,
        verbose=True,
        cache_enabled=True,
        show_banner=True,
        color_output=True,
        max_workers=2,
        log_level="DEBUG",
    ),
    Environment.STAGING: EnvironmentConfig(
        name="staging",
        debug=False,
        verbose=True,
        cache_enabled=True,
        show_banner=True,
        color_output=True,
        max_workers=4,
        log_level="INFO",
    ),
    Environment.PRODUCTION: EnvironmentConfig(
        name="production",
        debug=False,
        verbose=False,
        cache_enabled=True,
        show_banner=False,
        color_output=True,
        max_workers=8,
        log_level="WARNING",
    ),
    Environment.CI: EnvironmentConfig(
        name="ci",
        debug=False,
        verbose=False,
        cache_enabled=False,
        show_banner=False,
        color_output=False,
        max_workers=4,
        log_level="INFO",
    ),
}


def get_current_environment() -> Environment:
    """
    Detect the current environment from environment variables.

    Checks UNREALMATE_ENV, then falls back to common CI environment variables.

    Returns:
        Current Environment enum value
    """
    env_name = os.environ.get("UNREALMATE_ENV", "").lower()

    if env_name in ("dev", "development"):
        return Environment.DEVELOPMENT
    elif env_name in ("staging", "stage"):
        return Environment.STAGING
    elif env_name in ("prod", "production"):
        return Environment.PRODUCTION
    elif env_name in ("ci", "test"):
        return Environment.CI

    # Auto-detect CI environments
    ci_env_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "JENKINS_URL", "TRAVIS"]
    if any(os.environ.get(var) for var in ci_env_vars):
        return Environment.CI

    # Default to development
    return Environment.DEVELOPMENT


def get_environment_config(env: Optional[Environment] = None) -> EnvironmentConfig:
    """
    Get configuration for the specified or current environment.

    Args:
        env: Optional environment, uses current if not specified

    Returns:
        EnvironmentConfig for the environment
    """
    if env is None:
        env = get_current_environment()
    return ENV_CONFIGS.get(env, ENV_CONFIGS[Environment.DEVELOPMENT])


def load_env_file(path: Path) -> dict[str, str]:
    """
    Load environment variables from a .env file.

    Args:
        path: Path to .env file

    Returns:
        Dictionary of environment variables
    """
    env_vars: dict[str, str] = {}

    if not path.exists():
        return env_vars

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                env_vars[key] = value

    return env_vars


def setup_environment(env: Optional[Environment] = None) -> EnvironmentConfig:
    """
    Setup the environment and return its configuration.

    Args:
        env: Optional environment to use

    Returns:
        EnvironmentConfig for the setup environment
    """
    if env is None:
        env = get_current_environment()

    config = get_environment_config(env)

    # Set environment variable for subprocess
    os.environ["UNREALMATE_ENV"] = env.value

    if config.verbose:
        console.print(f"[dim]Environment: {config.name}[/dim]")

    return config


def is_development() -> bool:
    """Check if running in development environment."""
    return get_current_environment() == Environment.DEVELOPMENT


def is_production() -> bool:
    """Check if running in production environment."""
    return get_current_environment() == Environment.PRODUCTION


def is_ci() -> bool:
    """Check if running in CI environment."""
    return get_current_environment() == Environment.CI
