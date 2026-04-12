"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - UX Utilities Module                          ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: User Experience and Interaction utilities                          ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Interactive wizards, progress bars, and standardized UI components.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers

This module provides:
- Interactive mode (wizard-style prompts)
- Progress bars and loading indicators
- Colored output helpers
- Report generators (HTML, JSON, XML)
- Config validation
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# INTERACTIVE MODE (Wizard-style prompts)
# ═══════════════════════════════════════════════════════════════════════════════


class InteractiveWizard:
    """Wizard-style interactive prompts for complex commands."""

    def __init__(self, title: str, description: str = ""):
        self.title = title
        self.description = description
        self.steps: list[dict[str, Any]] = []
        self.results: dict[str, Any] = {}

    def add_step(
        self,
        key: str,
        prompt: str,
        step_type: str = "text",
        default: Any = None,
        choices: Optional[list[str]] = None,
        validator: Optional[Callable[[Any], bool]] = None,
    ) -> "InteractiveWizard":
        """
        Add a step to the wizard.

        Args:
            key: Key to store the result
            prompt: Prompt text to display
            step_type: Type of input ('text', 'confirm', 'int', 'choice')
            default: Default value
            choices: List of choices (for 'choice' type)
            validator: Optional validation function

        Returns:
            Self for chaining
        """
        self.steps.append({
            "key": key,
            "prompt": prompt,
            "type": step_type,
            "default": default,
            "choices": choices,
            "validator": validator,
        })
        return self

    def run(self) -> dict[str, Any]:
        """Run the wizard and collect all inputs."""
        console.print(Panel(
            f"[bold cyan]{self.title}[/bold cyan]\n{self.description}",
            border_style="cyan"
        ))
        console.print()

        for i, step in enumerate(self.steps, 1):
            console.print(f"[dim]Step {i}/{len(self.steps)}[/dim]")

            value = self._get_input(step)

            # Validate if validator provided
            if step["validator"] and not step["validator"](value):
                console.print("[bold red]Invalid input. Please try again.[/bold red]")
                value = self._get_input(step)

            self.results[step["key"]] = value
            console.print()

        console.print("[bold green]✓ Wizard completed![/bold green]\n")
        return self.results

    def _get_input(self, step: dict[str, Any]) -> Any:
        """Get input based on step type."""
        prompt_text = step["prompt"]
        default = step["default"]

        if step["type"] == "confirm":
            return Confirm.ask(prompt_text, default=default or False)
        elif step["type"] == "int":
            return IntPrompt.ask(prompt_text, default=default or 0)
        elif step["type"] == "choice" and step["choices"]:
            choices_str = ", ".join(step["choices"])
            console.print(f"[dim]Options: {choices_str}[/dim]")
            return Prompt.ask(
                prompt_text,
                choices=step["choices"],
                default=default
            )
        else:
            return Prompt.ask(prompt_text, default=default or "")


def run_setup_wizard() -> dict[str, Any]:
    """Run the initial setup wizard for new projects."""
    wizard = InteractiveWizard(
        title="🚀 UnrealMate Setup Wizard",
        description="Let's configure UnrealMate for your project"
    )

    wizard.add_step(
        "project_name",
        "What is your project name?",
        default="MyUnrealProject"
    ).add_step(
        "enable_git_lfs",
        "Enable Git LFS for large files?",
        step_type="confirm",
        default=True
    ).add_step(
        "enable_cache",
        "Enable performance cache?",
        step_type="confirm",
        default=True
    ).add_step(
        "color_theme",
        "Select color theme",
        step_type="choice",
        choices=["cyan_magenta", "green_blue", "monochrome"],
        default="cyan_magenta"
    ).add_step(
        "max_workers",
        "Maximum parallel workers",
        step_type="int",
        default=4
    )

    return wizard.run()


# ═══════════════════════════════════════════════════════════════════════════════
# PROGRESS BARS & LOADING INDICATORS
# ═══════════════════════════════════════════════════════════════════════════════


def create_progress_bar() -> Progress:
    """Create a styled progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    )


def create_simple_progress() -> Progress:
    """Create a simple progress bar for quick tasks."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold]{task.description}"),
        BarColumn(),
        console=console,
    )


def run_with_progress(
    items: list[Any],
    description: str,
    callback: Callable[[Any], Any],
) -> list[Any]:
    """
    Run a callback on each item with a progress bar.

    Args:
        items: List of items to process
        description: Description for progress bar
        callback: Function to call on each item

    Returns:
        List of results from callback
    """
    results = []
    with create_progress_bar() as progress:
        task = progress.add_task(description, total=len(items))
        for item in items:
            result = callback(item)
            results.append(result)
            progress.advance(task)
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════


class ConfigValidator:
    """Validate UnrealMate configuration."""

    VALID_COLOR_THEMES = ["cyan_magenta", "green_blue", "monochrome", "custom"]
    VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self) -> bool:
        """
        Validate the configuration.

        Returns:
            True if valid, False otherwise
        """
        self._validate_version()
        self._validate_performance()
        self._validate_signature()
        self._validate_git()
        return len(self.errors) == 0

    def _validate_version(self) -> None:
        """Validate version field."""
        version = self.config.get("version", "")
        if not version:
            self.errors.append("Missing 'version' field")
        elif not isinstance(version, str):
            self.errors.append("'version' must be a string")

    def _validate_performance(self) -> None:
        """Validate performance configuration."""
        perf = self.config.get("performance", {})

        if "cache_ttl_hours" in perf:
            ttl = perf["cache_ttl_hours"]
            if not isinstance(ttl, int) or ttl < 0:
                self.errors.append("'cache_ttl_hours' must be a non-negative integer")

        if "max_workers" in perf:
            workers = perf["max_workers"]
            if not isinstance(workers, int) or workers < 1:
                self.errors.append("'max_workers' must be a positive integer")
            elif workers > 32:
                self.warnings.append(
                    "'max_workers' is set very high (>32), consider reducing"
                )

        if "max_cache_size_mb" in perf:
            size = perf["max_cache_size_mb"]
            if not isinstance(size, int) or size < 0:
                self.errors.append("'max_cache_size_mb' must be a non-negative integer")

    def _validate_signature(self) -> None:
        """Validate signature configuration."""
        sig = self.config.get("signature", {})

        if "color_theme" in sig:
            theme = sig["color_theme"]
            if theme not in self.VALID_COLOR_THEMES:
                self.warnings.append(
                    f"Unknown color theme '{theme}', valid options: {self.VALID_COLOR_THEMES}"
                )

    def _validate_git(self) -> None:
        """Validate Git configuration."""
        git = self.config.get("git", {})
        # All git options are boolean, just check types
        for key in ["auto_lfs", "commit_template_enabled", "pre_commit_hooks"]:
            if key in git and not isinstance(git[key], bool):
                self.errors.append(f"'{key}' must be a boolean")

    def print_report(self) -> None:
        """Print validation report."""
        if self.errors:
            console.print("\n[bold red]❌ Configuration Errors:[/bold red]")
            for error in self.errors:
                console.print(f"  • {error}")

        if self.warnings:
            console.print("\n[bold yellow]⚠️  Configuration Warnings:[/bold yellow]")
            for warning in self.warnings:
                console.print(f"  • {warning}")

        if not self.errors and not self.warnings:
            console.print("[bold green]✅ Configuration is valid![/bold green]")


# ═══════════════════════════════════════════════════════════════════════════════
# REPORT GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════


class ReportGenerator:
    """Generate reports in various formats."""

    def __init__(self, title: str, data: dict[str, Any]):
        self.title = title
        self.data = data
        self.timestamp = datetime.now().isoformat()

    def to_json(self, output_path: Optional[Path] = None) -> str:
        """
        Generate JSON report.

        Args:
            output_path: Optional path to write file

        Returns:
            JSON string
        """
        report = {
            "title": self.title,
            "generated_at": self.timestamp,
            "generator": "UnrealMate by G & E ZYNTH",
            "data": self.data,
        }
        json_str = json.dumps(report, indent=2, default=str)

        if output_path:
            output_path.write_text(json_str, encoding="utf-8")
            console.print(f"[green]✓ JSON report saved to {output_path}[/green]")

        return json_str

    def to_xml(self, output_path: Optional[Path] = None) -> str:
        """
        Generate XML report.

        Args:
            output_path: Optional path to write file

        Returns:
            XML string
        """
        root = ET.Element("report")
        root.set("title", self.title)
        root.set("generated_at", self.timestamp)
        root.set("generator", "UnrealMate by G & E ZYNTH")

        self._dict_to_xml(root, self.data)

        xml_str = ET.tostring(root, encoding="unicode", method="xml")

        if output_path:
            output_path.write_text(xml_str, encoding="utf-8")
            console.print(f"[green]✓ XML report saved to {output_path}[/green]")

        return xml_str

    def _dict_to_xml(self, parent: ET.Element, data: dict[str, Any]) -> None:
        """Convert dictionary to XML elements."""
        for key, value in data.items():
            child = ET.SubElement(parent, str(key).replace(" ", "_"))
            if isinstance(value, dict):
                self._dict_to_xml(child, value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    item_elem = ET.SubElement(child, "item")
                    item_elem.set("index", str(i))
                    if isinstance(item, dict):
                        self._dict_to_xml(item_elem, item)
                    else:
                        item_elem.text = str(item)
            else:
                child.text = str(value)

    def to_html(self, output_path: Optional[Path] = None) -> str:
        """
        Generate HTML report.

        Args:
            output_path: Optional path to write file

        Returns:
            HTML string
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title} - UnrealMate Report</title>
    <style>
        :root {{
            --primary: #00d4ff;
            --secondary: #ff00ff;
            --bg: #0a0a0a;
            --text: #ffffff;
            --card-bg: #1a1a2e;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }}
        h1 {{ font-size: 2.5rem; }}
        .meta {{ color: #888; font-size: 0.9rem; margin-top: 0.5rem; }}
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .card h2 {{
            color: var(--primary);
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 0.5rem;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        th {{ color: var(--secondary); }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
        .footer a {{ color: var(--primary); text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 {self.title}</h1>
            <p class="meta">Generated: {self.timestamp}</p>
        </header>
        {self._data_to_html_cards(self.data)}
        <div class="footer">
            <p>Generated by <a href="https://github.com/gktrk363/unrealmate">UnrealMate</a> | © 2026 G & E ZYNTH</p>
        </div>
    </div>
</body>
</html>"""

        if output_path:
            output_path.write_text(html, encoding="utf-8")
            console.print(f"[green]✓ HTML report saved to {output_path}[/green]")

        return html

    def _data_to_html_cards(self, data: dict[str, Any]) -> str:
        """Convert data to HTML cards."""
        html_parts = []

        for key, value in data.items():
            title = key.replace("_", " ").title()

            if isinstance(value, dict):
                rows = "".join(
                    f"<tr><td>{k}</td><td>{v}</td></tr>"
                    for k, v in value.items()
                )
                html_parts.append(f"""
                <div class="card">
                    <h2>{title}</h2>
                    <table><tbody>{rows}</tbody></table>
                </div>
                """)
            elif isinstance(value, list):
                rows = "".join(f"<tr><td>{item}</td></tr>" for item in value)
                html_parts.append(f"""
                <div class="card">
                    <h2>{title}</h2>
                    <table><tbody>{rows}</tbody></table>
                </div>
                """)
            else:
                html_parts.append(f"""
                <div class="card">
                    <h2>{title}</h2>
                    <p>{value}</p>
                </div>
                """)

        return "".join(html_parts)


# ═══════════════════════════════════════════════════════════════════════════════
# COLORED OUTPUT HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[bold green]✅ {message}[/bold green]")


def print_error(message: str, hint: Optional[str] = None) -> None:
    """Print error message with optional hint."""
    console.print(f"\n[bold red]❌ Error:[/bold red] {message}")
    if hint:
        console.print(f"[dim]💡 Hint: {hint}[/dim]")
    console.print()


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[bold yellow]⚠️  Warning:[/bold yellow] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[bold cyan]ℹ️  {message}[/bold cyan]")


def print_step(step_num: int, total: int, message: str) -> None:
    """Print step progress."""
    console.print(f"[dim][{step_num}/{total}][/dim] {message}")


def print_header(title: str, subtitle: str = "") -> None:
    """Print a styled header."""
    content = f"[bold cyan]{title}[/bold cyan]"
    if subtitle:
        content += f"\n[dim]{subtitle}[/dim]"
    console.print(Panel(content, border_style="cyan"))


def print_summary_table(title: str, data: dict[str, Any]) -> None:
    """Print a summary table."""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    for key, value in data.items():
        table.add_row(str(key), str(value))

    console.print(table)

