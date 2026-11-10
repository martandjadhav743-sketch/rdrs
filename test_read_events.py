from app.database.database import SessionLocal
from app.database.models import FileEventRecord

session = SessionLocal()

events = session.query(FileEventRecord).all()

print(f"Total file events: {len(events)}")

for event in events:
    print(
        f"ID: {event.id} | "
        f"Type: {event.event_type} | "
        f"Path: {event.source_path} | "
        f"Extension: {event.extension} | "
        f"Time: {event.timestamp}"
    )

session.close()