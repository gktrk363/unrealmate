# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    UnrealMate - PowerShell Completion Script                 ║
# ║                                                                              ║
# ║  Author: gktrk363                                                            ║
# ║  GitHub: https://github.com/gktrk363/unrealmate                              ║
# ║  Purpose: Auto-completion for unrealmate commands in PowerShell              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# © 2026 gktrk363 - Crafted with passion for Unreal Engine developers
#
# Installation:
#   Add to your PowerShell profile ($PROFILE):
#   . /path/to/unrealmate_completion.ps1

# Register argument completer for unrealmate
Register-ArgumentCompleter -Native -CommandName unrealmate -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $baseCommands = @(
        @{ Name = 'git'; Description = 'Git helper commands' }
        @{ Name = 'asset'; Description = 'Asset management commands' }
        @{ Name = 'blueprint'; Description = 'Blueprint analysis commands' }
        @{ Name = 'bp'; Description = 'Blueprint analysis (alias)' }
        @{ Name = 'performance'; Description = 'Performance analysis commands' }
        @{ Name = 'perf'; Description = 'Performance analysis (alias)' }
        @{ Name = 'config'; Description = 'Configuration management' }
        @{ Name = 'cfg'; Description = 'Configuration (alias)' }
        @{ Name = 'plugin'; Description = 'Plugin management' }
        @{ Name = 'build'; Description = 'Build and CI/CD tools' }
        @{ Name = 'doctor'; Description = 'Check project health' }
        @{ Name = 'version'; Description = 'Show version information' }
    )

    $gitCommands = @(
        @{ Name = 'init'; Description = 'Initialize Git repository' }
        @{ Name = 'lfs'; Description = 'Setup Git LFS' }
        @{ Name = 'clean'; Description = 'Clean unnecessary files' }
        @{ Name = 'status'; Description = 'Show Git status' }
    )

    $assetCommands = @(
        @{ Name = 'scan'; Description = 'Scan project assets' }
        @{ Name = 'organize'; Description = 'Organize assets by type' }
        @{ Name = 'duplicates'; Description = 'Find duplicate assets' }
        @{ Name = 'validate'; Description = 'Validate asset integrity' }
    )

    $blueprintCommands = @(
        @{ Name = 'analyze'; Description = 'Analyze blueprints' }
        @{ Name = 'complexity'; Description = 'Check blueprint complexity' }
        @{ Name = 'lint'; Description = 'Lint blueprint files' }
    )

    $performanceCommands = @(
        @{ Name = 'profile'; Description = 'Profile project performance' }
        @{ Name = 'memory'; Description = 'Memory usage analysis' }
        @{ Name = 'shader'; Description = 'Shader complexity analysis' }
        @{ Name = 'audit'; Description = 'Full performance audit' }
    )

    $configCommands = @(
        @{ Name = 'init'; Description = 'Initialize configuration' }
        @{ Name = 'show'; Description = 'Show current configuration' }
        @{ Name = 'get'; Description = 'Get configuration value' }
        @{ Name = 'set'; Description = 'Set configuration value' }
    )

    $pluginCommands = @(
        @{ Name = 'list'; Description = 'List installed plugins' }
        @{ Name = 'install'; Description = 'Install a plugin' }
        @{ Name = 'enable'; Description = 'Enable a plugin' }
        @{ Name = 'disable'; Description = 'Disable a plugin' }
    )

    $buildCommands = @(
        @{ Name = 'generate'; Description = 'Generate CI/CD config' }
        @{ Name = 'validate'; Description = 'Validate build config' }
    )

    # Parse current command to determine context
    $elements = $commandAst.CommandElements
    $commands = @()

    if ($elements.Count -ge 2) {
        $subCommand = $elements[1].Extent.Text

        switch ($subCommand) {
            'git' { $commands = $gitCommands }
            'asset' { $commands = $assetCommands }
            'blueprint' { $commands = $blueprintCommands }
            'bp' { $commands = $blueprintCommands }
            'performance' { $commands = $performanceCommands }
            'perf' { $commands = $performanceCommands }
            'config' { $commands = $configCommands }
            'cfg' { $commands = $configCommands }
            'plugin' { $commands = $pluginCommands }
            'build' { $commands = $buildCommands }
            default { $commands = @() }
        }
    }
    else {
        $commands = $baseCommands
    }

    # Filter and return completions
    $commands | Where-Object { $_.Name -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new(
            $_.Name,
            $_.Name,
            'ParameterValue',
            $_.Description
        )
    }
}

Write-Host "UnrealMate completion loaded. Type 'unrealmate <Tab>' for suggestions." -ForegroundColor Cyan
