# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Models
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Typed models for the command registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RegistryError(Exception):
    """Base exception for command registry errors."""


class RegistryParseError(RegistryError):
    """Raised when the registry document cannot be parsed."""


class RegistryValidationError(RegistryError):
    """Raised when validation detects one or more rule violations."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


class Maturity(str, Enum):
    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    MOCK = "mock"
    DEPRECATED = "deprecated"
    LOCAL_ONLY = "local-only"


class Status(str, Enum):
    PRODUCTION_READY = "production-ready"
    PARTIALLY_IMPLEMENTED = "partially-implemented"
    PLACEHOLDER = "placeholder"
    RISKY = "risky"
    BROKEN = "broken"


class Visibility(str, Enum):
    DEFAULT = "default"
    OPT_IN = "opt-in"
    HIDDEN = "hidden"
    INTERNAL = "internal"


class DeprecationState(str, Enum):
    ACTIVE = "active"
    SOFT_DEPRECATED = "soft-deprecated"
    HIDDEN_DEPRECATED = "hidden-deprecated"
    REMOVED = "removed"


class SmokeTestTier(str, Enum):
    NONE = "none"
    NON_DESTRUCTIVE = "non-destructive"
    DESTRUCTIVE = "destructive"


@dataclass(frozen=True)
class RegistryMeta:
    """Metadata for the command registry document."""

    version: int
    source: str = "unrealmate/registry/command_registry.toml"
    coverage: str = "phase1"


@dataclass(frozen=True)
class CommandEntry:
    """Single command metadata record."""

    command_group: str
    subcommand: str
    full_command: str
    aliases: list[str]
    maturity: Maturity
    status: Status
    visibility: Visibility
    destructive: bool
    supports_dry_run: bool
    requires_project_path: bool
    requires_fixture_or_external_dependency: bool
    local_only: bool
    category: str
    short_help: str
    long_help_source: str
    docs_included: bool
    completion_included: bool
    default_help_included: bool
    deprecation_state: DeprecationState
    replacement_command: Optional[str]
    owner_module: str
    notes: str
    external_dependencies: list[str] = field(default_factory=list)
    smoke_test_tier: SmokeTestTier = SmokeTestTier.NONE
    source_refs: list[str] = field(default_factory=list)
    introduced_in: str = "phase1"

    @property
    def key(self) -> tuple[str, str]:
        return (self.command_group, self.subcommand)


@dataclass(frozen=True)
class CommandRegistry:
    """In-memory typed representation of the command registry."""

    meta: RegistryMeta
    commands: list[CommandEntry]

    def by_full_command(self) -> dict[str, CommandEntry]:
        return {entry.full_command: entry for entry in self.commands}

    def by_key(self) -> dict[tuple[str, str], CommandEntry]:
        return {entry.key: entry for entry in self.commands}
