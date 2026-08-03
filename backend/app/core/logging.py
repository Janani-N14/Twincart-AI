import logging
import sys

from app.config import get_settings


def configure_logging() -> None:
    """Configure structured logging for the application.

    Sets the root logger level from settings and attaches a single
    StreamHandler with a consistent format so every module can just
    call ``logging.getLogger(__name__)``.
    """
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers on repeated calls (e.g. during testing)
    if not root.handlers:
        root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger, configuring logging on first call."""
    configure_logging()
    return logging.getLogger(name)
