"""
Event System — Observer Pattern for decoupled communication.

EventBus broadcasts events. Observers listen without coupling to the emitter.
Pipeline emits DOCS_LOADED → LoggingObserver prints it, MetricsObserver counts it.
Neither knows about the other. That's the power of Observer Pattern.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto


class EventType(Enum):
    """All observable events in the system."""
    DOCS_LOADED = auto()
    CHUNKS_CREATED = auto()
    SEARCH_STARTED = auto()
    SEARCH_COMPLETED = auto()


@dataclass
class Event:
    """Immutable event envelope carrying type, data, and timestamp."""
    event_type: EventType
    data: dict[str, str | int | float | list[str]]
    timestamp: float


class Observer(ABC):
    """Abstract Observer — implement on_event to react to published events."""

    @abstractmethod
    def on_event(self, event: Event) -> None:
        pass


class EventBus:
    """
    Singleton EventBus for pub/sub event dispatch.

    One instance across the entire app. Subscribe observers once at startup,
    then publish events from anywhere — observers react automatically.
    """

    _instance: "EventBus | None" = None

    def __new__(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._observers: list[Observer] = []
        return cls._instance

    def subscribe(self, observer: Observer) -> None:
        """Register an observer. Duplicates are ignored."""
        if observer not in self._observers:
            self._observers.append(observer)

    def publish(self, event: Event) -> None:
        """Broadcast event to all registered observers."""
        for observer in self._observers:
            observer.on_event(event)


class LoggingObserver(Observer):
    """Prints all events to console for structured logging."""

    def on_event(self, event: Event) -> None:
        print(
            f"[EVENT LOG] {event.event_type.name} "
            f"at {event.timestamp:.2f}: {event.data}"
        )


class MetricsObserver(Observer):
    """Tracks event counts for observability dashboards."""

    def __init__(self) -> None:
        self.event_counts: dict[str, int] = {}

    def on_event(self, event: Event) -> None:
        name = event.event_type.name
        self.event_counts[name] = self.event_counts.get(name, 0) + 1
