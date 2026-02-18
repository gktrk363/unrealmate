"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Visual Enhancements                          ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Visual enhancements and CLI aesthetics                             ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Advanced visual components, animations, and branding.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import random
import time
from datetime import datetime
from typing import Any, Optional

from rich.align import Align
from rich.box import DOUBLE, HEAVY, MINIMAL, ROUNDED, SQUARE, Box
from rich.columns import Columns
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM BOX STYLES
# ═══════════════════════════════════════════════════════════════════════════════


# Use built-in box styles
UE_BOX = DOUBLE
GAMING_BOX = HEAVY


# ═══════════════════════════════════════════════════════════════════════════════
# STATUS ICONS & EMOJIS
# ═══════════════════════════════════════════════════════════════════════════════


class StatusIcons:
    """Status icons for CLI output."""
    
    # Basic status
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    PENDING = "⏳"
    
    # Actions
    ROCKET = "🚀"
    CHECK = "✓"
    CROSS = "✗"
    ARROW = "→"
    STAR = "⭐"
    FIRE = "🔥"
    SPARKLES = "✨"
    
    # Objects
    FOLDER = "📁"
    FILE = "📄"
    PACKAGE = "📦"
    GEAR = "⚙️"
    WRENCH = "🔧"
    HAMMER = "🔨"
    
    # Gaming/UE
    GAMEPAD = "🎮"
    JOYSTICK = "🕹️"
    BLUEPRINT = "📊"
    LIGHTNING = "⚡"
    TARGET = "🎯"
    TROPHY = "🏆"
    
    # Code
    BUG = "🐛"
    CODE = "💻"
    TERMINAL = "💻"
    GIT = "📝"
    
    @classmethod
    def get_status(cls, success: bool) -> str:
        return cls.SUCCESS if success else cls.ERROR


# ═══════════════════════════════════════════════════════════════════════════════
# GRADIENT TEXT
# ═══════════════════════════════════════════════════════════════════════════════


def gradient_text(text: str, colors: list[str] | None = None) -> Text:
    """
    Create gradient colored text.
    
    Args:
        text: Text to colorize
        colors: List of colors for gradient (default: lime green gradient)
    
    Returns:
        Rich Text object with gradient colors
    """
    if colors is None:
        colors = ["#00D9FF", "#FF006E", "cyan", "magenta"]
    
    result = Text()
    color_count = len(colors)
    
    for i, char in enumerate(text):
        color = colors[i % color_count]
        result.append(char, style=color)
    
    return result


def rainbow_text(text: str) -> Text:
    """Create rainbow colored text."""
    colors = ["red", "orange1", "yellow", "green", "cyan", "blue", "magenta"]
    return gradient_text(text, colors)


# ═══════════════════════════════════════════════════════════════════════════════
# FANCY BOXES & PANELS
# ═══════════════════════════════════════════════════════════════════════════════


def create_header_box(
    title: str,
    subtitle: str = "",
    style: str = "bright_green",
) -> Panel:
    """
    Create a fancy header box with title and subtitle.
    
    Args:
        title: Main title text
        subtitle: Optional subtitle
        style: Color style for the box
    
    Returns:
        Rich Panel object
    """
    content = Text()
    content.append(f"  {title}  ", style=f"bold {style}")
    
    if subtitle:
        content.append("\n")
        content.append(f"  {subtitle}  ", style="dim")
    
    return Panel(
        Align.center(content),
        box=DOUBLE,
        border_style=style,
        padding=(1, 2),
    )


def print_header_banner(
    title: str,
    subtitle: str = "",
    style: str = "bright_green",
) -> None:
    """
    Print a header banner to console.
    
    Args:
        title: Main title text
        subtitle: Optional subtitle
        style: Color style for the box
    """
    console = Console()
    content = Text()
    content.append(f"{title}", style=f"bold {style}")
    
    if subtitle:
        content.append("\n")
        content.append(f"{subtitle}", style="dim")
    
    console.print()
    console.print(Panel(
        Align.center(content),
        box=DOUBLE,
        border_style=style,
        padding=(0, 4),
    ))
    console.print()


def create_status_box(
    title: str,
    items: list[tuple[str, str, bool]],
    box_style: str = "bright_green",
) -> Panel:
    """
    Create a status box with check/cross items.
    
    Args:
        title: Box title
        items: List of (name, description, success) tuples
        box_style: Border color style
    
    Returns:
        Rich Panel with status items
    """
    content = Text()
    
    for name, desc, success in items:
        icon = StatusIcons.SUCCESS if success else StatusIcons.ERROR
        status_style = "green" if success else "red"
        
        content.append(f"  {icon} ", style=status_style)
        content.append(f"{name}", style="bold")
        content.append(f" - {desc}\n", style="dim")
    
    return Panel(
        content,
        title=f"[bold]{title}[/bold]",
        box=ROUNDED,
        border_style=box_style,
        padding=(1, 2),
    )


def create_stats_panel(
    stats: dict[str, Any],
    title: str = "Statistics",
    style: str = "cyan",
) -> Panel:
    """
    Create a statistics panel with key-value pairs.
    
    Args:
        stats: Dictionary of stat name to value
        title: Panel title
        style: Border color style
    
    Returns:
        Rich Panel with formatted statistics
    """
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold")
    table.add_column("Value", style=style)
    
    for key, value in stats.items():
        table.add_row(f"{key}:", str(value))
    
    return Panel(
        table,
        title=f" {StatusIcons.STAR} {title} ",
        box=ROUNDED,
        border_style=style,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PROGRESS ANIMATIONS
# ═══════════════════════════════════════════════════════════════════════════════


def create_fancy_progress() -> Progress:
    """
    Create a fancy progress bar with multiple columns.
    
    Returns:
        Rich Progress object with custom styling
    """
    return Progress(
        SpinnerColumn("dots", style="bright_green"),
        TextColumn("[bold bright_green]{task.description}"),
        BarColumn(
            bar_width=40,
            style="grey50",
            complete_style="bright_green",
            finished_style="green",
        ),
        TaskProgressColumn(),
        TextColumn("[dim]{task.fields[status]}"),
        TimeElapsedColumn(),
        console=console,
    )


def create_gaming_progress() -> Progress:
    """
    Create a gaming-style progress bar.
    
    Returns:
        Rich Progress with gaming theme
    """
    return Progress(
        SpinnerColumn("arrow3", style="cyan"),
        TextColumn("[bold cyan]⚡ {task.description}"),
        BarColumn(
            bar_width=30,
            style="grey30",
            complete_style="cyan",
            finished_style="bright_cyan",
            pulse_style="cyan",
        ),
        TextColumn("[bold]{task.percentage:>3.0f}%"),
        TextColumn("[dim]│"),
        TimeElapsedColumn(),
        console=console,
    )


LOADING_FRAMES = [
    "◐", "◓", "◑", "◒",
]

LOADING_FRAMES_BLOCKS = [
    "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█", "▉", "▊", "▋", "▌", "▍", "▎", "▏",
]

LOADING_FRAMES_DOTS = [
    "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏",
]


def animated_loading(message: str, duration: float = 2.0, color: str = "bright_green") -> None:
    """
    Show an animated loading indicator.
    
    Args:
        message: Message to display
        duration: How long to show the animation
        color: Color style for the animation
    """
    frames = LOADING_FRAMES_DOTS
    start = time.time()
    i = 0
    
    with Live(console=console, refresh_per_second=10) as live:
        while time.time() - start < duration:
            frame = frames[i % len(frames)]
            live.update(Text.from_markup(f"  [{color}]{frame}[/] [{color}]{message}[/]"))
            time.sleep(0.1)
            i += 1


# ═══════════════════════════════════════════════════════════════════════════════
# RESULT DISPLAYS
# ═══════════════════════════════════════════════════════════════════════════════


def print_success_banner(
    title: str,
    message: str = "",
    stats: dict[str, Any] | None = None,
) -> None:
    """
    Print a success banner with optional stats.
    
    Args:
        title: Success title
        message: Success message
        stats: Optional statistics to display
    """
    content = Text()
    content.append(f"\n  {StatusIcons.SUCCESS} ", style="bold green")
    content.append(title, style="bold bright_green")
    
    if message:
        content.append(f"\n  {message}", style="green")
    
    if stats:
        content.append("\n")
        for key, value in stats.items():
            content.append(f"\n  {StatusIcons.ARROW} ", style="dim")
            content.append(f"{key}: ", style="dim")
            content.append(str(value), style="bright_green")
    
    content.append("\n")
    
    console.print(Panel(
        content,
        box=ROUNDED,
        border_style="green",
        padding=(0, 2),
    ))


def print_error_banner(
    title: str,
    message: str = "",
    suggestion: str = "",
) -> None:
    """
    Print an error banner with optional suggestion.
    
    Args:
        title: Error title
        message: Error message
        suggestion: Optional suggestion to fix the error
    """
    content = Text()
    content.append(f"\n  {StatusIcons.ERROR} ", style="bold red")
    content.append(title, style="bold red")
    
    if message:
        content.append(f"\n  {message}", style="red")
    
    if suggestion:
        content.append(f"\n\n  {StatusIcons.INFO} Suggestion: ", style="yellow")
        content.append(suggestion, style="dim")
    
    content.append("\n")
    
    console.print(Panel(
        content,
        box=ROUNDED,
        border_style="red",
        padding=(0, 2),
    ))


def print_warning_banner(title: str, message: str = "", suggestion: str = "") -> None:
    """Print a warning banner."""
    content = Text()
    content.append(f"\n  {StatusIcons.WARNING} ", style="bold yellow")
    content.append(title, style="bold yellow")
    
    if message:
        content.append(f"\n  {message}", style="yellow")
    
    if suggestion:
        content.append(f"\n\n  {StatusIcons.INFO} Suggestion: ", style="yellow")
        content.append(suggestion, style="dim")
    
    content.append("\n")
    
    console.print(Panel(
        content,
        box=ROUNDED,
        border_style="yellow",
        padding=(0, 2),
    ))


def print_tip(message: str) -> None:
    """Print a styled tip message."""
    from rich.padding import Padding
    content = Text()
    content.append(f" {message}", style="cyan")
    
    panel = Panel(
        Align.center(content),
        title="[yellow]💡 UnrealMate Tip[/yellow]",
        box=ROUNDED,
        border_style="yellow",
        padding=(0, 2),
        width=64,
    )
    console.print(Padding(panel, (0, 0, 0, 2)))


# ═══════════════════════════════════════════════════════════════════════════════
# TREE VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════════════════════


def create_file_tree(
    root_name: str,
    items: dict[str, Any],
    style: str = "bright_green",
) -> Tree:
    """
    Create a file tree visualization.
    
    Args:
        root_name: Name of the root node
        items: Dictionary of items (nested for subdirectories)
        style: Color style
    
    Returns:
        Rich Tree object
    """
    tree = Tree(
        f"[bold {style}]{StatusIcons.FOLDER} {root_name}[/]",
        guide_style=style,
    )
    
    def add_items(parent: Tree, data: dict) -> None:
        for name, value in data.items():
            if isinstance(value, dict):
                branch = parent.add(f"[{style}]{StatusIcons.FOLDER} {name}[/]")
                add_items(branch, value)
            else:
                icon = StatusIcons.FILE
                if name.endswith(".uasset"):
                    icon = StatusIcons.PACKAGE
                elif name.endswith(".uproject"):
                    icon = StatusIcons.GAMEPAD
                parent.add(f"[dim]{icon} {name}[/] [bright_black]{value}[/]")
    
    add_items(tree, items)
    return tree


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════


def create_dashboard_layout() -> Layout:
    """
    Create a dashboard layout for complex displays.
    
    Returns:
        Rich Layout object
    """
    layout = Layout()
    
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3),
    )
    
    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right"),
    )
    
    return layout


def create_mini_card(
    title: str,
    value: str,
    icon: str = "",
    color: str = "cyan",
) -> Panel:
    """
    Create a mini info card.
    
    Args:
        title: Card title
        value: Main value to display
        icon: Optional icon
        color: Card color
    
    Returns:
        Rich Panel representing a card
    """
    content = Text()
    content.append(f"{icon} " if icon else "", style=color)
    content.append(f"{value}\n", style=f"bold {color}")
    content.append(title, style="dim")
    
    return Panel(
        Align.center(content),
        box=ROUNDED,
        border_style=color,
        padding=(0, 1),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND RESULT FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════


def format_command_result(
    command: str,
    success: bool,
    output: str = "",
    duration: float = 0.0,
) -> Panel:
    """
    Format a command execution result.
    
    Args:
        command: Command that was executed
        success: Whether it succeeded
        output: Command output
        duration: Execution duration in seconds
    
    Returns:
        Rich Panel with formatted result
    """
    status_icon = StatusIcons.SUCCESS if success else StatusIcons.ERROR
    status_color = "green" if success else "red"
    
    content = Text()
    content.append(f"  {status_icon} ", style=status_color)
    content.append(f"{command}\n", style=f"bold {status_color}")
    
    if output:
        content.append(f"\n{output}\n", style="dim")
    
    if duration > 0:
        content.append(f"\n  ⏱️  {duration:.2f}s", style="dim")
    
    return Panel(
        content,
        box=ROUNDED,
        border_style=status_color,
        title="[bold]Command Result[/bold]",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# UE-THEMED COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════


def print_ue_banner() -> None:
    """Print the modern minimal UnrealMate banner."""
    from unrealmate.core.signature import print_signature_banner
    print_signature_banner()


def print_command_header(command_name: str, description: str = "") -> None:
    """
    Print a styled command header.
    
    Args:
        command_name: Name of the command
        description: Command description
    """
    from rich.rule import Rule
    
    console.print()
    console.print(Rule(style="dim"))
    
    header = Text()
    header.append(f"  {StatusIcons.LIGHTNING} ", style="cyan")
    header.append(command_name.upper(), style="bold bright_green")
    
    if description:
        header.append(f"  |  {description}", style="dim")
    
    console.print(header)
    console.print()


def print_footer() -> None:
    """Print a styled footer (minimal)."""
    from rich.rule import Rule
    # Footer is mostly handled by the banner metadata now, keeping this empty/minimal
    console.print()
    console.print(Rule(style="dim"))
    console.print()


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def success(message: str) -> None:
    """Print a success message."""
    console.print(f"  {StatusIcons.SUCCESS} {message}", style="green")


def error(message: str) -> None:
    """Print an error message."""
    console.print(f"  {StatusIcons.ERROR} {message}", style="red")


def warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"  {StatusIcons.WARNING} {message}", style="yellow")


def info(message: str) -> None:
    """Print an info message."""
    console.print(f"  {StatusIcons.INFO} {message}", style="cyan")


def step(number: int, message: str) -> None:
    """Print a numbered step."""
    console.print(f"  [{number}] {message}", style="bold bright_green")


def bullet(message: str) -> None:
    """Print a bullet point."""
    console.print(f"  {StatusIcons.ARROW} {message}", style="dim")
