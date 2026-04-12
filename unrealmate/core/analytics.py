"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          UnrealMate - Analytics                              ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  Purpose: Analytics and telemetry tracking                                   ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Controls usage tracking, performance metrics, and error reporting.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

import time
import functools
import logging
from typing import Dict, Any, Optional

class AnalyticsManager:
    """
    Manages anonymous usage statistics and telemetry.
    """
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.session_id = str(int(time.time()))
        self.user_opt_in = False # Default to False for privacy

    def track_command(self, command_name: str, args: Dict[str, Any]) -> None:
        """Tracks command execution if opt-in is enabled."""
        if not self.enabled or not self.user_opt_in:
            return
        
        # In a real implementation, this would send data to a backend
        logging.info(f"Analytics: Command '{command_name}' executed.")

    def opt_in(self) -> None:
        self.user_opt_in = True
        print("Analytics: Opted in to anonymous usage tracking.")

    def opt_out(self) -> None:
        self.user_opt_in = False
        print("Analytics: Opted out of usage tracking.")

class CommandTracker:
    """
    Local tracking for command popularity to show user stats.
    Persists data to ~/.unrealmate/analytics.json
    """
    def __init__(self):
        from pathlib import Path
        
        self.stats: Dict[str, int] = {}
        self.storage_dir = Path.home() / ".unrealmate"
        self.storage_file = self.storage_dir / "analytics.json"
        
        self._load_stats()

    def _load_stats(self) -> None:
        import json
        try:
            if self.storage_file.exists():
                data = json.loads(self.storage_file.read_text(encoding='utf-8'))
                self.stats = data.get("commands", {})
        except Exception as e:
            logging.warning(f"Failed to load analytics: {e}")

    def _save_stats(self) -> None:
        import json
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            data = {"commands": self.stats, "last_updated": str(time.time())}
            self.storage_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        except Exception as e:
            logging.warning(f"Failed to save analytics: {e}")

    def record_usage(self, command: str) -> None:
        if not command:
            return
            
        current = self.stats.get(command, 0)
        self.stats[command] = current + 1
        self._save_stats()

    def get_most_used(self) -> str:
        if not self.stats:
            return "None"
        return max(self.stats, key=self.stats.get)

class PerformanceMetrics:
    """
    Utilities for measuring performance.
    """
    @staticmethod
    def measure_time(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            logging.debug(f"Function '{func.__name__}' took {duration:.4f}s")
            return result
        return wrapper

class SentryIntegration:
    """
    Stub for Sentry error reporting integration.
    """
    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn
        self.initialized = False

    def initialize(self) -> None:
        if self.dsn:
            # import sentry_sdk
            # sentry_sdk.init(self.dsn)
            self.initialized = True
            logging.info("Sentry integration initialized (MOCK).")

    def capture_exception(self, exception: Exception) -> None:
        if self.initialized:
            # sentry_sdk.capture_exception(exception)
            logging.error(f"Sentry captured: {exception}")

