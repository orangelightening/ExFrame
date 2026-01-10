"""LLM Consciousness Domain Plugins."""

from .failure_detection import FailureDetectionPlugin
from .monitoring import MonitoringPlugin

__all__ = [
    "FailureDetectionPlugin",
    "MonitoringPlugin",
]
