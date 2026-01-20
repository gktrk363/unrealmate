import typer
from pathlib import Path
from rich.console import Console

app = typer. Typer(
    name="unrealmate",
    help="🎮 All-in-one CLI toolkit for Unreal Engine developers"
)
console = Console()

# Git komutları için alt grup
git_app = typer. Typer(help="🔧 Git helper commands")
app.add_typer(git_app, name="git")

@app.command()
def version():
    """Show UnrealMate version"""
    console.print("[bold green]UnrealMate v0.1.0[/bold green] 🚀")

@app.command()
def doctor():
    """Check your UE project for issues"""
    console. print("[bold]🔍 Running UnrealMate Doctor.. .[/bold]")
    console.print("[yellow]Coming soon![/yellow]")

@git_app.command("init")
def git_init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing . gitignore")
):
    """Generate . gitignore for Unreal Engine project"""
    
    target = Path(".") / ".gitignore"
    template_path = Path(__file__).parent / "templates" / "gitignore.template"
    
    # Check if .gitignore already exists
    if target.exists() and not force:
        console.print("[yellow]⚠️  . gitignore already exists![/yellow]")
        console.print("[dim]Use --force to overwrite[/dim]")
        return
    
    # Read template
    if not template_path.exists():
        console.print("[red]❌ Template file not found![/red]")
        console.print(f"[dim]Looking for: {template_path}[/dim]")
        return
    
    content = template_path. read_text()
    
    # Write . gitignore
    target.write_text(content)
    console.print("[bold green]✅ .gitignore created successfully![/bold green]")
    console.print(f"[dim]Location: {target. absolute()}[/dim]")

if __name__ == "__main__":
    app()