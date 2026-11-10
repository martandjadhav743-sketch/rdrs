from datetime import datetime, timezone

import psutil

from app.database.database import SessionLocal
from app.database.models import ProcessSnapshot


def save_process_snapshot(process) -> None:
    session = SessionLocal()

    record = ProcessSnapshot(
        process_name=process.info["name"],
        process_id=process.info["pid"],
        cpu_percent=process.info["cpu_percent"],
        memory_percent=process.info["memory_percent"],
        timestamp=datetime.now(timezone.utc),
    )

    session.add(record)
    session.commit()
    session.close()


def take_process_snapshot() -> int:
    processes = psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent"]
    )

    saved_count = 0

    for process in processes:
        try:
            save_process_snapshot(process)
            saved_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return saved_count