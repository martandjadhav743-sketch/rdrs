from app.core.events import FileEvent
from app.database.database import SessionLocal
from app.database.models import FileEventRecord


def save_file_event(event: FileEvent) -> None:
    session = SessionLocal()

    record = FileEventRecord(
        event_type=event.event_type,
        source_path=event.source_path,
        destination_path=event.destination_path,
        extension=event.extension,
        previous_extension=event.previous_extension,
        timestamp=event.timestamp,
    )

    session.add(record)
    session.commit()
    session.close()