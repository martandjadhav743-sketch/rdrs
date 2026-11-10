from datetime import datetime, timezone

from app.core.events import FileEvent
from app.database.database import SessionLocal
from app.database.event_repository import save_file_event
from app.database.models import FileEventRecord

event = FileEvent(
    event_type="modified",
    source_path="data/sandbox/test_file.txt",
    timestamp=datetime.now(timezone.utc),
    extension=".txt",
    previous_extension=None,
    destination_path=None,
)

save_file_event(event)

session = SessionLocal()
events = session.query(FileEventRecord).all()
session.close()

print(f"Total file events: {len(events)}")

for saved_event in events:
    print(
        f"ID: {saved_event.id} | "
        f"Type: {saved_event.event_type} | "
        f"Path: {saved_event.source_path} | "
        f"Extension: {saved_event.extension}"
    )