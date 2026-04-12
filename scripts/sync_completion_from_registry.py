# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Sync Completion From Registry
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

#!/usr/bin/env python
"""Sync shell completion scripts from canonical command registry."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from unrealmate.registry import Visibility, load_command_registry  # noqa: E402


GROUP_DESCRIPTIONS = {
    "asset": "Asset management commands",
    "build": "Build and CI/CD tools",
    "config": "Configuration management",
    "git": "Git helper commands",
    "performance": "Performance analysis commands",
    "plugin": "Plugin management",
    "report": "Reporting commands",
}


def _clean_description(text: str) -> str:
    return " ".join(text.replace(":", " - ").split())


def _build_completion_surface() -> tuple[list[tuple[str, str]], dict[str, list[tuple[str, str]]]]:
    registry = load_command_registry()
    root_commands: list[tuple[str, str]] = []
    group_commands: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for entry in registry.commands:
        if not entry.completion_included:
            continue
        if entry.visibility != Visibility.DEFAULT:
            continue

        desc = _clean_description(entry.short_help)
        if entry.local_only:
            desc = f"{desc} (local-only)"

        if entry.command_group == "root":
            root_commands.append((entry.subcommand, desc))
        else:
            group_commands[entry.command_group].append((entry.subcommand, desc))

    root_commands.sort(key=lambda item: item[0])
    for group_name in list(group_commands.keys()):
        group_commands[group_name] = sorted(group_commands[group_name], key=lambda item: item[0])

    return root_commands, dict(sorted(group_commands.items(), key=lambda item: item[0]))


def _render_zsh(root_commands: list[tuple[str, str]], groups: dict[str, list[tuple[str, str]]]) -> str:
    group_vars = [f"{name}_commands" for name in groups]
    header = [
        "#compdef unrealmate",
        "# Generated from unrealmate/registry/command_registry.toml",
        "# Do not edit manually; run: python scripts/sync_completion_from_registry.py",
        "",
        "_unrealmate() {",
        "    local -a commands",
    ]
    for var in group_vars:
        header.append(f"    local -a {var}")

    lines = header + ["", "    commands=("]
    base_entries: list[tuple[str, str]] = []
    for group_name in groups:
        base_entries.append((group_name, GROUP_DESCRIPTIONS.get(group_name, "Command group")))
    base_entries.extend(root_commands)
    for name, description in base_entries:
        lines.append(f"        '{name}:{description}'")
    lines.append("    )")
    lines.append("")

    for group_name, subcommands in groups.items():
        lines.append(f"    {group_name}_commands=(")
        for name, description in subcommands:
            lines.append(f"        '{name}:{description}'")
        lines.append("    )")
        lines.append("")

    lines.extend(
        [
            "    _arguments -C \\",
            "        '1: :->command' \\",
            "        '2: :->subcommand' \\",
            "        '*: :->args'",
            "",
            "    case $state in",
            "        command)",
            "            _describe 'command' commands",
            "            ;;",
            "        subcommand)",
            "            case $words[2] in",
        ]
    )

    for group_name in groups:
        lines.extend(
            [
                f"                {group_name})",
                f"                    _describe '{group_name} subcommand' {group_name}_commands",
                "                    ;;",
            ]
        )

    lines.extend(
        [
            "            esac",
            "            ;;",
            "        args)",
            "            _files",
            "            ;;",
            "    esac",
            "}",
            "",
            "_unrealmate \"$@\"",
            "",
        ]
    )
    return "\n".join(lines)


def _render_bash(root_commands: list[tuple[str, str]], groups: dict[str, list[tuple[str, str]]]) -> str:
    base_names = [group_name for group_name in groups] + [name for name, _ in root_commands]
    lines = [
        "#!/usr/bin/env bash",
        "# Generated from unrealmate/registry/command_registry.toml",
        "# Do not edit manually; run: python scripts/sync_completion_from_registry.py",
        "",
        "_unrealmate_completion() {",
        "    local cur prev base_commands",
        "    COMPREPLY=()",
        "    cur=\"${COMP_WORDS[COMP_CWORD]}\"",
        "    prev=\"${COMP_WORDS[COMP_CWORD-1]}\"",
        "",
        f"    base_commands=\"{' '.join(base_names)}\"",
    ]

    for group_name, subcommands in groups.items():
        subcommand_names = " ".join(name for name, _ in subcommands)
        lines.append(f"    {group_name}_commands=\"{subcommand_names}\"")

    lines.extend(
        [
            "",
            "    case \"${prev}\" in",
            "        unrealmate)",
            "            COMPREPLY=( $(compgen -W \"${base_commands}\" -- ${cur}) )",
            "            return 0",
            "            ;;",
        ]
    )

    for group_name in groups:
        lines.extend(
            [
                f"        {group_name})",
                f"            COMPREPLY=( $(compgen -W \"${{{group_name}_commands}}\" -- ${{cur}}) )",
                "            return 0",
                "            ;;",
            ]
        )

    lines.extend(
        [
            "        *)",
            "            ;;",
            "    esac",
            "",
            "    COMPREPLY=( $(compgen -f -- ${cur}) )",
            "    return 0",
            "}",
            "",
            "complete -F _unrealmate_completion unrealmate",
            "",
        ]
    )

    return "\n".join(lines)


def _render_ps1(root_commands: list[tuple[str, str]], groups: dict[str, list[tuple[str, str]]]) -> str:
    lines = [
        "# Generated from unrealmate/registry/command_registry.toml",
        "# Do not edit manually; run: python scripts/sync_completion_from_registry.py",
        "",
        "Register-ArgumentCompleter -Native -CommandName unrealmate -ScriptBlock {",
        "    param($wordToComplete, $commandAst, $cursorPosition)",
        "",
        "    $baseCommands = @(",
    ]

    for group_name in groups:
        desc = GROUP_DESCRIPTIONS.get(group_name, "Command group")
        lines.append(f"        @{{ Name = '{group_name}'; Description = '{desc}' }}")
    for name, description in root_commands:
        lines.append(f"        @{{ Name = '{name}'; Description = '{description}' }}")
    lines.append("    )")
    lines.append("")

    for group_name, subcommands in groups.items():
        pascal_name = "".join(part.capitalize() for part in group_name.split("-"))
        variable = f"${pascal_name}Commands"
        lines.append(f"    {variable} = @(")
        for name, description in subcommands:
            lines.append(f"        @{{ Name = '{name}'; Description = '{description}' }}")
        lines.append("    )")
        lines.append("")

    lines.extend(
        [
            "    $elements = $commandAst.CommandElements",
            "    $commands = @()",
            "",
            "    if ($elements.Count -ge 2) {",
            "        $subCommand = $elements[1].Extent.Text",
            "",
            "        switch ($subCommand) {",
        ]
    )

    for group_name in groups:
        pascal_name = "".join(part.capitalize() for part in group_name.split("-"))
        variable = f"${pascal_name}Commands"
        lines.append(f"            '{group_name}' {{ $commands = {variable} }}")

    lines.extend(
        [
            "            default { $commands = @() }",
            "        }",
            "    }",
            "    else {",
            "        $commands = $baseCommands",
            "    }",
            "",
            "    $commands | Where-Object { $_.Name -like \"$wordToComplete*\" } | ForEach-Object {",
            "        [System.Management.Automation.CompletionResult]::new(",
            "            $_.Name,",
            "            $_.Name,",
            "            'ParameterValue',",
            "            $_.Description",
            "        )",
            "    }",
            "}",
            "",
            "Write-Host \"UnrealMate completion loaded. Type 'unrealmate <Tab>' for suggestions.\" -ForegroundColor Cyan",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    root_commands, groups = _build_completion_surface()
    (ROOT / "scripts" / "_unrealmate").write_text(_render_zsh(root_commands, groups), encoding="utf-8")
    (ROOT / "scripts" / "unrealmate_completion.bash").write_text(
        _render_bash(root_commands, groups), encoding="utf-8"
    )
    (ROOT / "scripts" / "unrealmate_completion.ps1").write_text(
        _render_ps1(root_commands, groups), encoding="utf-8"
    )
    print(f"Updated completion scripts from registry ({len(root_commands)} root commands, {len(groups)} groups).")


if __name__ == "__main__":
    main()
