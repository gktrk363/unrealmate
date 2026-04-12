# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Config Cli Safety Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for destructive config safety semantics."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def _write_config(config_path: Path) -> None:
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


def test_config_init_refuses_to_overwrite_without_force(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)
    config_path = tmp_path / ".unrealmate.toml"
    config_path.write_text("existing = true\n", encoding="utf-8")

    result = runner.invoke(cli.app, ["config", "init"], catch_exceptions=False)

    assert result.exit_code == 1
    assert "CONFIGURATION EXISTS" in result.output
    assert "Re-run with --force" in result.output
    assert config_path.read_text(encoding="utf-8") == "existing = true\n"


def test_config_set_requires_existing_config_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        cli.app,
        ["config", "set", "performance.cache_enabled", "false"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "CONFIGURATION MISSING" in result.output
    assert not (tmp_path / ".unrealmate.toml").exists()


def test_config_set_invalid_key_exits_non_zero_and_preserves_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    config_path = tmp_path / ".unrealmate.toml"
    _write_config(config_path)
    original = config_path.read_text(encoding="utf-8")

    result = runner.invoke(
        cli.app,
        ["config", "set", "signature.author", "Smoke User"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Failed to set signature.author" in result.output
    assert "No config changes were written." in result.output
    assert config_path.read_text(encoding="utf-8") == original


def test_config_set_invalid_value_exits_non_zero_and_preserves_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    config_path = tmp_path / ".unrealmate.toml"
    _write_config(config_path)
    original = config_path.read_text(encoding="utf-8")

    result = runner.invoke(
        cli.app,
        ["config", "set", "performance.max_workers", "many"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Invalid value for performance.max_workers" in result.output
    assert "Current value remains: 4" in result.output
    assert config_path.read_text(encoding="utf-8") == original


def test_config_template_requires_existing_config_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["config", "template", "mobile", "--yes"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "CONFIGURATION MISSING" in result.output
    assert not (tmp_path / ".unrealmate.toml").exists()


def test_config_template_unknown_template_exits_non_zero(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)
    _write_config(tmp_path / ".unrealmate.toml")

    result = runner.invoke(
        cli.app,
        ["config", "template", "cinematic", "--yes"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Unknown template: 'cinematic'" in result.output
