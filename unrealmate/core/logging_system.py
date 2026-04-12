"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Advanced Logging System                      ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Enhanced logging with rotation, formatting, and handlers           ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.logging import RichHandler

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# LOG LEVELS
# ═══════════════════════════════════════════════════════════════════════════════


class LogLevel:
    """Log level constants."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    SUCCESS = 25  # Custom level between INFO and WARNING


# Register custom SUCCESS level
logging.addLevelName(LogLevel.SUCCESS, "SUCCESS")


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM FORMATTERS
# ═══════════════════════════════════════════════════════════════════════════════


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter."""

    COLORS = {
        logging.DEBUG: "\033[36m",     # Cyan
        logging.INFO: "\033[32m",      # Green
        logging.WARNING: "\033[33m",   # Yellow
        logging.ERROR: "\033[31m",     # Red
        logging.CRITICAL: "\033[35m",  # Magenta
        LogLevel.SUCCESS: "\033[92m",  # Bright Green
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGER CLASS
# ═══════════════════════════════════════════════════════════════════════════════


class UnrealMateLogger:
    """Enhanced logger for UnrealMate."""

    def __init__(
        self,
        name: str = "unrealmate",
        level: int = logging.INFO,
        log_dir: Optional[Path] = None,
    ):
        self.name = name
        self.log_dir = log_dir or Path.home() / ".unrealmate" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._logger.handlers.clear()

        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Setup log handlers."""
        # Console handler with Rich
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
        )
        console_handler.setLevel(logging.INFO)
        self._logger.addHandler(console_handler)

        # File handler with rotation
        file_handler = RotatingFileHandler(
            self.log_dir / f"{self.name}.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        ))
        self._logger.addHandler(file_handler)

        # JSON file handler for structured logs
        json_handler = TimedRotatingFileHandler(
            self.log_dir / f"{self.name}.json",
            when="midnight",
            backupCount=7,
            encoding="utf-8",
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(JsonFormatter())
        self._logger.addHandler(json_handler)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)

    def success(self, message: str, **kwargs: Any) -> None:
        """Log success message."""
        self._log(LogLevel.SUCCESS, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self._logger.exception(message, extra={"extra_data": kwargs})

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        """Internal log method."""
        self._logger.log(level, message, extra={"extra_data": kwargs})

    def set_level(self, level: int) -> None:
        """Set log level."""
        self._logger.setLevel(level)

    def add_handler(self, handler: logging.Handler) -> None:
        """Add a custom handler."""
        self._logger.addHandler(handler)

    def get_log_file(self) -> Path:
        """Get the main log file path."""
        return self.log_dir / f"{self.name}.log"

    def clear_logs(self) -> int:
        """Clear all log files and return count."""
        count = 0
        for log_file in self.log_dir.glob("*"):
            if log_file.is_file():
                log_file.unlink()
                count += 1
        return count


# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXT LOGGER
# ═══════════════════════════════════════════════════════════════════════════════


class ContextLogger:
    """Logger with context information."""

    def __init__(self, logger: UnrealMateLogger, context: str):
        self._logger = logger
        self._context = context

    def _format(self, message: str) -> str:
        return f"[{self._context}] {message}"

    def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(self._format(message), **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(self._format(message), **kwargs)

    def success(self, message: str, **kwargs: Any) -> None:
        self._logger.success(self._format(message), **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(self._format(message), **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._logger.error(self._format(message), **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._logger.critical(self._format(message), **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL LOGGER
# ═══════════════════════════════════════════════════════════════════════════════

# Global logger instance
logger = UnrealMateLogger()


def get_logger(context: Optional[str] = None) -> UnrealMateLogger | ContextLogger:
    """
    Get the global logger, optionally with context.

    Args:
        context: Optional context string

    Returns:
        Logger instance
    """
    if context:
        return ContextLogger(logger, context)
    return logger


def configure_logging(
    level: int = logging.INFO,
    log_dir: Optional[Path] = None,
) -> None:
    """
    Configure global logging.

    Args:
        level: Log level
        log_dir: Log directory
    """
    global logger
    logger = UnrealMateLogger(level=level, log_dir=log_dir)

