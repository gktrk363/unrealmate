# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Config Template Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for config template trust hardening."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def test_config_template_cli_dry_run_does_not_modify_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    config_path = tmp_path / ".unrealmate.toml"
    config_path.write_text(
        """version = "1.0.0"

[performance]
cache_enabled = true
cache_ttl_hours = 24
max_cache_size_mb = 100
parallel_processing = true
max_workers = 4
""",
        encoding="utf-8",
    )
    original = config_path.read_text(encoding="utf-8")

    result = runner.invoke(
        cli.app,
        ["config", "template", "mobile", "--dry-run", "--yes"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "DRY RUN MODE" in result.output
    assert "This replaces the performance section" in result.output
    assert "rollback snapshot" in result.output
    assert config_path.read_text(encoding="utf-8") == original
