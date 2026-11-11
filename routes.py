from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from app.database.database import SessionLocal
from app.database.models import FileEventRecord


router = APIRouter()


class ScanRequest(BaseModel):
    folder_path: str


class SettingsRequest(BaseModel):
    simulation_mode: bool
    window_seconds: int


@router.get("/health")
def get_health():
    """Check whether the RDRS API is running."""
    return {
        "status": "ok",
        "service": "RDRS API",
    }


@router.get("/status")
def get_status():
    """Return basic RDRS status information."""
    return {
        "service": "RDRS",
        "api_status": "running",
        "monitoring": "configured",
        "watched_folder": "./data/sandbox",
        "simulation_mode": True,
    }


@router.get("/alerts")
def get_alerts():
    """Return alert log entries."""
    alert_log = Path("logs/alerts.log")

    if not alert_log.exists():
        return {
            "alerts": [],
            "message": "No alert log found.",
        }

    alerts = []

    with alert_log.open("r", encoding="utf-8") as log_file:
        for line in log_file:
            clean_line = line.strip()

            if clean_line:
                alerts.append(clean_line)

    return {
        "alerts": alerts,
        "total": len(alerts),
    }


@router.get("/events")
def get_events():
    """Return recent file events from the database."""
    session = SessionLocal()

    try:
        records = (
            session.query(FileEventRecord)
            .order_by(FileEventRecord.timestamp.desc())
            .limit(50)
            .all()
        )

        events = []

        for record in records:
            events.append(
                {
                    "id": record.id,
                    "event_type": record.event_type,
                    "source_path": record.source_path,
                    "destination_path": record.destination_path,
                    "extension": record.extension,
                    "previous_extension": record.previous_extension,
                    "timestamp": record.timestamp.isoformat(),
                }
            )

        return {
            "events": events,
            "total": len(events),
        }
    finally:
        session.close()


@router.get("/reports")
def get_reports():
    """Return a simple report based on recent file events."""
    session = SessionLocal()

    try:
        records = (
            session.query(FileEventRecord)
            .order_by(FileEventRecord.timestamp.desc())
            .limit(50)
            .all()
        )

        created_count = 0
        modified_count = 0
        deleted_count = 0
        moved_count = 0

        for record in records:
            if record.event_type == "created":
                created_count += 1
            elif record.event_type == "modified":
                modified_count += 1
            elif record.event_type == "deleted":
                deleted_count += 1
            elif record.event_type == "moved":
                moved_count += 1

        return {
            "report_period": "latest 50 events",
            "total_events": len(records),
            "created_events": created_count,
            "modified_events": modified_count,
            "deleted_events": deleted_count,
            "moved_events": moved_count,
        }
    finally:
        session.close()


@router.post("/scan")
def start_scan(request: ScanRequest):
    """Return a simulated scan result for a folder path."""
    return {
        "status": "scan requested",
        "folder_path": request.folder_path,
        "simulation_mode": True,
        "message": "RDRS received the scan request. No files were modified.",
    }


@router.post("/settings")
def update_settings(request: SettingsRequest):
    """Return the requested safe RDRS settings."""
    if request.window_seconds <= 0:
        return {
            "status": "error",
            "message": "window_seconds must be greater than zero.",
        }

    return {
        "status": "settings received",
        "simulation_mode": request.simulation_mode,
        "window_seconds": request.window_seconds,
        "message": "RDRS received the settings request. No configuration file was changed.",
    }