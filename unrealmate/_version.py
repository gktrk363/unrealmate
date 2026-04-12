"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Version Information                          ║
║                                                                              ║
║  Author: G & E ZYNTH                                                         ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Central version management for the package                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers

This is the single source of truth for version information.
All other version references should import from here.
"""

from typing import Final

# ═══════════════════════════════════════════════════════════════════════════════
# VERSION INFORMATION
# ═══════════════════════════════════════════════════════════════════════════════

__version__: Final[str] = "1.1.4"
__version_info__: Final[tuple[int, int, int]] = (1, 1, 4)

# ═══════════════════════════════════════════════════════════════════════════════
# PACKAGE METADATA
# ═══════════════════════════════════════════════════════════════════════════════

__title__: Final[str] = "unrealmate"
__description__: Final[str] = "CLI-first Unreal Engine workflow toolkit"
__author__: Final[str] = "G & E ZYNTH"
__author_email__: Final[str] = "gktrk363@github.com"
__license__: Final[str] = "MIT"
__copyright__: Final[str] = "© 2026 G & E ZYNTH"

# ═══════════════════════════════════════════════════════════════════════════════
# URLS
# ═══════════════════════════════════════════════════════════════════════════════

__url__: Final[str] = "https://github.com/gktrk363/unrealmate"
__repository__: Final[str] = "https://github.com/gktrk363/unrealmate"
__documentation__: Final[str] = "https://github.com/gktrk363/unrealmate#readme"
__bug_tracker__: Final[str] = "https://github.com/gktrk363/unrealmate/issues"

# ═══════════════════════════════════════════════════════════════════════════════
# RELEASE INFO
# ═══════════════════════════════════════════════════════════════════════════════

__release_date__: Final[str] = "2026-04-12"
__status__: Final[str] = "Release-hardening / merge-ready"

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def get_version() -> str:
    """Return the current version string."""
    return __version__


def get_version_info() -> tuple[int, int, int]:
    """Return the version as a tuple of (major, minor, patch)."""
    return __version_info__


def get_full_version() -> str:
    """Return a formatted version string with package name."""
    return f"{__title__} v{__version__}"


def get_banner_info() -> dict[str, str]:
    """Return all info needed for the CLI banner."""
    return {
        "title": __title__,
        "version": __version__,
        "author": __author__,
        "url": __url__,
        "description": __description__,
        "copyright": __copyright__,
    }

