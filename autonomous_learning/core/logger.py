"""
Structured logging for Autonomous Learning System.

Provides consistent logging across all components with:
- Timestamped log entries
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Component/context tags
- JSON formatting for machine parsing
- Human-readable console output
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import json


class AutonomousFormatter(logging.Formatter):
    """Custom formatter that outputs both JSON and human-readable formats."""

    def __init__(self):
        super().__init__()
        self.dateFormat = "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        # Create base log data
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).strftime(self.dateFormat),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in {"name", "msg", "args", "levelname", "levelno", "pathname",
                          "filename", "module", "lineno", "funcName", "created", "msecs",
                          "relativeCreated", "thread", "threadName", "processName",
                          "process", "exc_info", "exc_text", "stack_info"}:
                log_data[key] = value

        # Return JSON for machine parsing
        return json.dumps(log_data)


class HumanReadableFormatter(logging.Formatter):
    """Human-readable console formatter with colors."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
        "RESET": "\033[0m",     # Reset
    }

    def __init__(self):
        fmt = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
        super().__init__(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        formatted = super().format(record)
        # Reset levelname for subsequent formatters
        record.levelname = levelname
        return formatted


# Component-specific loggers
_loggers = {}


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_dir: Optional[Path] = None,
    json_output: bool = True
) -> logging.Logger:
    """
    Get or create a logger for a component.

    Args:
        name: Logger/component name (e.g., "supervisor", "certification")
        level: Logging level (default: INFO)
        log_dir: Directory for log files (optional)
        json_output: Whether to output JSON format (default: True)

    Returns:
        Configured logger instance
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(f"autonomous_learning.{name}")
    logger.setLevel(level)
    logger.handlers.clear()  # Remove any existing handlers
    logger.propagate = False  # Don't propagate to root logger

    # Console handler with human-readable output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(HumanReadableFormatter())
    logger.addHandler(console_handler)

    # File handler with JSON output (if log_dir specified)
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_dir / f"{name}.log")
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(AutonomousFormatter())
        logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger


def configure_root_logging(
    level: int = logging.INFO,
    log_dir: Optional[Path] = None
) -> None:
    """
    Configure root logging for the autonomous learning system.

    Args:
        level: Logging level (default: INFO)
        log_dir: Directory for log files (optional)
    """
    # Create log directory if specified
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(HumanReadableFormatter())
    root_logger.addHandler(console)

    # File handler (if log_dir specified)
    if log_dir:
        file_handler = logging.FileHandler(log_dir / "autonomous_learning.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(AutonomousFormatter())
        root_logger.addHandler(file_handler)


# Convenience functions for common logging patterns
def log_event(logger: logging.Logger, event: str, **kwargs) -> None:
    """Log an event with additional context as extra fields."""
    logger.info(event, extra=kwargs)


def log_error(logger: logging.Logger, error: str, **kwargs) -> None:
    """Log an error with additional context."""
    logger.error(error, extra=kwargs)


def log_metric(logger: logging.Logger, metric: str, value: float, **kwargs) -> None:
    """Log a metric value."""
    logger.info(f"METRIC: {metric}={value}", extra={"metric": metric, "value": value, **kwargs})
