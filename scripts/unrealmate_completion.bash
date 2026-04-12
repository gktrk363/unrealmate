#!/usr/bin/env bash
# Generated from unrealmate/registry/command_registry.toml
# Do not edit manually; run: python scripts/sync_completion_from_registry.py

_unrealmate_completion() {
    local cur prev base_commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    base_commands="asset build config git performance plugin report analytics doctor version"
    asset_commands="duplicates organize scan"
    build_commands="ci-init docker info"
    config_commands="edit get init set show template validate"
    git_commands="clean init lfs"
    performance_commands="memory profile shaders"
    plugin_commands="disable enable install list remove"
    report_commands="html json notify"

    case "${prev}" in
        unrealmate)
            COMPREPLY=( $(compgen -W "${base_commands}" -- ${cur}) )
            return 0
            ;;
        asset)
            COMPREPLY=( $(compgen -W "${asset_commands}" -- ${cur}) )
            return 0
            ;;
        build)
            COMPREPLY=( $(compgen -W "${build_commands}" -- ${cur}) )
            return 0
            ;;
        config)
            COMPREPLY=( $(compgen -W "${config_commands}" -- ${cur}) )
            return 0
            ;;
        git)
            COMPREPLY=( $(compgen -W "${git_commands}" -- ${cur}) )
            return 0
            ;;
        performance)
            COMPREPLY=( $(compgen -W "${performance_commands}" -- ${cur}) )
            return 0
            ;;
        plugin)
            COMPREPLY=( $(compgen -W "${plugin_commands}" -- ${cur}) )
            return 0
            ;;
        report)
            COMPREPLY=( $(compgen -W "${report_commands}" -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac

    COMPREPLY=( $(compgen -f -- ${cur}) )
    return 0
}

complete -F _unrealmate_completion unrealmate
