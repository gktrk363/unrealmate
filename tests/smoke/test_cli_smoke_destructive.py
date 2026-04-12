# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Cli Smoke Destructive
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Smoke coverage for destructive stable UnrealMate commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def _read_uproject_plugins(project_root: Path) -> list[dict]:
    uproject = next(project_root.glob("*.uproject"))
    data = json.loads(uproject.read_text(encoding="utf-8"))
    return data.get("Plugins", [])


def test_config_init_force_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["config", "init", "--force"], cwd=fixture_project)
    assert_ok(result)
    config_path = fixture_project / ".unrealmate.toml"
    assert config_path.exists()
    assert "[performance]" in config_path.read_text(encoding="utf-8")


def test_config_set_signature_author_command_smoke(fixture_project: Path, run_cli) -> None:
    # Command from smoke matrix: currently schema does not include signature.author.
    # Smoke verifies explicit failure signal without mutating the config file.
    result = run_cli(["config", "set", "signature.author", "Smoke User"], cwd=fixture_project)
    assert result.exit_code == 1, result.output
    assert "Failed to set signature.author" in result.output
    assert "No config changes were written." in result.output


def test_config_template_mobile_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["config", "template", "mobile", "--yes"], cwd=fixture_project)
    assert_ok(result)
    config_text = (fixture_project / ".unrealmate.toml").read_text(encoding="utf-8")
    assert "max_workers = 2" in config_text
    assert "parallel_processing = false" in config_text


def test_git_init_force_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["git", "init", "--force"], cwd=fixture_project)
    assert_ok(result)
    gitignore = fixture_project / ".gitignore"
    assert gitignore.exists()
    assert "*.sln" in gitignore.read_text(encoding="utf-8")


def test_git_lfs_force_smoke(fixture_project: Path, run_cli, assert_ok, git_lfs_available: bool) -> None:
    if not git_lfs_available:
        pytest.skip("git lfs is unavailable on this runner; skipping integration-dependent smoke test.")

    result = run_cli(["git", "lfs", "--force"], cwd=fixture_project)
    assert_ok(result)
    attrs = fixture_project / ".gitattributes"
    assert attrs.exists()
    assert "filter=lfs" in attrs.read_text(encoding="utf-8")


def test_git_clean_dry_run_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    binaries_dir = fixture_project / "Binaries"
    assert binaries_dir.exists()

    result = run_cli(["git", "clean", "--dry-run", "--yes"], cwd=fixture_project)
    assert_ok(result)
    assert "DRY RUN MODE" in result.output
    assert binaries_dir.exists()


def test_asset_organize_dry_run_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    loose_texture = fixture_project / "Content" / "LooseTexture.png"
    assert loose_texture.exists()

    result = run_cli(
        ["asset", "organize", str(fixture_project / "Content"), "--dry-run", "--yes"],
        cwd=fixture_project,
    )
    assert_ok(result)
    assert "Dry run mode - no files were moved" in result.output
    assert loose_texture.exists()


def test_plugin_install_smoke(
    fixture_project: Path,
    local_plugin_source: Path,
    run_cli,
    assert_ok,
) -> None:
    result = run_cli(
        ["plugin", "install", str(local_plugin_source), "--path", str(fixture_project), "--name", "SmokePlugin"],
        cwd=fixture_project,
    )
    assert_ok(result)
    assert (fixture_project / "Plugins" / "SmokePlugin").exists()


def test_plugin_enable_smoke(
    fixture_project: Path,
    local_plugin_source: Path,
    run_cli,
    assert_ok,
) -> None:
    install_result = run_cli(
        ["plugin", "install", str(local_plugin_source), "--path", str(fixture_project), "--name", "SmokePlugin"],
        cwd=fixture_project,
    )
    assert_ok(install_result)

    result = run_cli(["plugin", "enable", "SmokePlugin", "--path", str(fixture_project)], cwd=fixture_project)
    assert_ok(result)
    plugins = _read_uproject_plugins(fixture_project)
    entry = next((p for p in plugins if p.get("Name") == "SmokePlugin"), None)
    assert entry is not None
    assert entry.get("Enabled") is True


def test_plugin_disable_smoke(
    fixture_project: Path,
    local_plugin_source: Path,
    run_cli,
    assert_ok,
) -> None:
    install_result = run_cli(
        ["plugin", "install", str(local_plugin_source), "--path", str(fixture_project), "--name", "SmokePlugin"],
        cwd=fixture_project,
    )
    assert_ok(install_result)
    enable_result = run_cli(["plugin", "enable", "SmokePlugin", "--path", str(fixture_project)], cwd=fixture_project)
    assert_ok(enable_result)

    result = run_cli(["plugin", "disable", "SmokePlugin", "--path", str(fixture_project)], cwd=fixture_project)
    assert_ok(result)
    plugins = _read_uproject_plugins(fixture_project)
    entry = next((p for p in plugins if p.get("Name") == "SmokePlugin"), None)
    assert entry is not None
    assert entry.get("Enabled") is False


def test_plugin_remove_smoke(
    fixture_project: Path,
    local_plugin_source: Path,
    run_cli,
    assert_ok,
) -> None:
    install_result = run_cli(
        ["plugin", "install", str(local_plugin_source), "--path", str(fixture_project), "--name", "SmokePlugin"],
        cwd=fixture_project,
    )
    assert_ok(install_result)

    result = run_cli(
        ["plugin", "remove", "SmokePlugin", "--path", str(fixture_project), "--yes"],
        cwd=fixture_project,
    )
    assert_ok(result)
    assert ".uproject plugin references are not removed automatically" in result.output
    assert not (fixture_project / "Plugins" / "SmokePlugin").exists()


def test_build_ci_init_github_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(
        ["build", "ci-init", "--platform", "github", "--path", str(fixture_project)],
        cwd=fixture_project,
    )
    assert_ok(result)
    assert (fixture_project / ".github" / "workflows" / "unreal-build.yml").exists()


def test_build_docker_smoke(fixture_project: Path, run_cli, assert_ok) -> None:
    result = run_cli(["build", "docker", "--path", str(fixture_project)], cwd=fixture_project)
    assert_ok(result)
    dockerfile = fixture_project / "Dockerfile"
    assert dockerfile.exists()
    assert "FROM ghcr.io/epicgames/unreal-engine:dev-5.4" in dockerfile.read_text(encoding="utf-8")


def test_report_html_smoke(fixture_project: Path, run_cli, assert_ok, tmp_path: Path) -> None:
    output_path = tmp_path / "report.html"
    result = run_cli(
        ["report", "html", str(fixture_project), "--output", str(output_path)],
        cwd=fixture_project,
    )
    assert_ok(result)
    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    assert "<html" in html.lower()
    assert "Project Report" in html


def test_report_json_smoke(fixture_project: Path, run_cli, assert_ok, tmp_path: Path) -> None:
    output_path = tmp_path / "report.json"
    result = run_cli(
        ["report", "json", str(fixture_project), "--output", str(output_path)],
        cwd=fixture_project,
    )
    assert_ok(result)
    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert "stats" in payload
    assert payload["stats"]["uproject_files"] >= 1
