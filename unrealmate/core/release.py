"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Release Automation                           ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Automated release notes and version bump                           ║
║  Created: 2026-01-23                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class BumpType(Enum):
    """Version bump types following semantic versioning."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


@dataclass
class CommitInfo:
    """Information about a git commit."""
    hash: str
    short_hash: str
    message: str
    author: str
    date: str
    type: str = "other"  # feat, fix, docs, etc.


@dataclass
class ReleaseNotes:
    """Structure for release notes."""
    version: str
    date: str
    features: list[str] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)
    docs: list[str] = field(default_factory=list)
    breaking: list[str] = field(default_factory=list)
    other: list[str] = field(default_factory=list)


def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse a version string into components."""
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", version_str)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return 0, 0, 0


def bump_version(current: str, bump_type: BumpType) -> str:
    """
    Bump version according to semantic versioning.

    Args:
        current: Current version string
        bump_type: Type of version bump

    Returns:
        New version string
    """
    major, minor, patch = parse_version(current)

    if bump_type == BumpType.MAJOR:
        return f"{major + 1}.0.0"
    elif bump_type == BumpType.MINOR:
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


def get_commits_since_tag(tag: Optional[str] = None) -> list[CommitInfo]:
    """
    Get all commits since the last tag.

    Args:
        tag: Starting tag, uses latest if not specified

    Returns:
        List of CommitInfo objects
    """
    commits = []

    try:
        # Get the latest tag if not specified
        if tag is None:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
            )
            tag = result.stdout.strip() if result.returncode == 0 else ""

        # Get commits since tag
        range_spec = f"{tag}..HEAD" if tag else "HEAD"
        result = subprocess.run(
            [
                "git", "log", range_spec,
                "--pretty=format:%H|%h|%s|%an|%ad",
                "--date=short"
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout:
            for line in result.stdout.strip().split("\n"):
                parts = line.split("|")
                if len(parts) >= 5:
                    commit = CommitInfo(
                        hash=parts[0],
                        short_hash=parts[1],
                        message=parts[2],
                        author=parts[3],
                        date=parts[4],
                    )
                    commit.type = categorize_commit(commit.message)
                    commits.append(commit)

    except FileNotFoundError:
        console.print("[yellow]Git not found, skipping commit history[/yellow]")

    return commits


def categorize_commit(message: str) -> str:
    """Categorize a commit message by type."""
    message_lower = message.lower()

    if message_lower.startswith(("feat:", "feat(", "feature:")):
        return "feat"
    elif message_lower.startswith(("fix:", "fix(", "bugfix:")):
        return "fix"
    elif message_lower.startswith(("docs:", "doc:")):
        return "docs"
    elif message_lower.startswith(("breaking:", "breaking change:")):
        return "breaking"
    elif message_lower.startswith(("chore:", "build:", "ci:")):
        return "chore"
    elif message_lower.startswith(("refactor:", "perf:", "test:")):
        return "refactor"
    else:
        return "other"


def generate_release_notes(
    version: str,
    commits: Optional[list[CommitInfo]] = None,
) -> ReleaseNotes:
    """
    Generate release notes from commits.

    Args:
        version: Version for the release
        commits: List of commits, fetches from git if not provided

    Returns:
        ReleaseNotes object
    """
    if commits is None:
        commits = get_commits_since_tag()

    notes = ReleaseNotes(
        version=version,
        date=datetime.now().strftime("%Y-%m-%d"),
    )

    for commit in commits:
        # Clean up message (remove type prefix)
        msg = re.sub(r"^(feat|fix|docs|chore|refactor|perf|test|breaking)(\([^)]+\))?:\s*", "", commit.message)
        msg = f"{msg} ({commit.short_hash})"

        if commit.type == "feat":
            notes.features.append(msg)
        elif commit.type == "fix":
            notes.fixes.append(msg)
        elif commit.type == "docs":
            notes.docs.append(msg)
        elif commit.type == "breaking":
            notes.breaking.append(msg)
        elif commit.type in ("chore", "refactor"):
            pass  # Skip chores
        else:
            notes.other.append(msg)

    return notes


def format_release_notes_markdown(notes: ReleaseNotes) -> str:
    """
    Format release notes as markdown.

    Args:
        notes: ReleaseNotes object

    Returns:
        Formatted markdown string
    """
    lines = [
        f"# 🚀 Release v{notes.version}",
        "",
        f"**Release Date**: {notes.date}",
        "",
    ]

    if notes.breaking:
        lines.extend([
            "## ⚠️ Breaking Changes",
            "",
            *[f"- {item}" for item in notes.breaking],
            "",
        ])

    if notes.features:
        lines.extend([
            "## ✨ New Features",
            "",
            *[f"- {item}" for item in notes.features],
            "",
        ])

    if notes.fixes:
        lines.extend([
            "## 🐛 Bug Fixes",
            "",
            *[f"- {item}" for item in notes.fixes],
            "",
        ])

    if notes.docs:
        lines.extend([
            "## 📚 Documentation",
            "",
            *[f"- {item}" for item in notes.docs],
            "",
        ])

    if notes.other:
        lines.extend([
            "## 🔧 Other Changes",
            "",
            *[f"- {item}" for item in notes.other],
            "",
        ])

    lines.extend([
        "---",
        "",
        "*Generated by UnrealMate | © 2026 G & E ZYNTH*",
    ])

    return "\n".join(lines)


def update_version_file(
    version_file: Path,
    new_version: str,
) -> bool:
    """
    Update the version in a Python version file.

    Args:
        version_file: Path to _version.py
        new_version: New version string

    Returns:
        True if successful
    """
    try:
        content = version_file.read_text(encoding="utf-8")

        # Update __version__
        content = re.sub(
            r'__version__:\s*Final\[str\]\s*=\s*"[^"]+"',
            f'__version__: Final[str] = "{new_version}"',
            content
        )

        # Update __version_info__
        major, minor, patch = parse_version(new_version)
        content = re.sub(
            r'__version_info__:\s*Final\[tuple\[int, int, int\]\]\s*=\s*\([^)]+\)',
            f'__version_info__: Final[tuple[int, int, int]] = ({major}, {minor}, {patch})',
            content
        )

        # Update release date
        content = re.sub(
            r'__release_date__:\s*Final\[str\]\s*=\s*"[^"]+"',
            f'__release_date__: Final[str] = "{datetime.now().strftime("%Y-%m-%d")}"',
            content
        )

        version_file.write_text(content, encoding="utf-8")
        console.print(f"[green]✓ Updated version to {new_version}[/green]")
        return True

    except Exception as e:
        console.print(f"[red]✗ Failed to update version: {e}[/red]")
        return False


def update_pyproject_version(
    pyproject_path: Path,
    new_version: str,
) -> bool:
    """
    Update version in pyproject.toml.

    Args:
        pyproject_path: Path to pyproject.toml
        new_version: New version string

    Returns:
        True if successful
    """
    try:
        content = pyproject_path.read_text(encoding="utf-8")
        content = re.sub(
            r'version\s*=\s*"[^"]+"',
            f'version = "{new_version}"',
            content,
            count=1
        )
        pyproject_path.write_text(content, encoding="utf-8")
        console.print(f"[green]✓ Updated pyproject.toml to {new_version}[/green]")
        return True

    except Exception as e:
        console.print(f"[red]✗ Failed to update pyproject.toml: {e}[/red]")
        return False


def prepare_release(
    project_dir: Path,
    bump_type: BumpType = BumpType.PATCH,
    dry_run: bool = False,
) -> Optional[str]:
    """
    Prepare a new release with version bump and release notes.

    Args:
        project_dir: Project directory
        bump_type: Type of version bump
        dry_run: If True, don't make changes

    Returns:
        New version string if successful
    """
    version_file = project_dir / "unrealmate" / "_version.py"
    pyproject_file = project_dir / "pyproject.toml"
    changelog_file = project_dir / "CHANGELOG.md"

    # Get current version
    if version_file.exists():
        content = version_file.read_text()
        match = re.search(r'__version__.*=.*"([^"]+)"', content)
        current_version = match.group(1) if match else "0.0.0"
    else:
        current_version = "0.0.0"

    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    console.print(f"[cyan]Preparing release: {current_version} → {new_version}[/cyan]")

    # Generate release notes
    notes = generate_release_notes(new_version)
    notes_md = format_release_notes_markdown(notes)

    if dry_run:
        console.print("\n[yellow]Dry run - no changes made[/yellow]")
        console.print("\n[bold]Release Notes Preview:[/bold]")
        console.print(notes_md)
        return new_version

    # Update version files
    if version_file.exists():
        update_version_file(version_file, new_version)

    if pyproject_file.exists():
        update_pyproject_version(pyproject_file, new_version)

    # Update/create changelog
    if changelog_file.exists():
        existing = changelog_file.read_text(encoding="utf-8")
        # Insert new release after the header
        if "# Changelog" in existing:
            parts = existing.split("# Changelog", 1)
            new_content = f"# Changelog\n\n{notes_md}\n\n{parts[1].lstrip()}"
        else:
            new_content = f"{notes_md}\n\n{existing}"
        changelog_file.write_text(new_content, encoding="utf-8")
    else:
        changelog_file.write_text(f"# Changelog\n\n{notes_md}\n", encoding="utf-8")

    console.print("[green]✓ Updated CHANGELOG.md[/green]")
    console.print(f"\n[bold green]🎉 Release v{new_version} prepared![/bold green]")

    return new_version

