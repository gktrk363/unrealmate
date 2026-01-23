"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           UnrealMate Signature System                        ║
║                                                                              ║
║  Author: gktrk363                                                           ║
║  Purpose: Personal branding and signature utilities                         ║
║  Created: 2026-01-23                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Personal signature and branding system for UnrealMate.
Provides ASCII art banners, code headers, and custom theming.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from datetime import datetime
from typing import Optional

# Custom color theme - Cyan & Magenta gradient
SIGNATURE_THEME = Theme({
    "signature.primary": "#00D9FF bold",      # Cyan
    "signature.secondary": "#FF006E bold",    # Magenta
    "signature.accent": "#FFD700",            # Gold
    "signature.text": "#FFFFFF",              # White
    "signature.dim": "#888888",               # Gray
})


def get_ascii_banner() -> str:
    """
    Returns the UnrealMate ASCII art banner with developer signature.
    
    Returns:
        str: Multi-line ASCII art banner
        
    Example:
        >>> print(get_ascii_banner())
        # Displays branded ASCII art
    """
    banner = """
    ═══════════════════════════════════════════════════════════════
    
         _   _ _   _ ____  _____    _    _     __  __    _  _____ _____ 
        | | | | \\ | |  _ \\| ____|  / \\  | |   |  \\/  |  / \\|_   _| ____|
        | | | |  \\| | |_) |  _|   / _ \\ | |   | |\\/| | / _ \\ | | |  _|  
        | |_| | |\\  |  _ <| |___ / ___ \\| |___| |  | |/ ___ \\| | | |___ 
         \\___/|_| \\_|_| \\_\\_____/_/   \\_\\_____|_|  |_/_/   \\_\\_| |_____|
    
              All-in-One CLI Toolkit for Unreal Engine
    
                      ⚡ Crafted by gktrk363 ⚡
    
    ═══════════════════════════════════════════════════════════════
    """
    return banner


def get_compact_banner() -> str:
    """
    Returns a compact version of the banner for smaller displays.
    
    Returns:
        str: Compact ASCII art banner
    """
    banner = """
    ════════════════════════════════════════════════════════
    
      🎮  U N R E A L M A T E
    
      All-in-One CLI Toolkit for Unreal Engine
      ⚡ Crafted by gktrk363
    
    ════════════════════════════════════════════════════════
    """
    return banner


def get_code_header(
    filename: str,
    purpose: str,
    author: str = "gktrk363",
    created_date: Optional[str] = None
) -> str:
    """
    Generates a standardized code file header with developer signature.
    
    Args:
        filename: Name of the file
        purpose: Brief description of file's purpose
        author: Developer name (default: gktrk363)
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
    version: str = "0.1.10"
) -> None:
    """
    Prints the branded banner to console with custom styling.
    
    Args:
        console: Rich Console instance (creates new if None)
        compact: Use compact banner for smaller displays
        show_version: Display version information
        version: Version string to display
        
    Example:
        >>> print_signature_banner()
        # Displays full banner with colors
    """
    if console is None:
        console = Console(theme=SIGNATURE_THEME)
    
    # Auto-detect terminal width and force compact if too narrow
    terminal_width = console.width
    if terminal_width < 80 and not compact:
        compact = True  # Force compact mode for narrow terminals
    
    # Get appropriate banner
    banner_text = get_compact_banner() if compact else get_ascii_banner()
    
    # Create styled text
    styled_banner = Text()
    for line in banner_text.split('\n'):
        if 'gktrk363' in line:
            # Highlight developer name in magenta
            styled_banner.append(line, style="signature.secondary")
        elif 'UnrealMate' in line or 'UNREAL' in line:
            # Highlight product name in cyan
            styled_banner.append(line, style="signature.primary")
        elif '⚡' in line or '🎮' in line:
            # Highlight emojis in gold
            styled_banner.append(line, style="signature.accent")
        else:
            styled_banner.append(line, style="signature.text")
        styled_banner.append('\n')
    
    console.print(styled_banner)
    
    # Add version info if requested - properly aligned and centered
    if show_version:
        console.print()  # Empty line for spacing
        
        # Create centered version text
        version_line = f"Version: v{version} | GitHub: github.com/gktrk363/unrealmate"
        
        # Calculate padding for centering
        padding = max(0, (terminal_width - len(version_line)) // 2)
        
        version_text = Text()
        version_text.append(" " * padding)
        version_text.append("Version: ", style="signature.dim")
        version_text.append(f"v{version}", style="signature.primary bold")
        version_text.append(" | ", style="signature.dim")
        version_text.append("GitHub: ", style="signature.dim")
        version_text.append("github.com/gktrk363/unrealmate", style="signature.accent")
        
        console.print(version_text)
        console.print()  # Empty line after


def get_signature_footer() -> str:
    """
    Returns a footer signature for command outputs.
    
    Returns:
        str: Footer signature text
    """
    return "\n✨ Powered by UnrealMate | Crafted by gktrk363 ✨\n"


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
    return Console(theme=SIGNATURE_THEME)


# Developer signature constant
DEVELOPER_SIGNATURE = "gktrk363"
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
