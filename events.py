from dataclasses import dataclass
from datetime import datetime
from typing import Literal


EventType = Literal["created", "modified", "moved", "deleted"]


@dataclass(frozen=True)
class FileEvent:
    """A structured record of one observed file event."""

    event_type: EventType
    source_path: str
    timestamp: datetime
    extension: str
    destination_path: str | None = None
    previous_extension: str | None = None