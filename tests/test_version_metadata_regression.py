# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Version Metadata Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Regression checks for current-version metadata without a release-number bump."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli
from unrealmate import _version


runner = CliRunner()
REPO_ROOT = Path(__file__).resolve().parents[1]


def test_current_version_metadata_is_internally_consistent() -> None:
    assert _version.__version__ == "1.1.4"
    assert _version.__version_info__ == (1, 1, 4)
    assert _version.__description__ == "CLI-first Unreal Engine workflow toolkit"
    assert _version.__status__ == "Release-hardening / merge-ready"


def test_readme_badge_matches_current_version() -> None:
    readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert f"version-{_version.__version__}-blue.svg" in readme_text


def test_version_command_uses_current_metadata_truthfully() -> None:
    result = runner.invoke(cli.app, ["version"], catch_exceptions=False)

    assert result.exit_code == 0
    assert _version.__version__ in result.output
