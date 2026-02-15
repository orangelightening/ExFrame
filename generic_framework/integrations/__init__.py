"""
ExFrame External Integrations

This package contains integrations with external services like search APIs.
"""

from .brave_search import BraveSearch, create_brave_client, brave_search

__all__ = ["BraveSearch", "create_brave_client", "brave_search"]
