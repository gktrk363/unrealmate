import pytest
from typer.testing import CliRunner
from unrealmate.cli import app

runner = CliRunner()


class TestVersion:
    """Version command tests"""
    
    def test_version_shows_output(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "UnrealMate" in result.stdout

    def test_version_shows_version_number(self):
        result = runner.invoke(app, ["version"])
        assert "v0.1.9" in result.stdout or "0.1.9" in result.stdout


class TestDoctor:
    """Doctor command tests"""
    
    def test_doctor_runs(self):
        result = runner. invoke(app, ["doctor"])
        assert result.exit_code == 0
    
    def test_doctor_shows_health(self):
        result = runner. invoke(app, ["doctor"])
        assert "Health" in result.stdout or "Doctor" in result.stdout


class TestGitCommands:
    """Git command tests"""
    
    def test_git_init_runs(self):
        result = runner.invoke(app, ["git", "init"])
        assert result. exit_code == 0
    
    def test_git_lfs_runs(self):
        result = runner.invoke(app, ["git", "lfs"])
        assert result.exit_code == 0
    
    def test_git_clean_dry_run(self):
        result = runner.invoke(app, ["git", "clean", "--dry-run"])
        assert result.exit_code == 0


class TestAssetCommands:
    """Asset command tests"""
    
    def test_asset_scan_runs(self):
        result = runner.invoke(app, ["asset", "scan"])
        assert result.exit_code == 0
    
    def test_asset_organize_dry_run(self):
        result = runner.invoke(app, ["asset", "organize", "--dry-run"])
        assert result.exit_code == 0
    
    def test_asset_duplicates_runs(self):
        result = runner.invoke(app, ["asset", "duplicates"])
        assert result.exit_code == 0


class TestBlueprintCommands:
    """Blueprint command tests"""
    
    def test_blueprint_analyze_runs(self):
        result = runner.invoke(app, ["blueprint", "analyze"])
        assert result.exit_code == 0
    
    def test_blueprint_report_runs(self):
        result = runner.invoke(app, ["blueprint", "report"])
        assert result.exit_code == 0


class TestHelpCommands: 
    """Help command tests"""
    
    def test_main_help(self):
        result = runner. invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage" in result.stdout
    
    def test_git_help(self):
        result = runner.invoke(app, ["git", "--help"])
        assert result.exit_code == 0
    
    def test_asset_help(self):
        result = runner.invoke(app, ["asset", "--help"])
        assert result. exit_code == 0
    
    def test_blueprint_help(self):
        result = runner.invoke(app, ["blueprint", "--help"])
        assert result. exit_code == 0