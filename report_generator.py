from datetime import datetime
from pathlib import Path


def create_report_folder(report_folder: str = "data/reports") -> Path:
    folder = Path(report_folder)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def create_report_filename() -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"rdrs-report-{timestamp}.txt"

def create_report_content(
    total_events: int,
    created_events: int,
    modified_events: int,
    deleted_events: int,
    moved_events: int,
    total_alerts: int,
) -> str:
    lines = [
        "RDRS Activity Report",
        "====================",
        "",
        f"Total events: {total_events}",
        f"Created events: {created_events}",
        f"Modified events: {modified_events}",
        f"Deleted events: {deleted_events}",
        f"Moved events: {moved_events}",
        f"Total alerts: {total_alerts}",
    ]

    return "\n".join(lines)

def save_report(content: str, report_folder: str = "data/reports") -> Path:
    folder = create_report_folder(report_folder)
    filename = create_report_filename()
    report_path = folder / filename

    report_path.write_text(content, encoding="utf-8")

    return report_path