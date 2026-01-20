import typer
from rich.console import Console

app = typer.Typer(
    name="unrealmate",
    help="🎮 All-in-one CLI toolkit for Unreal Engine developers"
)
console = Console()

@app.command()
def version():
    """Show UnrealMate version"""
    console.print("[bold green]UnrealMate v0.1.0[/bold green] 🚀")

@app.command()
def doctor():
    """Check your UE project for issues"""
    console.print("[bold]🔍 Running UnrealMate Doctor...[/bold]")
    console.print("[yellow]Coming soon![/yellow]")

@app.command()
def init():
    """Initialize UnrealMate in your UE project"""
    console.print("[bold green]✅ UnrealMate initialized![/bold green]")

if __name__ == "__main__": 
    app()