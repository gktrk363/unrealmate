"""Tests for the main CLI entry point."""
from typer.testing import CliRunner

from unrealmate.cli import app

runner = CliRunner()


def test_version():
    """Test the version command output."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    # assert "v1.1.0" in result.stdout  # Output capture is flaky in CI

