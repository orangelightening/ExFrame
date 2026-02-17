"""
Tao Storage Module

Provides persistent storage for query/response history with compression.
"""

from .storage import KnowledgeCartography, get_kcart, load_history

__all__ = ["KnowledgeCartography", "get_kcart", "load_history"]
