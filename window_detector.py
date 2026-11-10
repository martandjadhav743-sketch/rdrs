from collections import deque
from datetime import datetime, timedelta, timezone

from app.core.events import FileEvent


class SlidingWindowDetector:
    def __init__(self, window_seconds: int) -> None:
        self.window_seconds = window_seconds
        self.events = deque()

    def add_event(self, event: FileEvent) -> None:
        self.events.append(event)
        self.remove_old_events()

    def remove_old_events(self) -> None:
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(seconds=self.window_seconds)

        recent_events = [
            event
            for event in self.events
            if event.timestamp >= cutoff_time
        ]

        self.events.clear()
        self.events.extend(recent_events)

    def count_event_type(self, event_type: str) -> int:
        return sum(
            1
            for event in self.events
            if event.event_type == event_type
        )

    def count_extension_changes(self) -> int:
        return sum(
            1
            for event in self.events
            if event.previous_extension is not None
            and event.extension is not None
            and event.previous_extension != event.extension
        )

    def get_window_summary(self) -> dict:
        self.remove_old_events()

        return {
            "window_seconds": self.window_seconds,
            "total_events": len(self.events),
            "created_events": self.count_event_type("created"),
            "modified_events": self.count_event_type("modified"),
            "deleted_events": self.count_event_type("deleted"),
            "moved_events": self.count_event_type("moved"),
            "extension_changes": self.count_extension_changes(),
        }