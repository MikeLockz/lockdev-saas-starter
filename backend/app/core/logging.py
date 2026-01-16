import logging
import sys
import structlog
from typing import Any
from app.core.pii_masking import mask_pii_processor

def configure_logging(log_level: str = "INFO", json_logs: bool = True):
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        mask_pii_processor,
    ]

    if json_logs:
        processors: list[Any] = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging to use structlog
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=log_level)