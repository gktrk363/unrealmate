# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Validator
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Validation rules for command registry metadata."""

from __future__ import annotations

from dataclasses import dataclass

from unrealmate.registry.models import (
    CommandRegistry,
    DeprecationState,
    Maturity,
    RegistryValidationError,
    SmokeTestTier,
    Status,
    Visibility,
)
from unrealmate.registry.parity import ParityReport


@dataclass(frozen=True)
class ValidationIssue:
    """Single registry validation issue."""

    code: str
    message: str
    full_command: str | None = None

    def as_text(self) -> str:
        if self.full_command:
            return f"[{self.code}] {self.full_command}: {self.message}"
        return f"[{self.code}] {self.message}"


def validate_registry(
    registry: CommandRegistry,
    parity_report: ParityReport | None = None,
) -> list[ValidationIssue]:
    """Return all validation issues discovered in registry content."""
    issues: list[ValidationIssue] = []

    full_command_seen: dict[str, str] = {}
    key_seen: dict[tuple[str, str], str] = {}
    alias_seen: dict[str, str] = {}

    for entry in registry.commands:
        if entry.full_command in full_command_seen:
            issues.append(
                ValidationIssue(
                    code="duplicate_full_command",
                    message=f"Already defined by {full_command_seen[entry.full_command]}",
                    full_command=entry.full_command,
                )
            )
        else:
            full_command_seen[entry.full_command] = entry.full_command

        if entry.key in key_seen:
            issues.append(
                ValidationIssue(
                    code="duplicate_command_key",
                    message=f"Duplicate command key {entry.command_group}/{entry.subcommand}",
                    full_command=entry.full_command,
                )
            )
        else:
            key_seen[entry.key] = entry.full_command

        for alias in entry.aliases:
            existing = alias_seen.get(alias)
            if existing and existing != entry.full_command:
                issues.append(
                    ValidationIssue(
                        code="alias_collision",
                        message=f"Alias '{alias}' already used by {existing}",
                        full_command=entry.full_command,
                    )
                )
            alias_seen[alias] = entry.full_command
            if alias in full_command_seen and alias != entry.full_command:
                issues.append(
                    ValidationIssue(
                        code="alias_full_command_collision",
                        message=f"Alias '{alias}' conflicts with canonical command name",
                        full_command=entry.full_command,
                    )
                )

        if entry.maturity == Maturity.MOCK and entry.default_help_included:
            issues.append(
                ValidationIssue(
                    code="mock_visible_in_default_help",
                    message="Mock command must not appear in default help.",
                    full_command=entry.full_command,
                )
            )

        if entry.visibility == Visibility.HIDDEN and entry.completion_included:
            issues.append(
                ValidationIssue(
                    code="hidden_completion_included",
                    message="Hidden command must not be included in completion.",
                    full_command=entry.full_command,
                )
            )

        if entry.local_only and entry.maturity not in {Maturity.LOCAL_ONLY, Maturity.STABLE}:
            issues.append(
                ValidationIssue(
                    code="local_only_maturity_mismatch",
                    message="Local-only command must have maturity 'local-only' or justified stable.",
                    full_command=entry.full_command,
                )
            )
        if entry.maturity == Maturity.LOCAL_ONLY and not entry.local_only:
            issues.append(
                ValidationIssue(
                    code="local_only_flag_required",
                    message="Maturity 'local-only' requires local_only=true.",
                    full_command=entry.full_command,
                )
            )

        if entry.destructive and not entry.notes.strip():
            issues.append(
                ValidationIssue(
                    code="destructive_missing_notes",
                    message="Destructive command must include safety notes.",
                    full_command=entry.full_command,
                )
            )

        if entry.requires_fixture_or_external_dependency and not entry.external_dependencies:
            issues.append(
                ValidationIssue(
                    code="missing_external_dependencies",
                    message="requires_fixture_or_external_dependency=true but no external_dependencies defined.",
                    full_command=entry.full_command,
                )
            )

        if not entry.docs_included and entry.default_help_included:
            issues.append(
                ValidationIssue(
                    code="docs_help_inconsistency",
                    message="Command cannot be in default help while excluded from docs.",
                    full_command=entry.full_command,
                )
            )

        if entry.deprecation_state != DeprecationState.ACTIVE:
            if entry.deprecation_state != DeprecationState.REMOVED and not entry.replacement_command:
                issues.append(
                    ValidationIssue(
                        code="deprecated_missing_replacement",
                        message="Deprecated command requires replacement_command.",
                        full_command=entry.full_command,
                    )
                )

        if entry.status == Status.BROKEN and entry.default_help_included:
            issues.append(
                ValidationIssue(
                    code="broken_visible_in_default_help",
                    message="Broken command must not be shown in default help.",
                    full_command=entry.full_command,
                )
            )

        if entry.smoke_test_tier != SmokeTestTier.NONE and entry.maturity != Maturity.STABLE:
            issues.append(
                ValidationIssue(
                    code="non_stable_smoke_tier",
                    message="Only stable commands should be marked with smoke_test_tier.",
                    full_command=entry.full_command,
                )
            )

    if parity_report is not None:
        for missing in parity_report.missing_in_registry:
            issues.append(
                ValidationIssue(
                    code="parity_missing_in_registry",
                    message="CLI command is missing from registry.",
                    full_command=missing,
                )
            )
        for orphaned in parity_report.orphaned_in_registry:
            issues.append(
                ValidationIssue(
                    code="parity_orphaned_registry_entry",
                    message="Registry command is not present in CLI inventory.",
                    full_command=orphaned,
                )
            )

    return issues


def assert_registry_valid(
    registry: CommandRegistry,
    parity_report: ParityReport | None = None,
) -> None:
    """Raise RegistryValidationError if validation issues are found."""
    issues = validate_registry(registry=registry, parity_report=parity_report)
    if issues:
        raise RegistryValidationError([issue.as_text() for issue in issues])
