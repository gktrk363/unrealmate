# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Sync Docs From Registry
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

#!/usr/bin/env python
"""Sync truth-surface docs from canonical command registry."""

from __future__ import annotations

import argparse
import ast
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
COMMAND_SURFACES_PATH = DOCS_DIR / "COMMAND_SURFACES.md"
SMOKE_TEST_FILES = (
    ROOT / "tests" / "smoke" / "test_cli_smoke_non_destructive.py",
    ROOT / "tests" / "smoke" / "test_cli_smoke_destructive.py",
)

sys.path.insert(0, str(ROOT))

from unrealmate.registry import (  # noqa: E402
    CommandEntry,
    DeprecationState,
    Maturity,
    SmokeTestTier,
    Status,
    load_command_registry,
)


def _escape_md(text: str) -> str:
    return text.replace("|", r"\|").replace("\n", "<br>")


def _normalize_notes(notes: str) -> str:
    clean = " ".join(notes.split())
    return _escape_md(clean) if clean else "-"


def _format_sources(entry: CommandEntry) -> str:
    refs = entry.source_refs or [entry.long_help_source]
    return "<br>".join(f"`{_escape_md(ref)}`" for ref in refs)


def _command_sort_key(entry: CommandEntry) -> tuple[str, str]:
    return (entry.command_group, entry.subcommand)


def _surface_by_maturity(entries: list[CommandEntry], maturity: Maturity) -> list[str]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        if entry.maturity != maturity:
            continue
        grouped[entry.command_group].append(entry.subcommand)

    if not grouped:
        return ["- None."]

    lines: list[str] = []
    for group_name in sorted(grouped):
        subcommands = ", ".join(f"`{item}`" for item in sorted(grouped[group_name]))
        lines.append(f"- `{group_name}`: {subcommands}")
    return lines


def _deprecated_surface(entries: list[CommandEntry]) -> list[str]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        if entry.maturity != Maturity.DEPRECATED and entry.deprecation_state == DeprecationState.ACTIVE:
            continue
        grouped[entry.command_group].append(entry.subcommand)

    if not grouped:
        return ["- None."]

    lines: list[str] = []
    for group_name in sorted(grouped):
        subcommands = ", ".join(f"`{item}`" for item in sorted(grouped[group_name]))
        lines.append(f"- `{group_name}`: {subcommands}")
    return lines


def _commands_as_text(entries: list[CommandEntry]) -> str:
    if not entries:
        return "none"
    return ", ".join(f"`{entry.command_group} {entry.subcommand}`" for entry in sorted(entries, key=_command_sort_key))


def build_maturity_matrix_markdown() -> str:
    registry = load_command_registry()
    entries = sorted([entry for entry in registry.commands if entry.docs_included], key=_command_sort_key)

    lines = [
        "# Command Maturity Matrix",
        "",
        "<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->",
        "<!-- Source: unrealmate/registry/command_registry.toml -->",
        "<!-- Regenerate with: python scripts/sync_docs_from_registry.py -->",
        "",
        "Bu dosya registry metadata'dan otomatik uretilir.",
        "",
        "## Matrix",
        "",
        "| Command Group | Subcommand | Maturity | Status | Visibility | Evidence | Notes |",
        "|---|---|---|---|---|---|---|",
    ]

    for entry in entries:
        lines.append(
            "| `{group}` | `{sub}` | `{maturity}` | `{status}` | `{visibility}` | {evidence} | {notes} |".format(
                group=_escape_md(entry.command_group),
                sub=_escape_md(entry.subcommand),
                maturity=entry.maturity.value,
                status=entry.status.value,
                visibility=entry.visibility.value,
                evidence=_format_sources(entry),
                notes=_normalize_notes(entry.notes),
            )
        )

    lines.extend(
        [
            "",
            "## Stable Surface",
            *_surface_by_maturity(entries, Maturity.STABLE),
            "",
            "## Experimental Surface",
            *_surface_by_maturity(entries, Maturity.EXPERIMENTAL),
            "",
            "## Mock Surface",
            *_surface_by_maturity(entries, Maturity.MOCK),
            "",
            "## Local-only Surface",
            *_surface_by_maturity(entries, Maturity.LOCAL_ONLY),
            "",
            "## Deprecated Surface",
            *_deprecated_surface(entries),
            "",
            "## Immediate Hide/Label Recommendations",
        ]
    )

    mock_visible = [entry for entry in entries if entry.maturity == Maturity.MOCK and entry.default_help_included]
    experimental_visible = [
        entry for entry in entries if entry.maturity == Maturity.EXPERIMENTAL and entry.default_help_included
    ]
    local_only_default = [entry for entry in entries if entry.local_only and entry.default_help_included]
    high_risk_stable = [
        entry
        for entry in entries
        if entry.maturity == Maturity.STABLE and entry.status in {Status.RISKY, Status.PARTIALLY_IMPLEMENTED}
    ]

    if mock_visible:
        lines.append(f"- Hide or label `[mock]` defaults: {_commands_as_text(mock_visible)}.")
    else:
        lines.append("- Policy check: no `mock` command is exposed in default help.")

    if experimental_visible:
        lines.append(
            f"- Move experimental defaults behind opt-in flag or label `[experimental]`: "
            f"{_commands_as_text(experimental_visible)}."
        )
    else:
        lines.append("- Policy check: no `experimental` command is exposed in default help.")

    if local_only_default:
        lines.append(
            f"- Keep explicit `[local-only]` labels on default-visible local commands: "
            f"{_commands_as_text(local_only_default)}."
        )
    else:
        lines.append("- Local-only defaults are not exposed.")

    if high_risk_stable:
        lines.append(
            f"- Stable but risky/partially-implemented commands should keep caution notes: "
            f"{_commands_as_text(high_risk_stable)}."
        )

    return "\n".join(lines).rstrip() + "\n"


def _literal_text(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _canonical_command_from_tokens(tokens: list[str], registry_commands: set[str]) -> str | None:
    if not tokens:
        return None
    if len(tokens) >= 2:
        group_candidate = f"unrealmate {tokens[0]} {tokens[1]}"
        if group_candidate in registry_commands:
            return group_candidate
    root_candidate = f"unrealmate {tokens[0]}"
    if root_candidate in registry_commands:
        return root_candidate
    return None


def _extract_smoke_tested_commands(registry_commands: set[str]) -> set[str]:
    detected: set[str] = set()
    for smoke_file in SMOKE_TEST_FILES:
        if not smoke_file.exists():
            continue
        tree = ast.parse(smoke_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Name) or node.func.id != "run_cli":
                continue
            if not node.args:
                continue
            first_arg = node.args[0]
            if not isinstance(first_arg, ast.List):
                continue
            tokens: list[str] = []
            for item in first_arg.elts[:2]:
                value = _literal_text(item)
                if value is None:
                    break
                tokens.append(value)
            command = _canonical_command_from_tokens(tokens, registry_commands)
            if command is not None:
                detected.add(command)
    return detected


def _invocation(entry: CommandEntry) -> str:
    base = f"python -m {entry.full_command}"
    if entry.command_group == "asset":
        if entry.subcommand in {"scan", "duplicates", "organize"}:
            base += " <fixture_project>/Content"
        if entry.subcommand == "organize":
            base += " --dry-run --yes"
        return base
    if entry.command_group == "build":
        if entry.subcommand == "info":
            return base + " <fixture_project>"
        if entry.subcommand == "ci-init":
            return base + " --platform github --path <fixture_project>"
        if entry.subcommand == "docker":
            return base + " --path <fixture_project>"
    if entry.command_group == "config":
        if entry.subcommand == "get":
            return base + " performance.cache_enabled"
        if entry.subcommand == "init":
            return base + " --force"
        if entry.subcommand == "set":
            return base + " signature.author \"Smoke User\""
        if entry.subcommand == "template":
            return base + " mobile"
    if entry.command_group == "git":
        if entry.subcommand in {"init", "lfs"}:
            return base + " --force"
        if entry.subcommand == "clean":
            return base + " --dry-run --yes"
    if entry.command_group == "performance":
        return base + " <fixture_project>"
    if entry.command_group == "plugin":
        if entry.subcommand == "list":
            return base + " <fixture_project>"
        if entry.subcommand == "install":
            return base + " <local_plugin_source> --path <fixture_project> --name SmokePlugin"
        if entry.subcommand in {"enable", "disable"}:
            return base + " SmokePlugin --path <fixture_project>"
        if entry.subcommand == "remove":
            return base + " SmokePlugin --path <fixture_project> --yes"
    if entry.command_group == "report":
        if entry.subcommand == "html":
            return base + " <fixture_project> --output <temp>/report.html"
        if entry.subcommand == "json":
            return base + " <fixture_project> --output <temp>/report.json"
    return base


def _preconditions(entry: CommandEntry) -> str:
    conditions: list[str] = []
    if entry.destructive:
        conditions.append("Run in disposable temp workspace.")
    if entry.requires_project_path:
        conditions.append("Fixture Unreal-like project path is required.")
    if entry.supports_dry_run:
        conditions.append("Use --dry-run for isolated smoke runs.")
    if entry.requires_fixture_or_external_dependency:
        if entry.external_dependencies:
            deps = ", ".join(entry.external_dependencies)
            conditions.append(f"External dependency: {deps}.")
        else:
            conditions.append("May require fixture data or external dependency.")
    if not conditions:
        return "No additional preconditions."
    return " ".join(conditions)


def _expected_signal(entry: CommandEntry) -> str:
    return _escape_md(entry.short_help)


def _risk_level(entry: CommandEntry) -> str:
    if entry.destructive:
        return "High"
    if entry.status == Status.PRODUCTION_READY:
        return "Low"
    return "Medium"


def _automated_label(entry: CommandEntry, tested_commands: set[str]) -> str:
    if entry.full_command in tested_commands:
        if entry.full_command == "unrealmate git lfs":
            return "Yes (skip if git lfs is unavailable)"
        return "Yes"
    if entry.smoke_test_tier == SmokeTestTier.NONE:
        return "No (pending mapping)"
    return "No"


def _render_smoke_table(entries: list[CommandEntry], tested_commands: set[str]) -> list[str]:
    lines = [
        "| Command | Preconditions | Expected Exit Code | Expected Signal | Risk Level | Automated? |",
        "|---|---|---|---|---|---|",
    ]
    if not entries:
        lines.append("| - | - | - | - | - | - |")
        return lines

    for entry in entries:
        lines.append(
            "| `{command}` | {pre} | `0` | {signal} | `{risk}` | `{auto}` |".format(
                command=_escape_md(_invocation(entry)),
                pre=_escape_md(_preconditions(entry)),
                signal=_expected_signal(entry),
                risk=_risk_level(entry),
                auto=_escape_md(_automated_label(entry, tested_commands)),
            )
        )
    return lines


def build_smoke_matrix_markdown() -> str:
    registry = load_command_registry()
    stable_entries = sorted(
        [entry for entry in registry.commands if entry.docs_included and entry.maturity == Maturity.STABLE],
        key=_command_sort_key,
    )
    non_destructive = [entry for entry in stable_entries if entry.smoke_test_tier == SmokeTestTier.NON_DESTRUCTIVE]
    destructive = [entry for entry in stable_entries if entry.smoke_test_tier == SmokeTestTier.DESTRUCTIVE]
    pending = [entry for entry in stable_entries if entry.smoke_test_tier == SmokeTestTier.NONE]

    registry_commands = {entry.full_command for entry in registry.commands}
    tested_commands = _extract_smoke_tested_commands(registry_commands)
    covered_commands = non_destructive + destructive
    covered_automated = sum(1 for entry in covered_commands if entry.full_command in tested_commands)

    lines = [
        "# Smoke Test Matrix",
        "",
        "<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->",
        "<!-- Source: unrealmate/registry/command_registry.toml + tests/smoke -->",
        "<!-- Regenerate with: python scripts/sync_docs_from_registry.py -->",
        "",
        "Bu dosya stable command metadata ve mevcut smoke test inventory'sinden otomatik uretilir.",
        "",
        "## Coverage Summary",
        f"- Stable commands in registry: `{len(stable_entries)}`",
        f"- Stable commands mapped to smoke tiers: `{len(covered_commands)}`",
        f"- Mapped commands with implemented smoke tests: `{covered_automated}`",
        f"- Stable commands pending smoke mapping: `{len(pending)}`",
        "",
        "## Non-Destructive Stable Commands",
        "",
        *_render_smoke_table(non_destructive, tested_commands),
        "",
        "## Destructive Stable Commands",
        "",
        *_render_smoke_table(destructive, tested_commands),
        "",
        "## Stable Commands Pending Smoke Mapping",
        "",
        *_render_smoke_table(pending, tested_commands),
        "",
        "## Safety Notes",
        "",
        "- `destructive=true` satirlari sadece disposable fixture/temp workspace'te kosulmalidir.",
        "- `supports_dry_run=true` komutlar smoke kosularinda dry-run ile calistirilmalidir.",
        "- Sistem bagimli testler acik skip nedeni ile calisabilir (`git lfs` gibi).",
        "- UTF-8 guvenli output ortami (`PYTHONIOENCODING=utf-8`) smoke job varsayimi olarak korunmalidir.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def build_command_surfaces_markdown() -> str:
    maturity = build_maturity_matrix_markdown().rstrip()
    smoke = build_smoke_matrix_markdown().rstrip()

    lines = [
        "# Command Surfaces",
        "",
        "<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->",
        "<!-- Source: unrealmate/registry/command_registry.toml + tests/smoke -->",
        "<!-- Regenerate with: python scripts/sync_docs_from_registry.py -->",
        "",
        "Bu dosya command truth surfaces icerigini registry metadata'dan otomatik uretilmis tek kaynakta birlestirir.",
        "",
        "## Command Maturity Matrix",
        "",
        maturity,
        "",
        "## Smoke Test Matrix",
        "",
        smoke,
    ]
    return "\n".join(lines).rstrip() + "\n"


def _sync_file(path: Path, expected_content: str, check_only: bool) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == expected_content:
        return False
    if check_only:
        return True
    path.write_text(expected_content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync docs truth surfaces from command registry.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated docs are not up-to-date. Does not write files.",
    )
    args = parser.parse_args()

    command_surfaces_content = build_command_surfaces_markdown()

    changed = []
    if _sync_file(COMMAND_SURFACES_PATH, command_surfaces_content, check_only=args.check):
        changed.append(str(COMMAND_SURFACES_PATH.relative_to(ROOT)))

    if args.check and changed:
        print("Docs are out of date. Run: python scripts/sync_docs_from_registry.py")
        for item in changed:
            print(f"- {item}")
        return 1

    if changed:
        print("Updated docs from registry:")
        for item in changed:
            print(f"- {item}")
    else:
        print("Docs are already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
