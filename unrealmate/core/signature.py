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

# Custom color theme - Standard Terminal Colors
SIGNATURE_THEME = Theme({
    "signature.primary": "bright_green bold",      # Lime Green
    "signature.secondary": "bright_green",         # Lime Green (Unified)
    "signature.accent": "bright_green",            # Lime Green (Unified)
    "signature.text": "white",                     # White
    "signature.dim": "bright_black",               # Dark Gray
})


def get_ascii_banner(version: str = "1.0.9") -> str:
    """
    Returns the UnrealMate ASCII art banner with developer signature.
    
    Args:
        version: Version string to display
    
    Returns:
        str: Multi-line ASCII art banner
        
    Example:
        >>> print(get_ascii_banner())
        # Displays branded ASCII art
    """
    lines = [
        "",
        "    ═══════════════════════════════════════════════════════════════",
        "    ",
        "           ██╗   ██╗███╗   ██╗██████╗ ███████╗ █████╗ ██╗     ",
        "           ██║   ██║████╗  ██║██╔══██╗██╔════╝██╔══██╗██║     ",
        "           ██║   ██║██╔██╗ ██║██████╔╝█████╗  ███████║██║     ",
        "           ██║   ██║██║╚██╗██║██╔══██╗██╔══╝  ██╔══██║██║     ",
        "           ╚██████╔╝██║ ╚████║██║  ██║███████╗██║  ██║███████╗",
        "            ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝",
        "    ",
        "                  ███╗   ███╗ █████╗ ████████╗███████╗",
        "                  ████╗ ████║██╔══██╗╚══██╔══╝██╔════╝",
        "                  ██╔████╔██║███████║   ██║   █████╗  ",
        "                  ██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  ",
        "                  ██║ ╚═╝ ██║██║  ██║   ██║   ███████╗",
        "                  ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝",
        "    ",
        "                All-in-One CLI Toolkit for Unreal Engine",
        "    ",
        "                      ⚡ Crafted by gktrk363 ⚡",
        "               Version: v" + version + " │ GitHub: gktrk363/unrealmate",
        "    ",
        "    ═══════════════════════════════════════════════════════════════",
        "",
    ]
    return "\n".join(lines)


def get_compact_banner(version: str = "1.0.6") -> str:
    """
    Returns a compact version of the banner with version info.
    
    Args:
        version: Version string to display
    
    Returns:
        str: Compact ASCII art banner with version
    """
    # Build banner line by line to ensure version is included
    lines = [
        "",
        "    ═══════════════════════════════════════════════════════════════",
        "    ",
        "           ██╗   ██╗███╗   ██╗██████╗ ███████╗ █████╗ ██╗     ",
        "           ██║   ██║████╗  ██║██╔══██╗██╔════╝██╔══██╗██║     ",
        "           ██║   ██║██╔██╗ ██║██████╔╝█████╗  ███████║██║     ",
        "           ██║   ██║██║╚██╗██║██╔══██╗██╔══╝  ██╔══██║██║     ",
        "           ╚██████╔╝██║ ╚████║██║  ██║███████╗██║  ██║███████╗",
        "            ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝",
        "    ",
        "                  ███╗   ███╗ █████╗ ████████╗███████╗",
        "                  ████╗ ████║██╔══██╗╚══██╔══╝██╔════╝",
        "                  ██╔████╔██║███████║   ██║   █████╗  ",
        "                  ██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  ",
        "                  ██║ ╚═╝ ██║██║  ██║   ██║   ███████╗",
        "                  ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝",
        "    ",
        "                All-in-One CLI Toolkit for Unreal Engine",
        "    ",
        "                      ⚡ Crafted by gktrk363 ⚡",
        "               Version: v" + version + " │ GitHub: gktrk363/unrealmate",
        "    ",
        "    ═══════════════════════════════════════════════════════════════",
        "",
    ]
    return "\n".join(lines)


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
    version: str = "1.0.9"
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
    
    # Get appropriate banner (both get version parameter now)
    if compact:
        banner_text = get_compact_banner(version)
    else:
        banner_text = get_ascii_banner(version)  # Now pass version here too!
    
    # Create styled text
    styled_banner = Text()
    for line in banner_text.split('\n'):
        if 'Crafted by' in line:
            # Split line for mixed styling: Gray "Crafted by" + Green Name + Green Bolts
            parts = line.split('Crafted by')
            before_text = parts[0] + "Crafted by "
            
            # Reconstruct with mixed styles
            # Part 1: "                      ⚡ Crafted by " (Gray/Dim)
            styled_banner.append(before_text.replace('⚡', ''), style="signature.dim")
            
            # Add the first bolt in green if it was stripped (it's at the start of the trimmed string usually)
            if '⚡' in parts[0]: 
                 # We need to be careful with exact reconstruction.
                 # Let's simplify: The line is "                      ⚡ Crafted by gktrk363 ⚡"
                 # We want: ⚡ (Green) " Crafted by " (Gray) "gktrk363" (Green) " ⚡" (Green)
                 
                 # Manual construction for this specific line for perfect control
                 styled_banner.append("                      ", style="signature.text")
                 styled_banner.append("⚡", style="signature.accent")
                 styled_banner.append(" Crafted by ", style="signature.dim")
                 styled_banner.append("gktrk363", style="signature.primary")
                 styled_banner.append(" ⚡", style="signature.accent")
            else:
                 # Fallback if format changes
                 styled_banner.append(line, style="signature.dim")

        elif 'UnrealMate' in line or 'UNREAL' in line or '██' in line:
            # Highlight product name in green
            styled_banner.append(line, style="signature.primary")
        elif 'Version:' in line or 'GitHub:' in line:
            # Highlight version line in dim
            styled_banner.append(line, style="signature.dim")
        else:
            styled_banner.append(line, style="signature.text")
        styled_banner.append('\n')
    
    console.print(styled_banner)
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


# © 2026 gktrk363 - Crafted with passion for Unreal Engine developers
