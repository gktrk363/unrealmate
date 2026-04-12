"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           UnrealMate Signature System                        ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  Purpose: Personal branding and signature utilities                          ║
║  Created: 2026-01-23                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Personal signature and branding system for UnrealMate.
Provides ASCII art banners, code headers, and custom theming.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from datetime import datetime
from typing import Optional
import sys

# Custom color theme - Standard Terminal Colors
SIGNATURE_THEME = Theme({
    "signature.primary": "cyan",                   # Soft Cyan
    "signature.secondary": "cyan",                 # Soft Cyan
    "signature.accent": "dim",                     # Dim Gray
    "signature.text": "white",                     # White
    "signature.dim": "bright_black",               # Dark Gray
})


def _pipe_char() -> str:
    """Return an ASCII-safe pipe separator when the visuals module is in ASCII mode."""
    try:
        from unrealmate.core.visuals import ASCII_MODE
        return "|" if ASCII_MODE else "│"
    except ImportError:
        return "│"


def get_ascii_banner(version: str = "1.0.10") -> str:
    """Returns the UnrealMate minimal banner with developer signature."""
    return f"\n  UnrealMate v{version} {_pipe_char()} CLI Toolkit for Unreal Engine\n"

def get_compact_banner(version: str = "1.0.6") -> str:
    """Returns a compact version of the banner."""
    return f"\n  UnrealMate v{version} {_pipe_char()} Crafted by G & E ZYNTH\n"


def get_code_header(
    filename: str,
    purpose: str,
    author: str = "G & E ZYNTH",
    created_date: Optional[str] = None
) -> str:
    """
    Generates a standardized code file header with developer signature.
    
    Args:
        filename: Name of the file
        purpose: Brief description of file's purpose
        author: Developer name (default: G & E ZYNTH)
        created_date: Creation date (default: current date)
        
    Returns:
        str: Formatted code header
        
    Example:
        >>> header = get_code_header("scanner.py", "Asset scanning utilities")
        >>> print(header)
    """
    if created_date is None:
        created_date = datetime.now().strftime("%Y-%m-%d")
    
    header = f'''"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              UnrealMate - {filename:<30} ║
║                                                                              ║
║  Author: {author:<66} ║
║  Purpose: {purpose:<64} ║
║  Created: {created_date:<64} ║
╚══════════════════════════════════════════════════════════════════════════════╝

{purpose}

© {datetime.now().year} {author} - Crafted with passion for Unreal Engine developers
"""
'''
    return header


def print_signature_banner(
    console: Optional[Console] = None,
    compact: bool = False,
    show_version: bool = True,
    version: str = "1.0.10"
) -> None:
    """Prints the minimal branded banner to console with subtle styling."""
    if console is None:
        console = Console(theme=SIGNATURE_THEME)
    
    styled_banner = Text()
    styled_banner.append("\n  ")
    styled_banner.append("Unreal", style="bold white")
    styled_banner.append("Mate", style="bold cyan")
    styled_banner.append(f" v{version} ", style="bold white")
    
    sep = _pipe_char()
    if compact:
        styled_banner.append(f"{sep} Crafted by G & E ZYNTH\n", style="dim")
    else:
        styled_banner.append(f"{sep} CLI Toolkit for Unreal Engine\n", style="dim")
        
    console.print(styled_banner)


def get_signature_footer() -> str:
    """
    Returns a footer signature for command outputs.
    
    Returns:
        str: Footer signature text
    """
    return ""


def create_branded_panel(
    content: str,
    title: str,
    console: Optional[Console] = None,
    border_style: str = "signature.primary"
) -> Panel:
    """
    Creates a Rich Panel with branded styling.
    
    Args:
        content: Panel content
        title: Panel title
        console: Rich Console instance
        border_style: Border color style
        
    Returns:
        Panel: Styled Rich Panel
        
    Example:
        >>> panel = create_branded_panel("Hello World", "Greeting")
        >>> console.print(panel)
    """
    if console is None:
        console = Console(theme=SIGNATURE_THEME)
    
    return Panel(
        content,
        title=f"[signature.accent]⚡[/] {title} [signature.accent]⚡[/]",
        border_style=border_style,
        padding=(1, 2)
    )


def get_signature_console() -> Console:
    """
    Returns a Rich Console instance with signature theme applied.
    
    Returns:
        Console: Themed Rich Console
        
    Example:
        >>> console = get_signature_console()
        >>> console.print("Hello", style="signature.primary")
    """
    encoding = getattr(sys.stdout, "encoding", None)
    unicode_ok = bool(encoding and "utf" in encoding.lower())
    return Console(theme=SIGNATURE_THEME, emoji=unicode_ok, safe_box=not unicode_ok)


# Developer signature constant
DEVELOPER_SIGNATURE = "G & E ZYNTH"
DEVELOPER_GITHUB = "https://github.com/gktrk363"
DEVELOPER_PROJECT = "https://github.com/gktrk363/unrealmate"

# Copyright notice
COPYRIGHT_NOTICE = f"© {datetime.now().year} {DEVELOPER_SIGNATURE} - All rights reserved"


if __name__ == "__main__":
    # Demo the signature system
    console = get_signature_console()
    
    console.print("\n[signature.primary]Full Banner:[/]\n")
    print_signature_banner(console, compact=False)
    
    console.print("\n[signature.primary]Compact Banner:[/]\n")
    print_signature_banner(console, compact=True)
    
    console.print("\n[signature.primary]Code Header Example:[/]\n")
    header = get_code_header("example.py", "Example file for demonstration")
    console.print(header)
    
    console.print("\n[signature.primary]Branded Panel Example:[/]\n")
    panel = create_branded_panel(
        "This is a test panel with branded styling!",
        "Test Panel",
        console
    )
    console.print(panel)
    
    console.print(get_signature_footer())


# © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers

