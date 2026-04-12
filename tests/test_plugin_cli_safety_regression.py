# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Plugin Cli Safety Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""CLI regression tests for plugin safety hardening."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

import unrealmate.cli as cli
import unrealmate.core.plugins.manager as plugin_manager_module


runner = CliRunner()


def _create_project(project_root: Path, plugins: list[dict] | None = None) -> Path:
    project_root.mkdir(parents=True, exist_ok=True)
    payload = {
        "FileVersion": 3,
        "EngineAssociation": "5.4",
        "Plugins": plugins or [{"Name": "BasePlugin", "Enabled": True}],
    }
    (project_root / "PluginSafetyProject.uproject").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return project_root


def _create_local_plugin_source(source_root: Path, plugin_name: str = "SmokePlugin") -> Path:
    source_root.mkdir(parents=True, exist_ok=True)
    meta = {
        "FileVersion": 3,
        "VersionName": "1.0",
        "FriendlyName": plugin_name,
        "Description": "Plugin safety test source",
        "Enabled": True,
    }
    (source_root / f"{plugin_name}.uplugin").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (source_root / "README.md").write_text("plugin safety source", encoding="utf-8")
    return source_root


def _read_uproject_plugins(project_root: Path) -> list[dict]:
    uproject = next(project_root.glob("*.uproject"))
    return json.loads(uproject.read_text(encoding="utf-8")).get("Plugins", [])


def test_plugin_install_cli_refuses_missing_project_path(monkeypatch, tmp_path: Path) -> None:
    source = _create_local_plugin_source(tmp_path / "SourcePlugin")
    missing_project = tmp_path / "MissingProject"
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["plugin", "install", str(source), "--path", str(missing_project)],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "PATH NOT FOUND" in result.output
    assert "Plugin commands require an existing Unreal project directory" in result.output


def test_plugin_install_cli_reports_local_mutation_scope(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path / "PluginInstallProject")
    source = _create_local_plugin_source(tmp_path / "SourcePlugin")
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    result = runner.invoke(
        cli.app,
        ["plugin", "install", str(source), "--path", str(project), "--name", "SmokePlugin"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "writes local plugin files under Plugins/" in result.output
    assert "It does not update" in result.output
    assert ".uproject automatically" in result.output
    assert "no automatic rollback" in result.output
    assert "Plugin installed." in result.output
    assert "Plugin files were written under the local Plugins directory." in result.output
    assert ".uproject was not modified. Enable the plugin separately if needed." in result.output
    assert (project / "Plugins" / "SmokePlugin").exists()


def test_plugin_install_cli_partial_copy_failure_is_actionable(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path / "PluginPartialInstallProject")
    source = _create_local_plugin_source(tmp_path / "SourcePlugin")
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    def _patched_copytree(src, dst, *args, **kwargs):
        Path(dst).mkdir(parents=True, exist_ok=True)
        raise PermissionError("locked")

    monkeypatch.setattr(plugin_manager_module.shutil, "copytree", _patched_copytree)

    result = runner.invoke(
        cli.app,
        ["plugin", "install", str(source), "--path", str(project), "--name", "SmokePlugin"],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Plugin install failed." in result.output
    assert "Copy operation failed: locked" in result.output
    assert "Partial local plugin files may remain at" in result.output
    assert ".uproject was not modified." in result.output
    assert "Manual recovery: Delete the partially copied plugin directory and retry." in result.output
    assert (project / "Plugins" / "SmokePlugin").exists()


def test_plugin_enable_cli_reports_uproject_only_mutation(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path / "PluginEnableProject")
    source = _create_local_plugin_source(tmp_path / "SourcePlugin")
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    install_result = runner.invoke(
        cli.app,
        ["plugin", "install", str(source), "--path", str(project), "--name", "SmokePlugin"],
        catch_exceptions=False,
    )
    assert install_result.exit_code == 0

    result = runner.invoke(
        cli.app,
        ["plugin", "enable", "SmokePlugin", "--path", str(project)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "edits the local .uproject only" in result.output
    assert "It does not copy or delete plugin" in result.output
    assert "files, and there is no automatic rollback." in result.output
    assert "Enabled plugin: SmokePlugin" in result.output
    assert "No plugin files were copied or deleted." in result.output
    assert ".uproject was modified locally only." in result.output

    entry = next((plugin for plugin in _read_uproject_plugins(project) if plugin.get("Name") == "SmokePlugin"), None)
    assert entry is not None
    assert entry.get("Enabled") is True


def test_plugin_disable_cli_refuses_missing_uproject_entry(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path / "PluginDisableProject")
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    before = _read_uproject_plugins(project)
    result = runner.invoke(
        cli.app,
        ["plugin", "disable", "GhostPlugin", "--path", str(project)],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Plugin disable failed." in result.output
    assert "No .uproject entry for 'GhostPlugin' was found" in result.output
    assert "No plugin files were copied or deleted." in result.output
    assert "was not modified" in result.output
    assert "Manual recovery:" in result.output
    assert _read_uproject_plugins(project) == before


def test_plugin_remove_cli_keeps_manual_uproject_cleanup_truthful(monkeypatch, tmp_path: Path) -> None:
    project = _create_project(tmp_path / "PluginRemoveProject")
    source = _create_local_plugin_source(tmp_path / "SourcePlugin")
    monkeypatch.setattr(cli.visuals, "animated_loading", lambda *args, **kwargs: None)

    install_result = runner.invoke(
        cli.app,
        ["plugin", "install", str(source), "--path", str(project), "--name", "SmokePlugin"],
        catch_exceptions=False,
    )
    assert install_result.exit_code == 0

    enable_result = runner.invoke(
        cli.app,
        ["plugin", "enable", "SmokePlugin", "--path", str(project)],
        catch_exceptions=False,
    )
    assert enable_result.exit_code == 0

    result = runner.invoke(
        cli.app,
        ["plugin", "remove", "SmokePlugin", "--path", str(project), "--yes"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Removed plugin: SmokePlugin" in result.output
    assert "The local plugin directory was deleted." in result.output
    assert ".uproject plugin references are not removed automatically" in result.output
    assert "Update PluginSafetyProject.uproject manually" in result.output
    assert not (project / "Plugins" / "SmokePlugin").exists()

    entry = next((plugin for plugin in _read_uproject_plugins(project) if plugin.get("Name") == "SmokePlugin"), None)
    assert entry is not None
    assert entry.get("Enabled") is True


def test_plugin_help_surface_is_truthful_about_mutation_scope() -> None:
    install_help = runner.invoke(cli.app, ["plugin", "install", "--help"], catch_exceptions=False)
    assert install_help.exit_code == 0
    assert "Clone or copy a plugin into the local Plugins directory" in install_help.output

    remove_help = runner.invoke(cli.app, ["plugin", "remove", "--help"], catch_exceptions=False)
    assert remove_help.exit_code == 0
    assert "Delete a local plugin directory; .uproject cleanup stays manual" in remove_help.output
