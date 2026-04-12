# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Command Registry
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Phase-1 tests for command registry loading, validation and parity."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import pytest
import toml

from unrealmate.registry import (
    Maturity,
    RegistryParseError,
    SmokeTestTier,
    Status,
    Visibility,
    assert_registry_valid,
    check_registry_cli_parity,
    default_registry_path,
    load_command_registry,
    parse_registry_data,
    validate_registry,
)


def _entry_by_command(full_command: str):
    registry = load_command_registry()
    entries = {entry.full_command: entry for entry in registry.commands}
    return entries[full_command]


def test_registry_loads_from_canonical_toml() -> None:
    registry = load_command_registry()

    assert registry.meta.version == 1
    assert len(registry.commands) >= 59


def test_registry_contains_required_phase1_commands() -> None:
    version = _entry_by_command("unrealmate version")
    doctor = _entry_by_command("unrealmate doctor")
    config_show = _entry_by_command("unrealmate config show")
    git_init = _entry_by_command("unrealmate git init")
    marketplace_install = _entry_by_command("unrealmate marketplace install")
    report_notify = _entry_by_command("unrealmate report notify")
    automate_organize = _entry_by_command("unrealmate automate organize")

    assert version.maturity == Maturity.STABLE
    assert version.status == Status.PRODUCTION_READY
    assert version.smoke_test_tier == SmokeTestTier.NON_DESTRUCTIVE

    assert doctor.maturity == Maturity.STABLE
    assert config_show.maturity == Maturity.STABLE
    assert git_init.maturity == Maturity.STABLE
    assert git_init.destructive is True

    assert marketplace_install.maturity == Maturity.MOCK
    assert marketplace_install.visibility == Visibility.OPT_IN
    assert marketplace_install.default_help_included is False

    assert report_notify.maturity == Maturity.LOCAL_ONLY
    assert report_notify.local_only is True

    assert automate_organize.maturity == Maturity.EXPERIMENTAL
    assert automate_organize.visibility == Visibility.OPT_IN


def test_parse_registry_rejects_invalid_enum_values() -> None:
    raw = toml.loads(default_registry_path().read_text(encoding="utf-8"))
    broken = deepcopy(raw)
    broken["commands"][0]["maturity"] = "invalid-maturity"

    with pytest.raises(RegistryParseError):
        parse_registry_data(broken)


def test_validator_detects_duplicate_and_alias_collisions() -> None:
    registry = load_command_registry()
    first = registry.commands[0]
    second = registry.commands[1]

    duplicate_full = replace(
        first,
        command_group="tmp",
        subcommand="dup-full",
    )
    alias_a = replace(
        first,
        full_command="unrealmate tmp alpha",
        command_group="tmp",
        subcommand="alpha",
        aliases=["um:shared"],
    )
    alias_b = replace(
        second,
        full_command="unrealmate tmp beta",
        command_group="tmp",
        subcommand="beta",
        aliases=["um:shared"],
    )
    broken_registry = replace(
        registry,
        commands=[first, second, duplicate_full, alias_a, alias_b],
    )

    issues = validate_registry(broken_registry)
    issue_codes = {issue.code for issue in issues}

    assert "duplicate_full_command" in issue_codes
    assert "alias_collision" in issue_codes


def test_validator_detects_visibility_and_local_only_rule_violations() -> None:
    registry = load_command_registry()
    marketplace_install = _entry_by_command("unrealmate marketplace install")
    report_notify = _entry_by_command("unrealmate report notify")

    mock_visible = replace(
        marketplace_install,
        default_help_included=True,
    )
    hidden_with_completion = replace(
        marketplace_install,
        visibility=Visibility.HIDDEN,
        completion_included=True,
    )
    local_only_broken = replace(
        report_notify,
        local_only=False,
    )
    destructive_without_notes = replace(
        _entry_by_command("unrealmate git init"),
        notes="",
    )
    bad_smoke_marker = replace(
        _entry_by_command("unrealmate automate organize"),
        smoke_test_tier=SmokeTestTier.NON_DESTRUCTIVE,
    )

    broken_registry = replace(
        registry,
        commands=[
            mock_visible,
            hidden_with_completion,
            local_only_broken,
            destructive_without_notes,
            bad_smoke_marker,
        ],
    )

    issues = validate_registry(broken_registry)
    issue_codes = {issue.code for issue in issues}

    assert "mock_visible_in_default_help" in issue_codes
    assert "hidden_completion_included" in issue_codes
    assert "local_only_flag_required" in issue_codes
    assert "destructive_missing_notes" in issue_codes
    assert "non_stable_smoke_tier" in issue_codes


def test_cli_parity_report_matches_registry_inventory() -> None:
    registry = load_command_registry()

    report = check_registry_cli_parity(registry=registry, strict=True)

    assert report.is_full_match is True
    assert report.registry_count == report.cli_count
    assert report.missing_in_registry == ()
    assert report.orphaned_in_registry == ()


def test_canonical_registry_validates_with_parity() -> None:
    registry = load_command_registry()
    parity = check_registry_cli_parity(registry=registry)

    assert_registry_valid(registry=registry, parity_report=parity)
