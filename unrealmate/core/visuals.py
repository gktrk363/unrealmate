"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Visual Enhancements                          ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Visual enhancements and CLI aesthetics                             ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Advanced visual components, animations, and branding.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import io
import sys
import time
from typing import Any, Optional


from rich.align import Align
from rich.box import ASCII, DOUBLE as BOX_DOUBLE, HEAVY as BOX_HEAVY, MINIMAL as BOX_MINIMAL, ROUNDED as BOX_ROUNDED
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
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

ASCII_MODE = False
DOUBLE = BOX_DOUBLE
HEAVY = BOX_HEAVY
MINIMAL = BOX_MINIMAL
ROUNDED = BOX_ROUNDED


def _build_console() -> Console:
    """Build a console that matches the current render-safety mode."""
    return Console(emoji=not ASCII_MODE, safe_box=ASCII_MODE)


console = _build_console()



def is_utf8_encoding(encoding: Optional[str]) -> bool:
    """Return True when the encoding can safely represent unicode output."""
    if not encoding:
        return False
    return "utf" in encoding.lower()


def output_supports_unicode(stream: Any | None = None) -> bool:
    """Detect whether the target stream supports unicode output reliably."""
    target = stream if stream is not None else sys.stdout
    return is_utf8_encoding(getattr(target, "encoding", None))


def configure_output_stream(stream: Any) -> bool:
    """
    Make non-UTF streams safe by switching to replacement error handling.

    Returns:
        True if stream settings were updated, False otherwise.
    """
    if stream is None:
        return False

    encoding = getattr(stream, "encoding", None)
    if is_utf8_encoding(encoding):
        return False

    reconfigure = getattr(stream, "reconfigure", None)
    if not callable(reconfigure):
        return False

    try:
        if getattr(stream, "errors", None) != "replace":
            reconfigure(errors="replace")
            return True
    except Exception:
        return False

    return False


def configure_output_safety() -> bool:
    """
    Configure stdout/stderr for safe rendering on legacy code pages.

    Returns:
        True if any stream configuration changed.
    """
    changed = False
    for stream in (sys.stdout, sys.stderr):
        changed = configure_output_stream(stream) or changed

    apply_render_mode(
        not (output_supports_unicode(sys.stdout) and output_supports_unicode(sys.stderr))
    )
    return changed


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM BOX STYLES
# ═══════════════════════════════════════════════════════════════════════════════


# Use built-in box styles
UE_BOX = MINIMAL
GAMING_BOX = MINIMAL


# ═══════════════════════════════════════════════════════════════════════════════
# STATUS ICONS & EMOJIS
# ═══════════════════════════════════════════════════════════════════════════════


class StatusIcons:
    """Status icons for CLI output."""

    # Basic status
    SUCCESS = "[OK]"
    ERROR = "[X]"
    WARNING = "[!]"
    INFO = "[i]"
    PENDING = "..."

    # Actions
    ROCKET = ">>"
    CHECK = "[OK]"
    CROSS = "[X]"
    ARROW = "->"
    STAR = "*"
    FIRE = "*"
    SPARKLES = "*"

    # Objects
    FOLDER = "[DIR]"
    FILE = "[FILE]"
    PACKAGE = "[PKG]"
    GEAR = "[CFG]"
    WRENCH = "[TOOL]"
    HAMMER = "[BUILD]"

    # Gaming/UE
    GAMEPAD = "[GAME]"
    JOYSTICK = "[CTRL]"
    BLUEPRINT = "[BP]"
    LIGHTNING = "[!]"
    TARGET = "[TARGET]"
    TROPHY = "[WIN]"

    # Code
    BUG = "[BUG]"
    CODE = "[CODE]"
    TERMINAL = "[TERM]"
    GIT = "[GIT]"

    # Extra icons used across CLI commands
    TIMER = "[TIME]"
    UP_ARROW = "[UP]"
    TIP = "[TIP]"
    SEARCH = "[?]"
    ALERT = "[!!]"
    CELEBRATE = "[OK]"
    THUMBSUP = "[OK]"
    LOCK = "[LOCK]"
    CHART = "[CHART]"
    GLOBE = "[WEB]"
    SEND = "[SEND]"
    SAVE = "[SAVE]"
    CLIPBOARD = "[CLIP]"
    DOCKER = "[DOCK]"
    ROBOT = "[AI]"
    TEAM = "[TEAM]"
    CART = "[SHOP]"
    REFRESH = "[SYNC]"
    HOSPITAL = "[HP]"
    BELL = "[BELL]"

    @classmethod
    def get_status(cls, success: bool) -> str:
        return cls.SUCCESS if success else cls.ERROR


def _apply_unicode_status_icons() -> None:
    """Apply full unicode icons when the terminal supports UTF-8."""
    icons = {
        "SUCCESS": "[OK]",
        "ERROR": "[X]",
        "WARNING": "[!]",
        "INFO": "[i]",
        "PENDING": "...",
        "ROCKET": ">>",
        "CHECK": "[OK]",
        "CROSS": "[X]",
        "ARROW": "->",
        "STAR": "*",
        "FIRE": "*",
        "SPARKLES": "*",
        "FOLDER": "[DIR]",
        "FILE": "[FILE]",
        "PACKAGE": "[PKG]",
        "GEAR": "[CFG]",
        "WRENCH": "[TOOL]",
        "HAMMER": "[BUILD]",
        "GAMEPAD": "[GAME]",
        "JOYSTICK": "[CTRL]",
        "BLUEPRINT": "[BP]",
        "LIGHTNING": "[!]",
        "TARGET": "[TARGET]",
        "TROPHY": "[WIN]",
        "BUG": "[BUG]",
        "CODE": "[CODE]",
        "TERMINAL": "[TERM]",
        "GIT": "[GIT]",
        "TIMER": "[TIME]",
        "UP_ARROW": "[UP]",
        "TIP": "[TIP]",
        "SEARCH": "[?]",
        "ALERT": "[!!]",
        "CELEBRATE": "[OK]",
        "THUMBSUP": "[OK]",
        "LOCK": "[LOCK]",
        "CHART": "[CHART]",
        "GLOBE": "[WEB]",
        "SEND": "[SEND]",
        "SAVE": "[SAVE]",
        "CLIPBOARD": "[CLIP]",
        "DOCKER": "[DOCK]",
        "ROBOT": "[AI]",
        "TEAM": "[TEAM]",
        "CART": "[SHOP]",
        "REFRESH": "[SYNC]",
        "HOSPITAL": "[HP]",
        "BELL": "[BELL]",
    }
    for attr, value in icons.items():
        setattr(StatusIcons, attr, value)


def _apply_ascii_status_icons() -> None:
    """Alias kept for backward compat; icons default to ASCII already."""
    _apply_unicode_status_icons()


def _apply_box_styles() -> None:
    """Switch shared box styles to ASCII-safe variants when needed."""
    global DOUBLE, HEAVY, MINIMAL, ROUNDED, UE_BOX, GAMING_BOX

    if ASCII_MODE:
        DOUBLE = ASCII
        HEAVY = ASCII
        MINIMAL = ASCII
        ROUNDED = ASCII
    else:
        DOUBLE = BOX_DOUBLE
        HEAVY = BOX_HEAVY
        MINIMAL = BOX_MINIMAL
        ROUNDED = BOX_ROUNDED

    UE_BOX = DOUBLE
    GAMING_BOX = HEAVY


def _refresh_console() -> None:
    """Refresh the shared module console after render-mode changes."""
    global console
    console = _build_console()


def apply_render_mode(ascii_mode: bool) -> None:
    """Update shared visuals to match the requested render mode."""
    global ASCII_MODE
    ASCII_MODE = ascii_mode
    if ASCII_MODE:
        _apply_ascii_status_icons()
    else:
        _apply_unicode_status_icons()
    _apply_box_styles()
    _refresh_console()


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


_KIND_STYLES: dict[str, tuple[str, str]] = {
    "info": ("cyan", "white"),
    "success": ("green", "white"),
    "warning": ("yellow", "white"),
    "error": ("red", "white"),
}


def _normalize_panel_rows(
    rows: dict[str, Any] | list[tuple[str, Any]] | tuple[tuple[str, Any], ...],
) -> list[tuple[str, Any]]:
    """Normalize stat/key-value input into a list of rows."""
    if isinstance(rows, dict):
        return list(rows.items())
    return list(rows)


def create_hero_panel(
    title: str,
    subtitle: str = "",
    eyebrow: str = "",
    accent: str = "cyan",
) -> Group:
    """Create a minimal hero group for command banners."""
    content = Text()
    if eyebrow:
        content.append(f"{eyebrow}\n", style="dim")
    content.append(title, style="bold white")
    if subtitle:
        content.append(f"  {subtitle}", style="dim")
    return Group(content, Text(""))


def create_section_title(title: str, subtitle: str = "") -> Group:
    """Create a compact section title group with optional subtitle."""
    content = Text()
    content.append(title, style="bold white")
    if subtitle:
        content.append(f"  {subtitle}", style="dim")

    return Group(content, Text(""))


def create_key_value_panel(
    title: str,
    rows: dict[str, Any] | list[tuple[str, Any]] | tuple[tuple[str, Any], ...],
    accent: str = "cyan",
) -> Panel:
    """Create a consistent key-value summary panel."""
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="bold white", no_wrap=True)
    table.add_column("Value", style=accent, overflow="fold")

    for key, value in _normalize_panel_rows(rows):
        table.add_row(f"{key}:", str(value))

    return Panel(
        table,
        title=f"[bold]{title}[/bold]",
        border_style=accent,
        box=ROUNDED,
        padding=(0, 1),
    )


def create_message_panel(
    kind: str,
    title: str,
    body: str = "",
    suggestion: str = "",
    stats: dict[str, Any] | list[tuple[str, Any]] | tuple[tuple[str, Any], ...] | None = None,
) -> Panel:
    """Create a consistent info/success/warning/error panel."""
    accent, body_style = _KIND_STYLES.get(kind, ("cyan", "white"))
    content_parts: list[Any] = []

    if body:
        content_parts.append(Text.from_markup(body, style=body_style))

    if stats:
        if content_parts:
            content_parts.append(Text(""))
        stats_table = Table(show_header=False, box=None, padding=(0, 1))
        stats_table.add_column("Key", style="bold white", no_wrap=True)
        stats_table.add_column("Value", style=accent, overflow="fold")
        for key, value in _normalize_panel_rows(stats):
            stats_table.add_row(f"{key}:", str(value))
        content_parts.append(stats_table)

    if suggestion:
        if content_parts:
            content_parts.append(Text(""))
        suggestion_text = Text()
        suggestion_text.append("Suggestion: ", style=f"bold {accent}")
        suggestion_text.append(suggestion, style="dim")
        content_parts.append(suggestion_text)

    if not content_parts:
        content_parts.append(Text("", style=body_style))

    return Panel(
        Group(*content_parts),
        title=f"[bold {accent}]{title}[/bold {accent}]",
        border_style=accent,
        box=ROUNDED,
        padding=(0, 1),
    )


def create_command_card(
    step: str,
    command: str,
    description: str,
    accent: str = "cyan",
) -> Panel:
    """Create a compact command card for onboarding and identity surfaces."""
    content = Text()
    content.append(f"{step}\n", style=f"bold {accent}")
    content.append(command, style="bold white")
    content.append(f"\n{description}", style="dim")

    return Panel(
        content,
        border_style=accent,
        box=ROUNDED,
        padding=(0, 1),
    )


def create_command_section_panel(
    title: str,
    rows: list[tuple[str, str]],
    *,
    accent: str = "cyan",
    subtitle: str = "",
    command_width: int = 24,
) -> Group:
    """Create a help-oriented section group with minimal visual noise."""
    table = Table.grid(expand=False, padding=(0, 2))
    table.add_column(width=3)
    table.add_column(style="cyan", width=command_width)
    table.add_column(style="dim")

    for command_name, description in rows:
        table.add_row("", command_name, description)

    parts: list[Any] = []
    
    header = Text()
    if title:
        header.append(f"{title}\n", style="bold white")
    if subtitle:
        header.append(f"  {subtitle}\n", style="dim")
    
    if len(header):
        parts.append(header)
        
    parts.append(table)
    parts.append(Text(""))

    return Group(*parts)


def render_renderables_to_text(
    renderable: Any,
    *,
    use_color: bool,
    width: int,
) -> str:
    """Render Rich content to terminal text, preserving ANSI only when requested."""
    capture_buffer = io.StringIO()
    capture_console = Console(
        file=capture_buffer,
        record=True,
        width=width,
        force_terminal=use_color and not ASCII_MODE,
        color_system="standard" if use_color and not ASCII_MODE else None,
        emoji=not ASCII_MODE,
        safe_box=ASCII_MODE,
    )
    capture_console.print(renderable)
    return capture_console.export_text(styles=use_color and not ASCII_MODE)


def render_version_screen(
    *,
    version: str,
    subtitle: str,
    runtime_rows: list[tuple[str, str]],
    release_rows: list[tuple[str, str]],
    help_rows: list[tuple[str, str]],
    repository: str,
) -> Group:
    """Render the CLI identity/version screen."""

    identity = Text()
    identity.append("UnrealMate CLI ", style="bold white")
    identity.append(f"v{version}\n", style="cyan")
    identity.append(subtitle, style="dim")

    detail_table = Table(show_header=False, box=None, padding=(0, 2, 0, 0), expand=False)
    detail_table.add_column("Key", style="dim", no_wrap=True)
    detail_table.add_column("Value", style="white", overflow="fold")

    for key, value in runtime_rows:
        detail_table.add_row(key, value)
    if runtime_rows and release_rows:
        detail_table.add_row("", "")
    for key, value in release_rows:
        detail_table.add_row(key, value)

    help_table = Table.grid(expand=False, padding=(0, 2))
    help_table.add_column(style="cyan")
    help_table.add_column(style="dim")

    for flag, description in help_rows:
        help_table.add_row(flag, description)

    repo_text = Text(f"\n{repository}", style="dim")

    return Group(identity, Text("\n"), detail_table, Text("\n"), help_table, repo_text)


def render_root_help_screen(
    *,
    version: str,
    subtitle: str,
    identity_body: str,
    start_safe_cards: list[tuple[str, str, str]],
    later_when_ready_body: str,
    workflow_sections: list[dict[str, Any]],
    labels_body: str,
    labels_suggestion: str,
) -> Group:
    """Render the stable/default root help screen as a curated workflow hub."""

    # --- Compact identity ---
    identity = Text(justify="center")
    identity.append("UNREALMATE", style="bold cyan")
    identity.append(f"  v{version}\n", style="bold white")
    identity.append(subtitle, style="dim")

    # (identity panel removed — minimalist format uses inline identity below)

    # --- Compact identity ---
    identity = Text()
    identity.append("Unreal", style="bold white")
    identity.append("Mate ", style="bold cyan")
    identity.append(f"v{version}\n", style="bold white")
    identity.append(subtitle, style="dim")

    usage = Group(
        Text("USAGE", style="bold white"),
        Text("  $ unrealmate [command] [options]\n", style="dim"),
    )

    # --- Unified Commands ---
    command_table = Table.grid(expand=False, padding=(0, 2))
    command_table.add_column(width=2)
    command_table.add_column(style="cyan", width=24)
    command_table.add_column(style="dim")

    for section in workflow_sections:
        command_table.add_row("", Text(section["title"], style="bold white"), "")
        for cmd, desc in section["rows"]:
            command_table.add_row("", cmd, desc)
        command_table.add_row("", "", "")

    commands_group = Group(
        Text("COMMANDS", style="bold white"),
        command_table
    )

    parts: list[Any] = [
        identity, Text("\n"),
        usage,
        commands_group,
    ]

    if labels_suggestion:
        footer = Group(
            Text("\nEXPLORE", style="bold white"),
            Text(f"  {labels_suggestion}", style="dim")
        )
        parts.append(footer)

    return Group(*parts)


def render_help_all_screen(
    *,
    root_renderable: Group,
    explore_intro_body: str,
    opt_in_sections: list[dict[str, Any]],
) -> Group:
    """Render the explicit opt-in/secondary exploration view."""
    opt_in_panels = [
        Group(
            Text(section["title"], style="bold white"),
            Text(f"  {section.get('subtitle', '')}\n", style="dim"),
            create_command_section_panel(
                "",
                section["rows"],
                accent=section.get("accent", "dim"),
                subtitle="",
                command_width=section.get("command_width", 22),
            )
        )
        for section in opt_in_sections
    ]

    separator = Group(
        Text("\nEXPLORE BEYOND THE PRIMARY SURFACE", style="bold white"),
        Text("  Opt-in, experimental, mock, and secondary surfaces\n", style="dim"),
        Text.from_markup(f"  [dim]{explore_intro_body}[/]\n"),
    )

    parts: list[Any] = [root_renderable, separator]
    parts.extend(opt_in_panels)
    return Group(*parts)


def render_group_help_screen(
    *,
    title: str,
    subtitle: str,
    eyebrow: str,
    note_body: str,
    note_suggestion: str,
    sections: list[dict[str, Any]],
    footer_rows: list[tuple[str, str]],
    usage: str,
) -> Group:
    """Render a custom, intentionally sectioned group help screen."""
    # --- Compact identity header ---
    header = Text()
    header.append(f"{title}\n", style="bold white")
    header.append(f"  {subtitle}", style="dim")

    # --- Usage note ---
    note_content = Text()
    note_content.append_text(Text.from_markup(f"  {note_body}"))
    if note_suggestion:
        note_content.append("\nTip: ", style="cyan")
        note_content.append(note_suggestion, style="dim")

    section_panels = [
        Group(
            Text(section["title"], style="bold white"),
            Text(f"  {section.get('subtitle', '')}\n", style="dim"),
            create_command_section_panel(
                "",
                section["rows"],
                accent=section.get("accent", "cyan"),
                subtitle="",
                command_width=section.get("command_width", 18),
            )
        )
        for section in sections
    ]

    # --- Footer ---
    footer = Group(
        Text("Options", style="bold white"),
        Text(f"  Usage: {usage}\n", style="dim"),
        create_command_section_panel(
            "",
            footer_rows,
            accent="dim",
            subtitle="",
            command_width=28,
        )
    )

    parts: list[Any] = [
        header, Text("\n"),
        note_content, Text("\n")
    ]
    parts.extend(section_panels)
    parts.append(footer)

    return Group(*parts)


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
    return create_hero_panel(title=title, subtitle=subtitle, accent=style)


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
    active_console = _build_console()
    active_console.print()
    active_console.print(create_hero_panel(title=title, subtitle=subtitle, accent=style))
    active_console.print()


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
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Status", width=6, no_wrap=True)
    table.add_column("Name", style="bold white", no_wrap=True)
    table.add_column("Description", style="dim")

    for name, desc, success in items:
        icon = StatusIcons.SUCCESS if success else StatusIcons.ERROR
        status_style = "green" if success else "red"
        table.add_row(f"[{status_style}]{icon}[/{status_style}]", name, desc)

    return Panel(
        table,
        title=f"[bold]{title}[/bold]",
        box=ROUNDED,
        border_style=box_style,
        padding=(0, 1),
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
    return create_key_value_panel(title=title, rows=stats, accent=style)


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
        SpinnerColumn(safe_spinner("dots"), style="bright_green"),
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
    separator = "|" if ASCII_MODE else "│"
    return Progress(
        SpinnerColumn(safe_spinner("arrow3"), style="cyan"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(
            bar_width=30,
            style="grey30",
            complete_style="cyan",
            finished_style="bright_cyan",
            pulse_style="cyan",
        ),
        TextColumn("[bold]{task.percentage:>3.0f}%"),
        TextColumn(f"[dim]{separator}"),
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

LOADING_FRAMES_ASCII = [
    "-", "\\", "|", "/",
]


def get_loading_frames(encoding: Optional[str] = None) -> list[str]:
    """Select loading frames based on output encoding support."""
    active_encoding = encoding
    if active_encoding is None:
        active_encoding = getattr(sys.stdout, "encoding", None)
    if is_utf8_encoding(active_encoding) and not ASCII_MODE:
        return LOADING_FRAMES_DOTS
    return LOADING_FRAMES_ASCII


def safe_spinner(preferred: str = "dots") -> str:
    """Return an ASCII-safe spinner name when unicode output is unreliable."""
    return preferred if not ASCII_MODE else "line"


def animated_loading(message: str, duration: float = 2.0, color: str = "bright_green") -> None:
    """
    Show an animated loading indicator.
    
    Args:
        message: Message to display
        duration: How long to show the animation
        color: Color style for the animation
    """
    frames = get_loading_frames()
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
    console.print(
        create_message_panel(
            "success",
            f"{StatusIcons.SUCCESS} {title}",
            body=message,
            stats=stats,
        )
    )


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
    console.print(
        create_message_panel(
            "error",
            f"{StatusIcons.ERROR} {title}",
            body=message,
            suggestion=suggestion,
        )
    )


def print_warning_banner(title: str, message: str = "", suggestion: str = "") -> None:
    """Print a warning banner."""
    console.print(
        create_message_panel(
            "warning",
            f"{StatusIcons.WARNING} {title}",
            body=message,
            suggestion=suggestion,
        )
    )


def print_tip(message: str) -> None:
    """Print a styled tip message."""
    from rich.padding import Padding
    content = Text()
    content.append(f" {message}", style="cyan")

    panel = Panel(
        Align.center(content),
        title=f"[yellow]{StatusIcons.TIP} UnrealMate Tip[/yellow]",
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
        content.append(f"\n  {StatusIcons.TIMER}  {duration:.2f}s", style="dim")
    
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


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE BOOTSTRAP — must run AFTER all classes/functions are defined
# ═══════════════════════════════════════════════════════════════════════════════
configure_output_safety()
