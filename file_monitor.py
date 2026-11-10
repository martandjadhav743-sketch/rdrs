import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app.core.events import FileEvent
from app.core.entropy import file_entropy
from app.database.event_repository import save_file_event
from app.detectors.window_detector import SlidingWindowDetector
from app.detectors.risk_scorer import RiskScorer
from app.detectors.incident_response import IncidentResponder

window_detector = SlidingWindowDetector(window_seconds=60)
risk_scorer = RiskScorer(
    modified_threshold=20,
    rename_threshold=10,
    extension_change_threshold=10,
    entropy_threshold=7.0,
    cpu_threshold=80.0,
)
incident_responder = IncidentResponder(
    quarantine_folder="data/quarantine",
    simulation_mode=True,
)

class RdrsFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.event_count = 0

    def create_event(
        self,
        event_type: str,
        source_path: str,
        destination_path: str | None = None,
        extension: str | None = None,
        previous_extension: str | None = None,
    ) -> FileEvent:
        self.event_count += 1

        event = FileEvent(
            event_type=event_type,
            source_path=source_path,
            timestamp=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            extension=extension,
            previous_extension=previous_extension,
            destination_path=destination_path,
        )
        save_file_event(event)
        window_detector.add_event(event)

        print(
            f"{event.timestamp.isoformat()} | {event_type} | {source_path}"
            f"{' -> ' + destination_path if destination_path else ''}"
            f" | extension={event.extension} | total={self.event_count}"
        )

        return event

    def get_extension(self, path: str) -> str | None:
        if "." not in path:
            return None

        return "." + path.rsplit(".", 1)[1].lower()

    def on_created(self, event):
        if not event.is_directory:
            self.create_event("created", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            try:
                entropy = file_entropy(event.src_path)
            except (FileNotFoundError, PermissionError, OSError):
                entropy = 0.0

            window_detector.add_entropy(entropy)

            self.create_event("modified", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.create_event("deleted", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.create_event(
                "moved",
                event.src_path,
                destination_path=event.dest_path,
                extension=self.get_extension(event.dest_path),
                previous_extension=self.get_extension(event.src_path),
            )


def start_monitoring(folders: list[str]) -> None:
    if not folders:
        raise ValueError("At least one folder must be configured for monitoring.")

    observer = Observer()
    handler = RdrsFileHandler()

    for folder in folders:
        observer.schedule(handler, folder, recursive=True)
        print(f"Watching folder: {folder}")

    observer.start()


    try:
        while True:
            time.sleep(10)

            summary = window_detector.get_window_summary()


            assessment = risk_scorer.assess(
                window_summary=summary,
                average_entropy=summary.get("average_entropy", 0.0),
                cpu_percent=0.0,
            )


            print("Sliding window summary:")
            print(summary)

            print("Risk assessment:")
            print(assessment)
            if assessment["severity"] == "Critical":
                affected_files = window_detector.get_affected_files()

                incident = incident_responder.create_incident(
                    score=assessment["score"],
                    severity=assessment["severity"],
                    affected_files=affected_files,
                )

                if incident is not None:
                    incident_responder.quarantine_files(incident)
    except KeyboardInterrupt:
        observer.stop()
        print("Monitoring stopped.")
    finally:
        observer.join()