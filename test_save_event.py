from datetime import datetime, timezone

from app.database.database import SessionLocal
from app.database.models import FileEventRecord

session = SessionLocal()

record = FileEventRecord(
    event_type="created",
    source_path="data/sandbox/test_file.txt",
    destination_path=None,
    extension=".txt",
    previous_extension=None,
    timestamp=datetime.now(timezone.utc),
)

session.add(record)
session.commit()
session.close()

print("File event saved successfully")