"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        UnrealMate - logger.py                                ║
║                                                                              ║
║  Author: gktrk363                                                           ║
║  Purpose: Comprehensive logging system                                      ║
║  Created: 2026-01-23                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Logging system for UnrealMate with debug mode and file rotation.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime


class UnrealMateLogger:
    """Custom logger for UnrealMate with file and console output."""
    
    def __init__(self, name: str = "unrealmate", debug: bool = False):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            debug: Enable debug mode
        """
        self.logger = logging.getLogger(name)
        self.debug_mode = debug
        
        # Set level based on debug mode
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (only in debug mode)
        if debug:
            self._setup_file_handler()
    
    def _setup_file_handler(self):
        """Setup file logging handler."""
        log_dir = Path.cwd() / ".unrealmate" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"unrealmate_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)


# Global logger instance
_global_logger: Optional[UnrealMateLogger] = None


def get_logger(debug: bool = False) -> UnrealMateLogger:
    """
    Get global logger instance.
    
    Args:
        debug: Enable debug mode
        
    Returns:
        UnrealMateLogger: Logger instance
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = UnrealMateLogger(debug=debug)
    
    return _global_logger


# © 2026 gktrk363 - Crafted with passion for Unreal Engine developers
