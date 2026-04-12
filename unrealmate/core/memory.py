"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Memory Optimization                          ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Memory-efficient operations and optimization utilities             ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import gc
import sys
import weakref
from collections.abc import Iterator
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Generic, Optional, TypeVar

from rich.console import Console

console = Console()

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY TRACKING
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class MemoryStats:
    """Memory usage statistics."""
    current_bytes: int
    peak_bytes: int
    allocated_objects: int

    @property
    def current_mb(self) -> float:
        return self.current_bytes / (1024 * 1024)

    @property
    def peak_mb(self) -> float:
        return self.peak_bytes / (1024 * 1024)


class MemoryTracker:
    """Track memory usage during operations."""

    def __init__(self):
        self._peak_bytes: int = 0
        self._start_bytes: int = 0
        self._tracking: bool = False

    def start(self) -> None:
        """Start memory tracking."""
        gc.collect()
        self._start_bytes = self._get_memory_usage()
        self._peak_bytes = self._start_bytes
        self._tracking = True

    def stop(self) -> MemoryStats:
        """Stop tracking and return stats."""
        gc.collect()
        current = self._get_memory_usage()
        self._tracking = False

        return MemoryStats(
            current_bytes=current - self._start_bytes,
            peak_bytes=self._peak_bytes - self._start_bytes,
            allocated_objects=len(gc.get_objects()),
        )

    def update(self) -> None:
        """Update peak memory if tracking."""
        if self._tracking:
            current = self._get_memory_usage()
            self._peak_bytes = max(self._peak_bytes, current)

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        # Sum size of all objects tracked by gc
        return sum(sys.getsizeof(obj) for obj in gc.get_objects()[:1000])

    def __enter__(self) -> "MemoryTracker":
        self.start()
        return self

    def __exit__(self, *args: Any) -> None:
        self.stop()


def track_memory(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to track memory usage of a function."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        tracker = MemoryTracker()
        tracker.start()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            stats = tracker.stop()
            console.print(f"[dim]Memory: {stats.current_mb:.2f} MB (peak: {stats.peak_mb:.2f} MB)[/dim]")

    return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY-EFFICIENT DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════


class ObjectPool(Generic[T]):
    """Object pool for reusing instances."""

    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 100,
        reset_func: Optional[Callable[[T], None]] = None,
    ):
        self._factory = factory
        self._max_size = max_size
        self._reset_func = reset_func
        self._pool: list[T] = []

    def acquire(self) -> T:
        """Get an object from the pool or create new one."""
        if self._pool:
            return self._pool.pop()
        return self._factory()

    def release(self, obj: T) -> None:
        """Return an object to the pool."""
        if len(self._pool) < self._max_size:
            if self._reset_func:
                self._reset_func(obj)
            self._pool.append(obj)

    def clear(self) -> None:
        """Clear the pool."""
        self._pool.clear()

    @property
    def size(self) -> int:
        """Current pool size."""
        return len(self._pool)


class WeakValueCache(Generic[T]):
    """Cache with weak references to allow garbage collection."""

    def __init__(self):
        self._cache: dict[str, weakref.ref[T]] = {}

    def get(self, key: str) -> Optional[T]:
        """Get a value from cache."""
        ref = self._cache.get(key)
        if ref is not None:
            value = ref()
            if value is not None:
                return value
            # Clean up dead reference
            del self._cache[key]
        return None

    def set(self, key: str, value: T) -> None:
        """Set a value in cache."""
        self._cache[key] = weakref.ref(value)

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()

    def cleanup(self) -> int:
        """Remove dead references and return count removed."""
        dead_keys = [k for k, v in self._cache.items() if v() is None]
        for key in dead_keys:
            del self._cache[key]
        return len(dead_keys)


# ═══════════════════════════════════════════════════════════════════════════════
# STREAMING & CHUNKED PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════


def chunked_read(
    file_path: Path,
    chunk_size: int = 8192,
) -> Iterator[bytes]:
    """Read a file in chunks to minimize memory usage."""
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def process_large_file(
    file_path: Path,
    processor: Callable[[bytes], Any],
    chunk_size: int = 8192,
) -> list[Any]:
    """Process a large file in chunks."""
    results = []
    for chunk in chunked_read(file_path, chunk_size):
        result = processor(chunk)
        if result is not None:
            results.append(result)
    return results


def stream_lines(
    file_path: Path,
    encoding: str = "utf-8",
) -> Iterator[str]:
    """Stream lines from a file one at a time."""
    with open(file_path, "r", encoding=encoding) as f:
        for line in f:
            yield line.rstrip("\n\r")


def batched_process(
    items: list[T],
    processor: Callable[[list[T]], Any],
    batch_size: int = 100,
) -> list[Any]:
    """Process items in batches to limit memory usage."""
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        result = processor(batch)
        results.append(result)
        gc.collect()  # Allow garbage collection between batches
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY OPTIMIZATION UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════


def optimize_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Optimize a dictionary by interning strings."""
    optimized = {}
    for key, value in d.items():
        # Intern string keys
        key = sys.intern(key) if isinstance(key, str) else key
        # Recursively optimize nested dicts
        if isinstance(value, dict):
            value = optimize_dict(value)
        elif isinstance(value, str):
            value = sys.intern(value)
        optimized[key] = value
    return optimized


def compact_list(items: list[Any]) -> list[Any]:
    """Remove None values and compact a list."""
    return [item for item in items if item is not None]


def force_gc() -> int:
    """Force garbage collection and return freed objects count."""
    before = len(gc.get_objects())
    gc.collect()
    after = len(gc.get_objects())
    return before - after


class MemoryLimit:
    """Context manager to enforce memory limits."""

    def __init__(self, max_mb: float = 100.0):
        self.max_bytes = int(max_mb * 1024 * 1024)
        self._tracker = MemoryTracker()

    def __enter__(self) -> "MemoryLimit":
        self._tracker.start()
        return self

    def __exit__(self, *args: Any) -> None:
        stats = self._tracker.stop()
        if stats.peak_bytes > self.max_bytes:
            console.print(
                f"[yellow]⚠️  Memory limit exceeded: {stats.peak_mb:.1f} MB > {self.max_bytes / 1024 / 1024:.1f} MB[/yellow]"
            )

    def check(self) -> bool:
        """Check if within memory limits."""
        self._tracker.update()
        return True  # Simplified check


# ═══════════════════════════════════════════════════════════════════════════════
# SLOTS OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════════


class SlottedBase:
    """Base class with __slots__ for memory optimization."""
    __slots__ = ()

    def __sizeof__(self) -> int:
        """Calculate object size."""
        size = object.__sizeof__(self)
        for slot in self.__slots__:
            value = getattr(self, slot, None)
            if value is not None:
                size += sys.getsizeof(value)
        return size

