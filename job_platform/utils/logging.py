"""Structured JSON logging via structlog."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def _level_from_string(level: str) -> int:
    resolved: int | str = logging.getLevelName(level.upper())
    if isinstance(resolved, str):
        return logging.INFO
    return resolved


def configure_logging(*, log_level: str, json_logs: bool = True) -> None:
    """
    Configure stdlib logging and structlog for JSON (or console) output.

    Uvicorn and other libraries that use the stdlib ``logging`` module will
    emit through the same formatter, so logs stay consistent.
    """
    level = _level_from_string(log_level)
    logging.root.setLevel(level)

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared_pre_chain: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    renderer: structlog.types.Processor
    if json_logs:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_pre_chain,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict[str, Any],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_pre_chain,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        log = logging.getLogger(name)
        log.handlers.clear()
        log.propagate = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structlog bound logger (stdlib-backed)."""
    return structlog.get_logger(name)
