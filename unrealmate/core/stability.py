"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          UnrealMate - Stability                              ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Stability features, backup, and rollback                           ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Ensures system stability through backups and error handling.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

import shutil
import os
import logging
from datetime import datetime

class StabilityManager:
    """
    Central manager for stability features.
    """
    def __init__(self):
        self.backup_manager = BackupManager()

    def run_safely(self, func, *args, **kwargs):
        """
        Executes a function with error handling and optional rollback.
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Operation failed: {e}")
            # Trigger rollback logic here if needed
            raise

class BackupManager:
    """
    Handles file backups before destructive operations.
    """
    def create_backup(self, source_path: str) -> str:
        """
        Creates a timestamped backup of target path.
        """
        if not os.path.exists(source_path):
            return ""
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{source_path}.backup_{timestamp}"
        
        try:
            if os.path.isdir(source_path):
                shutil.copytree(source_path, backup_path)
            else:
                shutil.copy2(source_path, backup_path)
            logging.info(f"Backup created at: {backup_path}")
            return backup_path
        except Exception as e:
            logging.error(f"Backup failed: {e}")
            return ""

    def restore_backup(self, backup_path: str, target_path: str) -> bool:
        """
        Restores a backup to the target path.
        """
        if not os.path.exists(backup_path):
            return False
            
        try:
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
                shutil.copytree(backup_path, target_path)
            else:
                os.remove(target_path)
                shutil.copy2(backup_path, target_path)
            logging.info(f"Restored from: {backup_path}")
            return True
        except Exception as e:
            logging.error(f"Restore failed: {e}")
            return False
