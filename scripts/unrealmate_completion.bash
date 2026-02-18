#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    UnrealMate - Bash Completion Script                       ║
# ║                                                                              ║
# ║  Author: gktrk363                                                            ║
# ║  GitHub: https://github.com/gktrk363/unrealmate                              ║
# ║  Purpose: Auto-completion for unrealmate commands in Bash                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# © 2026 gktrk363 - Crafted with passion for Unreal Engine developers
#
# Installation:
#   Add to ~/.bashrc:
#   source /path/to/unrealmate_completion.bash
#
#   Or copy to /etc/bash_completion.d/unrealmate

_unrealmate_completion() {
    local cur prev opts base_commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Base commands
    base_commands="git asset blueprint bp performance perf config cfg plugin build doctor version"

    # Git subcommands
    git_commands="init lfs clean status"

    # Asset subcommands
    asset_commands="scan organize duplicates validate"

    # Blueprint subcommands
    blueprint_commands="analyze complexity lint"

    # Performance subcommands
    performance_commands="profile memory shader audit"

    # Config subcommands
    config_commands="init show get set"

    # Plugin subcommands
    plugin_commands="list install enable disable"

    # Build subcommands
    build_commands="generate validate"

    case "${prev}" in
        unrealmate)
            COMPREPLY=( $(compgen -W "${base_commands}" -- ${cur}) )
            return 0
            ;;
        git)
            COMPREPLY=( $(compgen -W "${git_commands}" -- ${cur}) )
            return 0
            ;;
        asset)
            COMPREPLY=( $(compgen -W "${asset_commands}" -- ${cur}) )
            return 0
            ;;
        blueprint|bp)
            COMPREPLY=( $(compgen -W "${blueprint_commands}" -- ${cur}) )
            return 0
            ;;
        performance|perf)
            COMPREPLY=( $(compgen -W "${performance_commands}" -- ${cur}) )
            return 0
            ;;
        config|cfg)
            COMPREPLY=( $(compgen -W "${config_commands}" -- ${cur}) )
            return 0
            ;;
        plugin)
            COMPREPLY=( $(compgen -W "${plugin_commands}" -- ${cur}) )
            return 0
            ;;
        build)
            COMPREPLY=( $(compgen -W "${build_commands}" -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac

    # Complete with file/directory names by default
    COMPREPLY=( $(compgen -f -- ${cur}) )
    return 0
}

complete -F _unrealmate_completion unrealmate
