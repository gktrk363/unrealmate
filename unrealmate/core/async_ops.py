"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Async Operations                             ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Async/await utilities for I/O operations                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Coroutine, TypeVar

from rich.console import Console

console = Console()

T = TypeVar("T")

# Default thread pool for running sync functions async
_executor = ThreadPoolExecutor(max_workers=4)


# ═══════════════════════════════════════════════════════════════════════════════
# ASYNC FILE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


async def read_file_async(path: Path, encoding: str = "utf-8") -> str:
    """
    Read a file asynchronously.

    Args:
        path: Path to file
        encoding: File encoding

    Returns:
        File contents as string
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        lambda: path.read_text(encoding=encoding)
    )


async def write_file_async(
    path: Path,
    content: str,
    encoding: str = "utf-8",
) -> None:
    """
    Write to a file asynchronously.

    Args:
        path: Path to file
        content: Content to write
        encoding: File encoding
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        _executor,
        lambda: path.write_text(content, encoding=encoding)
    )


async def read_binary_async(path: Path) -> bytes:
    """Read a binary file asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        lambda: path.read_bytes()
    )


async def write_binary_async(path: Path, content: bytes) -> None:
    """Write to a binary file asynchronously."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        _executor,
        lambda: path.write_bytes(content)
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ASYNC DIRECTORY OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


async def scan_directory_async(
    directory: Path,
    pattern: str = "*",
    recursive: bool = False,
) -> list[Path]:
    """
    Scan a directory asynchronously.

    Args:
        directory: Directory to scan
        pattern: Glob pattern
        recursive: Whether to scan recursively

    Returns:
        List of matching paths
    """
    loop = asyncio.get_event_loop()

    def scan() -> list[Path]:
        if recursive:
            return list(directory.rglob(pattern))
        return list(directory.glob(pattern))

    return await loop.run_in_executor(_executor, scan)


async def get_file_info_async(path: Path) -> dict[str, Any]:
    """
    Get file information asynchronously.

    Args:
        path: Path to file

    Returns:
        Dictionary with file info
    """
    loop = asyncio.get_event_loop()

    def get_info() -> dict[str, Any]:
        stat = path.stat()
        return {
            "name": path.name,
            "path": str(path),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "suffix": path.suffix,
        }

    return await loop.run_in_executor(_executor, get_info)


# ═══════════════════════════════════════════════════════════════════════════════
# PARALLEL PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════


async def process_files_parallel(
    files: list[Path],
    processor: Callable[[Path], T],
    max_concurrent: int = 4,
) -> list[T]:
    """
    Process multiple files in parallel.

    Args:
        files: List of files to process
        processor: Function to apply to each file
        max_concurrent: Maximum concurrent operations

    Returns:
        List of results
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    loop = asyncio.get_event_loop()

    async def process_one(file: Path) -> T:
        async with semaphore:
            return await loop.run_in_executor(_executor, processor, file)

    tasks = [process_one(f) for f in files]
    return await asyncio.gather(*tasks)


async def run_parallel(
    *coroutines: Coroutine[Any, Any, T],
) -> list[T]:
    """
    Run multiple coroutines in parallel.

    Args:
        *coroutines: Coroutines to run

    Returns:
        List of results
    """
    return await asyncio.gather(*coroutines)


# ═══════════════════════════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════════════════════════


def run_async(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """
    Decorator to run an async function synchronously.

    Args:
        func: Async function

    Returns:
        Wrapped function that runs synchronously
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()

    return wrapper


def to_async(func: Callable[..., T]) -> Callable[..., Coroutine[Any, Any, T]]:
    """
    Decorator to convert a sync function to async.

    Args:
        func: Sync function

    Returns:
        Async version of the function
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor,
            lambda: func(*args, **kwargs)
        )

    return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# ASYNC HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


async def sleep_async(seconds: float) -> None:
    """Async sleep wrapper."""
    await asyncio.sleep(seconds)


async def timeout(
    coroutine: Coroutine[Any, Any, T],
    seconds: float,
) -> T:
    """
    Run a coroutine with a timeout.

    Args:
        coroutine: Coroutine to run
        seconds: Timeout in seconds

    Returns:
        Result of coroutine

    Raises:
        asyncio.TimeoutError: If timeout is exceeded
    """
    return await asyncio.wait_for(coroutine, timeout=seconds)


def get_event_loop() -> asyncio.AbstractEventLoop:
    """Get or create an event loop."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def shutdown_executor() -> None:
    """Shutdown the thread pool executor."""
    _executor.shutdown(wait=True)
