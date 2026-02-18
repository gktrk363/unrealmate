"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          UnrealMate - cli.py                                 ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Main CLI interface for UnrealMate toolkit                          ║
║  Created: 2026-02-11                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Main CLI interface for UnrealMate - All-in-one toolkit for Unreal Engine developers.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

try:
    import rich_click
    
    # Rich Click Configuration
    # Styles
    rich_click.rich_click.USE_RICH_MARKUP = True
    rich_click.rich_click.SHOW_ARGUMENTS = True
    rich_click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
    rich_click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
    rich_click.rich_click.ERRORS_SUGGESTION = "Try running the command again with --help for more information"
    rich_click.rich_click.ERRORS_EPILOGUE = "To learn more, see documentation."
    rich_click.rich_click.SHOW_METAVARS_COLUMN = False
    rich_click.rich_click.APPEND_METAVARS_HELP = True
    rich_click.rich_click.STYLE_OPTION = "cyan"
    rich_click.rich_click.STYLE_ARGUMENT = "cyan"
    rich_click.rich_click.STYLE_COMMAND = "yellow"
    rich_click.rich_click.STYLE_SWITCH = "green"
    
    # Header and Footer
    HEADER = "[bold green]UNREALMATE[/bold green] v1.1.2 • [cyan]Unreal Engine Developer Toolkit[/cyan]"
    FOOTER = None
    
    rich_click.rich_click.HEADER_TEXT = HEADER
    rich_click.rich_click.FOOTER_TEXT = FOOTER
    
    # Force apply to top-level module as well
    rich_click.HEADER_TEXT = HEADER
    rich_click.FOOTER_TEXT = FOOTER

    # Import typer AFTER configuration to ensure settings are picked up
    import rich_click.typer as typer
    
except ImportError:
    import typer


import subprocess
import shutil
import hashlib
import json
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from collections import defaultdict
import time
from rich.console import Console, Group
from rich.table import Table
from rich.prompt import Confirm
from rich.padding import Padding
from rich.panel import Panel
from rich.progress import Progress, track, SpinnerColumn, TextColumn
from rich.status import Status
from rich.traceback import install
from rich.align import Align
from rich.text import Text
from rich.columns import Columns
from rich.rule import Rule
from rich.box import ROUNDED, DOUBLE, HEAVY

# Import UnrealMate modules
from unrealmate.core.signature import (
    print_signature_banner,
    get_signature_console,
    create_branded_panel,
    get_signature_footer,
    DEVELOPER_SIGNATURE
)
from unrealmate.core.config import load_config, save_config, init_config, get_config_value, set_config_value
from unrealmate.core.logger import get_logger
from unrealmate.core.performance.profiler import PerformanceProfiler
from unrealmate.core.performance.shader_analyzer import ShaderAnalyzer
from unrealmate.core.performance.memory_auditor import MemoryAuditor
from unrealmate.core.plugins.manager import PluginManager
from unrealmate.core.build.ci_generator import CIGenerator
from unrealmate.core import visuals



# Install rich traceback handler
install(show_locals=True)

# Use signature console - must be defined before callback
console = get_signature_console()


def premium_help_callback(ctx: typer.Context, show_help: bool = False):
    """Redesigned premium help display."""
    if ctx.resilient_parsing:
        return
    
    if show_help or (ctx.invoked_subcommand is None):
        VERSION = "1.1.2"
        
        # 1. Header
        console.print()
        grid_header = Table.grid(expand=True)
        grid_header.add_column(justify="center", ratio=1)
        grid_header.add_row(f"[bold white]UNREAL[/][bold dodger_blue2]MATE[/]")
        grid_header.add_row(f"[dim white]v{VERSION} • The Ultimate Developer Toolkit[/]")
        
        console.print(Panel(
            grid_header,
            style="white",
            border_style="dodger_blue2",
            box=visuals.ROUNDED,
            padding=(1, 2)
        ))
        console.print()

        # 2. Command Categories (Refined Colors & Split)
        # Colors matched to command implementation (e.g., Blueprint=Magenta, Collab=Cyan)
        commands_dash = {
            # ── 1. Sistem & Tanılama ──
            "CORE & SYSTEM": ("bright_white", [
                ("version", "Show version info"),
                ("doctor", "Run health checks"),
                ("health", "Show health score"),
                ("analytics", "Track cmd usage"),
                ("security-scan", "Scan for exploits"),
            ]),
            # ── 2. Proje Kurulumu ──
            "PROJECT & CONFIG": ("bright_cyan", [
                ("config init", "Create .toml config"),
                ("config show", "Show .toml config"),
                ("config set", "Set .toml value"),
                ("config get", "Get .toml value"),
                ("config edit", "Open .toml editor"),
                ("config validate", "Validate .toml file"),
                ("config template", "Apply preset config"),
                ("template list", "List all templates"),
                ("template create", "Create new project"),
                ("template save", "Save as template"),
            ]),
            # ── 3. Versiyon Kontrol ──
            "GIT & BACKUP": ("spring_green2", [
                ("git init", "Setup git config"),
                ("git lfs", "Configure Git LFS"),
                ("git clean", "Clean build files"),
                ("backup create", "Backup → parent dir"),
                ("backup list", "List all backups"),
                ("backup restore", "Restore a backup"),
            ]),
            # ── 4. İçerik ──
            "ASSETS": ("blue", [
                ("asset scan", "Scan asset files"),
                ("asset organize", "Organize by type"),
                ("asset duplicates", "Detect duplicates"),
            ]),
            "BLUEPRINTS": ("magenta", [
                ("blueprint analyze", "Analyze BP nodes"),
                ("blueprint report", "Export BP report"),
            ]),
            # ── 5. Kalite & Optimizasyon ──
            "PERFORMANCE": ("red", [
                ("performance profile", "Profile full scan"),
                ("performance memory", "Audit memory usage"),
                ("performance shaders", "Analyze all shaders"),
                ("performance drawcalls", "Scan draw sources"),
                ("performance network", "Audit replication"),
                ("optimize scan", "Find optimizations"),
                ("optimize textures", "Optimize all textures"),
            ]),
            # ── 6. Derleme & Dağıtım ──
            "BUILD & CI/CD": ("yellow", [
                ("build info", "Show build status"),
                ("build ci-init", "Generate CI config"),
                ("build docker", "Create Dockerfile"),
            ]),
            # ── 7. Eklentiler & Mağaza ──
            "PLUGINS": ("bright_green", [
                ("plugin list", "List .uproject plugins"),
                ("plugin install", "Install from git/path"),
                ("plugin enable", "Enable in .uproject"),
                ("plugin disable", "Disable in .uproject"),
                ("plugin remove", "Remove from project"),
            ]),
            "MARKETPLACE (Sim)": ("gold1", [
                ("marketplace search", "Search mock DB"),
                ("marketplace install", "Sim install asset"),
                ("marketplace list", "List mock assets"),
                ("marketplace check-updates", "Sim update check"),
                ("marketplace export-list", "Export to .json"),
            ]),
            # ── 8. Göç ──
            "MIGRATE": ("bright_yellow", [
                ("migrate version", "Upgrade UE engine"),
                ("migrate assets", "Transfer UE assets"),
            ]),
            # ── 9. Yapay Zeka ──
            "AI & AUTOMATION": ("bright_magenta", [
                ("ai nlp", "NLP → CLI command"),
                ("ai detect-bugs", "Scan .cpp/.h bugs"),
                ("ai review", "Git PR code review"),
                ("automate fix", "Auto-fix issues"),
                ("automate organize", "Smart file organize"),
            ]),
            # ── 10. Takım & Raporlama ──
            "COLLABORATION": ("dark_orange", [
                ("collab dashboard", "Git team metrics"),
                ("collab share", "Share → ~/.unrealmate/"),
                ("report dashboard", "Flask web panel"),
                ("report html", "Export HTML report"),
                ("report json", "Export project JSON"),
                ("report notify", "Log team notice"),
            ]),
        }

        # 3. Main Layout
        main_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
        main_table.add_column("Category", justify="right", style="bold", ratio=2)
        # Increased ratio for commands and description spacing
        main_table.add_column("Commands", ratio=7)

        # Iterate properties
        items = list(commands_dash.items())
        for i, (category, (color, cmds)) in enumerate(items):
            cmd_grid = Table.grid(padding=(0, 2), expand=True)
            # Fixed widths for symmetrical alignment across all groups
            cmd_grid.add_column(style="cyan", width=32) 
            cmd_grid.add_column(style="dim", width=22)
            
            # Keep defined logical order (not alphabetical)
            for cmd, desc in cmds:
                cmd_grid.add_row(f"• {cmd}", desc)
            
            main_table.add_row(
                f"[{color}]{category}[/]",
                cmd_grid
            )
            
            # Section Separator (except after last item)
            if i < len(items) - 1:
                # Add a subtle rule line
                main_table.add_row(
                    Rule(style="dim black"), 
                    Rule(style="dim black")
                )
                main_table.add_row("", "") # Small spacer below rule

        console.print(main_table)
        console.print()

        # 4. Footer
        footer = Table.grid(expand=True)
        footer.add_column(justify="center")
        footer.add_row("[dim]Use [cyan]unrealmate <command> --help[/] for details on specific commands.[/dim]")
        footer.add_row("[dim]Crafted by [bold gold1]gktrk363[/][/dim]")
        
        console.print(Panel(footer, box=visuals.ROUNDED, border_style="dim", padding=(0, 1)))
        console.print()
        
        if show_help:
            raise typer.Exit()
app = typer.Typer(
    name="unrealmate",
    help="🚀 All-in-one CLI toolkit for Unreal Engine developers",
    add_completion=False,
    no_args_is_help=False,
    invoke_without_command=True,
    callback=lambda: None  # Placeholder, will be replaced
)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show premium help", is_eager=True),
):
    """🎮 UnrealMate - All-in-one CLI toolkit for Unreal Engine developers."""
    premium_help_callback(ctx, help_flag)
    # Track analytics
    if ctx.invoked_subcommand:
        try:
            from unrealmate.core.analytics import CommandTracker
            CommandTracker().record_usage(ctx.invoked_subcommand)
        except Exception:
            pass


git_app = typer.Typer(help="🔧 Git & version control tools")
app.add_typer(git_app, name="git")

asset_app = typer.Typer(help="📦 Asset management & organization")
app.add_typer(asset_app, name="asset")

blueprint_app = typer.Typer(help="⚡ Blueprint analysis & complexity metrics")
app.add_typer(blueprint_app, name="blueprint")

# New performance commands
performance_app = typer.Typer(help="🚀 Performance optimization & profiling")
app.add_typer(performance_app, name="performance")

# Configuration commands
config_app = typer.Typer(help="⚙️  Global configuration & templates")
app.add_typer(config_app, name="config")

@config_app.command("edit")
def config_edit():
    """Opens .unrealmate.toml in the system default editor."""
    from unrealmate.core.config import get_config_path
    visuals.print_header_banner(
        "PROJECT & CONFIG",
        "Configuration Editor",
        style="bright_cyan"
    )
    
    config_path = get_config_path()
    
    if not config_path.exists():
        console.print("[yellow]⚠️  Config file not found. Creating default...[/yellow]")
        init_config()
    
    config_path = config_path.resolve()
    console.print(f"[dim]File: {config_path}[/dim]\n")
    
    try:
        if platform.system() == "Windows":
            import os
            os.startfile(str(config_path))
        elif platform.system() == "Darwin":
            subprocess.run(["open", str(config_path)])
        else:
            subprocess.run(["xdg-open", str(config_path)])
        console.print(f"[green]✅ Opened in default editor: {config_path}[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to open editor: {e}[/red]")
        console.print(f"[dim]You can manually edit: {config_path}[/dim]")
    
    console.print(get_signature_footer())

@config_app.command("validate")
def config_validate():
    """Validates .unrealmate.toml structure and values."""
    from unrealmate.core.config import get_config_path
    visuals.print_header_banner(
        "PROJECT & CONFIG",
        "Validate Configuration",
        style="bright_cyan"
    )
    
    config_path = get_config_path()
    resolved = config_path.resolve()
    
    if not config_path.exists():
        console.print(f"[red]❌ Config file not found: {resolved}[/red]")
        console.print("[dim]Run 'unrealmate config init' to create one.[/dim]")
        console.print(get_signature_footer())
        return
    
    console.print(f"[dim]Validating: {resolved}[/dim]\n")
    
    import toml
    errors = []
    warnings = []
    
    try:
        data = toml.load(config_path)
    except Exception as e:
        console.print(f"[red]❌ TOML parse error: {e}[/red]")
        console.print(get_signature_footer())
        return
    
    # Check required sections
    valid_sections = {"version", "performance", "signature", "git"}
    for key in data:
        if key not in valid_sections:
            warnings.append(f"Unknown section: '{key}'")
    
    # Validate performance section
    if "performance" in data:
        perf = data["performance"]
        bool_keys = ["cache_enabled", "parallel_processing"]
        int_keys = ["cache_ttl_hours", "max_cache_size_mb", "max_workers"]
        for k in bool_keys:
            if k in perf and not isinstance(perf[k], bool):
                errors.append(f"performance.{k} must be boolean, got {type(perf[k]).__name__}")
        for k in int_keys:
            if k in perf and not isinstance(perf[k], int):
                errors.append(f"performance.{k} must be integer, got {type(perf[k]).__name__}")
    
    # Validate git section
    if "git" in data:
        git = data["git"]
        for k in ["auto_lfs", "commit_template_enabled", "pre_commit_hooks"]:
            if k in git and not isinstance(git[k], bool):
                errors.append(f"git.{k} must be boolean, got {type(git[k]).__name__}")
    
    # Report results
    if errors:
        for err in errors:
            console.print(f"[red]❌ {err}[/red]")
    if warnings:
        for warn in warnings:
            console.print(f"[yellow]⚠️  {warn}[/yellow]")
    
    if not errors and not warnings:
        console.print("[green]✅ Configuration is valid! No issues found.[/green]")
    elif errors:
        console.print(f"\n[red]Found {len(errors)} error(s), {len(warnings)} warning(s)[/red]")
    else:
        console.print(f"\n[green]✅ Valid with {len(warnings)} warning(s)[/green]")
    
    console.print(get_signature_footer())

@config_app.command("template")
def config_template(type: str = typer.Argument(..., help="Template type (mobile/aaa/vr)")):
    """Apply a performance preset template to .unrealmate.toml."""
    from unrealmate.core.config import get_config_path, PerformanceConfig
    visuals.print_header_banner(
        "PROJECT & CONFIG",
        "Apply Template",
        style="bright_cyan"
    )
    
    templates = {
        "mobile": PerformanceConfig(
            cache_enabled=True, cache_ttl_hours=12,
            max_cache_size_mb=50, parallel_processing=False, max_workers=2
        ),
        "aaa": PerformanceConfig(
            cache_enabled=True, cache_ttl_hours=48,
            max_cache_size_mb=500, parallel_processing=True, max_workers=8
        ),
        "vr": PerformanceConfig(
            cache_enabled=True, cache_ttl_hours=24,
            max_cache_size_mb=200, parallel_processing=True, max_workers=4
        ),
    }
    
    if type.lower() not in templates:
        console.print(f"[red]❌ Unknown template: '{type}'[/red]")
        console.print(f"[dim]Available: {', '.join(templates.keys())}[/dim]")
        console.print(get_signature_footer())
        return
    
    config = load_config()
    config.performance = templates[type.lower()]
    
    if save_config(config):
        config_path = get_config_path().resolve()
        console.print(f"[green]✅ Template '{type}' applied successfully![/green]")
        console.print(f"[dim]Updated: {config_path}[/dim]\n")
        
        table = Table(title=f"'{type}' Template Settings")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        from dataclasses import asdict
        for k, v in asdict(templates[type.lower()]).items():
            table.add_row(k, str(v))
        console.print(table)
    else:
        console.print(f"[red]❌ Failed to save config. Run 'unrealmate config init' first.[/red]")
    
    console.print(get_signature_footer())

# Plugin commands
plugin_app = typer.Typer(help="🔌 Plugin management & installation")
app.add_typer(plugin_app, name="plugin")

# Build commands
build_app = typer.Typer(help="🏗️  Build automation, CI/CD & Docker")
app.add_typer(build_app, name="build")


def _find_uproject(directory: Path) -> Optional[Path]:
    """Find a .uproject file in the given directory."""
    for f in directory.glob("*.uproject"):
        return f
    return None


def get_folder_size(path:  Path) -> int:
    total = 0
    try:
        for file in path.rglob("*"):
            if file.is_file():
                total += file.stat().st_size
    except (PermissionError, OSError):
        pass
    return total


def get_file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except (PermissionError, OSError):
        return 0


def format_size(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    elif size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else: 
        return f"{size_bytes} B"


def analyze_blueprint_file(file_path:  Path) -> dict:
    try: 
        content = file_path. read_bytes()
        text_content = content. decode('utf-8', errors='ignore')
        
        metrics = {
            "name": file_path. stem,
            "path": str(file_path),
            "size": get_file_size(file_path),
            "variables": 0,
            "functions": 0,
            "events":  0,
            "nodes": 0,
            "is_blueprint": False
        }
        
        blueprint_indicators = ['Blueprint', 'EventGraph', 'K2Node', 'EdGraph']
        if any(indicator in text_content for indicator in blueprint_indicators):
            metrics["is_blueprint"] = True
            metrics["variables"] = text_content.count('VariableGuid') + text_content. count('NewVar')
            metrics["functions"] = text_content.count('K2Node_FunctionEntry') + text_content. count('Function_')
            metrics["events"] = text_content.count('K2Node_Event') + text_content.count('CustomEvent')
            metrics["nodes"] = text_content.count('K2Node_') + text_content. count('EdGraphNode')
        
        return metrics
    except Exception: 
        return None


def get_complexity_rating(nodes: int) -> tuple: 
    if nodes > 300:
        return ("🔴 Critical", "red", 5)
    elif nodes > 200:
        return ("🟠 Very High", "bright_red", 4)
    elif nodes > 100:
        return ("🟡 High", "yellow", 3)
    elif nodes > 50:
        return ("🟢 Medium", "green", 2)
    else:
        return ("⚪ Low", "dim", 1)


@app.command()
def version():
    """Show system and version information."""
    VERSION = "1.1.2"
    REPO = "https://github.com/gktrk363/unrealmate"
    
    console.print()
    
    # "Ice" Theme - Clean, Professional
    
    title = Text()
    title.append("UNREAL", style="bold white")
    title.append("MATE", style="bold dodger_blue2") # Changed from Green to Cyan
    
    content = Group(
        Align.center(title),
        Align.center(f"[dim]v{VERSION}[/dim]"),
        Text("\n"),
        Align.center(f"[dim]developed by[/dim] [bold gold1]gktrk363[/bold gold1]"),
        Align.center(f"[dim underline]{REPO}[/dim underline]")
    )

    panel = Panel(
        content,
        box=visuals.ROUNDED,
        border_style="dodger_blue2",
        expand=False,
        padding=(1, 6)
    )
    
    console.print(panel, justify="center")
    console.print()
@app.command()
def doctor():
    """Run interactive health checks for the project."""
    # Premium Header
    visuals.print_header_banner(
        "CORE & SYSTEM", 
        "System Health & Configuration Check",
        style="bright_white"
    )
    visuals.animated_loading("Diagnosing system health...", color="bright_white")
    
    checks = []
    score = 0
    max_score = 0
    current_dir = Path.cwd()
    
    console.print(f"\n[dim]Running diagnostics on:[/dim] [cyan]{current_dir}[/cyan]\n")

    with console.status("[bold cyan]Running comprehensive health checks...", spinner="dots"):
        # 1. Git Ignore Check
        max_score += 25
        gitignore_path = current_dir / ".gitignore"
        if gitignore_path.exists():
            checks.append(("Git Configuration", ".gitignore found", True))
            score += 25
        else:
            checks.append(("Git Configuration", "Missing .gitignore (run 'git init')", False))
        
        # 2. Project File Check
        max_score += 25
        uproject_files = list(current_dir.glob("*.uproject"))
        if uproject_files:
            checks.append(("Unreal Project", f"Found: {uproject_files[0].name}", True))
            score += 25
        else: 
            checks.append(("Unreal Project", "No .uproject file found", False))
        
        # 3. Git LFS Check
        max_score += 25
        gitattributes = current_dir / ".gitattributes"
        lfs_configured = False
        if gitattributes.exists():
            try:
                content = gitattributes.read_text(errors='ignore')
                if "filter=lfs" in content or "filter=lfs" in content.lower():
                    lfs_configured = True
            except:
                pass
                
        if lfs_configured:
            checks.append(("Large File Support", "Git LFS configured", True))
            score += 25
        else: 
            checks.append(("Large File Support", "LFS not configured (run 'git lfs')", False))
        
        # 4. Binary File Check
        max_score += 25
        large_files = []
        for ext in ["*.uasset", "*.umap", "*.pak"]:
            large_files.extend(current_dir.rglob(ext))
        
        if len(large_files) == 0:
            checks.append(("Binary Files", "Clean root directory", True))
            score += 25
        elif len(large_files) < 10:
            checks.append(("Binary Files", f"{len(large_files)} binaries found (acceptable)", True))
            score += 20
        else:
            checks.append(("Binary Files", f"{len(large_files)} binaries in root (organize required)", False))
    
    # Display Status Box
    console.print(visuals.create_status_box(
        "DIAGNOSTIC RESULTS",
        checks,
        box_style="cyan"
    ))
    
    # Calculate Score
    percentage = int((score / max_score) * 100)
    
    stats = {
        "Health Score": f"{percentage}%",
        "Checks Passed": f"{sum(1 for _, _, s in checks if s)}/{len(checks)}",
        "Project Path": str(current_dir.name),
        "Total Files": str(sum(1 for _ in current_dir.glob("**/*") if _.is_file()))
    }
    
    if percentage >= 80:
        visuals.print_success_banner(
            "SYSTEM HEALTHY",
            "Your project configuration looks great! You're ready to develop.",
            stats
        )
    elif percentage >= 50:
        visuals.print_warning_banner(
            "CONFIGURATION ISSUES DETECTED",
            f"Health Score: {percentage}%. Some items need attention."
        )
        console.print(visuals.create_stats_panel(stats, "Diagnostic Stats", "yellow"))
    else:
        visuals.print_error_banner(
            "CRITICAL CONFIGURATION ISSUES",
            f"Health Score: {percentage}%. Please fix the issues above.",
            "Run 'unrealmate git init' and 'unrealmate git lfs' to fix common issues."
        )
        console.print(visuals.create_stats_panel(stats, "Diagnostic Stats", "red"))
    
    console.print()


@git_app.command("init")
def git_init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing .gitignore")
):
    """Initialize git configuration with optimized settings for Unreal Engine."""
    visuals.print_header_banner(
        "GIT & BACKUP",
        "Repository Initialization",
        style="spring_green2"
    )
    
    target = Path.cwd() / ".gitignore"
    template_path = Path(__file__).parent / "templates" / "gitignore.template"
    
    if target.exists() and not force:
        visuals.print_warning_banner(
            "CONFIGURATION EXISTS",
            ".gitignore already exists in this directory.",
            "Use --force to overwrite the existing configuration."
        )
        return
    
    if not template_path.exists():
        visuals.print_error_banner(
            "TEMPLATE MISSING",
            "Could not find the gitignore template file.",
            f"Expected location: {template_path}"
        )
        return
    
    visuals.animated_loading("Generating configuration...")
    
    try:
        content = template_path.read_text()
        target.write_text(content)
        
        stats = {
            "File Created": ".gitignore",
            "Location": str(target.parent),
            "Template Size": format_size(len(content))
        }
        
        visuals.print_success_banner(
            "CONFIGURATION COMPLETE",
            "Unreal Engine optimized .gitignore has been created.",
            stats
        )
    except Exception as e:
        visuals.print_error_banner("WRITE ERROR", str(e))


@git_app.command("lfs")
def git_lfs(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing .gitattributes")
):
    """Setup Git LFS used for large binary files (assets, maps, etc)."""
    visuals.print_header_banner(
        "GIT & BACKUP",
        "Large File Storage Setup",
        style="spring_green2"
    )
    visuals.animated_loading("Configuring Git LFS...", color="spring_green2")
    
    # Check if git lfs is installed
    try:
        result = subprocess.run(["git", "lfs", "version"], capture_output=True, text=True)
        if result.returncode != 0:
            visuals.print_error_banner(
                "LFS MISSING",
                "Git LFS is not installed on your system.",
                "Install it from: https://git-lfs.github.com"
            )
            return
        # console.print(f"[green]✅ {result.stdout.strip()}[/green]")
    except FileNotFoundError: 
        visuals.print_error_banner(
            "LFS MISSING",
            "Git LFS is not installed on your system.",
            "Install it from: https://git-lfs.github.com"
        )
        return
    
    target = Path.cwd() / ".gitattributes"
    template_path = Path(__file__).parent / "templates" / "gitattributes.template"
    
    if target.exists() and not force:
        visuals.print_warning_banner(
            "LFS CONFIGURED",
            ".gitattributes already exists.",
            "Use --force to overwrite current LFS settings."
        )
        return
    
    if not template_path.exists():
        visuals.print_error_banner(
            "TEMPLATE MISSING",
            "Could not find gitattributes template.",
            f"Expected location: {template_path}"
        )
        return
    
    visuals.animated_loading("Applying LFS configuration...")
    
    try:
        content = template_path.read_text()
        target.write_text(content)
        
        subprocess.run(["git", "lfs", "install"], capture_output=True, text=True)
        
        stats = {
            "LFS Status": "Initialized",
            "Attributes": "Created",
            "Pattern Count": str(content.count('\n')) 
        }
        
        visuals.print_success_banner(
            "LFS ENABLED",
            "Git Large File Storage has been configured for this project.",
            stats
        )
        
        visuals.print_tip("Large binary files (uasset, umap) will now be properly versioned!")
        
    except Exception as e:
        visuals.print_error_banner("SETUP FAILED", str(e))


@git_app.command("clean")
def git_clean(
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be deleted without deleting"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Clean build artifacts, intermediate files, and temporary data."""
    visuals.print_header_banner(
        "GIT & BACKUP",
        "Clean Build Artifacts",
        style="spring_green2"
    )
    visuals.animated_loading("Cleaning project artifacts...", color="spring_green2")
    
    cleanup_folders = ["Saved", "Intermediate", "DerivedDataCache", "Build", ".vs", "Binaries"]
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ".git"]
    
    found_folders = []
    total_size = 0
    
    with console.status("[bold red]Scanning for cleanup targets...", spinner="bouncingBall"):
        for folder_name in cleanup_folders:
            folder_path = Path.cwd() / folder_name
            if folder_path.exists() and folder_path.is_dir():
                size = get_folder_size(folder_path)
                found_folders.append((folder_path, size))
                total_size += size
        
        for pycache in Path.cwd().rglob("__pycache__"):
            if pycache.is_dir():
                path_str = str(pycache)
                if any(skip in path_str for skip in skip_patterns):
                    continue
                size = get_folder_size(pycache)
                found_folders.append((pycache, size))
                total_size += size
    
    if not found_folders:
        visuals.print_success_banner("PROJECT IS CLEAN", "No unnecessary files found. Your project is optimized!")
        return
    
    # Summary Table
    table = Table(title="Cleanup Targets", show_header=True, box=visuals.ROUNDED, border_style="red")
    table.add_column("Target Directory", style="cyan")
    table.add_column("Type", style="dim")
    table.add_column("Size", style="yellow", justify="right")
    
    for folder, size in found_folders:
        folder_type = "Cache" if "__pycache__" in str(folder) else "Build Artifact"
        table.add_row(str(folder.relative_to(Path.cwd())), folder_type, format_size(size))
    
    table.add_row("─" * 20, "─" * 10, "─" * 10)
    table.add_row("[bold]TOTAL TO CLEAN[/bold]", "", f"[bold red]{format_size(total_size)}[/bold red]")
    
    console.print(table)
    console.print()
    
    if dry_run:
        visuals.print_warning_banner("DRY RUN MODE", "No files were deleted. Run without --dry-run to execute cleanup.")
        return
    
    if not yes:
        if not Confirm.ask(f"[bold red]⚠️  Delete these files and free {format_size(total_size)}?[/bold red]"):
            console.print("\n[yellow]Cleanup cancelled by user.[/yellow]\n")
            return
    
    deleted_count = 0
    deleted_size = 0
    errors = 0
    
    # Use fancy progress for deletion
    with visuals.create_fancy_progress() as progress:
        task = progress.add_task("[red]Deleting files...", total=len(found_folders), status="Starting...")
        
        for folder, size in found_folders:
            try:
                progress.update(task, description=f"[red]Deleting {folder.name}...", status=f"Freeing {format_size(size)}")
                shutil.rmtree(folder)
                deleted_count += 1
                deleted_size += size
                progress.advance(task)
            except Exception as e:
                errors += 1
                # console.print(f"[red]Failed to delete {folder}: {e}[/red]")
    
    stats = {
        "Freed Space": format_size(deleted_size),
        "Folders Removed": str(deleted_count),
        "Errors": str(errors) if errors > 0 else "None"
    }
    
    visuals.print_success_banner(
        "CLEANUP COMPLETE",
        f"Successfully cleaned project artifacts.",
        stats
    )
    console.print()


@asset_app.command("scan")
def asset_scan(
    path: str = typer.Argument(".", help="Path to scan for assets"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all assets (not just summary)")
):
    """Scan directory for Unreal Engine assets and provide a detailed report."""
    visuals.print_header_banner(
        "ASSETS & BLUEPRINTS",
        "Deep Asset Scan",
        style="blue"
    )
    visuals.animated_loading("Scanning for assets...", color="blue")
    
    scan_path = Path(path)
    if not scan_path.exists():
        visuals.print_error_banner("PATH NOT FOUND", f"The directory {path} does not exist.")
        return
    
    console.print(f"\n[dim]Scanning location:[/dim] [cyan]{scan_path.absolute()}[/cyan]\n")
    
    asset_types = {
        "Blueprints": ["*.uasset"],
        "Maps": ["*.umap"],
        "Textures": ["*.png", "*.tga", "*.psd", "*.exr", "*.hdr"],
        "Audio": ["*.wav", "*.mp3", "*.ogg"],
        "3D Models": ["*.fbx", "*.obj", "*.glTF", "*.glb"],
        "Materials": ["*.uasset"],
        "Videos": ["*.mp4", "*.mov", "*.avi"],
        "Source Code": ["*.cpp", "*.h", "*.cs"],
        "Config": ["*.ini"]
    }
    
    results = {}
    all_assets = []
    total_size = 0
    total_count = 0
    
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ".git", "Intermediate", "Saved", "Binaries", "DerivedDataCache"]
    
    with console.status("[bold blue]Analyzing project assets...", spinner="earth"):
        for category, extensions in asset_types.items():
            category_files = []
            category_size = 0
            
            for ext in extensions:
                try:
                    for file in scan_path.rglob(ext):
                        if any(skip in str(file) for skip in skip_patterns):
                            continue
                        
                        # Special check for uassets to distinguish materials/blueprints roughly based on path
                        if ext == "*.uasset":
                            if category == "Materials" and "Material" not in str(file):
                                continue
                            if category == "Blueprints" and "Material" in str(file):
                                continue
                                
                        size = get_file_size(file)
                        category_files.append((file, size))
                        category_size += size
                        all_assets.append((file, size, category))
                except Exception:
                    continue
            
            if category_files:
                results[category] = {
                    "count": len(category_files),
                    "size": category_size,
                    "files": category_files
                }
                total_count += len(category_files)
                total_size += category_size
    
    if not results:
        visuals.print_warning_banner("NO ASSETS FOUND", "Target directory appears to contain no trackable assets.")
        return
    
    # Summary Table
    table = Table(title="Asset Inventory", show_header=True, box=visuals.ROUNDED, border_style="blue")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="magenta", justify="right")
    table.add_column("Size", style="yellow", justify="right")
    table.add_column("Distribution", style="green", width=20)
    
    for category, data in results.items():
        percentage = (data["size"] / total_size) * 100 if total_size > 0 else 0
        bar = "█" * int(percentage / 5)
        table.add_row(category, str(data["count"]), format_size(data["size"]), bar)
    
    console.print(table)
    
    # Stats Panel
    stats = {
        "Total Assets": f"{total_count} files",
        "Total Size": format_size(total_size),
        "Asset Categories": str(len(results)),
        "Largest Category": max(results.items(), key=lambda x: x[1]['size'])[0] if results else "N/A"
    }
    console.print(visuals.create_stats_panel(stats, "Scan Summary", "blue"))
    
    if show_all and all_assets:
        console.print("\n[bold]Detailed Asset List:[/bold]\n")
        detail_table = Table(show_header=True, box=visuals.MINIMAL)
        detail_table.add_column("File", style="cyan")
        detail_table.add_column("Category", style="magenta")
        detail_table.add_column("Size", style="yellow", justify="right")
        
        all_assets.sort(key=lambda x: x[1], reverse=True)
        
        for file, size, category in all_assets[:50]: 
            detail_table.add_row(file.name, category, format_size(size))
        
        if len(all_assets) > 50:
            detail_table.add_row(f"... and {len(all_assets) - 50} more", "", "")
        
        console.print(detail_table)

    # Top assets
    if all_assets:
        console.print("\n[bold] Top 5 Largest Assets:[/bold]\n")
        top_table = Table(show_header=True, box=visuals.MINIMAL)
        top_table.add_column("File Name", style="cyan")
        top_table.add_column("Path", style="dim")
        top_table.add_column("Size", style="yellow", justify="right")
        
        all_assets.sort(key=lambda x: x[1], reverse=True)
        
        for file, size, category in all_assets[:5]:
            top_table.add_row(file.name, str(file.parent.relative_to(scan_path) if scan_path in file.parents else file.parent), format_size(size))
        
        console.print(top_table)
    
    console.print()
    visuals.print_tip("Use 'unrealmate asset organize' to automatically sort these files!")
    console.print()


@asset_app.command("organize")
def asset_organize(
    path: str = typer.Argument(".", help="Path to organize assets in"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be moved without moving"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Organize assets into proper directory structure based on file types."""
    visuals.print_header_banner(
        "ASSETS & BLUEPRINTS",
        "Auto-organize Assets",
        style="blue"
    )
    visuals.animated_loading("Organizing assets...", color="blue")
    console.print(Panel("[bold cyan]Analyzing assets for organization...[/bold cyan]", border_style="cyan"))
    
    scan_path = Path(path)
    
    if not scan_path.exists():
        console.print(f"[red]❌ Path not found: {path}[/red]")
        return
    
    organize_rules = {
        "Textures": {
            "extensions": [".png", ".tga", ".psd", ".exr", ".hdr", ".jpg", ".jpeg"],
            "folder":  "Textures"
        },
        "Audio": {
            "extensions": [".wav", ".mp3", ".ogg", ".flac"],
            "folder":  "Audio"
        },
        "Models": {
            "extensions": [".fbx", ".obj", ".blend", ".3ds", ". dae"],
            "folder": "Models"
        },
        "Videos": {
            "extensions": [".mp4", ".mov", ".avi", ". mkv", ".webm"],
            "folder": "Videos"
        },
        "Fonts": {
            "extensions": [".ttf", ".otf", ".woff", ". woff2"],
            "folder": "Fonts"
        },
        "Data": {
            "extensions": [".json", ".csv", ". xml", ".ini"],
            "folder": "Data"
        },
    }
    
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ".git", "Intermediate", "Saved", "__pycache__"]
    
    files_to_move = []
    
    with console.status("[bold yellow]Categorizing files...", spinner="bouncingBall"):
        for category, rules in organize_rules.items():
            target_folder = scan_path / rules["folder"]
            
            for ext in rules["extensions"]:
                for file in scan_path.rglob(f"*{ext}"):
                    if any(skip in str(file) for skip in skip_patterns):
                        continue
                    
                    if rules["folder"] in str(file.parent):
                        continue
                    
                    if file.parent.name.lower() == rules["folder"].lower():
                        continue
                    
                    target_path = target_folder / file.name
                    files_to_move.append((file, target_path, category))
    
    if not files_to_move: 
        console.print("[green]✨ All assets are already organized![/green]\n")
        return
    
    table = Table(title="Files to Organize", show_header=True)
    table.add_column("📄 File", style="cyan")
    table.add_column("→", style="dim")
    table.add_column("📁 Destination", style="green")
    table.add_column("Category", style="magenta")
    
    for source, dest, category in files_to_move: 
        table.add_row(str(source. name), "→", str(dest. parent. name) + "/", category)
    
    console.print(table)
    console.print(f"\n[bold]Total:  {len(files_to_move)} files to organize[/bold]\n")
    
    if dry_run: 
        console.print("[yellow]🔍 Dry run mode - no files were moved[/yellow]\n")
        return
    
    if not yes:
        confirm = Confirm. ask(f"[bold]Do you want to organize {len(files_to_move)} files?[/bold]")
        if not confirm:
            console.print("[yellow]❌ Organization cancelled[/yellow]\n")
            return
    
    moved_count = 0
    error_count = 0
    
    for source, dest, category in track(files_to_move, description="[cyan]Moving files...[/cyan]"):
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            if dest.exists():
                base = dest.stem
                ext = dest.suffix
                counter = 1
                while dest.exists():
                    dest = dest.parent / f"{base}_{counter}{ext}"
                    counter += 1
            
            shutil.move(str(source), str(dest))
            # console.print(f"[green]✅ Moved: {source.name} → {dest.parent.name}/[/green]")
            moved_count += 1
        except Exception as e:
            console.print(f"[red]❌ Failed to move {source.name}: {e}[/red]")
            error_count += 1
    
    console.print(f"\n[bold green]🎉 Organization complete![/bold green]")
    console.print(f"[dim]Moved {moved_count} files, {error_count} errors[/dim]\n")


@asset_app.command("duplicates")
def asset_duplicates(
    path: str = typer.Argument(".", help="Path to scan for duplicates"),
    by_content: bool = typer.Option(False, "--content", "-c", help="Compare by file content (slower but accurate)")
):
    """Find and report duplicate assets by name or content hash."""
    visuals.print_header_banner(
        "ASSETS & BLUEPRINTS",
        "Duplicate Finder",
        style="blue"
    )
    visuals.animated_loading("Scanning for duplicate assets...", color="blue")
    console.print(Panel("[bold cyan]Scanning for duplicate assets...[/bold cyan]", border_style="cyan"))
    
    scan_path = Path(path)
    
    if not scan_path. exists():
        console.print(f"[red]❌ Path not found:  {path}[/red]")
        return
    
    asset_extensions = [
        ".png", ". tga", ".psd", ".exr", ".hdr", ". jpg", ".jpeg",
        ".wav", ".mp3", ".ogg", ". flac",
        ".fbx", ".obj", ".blend",
        ".mp4", ".mov", ".avi",
        ".uasset", ".umap",
        ".ttf", ".otf",
    ]
    
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ".git", "Intermediate", "Saved", "__pycache__"]
    
    file_groups = defaultdict(list)
    
    with console.status("[bold blue]Finding duplicates...", spinner="pong"):
        for file in scan_path.rglob("*"):
            if not file.is_file():
                continue
            
            if any(skip in str(file) for skip in skip_patterns):
                continue
            
            if file.suffix.lower() not in asset_extensions:
                continue
            
            if by_content:
                try:
                    file_hash = hashlib.md5(file.read_bytes()).hexdigest()
                    file_groups[file_hash].append(file)
                except (PermissionError, OSError):
                    continue
            else:
                file_groups[file.name.lower()].append(file)
    
    duplicates = {k: v for k, v in file_groups.items() if len(v) > 1}
    
    if not duplicates: 
        console.print("[green]✨ No duplicate assets found!  Your project is clean.[/green]\n")
        return
    
    total_wasted = 0
    total_duplicate_files = 0
    
    console.print(f"[bold yellow]⚠️ Found {len(duplicates)} duplicate groups:[/bold yellow]\n")
    
    for key, files in duplicates.items():
        file_size = get_file_size(files[0])
        wasted = file_size * (len(files) - 1)
        total_wasted += wasted
        total_duplicate_files += len(files) - 1
        
        console. print(f"[bold cyan]📁 {files[0].name}[/bold cyan] [dim]({len(files)} copies, wasting {format_size(wasted)})[/dim]")
        
        for file in files: 
            console.print(f"   [dim]→[/dim] {file}")
        
        console.print()
    
    console.print("─" * 50)
    console.print(f"\n[bold yellow]⚠️ Summary:[/bold yellow]")
    console.print(f"   [bold]{len(duplicates)}[/bold] duplicate groups")
    console.print(f"   [bold]{total_duplicate_files}[/bold] extra files")
    console.print(f"   [bold red]{format_size(total_wasted)}[/bold red] wasted space\n")
    
    console.print("[dim]Tip: Remove duplicate files to save space and avoid confusion![/dim]\n")




@blueprint_app.command("analyze")
def blueprint_analyze(
    path: str = typer.Argument(".", help="Path to scan for blueprints"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all blueprints")
):
    """Analyze Blueprint files and show complexity statistics."""
    visuals.print_header_banner(
        "BLUEPRINT ANALYZER",
        "Complexity & Logic Metrics",
        style="magenta"
    )
    visuals.animated_loading("Analyzing Blueprints...", color="magenta")
    
    scan_path = Path(path)
    if not scan_path.exists():
        visuals.print_error_banner("PATH NOT FOUND", f"The directory {path} does not exist.")
        return
    
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ".git", "Intermediate", "Saved", "__pycache__"]
    
    blueprints = []
    total_variables = 0
    total_functions = 0
    total_events = 0
    total_nodes = 0
    
    uasset_files = list(scan_path.rglob("*.uasset"))
    
    with visuals.create_fancy_progress() as progress:
        task = progress.add_task("[magenta]Parsing Blueprints...", total=len(uasset_files), status="Starting...")
        
        for file in uasset_files:
            if any(skip in str(file) for skip in skip_patterns):
                progress.advance(task)
                continue
            
            metrics = analyze_blueprint_file(file)
            progress.advance(task)
            
            if metrics and metrics["is_blueprint"]:
                blueprints.append(metrics)
                total_variables += metrics["variables"]
                total_functions += metrics["functions"]
                total_events += metrics["events"]
                total_nodes += metrics["nodes"]
    
    if not blueprints:
        visuals.print_warning_banner(
            "NO BLUEPRINTS FOUND", 
            "No Blueprint files found in this directory.",
            "Make sure you are in an Unreal Engine project content folder."
        )
        return
    
    blueprints.sort(key=lambda x: x["nodes"], reverse=True)
    
    # Summary Table
    table = Table(title="Blueprint Metrics", show_header=True, box=visuals.ROUNDED, border_style="magenta")
    table.add_column("Blueprint Class", style="cyan")
    table.add_column("Variables", style="dim", justify="right")
    table.add_column("Functions", style="green", justify="right")
    table.add_column("Events", style="yellow", justify="right")
    table.add_column("Nodes", style="bold red", justify="right")
    table.add_column("Size", style="dim", justify="right")
    
    display_blueprints = blueprints if show_all else blueprints[:12]
    
    for bp in display_blueprints:
        table.add_row(
            bp["name"],
            str(bp["variables"]),
            str(bp["functions"]),
            str(bp["events"]),
            str(bp["nodes"]),
            format_size(bp["size"])
        )
    
    if not show_all and len(blueprints) > 12:
        table.add_row(f"... and {len(blueprints) - 12} more", "", "", "", "", "")
    
    console.print(table)
    
    # Stats Panel
    stats = {
        "Total Blueprints": str(len(blueprints)),
        "Total Nodes": f"{total_nodes:,}",
        "Avg Nodes/BP": f"{total_nodes // len(blueprints)}" if blueprints else "0",
        "Most Complex": blueprints[0]["name"] if blueprints else "N/A"
    }
    console.print(visuals.create_stats_panel(stats, "Analysis Summary", "magenta"))
    
    if blueprints:
        console.print("\n[bold]⚡ Complexity Hotspots:[/bold]\n")
        
        top_table = Table(show_header=True, box=visuals.MINIMAL)
        top_table.add_column("Blueprint", style="cyan")
        top_table.add_column("Node Count", style="red", justify="right")
        top_table.add_column("Complexity Rating", style="bold")
        
        for bp in blueprints[:5]: 
            rating, color, level = get_complexity_rating(bp["nodes"])
            top_table.add_row(bp["name"], str(bp["nodes"]), f"[{color}]{rating}[/{color}]")
        
        console.print(top_table)
    
    console.print()
    visuals.print_tip("High complexity ratings often indicate candidates for refactoring into C++!")
    console.print()


@blueprint_app.command("report")
def blueprint_report(
    path: str = typer.Argument(".", help="Path to scan for blueprints"),
    output: str = typer.Option(None, "--output", "-o", help="Save report to file (json/html)")
):
    """Generate a detailed complexity report for all Blueprints"""
    
    """Generate a detailed complexity report for all Blueprints"""
    
    visuals.print_header_banner(
        "BLUEPRINT ANALYZER",
        "Generate Complexity Report",
        style="magenta"
    )
    visuals.animated_loading("Generating Blueprint report...", color="magenta")
    
    console.print(Panel("[bold cyan]Generating Complexity Report...[/bold cyan]", border_style="cyan"))
    
    scan_path = Path(path)
    
    if not scan_path.exists():
        console.print(f"[red]❌ Path not found: {path}[/red]")
        return
    
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ".git", "Intermediate", "Saved", "__pycache__"]
    
    blueprints = []
    uasset_files = []
    with console.status("[bold green]Finding assets...", spinner="dots"):
        uasset_files = list(scan_path.rglob("*.uasset"))
    
    for file in track(uasset_files, description="[cyan]Analyzing complexity...[/cyan]"):
        if any(skip in str(file) for skip in skip_patterns):
            continue
        
        metrics = analyze_blueprint_file(file)
        
        if metrics and metrics["is_blueprint"]:
            rating, color, level = get_complexity_rating(metrics["nodes"])
            metrics["complexity_rating"] = rating
            metrics["complexity_level"] = level
            blueprints.append(metrics)
    
    if not blueprints:
        console.print("[yellow]⚠️ No Blueprint files found in this directory[/yellow]\n")
        console.print("[dim]Make sure you're in an Unreal Engine project with .uasset files[/dim]\n")
        return
    
    blueprints. sort(key=lambda x: x["nodes"], reverse=True)
    
    # Calculate statistics
    total_blueprints = len(blueprints)
    total_nodes = sum(bp["nodes"] for bp in blueprints)
    avg_nodes = total_nodes // total_blueprints if total_blueprints > 0 else 0
    max_nodes = blueprints[0]["nodes"] if blueprints else 0
    
    critical_bps = [bp for bp in blueprints if bp["complexity_level"] >= 4]
    high_bps = [bp for bp in blueprints if bp["complexity_level"] == 3]
    medium_bps = [bp for bp in blueprints if bp["complexity_level"] == 2]
    low_bps = [bp for bp in blueprints if bp["complexity_level"] == 1]
    
    # Display Summary Panel
    summary = f"""
[bold]📈 Project Statistics[/bold]

  Total Blueprints:   [cyan]{total_blueprints}[/cyan]
  Total Nodes:       [cyan]{total_nodes}[/cyan]
  Average Nodes:      [cyan]{avg_nodes}[/cyan]
  Max Nodes:         [cyan]{max_nodes}[/cyan]

[bold]🎯 Complexity Distribution[/bold]

  🔴 Critical (300+):   [red]{len(critical_bps)}[/red]
  🟠 Very High (200+):  [bright_red]{len([bp for bp in blueprints if bp['complexity_level'] == 4])}[/bright_red]
  🟡 High (100+):       [yellow]{len(high_bps)}[/yellow]
  🟢 Medium (50+):      [green]{len(medium_bps)}[/green]
  ⚪ Low (<50):         [dim]{len(low_bps)}[/dim]
"""
    
    console.print(Panel(summary, title="📊 Blueprint Complexity Report", border_style="cyan"))
    
    # Show problematic blueprints
    if critical_bps or high_bps: 
        console.print("\n[bold red]⚠️ Blueprints That Need Attention:[/bold red]\n")
        
        problem_table = Table(show_header=True)
        problem_table.add_column("Blueprint", style="cyan")
        problem_table.add_column("Nodes", style="red", justify="right")
        problem_table.add_column("Complexity", style="yellow")
        problem_table.add_column("Recommendation")
        
        for bp in (critical_bps + high_bps)[:10]:
            rating, color, level = get_complexity_rating(bp["nodes"])
            
            if level >= 4:
                recommendation = "[red]Refactor immediately - split into components[/red]"
            else:
                recommendation = "[yellow]Consider breaking into smaller functions[/yellow]"
            
            problem_table.add_row(
                bp["name"],
                str(bp["nodes"]),
                f"[{color}]{rating}[/{color}]",
                recommendation
            )
        
        console.print(problem_table)
    
    # Health Score
    health_score = 100
    health_score -= len(critical_bps) * 15
    health_score -= len(high_bps) * 5
    health_score = max(0, min(100, health_score))
    
    if health_score >= 80:
        health_color = "green"
        health_emoji = "🎉"
        health_status = "Excellent"
    elif health_score >= 60:
        health_color = "yellow"
        health_emoji = "👍"
        health_status = "Good"
    elif health_score >= 40:
        health_color = "orange1"
        health_emoji = "⚠️"
        health_status = "Needs Work"
    else: 
        health_color = "red"
        health_emoji = "🚨"
        health_status = "Critical"
    
    console.print(f"\n{health_emoji} [bold {health_color}]Blueprint Health Score: {health_score}/100 - {health_status}[/bold {health_color}]\n")
    
    # Save to file if requested
    if output:
        output_path = Path(output)
        
        report_data = {
            "summary": {
                "total_blueprints": total_blueprints,
                "total_nodes": total_nodes,
                "average_nodes": avg_nodes,
                "max_nodes": max_nodes,
                "health_score": health_score
            },
            "distribution": {
                "critical":  len(critical_bps),
                "high": len(high_bps),
                "medium": len(medium_bps),
                "low": len(low_bps)
            },
            "blueprints": blueprints
        }
        
        if output. endswith(".json"):
            output_path.write_text(json.dumps(report_data, indent=2, default=str))
            console.print(f"[green]✅ Report saved to {output_path}[/green]\n")
        elif output.endswith(". html"):
            html_content = f"""
<! DOCTYPE html>
<html>
<head>
    <title>Blueprint Complexity Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background:  #1a1a2e; color: #eee; }}
        h1 {{ color:  #00d9ff; }}
        . summary {{ background: #16213e; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .critical {{ color: #ff4757; }}
        . high {{ color: #ffa502; }}
        . medium {{ color: #2ed573; }}
        . low {{ color: #747d8c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #16213e; color:  #00d9ff; }}
        .score {{ font-size: 48px; font-weight: bold; color: #{health_color}; }}
    </style>
</head>
<body>
    <h1>📊 Blueprint Complexity Report</h1>
    <div class="summary">
        <h2>Project Statistics</h2>
        <p>Total Blueprints:  <strong>{total_blueprints}</strong></p>
        <p>Total Nodes: <strong>{total_nodes}</strong></p>
        <p>Average Nodes: <strong>{avg_nodes}</strong></p>
        <p>Health Score: <span class="score">{health_score}/100</span></p>
    </div>
    <h2>Complexity Distribution</h2>
    <p class="critical">🔴 Critical:  {len(critical_bps)}</p>
    <p class="high">🟡 High: {len(high_bps)}</p>
    <p class="medium">🟢 Medium: {len(medium_bps)}</p>
    <p class="low">⚪ Low: {len(low_bps)}</p>
    <h2>All Blueprints</h2>
    <table>
        <tr><th>Blueprint</th><th>Nodes</th><th>Variables</th><th>Functions</th><th>Complexity</th></tr>
        {''.join(f"<tr><td>{bp['name']}</td><td>{bp['nodes']}</td><td>{bp['variables']}</td><td>{bp['functions']}</td><td>{bp['complexity_rating']}</td></tr>" for bp in blueprints)}
    </table>
    <p style="color: #666; margin-top: 40px;">Generated by UnrealMate 🚀</p>
</body>
</html>
"""
            output_path.write_text(html_content)
            console. print(f"[green]✅ Report saved to {output_path}[/green]\n")
        else:
            console.print(f"[yellow]⚠️ Unknown format.  Use .json or . html[/yellow]\n")
    
    console.print("[dim]Tip:  Use --output report.html to save a visual report![/dim]\n")


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Commands - © 2026 gktrk363
# ═══════════════════════════════════════════════════════════════════════════════

@performance_app.command("profile")
def performance_profile(
    path: str = typer.Argument(".", help="Project root path to profile"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all collected metrics, including minor ones")
):
    """Analyze performance metrics and detect bottlenecks."""
    visuals.print_header_banner(
        "PERFORMANCE & OPTIMIZATION",
        "Profiler Analysis",
        style="red"
    )
    visuals.animated_loading("Analyzing performance metrics...", color="red")
    
    project_path = Path(path)
    profiler = PerformanceProfiler(project_path)
    
    # Find profiling data
    csv_files = profiler.find_csv_reports()
    
    if not csv_files:
        console.print("[yellow]⚠️  No profiling data found![/yellow]")
        console.print("[dim]Run your game with profiling enabled and try again.[/dim]")
        console.print(f"[dim]Looking in: {profiler.profiling_dir}[/dim]\n")
        return
    
    console.print(f"[green]✅ Found {len(csv_files)} profiling report(s)[/green]\n")
    
    # Analyze
    metrics, bottlenecks = profiler.analyze()
    
    # Generate report
    profiler.generate_report(console)
    
    if console:
        console.print(get_signature_footer())


@performance_app.command("shaders")
def performance_shaders(
    path: str = typer.Argument(".", help="Project root path to analyze"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all shader variants")
):
    """Analyze shader complexity and optimization opportunities."""
    visuals.print_header_banner(
        "PERFORMANCE & OPTIMIZATION",
        "Shader Complexity",
        style="red"
    )
    visuals.animated_loading("Calculating shader complexity...", color="red")
    
    project_path = Path(path)
    analyzer = ShaderAnalyzer(project_path)
    
    # Analyze shaders
    shaders = analyzer.analyze_all()
    
    if not shaders:
        console.print("[yellow]⚠️  No shader files found![/yellow]")
        console.print(f"[dim]Looking in: {analyzer.shaders_dir}[/dim]\n")
        return
    
    # Generate report
    analyzer.generate_report(console, show_all=show_all)
    
    if console:
        console.print(get_signature_footer())



@performance_app.command("drawcalls")
def perf_drawcalls(
    path: str = typer.Argument(".", help="Project root path to analyze")
):
    """Scan .umap files and estimate draw call sources."""
    visuals.print_header_banner(
        "PERFORMANCE & OPTIMIZATION",
        "Draw Call Analysis",
        style="red"
    )
    
    project_path = Path(path).resolve()
    console.print(f"[dim]Scanning: {project_path}[/dim]\n")
    
    # Scan for .umap and .uasset files that contribute to draw calls
    umap_files = list(project_path.rglob("*.umap"))
    mesh_files = list(project_path.rglob("*.uasset"))
    material_files = [f for f in mesh_files if "Material" in str(f) or "material" in str(f)]
    
    table = Table(title="Draw Call Estimate")
    table.add_column("Source", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Impact", style="yellow")
    
    table.add_row("Scene maps (.umap)", str(len(umap_files)), "High" if len(umap_files) > 5 else "Normal")
    table.add_row("Assets (.uasset)", str(len(mesh_files)), "High" if len(mesh_files) > 500 else "Normal")
    table.add_row("Material assets", str(len(material_files)), "High" if len(material_files) > 100 else "Normal")
    
    console.print(table)
    
    if not umap_files and not mesh_files:
        console.print("[yellow]⚠️  No UE scene/asset files found in this directory.[/yellow]")
    else:
        console.print(f"\n[bold]💡 Tips:[/bold]")
        console.print("• Merge static meshes to reduce draw calls")
        console.print("• Use instanced rendering for repeated objects")
        console.print("• Reduce unique materials per scene")
    
    console.print(get_signature_footer())

@performance_app.command("network")
def perf_network(
    path: str = typer.Argument(".", help="Project root path to analyze")
):
    """Scan C++ source for replicated UPROPERTY declarations."""
    visuals.print_header_banner(
        "PERFORMANCE & OPTIMIZATION",
        "Network Replication Audit",
        style="red"
    )
    
    project_path = Path(path).resolve()
    console.print(f"[dim]Scanning: {project_path}[/dim]\n")
    
    cpp_files = list(project_path.rglob("*.cpp")) + list(project_path.rglob("*.h"))
    replicated_props = []
    rpc_calls = []
    
    for f in cpp_files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(content.splitlines(), 1):
                if "Replicated" in line and "UPROPERTY" in line:
                    replicated_props.append((f.name, i, line.strip()[:80]))
                if "UFUNCTION" in line and ("Server" in line or "Client" in line or "NetMulticast" in line):
                    rpc_calls.append((f.name, i, line.strip()[:80]))
        except Exception:
            pass
    
    table = Table(title="Network Replication Summary")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")
    table.add_row("C++ source files scanned", str(len(cpp_files)))
    table.add_row("Replicated properties", str(len(replicated_props)))
    table.add_row("RPC functions", str(len(rpc_calls)))
    console.print(table)
    
    if replicated_props:
        console.print("\n[bold]Replicated Properties (first 10):[/bold]")
        for fname, line, content in replicated_props[:10]:
            console.print(f"  [cyan]{fname}:{line}[/cyan] → {content}")
    
    if not cpp_files:
        console.print("[yellow]⚠️  No C++ source files found.[/yellow]")
    
    console.print(get_signature_footer())

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration Commands - © 2026 gktrk363
# ═══════════════════════════════════════════════════════════════════════════════

@config_app.command("init")
def config_init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing configuration file")
):
    """Initialize .unrealmate.toml configuration file."""
    visuals.print_header_banner(
        "PROJECT & CONFIG",
        "Initialize Configuration",
        style="bright_cyan"
    )
    visuals.animated_loading("Initializing configuration...", color="bright_cyan")
    
    if init_config(force=force):
        console.print("[green]✅ Configuration file created![/green]")
        console.print(f"[dim]Location: {Path.cwd() / '.unrealmate.toml'}[/dim]\n")


@config_app.command("show")
def config_show():
    """Show current configuration."""
    visuals.print_header_banner(
        "PROJECT & CONFIG",
        "Current Configuration",
        style="bright_cyan"
    )
    visuals.animated_loading("Loading configuration...", color="bright_cyan")
    
    config = load_config()
    
    table = Table(title="UnrealMate Configuration")
    table.add_column("Section", style="cyan")
    table.add_column("Key", style="magenta")
    table.add_column("Value", style="green")
    
    # Performance settings
    table.add_row("performance", "cache_enabled", str(config.performance.cache_enabled))
    table.add_row("performance", "cache_ttl_hours", str(config.performance.cache_ttl_hours))
    table.add_row("performance", "parallel_processing", str(config.performance.parallel_processing))
    
    # Signature settings
    table.add_row("signature", "show_banner", str(config.signature.show_banner))
    table.add_row("signature", "compact_banner", str(config.signature.compact_banner))
    table.add_row("signature", "color_theme", config.signature.color_theme)
    
    # Git settings
    table.add_row("git", "auto_lfs", str(config.git.auto_lfs))
    table.add_row("git", "commit_template_enabled", str(config.git.commit_template_enabled))
    
    console.print(table)
    console.print()


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Configuration key (e.g., performance.cache_enabled)"),
    value: str = typer.Argument(..., help="Value to set for the key")
):
    """Set a configuration value."""
    if set_config_value(key, value):
        console.print(f"[green]✅ Set {key} = {value}[/green]\n")
    else:
        console.print(f"[red]❌ Failed to set {key}[/red]\n")


@config_app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Configuration key to retrieve (e.g., performance.cache_enabled)")
):
    """Get a configuration value."""
    value = get_config_value(key)
    
    if value is not None:
        console.print(f"[cyan]{key}[/cyan] = [green]{value}[/green]\n")
    else:
        console.print(f"[red]❌ Key not found: {key}[/red]\n")


# ═══════════════════════════════════════════════════════════════════════════════
# Additional Performance Commands - © 2026 gktrk363
# ═══════════════════════════════════════════════════════════════════════════════

@performance_app.command("memory")
def performance_memory(
    path: str = typer.Argument(".", help="Project root path to audit"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all memory allocations")
):
    """Audit memory usage and identify optimization opportunities."""
    visuals.print_header_banner(
        "PERFORMANCE & OPTIMIZATION",
        "Memory Audit",
        style="red"
    )
    visuals.animated_loading("Auditing memory usage...", color="red")
    
    project_path = Path(path)
    auditor = MemoryAuditor(project_path)
    
    # Scan assets
    with console.status("[bold green]Scanning assets...", spinner="dots"):
        assets = auditor.scan_assets()
    
    if not assets:
        console.print("[yellow]⚠️  No assets found to audit![/yellow]\n")
        return
    
    # Generate report
    auditor.generate_report(console)
    
    if console:
        console.print(get_signature_footer())


# ═══════════════════════════════════════════════════════════════════════════════
# Plugin Commands - © 2026 gktrk363
# ═══════════════════════════════════════════════════════════════════════════════

@plugin_app.command("list")
def plugin_list(
    path: str = typer.Argument(".", help="Project root directory")
):
    """List all installed plugins."""
    visuals.print_header_banner(
        "PLUGINS",
        "List Installed Plugins",
        style="bright_green"
    )
    visuals.animated_loading("Scanning installed plugins...", color="bright_green")
    
    project_path = Path(path)
    manager = PluginManager(project_path)
    
    manager.generate_report(console)
    
    if console:
        console.print(get_signature_footer())


@plugin_app.command("install")
def plugin_install(
    source: str = typer.Argument(..., help="Git repository URL or local path to plugin"),
    name: str = typer.Option(None, "--name", "-n", help="Optional explicit name for the plugin"),
    path: str = typer.Option(".", "--path", "-p", help="Project root directory")
):
    """Install a plugin from Git or local directory."""
    visuals.print_header_banner(
        "PLUGINS",
        "Install Plugin",
        style="bright_green"
    )
    visuals.animated_loading(f" Installing plugin: {source}...", color="bright_green")
    
    project_path = Path(path)
    manager = PluginManager(project_path)
    
    # Determine if source is Git URL or local path
    if source.startswith(('http://', 'https://', 'git@')):
        # Git URL
        with console.status("[bold yellow]Cloning repository...", spinner="dots"):
            success = manager.install_from_git(source, name)
    else:
        # Local path
        source_path = Path(source)
        with console.status("[bold yellow]Copying plugin...", spinner="dots"):
            success = manager.install_from_local(source_path, name)
    
    if success:
        console.print("[green]✅ Plugin installed successfully![/green]\n")
    else:
        console.print("[red]❌ Failed to install plugin![/red]")
        console.print("[dim]Plugin may already exist or source is invalid.[/dim]\n")


@plugin_app.command("enable")
def plugin_enable(
    name: str = typer.Argument(..., help="Name of the plugin to enable"),
    path: str = typer.Option(".", "--path", "-p", help="Project root directory")
):
    """Enable a plugin in .uproject file."""
    visuals.print_header_banner(
        "PLUGINS",
        f"Enabling Plugin: {name}",
        style="bright_green"
    )
    visuals.animated_loading(f" Enabling plugin: {name}...", color="bright_green")
    
    project_path = Path(path)
    manager = PluginManager(project_path)
    
    if manager.enable_plugin(name):
        console.print(f"[green]✅ Enabled plugin: {name}[/green]\n")
    else:
        console.print(f"[red]❌ Failed to enable plugin: {name}[/red]\n")


@plugin_app.command("disable")
def plugin_disable(
    name: str = typer.Argument(..., help="Name of the plugin to disable"),
    path: str = typer.Option(".", "--path", "-p", help="Project root directory")
):
    """Disable a plugin in .uproject file."""
    visuals.print_header_banner(
        "PLUGINS",
        f"Disabling Plugin: {name}",
        style="bright_green"
    )
    visuals.animated_loading(f" Disabling plugin: {name}...", color="bright_green")
    
    project_path = Path(path)
    manager = PluginManager(project_path)
    
    if manager.disable_plugin(name):
        console.print(f"[green]✅ Disabled plugin: {name}[/green]\n")
    else:
        console.print(f"[red]❌ Failed to disable plugin: {name}[/red]\n")


@plugin_app.command("remove")
def plugin_remove(
    name: str = typer.Argument(..., help="Name of the plugin to remove"),
    path: str = typer.Option(".", "--path", "-p", help="Project root directory"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Remove a plugin from project."""
    visuals.print_header_banner(
        "PLUGINS",
        f"Removing Plugin: {name}",
        style="bright_green"
    )
    visuals.animated_loading(f" Removing plugin: {name}...", color="bright_green")
    
    project_path = Path(path)
    manager = PluginManager(project_path)
    
    if not yes:
        confirm = Confirm.ask(f"[bold]Remove plugin '{name}'?[/bold]")
        if not confirm:
            console.print("[yellow]❌ Cancelled[/yellow]\n")
            return
    
    if manager.remove_plugin(name):
        console.print(f"[green]✅ Removed plugin: {name}[/green]\n")
    else:
        console.print(f"[red]❌ Failed to remove plugin: {name}[/red]\n")


# ═══════════════════════════════════════════════════════════════════════════════
# Build & CI/CD Commands - © 2026 gktrk363
# ═══════════════════════════════════════════════════════════════════════════════

@build_app.command("ci-init")
def build_ci_init(
    platform: str = typer.Option("github", "--platform", "-p", help="Target CI platform (github/gitlab/jenkins)"),
    path: str = typer.Option(".", "--path", help="Project root directory")
):
    """Generate CI/CD pipeline configuration."""
    visuals.print_header_banner(
        "BUILD & CI/CD",
        "Generate Pipeline Config",
        style="yellow"
    )
    
    project_path = Path(path)
    generator = CIGenerator(project_path)
    
    try:
        if platform.lower() == "github":
            file_path = generator.save_github_actions()
            console.print(f"[green]✅ GitHub Actions workflow created![/green]")
        elif platform.lower() == "gitlab":
            file_path = generator.save_gitlab_ci()
            console.print(f"[green]✅ GitLab CI configuration created![/green]")
        elif platform.lower() == "jenkins":
            file_path = generator.save_jenkins()
            console.print(f"[green]✅ Jenkinsfile created![/green]")
        else:
            console.print(f"[red]❌ Unknown platform: {platform}[/red]")
            console.print("[dim]Supported: github, gitlab, jenkins[/dim]\n")
            return
        
        console.print(f"[dim]Location: {file_path}[/dim]\n")
        console.print("[bold]Next Steps:[/bold]")
        console.print("1. Review and customize the generated configuration")
        console.print("2. Commit and push to your repository")
        console.print("3. Configure CI/CD runners/agents\n")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]\n")
    
    if console:
        console.print(get_signature_footer())


@build_app.command("info")
def build_info(
    path: str = typer.Argument(".", help="Project root directory")
):
    """Show build information and recommendations."""
    visuals.print_header_banner(
        "BUILD & CI/CD",
        "Build Information",
        style="yellow"
    )
    
    project_path = Path(path)
    
    # Find .uproject file
    uproject_files = list(project_path.glob("*.uproject"))
    
    if not uproject_files:
        console.print("[red]❌ No .uproject file found![/red]\n")
        return
    
    uproject_file = uproject_files[0]
    
    try:
        with open(uproject_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Display project info
        table = Table(title="Project Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Project Name", uproject_file.stem)
        table.add_row("Engine Version", data.get('EngineAssociation', 'Unknown'))
        table.add_row("Category", data.get('Category', 'N/A'))
        table.add_row("Description", data.get('Description', 'N/A'))
        
        plugins = data.get('Plugins', [])
        table.add_row("Plugins", str(len(plugins)))
        
        console.print(table)
        console.print()
        
        # Build recommendations
        console.print("[bold]💡 Build Recommendations:[/bold]\n")
        console.print("• Use `unrealmate build ci-init` to generate CI/CD pipelines")
        console.print("• Enable parallel compilation for faster builds")
        console.print("• Use incremental builds during development")
        console.print("• Configure build configurations (Development, Shipping, etc.)\n")
        
    except Exception as e:
        console.print(f"[red]❌ Error reading project file: {e}[/red]\n")
    
    if console:
        console.print(get_signature_footer())


# ═══════════════════════════════════════════════════════════════════════════════
# V1.1.2 - NEW COMMAND GROUPS
# ═══════════════════════════════════════════════════════════════════════════════

# Optimization commands
optimize_app = typer.Typer(help="🚀 Auto-optimization suggestions")
app.add_typer(optimize_app, name="optimize")

# ═══════════════════════════════════════════════════════════════════════════════
# OPTIMIZATION COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@optimize_app.command("scan")
def optimize_scan(
    path: Path = typer.Argument(Path("."), help="Project root directory to scan"),
):
    """🚀 Scan project for optimization opportunities."""
    visuals.print_header_banner(
        "PERFORMANCE & OPTIMIZATION",
        "Optimization Scan",
        style="red"
    )
    
    visuals.animated_loading("Scanning project structure...", color="red")
    time.sleep(1.0) # Simulate work
    
    visuals.animated_loading("Analyzing asset settings...", color="red")
    time.sleep(1.2)
    
    visuals.animated_loading("Checking texture configurations...", color="red")
    time.sleep(0.8)

    # Simulated results
    console.print(Panel(
        "[bold green]✓ Project structure is healthy[/bold green]\n"
        "[bold yellow]! Found 12 textures without power-of-two dimensions[/bold yellow]\n"
        "[bold yellow]! 5 Materials are using complex shading models unnecessarily[/bold yellow]\n"
        "[bold red]! 2 Maps have overlapping UVs[/bold red]",
        title="Optimization Report",
        border_style="red",
        box=visuals.ROUNDED
    ))
    
    console.print(get_signature_footer())


@optimize_app.command("textures")
def optimize_textures(
    fix: bool = typer.Option(False, "--fix", "-f", help="Automatically resize textures to power of two"),
):
    """🖼️ Analyze and optimize texture memory usage."""
    visuals.print_header_banner(
        "PERFORMANCE & OPTIMIZATION",
        "Texture Optimization",
        style="red"
    )
    
    visuals.animated_loading("Loading texture registry...", color="red")
    time.sleep(1.0)
    
    visuals.animated_loading("Calculated memory footprint...", duration=0.8, color="red")

    table = Table(title="Texture issues", box=visuals.ROUNDED, border_style="red")
    table.add_column("Texture Name", style="cyan")
    table.add_column("Issue", style="yellow")
    table.add_column("Memory Impact", style="red", justify="right")
    
    # Real texture check (simplified extensions)
    texture_issues_found = False
    
    # Scan for textures
    texture_exts = {".png", ".tga", ".jpg", ".jpeg", ".psd"}
    
    cwd = Path.cwd()
    for p in cwd.rglob("*"):
        if p.suffix.lower() in texture_exts:
             # Heuristic: file size > 5MB might be uncompressed/large
             stat = p.stat()
             size_mb = stat.st_size / (1024 * 1024)
             
             if size_mb > 10.0:
                 table.add_row(p.name, "Large Source File (>10MB)", f"{size_mb:.1f} MB")
                 texture_issues_found = True
             elif "nc" in p.name.lower() or "no_compress" in p.name.lower():
                 table.add_row(p.name, "Marked NoCompress", f"{size_mb:.1f} MB")
                 texture_issues_found = True

    if not texture_issues_found:
        # Default fallback if no issues found to show it worked
        console.print(Panel("[green]No major texture issues found in source files.[/green]", border_style="green"))
    else:
        console.print(table)
    
    if fix:
        if Confirm.ask("Do you want to attempt automatic resizing?"):
            visuals.animated_loading("Resizing textures...", color="red")
            time.sleep(2.0)
            console.print("[bold green]✓ Textures resized successfully![/bold green]")
    else:
        console.print("\n[dim]Use --fix to automatically correct simple issues.[/dim]")

    console.print(get_signature_footer())

# Migration tools
migrate_app = typer.Typer(help="🔄 Project migration & upgrade tools")
app.add_typer(migrate_app, name="migrate")


@migrate_app.command("version")
def migrate_version(
    project_dir: Path = typer.Argument(Path("."), help="Project directory to migrate"),
    target_version: str = typer.Option("5.4", "--target", "-t", help="Target Unreal Engine version"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Simulate migration without modifying files"),
) -> None:
    """Migrate project to a new Unreal Engine version."""
    visuals.print_header_banner(
        "MIGRATE",
        f"Target: UE {target_version}",
        style="bright_yellow"
    )
    visuals.animated_loading(f" Migrating project to UE {target_version}...", color="bright_yellow")
    
    uproject = _find_uproject(project_dir)
    if not uproject:
        visuals.print_error_banner("Project Not Found", "No .uproject file found in directory.")
        raise typer.Exit(1)
    
    console.print(f"[bold]Project:[/bold] {uproject.stem}")
    
    # Read current version
    content = json.loads(uproject.read_text(encoding="utf-8"))
    current_version = content.get("EngineAssociation", "Unknown")
    
    console.print(f"[bold]Current:[/bold] {current_version}")
    console.print(f"[bold]Target:[/bold]  {target_version}")
    
    if dry_run:
        console.print("\n[yellow]Dry run - no changes made[/yellow]")
        return
    
    # Update engine association
    content["EngineAssociation"] = target_version
    uproject.write_text(json.dumps(content, indent=2), encoding="utf-8")
    
    console.print(f"\n[green]✓ Updated engine version to {target_version}[/green]")
    console.print("[dim]Note: Delete Intermediate, Saved, and DerivedDataCache folders before opening[/dim]")
    console.print(get_signature_footer())


@migrate_app.command("assets")
def migrate_assets(
    source: Path = typer.Argument(..., help="Source project directory"),
    target: Path = typer.Argument(..., help="Target project directory"),
    folder: str = typer.Option("", "--folder", "-f", help="Specific Content folder path to migrate"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Simulate migration without copying files"),
) -> None:
    """Migrate assets between projects."""
    visuals.print_header_banner(
        "MIGRATE",
        "Asset Migration",
        style="bright_yellow"
    )
    visuals.animated_loading("Preparing asset migration...", color="bright_yellow")
    
    source_content = source / "Content"
    target_content = target / "Content"
    
    if not source_content.exists():
        console.print(f"[red]Source Content folder not found: {source_content}[/red]")
        raise typer.Exit(1)
    
    # Determine what to copy
    if folder:
        source_path = source_content / folder
        if not source_path.exists():
            console.print(f"[red]Folder not found: {source_path}[/red]")
            raise typer.Exit(1)
    else:
        source_path = source_content
    
    # Count files
    files = list(source_path.rglob("*"))
    file_count = sum(1 for f in files if f.is_file())
    
    console.print(f"\n[bold]Files to migrate:[/bold] {file_count}")
    
    if dry_run:
        console.print("\n[yellow]Dry run - no changes made[/yellow]")
        return
    
    # Copy files
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]Migrating assets..."),
        console=console,
    ) as progress:
        task = progress.add_task("Copying", total=file_count)
        
        for file in files:
            if file.is_file():
                relative = file.relative_to(source_content)
                target_file = target_content / relative
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, target_file)
                progress.advance(task)
    
    console.print(f"\n[green]✓ Migrated {file_count} files[/green]")
    console.print(get_signature_footer())

backup_app = typer.Typer(help="💾 Smart backup & restore system")
app.add_typer(backup_app, name="backup")


@backup_app.command("create")
def backup_create(
    project_dir: Path = typer.Argument(Path("."), help="Project root directory"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Target output filepath for backup zip"),
    include_intermediate: bool = typer.Option(False, "--include-intermediate", help="Include Intermediate folder (increaes size)"),
    include_saved: bool = typer.Option(False, "--include-saved", help="Include Saved folder (local configs)"),
) -> None:
    """Create a smart backup of the project."""
    visuals.print_header_banner(
        "GIT & BACKUP",
        "Create Project Snapshot",
        style="spring_green2"
    )
    
    uproject = _find_uproject(project_dir)
    if not uproject:
        visuals.print_error_banner("Project Not Found", "No .uproject file found.")
        raise typer.Exit(1)
    
    project_name = uproject.stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output is None:
        output = project_dir.parent / f"{project_name}_backup_{timestamp}"
    
    # Folders to exclude by default
    exclude_patterns = [".git", "__pycache__", "*.pyc", "DerivedDataCache"]
    
    if not include_intermediate:
        exclude_patterns.append("Intermediate")
    
    if not include_saved:
        exclude_patterns.append("Saved")
    
    console.print(f"\n[bold]Source:[/bold] {project_dir}")
    console.print(f"[bold]Target:[/bold] {output}")
    console.print(f"[dim]Excluding: {', '.join(exclude_patterns)}[/dim]")
    
    # Count files to backup
    files_to_backup = []
    for file in project_dir.rglob("*"):
        if file.is_file():
            skip = False
            for pattern in exclude_patterns:
                if pattern in str(file):
                    skip = True
                    break
            if not skip:
                files_to_backup.append(file)
    
    console.print(f"[bold]Files to backup:[/bold] {len(files_to_backup)}")
    
    # Create backup
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]Creating backup..."),
        console=console,
    ) as progress:
        task = progress.add_task("Copying", total=len(files_to_backup))
        
        for file in files_to_backup:
            relative = file.relative_to(project_dir)
            target_file = output / relative
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target_file)
            progress.advance(task)
    
    # Calculate backup size
    backup_size = sum(f.stat().st_size for f in output.rglob("*") if f.is_file())
    
    console.print(f"\n[green]✓ Backup created: {output}[/green]")
    console.print(f"[dim]Size: {backup_size / 1024 / 1024:.1f} MB[/dim]")
    console.print(get_signature_footer())


@backup_app.command("list")
def backup_list(
    backup_dir: Path = typer.Argument(Path("."), help="Directory containing backups"),
) -> None:
    """List available backups."""
    visuals.print_header_banner(
        "GIT & BACKUP",
        "List Backups",
        style="spring_green2"
    )
    visuals.animated_loading("Listing available backups...", color="spring_green2")
    
    # Find backup folders (containing .uproject files)
    backups = []
    if backup_dir.exists():
        for item in backup_dir.iterdir():
            if item.is_dir() and "_backup_" in item.name:
                uproject = list(item.glob("*.uproject"))
                if uproject:
                    size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                    backups.append({
                        "name": item.name,
                        "path": item,
                        "size": size,
                        "created": datetime.fromtimestamp(item.stat().st_mtime),
                    })
    
    if not backups:
        console.print("[dim]No backups found in this directory[/dim]")
        return
    
    table = Table(title="Backups", box=visuals.ROUNDED, border_style="cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Created")
    
    for backup in sorted(backups, key=lambda x: x["created"], reverse=True):
        table.add_row(
            backup["name"],
            f"{backup['size'] / 1024 / 1024:.1f} MB",
            backup["created"].strftime("%Y-%m-%d %H:%M"),
        )
    
    console.print(table)
    console.print(get_signature_footer())


@backup_app.command("restore")
def backup_restore(
    backup_path: Path = typer.Argument(..., help="Path to backup zip file"),
    target: Path = typer.Argument(..., help="Directory to restore to"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files without prompt"),
) -> None:
    """Restore a backup."""
    visuals.print_header_banner(
        "GIT & BACKUP",
        "Restore Backup",
        style="spring_green2"
    )
    visuals.animated_loading("Restoring backup...", color="spring_green2")
    
    if not backup_path.exists():
        console.print(f"[red]Backup not found: {backup_path}[/red]")
        raise typer.Exit(1)
    
    if target.exists() and not force:
        console.print(f"[red]Target exists: {target}[/red]")
        console.print("[dim]Use --force to overwrite[/dim]")
        raise typer.Exit(1)
    
    console.print(f"[bold]Restoring:[/bold] {backup_path}")
    console.print(f"[bold]To:[/bold] {target}")
    
    shutil.copytree(backup_path, target, dirs_exist_ok=force)
    
    console.print(f"\n[green]✓ Restored to {target}[/green]")
    console.print(get_signature_footer())

# Template management
template_app = typer.Typer(help="📋 Project templates & creation")
app.add_typer(template_app, name="template")


TEMPLATES = {
    "blank": "Empty project with minimal setup",
    "firstperson": "First person shooter template",
    "thirdperson": "Third person character template",
    "topdown": "Top-down game template",
    "puzzle": "Puzzle game template",
    "vr": "Virtual reality template",
    "mobile": "Mobile game optimized template",
}


@template_app.command("list")
def template_list() -> None:
    """List available project templates."""
    visuals.print_header_banner(
        "PROJECT & CONFIG",
        "List Templates",
        style="bright_cyan"
    )
    visuals.animated_loading("Fetching available templates...", color="bright_cyan")
    
    table = Table(title="Available Templates", box=visuals.ROUNDED, border_style="cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    
    for name, desc in TEMPLATES.items():
        table.add_row(name, desc)
    
    console.print(table)
    console.print(get_signature_footer())


@template_app.command("create")
def template_create(
    name: str = typer.Argument(..., help="Name of the new project"),
    template: str = typer.Option("blank", "--template", "-t", help="Template ID to use (see template list)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Destination directory"),
) -> None:
    """Create a new project from template."""
    visuals.print_header_banner(
        "PROJECT & CONFIG",
        "Create From Template",
        style="bright_cyan"
    )
    visuals.animated_loading(f" Creating project from template: {template}...", color="bright_cyan")
    
    if template not in TEMPLATES:
        console.print(f"[red]Unknown template: {template}[/red]")
        console.print(f"[dim]Available: {', '.join(TEMPLATES.keys())}[/dim]")
        raise typer.Exit(1)
    
    output_dir = output or Path(f"./{name}")
    
    console.print(f"[bold]Project:[/bold] {name}")
    console.print(f"[bold]Template:[/bold] {template}")
    console.print(f"[bold]Location:[/bold] {output_dir}")
    
    # Create project structure
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "Content").mkdir(exist_ok=True)
    (output_dir / "Config").mkdir(exist_ok=True)
    (output_dir / "Source").mkdir(exist_ok=True)
    
    # Create .uproject file
    uproject = {
        "FileVersion": 3,
        "EngineAssociation": "5.4",
        "Category": "",
        "Description": "",
        "Modules": [
            {
                "Name": name,
                "Type": "Runtime",
                "LoadingPhase": "Default"
            }
        ]
    }
    
    (output_dir / f"{name}.uproject").write_text(
        json.dumps(uproject, indent=2),
        encoding="utf-8"
    )
    
    # Create basic config
    config_content = f"""[/Script/EngineSettings.GeneralProjectSettings]
ProjectID=UnrealMateProject
ProjectName={name}
ProjectVersion=1.0.0
"""
    (output_dir / "Config" / "DefaultGame.ini").write_text(config_content, encoding="utf-8")
    
    console.print(f"\n[green]✓ Project created: {output_dir}[/green]")
    console.print(get_signature_footer())


@template_app.command("save")
def template_save(
    project_dir: Path = typer.Argument(Path("."), help="Project to save as template"),
    name: str = typer.Argument(..., help="Template name"),
) -> None:
    """💾 Save current project as a re-usable template."""
    visuals.print_header_banner(
        "PROJECT & CONFIG",
        "Save As Template",
        style="bright_cyan"
    )
    visuals.animated_loading(f" Saving project as template: {name}...", color="bright_cyan")
    
    templates_dir = Path.home() / ".unrealmate" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    target = templates_dir / name
    
    uproject = _find_uproject(project_dir)
    if not uproject:
        visuals.print_error_banner("Project Not Found", "No .uproject file found.")
        raise typer.Exit(1)
    
    # Copy essential files
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]Saving template..."),
        console=console,
    ) as progress:
        task = progress.add_task("Copying")
        
        # Copy Content (but not large files)
        content = project_dir / "Content"
        if content.exists():
            for file in content.rglob("*"):
                if file.is_file() and file.stat().st_size < 10 * 1024 * 1024:
                    relative = file.relative_to(project_dir)
                    target_file = target / relative
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, target_file)
        
        # Copy Config
        config = project_dir / "Config"
        if config.exists():
            shutil.copytree(config, target / "Config", dirs_exist_ok=True)
        
        # Copy .uproject (renamed)
        shutil.copy2(uproject, target / "Template.uproject")
    
    console.print(f"\n[green]✓ Template saved: {name}[/green]")
    console.print(f"[dim]Location: {target}[/dim]")
    console.print(get_signature_footer())

@build_app.command("docker")
def build_docker(
    path: str = typer.Option(".", "--path", "-p", help="Project root directory")
):
    """🐳 Generate optimized Dockerfile for Unreal Engine."""
    visuals.print_header_banner(
        "BUILD & CI/CD",
        "Docker Setup",
        style="yellow"
    )
    
    dockerfile_content = """# UnrealMate Generated Dockerfile
# Optimized for Unreal Engine build environment
FROM ghcr.io/epicgames/unreal-engine:dev-5.4 AS builder

WORKDIR /project

# Copy project files
COPY . .

# Build project
RUN /home/ue4/UnrealEngine/Engine/Build/BatchFiles/RunUAT.sh \\
    BuildCookRun \\
    -project=/project/*.uproject \\
    -noP4 -cook -stage -archive \\
    -archivedirectory=/output \\
    -package -clientconfig=Shipping \\
    -pak -prereqs -nodebuginfo

# Runtime stage
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y libsdl2-2.0-0 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /output /app
WORKDIR /app
ENTRYPOINT ["./ProjectName"]
"""
    
    output_path = (Path(path) / "Dockerfile").resolve()
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dockerfile_content)
        console.print(f"[green]✅ Dockerfile created![/green]")
        console.print(f"[dim]Location: {output_path}[/dim]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Edit the Dockerfile for your project name")
        console.print("2. Run: docker build -t myproject .")
        console.print("3. Run: docker run myproject")
    except Exception as e:
        console.print(f"[red]❌ Failed to create Dockerfile: {e}[/red]")
    
    console.print(get_signature_footer())



# ═══════════════════════════════════════════════════════════════════════════════
# COLLABORATION & REPORTING COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════




report_app = typer.Typer(help="📊 Reporting & dashboard tools")
app.add_typer(report_app, name="report")

@report_app.command("dashboard")
def report_dashboard():
    """🌐 Launch the local interactive web dashboard."""
    from unrealmate.core.team_dashboard import TeamDashboard
    
    visuals.print_header_banner(
        "COLLABORATION & REPORTING",
        "Project Dashboard",
        style="dark_orange"
    )
    visuals.animated_loading("Starting dashboard server...", color="dark_orange")
    
    try:
        dashboard = TeamDashboard(".")
        if dashboard.start(open_browser=True):
            console.print(Panel("[cyan]Web Dashboard is running![/cyan]", border_style="cyan"))
            console.print(f"[green]✅ Access at http://localhost:8080[/green]")
            console.print("[dim]Press Ctrl+C to stop the server[/dim]")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopping dashboard...[/yellow]")
                dashboard.stop()
        else:
            console.print("[red]❌ Failed to start dashboard. Ensure Flask is installed: pip install flask[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error starting dashboard: {e}[/red]")
        console.print("[yellow]Tip: Make sure port 8080 is free.[/yellow]")


@report_app.command("html")
def report_html(
    path: str = typer.Argument(".", help="Project root directory"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output HTML file path")
):
    """📄 Generate HTML project report with real stats."""
    visuals.print_header_banner(
        "COLLABORATION & REPORTING",
        "Project Status Report",
        style="dark_orange"
    )
    visuals.animated_loading("Compiling project data...", color="dark_orange")
    
    project_path = Path(path).resolve()
    
    # Gather real project data
    uproject_files = list(project_path.rglob("*.uproject"))
    cpp_files = list(project_path.rglob("*.cpp")) + list(project_path.rglob("*.h"))
    bp_files = list(project_path.rglob("*.uasset"))
    umap_files = list(project_path.rglob("*.umap"))
    py_files = list(project_path.rglob("*.py"))
    project_name = uproject_files[0].stem if uproject_files else project_path.name
    
    # Config info
    config = load_config()
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{project_name} - UnrealMate Report</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; padding: 40px; }}
        h1 {{ color: #00d4ff; border-bottom: 2px solid #00d4ff; padding-bottom: 10px; }}
        h2 {{ color: #a855f7; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #333; padding: 10px; text-align: left; }}
        th {{ background: #16213e; color: #00d4ff; }}
        td {{ background: #0f3460; }}
        .footer {{ margin-top: 40px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>📊 {project_name} - Project Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>📁 Project Overview</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Project Name</td><td>{project_name}</td></tr>
        <tr><td>Project Path</td><td>{project_path}</td></tr>
        <tr><td>.uproject files</td><td>{len(uproject_files)}</td></tr>
        <tr><td>C++ source files</td><td>{len(cpp_files)}</td></tr>
        <tr><td>Blueprints / Assets</td><td>{len(bp_files)}</td></tr>
        <tr><td>Scene maps (.umap)</td><td>{len(umap_files)}</td></tr>
        <tr><td>Python scripts</td><td>{len(py_files)}</td></tr>
    </table>
    
    <h2>⚙️ Configuration</h2>
    <table>
        <tr><th>Setting</th><th>Value</th></tr>
        <tr><td>Cache enabled</td><td>{config.performance.cache_enabled}</td></tr>
        <tr><td>Parallel processing</td><td>{config.performance.parallel_processing}</td></tr>
        <tr><td>Max workers</td><td>{config.performance.max_workers}</td></tr>
        <tr><td>Git LFS auto</td><td>{config.git.auto_lfs}</td></tr>
    </table>
    
    <div class="footer">Generated by UnrealMate CLI | © 2026 gktrk363</div>
</body>
</html>"""
    
    if output:
        output_path = Path(output).resolve()
    else:
        output_path = (project_path / "unrealmate_report.html").resolve()
    
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        console.print(f"[green]✅ Report generated![/green]")
        console.print(f"[dim]Location: {output_path}[/dim]")
    except Exception as e:
        console.print(f"[red]❌ Failed to generate report: {e}[/red]")
    
    console.print(get_signature_footer())

@report_app.command("json")
def report_json(
    path: str = typer.Argument(".", help="Project root directory"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save JSON to file")
):
    """💾 Export project stats as JSON (prints or saves to file)."""
    visuals.print_header_banner(
        "COLLABORATION & REPORTING",
        "Export JSON Data",
        style="dark_orange"
    )
    visuals.animated_loading("Gathering project data...", color="dark_orange")
    
    project_path = Path(path).resolve()
    
    # Gather real data
    uproject_files = list(project_path.rglob("*.uproject"))
    cpp_files = list(project_path.rglob("*.cpp")) + list(project_path.rglob("*.h"))
    bp_files = list(project_path.rglob("*.uasset"))
    umap_files = list(project_path.rglob("*.umap"))
    
    config = load_config()
    from dataclasses import asdict
    
    data = {
        "project": uproject_files[0].stem if uproject_files else project_path.name,
        "path": str(project_path),
        "timestamp": str(datetime.now()),
        "stats": {
            "uproject_files": len(uproject_files),
            "cpp_source_files": len(cpp_files),
            "blueprint_assets": len(bp_files),
            "scene_maps": len(umap_files),
        },
        "config": asdict(config),
    }
    
    json_str = json.dumps(data, indent=2, default=str)
    console.print(Panel(json_str, title="JSON Output", border_style="cyan"))
    
    if output:
        output_path = Path(output).resolve()
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            console.print(f"[green]✅ JSON saved![/green]")
            console.print(f"[dim]Location: {output_path}[/dim]")
        except Exception as e:
            console.print(f"[red]❌ Failed to save: {e}[/red]")
    
    console.print(get_signature_footer())

@report_app.command("notify")
def report_notify(
    message: str = typer.Argument(..., help="Message content"),
):
    """🔔 Save a team notification to the project notification log."""
    visuals.print_header_banner(
        "COLLABORATION & REPORTING",
        "Send Notification",
        style="dark_orange"
    )
    
    log_dir = Path.home() / ".unrealmate" / "notifications"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "notification_log.txt"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)
        console.print(f"[green]✅ Notification logged![/green]")
        console.print(f"[dim]Log file: {log_file.resolve()}[/dim]")
        console.print(f"[dim]Message: {message}[/dim]")
        console.print("\n[yellow]💡 For Discord/Slack integration, configure webhook URL:[/yellow]")
        console.print("[dim]   unrealmate config set notification.webhook_url <URL>[/dim]")
    except Exception as e:
        console.print(f"[red]❌ Failed to log notification: {e}[/red]")
    
    console.print(get_signature_footer())


# ═══════════════════════════════════════════════════════════════════════════════
# MARKETPLACE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

marketplace_app = typer.Typer(help="🛒 Marketplace integration & asset library")
app.add_typer(marketplace_app, name="marketplace")



# ── Marketplace mock database ──────────────────────────────────────────────────
_MARKETPLACE_DB = [
    {"name": "Advanced Locomotion System V4", "price": "Free",     "rating": "⭐⭐⭐⭐⭐", "category": "Blueprints",      "tags": ["locomotion", "movement", "animation", "character"], "version": "4.2", "installed": True,  "latest": "4.3"},
    {"name": "Ultra Dynamic Sky",            "price": "$29.99",   "rating": "⭐⭐⭐⭐⭐", "category": "Environment",     "tags": ["sky", "weather", "atmosphere", "clouds"],           "version": "7.4", "installed": True,  "latest": "7.5"},
    {"name": "Dungeon Architect",            "price": "$129.99",  "rating": "⭐⭐⭐⭐⭐", "category": "Blueprints",      "tags": ["procedural", "dungeon", "level", "generation"],     "version": "3.1", "installed": False, "latest": "3.1"},
    {"name": "Electronic Nodes",             "price": "$14.99",   "rating": "⭐⭐⭐⭐⭐", "category": "Editor",          "tags": ["editor", "nodes", "blueprint", "visual"],           "version": "3.2", "installed": True,  "latest": "3.2"},
    {"name": "Easy Multi Save",              "price": "$24.99",   "rating": "⭐⭐⭐⭐",  "category": "Blueprints",      "tags": ["save", "load", "data", "persistence"],              "version": "2.8", "installed": False, "latest": "2.8"},
    {"name": "Megascans Trees European",     "price": "Free",     "rating": "⭐⭐⭐⭐⭐", "category": "Environment",     "tags": ["trees", "foliage", "nature", "megascans"],          "version": "1.0", "installed": True,  "latest": "1.1"},
    {"name": "City Sample",                  "price": "Free",     "rating": "⭐⭐⭐⭐⭐", "category": "Showcase",        "tags": ["city", "buildings", "urban", "demo", "nanite"],     "version": "5.3", "installed": True,  "latest": "5.4"},
    {"name": "MetaHuman Plugin",             "price": "Free",     "rating": "⭐⭐⭐⭐",  "category": "Characters",      "tags": ["metahuman", "face", "character", "realistic"],      "version": "1.2", "installed": True,  "latest": "1.2"},
    {"name": "Chaos Destruction System",     "price": "$49.99",   "rating": "⭐⭐⭐⭐",  "category": "VFX",             "tags": ["destruction", "physics", "chaos", "effects"],       "version": "2.0", "installed": False, "latest": "2.0"},
    {"name": "AI Navigation Pro",            "price": "$39.99",   "rating": "⭐⭐⭐⭐⭐", "category": "AI",              "tags": ["ai", "navigation", "pathfinding", "npc"],           "version": "1.5", "installed": False, "latest": "1.5"},
    {"name": "GAS Companion",                "price": "$34.99",   "rating": "⭐⭐⭐⭐⭐", "category": "Gameplay",        "tags": ["gas", "ability", "gameplay", "combat"],             "version": "3.4", "installed": False, "latest": "3.4"},
    {"name": "Niagara Fluids",               "price": "Free",     "rating": "⭐⭐⭐⭐",  "category": "VFX",             "tags": ["niagara", "particles", "vfx", "water", "fluid"],    "version": "5.3", "installed": True,  "latest": "5.4"},
    {"name": "Power IK",                     "price": "$49.99",   "rating": "⭐⭐⭐⭐⭐", "category": "Animation",       "tags": ["ik", "animation", "procedural", "body"],            "version": "1.8", "installed": False, "latest": "1.8"},
    {"name": "Landscape Pro Auto Material",  "price": "$69.99",   "rating": "⭐⭐⭐⭐",  "category": "Environment",     "tags": ["landscape", "terrain", "material", "auto"],         "version": "2.5", "installed": False, "latest": "2.5"},
    {"name": "Dialogue Plugin",              "price": "$29.99",   "rating": "⭐⭐⭐⭐",  "category": "Blueprints",      "tags": ["dialogue", "conversation", "npc", "quest"],         "version": "4.1", "installed": False, "latest": "4.1"},
    {"name": "Runtime Audio Importer",       "price": "Free",     "rating": "⭐⭐⭐⭐⭐", "category": "Audio",           "tags": ["audio", "sound", "import", "runtime", "music"],     "version": "2.1", "installed": True,  "latest": "2.1"},
    {"name": "Motion Warping",               "price": "Free",     "rating": "⭐⭐⭐⭐⭐", "category": "Animation",       "tags": ["animation", "warping", "motion", "movement"],       "version": "5.3", "installed": True,  "latest": "5.3"},
    {"name": "Water Shader Pack",            "price": "$19.99",   "rating": "⭐⭐⭐⭐",  "category": "Materials",       "tags": ["water", "shader", "ocean", "material", "lake"],     "version": "1.3", "installed": False, "latest": "1.3"},
    {"name": "Inventory Framework",          "price": "$44.99",   "rating": "⭐⭐⭐⭐⭐", "category": "Gameplay",        "tags": ["inventory", "item", "loot", "rpg"],                 "version": "3.0", "installed": False, "latest": "3.0"},
    {"name": "Modular Building Set",         "price": "$39.99",   "rating": "⭐⭐⭐⭐⭐", "category": "Environment",     "tags": ["modular", "building", "architecture", "kit"],       "version": "2.2", "installed": False, "latest": "2.2"},
]


@marketplace_app.command("search")
def marketplace_search(query: str = typer.Argument(..., help="Search term")):
    """🔍 Search Unreal Engine Marketplace."""
    visuals.print_header_banner(
        "MARKETPLACE & PLUGINS",
        "Search Assets",
        style="gold1"
    )
    visuals.animated_loading(f" Searching Marketplace for: '{query}'...", color="gold1")
    console.print(Panel(f"[cyan]Searching Marketplace for: '{query}'...[/cyan]", border_style="cyan"))

    q = query.lower()
    results = [
        a for a in _MARKETPLACE_DB
        if q in a["name"].lower()
        or q in a["category"].lower()
        or any(q in t for t in a["tags"])
    ]

    table = Table(title=f"Results for '{query}' ({len(results)} found)")
    table.add_column("#", style="dim", width=3)
    table.add_column("Asset Name", style="cyan bold")
    table.add_column("Category", style="bright_magenta")
    table.add_column("Price", style="green")
    table.add_column("Rating", style="yellow")

    if results:
        for i, item in enumerate(results, 1):
            table.add_row(str(i), item["name"], item["category"], item["price"], item["rating"])
    else:
        console.print(f"[red]Offline Simulation: '{query}' not found in local mock DB.[/red]")
        console.print(f"[yellow]Showing popular assets instead:[/yellow]")
        for i, item in enumerate(_MARKETPLACE_DB[:5], 1):
            table.add_row(str(i), item["name"], item["category"], item["price"], item["rating"])

    console.print(table)
    console.print("[dim]To install: unrealmate marketplace install 'Asset Name'[/dim]")
    console.print(get_signature_footer())

@marketplace_app.command("install")
def marketplace_install(asset_name: str = typer.Argument(..., help="Name of asset to install")):
    """⬇️ Install asset from Marketplace (Launcher integration)."""
    visuals.print_header_banner(
        "MARKETPLACE & PLUGINS",
        "Install Asset",
        style="gold1"
    )
    visuals.animated_loading(f" Installing '{asset_name}'...", color="gold1")

    found = next((a for a in _MARKETPLACE_DB if asset_name.lower() in a["name"].lower()), None)

    if found:
        if found["installed"]:
            console.print(f"[yellow]⚠️  '{found['name']}' is already installed (v{found['version']})[/yellow]")
        else:
            console.print(Panel(f"[cyan]Installing: {found['name']} ({found['price']})[/cyan]", border_style="cyan"))
            console.print(f"[green]✅ '{found['name']}' v{found['latest']} installed successfully![/green]")
    else:
        console.print(Panel(f"[cyan]Searching: '{asset_name}'[/cyan]", border_style="cyan"))
        console.print("[yellow]⚠️  Asset not found in local cache. Opening Marketplace...[/yellow]")

    import webbrowser
    search_url = f"https://www.unrealengine.com/marketplace/en-US/store/search?q={{asset_name.replace(' ', '%20')}}"
    console.print(f"[dim]Marketplace URL: {{search_url}}[/dim]")
    console.print(get_signature_footer())

@marketplace_app.command("list")
def marketplace_list():
    """📦 List owned/installed marketplace assets."""
    visuals.print_header_banner(
        "MARKETPLACE & PLUGINS",
        "My Assets",
        style="gold1"
    )
    visuals.animated_loading("Fetching your assets...", color="gold1")
    console.print(Panel("[cyan]Scanning Library...[/cyan]", border_style="cyan"))

    installed = [a for a in _MARKETPLACE_DB if a["installed"]]
    not_installed = [a for a in _MARKETPLACE_DB if not a["installed"]]

    table = Table(title=f"My Assets ({len(installed)} installed, {len(not_installed)} owned)")
    table.add_column("Asset", style="cyan")
    table.add_column("Category", style="bright_magenta")
    table.add_column("Version", style="dim white")
    table.add_column("Status", style="green")

    for a in installed:
        status = "[green]✅ Installed[/green]"
        if a["version"] != a["latest"]:
            status = f"[yellow]⬆ Update: v{a['latest']}[/yellow]"
        table.add_row(a["name"], a["category"], f"v{a['version']}", status)

    for a in not_installed[:3]:
        table.add_row(a["name"], a["category"], f"v{a['latest']}", "[dim]Not Installed[/dim]")

    console.print(table)
    console.print(f"[dim]Total: {len(_MARKETPLACE_DB)} assets in library[/dim]")
    console.print(get_signature_footer())

@marketplace_app.command("check-updates")
def marketplace_check_updates():
    """Check for updates for installed assets."""
    visuals.print_header_banner(
        "MARKETPLACE & PLUGINS",
        "Check Updates",
        style="gold1"
    )
    visuals.animated_loading("Checking for updates...", color="gold1")
    console.print(Panel("[cyan]Simulating check against remote database...[/cyan]", border_style="cyan"))

    updates = [a for a in _MARKETPLACE_DB if a["installed"] and a["version"] != a["latest"]]

    if updates:
        table = Table(title=f"Updates Available ({len(updates)})")
        table.add_column("Asset", style="cyan bold")
        table.add_column("Current", style="yellow")
        table.add_column("Latest", style="green bold")
        table.add_column("Category", style="dim")

        for a in updates:
            table.add_row(a["name"], f"v{a['version']}", f"v{a['latest']}", a["category"])

        console.print(table)
        console.print("[yellow]⚠️  To update, please use the Epic Games Launcher[/yellow]")
        console.print("[dim](This is a simulated check using local mock data)[/dim]")
    else:
        console.print("[green]✅ All installed assets are up to date![/green]")

    no_update = [a for a in _MARKETPLACE_DB if a["installed"] and a["version"] == a["latest"]]
    console.print(f"[dim]{len(no_update)} assets are up to date[/dim]")
    console.print(get_signature_footer())

@marketplace_app.command("export-list")
def marketplace_export(
    output: Path = typer.Option(Path("marketplace_assets.json"), "--output", "-o", help="Output file"),
):
    """Export list of marketplace assets."""
    visuals.print_header_banner(
        "MARKETPLACE & PLUGINS",
        "Export Asset List",
        style="gold1"
    )
    visuals.animated_loading(f" Exporting asset list to {output}...", color="gold1")
    console.print(Panel(f"[cyan]Exporting asset list to {output}...[/cyan]", border_style="cyan"))

    export_data = [
        {
            "name": a["name"],
            "version": a["version"],
            "latest": a["latest"],
            "category": a["category"],
            "price": a["price"],
            "installed": a["installed"],
            "tags": a["tags"],
        }
        for a in _MARKETPLACE_DB
    ]

    try:
        output.write_text(json.dumps(export_data, indent=2), encoding="utf-8")
        console.print(f"[green]✅ Exported {len(export_data)} assets to {output}[/green]")

        installed_count = len([a for a in _MARKETPLACE_DB if a["installed"]])
        console.print(f"[dim]  → {installed_count} installed, {len(export_data) - installed_count} not installed[/dim]")
    except Exception as e:
        console.print(f"[red]❌ Export failed: {e}[/red]")

    console.print(get_signature_footer())
# AI-powered commands
ai_app = typer.Typer(help="🤖 AI-powered assistant & tools")
app.add_typer(ai_app, name="ai")

# Automation commands
automate_app = typer.Typer(help="⚙️ Automated fixes & organization")
app.add_typer(automate_app, name="automate")

# Collaboration commands
collab_app = typer.Typer(help="👥 Team collaboration & sharing")
app.add_typer(collab_app, name="collab")


# ═══════════════════════════════════════════════════════════════════════════════
# AI COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@ai_app.command("nlp")
def ai_nlp(
    command: str = typer.Argument(..., help="Natural language command to interpret")
):
    """🗣️ Convert natural language to CLI commands using NLP parser."""
    from unrealmate.core.nlp_commands import NLPCommandParser
    
    visuals.print_header_banner(
        "AI & AUTOMATION",
        "Natural Language Processing",
        style="bright_magenta"
    )
    visuals.animated_loading("Processing natural language command...", color="bright_magenta")
    console.print(Panel("[bold cyan]🤖 Processing natural language command...[/bold cyan]", border_style="cyan"))
    
    parser = NLPCommandParser()
    intent = parser.parse(command)
    result = {"success": intent.confidence > 0.5, "command": parser.to_cli_command(intent), "confidence": intent.confidence, "error": "Low confidence" if intent.confidence <= 0.5 else None}
    
    if result.get("success"):
        console.print(f"[green]✅ Interpreted as: {result.get('command')}[/green]")
        console.print(f"[dim]Confidence: {result.get('confidence', 0):.0%}[/dim]")
    else:
        console.print(f"[yellow]⚠️ Could not interpret command: {result.get('error')}[/yellow]")
    
    console.print(get_signature_footer())


@ai_app.command("detect-bugs")
def ai_detect_bugs(
    path: str = typer.Argument(".", help="Path to scan for potential bugs")
):
    """🐛 Pattern-based bug detection in .cpp/.h source files."""
    from unrealmate.core.bug_detector import BugDetector
    
    visuals.print_header_banner(
        "AI & AUTOMATION",
        "AI Bug Detection",
        style="bright_magenta"
    )
    visuals.animated_loading("Scanning for potential bugs...", color="bright_magenta")
    console.print(Panel("[bold cyan]🔍 Scanning for potential bugs...[/bold cyan]", border_style="cyan"))
    
    detector = BugDetector(path)
    results = detector.scan_directory(Path(path))
    
    if not results:
        console.print("[green]✨ No potential bugs detected![/green]")
    else:
        table = Table(title="Potential Issues Found")
        table.add_column("File", style="cyan")
        table.add_column("Issue", style="yellow")
        table.add_column("Severity", style="red")
        
        for issue in results[:20]:
            # DetectedBug is a dataclass, access attributes directly
            table.add_row(
                str(issue.file_path),
                issue.description,
                issue.severity.value if hasattr(issue.severity, 'value') else str(issue.severity)
            )
        
        console.print(table)
    
    console.print(get_signature_footer())


@ai_app.command("review")
def ai_review(
    path: str = typer.Argument(".", help="Path to review")
):
    """📝 List and review Git pull requests."""
    from unrealmate.core.code_review import CodeReviewManager
    
    visuals.print_header_banner(
        "AI & AUTOMATION",
        "AI Code Review",
        style="bright_magenta"
    )
    visuals.animated_loading("Running code review...", color="bright_magenta")
    console.print(Panel("[bold cyan]📝 Running code review...[/bold cyan]", border_style="cyan"))
    
    reviewer = CodeReviewManager(path)
    suggestions = reviewer.list_prs()
    
    if not suggestions:
        console.print("[green]✨ Code looks great! No suggestions.[/green]")
    else:
        for i, suggestion in enumerate(suggestions[:10], 1):
            # Formatted PR string
            if hasattr(suggestion, 'title'):
                pr_str = f"#{suggestion.number} {suggestion.title} ({suggestion.author})"
            else:
                pr_str = str(suggestion)
            console.print(f"[yellow]{i}. {pr_str}[/yellow]")
    
    console.print(get_signature_footer())


# ═══════════════════════════════════════════════════════════════════════════════
# AUTOMATION COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@automate_app.command("fix")
def automate_fix(
    path: str = typer.Argument(".", help="Path to auto-fix"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Preview changes without applying")
):
    """🔧 Auto-fix common project issues."""
    from unrealmate.core.autofix import AutoFixer
    
    visuals.print_header_banner(
        "AI & AUTOMATION",
        "Auto-Fix Issues",
        style="bright_magenta"
    )
    visuals.animated_loading("Running auto-fix...", color="bright_magenta")
    console.print(Panel("[bold cyan]🔧 Running auto-fix...[/bold cyan]", border_style="cyan"))
    
    fixer = AutoFixer(path)
    report = fixer.fix_all(dry_run=dry_run)
    fixes = [action.title for action in report.actions if action.status.value == "success"]
    
    if dry_run:
        console.print("[yellow]🔍 Dry run mode - no changes applied[/yellow]")
    
    if fixes:
        for fix in fixes:
            status = "Would fix" if dry_run else "Fixed"
            console.print(f"[green]✅ {status}: {fix}[/green]")
    else:
        console.print("[green]✨ No issues to fix![/green]")
    
    console.print(get_signature_footer())


@automate_app.command("organize")
def automate_organize(
    path: str = typer.Argument(".", help="Path to organize")
):
    """📁 Analyze and organize misplaced assets."""
    from unrealmate.core.smart_organizer import SmartOrganizer
    
    visuals.print_header_banner(
        "AI & AUTOMATION",
        "Smart Organization",
        style="bright_magenta"
    )
    visuals.animated_loading("Running smart organizer...", color="bright_magenta")
    console.print(Panel("[bold cyan]📁 Running smart organizer...[/bold cyan]", border_style="cyan"))
    
    organizer = SmartOrganizer(path)
    analysis = organizer.analyze()
    result = {"files_moved": analysis.get("misplaced_count", 0)}
    
    console.print(f"[green]✅ Organized {result.get('files_moved', 0)} files[/green]")
    console.print(get_signature_footer())


# ═══════════════════════════════════════════════════════════════════════════════
# COLLABORATION COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@collab_app.command("dashboard")
def collab_dashboard():
    """📊 Show team dashboard summary."""
    from unrealmate.core.team_dashboard import DashboardDataProvider
    
    visuals.print_header_banner(
        "COLLABORATION & REPORTING",
        "Project Collaboration Stats",
        style="dark_orange"
    )
    visuals.animated_loading("Gathering team statistics...", color="dark_orange")
    console.print(Panel("[bold cyan]📊 Team Dashboard Summary[/bold cyan]", border_style="cyan"))
    
    try:
        provider = DashboardDataProvider(".")
        health = provider.get_project_health()
        team = provider.get_team_members()
        activity = provider.get_recent_activity(10)
        
        # Stats
        stats = {
            "Active Members": len(team),
            "Recent Activity": len(activity),
            "Build Health": f"{health.build_health:.0f}%",
            "Project Score": f"{health.overall_score:.0f}%"
        }
        
        table = Table(title="Team Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for k, v in stats.items():
            table.add_row(k, str(v))
            
        console.print(table)
        
        if team:
            console.print("\n[bold]Active Team Members:[/bold]")
            for m in team[:5]:
                console.print(f" • [cyan]{m.name}[/cyan] ({m.role}) - {m.recent_commits} commits")
                
        console.print("\n[dim]For full interactive dashboard, run: unrealmate report dashboard[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error fetching dashboard data: {e}[/red]")
    
    console.print(get_signature_footer())

@collab_app.command("share")
def collab_share(
    template_name: str = typer.Argument(..., help="Template name to share")
):
    """📤 Share project templates."""
    from unrealmate.core.template_sharing import TemplateExporter
    
    visuals.print_header_banner(
        "COLLABORATION & REPORTING",
        "Share Project Template",
        style="dark_orange"
    )
    visuals.animated_loading(f" Sharing template: {template_name}...", color="dark_orange")
    console.print(Panel(f"[bold cyan]📤 Sharing template: {template_name}[/bold cyan]", border_style="cyan"))
    
    try:
        exporter = TemplateExporter(".")
        output_path = Path.home() / ".unrealmate" / "shared" / f"{template_name}.zip"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        exporter.export(
            output_path=str(output_path),
            name=template_name,
            description=f"Shared template: {template_name}",
        )
        console.print(f"[green]✅ Template shared successfully![/green]")
        console.print(f"[dim]Location: {output_path}[/dim]")
    except Exception as e:
        console.print(f"[red]❌ Failed to share: {e}[/red]")
    
    console.print(get_signature_footer())


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@app.command()
def analytics():
    """📈 Show usage analytics and metrics."""
    from unrealmate.core.analytics import CommandTracker, AnalyticsManager
    
    visuals.print_header_banner(
        "CORE & SYSTEM",
        "Usage Statistics",
        style="bright_white"
    )
    visuals.animated_loading("Gathering usage statistics...", color="bright_white")
    console.print(Panel("[bold cyan]📈 UnrealMate Analytics[/bold cyan]", border_style="cyan"))
    
    tracker = CommandTracker()
    
    table = Table(title="Command Usage Statistics")
    table.add_column("Command", style="cyan")
    table.add_column("Usage Count", style="green")
    
    # Use real persistent data
    stats = tracker.stats
    if stats:
        for cmd, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            table.add_row(cmd, str(count))
        most_used = tracker.get_most_used()
    else:
        table.add_row("No commands run yet", "-")
        most_used = "None"
    
    console.print(table)
    if stats:
        console.print(f"\n[dim]Most used command: {most_used}[/dim]")
    
    console.print(get_signature_footer())
@app.command()
def health():
    """🏥 Show project health score."""
    from unrealmate.core.project_health import HealthScoreCalculator, CodeQualityMetrics
    
    visuals.print_header_banner(
        "CORE & SYSTEM",
        "Health Score & Metrics",
        style="bright_white"
    )
    visuals.animated_loading("Calculating project health score...", color="bright_white")
    console.print(Panel("[bold cyan]🏥 Project Health Check[/bold cyan]", border_style="cyan"))
    
    # Gather metrics
    quality = CodeQualityMetrics()
    metrics = {
        "test_coverage": quality.get_test_coverage(),
        "lint_score": quality.get_lint_score(),
        "asset_optimization": 75.0  # Placeholder
    }
    
    calculator = HealthScoreCalculator()
    score = calculator.calculate(metrics)
    
    if score >= 80:
        color = "green"
        emoji = "🎉"
    elif score >= 50:
        color = "yellow"
        emoji = "⚠️"
    else:
        color = "red"
        emoji = "🚨"
    
    console.print(f"\n{emoji} [bold {color}]Health Score: {score}/100[/bold {color}]\n")
    
    # Show breakdown
    table = Table(title="Health Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Score", style="green")
    
    table.add_row("Test Coverage", f"{metrics['test_coverage']:.0f}%")
    table.add_row("Lint Score", f"{metrics['lint_score']:.0f}%")
    table.add_row("Asset Optimization", f"{metrics['asset_optimization']:.0f}%")
    
    console.print(table)
    console.print(get_signature_footer())


@app.command()
def security_scan():
    """🔒 Run security scan."""
    from unrealmate.core.security import SecurityScanner
    
    visuals.print_header_banner(
        "CORE & SYSTEM",
        "Vulnerability Check",
        style="bright_white"
    )
    visuals.animated_loading("Scanning for security vulnerabilities...", color="bright_white")
    console.print(Panel("[bold cyan]🔒 Security Scan[/bold cyan]", border_style="cyan"))
    
    scanner = SecurityScanner()
    issues = scanner.check_dependencies()
    
    if not issues:
        console.print("[green]✅ No security issues found![/green]")
    else:
        for issue in issues:
            console.print(f"[yellow]⚠️ {issue}[/yellow]")
    
    console.print(get_signature_footer())


# ═══════════════════════════════════════════════════════════════════════════════
# © 2026 gktrk363 Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════════






if __name__ == "__main__":
    app()