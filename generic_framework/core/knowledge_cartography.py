"""
Knowledge Cartography (KCart) - Dialectical Knowledge Mapping

Stores and analyzes all query/response pairs to build a personal knowledge map.
Implements compressed storage, context loading, and basic analytics.

See: kcart.md for full design documentation
"""

import gzip
import json
import os
from datetime import datetime
import zoneinfo
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class KnowledgeCartography:
    """Manages query/response history storage and retrieval."""

    def __init__(self, domain_path: str, config: Optional[Dict] = None):
        """
        Initialize knowledge cartography for a domain.

        Args:
            domain_path: Path to domain directory
            config: Optional configuration dict from domain.json
        """
        self.domain_path = domain_path
        self.config = config or {}

        # Configuration with defaults
        self.enabled = self.config.get("enabled", True)
        self.compression = self.config.get("compression", "gzip")
        self.context_window = self.config.get("context_window", 20)
        self.max_entries = self.config.get("max_entries", None)
        self.store_evoked_questions = self.config.get("store_evoked_questions", True)
        self.extract_concepts = self.config.get("extract_concepts", False)

        # File paths
        self.history_file = os.path.join(domain_path, "query_history.json.gz")

        logger.info(f"KCart initialized for {domain_path} (enabled={self.enabled}, "
                   f"context_window={self.context_window})")

    def save_query_response(
        self,
        query: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a query/response pair to compressed history.

        Args:
            query: User's query text
            response: System's response text
            metadata: Optional metadata (source, confidence, patterns_used, etc.)

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            # Load existing history
            history = self._load_history_raw()

            # Get timezone-aware timestamp
            tz_name = os.getenv("APP_TIMEZONE", "America/Vancouver")
            try:
                tz = zoneinfo.ZoneInfo(tz_name)
                timestamp = datetime.now(tz).isoformat()
            except Exception as e:
                logger.warning(f"Invalid timezone '{tz_name}', falling back to UTC: {e}")
                timestamp = datetime.utcnow().isoformat()

            # Create new entry
            entry = {
                "id": len(history) + 1,
                "timestamp": timestamp,
                "query": query,
                "response": response,
                "metadata": metadata or {}
            }

            # Add evoked questions if present in metadata
            if self.store_evoked_questions and metadata:
                evoked = metadata.get("evoked_questions", [])
                if evoked:
                    entry["evoked_questions"] = evoked

            # Append to history
            history.append(entry)

            # Apply max_entries limit if set
            if self.max_entries and len(history) > self.max_entries:
                # Keep only the most recent max_entries
                history = history[-self.max_entries:]
                logger.info(f"Trimmed history to {self.max_entries} entries")

            # Save compressed
            self._save_history_raw(history)

            logger.debug(f"Saved Q/R pair #{entry['id']} to {self.history_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save Q/R pair: {e}", exc_info=True)
            return False

    def load_recent_context(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Load recent query/response pairs formatted as conversation context.

        Args:
            limit: Number of recent pairs to load (default: from config)

        Returns:
            List of message dicts suitable for LLM context:
            [
                {"role": "user", "content": "query text"},
                {"role": "assistant", "content": "response text"},
                ...
            ]
        """
        if not self.enabled:
            return []

        limit = limit or self.context_window

        try:
            # Load full history
            history = self._load_history_raw()

            if not history:
                return []

            # Get last N entries
            recent = history[-limit:] if len(history) > limit else history

            # Format as conversation messages
            context = []
            for entry in recent:
                context.append({
                    "role": "user",
                    "content": entry["query"]
                })
                context.append({
                    "role": "assistant",
                    "content": entry["response"]
                })

            logger.debug(f"Loaded {len(recent)} Q/R pairs ({len(context)} messages) for context")
            return context

        except Exception as e:
            logger.error(f"Failed to load context: {e}", exc_info=True)
            return []

    def get_history_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about query history.

        Returns:
            Dict with summary info (count, date range, avg confidence, etc.)
        """
        try:
            history = self._load_history_raw()

            if not history:
                return {
                    "count": 0,
                    "enabled": self.enabled
                }

            # Calculate statistics
            confidences = [
                entry["metadata"].get("confidence", 0.0)
                for entry in history
                if "metadata" in entry
            ]

            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return {
                "count": len(history),
                "enabled": self.enabled,
                "first_query": history[0]["timestamp"] if history else None,
                "last_query": history[-1]["timestamp"] if history else None,
                "avg_confidence": round(avg_confidence, 3),
                "context_window": self.context_window,
                "compression": self.compression
            }

        except Exception as e:
            logger.error(f"Failed to get history summary: {e}", exc_info=True)
            return {"count": 0, "enabled": self.enabled, "error": str(e)}

    def _load_history_raw(self) -> List[Dict]:
        """Load raw history from compressed file."""
        if not os.path.exists(self.history_file):
            return []

        try:
            with gzip.open(self.history_file, 'rt', encoding='utf-8') as f:
                history = json.load(f)
            return history
        except Exception as e:
            logger.error(f"Failed to load history from {self.history_file}: {e}")
            return []

    def _save_history_raw(self, history: List[Dict]):
        """Save raw history to compressed file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

            # Write compressed
            with gzip.open(self.history_file, 'wt', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to save history to {self.history_file}: {e}")
            raise


def get_kcart(domain_path: str, domain_config: Dict) -> KnowledgeCartography:
    """
    Factory function to get KnowledgeCartography instance for a domain.

    Args:
        domain_path: Path to domain directory
        domain_config: Domain configuration dict (from domain.json)

    Returns:
        KnowledgeCartography instance
    """
    # Get query_history config from domain.json
    kcart_config = domain_config.get("query_history", {})

    return KnowledgeCartography(domain_path, kcart_config)
