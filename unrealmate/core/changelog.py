"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Changelog Generator                          ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Automatic changelog generation from git history                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


@dataclass
class ChangelogEntry:
    """A single changelog entry."""
    type: str
    scope: Optional[str]
    message: str
    hash: str
    date: str
    author: str
    breaking: bool = False


@dataclass
class ChangelogVersion:
    """A version entry in the changelog."""
    version: str
    date: str
    entries: list[ChangelogEntry] = field(default_factory=list)

    @property
    def features(self) -> list[ChangelogEntry]:
        return [e for e in self.entries if e.type == "feat"]

    @property
    def fixes(self) -> list[ChangelogEntry]:
        return [e for e in self.entries if e.type == "fix"]

    @property
    def docs(self) -> list[ChangelogEntry]:
        return [e for e in self.entries if e.type == "docs"]

    @property
    def breaking_changes(self) -> list[ChangelogEntry]:
        return [e for e in self.entries if e.breaking]


class ChangelogGenerator:
    """Generates changelogs from git commit history."""

    # Conventional commit pattern
    COMMIT_PATTERN = re.compile(
        r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
        r"(?:\((?P<scope>[^)]+)\))?"
        r"(?P<breaking>!)?"
        r":\s*(?P<message>.+)$",
        re.IGNORECASE
    )

    TYPE_LABELS = {
        "feat": "✨ Features",
        "fix": "🐛 Bug Fixes",
        "docs": "📚 Documentation",
        "style": "💄 Styles",
        "refactor": "♻️ Code Refactoring",
        "perf": "⚡ Performance",
        "test": "✅ Tests",
        "build": "📦 Build System",
        "ci": "👷 CI/CD",
        "chore": "🔧 Chores",
        "revert": "⏪ Reverts",
    }

    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path or Path.cwd()

    def get_tags(self) -> list[str]:
        """Get all version tags from git."""
        try:
            result = subprocess.run(
                ["git", "tag", "--sort=-creatordate"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )
            if result.returncode == 0:
                return [t for t in result.stdout.strip().split("\n") if t.startswith("v")]
            return []
        except Exception:
            return []

    def get_commits_between(
        self,
        from_ref: Optional[str] = None,
        to_ref: str = "HEAD",
    ) -> list[ChangelogEntry]:
        """Get commits between two refs."""
        range_spec = f"{from_ref}..{to_ref}" if from_ref else to_ref

        try:
            result = subprocess.run(
                [
                    "git", "log", range_spec,
                    "--pretty=format:%H|%h|%s|%an|%ad",
                    "--date=short",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            if result.returncode != 0:
                return []

            entries = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) < 5:
                    continue

                full_hash, short_hash, subject, author, date = parts[:5]
                entry = self._parse_commit(subject, short_hash, date, author)
                if entry:
                    entries.append(entry)

            return entries

        except Exception as e:
            console.print(f"[red]Error getting commits: {e}[/red]")
            return []

    def _parse_commit(
        self,
        subject: str,
        hash: str,
        date: str,
        author: str,
    ) -> Optional[ChangelogEntry]:
        """Parse a commit message into a ChangelogEntry."""
        match = self.COMMIT_PATTERN.match(subject)

        if match:
            return ChangelogEntry(
                type=match.group("type").lower(),
                scope=match.group("scope"),
                message=match.group("message"),
                hash=hash,
                date=date,
                author=author,
                breaking=bool(match.group("breaking")),
            )

        # Non-conventional commit
        return ChangelogEntry(
            type="other",
            scope=None,
            message=subject,
            hash=hash,
            date=date,
            author=author,
        )

    def generate(self, include_unreleased: bool = True) -> list[ChangelogVersion]:
        """Generate changelog from git history."""
        tags = self.get_tags()
        versions = []

        # Unreleased changes
        if include_unreleased:
            last_tag = tags[0] if tags else None
            unreleased_entries = self.get_commits_between(last_tag, "HEAD")
            if unreleased_entries:
                versions.append(ChangelogVersion(
                    version="Unreleased",
                    date=datetime.now().strftime("%Y-%m-%d"),
                    entries=unreleased_entries,
                ))

        # Released versions
        for i, tag in enumerate(tags):
            prev_tag = tags[i + 1] if i + 1 < len(tags) else None
            entries = self.get_commits_between(prev_tag, tag)

            # Get tag date
            try:
                result = subprocess.run(
                    ["git", "log", "-1", "--format=%ad", "--date=short", tag],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                )
                date = result.stdout.strip() if result.returncode == 0 else ""
            except Exception:
                date = ""

            versions.append(ChangelogVersion(
                version=tag,
                date=date,
                entries=entries,
            ))

        return versions

    def format_markdown(self, versions: list[ChangelogVersion]) -> str:
        """Format changelog as markdown."""
        lines = [
            "# Changelog",
            "",
            "All notable changes to UnrealMate will be documented in this file.",
            "",
            "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),",
            "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
            "",
        ]

        for version in versions:
            lines.append(f"## [{version.version}] - {version.date}")
            lines.append("")

            # Group entries by type
            entries_by_type: dict[str, list[ChangelogEntry]] = {}
            for entry in version.entries:
                if entry.type not in entries_by_type:
                    entries_by_type[entry.type] = []
                entries_by_type[entry.type].append(entry)

            # Breaking changes first
            if version.breaking_changes:
                lines.append("### ⚠️ BREAKING CHANGES")
                lines.append("")
                for entry in version.breaking_changes:
                    scope = f"**{entry.scope}**: " if entry.scope else ""
                    lines.append(f"- {scope}{entry.message} ({entry.hash})")
                lines.append("")

            # Other changes by type
            for entry_type, label in self.TYPE_LABELS.items():
                type_entries = entries_by_type.get(entry_type, [])
                type_entries = [e for e in type_entries if not e.breaking]

                if type_entries:
                    lines.append(f"### {label}")
                    lines.append("")
                    for entry in type_entries:
                        scope = f"**{entry.scope}**: " if entry.scope else ""
                        lines.append(f"- {scope}{entry.message} ({entry.hash})")
                    lines.append("")

        lines.extend([
            "---",
            "",
            "*Generated by UnrealMate | © 2026 gktrk363*",
        ])

        return "\n".join(lines)

    def write(
        self,
        output_path: Optional[Path] = None,
        include_unreleased: bool = True,
    ) -> Path:
        """
        Generate and write changelog to file.

        Args:
            output_path: Output file path
            include_unreleased: Include unreleased changes

        Returns:
            Path to written file
        """
        output_path = output_path or self.repo_path / "CHANGELOG.md"
        versions = self.generate(include_unreleased)
        content = self.format_markdown(versions)

        output_path.write_text(content, encoding="utf-8")
        console.print(f"[green]✓ Changelog written to {output_path}[/green]")

        return output_path


def generate_changelog(
    repo_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Generate a changelog file.

    Args:
        repo_path: Repository path
        output_path: Output file path

    Returns:
        Path to generated file
    """
    generator = ChangelogGenerator(repo_path)
    return generator.write(output_path)
