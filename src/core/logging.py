"""
Logging configuration for the application
"""
import logging
import sys
from typing import Any, Dict

import structlog
from structlog.types import Processor

from src.core.config import settings


def setup_logging() -> None:
    """
    Configure structlog and Python's logging
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Set log level for third-party libraries
    for logger_name in ["uvicorn", "uvicorn.error", "fastapi"]:
        logging.getLogger(logger_name).setLevel(log_level)
        
    # Configure structlog processors for development vs. production
    if settings.ENV == "development":
        processors = _get_dev_processors()
    else:
        processors = _get_prod_processors()
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _get_dev_processors() -> list[Processor]:
    """Configure structlog processors for development environment"""
    return [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.dev.ConsoleRenderer(colors=True, exception_formatter=structlog.dev.plain_traceback),
    ]


def _get_prod_processors() -> list[Processor]:
    """Configure structlog processors for production environment"""
    return [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ]


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger with the given name
    """
    return structlog.getLogger(name)
