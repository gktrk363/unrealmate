import typer
import subprocess
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich. prompt import Confirm

app = typer.Typer(
    name="unrealmate",
    help="🎮 All-in-one CLI toolkit for Unreal Engine developers"
)
console = Console()

# Git komutları için alt grup
git_app = typer.Typer(help="🔧 Git helper commands")
app.add_typer(git_app, name="git")


def get_folder_size(path: Path) -> int:
    """Calculate total size of a folder in bytes"""
    total = 0
    try:
        for file in path.rglob("*"):
            if file.is_file():
                total += file.stat().st_size
    except (PermissionError, OSError):
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes >= 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    elif size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"


@app.command()
def version():
    """Show UnrealMate version"""
    console.print("[bold green]UnrealMate v0.1.0[/bold green] 🚀")
    console.print("[dim]https://github.com/gktrk363/unrealmate[/dim]")
    console.print("[dim]Created by:  gktrk363[/dim]")


@app.command()
def doctor():
    """Check your UE project health and configuration"""
    console.print("\n[bold cyan]🔍 Running UnrealMate Doctor.. .[/bold cyan]\n")
    
    checks = []
    score = 0
    max_score = 0
    
    # Check 1: . gitignore
    max_score += 25
    gitignore_path = Path(".gitignore")
    if gitignore_path. exists():
        checks.append(("✅", ". gitignore", "Found", "green"))
        score += 25
    else:
        checks.append(("❌", ".gitignore", "Missing - run 'unrealmate git init'", "red"))
    
    # Check 2: . uproject file (Unreal Project)
    max_score += 25
    uproject_files = list(Path(".").glob("*.uproject"))
    if uproject_files:
        checks.append(("✅", "UE Project", f"Found:  {uproject_files[0]. name}", "green"))
        score += 25
    else: 
        checks.append(("⚠️", "UE Project", "No .uproject file found", "yellow"))
    
    # Check 3: Git LFS
    max_score += 25
    gitattributes = Path(".gitattributes")
    if gitattributes.exists() and "lfs" in gitattributes. read_text().lower():
        checks.append(("✅", "Git LFS", "Configured", "green"))
        score += 25
    else:
        checks.append(("❌", "Git LFS", "Not configured - run 'unrealmate git lfs'", "red"))
    
    # Check 4: Large files check
    max_score += 25
    large_files = []
    for ext in ["*.uasset", "*.umap", "*.pak"]:
        large_files.extend(Path(". ").rglob(ext))
    
    if len(large_files) == 0:
        checks.append(("✅", "Large Files", "No large binary files in root", "green"))
        score += 25
    elif len(large_files) < 10:
        checks.append(("⚠️", "Large Files", f"{len(large_files)} binary files found", "yellow"))
        score += 15
    else:
        checks. append(("❌", "Large Files", f"{len(large_files)} binary files - consider LFS", "red"))
    
    # Display results table
    table = Table(title="Health Check Results", show_header=True)
    table.add_column("Status", style="bold", width=6)
    table.add_column("Check", style="bold")
    table.add_column("Details")
    
    for status, check, details, color in checks:
        table.add_row(status, check, f"[{color}]{details}[/{color}]")
    
    console.print(table)
    
    # Health score
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
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing . gitignore")
):
    """Generate . gitignore for Unreal Engine project"""
    
    target = Path(".") / ".gitignore"
    template_path = Path(__file__).parent / "templates" / "gitignore.template"
    
    if target. exists() and not force:
        console. print("[yellow]⚠️  .gitignore already exists![/yellow]")
        console.print("[dim]Use --force to overwrite[/dim]")
        return
    
    if not template_path.exists():
        console.print("[red]❌ Template file not found![/red]")
        console.print(f"[dim]Looking for:  {template_path}[/dim]")
        return
    
    content = template_path.read_text()
    target.write_text(content)
    console.print("[bold green]✅ . gitignore created successfully![/bold green]")
    console.print(f"[dim]Location: {target. absolute()}[/dim]")


@git_app.command("lfs")
def git_lfs(
    force: bool = typer. Option(False, "--force", "-f", help="Overwrite existing .gitattributes")
):
    """Setup Git LFS for Unreal Engine project"""
    
    console.print("\n[bold cyan]🔧 Setting up Git LFS...[/bold cyan]\n")
    
    # Check if git lfs is installed
    try:
        result = subprocess.run(["git", "lfs", "version"], capture_output=True, text=True)
        if result.returncode != 0:
            console.print("[red]❌ Git LFS is not installed![/red]")
            console.print("[dim]Install it from:  https://git-lfs.github.com[/dim]")
            return
        console.print(f"[green]✅ {result.stdout.strip()}[/green]")
    except FileNotFoundError:
        console. print("[red]❌ Git LFS is not installed![/red]")
        console.print("[dim]Install it from: https://git-lfs.github.com[/dim]")
        return
    
    # Create .gitattributes
    target = Path(".") / ".gitattributes"
    template_path = Path(__file__).parent / "templates" / "gitattributes.template"
    
    if target.exists() and not force:
        console.print("[yellow]⚠️  .gitattributes already exists![/yellow]")
        console.print("[dim]Use --force to overwrite[/dim]")
        return
    
    if not template_path.exists():
        console.print("[red]❌ Template file not found![/red]")
        console.print(f"[dim]Looking for: {template_path}[/dim]")
        return
    
    content = template_path.read_text()
    target.write_text(content)
    console.print("[bold green]✅ .gitattributes created successfully![/bold green]")
    
    # Initialize LFS
    try:
        subprocess.run(["git", "lfs", "install"], capture_output=True, text=True)
        console.print("[bold green]✅ Git LFS initialized![/bold green]")
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not run 'git lfs install': {e}[/yellow]")
    
    console.print(f"\n[dim]Location: {target.absolute()}[/dim]")
    console.print("\n[bold green]🎉 Git LFS setup complete![/bold green]")
    console.print("[dim]Large binary files will now be tracked by LFS[/dim]\n")


@git_app.command("clean")
def git_clean(
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be deleted without deleting"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Clean up unnecessary UE project files (Saved, Intermediate, etc.)"""
    
    console. print("\n[bold cyan]🧹 Scanning for unnecessary files...[/bold cyan]\n")
    
    # Folders to clean (only UE specific folders)
    cleanup_folders = [
        "Saved",
        "Intermediate",
        "DerivedDataCache",
        "Build",
        ". vs",
    ]
    
    # Folders to skip
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ". git"]
    
    found_folders = []
    total_size = 0
    
    # Scan for folders
    for folder_name in cleanup_folders:
        folder_path = Path(". ") / folder_name
        if folder_path.exists() and folder_path.is_dir():
            size = get_folder_size(folder_path)
            found_folders.append((folder_path, size))
            total_size += size
    
    # Scan for __pycache__ only in project folders (not venv)
    for pycache in Path(".").rglob("__pycache__"):
        if pycache.is_dir():
            # Skip if path contains any skip pattern
            path_str = str(pycache)
            if any(skip in path_str for skip in skip_patterns):
                continue
            size = get_folder_size(pycache)
            found_folders.append((pycache, size))
            total_size += size
    
    if not found_folders:
        console.print("[green]✨ No unnecessary files found!  Your project is clean.[/green]\n")
        return
    
    # Display found folders
    table = Table(title="Found Unnecessary Files", show_header=True)
    table.add_column("📁 Folder", style="cyan")
    table.add_column("Size", style="yellow", justify="right")
    
    for folder, size in found_folders: 
        table.add_row(str(folder), format_size(size))
    
    table.add_row("─" * 20, "─" * 10)
    table.add_row("[bold]Total[/bold]", f"[bold green]{format_size(total_size)}[/bold green]")
    
    console.print(table)
    console.print()
    
    if dry_run:
        console.print("[yellow]🔍 Dry run mode - no files were deleted[/yellow]\n")
        return
    
    # Confirm deletion
    if not yes:
        confirm = Confirm.ask(f"[bold]Do you want to delete these files and free {format_size(total_size)}?[/bold]")
        if not confirm:
            console.print("[yellow]❌ Cleanup cancelled[/yellow]\n")
            return
    
    # Delete folders
    deleted_count = 0
    deleted_size = 0
    
    for folder, size in found_folders:
        try:
            shutil.rmtree(folder)
            deleted_count += 1
            deleted_size += size
            console.print(f"[green]✅ Deleted:  {folder}[/green]")
        except Exception as e: 
            console.print(f"[red]❌ Failed to delete {folder}: {e}[/red]")
    
    console.print(f"\n[bold green]🎉 Cleanup complete![/bold green]")
    console.print(f"[dim]Deleted {deleted_count} folders, freed {format_size(deleted_size)}[/dim]\n")


if __name__ == "__main__": 
    app()