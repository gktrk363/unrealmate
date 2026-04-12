# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Cli
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""P0 stabilization regression tests for UnrealMate CLI."""

from __future__ import annotations
import pytest

from pathlib import Path

from rich.box import ASCII
from typer.testing import CliRunner

import unrealmate.cli as cli
from unrealmate.core import visuals


runner = CliRunner()


class _DummyStream:
    """Small stream stub for encoding fallback tests."""

    def __init__(self, encoding: str, errors: str = "strict") -> None:
        self.encoding = encoding
        self.errors = errors

    def reconfigure(self, **kwargs) -> None:
        if "errors" in kwargs:
            self.errors = kwargs["errors"]


def test_output_fallback_switches_non_utf8_stream_to_replace() -> None:
    stream = _DummyStream("cp1254", errors="strict")

    changed = visuals.configure_output_stream(stream)

    assert changed is True
    assert stream.errors == "replace"
    assert visuals.get_loading_frames("cp1254") == visuals.LOADING_FRAMES_ASCII


def test_safe_spinner_falls_back_to_ascii_line_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(visuals, "ASCII_MODE", True)

    assert visuals.safe_spinner("earth") == "line"


def test_apply_render_mode_switches_box_styles_to_ascii() -> None:
    original_mode = visuals.ASCII_MODE

    try:
        visuals.apply_render_mode(True)

        assert visuals.ASCII_MODE is True
        assert visuals.DOUBLE == ASCII
        assert visuals.ROUNDED == ASCII
        assert visuals.MINIMAL == ASCII
        assert visuals.UE_BOX == ASCII
        assert visuals.GAMING_BOX == ASCII
    finally:
        visuals.apply_render_mode(original_mode)


def test_template_files_have_normalized_patterns() -> None:
    root = Path(__file__).resolve().parents[1]
    gitignore = (root / "unrealmate" / "templates" / "gitignore.template").read_text(encoding="utf-8")
    gitattributes = (root / "unrealmate" / "templates" / "gitattributes.template").read_text(encoding="utf-8")

    assert "*.sln" in gitignore
    assert "*.VC.db" in gitignore
    assert "*.VC.opendb" in gitignore
    assert "*.pdb" in gitignore
    assert "*.ini.bak" in gitignore
    assert ".cache/" in gitignore
    assert "*.rar" in gitignore
    assert "*. sln" not in gitignore
    assert "*. VC.db" not in gitignore
    assert "*.VC. VC.opendb" not in gitignore
    assert "*. pdb" not in gitignore
    assert "*. ini. bak" not in gitignore
    assert ". cache/" not in gitignore
    assert "*. rar" not in gitignore

    assert "*.uasset filter=lfs diff=lfs merge=lfs -text" in gitattributes
    assert "*.ogg filter=lfs diff=lfs merge=lfs -text" in gitattributes
    assert "*.avi filter=lfs diff=lfs merge=lfs -text" in gitattributes
    assert "*.exe filter=lfs diff=lfs merge=lfs -text" in gitattributes
    assert "*. uasset filter=lfs diff=lfs merge=lfs -text" not in gitattributes
    assert "*. ogg filter=lfs diff=lfs merge=lfs -text" not in gitattributes
    assert "*. avi filter=lfs diff=lfs merge=lfs -text" not in gitattributes
    assert "*. exe filter=lfs diff=lfs merge=lfs -text" not in gitattributes


@pytest.mark.skip(reason="Obsolete after UX/CLI architectural refactoring")
def test_automate_organize_uses_misplaced_assets_key(monkeypatch, tmp_path: Path) -> None:
    class _FakeSmartOrganizer:
        def __init__(self, _path: str) -> None:
            self.path = _path

        def analyze(self) -> dict:
            return {"misplaced_assets": 3}

    import unrealmate.core.smart_organizer as smart_organizer

    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)
    monkeypatch.setattr(smart_organizer, "SmartOrganizer", _FakeSmartOrganizer)

    result = runner.invoke(cli.app, ["automate", "organize", str(tmp_path)])

    assert result.exit_code == 0
    assert "Organized 3 files" in result.output


@pytest.mark.skip(reason="Obsolete after UX/CLI architectural refactoring")
def test_marketplace_install_generates_valid_url_and_opens_browser(monkeypatch) -> None:
    opened_urls: list[str] = []
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: opened_urls.append(url) or True)

    asset_name = "Ultra Dynamic Sky"
    expected_url = cli._build_marketplace_search_url(asset_name)
    result = runner.invoke(cli.app, ["marketplace", "install", asset_name])

    assert result.exit_code == 0
    assert opened_urls == [expected_url]
    normalized_output = result.output.replace("\r", "").replace("\n", "")
    assert expected_url in normalized_output
