"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Lazy Loading System                          ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Lazy loading utilities for deferred initialization                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import importlib
import sys
from functools import cached_property
from typing import Any, Callable, Generic, Optional, TypeVar

from rich.console import Console

console = Console()

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════════════════════════
# LAZY VALUE
# ═══════════════════════════════════════════════════════════════════════════════


class Lazy(Generic[T]):
    """Lazy value that is computed on first access."""

    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._value: Optional[T] = None
        self._initialized: bool = False

    @property
    def value(self) -> T:
        """Get the lazy value, initializing if needed."""
        if not self._initialized:
            self._value = self._factory()
            self._initialized = True
        return self._value  # type: ignore

    @property
    def is_initialized(self) -> bool:
        """Check if value has been initialized."""
        return self._initialized

    def reset(self) -> None:
        """Reset the lazy value."""
        self._value = None
        self._initialized = False

    def __repr__(self) -> str:
        if self._initialized:
            return f"Lazy({self._value!r})"
        return "Lazy(<not initialized>)"


class LazyProperty(Generic[T]):
    """Descriptor for lazy property initialization."""

    def __init__(self, factory: Callable[[Any], T]):
        self._factory = factory
        self._attr_name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self._attr_name = f"_lazy_{name}"

    def __get__(self, instance: Any, owner: type) -> T:
        if instance is None:
            return self  # type: ignore

        if not hasattr(instance, self._attr_name):
            value = self._factory(instance)
            setattr(instance, self._attr_name, value)

        return getattr(instance, self._attr_name)


def lazy_property(func: Callable[[Any], T]) -> LazyProperty[T]:
    """Decorator to create a lazy property."""
    return LazyProperty(func)


# ═══════════════════════════════════════════════════════════════════════════════
# LAZY MODULE IMPORT
# ═══════════════════════════════════════════════════════════════════════════════


class LazyModule:
    """Lazy module loader that imports on first access."""

    def __init__(self, module_name: str):
        self._module_name = module_name
        self._module: Optional[Any] = None

    def _load(self) -> Any:
        """Load the module."""
        if self._module is None:
            self._module = importlib.import_module(self._module_name)
        return self._module

    def __getattr__(self, name: str) -> Any:
        module = self._load()
        return getattr(module, name)

    def __repr__(self) -> str:
        if self._module is not None:
            return f"LazyModule({self._module_name}, loaded)"
        return f"LazyModule({self._module_name}, not loaded)"


def lazy_import(module_name: str) -> LazyModule:
    """Create a lazy module import."""
    return LazyModule(module_name)


class LazyImporter:
    """Bulk lazy module importer."""

    def __init__(self):
        self._modules: dict[str, LazyModule] = {}

    def register(self, alias: str, module_name: str) -> None:
        """Register a module for lazy loading."""
        self._modules[alias] = LazyModule(module_name)

    def __getattr__(self, name: str) -> Any:
        if name in self._modules:
            return self._modules[name]
        raise AttributeError(f"No module registered as '{name}'")


# ═══════════════════════════════════════════════════════════════════════════════
# LAZY COLLECTION
# ═══════════════════════════════════════════════════════════════════════════════


class LazyList(Generic[T]):
    """List that loads items lazily."""

    def __init__(self, items: list[Callable[[], T]]):
        self._factories = items
        self._cache: dict[int, T] = {}

    def __getitem__(self, index: int) -> T:
        if index not in self._cache:
            self._cache[index] = self._factories[index]()
        return self._cache[index]

    def __len__(self) -> int:
        return len(self._factories)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    @property
    def loaded_count(self) -> int:
        """Number of items already loaded."""
        return len(self._cache)


class LazyDict(Generic[T]):
    """Dictionary that loads values lazily."""

    def __init__(self, factories: dict[str, Callable[[], T]]):
        self._factories = factories
        self._cache: dict[str, T] = {}

    def __getitem__(self, key: str) -> T:
        if key not in self._cache:
            if key not in self._factories:
                raise KeyError(key)
            self._cache[key] = self._factories[key]()
        return self._cache[key]

    def __contains__(self, key: str) -> bool:
        return key in self._factories

    def keys(self):
        return self._factories.keys()

    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Get a value with optional default."""
        try:
            return self[key]
        except KeyError:
            return default


# ═══════════════════════════════════════════════════════════════════════════════
# LAZY SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════


class LazySingleton(Generic[T]):
    """Lazy singleton pattern implementation."""

    _instances: dict[type, Any] = {}

    def __init__(self, cls: type[T]):
        self._cls = cls

    @property
    def instance(self) -> T:
        """Get or create the singleton instance."""
        if self._cls not in LazySingleton._instances:
            LazySingleton._instances[self._cls] = self._cls()
        return LazySingleton._instances[self._cls]

    @classmethod
    def reset(cls, target: type) -> None:
        """Reset a singleton instance."""
        if target in cls._instances:
            del cls._instances[target]

    @classmethod
    def reset_all(cls) -> None:
        """Reset all singleton instances."""
        cls._instances.clear()


def lazy_singleton(cls: type[T]) -> LazySingleton[T]:
    """Decorator to make a class a lazy singleton."""
    return LazySingleton(cls)


# ═══════════════════════════════════════════════════════════════════════════════
# DEFERRED INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════


class DeferredInit:
    """Mixin for deferred initialization."""

    _deferred_initialized: bool = False

    def _deferred_init(self) -> None:
        """Override this to perform deferred initialization."""
        pass

    def ensure_initialized(self) -> None:
        """Ensure deferred initialization has been performed."""
        if not self._deferred_initialized:
            self._deferred_init()
            self._deferred_initialized = True


def deferred(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to defer function execution until first call."""
    result: dict[str, Any] = {"value": None, "executed": False}

    def wrapper(*args: Any, **kwargs: Any) -> T:
        if not result["executed"]:
            result["value"] = func(*args, **kwargs)
            result["executed"] = True
        return result["value"]

    return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# CACHED PROPERTY HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


class cached:
    """Additional cached property utilities."""

    @staticmethod
    def clear(obj: Any, name: str) -> None:
        """Clear a cached_property value."""
        if name in obj.__dict__:
            del obj.__dict__[name]

    @staticmethod
    def clear_all(obj: Any) -> int:
        """Clear all cached_property values from an object."""
        # Find all cached_property attributes
        cls = type(obj)
        cached_names = [
            name for name, value in cls.__dict__.items()
            if isinstance(value, cached_property)
        ]

        count = 0
        for name in cached_names:
            if name in obj.__dict__:
                del obj.__dict__[name]
                count += 1

        return count
