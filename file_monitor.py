import os
import time
from datetime import datetime, timezone
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler

from app.core.events import EventType, FileEvent


class RdrsFileHandler(FileSystemEventHandler):
    """Convert Watchdog events into RDRS events and print them."""

    def __init__(self) -> None:
        super().__init__()
        self.event_count = 0

    def on_created(self, event: FileSystemEvent) -> None:
        self._record_event(event, "created")

    def on_modified(self, event: FileSystemEvent) -> None:
        self._record_event(event, "modified")

    def on_moved(self, event: FileSystemEvent) -> None:
        self._record_event(event, "moved")

    def on_deleted(self, event: FileSystemEvent) -> None:
        self._record_event(event, "deleted")

    def _record_event(
        self,
        event: FileSystemEvent,
        event_type: EventType,
    ) -> None:
        if event.is_directory:
            return

        source_path = os.fsdecode(event.src_path)
        destination_path = None
        previous_extension = None

        if event_type == "moved":
            destination_path = os.fsdecode(event.dest_path)
            previous_extension = Path(source_path).suffix.lower()

        current_path = destination_path or source_path

        record = FileEvent(
            event_type=event_type,
            source_path=source_path,
            timestamp=datetime.now(timezone.utc),
            extension=Path(current_path).suffix.lower(),
            destination_path=destination_path,
            previous_extension=previous_extension,
        )

        self.event_count += 1

        path_description = record.source_path
        if record.destination_path is not None:
            path_description += f" -> {record.destination_path}"

        print(
            f"[{record.timestamp.isoformat(timespec='seconds')}] "
            f"{record.event_type.upper()} | {path_description} | "
            f"extension={record.extension or '(none)'} | "
            f"total={self.event_count}",
            flush=True,
        )
        import time

from watchdog.observers import Observer
def start_monitoring(folders: list[str]) -> None:
    """Monitor configured folders until the user presses Ctrl + C."""
    if not folders:
        raise ValueError("No watched folders are configured.")

    paths = [Path(folder).resolve() for folder in folders]

    for path in paths:
        if not path.is_dir():
            raise ValueError(
                f"Watched folder does not exist or is not a directory: {path}"
            )

    handler = RdrsFileHandler()
    observer = Observer()

    for path in dict.fromkeys(paths):
        observer.schedule(handler, str(path), recursive=True)

    observer.start()

    print("\nRDRS is watching these folders:", flush=True)
    for path in dict.fromkeys(paths):
        print(f"  {path}", flush=True)

    print("Press Ctrl + C to stop.\n", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping RDRS...", flush=True)
    finally:
        observer.stop()
        observer.join()