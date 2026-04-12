# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Notify Config Alignment
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Stabilization tests for report notify semantics and config-schema alignment."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli
from unrealmate.core.config import get_config_value, init_config, load_config, set_config_value


runner = CliRunner()


def test_notification_webhook_config_round_trip(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    assert init_config(force=True) is True
    assert set_config_value("notification.webhook_url", "https://hooks.example.invalid/abc") is True
    assert get_config_value("notification.webhook_url") == "https://hooks.example.invalid/abc"
    assert load_config().notification.webhook_url == "https://hooks.example.invalid/abc"


def test_report_notify_cli_is_truthful_about_local_only_behavior(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    result = runner.invoke(
        cli.app,
        ["report", "notify", "hello team"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Local notification entry written." in result.output
    assert "`report notify` is local-only." in result.output
    assert "Webhook delivery is not implemented" in result.output


def test_report_notify_cli_failure_exits_non_zero(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    import builtins

    real_open = builtins.open

    def _failing_open(*args, **kwargs):  # type: ignore[no-untyped-def]
        target = args[0] if args else ""
        if "notification_log.txt" in str(target):
            raise OSError("disk full")
        return real_open(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", _failing_open)

    result = runner.invoke(
        cli.app,
        ["report", "notify", "hello team"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Failed to write local notification log" in result.output


def test_config_validate_accepts_notification_section(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    init_result = runner.invoke(cli.app, ["config", "init", "--force"], catch_exceptions=False)
    assert init_result.exit_code == 0

    set_result = runner.invoke(
        cli.app,
        ["config", "set", "notification.webhook_url", "https://hooks.example.invalid/abc"],
        catch_exceptions=False,
    )
    assert set_result.exit_code == 0
    assert "Set notification.webhook_url" in set_result.output

    validate_result = runner.invoke(cli.app, ["config", "validate"], catch_exceptions=False)
    assert validate_result.exit_code == 0
    assert "Unknown section: 'notification'" not in validate_result.output
    assert "notification.webhook_url must be string" not in validate_result.output
