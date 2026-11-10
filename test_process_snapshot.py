from app.database.database import SessionLocal
from app.database.models import ProcessSnapshot
from app.database.process_repository import take_process_snapshot

saved_count = take_process_snapshot()

print(f"Process snapshots saved: {saved_count}")

session = SessionLocal()
snapshots = session.query(ProcessSnapshot).all()
session.close()

print(f"Total process snapshots in database: {len(snapshots)}")

for snapshot in snapshots[:5]:
    print(
        f"ID: {snapshot.id} | "
        f"Process: {snapshot.process_name} | "
        f"PID: {snapshot.process_id} | "
        f"CPU: {snapshot.cpu_percent}% | "
        f"Memory: {snapshot.memory_percent}%"
    )