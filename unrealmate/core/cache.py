"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Caching System                               ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: High-performance caching for expensive operations                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import hashlib
import json
import pickle
import time
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar

from rich.console import Console

console = Console()

T = TypeVar("T")


@dataclass
class CacheEntry:
    """A single cache entry with metadata."""
    key: str
    value: Any
    created_at: float
    expires_at: float
    hits: int = 0
    size_bytes: int = 0


@dataclass
class CacheStats:
    """Statistics for cache performance."""
    hits: int = 0
    misses: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class MemoryCache:
    """In-memory cache with TTL and size limits."""

    def __init__(
        self,
        max_size_mb: int = 100,
        default_ttl_seconds: int = 3600,
    ):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = default_ttl_seconds
        self._cache: dict[str, CacheEntry] = {}
        self._stats = CacheStats()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        entry = self._cache.get(key)

        if entry is None:
            self._stats.misses += 1
            return None

        # Check expiration
        if time.time() > entry.expires_at:
            self.delete(key)
            self._stats.misses += 1
            return None

        entry.hits += 1
        self._stats.hits += 1
        return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds

        Returns:
            True if successful
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        now = time.time()

        # Calculate size
        try:
            size = len(pickle.dumps(value))
        except Exception:
            size = 0

        # Check if we need to evict
        while self._stats.total_size_bytes + size > self.max_size_bytes:
            if not self._evict_oldest():
                break

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + ttl,
            size_bytes=size,
        )

        self._cache[key] = entry
        self._stats.total_size_bytes += size
        self._stats.entry_count = len(self._cache)

        return True

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if key in self._cache:
            entry = self._cache.pop(key)
            self._stats.total_size_bytes -= entry.size_bytes
            self._stats.entry_count = len(self._cache)
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._stats = CacheStats()

    def _evict_oldest(self) -> bool:
        """Evict the oldest cache entry."""
        if not self._cache:
            return False

        oldest_key = min(self._cache, key=lambda k: self._cache[k].created_at)
        self.delete(oldest_key)
        return True

    @property
    def stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._stats


class FileCache:
    """File-based persistent cache."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        default_ttl_hours: int = 24,
    ):
        self.cache_dir = cache_dir or Path.home() / ".unrealmate" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl_hours * 3600
        self._index_file = self.cache_dir / "index.json"
        self._index: dict[str, dict[str, Any]] = self._load_index()

    def _load_index(self) -> dict[str, dict[str, Any]]:
        """Load cache index from disk."""
        if self._index_file.exists():
            try:
                return json.loads(self._index_file.read_text())
            except Exception:
                return {}
        return {}

    def _save_index(self) -> None:
        """Save cache index to disk."""
        self._index_file.write_text(json.dumps(self._index, indent=2))

    def _get_file_path(self, key: str) -> Path:
        """Get file path for a cache key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def get(self, key: str) -> Optional[Any]:
        """Get a value from file cache."""
        if key not in self._index:
            return None

        meta = self._index[key]

        # Check expiration
        if time.time() > meta.get("expires_at", 0):
            self.delete(key)
            return None

        file_path = self._get_file_path(key)
        if not file_path.exists():
            del self._index[key]
            self._save_index()
            return None

        try:
            with open(file_path, "rb") as f:
                return pickle.load(f)
        except Exception:
            self.delete(key)
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl_hours: Optional[int] = None,
    ) -> bool:
        """Set a value in file cache."""
        ttl = (ttl_hours * 3600) if ttl_hours else self.default_ttl
        now = time.time()

        file_path = self._get_file_path(key)

        try:
            with open(file_path, "wb") as f:
                pickle.dump(value, f)

            self._index[key] = {
                "created_at": now,
                "expires_at": now + ttl,
                "file": str(file_path),
            }
            self._save_index()
            return True

        except Exception as e:
            console.print(f"[red]Cache write error: {e}[/red]")
            return False

    def delete(self, key: str) -> bool:
        """Delete a key from file cache."""
        if key in self._index:
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
            del self._index[key]
            self._save_index()
            return True
        return False

    def clear(self) -> None:
        """Clear all cache files."""
        for file in self.cache_dir.glob("*.cache"):
            file.unlink()
        self._index = {}
        self._save_index()


# ═══════════════════════════════════════════════════════════════════════════════
# CACHE DECORATORS
# ═══════════════════════════════════════════════════════════════════════════════

_memory_cache = MemoryCache()


def cached(
    ttl_seconds: int = 3600,
    key_prefix: str = "",
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to cache function results.

    Args:
        ttl_seconds: Cache TTL in seconds
        key_prefix: Prefix for cache key

    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # Try to get from cache
            result = _memory_cache.get(cache_key)
            if result is not None:
                return result

            # Call function and cache result
            result = func(*args, **kwargs)
            _memory_cache.set(cache_key, result, ttl_seconds)
            return result

        return wrapper
    return decorator


def clear_cache() -> None:
    """Clear the global memory cache."""
    _memory_cache.clear()


def get_cache_stats() -> CacheStats:
    """Get global cache statistics."""
    return _memory_cache.stats
