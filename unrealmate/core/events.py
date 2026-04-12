"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Event System                                 ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Publish-subscribe event system for decoupled communication         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Optional
from weakref import WeakMethod, ref

from rich.console import Console

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# EVENT TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class EventType(Enum):
    """Built-in event types."""
    # CLI Events
    CLI_START = auto()
    CLI_END = auto()
    COMMAND_START = auto()
    COMMAND_END = auto()
    COMMAND_ERROR = auto()

    # Build Events
    BUILD_START = auto()
    BUILD_PROGRESS = auto()
    BUILD_SUCCESS = auto()
    BUILD_FAILURE = auto()

    # Asset Events
    ASSET_SCAN_START = auto()
    ASSET_SCAN_PROGRESS = auto()
    ASSET_SCAN_COMPLETE = auto()

    # Git Events
    GIT_OPERATION_START = auto()
    GIT_OPERATION_COMPLETE = auto()

    # Config Events
    CONFIG_LOADED = auto()
    CONFIG_CHANGED = auto()
    CONFIG_SAVED = auto()

    # Performance Events
    PERF_AUDIT_START = auto()
    PERF_AUDIT_COMPLETE = auto()

    # Custom Events
    CUSTOM = auto()


@dataclass
class Event:
    """Represents an event in the system."""
    event_type: EventType
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    cancelled: bool = False

    def cancel(self) -> None:
        """Cancel this event."""
        self.cancelled = True


# ═══════════════════════════════════════════════════════════════════════════════
# EVENT BUS
# ═══════════════════════════════════════════════════════════════════════════════


EventHandler = Callable[[Event], None]


class EventBus:
    """Central event bus for publish-subscribe communication."""

    def __init__(self):
        self._handlers: dict[EventType, list[Callable[[Event], None]]] = {}
        self._async_handlers: dict[EventType, list[Callable[[Event], Any]]] = {}
        self._history: list[Event] = []
        self._history_limit: int = 100
        self._debug: bool = False

    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler,
        weak: bool = False,
    ) -> Callable[[], None]:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Handler function
            weak: Use weak reference (auto-cleanup)

        Returns:
            Unsubscribe function
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        if weak:
            # Use weak reference for methods
            if hasattr(handler, "__self__"):
                handler_ref = WeakMethod(handler)
            else:
                handler_ref = ref(handler)
            self._handlers[event_type].append(handler_ref)
        else:
            self._handlers[event_type].append(handler)

        # Return unsubscribe function
        def unsubscribe() -> None:
            self.unsubscribe(event_type, handler)

        return unsubscribe

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> bool:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Event type
            handler: Handler to remove

        Returns:
            True if handler was found and removed
        """
        if event_type not in self._handlers:
            return False

        try:
            self._handlers[event_type].remove(handler)
            return True
        except ValueError:
            return False

    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: Event to publish
        """
        if self._debug:
            console.print(f"[dim]Event: {event.event_type.name}[/dim]")

        # Store in history
        self._history.append(event)
        if len(self._history) > self._history_limit:
            self._history.pop(0)

        # Call handlers
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers[:]:  # Copy to allow modification
            if event.cancelled:
                break

            try:
                # Handle weak references
                if isinstance(handler, (ref, WeakMethod)):
                    actual_handler = handler()
                    if actual_handler is None:
                        handlers.remove(handler)
                        continue
                    actual_handler(event)
                else:
                    handler(event)
            except Exception as e:
                console.print(f"[red]Event handler error: {e}[/red]")

    def emit(
        self,
        event_type: EventType,
        data: Optional[dict[str, Any]] = None,
        source: str = "",
    ) -> Event:
        """
        Emit an event (convenience method).

        Args:
            event_type: Type of event
            data: Event data
            source: Event source

        Returns:
            Created event
        """
        event = Event(
            event_type=event_type,
            data=data or {},
            source=source,
        )
        self.publish(event)
        return event

    async def publish_async(self, event: Event) -> None:
        """
        Publish an event asynchronously.

        Args:
            event: Event to publish
        """
        handlers = self._async_handlers.get(event.event_type, [])
        tasks = []

        for handler in handlers:
            if event.cancelled:
                break
            tasks.append(handler(event))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def subscribe_async(
        self,
        event_type: EventType,
        handler: Callable[[Event], Any],
    ) -> Callable[[], None]:
        """
        Subscribe an async handler.

        Args:
            event_type: Event type
            handler: Async handler function

        Returns:
            Unsubscribe function
        """
        if event_type not in self._async_handlers:
            self._async_handlers[event_type] = []
        self._async_handlers[event_type].append(handler)

        def unsubscribe() -> None:
            if handler in self._async_handlers.get(event_type, []):
                self._async_handlers[event_type].remove(handler)

        return unsubscribe

    def clear(self, event_type: Optional[EventType] = None) -> None:
        """
        Clear handlers for an event type or all.

        Args:
            event_type: Specific type to clear, or None for all
        """
        if event_type:
            self._handlers.pop(event_type, None)
            self._async_handlers.pop(event_type, None)
        else:
            self._handlers.clear()
            self._async_handlers.clear()

    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 10,
    ) -> list[Event]:
        """
        Get recent event history.

        Args:
            event_type: Filter by type
            limit: Maximum events to return

        Returns:
            List of recent events
        """
        events = self._history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]

    def set_debug(self, enabled: bool) -> None:
        """Enable or disable debug mode."""
        self._debug = enabled


# ═══════════════════════════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════════════════════════

# Global event bus
event_bus = EventBus()


def on_event(event_type: EventType) -> Callable[[EventHandler], EventHandler]:
    """
    Decorator to subscribe a function to an event.

    Args:
        event_type: Event type to subscribe to

    Returns:
        Decorator function
    """
    def decorator(func: EventHandler) -> EventHandler:
        event_bus.subscribe(event_type, func)
        return func
    return decorator


def emit_event(
    event_type: EventType,
    data_getter: Optional[Callable[..., dict[str, Any]]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to emit an event after function execution.

    Args:
        event_type: Event type to emit
        data_getter: Optional function to extract event data

    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            data = data_getter(*args, **kwargs) if data_getter else {"result": result}
            event_bus.emit(event_type, data, source=func.__name__)
            return result
        return wrapper
    return decorator

