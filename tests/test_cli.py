"""Tests for the main CLI entry point."""

def test_imports():
    """Test that the package and CLI module can be imported."""
    import unrealmate
    from unrealmate import cli
    assert unrealmate.__version__ is not None
    assert cli is not None

