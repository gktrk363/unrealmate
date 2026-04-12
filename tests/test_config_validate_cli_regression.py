# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Config Validate Cli Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for config validate truthfulness and status wording."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def test_config_validate_missing_file_exits_non_zero(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(cli.app, ["config", "validate"], catch_exceptions=False)

    assert result.exit_code == 1
    assert "CONFIGURATION MISSING" in result.output


def test_config_validate_valid_file_reports_schema_success(monkeypatch, tmp_path: Path) -> None:
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

[signature]
show_banner = true
compact_banner = false
show_footer = true
color_theme = "cyan_magenta"

[git]
auto_lfs = true
commit_template_enabled = true
pre_commit_hooks = true

[notification]
webhook_url = ""
""",
        encoding="utf-8",
    )

    result = runner.invoke(cli.app, ["config", "validate"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Validation passed with no schema issues." in result.output
    assert "local TOML structure and value types only" in result.output


def test_config_validate_parse_failure_exits_non_zero(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)
    (tmp_path / ".unrealmate.toml").write_text("[performance\nbroken = true\n", encoding="utf-8")

    result = runner.invoke(cli.app, ["config", "validate"], catch_exceptions=False)

    assert result.exit_code == 1
    assert "VALIDATION FAILED" in result.output
    assert "Could not parse .unrealmate.toml" in result.output
