"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Dependency Injection                         ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Simple dependency injection container                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar, get_type_hints

from rich.console import Console

console = Console()

T = TypeVar("T")


class Lifetime(Enum):
    """Dependency lifetime options."""
    TRANSIENT = auto()   # New instance every time
    SINGLETON = auto()   # Single instance shared
    SCOPED = auto()      # Single instance per scope


@dataclass
class Registration:
    """A dependency registration."""
    service_type: Type[Any]
    implementation: Any  # Type or factory function
    lifetime: Lifetime
    instance: Optional[Any] = None


class Container:
    """Simple dependency injection container."""

    def __init__(self):
        self._registrations: dict[Type[Any], Registration] = {}
        self._scopes: dict[str, dict[Type[Any], Any]] = {}
        self._current_scope: Optional[str] = None

    def register(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T] | Callable[..., T]] = None,
        lifetime: Lifetime = Lifetime.TRANSIENT,
    ) -> "Container":
        """
        Register a service.

        Args:
            service_type: The service type/interface
            implementation: Implementation class or factory
            lifetime: Lifetime of the service

        Returns:
            Self for chaining
        """
        impl = implementation or service_type
        self._registrations[service_type] = Registration(
            service_type=service_type,
            implementation=impl,
            lifetime=lifetime,
        )
        return self

    def register_singleton(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T] | Callable[..., T]] = None,
    ) -> "Container":
        """Register a singleton service."""
        return self.register(service_type, implementation, Lifetime.SINGLETON)

    def register_instance(
        self,
        service_type: Type[T],
        instance: T,
    ) -> "Container":
        """
        Register an existing instance as a singleton.

        Args:
            service_type: The service type
            instance: The instance to register

        Returns:
            Self for chaining
        """
        self._registrations[service_type] = Registration(
            service_type=service_type,
            implementation=type(instance),
            lifetime=Lifetime.SINGLETON,
            instance=instance,
        )
        return self

    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service.

        Args:
            service_type: The service type to resolve

        Returns:
            Instance of the service

        Raises:
            KeyError: If service is not registered
        """
        if service_type not in self._registrations:
            raise KeyError(f"Service not registered: {service_type}")

        reg = self._registrations[service_type]

        # Check for existing singleton instance
        if reg.lifetime == Lifetime.SINGLETON and reg.instance is not None:
            return reg.instance

        # Check for scoped instance
        if reg.lifetime == Lifetime.SCOPED and self._current_scope:
            scope = self._scopes.get(self._current_scope, {})
            if service_type in scope:
                return scope[service_type]

        # Create new instance
        instance = self._create_instance(reg.implementation)

        # Store singleton
        if reg.lifetime == Lifetime.SINGLETON:
            reg.instance = instance

        # Store scoped
        if reg.lifetime == Lifetime.SCOPED and self._current_scope:
            if self._current_scope not in self._scopes:
                self._scopes[self._current_scope] = {}
            self._scopes[self._current_scope][service_type] = instance

        return instance

    def _create_instance(self, implementation: Any) -> Any:
        """Create an instance, resolving constructor dependencies."""
        # If it's a factory function
        if callable(implementation) and not isinstance(implementation, type):
            return self._call_with_injection(implementation)

        # If it's a class
        if isinstance(implementation, type):
            return self._call_with_injection(implementation)

        return implementation

    def _call_with_injection(self, func: Callable[..., T]) -> T:
        """Call a function/constructor with injected dependencies."""
        try:
            hints = get_type_hints(func)
        except Exception:
            hints = {}

        sig = inspect.signature(func)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = hints.get(param_name)

            if param_type and param_type in self._registrations:
                kwargs[param_name] = self.resolve(param_type)
            elif param.default is not inspect.Parameter.empty:
                kwargs[param_name] = param.default

        return func(**kwargs)

    def create_scope(self, scope_name: str) -> "ScopeContext":
        """
        Create a scope for scoped dependencies.

        Args:
            scope_name: Name of the scope

        Returns:
            ScopeContext context manager
        """
        return ScopeContext(self, scope_name)

    def clear_scope(self, scope_name: str) -> None:
        """Clear a scope and its instances."""
        if scope_name in self._scopes:
            del self._scopes[scope_name]

    def clear(self) -> None:
        """Clear all registrations."""
        self._registrations.clear()
        self._scopes.clear()


class ScopeContext:
    """Context manager for dependency scopes."""

    def __init__(self, container: Container, scope_name: str):
        self.container = container
        self.scope_name = scope_name
        self._previous_scope: Optional[str] = None

    def __enter__(self) -> "ScopeContext":
        self._previous_scope = self.container._current_scope
        self.container._current_scope = self.scope_name
        return self

    def __exit__(self, *args: Any) -> None:
        self.container.clear_scope(self.scope_name)
        self.container._current_scope = self._previous_scope


# ═══════════════════════════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════════════════════════

# Global container
container = Container()


def inject(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to inject dependencies into a function.

    Args:
        func: Function to inject into

    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return container._call_with_injection(
            lambda **injected: func(*args, **{**injected, **kwargs})
        )
    return wrapper


def injectable(
    lifetime: Lifetime = Lifetime.TRANSIENT,
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to mark a class as injectable and register it.

    Args:
        lifetime: Service lifetime

    Returns:
        Decorator function
    """
    def decorator(cls: Type[T]) -> Type[T]:
        container.register(cls, cls, lifetime)
        return cls
    return decorator


def singleton(cls: Type[T]) -> Type[T]:
    """Decorator to register a class as a singleton."""
    container.register_singleton(cls)
    return cls

