from typer.testing import CliRunner
from unrealmate.cli import app

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "UnrealMate CLI" in result.stdout
