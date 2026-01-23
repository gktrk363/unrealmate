"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          UnrealMate - cli.py                                 ║
║                                                                              ║
║  Author: gktrk363                                                           ║
║  Purpose: Main CLI interface for UnrealMate toolkit                         ║
║  Created: 2026-01-23                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Main CLI interface for UnrealMate - All-in-one toolkit for Unreal Engine developers.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

import typer
import subprocess
import shutil
import hashlib
import json
from pathlib import Path
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from rich.panel import Panel
from rich.progress import Progress, track
from rich.status import Status
from rich.traceback import install
from rich.align import Align
from rich.text import Text

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

# Install rich traceback handler
install(show_locals=True)

app = typer.Typer(
    name="unrealmate",
    help="🎮 All-in-one CLI toolkit for Unreal Engine developers",
    add_completion=False
)

# Use signature console
console = get_signature_console()

git_app = typer.Typer(help="🔧 Git helper commands")
app.add_typer(git_app, name="git")

asset_app = typer.Typer(help="📦 Asset management commands")
app.add_typer(asset_app, name="asset")

blueprint_app = typer.Typer(help="📊 Blueprint analysis commands")
app.add_typer(blueprint_app, name="blueprint")

# New performance commands
performance_app = typer.Typer(help="⚡ Performance analysis commands")
app.add_typer(performance_app, name="performance")

# Configuration commands
config_app = typer.Typer(help="⚙️  Configuration management")
app.add_typer(config_app, name="config")

# Plugin commands
plugin_app = typer.Typer(help="🔌 Plugin management")
app.add_typer(plugin_app, name="plugin")

# Build commands
build_app = typer.Typer(help="🏗️  Build and CI/CD tools")
app.add_typer(build_app, name="build")


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
    """Show UnrealMate version and information with signature banner."""
    config = load_config()
    
    # Show banner based on config
    print_signature_banner(
        console=console,
        compact=config.signature.compact_banner,
        show_version=True,
        version="1.0.7"
    )
    
    if config.signature.show_footer:
        console.print(get_signature_footer())


@app.command()
def doctor():
    console.print(Panel("[bold cyan]Running UnrealMate Doctor...[/bold cyan]", border_style="cyan"))

    checks = []
    score = 0
    max_score = 0
    current_dir = Path.cwd()
    console.print(f"[dim]Checking directory: {current_dir}[/dim]\n")

    with console.status("[bold green]Running health checks...", spinner="dots"):
        max_score += 25
        gitignore_path = current_dir / ".gitignore"
        if gitignore_path.exists():
            checks.append(("✅", ".gitignore", "Found", "green"))
            score += 25
        else:
            checks.append(("❌", ".gitignore", "Missing - run 'unrealmate git init'", "red"))
        
        max_score += 25
        uproject_files = list(current_dir.glob("*.uproject"))
        if uproject_files:
            checks.append(("✅", "UE Project", f"Found: {uproject_files[0].name}", "green"))
            score += 25
        else: 
            checks.append(("⚠️", "UE Project", "No .uproject file found", "yellow"))
        
        max_score += 25
        gitattributes = current_dir / ".gitattributes"
        if gitattributes.exists() and "lfs" in gitattributes.read_text().lower():
            checks.append(("✅", "Git LFS", "Configured", "green"))
            score += 25
        else: 
            checks.append(("❌", "Git LFS", "Not configured - run 'unrealmate git lfs'", "red"))
        
        max_score += 25
        large_files = []
        for ext in ["*.uasset", "*.umap", "*.pak"]:
            large_files.extend(current_dir.rglob(ext))
        
        if len(large_files) == 0:
            checks.append(("✅", "Large Files", "No large binary files in root", "green"))
            score += 25
        elif len(large_files) < 10:
            checks.append(("⚠️", "Large Files", f"{len(large_files)} binary files found", "yellow"))
            score += 15
        else:
            checks.append(("❌", "Large Files", f"{len(large_files)} binary files - consider LFS", "red"))
    
    table = Table(title="Health Check Results", show_header=True)
    table.add_column("Status", style="bold", width=6)
    table.add_column("Check", style="bold")
    table.add_column("Details")
    
    for status, check, details, color in checks: 
        table.add_row(status, check, f"[{color}]{details}[/{color}]")
    
    console.print(table)
    
    percentage = int((score / max_score) * 100)
    
    if percentage >= 80:
        color = "green"
        emoji = "🎉"
    elif percentage >= 50:
        color = "yellow"
        emoji = "⚠️"
    else:
        color = "red"
        emoji = "🚨"
    
    console.print(f"\n{emoji} [bold {color}]Health Score: {percentage}/100[/bold {color}]\n")


@git_app.command("init")
def git_init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing .gitignore")
):
    target = Path.cwd() / ".gitignore"
    template_path = Path(__file__).parent / "templates" / "gitignore.template"
    
    if target.exists() and not force:
        console.print("[yellow]⚠️ . gitignore already exists![/yellow]")
        console.print("[dim]Use --force to overwrite[/dim]")
        return
    
    if not template_path.exists():
        console.print("[red]❌ Template file not found![/red]")
        console.print(f"[dim]Looking for: {template_path}[/dim]")
        return
    
    content = template_path. read_text()
    target.write_text(content)
    console.print("[bold green]✅ .gitignore created successfully![/bold green]")
    console.print(f"[dim]Location: {target. absolute()}[/dim]")


@git_app.command("lfs")
def git_lfs(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing . gitattributes")
):
    console.print("\n[bold cyan]🔧 Setting up Git LFS.. .[/bold cyan]\n")
    
    try:
        result = subprocess.run(["git", "lfs", "version"], capture_output=True, text=True)
        if result.returncode != 0:
            console.print("[red]❌ Git LFS is not installed![/red]")
            console.print("[dim]Install it from: https://git-lfs.github.com[/dim]")
            return
        console.print(f"[green]✅ {result.stdout.strip()}[/green]")
    except FileNotFoundError: 
        console.print("[red]❌ Git LFS is not installed![/red]")
        console.print("[dim]Install it from: https://git-lfs.github.com[/dim]")
        return
    
    target = Path.cwd() / ".gitattributes"
    template_path = Path(__file__).parent / "templates" / "gitattributes. template"
    
    if target.exists() and not force:
        console.print("[yellow]⚠️ .gitattributes already exists![/yellow]")
        console.print("[dim]Use --force to overwrite[/dim]")
        return
    
    if not template_path.exists():
        console.print("[red]❌ Template file not found![/red]")
        console.print(f"[dim]Looking for: {template_path}[/dim]")
        return
    
    content = template_path.read_text()
    target.write_text(content)
    console.print("[bold green]✅ .gitattributes created successfully![/bold green]")
    
    try:
        subprocess.run(["git", "lfs", "install"], capture_output=True, text=True)
        console.print("[bold green]✅ Git LFS initialized![/bold green]")
    except Exception as e:
        console.print(f"[yellow]⚠️ Could not run 'git lfs install': {e}[/yellow]")
    
    console. print(f"\n[dim]Location: {target.absolute()}[/dim]")
    console.print("\n[bold green]🎉 Git LFS setup complete![/bold green]")
    console.print("[dim]Large binary files will now be tracked by LFS[/dim]\n")


@git_app.command("clean")
def git_clean(
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be deleted without deleting"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    console.print(Panel("[bold cyan]Scanning for unnecessary files...[/bold cyan]", border_style="cyan"))
    
    cleanup_folders = ["Saved", "Intermediate", "DerivedDataCache", "Build", ".vs"]
    skip_patterns = ["venv", ". venv", "site-packages", "node_modules", ". git"]
    
    found_folders = []
    total_size = 0
    
    with console.status("[bold yellow]Scanning directories...", spinner="dots"):
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
        console.print("[green]✨ No unnecessary files found!  Your project is clean.[/green]\n")
        return
    
    table = Table(title="Found Unnecessary Files", show_header=True)
    table.add_column("📁 Folder", style="cyan")
    table.add_column("Size", style="yellow", justify="right")
    
    for folder, size in found_folders:
        table. add_row(str(folder), format_size(size))
    
    table.add_row("─" * 20, "─" * 10)
    table.add_row("[bold]Total[/bold]", f"[bold green]{format_size(total_size)}[/bold green]")
    
    console.print(table)
    console.print()
    
    if dry_run:
        console.print("[yellow]🔍 Dry run mode - no files were deleted[/yellow]\n")
        return
    
    if not yes:
        confirm = Confirm.ask(f"[bold]Do you want to delete these files and free {format_size(total_size)}?[/bold]")
        if not confirm:
            console. print("[yellow]❌ Cleanup cancelled[/yellow]\n")
            return
    
    deleted_count = 0
    deleted_size = 0
    
    deleted_count = 0
    deleted_size = 0
    
    for folder, size in track(found_folders, description="[red]Deleting files...[/red]"):
        try:
            shutil.rmtree(folder)
            deleted_count += 1
            deleted_size += size
            # console.print(f"[green]✅ Deleted: {folder}[/green]") # Reduced verbosity for progress bar
        except Exception as e:
            console.print(f"[red]❌ Failed to delete {folder}: {e}[/red]")
    
    console.print(f"\n[bold green]🎉 Cleanup complete![/bold green]")
    console.print(f"[dim]Deleted {deleted_count} folders, freed {format_size(deleted_size)}[/dim]\n")


@asset_app.command("scan")
def asset_scan(
    path: str = typer.Argument(".", help="Path to scan for assets"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all assets (not just summary)")
):
    console.print(Panel("[bold cyan]Scanning for assets...[/bold cyan]", border_style="cyan"))
    
    scan_path = Path(path)
    
    if not scan_path. exists():
        console.print(f"[red]❌ Path not found: {path}[/red]")
        return
    
    asset_types = {
        "Blueprints": ["*. uasset"],
        "Maps": ["*.umap"],
        "Textures": ["*. png", "*.tga", "*.psd", "*.exr", "*.hdr"],
        "Audio": ["*.wav", "*.mp3", "*.ogg"],
        "3D Models": ["*. fbx", "*.obj"],
        "Materials": ["*.uasset"],
        "Videos": ["*.mp4", "*.mov", "*.avi"],
    }
    
    results = {}
    all_assets = []
    total_size = 0
    total_count = 0
    
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ".git", "Intermediate", "Saved"]
    
    with console.status("[bold green]Searching for files...", spinner="earth"):
        for category, extensions in asset_types.items():
            category_files = []
            category_size = 0
            
            for ext in extensions:
                for file in scan_path.rglob(ext):
                    if any(skip in str(file) for skip in skip_patterns):
                        continue
                    
                    size = get_file_size(file)
                    category_files.append((file, size))
                    category_size += size
                    all_assets.append((file, size, category))
            
            if category_files:
                results[category] = {
                    "count": len(category_files),
                    "size": category_size,
                    "files": category_files
                }
                total_count += len(category_files)
                total_size += category_size
    
    if not results:
        console. print("[yellow]⚠️ No assets found in this directory[/yellow]\n")
        return
    
    table = Table(title="Asset Summary", show_header=True)
    table.add_column("📁 Category", style="cyan")
    table.add_column("Count", style="magenta", justify="right")
    table.add_column("Size", style="yellow", justify="right")
    
    for category, data in results.items():
        table.add_row(category, str(data["count"]), format_size(data["size"]))
    
    table. add_row("─" * 15, "─" * 5, "─" * 10)
    table.add_row("[bold]Total[/bold]", f"[bold]{total_count}[/bold]", f"[bold green]{format_size(total_size)}[/bold green]")
    
    console.print(table)
    
    if show_all and all_assets:
        console.print("\n[bold]All Assets:[/bold]\n")
        
        detail_table = Table(show_header=True)
        detail_table.add_column("File", style="cyan")
        detail_table.add_column("Category", style="magenta")
        detail_table.add_column("Size", style="yellow", justify="right")
        
        all_assets. sort(key=lambda x: x[1], reverse=True)
        
        for file, size, category in all_assets[: 50]: 
            detail_table. add_row(str(file), category, format_size(size))
        
        if len(all_assets) > 50:
            detail_table.add_row(f"... and {len(all_assets) - 50} more", "", "")
        
        console.print(detail_table)
    
    if all_assets:
        console.print("\n[bold]🔝 Top 5 Largest Assets:[/bold]\n")
        
        top_table = Table(show_header=True)
        top_table. add_column("File", style="cyan")
        top_table.add_column("Size", style="yellow", justify="right")
        
        all_assets.sort(key=lambda x:  x[1], reverse=True)
        
        for file, size, category in all_assets[:5]:
            top_table.add_row(str(file), format_size(size))
        
        console.print(top_table)
    
    console.print(f"\n[bold green]✅ Scan complete![/bold green]")
    console.print(f"[dim]Found {total_count} assets totaling {format_size(total_size)}[/dim]\n")


@asset_app.command("organize")
def asset_organize(
    path: str = typer.Argument(".", help="Path to organize assets in"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be moved without moving"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
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
    """Analyze Blueprint files and show statistics"""
    
    console.print(Panel("[bold cyan]Analyzing Blueprints...[/bold cyan]", border_style="cyan"))
    
    scan_path = Path(path)
    
    if not scan_path.exists():
        console.print(f"[red]❌ Path not found: {path}[/red]")
        return
    
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ".git", "Intermediate", "Saved", "__pycache__"]
    
    blueprints = []
    total_variables = 0
    total_functions = 0
    total_events = 0
    total_nodes = 0
    
    blueprints = []
    total_variables = 0
    total_functions = 0
    total_events = 0
    total_nodes = 0
    
    uasset_files = list(scan_path.rglob("*.uasset"))
    
    for file in track(uasset_files, description="[green]Parsing Blueprints...[/green]"):
        if any(skip in str(file) for skip in skip_patterns):
            continue
        
        metrics = analyze_blueprint_file(file)
        
        if metrics and metrics["is_blueprint"]:
            blueprints.append(metrics)
            total_variables += metrics["variables"]
            total_functions += metrics["functions"]
            total_events += metrics["events"]
            total_nodes += metrics["nodes"]
    
    if not blueprints:
        console.print("[yellow]⚠️ No Blueprint files found in this directory[/yellow]\n")
        console.print("[dim]Make sure you're in an Unreal Engine project with . uasset files[/dim]\n")
        return
    
    blueprints.sort(key=lambda x:  x["nodes"], reverse=True)
    
    table = Table(title="Blueprint Analysis", show_header=True)
    table.add_column("📘 Blueprint", style="cyan")
    table.add_column("Variables", style="magenta", justify="right")
    table.add_column("Functions", style="green", justify="right")
    table.add_column("Events", style="yellow", justify="right")
    table.add_column("Nodes", style="red", justify="right")
    table.add_column("Size", style="dim", justify="right")
    
    display_blueprints = blueprints if show_all else blueprints[:10]
    
    for bp in display_blueprints:
        table.add_row(
            bp["name"],
            str(bp["variables"]),
            str(bp["functions"]),
            str(bp["events"]),
            str(bp["nodes"]),
            format_size(bp["size"])
        )
    
    if not show_all and len(blueprints) > 10:
        table.add_row(f"... and {len(blueprints) - 10} more", "", "", "", "", "")
    
    table.add_row("─" * 20, "─" * 5, "─" * 5, "─" * 5, "─" * 5, "─" * 8)
    table.add_row(
        f"[bold]Total ({len(blueprints)} BPs)[/bold]",
        f"[bold]{total_variables}[/bold]",
        f"[bold]{total_functions}[/bold]",
        f"[bold]{total_events}[/bold]",
        f"[bold]{total_nodes}[/bold]",
        ""
    )
    
    console.print(table)
    
    if blueprints:
        console.print("\n[bold]🔝 Most Complex Blueprints:[/bold]\n")
        
        top_table = Table(show_header=True)
        top_table. add_column("Blueprint", style="cyan")
        top_table.add_column("Nodes", style="red", justify="right")
        top_table.add_column("Complexity", style="yellow")
        
        for bp in blueprints[:5]: 
            rating, color, level = get_complexity_rating(bp["nodes"])
            top_table.add_row(bp["name"], str(bp["nodes"]), f"[{color}]{rating}[/{color}]")
        
        console.print(top_table)
    
    console.print(f"\n[bold green]✅ Analysis complete![/bold green]")
    console.print(f"[dim]Analyzed {len(blueprints)} blueprints with {total_nodes} total nodes[/dim]\n")


@blueprint_app.command("report")
def blueprint_report(
    path: str = typer.Argument(".", help="Path to scan for blueprints"),
    output: str = typer.Option(None, "--output", "-o", help="Save report to file (json/html)")
):
    """Generate a detailed complexity report for all Blueprints"""
    
    """Generate a detailed complexity report for all Blueprints"""
    
    console.print(Panel("[bold cyan]Generating Complexity Report...[/bold cyan]", border_style="cyan"))
    
    scan_path = Path(path)
    
    if not scan_path.exists():
        console.print(f"[red]❌ Path not found: {path}[/red]")
        return
    
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ". git", "Intermediate", "Saved", "__pycache__"]
    
    blueprints = []
    
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
    path: str = typer.Argument(".", help="Project root path"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all metrics")
):
    """Analyze performance metrics and detect bottlenecks."""
    console.print(create_branded_panel(
        "[bold cyan]Running Performance Analysis...[/bold cyan]",
        "Performance Profiler"
    ))
    
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
    path: str = typer.Argument(".", help="Project root path"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all shaders")
):
    """Analyze shader complexity and optimization opportunities."""
    console.print(create_branded_panel(
        "[bold cyan]Running Shader Analysis...[/bold cyan]",
        "Shader Analyzer"
    ))
    
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


# ═══════════════════════════════════════════════════════════════════════════════
# Configuration Commands - © 2026 gktrk363
# ═══════════════════════════════════════════════════════════════════════════════

@config_app.command("init")
def config_init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config")
):
    """Initialize .unrealmate.toml configuration file."""
    console.print(create_branded_panel(
        "[bold cyan]Initializing Configuration...[/bold cyan]",
        "Config Manager"
    ))
    
    if init_config(force=force):
        console.print("[green]✅ Configuration file created![/green]")
        console.print(f"[dim]Location: {Path.cwd() / '.unrealmate.toml'}[/dim]\n")
    else:
        console.print("[yellow]⚠️  Configuration already exists![/yellow]")
        console.print("[dim]Use --force to overwrite[/dim]\n")


@config_app.command("show")
def config_show():
    """Show current configuration."""
    console.print(create_branded_panel(
        "[bold cyan]Current Configuration[/bold cyan]",
        "Config Manager"
    ))
    
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
    key: str = typer.Argument(..., help="Config key (e.g., performance.cache_enabled)"),
    value: str = typer.Argument(..., help="Value to set")
):
    """Set a configuration value."""
    if set_config_value(key, value):
        console.print(f"[green]✅ Set {key} = {value}[/green]\n")
    else:
        console.print(f"[red]❌ Failed to set {key}[/red]\n")


@config_app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Config key (e.g., performance.cache_enabled)")
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
    path: str = typer.Argument(".", help="Project root path"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all assets")
):
    """Audit memory usage and identify optimization opportunities."""
    console.print(create_branded_panel(
        "[bold cyan]Running Memory Audit...[/bold cyan]",
        "Memory Auditor"
    ))
    
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
    path: str = typer.Argument(".", help="Project root path")
):
    """List all installed plugins."""
    console.print(create_branded_panel(
        "[bold cyan]Listing Plugins...[/bold cyan]",
        "Plugin Manager"
    ))
    
    project_path = Path(path)
    manager = PluginManager(project_path)
    
    manager.generate_report(console)
    
    if console:
        console.print(get_signature_footer())


@plugin_app.command("install")
def plugin_install(
    source: str = typer.Argument(..., help="Git URL or local path"),
    name: str = typer.Option(None, "--name", "-n", help="Plugin name"),
    path: str = typer.Option(".", "--path", "-p", help="Project root path")
):
    """Install a plugin from Git or local directory."""
    console.print(create_branded_panel(
        "[bold cyan]Installing Plugin...[/bold cyan]",
        "Plugin Manager"
    ))
    
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
    name: str = typer.Argument(..., help="Plugin name"),
    path: str = typer.Option(".", "--path", "-p", help="Project root path")
):
    """Enable a plugin in .uproject file."""
    project_path = Path(path)
    manager = PluginManager(project_path)
    
    if manager.enable_plugin(name):
        console.print(f"[green]✅ Enabled plugin: {name}[/green]\n")
    else:
        console.print(f"[red]❌ Failed to enable plugin: {name}[/red]\n")


@plugin_app.command("disable")
def plugin_disable(
    name: str = typer.Argument(..., help="Plugin name"),
    path: str = typer.Option(".", "--path", "-p", help="Project root path")
):
    """Disable a plugin in .uproject file."""
    project_path = Path(path)
    manager = PluginManager(project_path)
    
    if manager.disable_plugin(name):
        console.print(f"[green]✅ Disabled plugin: {name}[/green]\n")
    else:
        console.print(f"[red]❌ Failed to disable plugin: {name}[/red]\n")


@plugin_app.command("remove")
def plugin_remove(
    name: str = typer.Argument(..., help="Plugin name"),
    path: str = typer.Option(".", "--path", "-p", help="Project root path"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Remove a plugin from project."""
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
    platform: str = typer.Option("github", "--platform", "-p", help="CI platform (github/gitlab/jenkins)"),
    path: str = typer.Option(".", "--path", help="Project root path")
):
    """Generate CI/CD pipeline configuration."""
    console.print(create_branded_panel(
        f"[bold cyan]Generating {platform.upper()} CI/CD Configuration...[/bold cyan]",
        "CI/CD Generator"
    ))
    
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
    path: str = typer.Option(".", "--path", help="Project root path")
):
    """Show build information and recommendations."""
    console.print(create_branded_panel(
        "[bold cyan]Build Information[/bold cyan]",
        "Build Tools"
    ))
    
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
# © 2026 gktrk363 - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__": 
    app()