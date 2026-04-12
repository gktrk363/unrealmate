# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - registry
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Command registry public API."""

from unrealmate.registry.loader import default_registry_path, load_command_registry, parse_registry_data
from unrealmate.registry.models import (
    CommandEntry,
    CommandRegistry,
    DeprecationState,
    Maturity,
    RegistryError,
    RegistryMeta,
    RegistryParseError,
    RegistryValidationError,
    SmokeTestTier,
    Status,
    Visibility,
)
from unrealmate.registry.parity import ParityReport, check_registry_cli_parity, collect_cli_command_inventory
from unrealmate.registry.validator import ValidationIssue, assert_registry_valid, validate_registry

__all__ = [
    "CommandEntry",
    "CommandRegistry",
    "DeprecationState",
    "Maturity",
    "ParityReport",
    "RegistryError",
    "RegistryMeta",
    "RegistryParseError",
    "RegistryValidationError",
    "SmokeTestTier",
    "Status",
    "ValidationIssue",
    "Visibility",
    "assert_registry_valid",
    "check_registry_cli_parity",
    "collect_cli_command_inventory",
    "default_registry_path",
    "load_command_registry",
    "parse_registry_data",
    "validate_registry",
]
