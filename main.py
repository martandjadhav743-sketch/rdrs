from datetime import datetime, timezone
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import load_config
from app.core.logging_setup import configure_logging
from app.database.database import engine, initialise_database
from app.database.process_repository import take_process_snapshot
from app.detectors.file_monitor import start_monitoring
from app.database.database import SessionLocal
from app.database.models import FileEventRecord, ProcessSnapshot
from app.database.models import AlertRecord


REPORT_PATH = Path("reports/rdrs-report.md")


app = FastAPI(
    title="RDRS",
    description="Ransomware Detection and Response System API",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "RDRS API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


def create_report():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    session = SessionLocal()

    try:
        events = (
            session.query(FileEventRecord)
            .order_by(FileEventRecord.timestamp.desc())
            .limit(50)
            .all()
        )

        snapshots = (
            session.query(ProcessSnapshot)
            .order_by(ProcessSnapshot.timestamp.desc())
            .limit(50)
            .all()
        )

        alerts = (
            session.query(AlertRecord)
            .order_by(AlertRecord.created_at.desc())
            .limit(50)
            .all()
        )
    finally:
        session.close()

    lines = []
    lines.append("# RDRS Activity Report")
    lines.append("")
    lines.append(
        f"Generated at: {datetime.now(timezone.utc).isoformat()}"
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"Total file events: {len(events)}")
    lines.append(f"Total process snapshots: {len(snapshots)}")
    lines.append(f"Total alerts: {len(alerts)}")
    lines.append("")
    lines.append("## Recent File Events")
    lines.append("")

    if events:
        for event in events:
            lines.append(
                f"- {event.timestamp} | {event.event_type} | "
                f"{event.source_path}"
            )
    else:
        lines.append("No file events recorded.")

    lines.append("")
    lines.append("## Recent Process Snapshots")
    lines.append("")

    if snapshots:
        for snapshot in snapshots:
            lines.append(
                f"- {snapshot.timestamp} | {snapshot.process_name} | "
                f"PID {snapshot.process_id} | "
                f"CPU {snapshot.cpu_percent}% | "
                f"Memory {snapshot.memory_percent}%"
            )
    else:
        lines.append("No process snapshots recorded.")

    lines.append("")
    lines.append("## Latest Alerts")
    lines.append("")

    if alerts:
        for alert in alerts:
            lines.append(
                f"- {alert.created_at} | {alert.severity} | "
                f"{alert.message}"
            )
    else:
        lines.append("No alerts recorded.")

    REPORT_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return REPORT_PATH


@app.post("/generate-report")
def generate_report():
    try:
        report_path = create_report()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Report generation failed",
        )

    return {
        "message": "Report generated successfully",
        "report_path": str(report_path),
    }


@app.on_event("startup")
def startup_event():
    configure_logging()

    config = load_config()

    initialise_database()

    saved_count = take_process_snapshot()

    print("RDRS started")
    print(f"Watched folders: {config.watched_folders}")
    print(f"Simulation mode: {config.response.simulation_mode}")
    print(f"Process snapshots saved: {saved_count}")

    start_monitoring(config.watched_folders)


@app.on_event("shutdown")
def shutdown_event():
    engine.dispose()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )