"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Error Handling                               ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Standardized error handling and custom exceptions                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from rich.console import Console
from rich.panel import Panel

console = Console()

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════════════════════════
# ERROR CODES
# ═══════════════════════════════════════════════════════════════════════════════


class ErrorCode(Enum):
    """Standard error codes."""
    # General errors (1-99)
    UNKNOWN = auto()
    INVALID_ARGUMENT = auto()
    MISSING_ARGUMENT = auto()
    PERMISSION_DENIED = auto()
    OPERATION_CANCELLED = auto()

    # File/Path errors (100-199)
    FILE_NOT_FOUND = auto()
    DIRECTORY_NOT_FOUND = auto()
    PATH_EXISTS = auto()
    INVALID_PATH = auto()
    READ_ERROR = auto()
    WRITE_ERROR = auto()

    # Project errors (200-299)
    PROJECT_NOT_FOUND = auto()
    INVALID_PROJECT = auto()
    MISSING_UPROJECT = auto()
    ENGINE_NOT_FOUND = auto()

    # Build errors (300-399)
    BUILD_FAILED = auto()
    COOK_FAILED = auto()
    PACKAGE_FAILED = auto()
    COMPILE_ERROR = auto()

    # Git errors (400-499)
    NOT_A_REPOSITORY = auto()
    GIT_NOT_FOUND = auto()
    LFS_NOT_INSTALLED = auto()
    MERGE_CONFLICT = auto()

    # Config errors (500-599)
    CONFIG_NOT_FOUND = auto()
    INVALID_CONFIG = auto()
    CONFIG_PARSE_ERROR = auto()

    # Network errors (600-699)
    CONNECTION_ERROR = auto()
    TIMEOUT_ERROR = auto()
    API_ERROR = auto()


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM EXCEPTIONS
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ErrorContext:
    """Additional context for an error."""
    file: Optional[str] = None
    line: Optional[int] = None
    function: Optional[str] = None
    suggestions: list[str] = None
    docs_url: Optional[str] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


class UnrealMateError(Exception):
    """Base exception for all UnrealMate errors."""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.UNKNOWN,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or ErrorContext()
        self.cause = cause

    def __str__(self) -> str:
        return f"[{self.code.name}] {self.message}"

    def format_rich(self) -> str:
        """Format error for rich console output."""
        lines = [f"[bold red]❌ Error:[/bold red] {self.message}"]

        if self.context.suggestions:
            lines.append("\n[bold cyan]💡 Suggestions:[/bold cyan]")
            for suggestion in self.context.suggestions:
                lines.append(f"  • {suggestion}")

        if self.context.docs_url:
            lines.append(f"\n[dim]📚 Docs: {self.context.docs_url}[/dim]")

        return "\n".join(lines)


class FileError(UnrealMateError):
    """File-related errors."""

    def __init__(self, message: str, path: str, **kwargs: Any):
        context = ErrorContext(file=path, suggestions=[
            f"Check if the file exists: {path}",
            "Verify file permissions",
        ])
        super().__init__(message, context=context, **kwargs)
        self.path = path


class ProjectError(UnrealMateError):
    """Project-related errors."""

    def __init__(self, message: str, project_path: str = "", **kwargs: Any):
        context = ErrorContext(suggestions=[
            "Make sure you're in an Unreal Engine project directory",
            "Check if .uproject file exists",
            "Run 'unrealmate doctor' to diagnose issues",
        ])
        super().__init__(message, code=ErrorCode.PROJECT_NOT_FOUND, context=context, **kwargs)


class BuildError(UnrealMateError):
    """Build-related errors."""

    def __init__(self, message: str, **kwargs: Any):
        context = ErrorContext(suggestions=[
            "Check the build logs for details",
            "Make sure all dependencies are installed",
            "Try rebuilding the project",
        ])
        super().__init__(message, code=ErrorCode.BUILD_FAILED, context=context, **kwargs)


class ConfigError(UnrealMateError):
    """Configuration-related errors."""

    def __init__(self, message: str, config_path: str = "", **kwargs: Any):
        context = ErrorContext(
            file=config_path,
            suggestions=[
                "Run 'unrealmate config init' to create a default config",
                "Check TOML syntax in your config file",
            ]
        )
        super().__init__(message, code=ErrorCode.INVALID_CONFIG, context=context, **kwargs)


class GitError(UnrealMateError):
    """Git-related errors."""

    def __init__(self, message: str, **kwargs: Any):
        context = ErrorContext(suggestions=[
            "Make sure Git is installed and in PATH",
            "Check if you're in a Git repository",
            "Run 'git status' to see the current state",
        ])
        super().__init__(message, code=ErrorCode.NOT_A_REPOSITORY, context=context, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════════════════


class ErrorHandler:
    """Central error handling and formatting."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self._handlers: dict[type, Callable[[Exception], None]] = {}

    def register(
        self,
        exception_type: type,
        handler: Callable[[Exception], None],
    ) -> None:
        """Register a custom handler for an exception type."""
        self._handlers[exception_type] = handler

    def handle(self, error: Exception) -> int:
        """
        Handle an exception and return exit code.

        Args:
            error: Exception to handle

        Returns:
            Exit code
        """
        # Check for custom handler
        for exc_type, handler in self._handlers.items():
            if isinstance(error, exc_type):
                handler(error)
                return 1

        # Handle UnrealMateError
        if isinstance(error, UnrealMateError):
            console.print(Panel(
                error.format_rich(),
                title="[red]UnrealMate Error[/red]",
                border_style="red",
            ))
            if self.debug and error.cause:
                console.print("\n[dim]Caused by:[/dim]")
                console.print_exception()
            return error.code.value

        # Handle generic exceptions
        console.print(f"[bold red]❌ Unexpected error:[/bold red] {error}")
        if self.debug:
            console.print_exception()
        return 1

    def wrap(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to wrap a function with error handling.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                exit_code = self.handle(e)
                sys.exit(exit_code)

        return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════════════════════════

# Global error handler
error_handler = ErrorHandler()


def handle_errors(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to handle errors in a function."""
    return error_handler.wrap(func)


def reraise_as(
    original_type: type,
    new_type: type[UnrealMateError],
    message: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to re-raise an exception as a different type.

    Args:
        original_type: Original exception type
        new_type: New exception type
        message: Optional custom message

    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except original_type as e:
                raise new_type(message or str(e), cause=e) from e

        return wrapper
    return decorator


def show_error(
    message: str,
    suggestions: Optional[list[str]] = None,
    code: ErrorCode = ErrorCode.UNKNOWN,
) -> None:
    """
    Display a formatted error message.

    Args:
        message: Error message
        suggestions: Optional suggestions
        code: Error code
    """
    error = UnrealMateError(
        message,
        code=code,
        context=ErrorContext(suggestions=suggestions or []),
    )
    console.print(error.format_rich())


def show_warning(message: str) -> None:
    """Display a warning message."""
    console.print(f"[bold yellow]⚠️  Warning:[/bold yellow] {message}")
