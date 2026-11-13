from loguru import logger


def setup_logging() -> None:
    logger.add("logs/system.log", rotation="1 MB", level="INFO")
    logger.add("logs/events.log", rotation="1 MB", level="INFO")
    logger.add("logs/alerts.log", rotation="1 MB", level="WARNING")
    logger.add("logs/errors.log", rotation="1 MB", level="ERROR")
    logger.add("logs/audit.log", rotation="1 MB", level="INFO")


def configure_logging() -> None:
    setup_logging()