# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Conftest
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Smoke test fixtures for stable UnrealMate CLI commands."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Callable, Sequence

import pytest
from typer.testing import CliRunner

import unrealmate.cli as cli


runner = CliRunner()


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _create_fixture_project(project_root: Path) -> Path:
    """Create a minimal Unreal-like project layout used by smoke tests."""
    project_root.mkdir(parents=True, exist_ok=True)

    uproject = {
        "FileVersion": 3,
        "EngineAssociation": "5.4",
        "Category": "Games",
        "Description": "Smoke fixture project",
        "Plugins": [{"Name": "BasePlugin", "Enabled": True}],
    }
    _write_text(project_root / "SmokeProject.uproject", json.dumps(uproject, indent=2))

    _write_text(
        project_root / ".unrealmate.toml",
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
""",
    )

    _write_text(project_root / ".gitignore", "Saved/\nIntermediate/\n")
    _write_text(project_root / ".gitattributes", "*.uasset filter=lfs diff=lfs merge=lfs -text\n")

    # Content fixture for asset/performance/report tests.
    _write_bytes(project_root / "Content" / "Textures" / "T_Hero.png", b"\x89PNG\r\n\x1a\nSMOKE")
    _write_bytes(project_root / "Content" / "Audio" / "S_Theme.wav", b"RIFFSMOKEWAVE")
    _write_bytes(project_root / "Content" / "Blueprints" / "BP_Test.uasset", b"UEASSET_SMOKE")
    _write_bytes(project_root / "Content" / "Maps" / "L_Test.umap", b"UEMAP_SMOKE")
    _write_bytes(project_root / "Content" / "A" / "Duplicate.png", b"DUPLICATE_BYTES")
    _write_bytes(project_root / "Content" / "B" / "Duplicate.png", b"DUPLICATE_BYTES")
    _write_bytes(project_root / "Content" / "LooseTexture.png", b"MOVE_ME")

    # Performance fixtures.
    _write_text(
        project_root / "Saved" / "Profiling" / "frame_metrics.csv",
        "Name,Value,Unit\nFrameTime,16.5,ms\nDrawCalls,120,count\n",
    )
    _write_text(
        project_root / "Shaders" / "TestShader.usf",
        "float4 MainPS() : SV_Target { float3 n = normalize(float3(1,1,1)); return float4(n,1); }\n",
    )

    # Plugin fixture for plugin list command.
    base_plugin = {
        "FileVersion": 3,
        "VersionName": "1.0",
        "FriendlyName": "BasePlugin",
        "Description": "Built-in smoke plugin",
        "Enabled": True,
    }
    _write_text(
        project_root / "Plugins" / "BasePlugin" / "BasePlugin.uplugin",
        json.dumps(base_plugin, indent=2),
    )

    # Cleanup targets for git clean smoke command.
    _write_bytes(project_root / "Binaries" / "Win64" / "Smoke.bin", b"SMOKE_BIN")
    _write_bytes(project_root / "Intermediate" / "Build" / "temp.obj", b"SMOKE_OBJ")
    _write_text(project_root / "Saved" / "Logs" / "Smoke.log", "log")

    return project_root


def _create_local_plugin_source(source_root: Path) -> Path:
    source_root.mkdir(parents=True, exist_ok=True)
    plugin_meta = {
        "FileVersion": 3,
        "VersionName": "1.0",
        "FriendlyName": "SmokePlugin",
        "Description": "Smoke install source plugin",
        "Enabled": True,
    }
    _write_text(source_root / "SmokePlugin.uplugin", json.dumps(plugin_meta, indent=2))
    _write_text(source_root / "README.md", "Smoke plugin source")
    return source_root


def _has_git_lfs() -> bool:
    try:
        proc = subprocess.run(["git", "lfs", "version"], capture_output=True, text=True)
    except FileNotFoundError:
        return False
    return proc.returncode == 0


@pytest.fixture(autouse=True)
def disable_animations(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid waiting for animated_loading delays in smoke tests."""
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)


@pytest.fixture
def fixture_project(tmp_path: Path) -> Path:
    return _create_fixture_project(tmp_path / "SmokeProject")


@pytest.fixture
def local_plugin_source(tmp_path: Path) -> Path:
    return _create_local_plugin_source(tmp_path / "SmokePluginSource")


@pytest.fixture(scope="session")
def git_lfs_available() -> bool:
    return _has_git_lfs()


@pytest.fixture
def run_cli(monkeypatch: pytest.MonkeyPatch) -> Callable[[Sequence[str], Path | None], object]:
    """
    Invoke UnrealMate CLI with optional cwd isolation.

    Returns:
        Function(args, cwd=None) -> typer.testing.Result
    """

    def _run(args: Sequence[str], cwd: Path | None = None):
        if cwd is not None:
            monkeypatch.chdir(cwd)
        return runner.invoke(cli.app, list(args), catch_exceptions=False)

    return _run


@pytest.fixture
def assert_ok() -> Callable[[object], None]:
    def _assert_ok(result) -> None:
        assert result.exit_code == 0, result.output

    return _assert_ok
