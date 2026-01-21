import typer
import subprocess
import shutil
import hashlib
from pathlib import Path
from collections import defaultdict
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

# Asset komutları için alt grup
asset_app = typer.Typer(help="📦 Asset management commands")
app.add_typer(asset_app, name="asset")


def get_folder_size(path: Path) -> int:
    """Calculate total size of a folder in bytes"""
    total = 0
    try:
        for file in path. rglob("*"):
            if file.is_file():
                total += file.stat().st_size
    except (PermissionError, OSError):
        pass
    return total


def get_file_size(path: Path) -> int:
    """Get file size in bytes"""
    try:
        return path.stat().st_size
    except (PermissionError, OSError):
        return 0


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
    
    max_score += 25
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        checks.append(("✅", ". gitignore", "Found", "green"))
        score += 25
    else:
        checks.append(("❌", ".gitignore", "Missing - run 'unrealmate git init'", "red"))
    
    max_score += 25
    uproject_files = list(Path(". ").glob("*.uproject"))
    if uproject_files:
        checks.append(("✅", "UE Project", f"Found:  {uproject_files[0].name}", "green"))
        score += 25
    else:
        checks.append(("⚠️", "UE Project", "No . uproject file found", "yellow"))
    
    max_score += 25
    gitattributes = Path(".gitattributes")
    if gitattributes.exists() and "lfs" in gitattributes. read_text().lower():
        checks.append(("✅", "Git LFS", "Configured", "green"))
        score += 25
    else:
        checks.append(("❌", "Git LFS", "Not configured - run 'unrealmate git lfs'", "red"))
    
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
    
    console. print(f"\n{emoji} [bold {color}]Health Score: {percentage}/100[/bold {color}]\n")


@git_app.command("init")
def git_init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing . gitignore")
):
    """Generate .gitignore for Unreal Engine project"""
    
    target = Path(".") / ".gitignore"
    template_path = Path(__file__).parent / "templates" / "gitignore.template"
    
    if target.exists() and not force:
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
    dry_run: bool = typer. Option(False, "--dry-run", "-d", help="Show what would be deleted without deleting"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Clean up unnecessary UE project files (Saved, Intermediate, etc.)"""
    
    console. print("\n[bold cyan]🧹 Scanning for unnecessary files...[/bold cyan]\n")
    
    cleanup_folders = [
        "Saved",
        "Intermediate",
        "DerivedDataCache",
        "Build",
        ". vs",
    ]
    
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ". git"]
    
    found_folders = []
    total_size = 0
    
    for folder_name in cleanup_folders:
        folder_path = Path(". ") / folder_name
        if folder_path.exists() and folder_path.is_dir():
            size = get_folder_size(folder_path)
            found_folders.append((folder_path, size))
            total_size += size
    
    for pycache in Path(".").rglob("__pycache__"):
        if pycache. is_dir():
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
        table.add_row(str(folder), format_size(size))
    
    table.add_row("─" * 20, "─" * 10)
    table.add_row("[bold]Total[/bold]", f"[bold green]{format_size(total_size)}[/bold green]")
    
    console.print(table)
    console.print()
    
    if dry_run:
        console.print("[yellow]🔍 Dry run mode - no files were deleted[/yellow]\n")
        return
    
    if not yes:
        confirm = Confirm.ask(f"[bold]Do you want to delete these files and free {format_size(total_size)}? [/bold]")
        if not confirm:
            console.print("[yellow]❌ Cleanup cancelled[/yellow]\n")
            return
    
    deleted_count = 0
    deleted_size = 0
    
    for folder, size in found_folders:
        try:
            shutil.rmtree(folder)
            deleted_count += 1
            deleted_size += size
            console.print(f"[green]✅ Deleted: {folder}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to delete {folder}: {e}[/red]")
    
    console.print(f"\n[bold green]🎉 Cleanup complete![/bold green]")
    console.print(f"[dim]Deleted {deleted_count} folders, freed {format_size(deleted_size)}[/dim]\n")


@asset_app.command("scan")
def asset_scan(
    path: str = typer.Argument(".", help="Path to scan for assets"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all assets (not just summary)")
):
    """Scan and report all assets in your UE project"""
    
    console.print("\n[bold cyan]📦 Scanning for assets...[/bold cyan]\n")
    
    scan_path = Path(path)
    
    if not scan_path.exists():
        console.print(f"[red]❌ Path not found: {path}[/red]")
        return
    
    asset_types = {
        "Blueprints": ["*. uasset"],
        "Maps": ["*.umap"],
        "Textures": ["*.png", "*.tga", "*.psd", "*.exr", "*.hdr"],
        "Audio": ["*.wav", "*.mp3", "*.ogg"],
        "3D Models": ["*.fbx", "*.obj"],
        "Materials": ["*.uasset"],
        "Videos": ["*.mp4", "*. mov", "*.avi"],
    }
    
    results = {}
    all_assets = []
    total_size = 0
    total_count = 0
    
    skip_patterns = ["venv", ".venv", "site-packages", "node_modules", ".git", "Intermediate", "Saved"]
    
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
                "count":  len(category_files),
                "size": category_size,
                "files": category_files
            }
            total_count += len(category_files)
            total_size += category_size
    
    if not results:
        console.print("[yellow]⚠️ No assets found in this directory[/yellow]\n")
        return
    
    table = Table(title="Asset Summary", show_header=True)
    table.add_column("📁 Category", style="cyan")
    table.add_column("Count", style="magenta", justify="right")
    table.add_column("Size", style="yellow", justify="right")
    
    for category, data in results.items():
        table.add_row(category, str(data["count"]), format_size(data["size"]))
    
    table.add_row("─" * 15, "─" * 5, "─" * 10)
    table.add_row("[bold]Total[/bold]", f"[bold]{total_count}[/bold]", f"[bold green]{format_size(total_size)}[/bold green]")
    
    console.print(table)
    
    if show_all and all_assets:
        console.print("\n[bold]All Assets:[/bold]\n")
        
        detail_table = Table(show_header=True)
        detail_table.add_column("File", style="cyan")
        detail_table.add_column("Category", style="magenta")
        detail_table.add_column("Size", style="yellow", justify="right")
        
        all_assets.sort(key=lambda x: x[1], reverse=True)
        
        for file, size, category in all_assets[: 50]:
            detail_table.add_row(str(file), category, format_size(size))
        
        if len(all_assets) > 50:
            detail_table. add_row(f"... and {len(all_assets) - 50} more", "", "")
        
        console.print(detail_table)
    
    if all_assets:
        console.print("\n[bold]🔝 Top 5 Largest Assets:[/bold]\n")
        
        top_table = Table(show_header=True)
        top_table.add_column("File", style="cyan")
        top_table.add_column("Size", style="yellow", justify="right")
        
        all_assets.sort(key=lambda x: x[1], reverse=True)
        
        for file, size, category in all_assets[:5]:
            top_table.add_row(str(file), format_size(size))
        
        console.print(top_table)
    
    console.print(f"\n[bold green]✅ Scan complete![/bold green]")
    console.print(f"[dim]Found {total_count} assets totaling {format_size(total_size)}[/dim]\n")


@asset_app.command("organize")
def asset_organize(
    path: str = typer. Argument(".", help="Path to organize assets in"),
    dry_run: bool = typer. Option(False, "--dry-run", "-d", help="Show what would be moved without moving"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Auto-organize assets into proper folder structure"""
    
    console. print("\n[bold cyan]📦 Analyzing assets for organization...[/bold cyan]\n")
    
    scan_path = Path(path)
    
    if not scan_path.exists():
        console.print(f"[red]❌ Path not found: {path}[/red]")
        return
    
    organize_rules = {
        "Textures": {
            "extensions": [".png", ".tga", ".psd", ".exr", ".hdr", ".jpg", ".jpeg"],
            "folder": "Textures"
        },
        "Audio": {
            "extensions": [".wav", ".mp3", ". ogg", ".flac"],
            "folder": "Audio"
        },
        "Models": {
            "extensions": [".fbx", ". obj", ".blend", ".3ds", ". dae"],
            "folder": "Models"
        },
        "Videos": {
            "extensions": [".mp4", ".mov", ". avi", ".mkv", ".webm"],
            "folder": "Videos"
        },
        "Fonts": {
            "extensions": [".ttf", ".otf", ".woff", ".woff2"],
            "folder": "Fonts"
        },
        "Data": {
            "extensions": [".json", ".csv", ".xml", ".ini"],
            "folder": "Data"
        },
    }
    
    skip_patterns = ["venv", ". venv", "site-packages", "node_modules", ".git", "Intermediate", "Saved", "__pycache__"]
    
    files_to_move = []
    
    for category, rules in organize_rules.items():
        target_folder = scan_path / rules["folder"]
        
        for ext in rules["extensions"]: 
            for file in scan_path. rglob(f"*{ext}"):
                if any(skip in str(file) for skip in skip_patterns):
                    continue
                
                if rules["folder"] in str(file. parent):
                    continue
                
                if file.parent.name. lower() == rules["folder"].lower():
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
        table.add_row(str(source. name), "→", str(dest.parent.name) + "/", category)
    
    console.print(table)
    console.print(f"\n[bold]Total:  {len(files_to_move)} files to organize[/bold]\n")
    
    if dry_run:
        console.print("[yellow]🔍 Dry run mode - no files were moved[/yellow]\n")
        return
    
    if not yes:
        confirm = Confirm.ask(f"[bold]Do you want to organize {len(files_to_move)} files?[/bold]")
        if not confirm:
            console.print("[yellow]❌ Organization cancelled[/yellow]\n")
            return
    
    moved_count = 0
    error_count = 0
    
    for source, dest, category in files_to_move:
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
            console.print(f"[green]✅ Moved: {source. name} → {dest.parent.name}/[/green]")
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
    """Find duplicate assets in your UE project"""
    
    console.print("\n[bold cyan]🔍 Scanning for duplicate assets...[/bold cyan]\n")
    
    scan_path = Path(path)
    
    if not scan_path.exists():
        console.print(f"[red]❌ Path not found: {path}[/red]")
        return
    
    asset_extensions = [
        ".png", ".tga", ".psd", ".exr", ".hdr", ".jpg", ".jpeg",
        ".wav", ".mp3", ".ogg", ".flac",
        ".fbx", ".obj", ".blend",
        ".mp4", ".mov", ".avi",
        ".uasset", ".umap",
        ".ttf", ".otf",
    ]
    
    skip_patterns = ["venv", ". venv", "site-packages", "node_modules", ".git", "Intermediate", "Saved", "__pycache__"]
    
    file_groups = defaultdict(list)
    
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
            file_groups[file.name. lower()].append(file)
    
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
        
        console.print(f"[bold cyan]📁 {files[0].name}[/bold cyan] [dim]({len(files)} copies, wasting {format_size(wasted)})[/dim]")
        
        for file in files:
            console.print(f"   [dim]→[/dim] {file}")
        
        console.print()
    
    console.print("─" * 50)
    console.print(f"\n[bold yellow]⚠️ Summary:[/bold yellow]")
    console.print(f"   [bold]{len(duplicates)}[/bold] duplicate groups")
    console.print(f"   [bold]{total_duplicate_files}[/bold] extra files")
    console.print(f"   [bold red]{format_size(total_wasted)}[/bold red] wasted space\n")
    
    console.print("[dim]Tip: Remove duplicate files to save space and avoid confusion![/dim]\n")


if __name__ == "__main__": 
    app()