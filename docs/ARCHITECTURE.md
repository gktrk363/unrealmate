<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                        UnrealMate - Architecture                             ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Technical architecture overview                                    ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
-->

# 🏗️ UnrealMate Architecture

## Overview
UnrealMate is built on a modular architecture using **Typer** for the CLI interface and **Rich** for the terminal UI. It separates core logic from command implementations to allow for easy extensibility.

## Folder Structure

```
unrealmate/
├── core/           # Core Logic Modules
├── cli.py          # Main Entry Point & Command Definitions
├── templates/      # Project Templates
└── utils/          # Helper Functions
```

## Key Components

### 1. Core Modules
The `core/` directory contains the heavy lifting logic:
- **`plugin_system.py`**: Manages .uproject plugins and dependencies.
- **`performance_profiler.py`**: Handles performance metrics gathering.
- **`ue_plugin_manager.py`**: Manages installed plugins.
- **`team_dashboard.py`**: Aggregates git stats for the team dashboard.
- **`nlp_commands.py`**: Natural Language Processing engine for CLI commands.
- **`bug_detector.py`**: AI-driven static analysis for Blueprint/Code.

### 2. Dependency Injection
`core/di.py` manages dependencies between modules, improving testability and modularity.

### 3. Event System
`core/events.py` implements a pub/sub model, allowing modules to communicate asynchronously without tight coupling.

### 4. Configuration
`core/config.py` handles the `.unrealmate.toml` configuration file, allowing users to customize behavior per project.

## Extensibility
To add a new feature, you typically:
1. Create a new module in `core/`.
2. Register a new command group in `cli.py` using Typer.
3. Wire up the core logic to the CLI command.

---
*Created by [gktrk363](https://github.com/gktrk363)*
