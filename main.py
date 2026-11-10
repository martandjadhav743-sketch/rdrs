from loguru import logger

from app.core.config import load_config
from app.core.logging_setup import setup_logging
from app.detectors.file_monitor import start_monitoring


def main() -> None:
    setup_logging()
    config = load_config()

    logger.info("RDRS started")
    start_monitoring(config.watched_folders)


if __name__ == "__main__":
    main()