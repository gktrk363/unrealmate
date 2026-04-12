# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Loader
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Loader and parser utilities for the command registry."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Any, TypeVar

import toml

from unrealmate.registry.models import (
    CommandEntry,
    CommandRegistry,
    DeprecationState,
    Maturity,
    RegistryMeta,
    RegistryParseError,
    SmokeTestTier,
    Status,
    Visibility,
)


TEnum = TypeVar("TEnum")

_REQUIRED_ENTRY_FIELDS = (
    "command_group",
    "subcommand",
    "full_command",
    "aliases",
    "maturity",
    "status",
    "visibility",
    "destructive",
    "supports_dry_run",
    "requires_project_path",
    "requires_fixture_or_external_dependency",
    "local_only",
    "category",
    "short_help",
    "long_help_source",
    "docs_included",
    "completion_included",
    "default_help_included",
    "deprecation_state",
    "replacement_command",
    "owner_module",
    "notes",
)


def default_registry_path() -> Path:
    """Return the canonical command registry path."""
    return Path(resources.files("unrealmate.registry").joinpath("command_registry.toml"))


def _enum_value(enum_cls: type[TEnum], raw_value: Any, field_name: str, index: int) -> TEnum:
    if not isinstance(raw_value, str):
        raise RegistryParseError(
            f"Command #{index} field '{field_name}' must be a string, got: {type(raw_value).__name__}"
        )
    try:
        return enum_cls(raw_value)  # type: ignore[arg-type]
    except ValueError as exc:
        allowed = ", ".join(value.value for value in enum_cls)  # type: ignore[attr-defined]
        raise RegistryParseError(
            f"Command #{index} has invalid '{field_name}' value '{raw_value}'. Allowed: {allowed}"
        ) from exc


def _list_of_strings(raw_value: Any, field_name: str, index: int) -> list[str]:
    if raw_value is None:
        return []
    if not isinstance(raw_value, list):
        raise RegistryParseError(
            f"Command #{index} field '{field_name}' must be a list of strings."
        )
    result: list[str] = []
    for item in raw_value:
        if not isinstance(item, str):
            raise RegistryParseError(
                f"Command #{index} field '{field_name}' contains non-string item: {item!r}"
            )
        result.append(item)
    return result


def _bool_value(raw_value: Any, field_name: str, index: int) -> bool:
    if not isinstance(raw_value, bool):
        raise RegistryParseError(
            f"Command #{index} field '{field_name}' must be boolean, got: {type(raw_value).__name__}"
        )
    return raw_value


def _str_value(raw_value: Any, field_name: str, index: int) -> str:
    if not isinstance(raw_value, str):
        raise RegistryParseError(
            f"Command #{index} field '{field_name}' must be a string, got: {type(raw_value).__name__}"
        )
    return raw_value


def _validate_required_fields(raw_entry: dict[str, Any], index: int) -> None:
    missing = [field for field in _REQUIRED_ENTRY_FIELDS if field not in raw_entry]
    if missing:
        raise RegistryParseError(
            f"Command #{index} is missing required field(s): {', '.join(sorted(missing))}"
        )


def parse_registry_data(raw_data: dict[str, Any]) -> CommandRegistry:
    """Parse raw dictionary data into a typed command registry."""
    if not isinstance(raw_data, dict):
        raise RegistryParseError("Registry payload must be a dictionary.")

    meta_section = raw_data.get("registry")
    if not isinstance(meta_section, dict):
        raise RegistryParseError("Registry file must contain a [registry] section.")
    version = meta_section.get("version")
    if not isinstance(version, int):
        raise RegistryParseError("Registry [registry].version must be an integer.")
    source = meta_section.get("source", "unrealmate/registry/command_registry.toml")
    coverage = meta_section.get("coverage", "phase1")
    if not isinstance(source, str) or not isinstance(coverage, str):
        raise RegistryParseError("Registry metadata fields 'source' and 'coverage' must be strings.")
    meta = RegistryMeta(version=version, source=source, coverage=coverage)

    commands_section = raw_data.get("commands")
    if not isinstance(commands_section, list):
        raise RegistryParseError("Registry file must contain a [[commands]] list.")

    parsed_commands: list[CommandEntry] = []
    for index, raw_entry in enumerate(commands_section, start=1):
        if not isinstance(raw_entry, dict):
            raise RegistryParseError(f"Command #{index} must be a dictionary table.")
        _validate_required_fields(raw_entry, index)
        replacement_command = raw_entry.get("replacement_command")
        if replacement_command == "":
            replacement_command = None
        if replacement_command is not None and not isinstance(replacement_command, str):
            raise RegistryParseError(
                f"Command #{index} field 'replacement_command' must be string or null."
            )

        parsed_commands.append(
            CommandEntry(
                command_group=_str_value(raw_entry["command_group"], "command_group", index),
                subcommand=_str_value(raw_entry["subcommand"], "subcommand", index),
                full_command=_str_value(raw_entry["full_command"], "full_command", index),
                aliases=_list_of_strings(raw_entry["aliases"], "aliases", index),
                maturity=_enum_value(Maturity, raw_entry["maturity"], "maturity", index),
                status=_enum_value(Status, raw_entry["status"], "status", index),
                visibility=_enum_value(Visibility, raw_entry["visibility"], "visibility", index),
                destructive=_bool_value(raw_entry["destructive"], "destructive", index),
                supports_dry_run=_bool_value(raw_entry["supports_dry_run"], "supports_dry_run", index),
                requires_project_path=_bool_value(
                    raw_entry["requires_project_path"], "requires_project_path", index
                ),
                requires_fixture_or_external_dependency=_bool_value(
                    raw_entry["requires_fixture_or_external_dependency"],
                    "requires_fixture_or_external_dependency",
                    index,
                ),
                local_only=_bool_value(raw_entry["local_only"], "local_only", index),
                category=_str_value(raw_entry["category"], "category", index),
                short_help=_str_value(raw_entry["short_help"], "short_help", index),
                long_help_source=_str_value(raw_entry["long_help_source"], "long_help_source", index),
                docs_included=_bool_value(raw_entry["docs_included"], "docs_included", index),
                completion_included=_bool_value(
                    raw_entry["completion_included"], "completion_included", index
                ),
                default_help_included=_bool_value(
                    raw_entry["default_help_included"], "default_help_included", index
                ),
                deprecation_state=_enum_value(
                    DeprecationState, raw_entry["deprecation_state"], "deprecation_state", index
                ),
                replacement_command=replacement_command,
                owner_module=_str_value(raw_entry["owner_module"], "owner_module", index),
                notes=_str_value(raw_entry["notes"], "notes", index),
                external_dependencies=_list_of_strings(
                    raw_entry.get("external_dependencies", []), "external_dependencies", index
                ),
                smoke_test_tier=_enum_value(
                    SmokeTestTier, raw_entry.get("smoke_test_tier", "none"), "smoke_test_tier", index
                ),
                source_refs=_list_of_strings(raw_entry.get("source_refs", []), "source_refs", index),
                introduced_in=_str_value(raw_entry.get("introduced_in", "phase1"), "introduced_in", index),
            )
        )

    return CommandRegistry(meta=meta, commands=parsed_commands)


def load_command_registry(path: Path | None = None) -> CommandRegistry:
    """Load command registry from TOML and return typed data."""
    registry_path = path or default_registry_path()
    try:
        raw_data = toml.loads(registry_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RegistryParseError(f"Registry file not found: {registry_path}") from exc
    except toml.TomlDecodeError as exc:
        raise RegistryParseError(f"Invalid TOML in registry file: {registry_path}") from exc
    return parse_registry_data(raw_data)
