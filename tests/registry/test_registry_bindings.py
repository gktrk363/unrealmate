# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Registry Bindings
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Binding checks for registry-backed completion and docs surfaces."""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from unrealmate.registry import Maturity, Status, Visibility, load_command_registry


REPO_ROOT = Path(__file__).resolve().parents[2]
COMMAND_SURFACES_PATH = REPO_ROOT / "docs" / "COMMAND_SURFACES.md"


def _registry_completion_surface() -> tuple[set[str], dict[str, set[str]]]:
    registry = load_command_registry()
    base_commands: set[str] = set()
    subcommands_by_group: dict[str, set[str]] = defaultdict(set)

    for entry in registry.commands:
        if not entry.completion_included:
            continue
        if entry.visibility != Visibility.DEFAULT:
            continue
        if entry.command_group == "root":
            base_commands.add(entry.subcommand)
            continue
        base_commands.add(entry.command_group)
        subcommands_by_group[entry.command_group].add(entry.subcommand)

    return base_commands, dict(subcommands_by_group)


def _parse_zsh_array(content: str, array_name: str) -> list[str]:
    pattern = rf"{array_name}=\((.*?)\n    \)"
    match = re.search(pattern, content, re.DOTALL)
    if match is None:
        return []
    block = match.group(1)
    entries = re.findall(r"'([^']+)'", block)
    return [entry.split(":", 1)[0] for entry in entries]


def _parse_bash_words(content: str, variable_name: str) -> list[str]:
    match = re.search(rf'{variable_name}="([^"]*)"', content)
    if match is None:
        return []
    return [token for token in match.group(1).split() if token]


def _parse_ps1_array(content: str, variable_name: str) -> list[str]:
    pattern = rf"\${variable_name}\s*=\s*@\((.*?)\n\s*\)"
    match = re.search(pattern, content, re.DOTALL)
    if match is None:
        return []
    block = match.group(1)
    return re.findall(r"Name\s*=\s*'([^']+)'", block)


def test_completion_scripts_match_registry_default_surface() -> None:
    expected_base, expected_subcommands = _registry_completion_surface()

    zsh_text = (REPO_ROOT / "scripts" / "_unrealmate").read_text(encoding="utf-8")
    bash_text = (REPO_ROOT / "scripts" / "unrealmate_completion.bash").read_text(encoding="utf-8")
    ps1_text = (REPO_ROOT / "scripts" / "unrealmate_completion.ps1").read_text(encoding="utf-8")

    assert set(_parse_zsh_array(zsh_text, "commands")) == expected_base
    assert set(_parse_bash_words(bash_text, "base_commands")) == expected_base
    assert set(_parse_ps1_array(ps1_text, "baseCommands")) == expected_base

    for group_name, expected_subs in expected_subcommands.items():
        assert set(_parse_zsh_array(zsh_text, f"{group_name}_commands")) == expected_subs
        assert set(_parse_bash_words(bash_text, f"{group_name}_commands")) == expected_subs
        ps1_var = "".join(part.capitalize() for part in group_name.split("-")) + "Commands"
        assert set(_parse_ps1_array(ps1_text, ps1_var)) == expected_subs


def test_docs_sync_script_reports_up_to_date() -> None:
    proc = subprocess.run(
        [sys.executable, "scripts/sync_docs_from_registry.py", "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_completion_scripts_do_not_expose_known_stale_aliases_or_commands() -> None:
    zsh_text = (REPO_ROOT / "scripts" / "_unrealmate").read_text(encoding="utf-8")
    bash_text = (REPO_ROOT / "scripts" / "unrealmate_completion.bash").read_text(encoding="utf-8")
    ps1_text = (REPO_ROOT / "scripts" / "unrealmate_completion.ps1").read_text(encoding="utf-8")
    stale_base_commands = {
        "bp",
        "perf",
        "cfg",
        "blueprint",
        "ai",
        "automate",
        "backup",
        "collab",
        "marketplace",
        "migrate",
        "optimize",
        "template",
        "health",
        "security-scan",
    }
    stale_subcommands_by_group = {
        "git": {"status"},
        "asset": {"validate"},
        "build": {"generate", "validate"},
        "performance": {"shader", "audit", "drawcalls", "network"},
    }

    zsh_base = set(_parse_zsh_array(zsh_text, "commands"))
    bash_base = set(_parse_bash_words(bash_text, "base_commands"))
    ps1_base = set(_parse_ps1_array(ps1_text, "baseCommands"))

    assert zsh_base.isdisjoint(stale_base_commands)
    assert bash_base.isdisjoint(stale_base_commands)
    assert ps1_base.isdisjoint(stale_base_commands)

    for group_name, stale_subcommands in stale_subcommands_by_group.items():
        zsh_sub = set(_parse_zsh_array(zsh_text, f"{group_name}_commands"))
        bash_sub = set(_parse_bash_words(bash_text, f"{group_name}_commands"))
        ps1_var = "".join(part.capitalize() for part in group_name.split("-")) + "Commands"
        ps1_sub = set(_parse_ps1_array(ps1_text, ps1_var))

        assert zsh_sub.isdisjoint(stale_subcommands)
        assert bash_sub.isdisjoint(stale_subcommands)
        assert ps1_sub.isdisjoint(stale_subcommands)


def test_maturity_matrix_rows_match_registry_and_enums() -> None:
    registry = load_command_registry()
    expected = {
        (entry.command_group, entry.subcommand)
        for entry in registry.commands
        if entry.docs_included
    }
    maturity_values = {item.value for item in Maturity}
    status_values = {item.value for item in Status}
    visibility_values = {item.value for item in Visibility}

    matrix_text = COMMAND_SURFACES_PATH.read_text(encoding="utf-8")
    actual: set[tuple[str, str]] = set()

    for line in matrix_text.splitlines():
        if not line.startswith("| `"):
            continue
        parts = [part.strip() for part in line.strip().split("|")[1:-1]]
        if len(parts) != 7:
            continue
        command_group = parts[0].strip("`")
        subcommand = parts[1].strip("`")
        maturity = parts[2].strip("`")
        status = parts[3].strip("`")
        visibility = parts[4].strip("`")

        actual.add((command_group, subcommand))
        assert maturity in maturity_values
        assert status in status_values
        assert visibility in visibility_values

    assert actual == expected


def test_smoke_matrix_command_examples_resolve_to_registry_commands() -> None:
    registry = load_command_registry()
    registry_commands = {entry.full_command for entry in registry.commands}

    smoke_matrix = COMMAND_SURFACES_PATH.read_text(encoding="utf-8")
    command_blocks = re.findall(r"`python -m (unrealmate [^`]+)`", smoke_matrix)
    unresolved: list[str] = []

    for block in command_blocks:
        tokens = shlex.split(block)
        if len(tokens) < 2:
            unresolved.append(block)
            continue
        canonical_root = f"{tokens[0]} {tokens[1]}"
        canonical_group = ""
        if len(tokens) >= 3:
            canonical_group = f"{tokens[0]} {tokens[1]} {tokens[2]}"

        if canonical_group and canonical_group in registry_commands:
            continue
        if canonical_root in registry_commands:
            continue
        unresolved.append(block)

    assert unresolved == []


def test_smoke_matrix_covers_all_stable_docs_commands() -> None:
    registry = load_command_registry()
    expected = {
        entry.full_command
        for entry in registry.commands
        if entry.docs_included and entry.maturity == Maturity.STABLE
    }

    smoke_matrix = COMMAND_SURFACES_PATH.read_text(encoding="utf-8")
    command_blocks = re.findall(r"`python -m (unrealmate [^`]+)`", smoke_matrix)
    resolved: set[str] = set()

    for block in command_blocks:
        tokens = shlex.split(block)
        if len(tokens) < 2:
            continue
        canonical_root = f"{tokens[0]} {tokens[1]}"
        canonical_group = ""
        if len(tokens) >= 3:
            canonical_group = f"{tokens[0]} {tokens[1]} {tokens[2]}"
        if canonical_group and canonical_group in expected:
            resolved.add(canonical_group)
            continue
        if canonical_root in expected:
            resolved.add(canonical_root)

    assert resolved == expected


def test_docs_no_longer_mark_fixed_rows_as_broken() -> None:
    maturity_matrix = COMMAND_SURFACES_PATH.read_text(encoding="utf-8")

    assert "| `marketplace` | `install` | `mock` | `broken` |" not in maturity_matrix
    assert "| `automate` | `organize` | `experimental` | `broken` |" not in maturity_matrix


def test_docs_truth_surfaces_do_not_reference_removed_alias_commands() -> None:
    docs_blob = "\n".join(
        [
            (REPO_ROOT / "README.md").read_text(encoding="utf-8"),
            COMMAND_SURFACES_PATH.read_text(encoding="utf-8"),
        ]
    )
    stale_command_patterns = [
        r"\bunrealmate\s+bp(\s|$)",
        r"\bunrealmate\s+perf(\s|$)",
        r"\bunrealmate\s+cfg(\s|$)",
        r"\bunrealmate\s+git\s+status(\s|$)",
        r"\bunrealmate\s+asset\s+validate(\s|$)",
        r"\bunrealmate\s+build\s+generate(\s|$)",
        r"\bunrealmate\s+build\s+validate(\s|$)",
    ]
    for pattern in stale_command_patterns:
        assert re.search(pattern, docs_blob) is None


def test_readme_first_run_section_stays_safe_first() -> None:
    readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    match = re.search(
        r"^## .*First Run\s*$\n(?P<body>.*?)(?=^---\s*$|^##\s)",
        readme_text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None
    first_run = match.group("body")

    assert "unrealmate doctor" in first_run
    assert "unrealmate config show" in first_run
    assert "unrealmate asset scan Content" in first_run
    assert "unrealmate build info ." in first_run

    assert "unrealmate report dashboard" not in first_run
    assert "unrealmate config init" not in first_run
    assert "unrealmate git clean" not in first_run
    assert "unrealmate plugin install" not in first_run


def test_readme_install_and_project_path_guidance_stays_clear_and_cross_platform() -> None:
    readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "pip install unrealmate" in readme_text
    assert "python -m unrealmate version" in readme_text
    assert "Run UnrealMate from your Unreal project root" in readme_text
    assert "or pass `<project-root>` to commands that accept a project path" in readme_text
    assert "python -m unrealmate build info <project-root>" in readme_text
    assert "python -m unrealmate plugin list <project-root>" in readme_text
    assert "C:\\Projects\\" not in readme_text
    assert "python -m unrealmate --help-all" in readme_text
