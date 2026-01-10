"""
SQLite Knowledge Base - SQLite database pattern storage.

Implements the KnowledgeBasePlugin interface for SQLite storage.
Useful for larger datasets and faster queries.
"""

import sqlite3
import json
import aiosqlite
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_base_plugin import KnowledgeBasePlugin
from core.knowledge_base import KnowledgeBaseConfig


class SQLiteKnowledgeBase(KnowledgeBasePlugin):
    """
    SQLite-based knowledge base implementation.

    Stores patterns in SQLite database for better performance
    with larger datasets and more complex queries.
    """

    name = "SQLite Knowledge Base"

    def __init__(self, config: KnowledgeBaseConfig):
        """Initialize with config."""
        self.config = config
        self.db_path = Path(config.storage_path) / "patterns.db"
        self._connection = None
        self._loaded = False

    async def load_patterns(self) -> None:
        """Load patterns - creates/updates database from JSON if needed."""
        if self._loaded:
            return

        # Initialize database
        await self._init_db()

        # Check if we need to import from JSON
        json_file = Path(self.config.storage_path) / "patterns.json"
        if json_file.exists():
            await self._import_from_json(json_file)

        self._loaded = True

    async def _init_db(self) -> None:
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    pattern_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT,
                    category TEXT,
                    problem TEXT,
                    solution TEXT,
                    examples TEXT,
                    tags TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create full-text search table
            await db.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts
                USING fts5(
                    pattern_id, name, problem, solution,
                    content='patterns',
                    content_rowid='rowid'
                )
            """)

            # Create indexes
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_category
                ON patterns(category)
            """)

            await db.commit()

    async def _import_from_json(self, json_file: Path) -> None:
        """Import patterns from JSON file."""
        with open(json_file, 'r') as f:
            patterns = json.load(f)

        async with aiosqlite.connect(self.db_path) as db:
            for pattern in patterns:
                pattern_id = pattern.get('pattern_id') or pattern.get('id', '')
                if not pattern_id:
                    continue

                await db.execute("""
                    INSERT OR REPLACE INTO patterns
                    (pattern_id, name, type, category, problem, solution, examples, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern_id,
                    pattern.get('name', ''),
                    pattern.get('type', ''),
                    pattern.get('category', ''),
                    pattern.get('problem', ''),
                    pattern.get('solution', ''),
                    json.dumps(pattern.get('examples', [])),
                    json.dumps(pattern.get('tags', [])),
                    json.dumps(pattern.get('metadata', {}))
                ))

            await db.commit()

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Search patterns using full-text search.

        Args:
            query: Search query
            category: Optional category filter
            limit: Max results
            **filters: Additional filters (e.g., min_relevance)

        Returns:
            List of matching patterns sorted by relevance.
        """
        if not self._loaded:
            await self.load_patterns()

        async with aiosqlite.connect(self.db_path) as db:
            # Build query
            sql = """
                SELECT DISTINCT p.pattern_id, p.name, p.type, p.category,
                       p.problem, p.solution, p.examples, p.tags, p.metadata
                FROM patterns p
                LEFT JOIN patterns_fts fts ON p.pattern_id = fts.pattern_id
                WHERE 1=1
            """
            params = []

            # Add category filter
            if category:
                sql += " AND p.category = ?"
                params.append(category)

            # Add full-text search
            if query:
                sql += " AND patterns_fts MATCH ?"
                params.append(query)

            # Add limit
            sql += " LIMIT ?"
            params.append(limit)

            # Execute query
            async with db.execute(sql, params) as cursor:
                rows = await cursor.fetchall()

            # Convert to dict format
            results = []
            for row in rows:
                results.append({
                    'pattern_id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'category': row[3],
                    'problem': row[4],
                    'solution': row[5],
                    'examples': json.loads(row[6]) if row[6] else [],
                    'tags': json.loads(row[7]) if row[7] else [],
                    'metadata': json.loads(row[8]) if row[8] else {}
                })

            return results

    async def get_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific pattern by ID."""
        if not self._loaded:
            await self.load_patterns()

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM patterns WHERE pattern_id = ?",
                (pattern_id,)
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    return None

                return {
                    'pattern_id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'category': row[3],
                    'problem': row[4],
                    'solution': row[5],
                    'examples': json.loads(row[6]) if row[6] else [],
                    'tags': json.loads(row[7]) if row[7] else [],
                    'metadata': json.loads(row[8]) if row[8] else {}
                }

    def get_all_categories(self) -> List[str]:
        """Get all available categories."""
        # This needs to be async but keeping sync for now
        return []

    def get_pattern_count(self) -> int:
        """Get total number of patterns."""
        # This needs to be async but keeping sync for now
        return 0

    async def health_check(self) -> Dict[str, Any]:
        """Check database health."""
        import os

        return {
            "status": "healthy",
            "backend": self.name,
            "db_path": str(self.db_path),
            "db_exists": self.db_path.exists(),
            "db_size_mb": self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
        }
