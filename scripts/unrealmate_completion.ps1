# Generated from unrealmate/registry/command_registry.toml
# Do not edit manually; run: python scripts/sync_completion_from_registry.py

Register-ArgumentCompleter -Native -CommandName unrealmate -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $baseCommands = @(
        @{ Name = 'asset'; Description = 'Asset management commands' }
        @{ Name = 'build'; Description = 'Build and CI/CD tools' }
        @{ Name = 'config'; Description = 'Configuration management' }
        @{ Name = 'git'; Description = 'Git helper commands' }
        @{ Name = 'performance'; Description = 'Performance analysis commands' }
        @{ Name = 'plugin'; Description = 'Plugin management' }
        @{ Name = 'report'; Description = 'Reporting commands' }
        @{ Name = 'analytics'; Description = 'Show usage analytics and metrics. (local-only)' }
        @{ Name = 'doctor'; Description = 'Run interactive health checks for the project.' }
        @{ Name = 'version'; Description = 'Show system and version information.' }
    )

    $AssetCommands = @(
        @{ Name = 'duplicates'; Description = 'Find and report duplicate assets by name or content hash.' }
        @{ Name = 'organize'; Description = 'Organize assets into proper directory structure based on file types.' }
        @{ Name = 'scan'; Description = 'Scan directory for Unreal Engine assets and provide a detailed report.' }
    )

    $BuildCommands = @(
        @{ Name = 'ci-init'; Description = 'Generate CI/CD pipeline configuration.' }
        @{ Name = 'docker'; Description = 'Generate optimized Dockerfile for Unreal Engine.' }
        @{ Name = 'info'; Description = 'Show build information and recommendations.' }
    )

    $ConfigCommands = @(
        @{ Name = 'edit'; Description = 'Opens .unrealmate.toml in the system default editor.' }
        @{ Name = 'get'; Description = 'Get a configuration value.' }
        @{ Name = 'init'; Description = 'Initialize .unrealmate.toml configuration file.' }
        @{ Name = 'set'; Description = 'Set a configuration value.' }
        @{ Name = 'show'; Description = 'Show current configuration.' }
        @{ Name = 'template'; Description = 'Apply a performance preset template to .unrealmate.toml.' }
        @{ Name = 'validate'; Description = 'Validates .unrealmate.toml structure and values.' }
    )

    $GitCommands = @(
        @{ Name = 'clean'; Description = 'Clean build artifacts, intermediate files, and temporary data.' }
        @{ Name = 'init'; Description = 'Initialize git configuration with optimized settings for Unreal Engine.' }
        @{ Name = 'lfs'; Description = 'Setup Git LFS used for large binary files (assets, maps, etc).' }
    )

    $PerformanceCommands = @(
        @{ Name = 'memory'; Description = 'Audit memory usage and identify optimization opportunities.' }
        @{ Name = 'profile'; Description = 'Analyze performance metrics and detect bottlenecks.' }
        @{ Name = 'shaders'; Description = 'Analyze shader complexity and optimization opportunities.' }
    )

    $PluginCommands = @(
        @{ Name = 'disable'; Description = 'Disable a plugin in .uproject file.' }
        @{ Name = 'enable'; Description = 'Enable a plugin in .uproject file.' }
        @{ Name = 'install'; Description = 'Install a plugin from Git or local directory.' }
        @{ Name = 'list'; Description = 'List all installed plugins.' }
        @{ Name = 'remove'; Description = 'Remove a plugin from project.' }
    )

    $ReportCommands = @(
        @{ Name = 'html'; Description = 'Generate HTML project report with real stats.' }
        @{ Name = 'json'; Description = 'Export project stats as JSON (prints or saves to file).' }
        @{ Name = 'notify'; Description = 'Save a team notification to the project notification log. (local-only)' }
    )

    $elements = $commandAst.CommandElements
    $commands = @()

    if ($elements.Count -ge 2) {
        $subCommand = $elements[1].Extent.Text

        switch ($subCommand) {
            'asset' { $commands = $AssetCommands }
            'build' { $commands = $BuildCommands }
            'config' { $commands = $ConfigCommands }
            'git' { $commands = $GitCommands }
            'performance' { $commands = $PerformanceCommands }
            'plugin' { $commands = $PluginCommands }
            'report' { $commands = $ReportCommands }
            default { $commands = @() }
        }
    }
    else {
        $commands = $baseCommands
    }

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
