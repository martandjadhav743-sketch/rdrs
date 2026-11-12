from app.database.database import SessionLocal
from app.database.models import FileEventRecord
from app.reports.report_generator import create_report_content, save_report
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import load_config
from app.core.logging_setup import setup_logging
from app.database.process_repository import take_process_snapshot
from app.detectors.file_monitor import start_monitoring


app = FastAPI(
    title="RDRS API",
    description="Ransomware Detection and Response System API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

def main() -> None:
    setup_logging()

    config = load_config()

    print("RDRS started")
    print(f"Watched folders: {config.watched_folders}")
    print(f"Simulation mode: {config.response.simulation_mode}")

    saved_processes = take_process_snapshot()
    print(f"Process snapshots saved: {saved_processes}")

    start_monitoring(config.watched_folders)

@app.post("/generate-report")
def generate_report():
    session = SessionLocal()


    try:
        total_events = session.query(FileEventRecord).count()
        created_events = session.query(FileEventRecord).filter(
            FileEventRecord.event_type == "created"
        ).count()
        modified_events = session.query(FileEventRecord).filter(
            FileEventRecord.event_type == "modified"
        ).count()
        deleted_events = session.query(FileEventRecord).filter(
            FileEventRecord.event_type == "deleted"
        ).count()
        moved_events = session.query(FileEventRecord).filter(
            FileEventRecord.event_type == "moved"
        ).count()
        total_alerts = 0


        content = create_report_content(
            total_events=total_events,
            created_events=created_events,
            modified_events=modified_events,
            deleted_events=deleted_events,
            moved_events=moved_events,
            total_alerts=total_alerts,
        )


        report_path = save_report(content)


        return {
            "message": "Report generated successfully",
            "report_path": str(report_path),
        }


    finally:
        session.close()

if __name__ == "__main__":
    main()

