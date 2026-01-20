import typer
from pathlib import Path
from rich.console import Console
from rich. table import Table

app = typer.Typer(
    name="unrealmate",
    help="🎮 All-in-one CLI toolkit for Unreal Engine developers"
)
console = Console()

# Git komutları için alt grup
git_app = typer.Typer(help="🔧 Git helper commands")
app.add_typer(git_app, name="git")


@app.command()
def version():
    """Show UnrealMate version"""
    console.print("[bold green]UnrealMate v0.1.0[/bold green] 🚀")


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
    if gitignore_path.exists():
        checks.append(("✅", ". gitignore", "Found", "green"))
        score += 25
    else:
        checks. append(("❌", ".gitignore", "Missing - run 'unrealmate git init'", "red"))
    
    # Check 2: . uproject file (Unreal Project)
    max_score += 25
    uproject_files = list(Path(". ").glob("*.uproject"))
    if uproject_files:
        checks.append(("✅", "UE Project", f"Found:  {uproject_files[0].name}", "green"))
        score += 25
    else:
        checks.append(("⚠️", "UE Project", "No .uproject file found", "yellow"))
    
    # Check 3: Git LFS
    max_score += 25
    gitattributes = Path(".gitattributes")
    if gitattributes.exists() and "lfs" in gitattributes.read_text().lower():
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
    
    console. print(f"\n{emoji} [bold {color}]Health Score: {percentage}/100[/bold {color}]\n")


@git_app.command("init")
def git_init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing . gitignore")
):
    """Generate .gitignore for Unreal Engine project"""
    
    target = Path(".") / ".gitignore"
    template_path = Path(__file__).parent / "templates" / "gitignore.template"
    
    # Check if . gitignore already exists
    if target.exists() and not force:
        console. print("[yellow]⚠️  .gitignore already exists![/yellow]")
        console.print("[dim]Use --force to overwrite[/dim]")
        return
    
    # Read template
    if not template_path.exists():
        console.print("[red]❌ Template file not found![/red]")
        console.print(f"[dim]Looking for:  {template_path}[/dim]")
        return
    
    content = template_path.read_text()
    
    # Write .gitignore
    target.write_text(content)
    console.print("[bold green]✅ .gitignore created successfully![/bold green]")
    console.print(f"[dim]Location: {target. absolute()}[/dim]")


if __name__ == "__main__": 
    app()