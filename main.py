from app.core.config import load_config
from app.core.logging_setup import setup_logging
from app.database.process_repository import take_process_snapshot
from app.detectors.file_monitor import start_monitoring


def main() -> None:
    setup_logging()

    config = load_config()

    print("RDRS started")
    print(f"Watched folders: {config.watched_folders}")
    print(f"Simulation mode: {config.response.simulation_mode}")

    saved_processes = take_process_snapshot()
    print(f"Process snapshots saved: {saved_processes}")

    start_monitoring(config.watched_folders)


if __name__ == "__main__":
    main()