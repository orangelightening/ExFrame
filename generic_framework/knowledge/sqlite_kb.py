#
# Copyright 2025 ExFrame Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
SQLite Knowledge Base - High-performance pattern storage with FTS5.

Implements the KnowledgeBasePlugin interface using SQLite with:
- FTS5 full-text search for fast pattern matching
- JSON1 extension for flexible schema
- Proper indexing for fast lookups
- ACID transactions for data integrity
- Async support via aiosqlite
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import aiosqlite

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_base_plugin import KnowledgeBasePlugin
from core.knowledge_base import KnowledgeBaseConfig


logger = logging.getLogger(__name__)


class SQLiteKnowledgeBase(KnowledgeBasePlugin):
    """
    SQLite-based knowledge base with full-text search.

    Features:
    - FTS5 full-text search on name, problem, solution
    - Indexed searches on status, confidence, domain
    - JSON blob storage for flexible schema
    - Thread-safe async operations
    - Automatic migration from JSON files

    Configuration:
        storage_path: Path to database directory (will create .db file)
        pattern_format: "json" (stored as JSON in database)
        pattern_schema: Optional schema validation
    """

    name = "SQLite Knowledge Base"

    # SQL Schema with full pattern lifecycle support
    SCHEMA = """
    -- Main patterns table
    CREATE TABLE IF NOT EXISTS patterns (
        id TEXT PRIMARY KEY,
        status TEXT NOT NULL DEFAULT 'candidate',
        confidence REAL NOT NULL DEFAULT 0.5,
        domain_id TEXT NOT NULL,
        origin_query TEXT,
        pattern_type TEXT,
        name TEXT,
        problem TEXT,
        solution TEXT,
        description TEXT,
        tags TEXT,
        examples TEXT,
        conditions TEXT,
        related_patterns TEXT,
        prerequisites TEXT,
        alternatives TEXT,
        sources TEXT,
        created_at TEXT,
        updated_at TEXT,
        times_accessed INTEGER DEFAULT 0,
        user_rating REAL,
        reviewed_by TEXT,
        reviewed_at TEXT,
        review_notes TEXT,
        generated_by TEXT,
        generated_at TEXT,
        usage_count INTEGER DEFAULT 0,
        llm_generated INTEGER DEFAULT 0
    );

    -- Indexes for fast lookups
    CREATE INDEX IF NOT EXISTS idx_status ON patterns(status);
    CREATE INDEX IF NOT EXISTS idx_domain ON patterns(domain_id);
    CREATE INDEX IF NOT EXISTS idx_confidence ON patterns(confidence);
    CREATE INDEX IF NOT EXISTS idx_origin_query ON patterns(origin_query);
    CREATE INDEX IF NOT EXISTS idx_type ON patterns(pattern_type);

    -- Full-text search table
    CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
        name,
        problem,
        solution,
        description,
        content='patterns',
        content_rowid='rowid',
        tokenize='porter'
    );

    -- Triggers to keep FTS in sync
    CREATE TRIGGER IF NOT EXISTS patterns_ai AFTER INSERT ON patterns BEGIN
        INSERT INTO patterns_fts(rowid, name, problem, solution, description)
        VALUES (new.rowid, new.name, new.problem, new.solution, new.description);
    END;

    CREATE TRIGGER IF NOT EXISTS patterns_ad AFTER DELETE ON patterns BEGIN
        INSERT INTO patterns_fts(patterns_fts, rowid, name, problem, solution, description)
        VALUES ('delete', old.rowid, old.name, old.problem, old.solution, old.description);
    END;

    CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE ON patterns BEGIN
        UPDATE patterns_fts
        SET name = new.name,
            problem = new.problem,
            solution = new.solution,
            description = new.description
        WHERE rowid = new.rowid;
    END;
    """

    def __init__(self, config: KnowledgeBaseConfig):
        """
        Initialize SQLite knowledge base.

        Args:
            config: Knowledge base configuration
        """
        self.config = config
        self.storage_path = Path(config.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Database file path
        self.db_path = self.storage_path / "patterns.db"

        # Connection state
        self._db: Optional[aiosqlite.Connection] = None
        self._loaded = False

        # Lock for database operations
        self._lock = asyncio.Lock()

        logger.info(f"SQLite KB initialized at {self.db_path}")

    async def _get_db(self) -> aiosqlite.Connection:
        """Get or create database connection."""
        if self._db is None:
            self._db = await aiosqlite.connect(self.db_path)
            # Set row_factory for dict-like access to rows
            self._db.row_factory = aiosqlite.Row
            # Enable optimizations
            await self._db.execute("PRAGMA journal_mode = WAL")
            await self._db.execute("PRAGMA synchronous = NORMAL")
            await self._db.execute("PRAGMA cache_size = -64000")
            await self._db.execute("PRAGMA foreign_keys = ON")
        return self._db

    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            await self._db.close()
            self._db = None

    async def _ensure_database(self) -> None:
        """Create database schema if it doesn't exist."""
        async with self._lock:
            db = await self._get_db()
            await db.executescript(self.SCHEMA)
            await db.commit()

    async def load_patterns(self) -> None:
        """
        Load patterns - validates database and optionally imports from JSON.

        For SQLite, patterns are loaded on-demand, so we:
        1. Ensure database schema exists
        2. Check if JSON import is needed
        3. Validate database is accessible
        """
        if self._loaded:
            return

        await self._ensure_database()

        # Check if we need to import from JSON
        json_file = self.storage_path / "patterns.json"
        if json_file.exists():
            await self._import_from_json_if_needed(json_file)

        self._loaded = True

        # Validate
        count = await self.async_get_pattern_count()
        logger.info(f"SQLite KB loaded: {count} patterns in database")

    async def _import_from_json_if_needed(self, json_file: Path) -> None:
        """Import patterns from JSON file if database is empty."""
        db = await self._get_db()

        # Check if database has patterns
        async with db.execute("SELECT COUNT(*) as count FROM patterns") as cursor:
            row = await cursor.fetchone()
            if row and row[0] > 0:
                return  # Already has data, skip import

        logger.info(f"Importing patterns from {json_file}")
        with open(json_file, 'r') as f:
            patterns = json.load(f)

        imported = 0
        for pattern in patterns:
            pattern_id = pattern.get('id') or pattern.get('pattern_id')
            if not pattern_id:
                continue

            await self.add_pattern(pattern)
            imported += 1

        logger.info(f"Imported {imported} patterns from JSON")

    def get_pattern_count(self) -> int:
        """
        Get total number of patterns (synchronous).

        Note: This uses a synchronous connection for compatibility.
        For async contexts, the internal methods use async_get_pattern_count.
        """
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT COUNT(*) as count FROM patterns")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0

    async def async_get_pattern_count(self) -> int:
        """Async version of get_pattern_count."""
        db = await self._get_db()
        async with db.execute("SELECT COUNT(*) as count FROM patterns") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Search patterns using full-text search.

        Uses FTS5 for relevance-ranked full-text search on
        name, problem, and solution fields.

        Args:
            query: Search query text
            category: Optional category (pattern_type) filter
            limit: Maximum results to return
            **filters: Additional filters (status, confidence_min, etc.)

        Returns:
            List of matching patterns with relevance scores
        """
        if not self._loaded:
            await self.load_patterns()

        # Extract search terms
        query_terms = self._extract_terms(query)

        if not query_terms:
            # No valid search terms, return recent patterns
            return await self._get_recent_patterns(limit)

        db = await self._get_db()

        # Build FTS5 search query
        fts_query = " ".join(query_terms)

        # Build SQL query with filters
        sql = """
            SELECT
                p.*,
                fts.rank as fts_rank
            FROM patterns p
            JOIN patterns_fts fts ON p.rowid = fts.rowid
            WHERE patterns_fts MATCH ?
        """

        params = [fts_query]

        # Add category filter
        if category:
            sql += " AND p.pattern_type = ?"
            params.append(category)

        # Add status filter
        if 'status' in filters:
            sql += " AND p.status = ?"
            params.append(filters['status'])

        # Add confidence filter
        if 'confidence_min' in filters:
            sql += " AND p.confidence >= ?"
            params.append(filters['confidence_min'])

        # Order by FTS rank and confidence
        sql += " ORDER BY fts.rank DESC, p.confidence DESC LIMIT ?"
        params.append(limit)

        async with db.execute(sql, params) as cursor:
            rows = await cursor.fetchall()

        # Convert to dict format
        results = []
        for row in rows:
            pattern = await self._row_to_dict(row)
            # Calculate combined relevance score
            pattern['confidence'] = await self._calculate_relevance(pattern, query, query_terms)
            results.append(pattern)

        return results

    async def get_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific pattern by ID.

        Args:
            pattern_id: Unique pattern identifier

        Returns:
            Pattern dict or None if not found
        """
        if not self._loaded:
            await self.load_patterns()

        db = await self._get_db()
        async with db.execute("SELECT * FROM patterns WHERE id = ?", (pattern_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return await self._row_to_dict(row)
        return None

    async def get_all_patterns(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all patterns, optionally limited.

        Args:
            limit: Maximum patterns to return

        Returns:
            List of pattern dictionaries
        """
        if not self._loaded:
            await self.load_patterns()

        db = await self._get_db()
        async with db.execute(
            "SELECT * FROM patterns ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()

        return [await self._row_to_dict(row) for row in rows]

    def get_all_categories(self) -> List[str]:
        """
        Get all unique categories (pattern types).

        Note: Synchronous wrapper. Use async version in async contexts.
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT DISTINCT pattern_type FROM patterns WHERE pattern_type IS NOT NULL ORDER BY pattern_type"
        )
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories

    async def async_get_all_categories(self) -> List[str]:
        """Async version of get_all_categories."""
        db = await self._get_db()
        async with db.execute(
            "SELECT DISTINCT pattern_type FROM patterns WHERE pattern_type IS NOT NULL ORDER BY pattern_type"
        ) as cursor:
            rows = await cursor.fetchall()
        return [row[0] for row in rows]

    async def add_pattern(self, pattern: Dict[str, Any]) -> str:
        """
        Add a new pattern to the database.

        Args:
            pattern: Pattern dictionary

        Returns:
            Pattern ID
        """
        # Generate ID if not present
        if 'id' not in pattern:
            count = await self.async_get_pattern_count()
            domain = pattern.get('domain', 'unknown')
            pattern['id'] = f"{domain}_sqlite_{count + 1:05d}"

        # Add timestamps
        now = datetime.now(timezone.utc).isoformat()
        pattern['created_at'] = now
        pattern['updated_at'] = now

        # Build INSERT statement with exactly 28 placeholders
        placeholders = ", ".join(["?"] * 28)
        sql = f"""
            INSERT INTO patterns (
                id, status, confidence, domain_id, origin_query,
                pattern_type, name, problem, solution, description,
                tags, examples, conditions, related_patterns, prerequisites,
                alternatives, sources, created_at, updated_at,
                times_accessed, user_rating, reviewed_by, reviewed_at,
                review_notes, generated_by, generated_at, usage_count,
                llm_generated
            ) VALUES ({placeholders})
        """

        params = (
            pattern.get('id'),
            pattern.get('status', 'candidate'),
            pattern.get('confidence', pattern.get('confidence_score', 0.5)),
            pattern.get('domain', ''),
            pattern.get('origin_query'),
            pattern.get('pattern_type', pattern.get('type')),
            pattern.get('name'),
            pattern.get('problem'),
            pattern.get('solution'),
            pattern.get('description'),
            json.dumps(pattern.get('tags', [])),
            json.dumps(pattern.get('examples', [])),
            json.dumps(pattern.get('conditions', {})),
            json.dumps(pattern.get('related_patterns', [])),
            json.dumps(pattern.get('prerequisites', [])),
            json.dumps(pattern.get('alternatives', [])),
            json.dumps(pattern.get('sources', [])),
            pattern.get('created_at'),
            pattern.get('updated_at'),
            pattern.get('times_accessed', 0),
            pattern.get('user_rating'),
            pattern.get('reviewed_by'),
            pattern.get('reviewed_at'),
            pattern.get('review_notes'),
            pattern.get('generated_by'),
            pattern.get('generated_at'),
            pattern.get('usage_count', 0),
            1 if pattern.get('llm_generated') else 0
        )

        db = await self._get_db()
        await db.execute(sql, params)
        await db.commit()

        return pattern['id']

    async def update_pattern(self, pattern_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing pattern.

        Args:
            pattern_id: Pattern ID to update
            updates: Dictionary of fields to update
        """
        # Build UPDATE statement dynamically
        set_clauses = []
        params = []

        for key, value in updates.items():
            if key in ['tags', 'examples', 'conditions', 'related_patterns',
                      'prerequisites', 'alternatives', 'sources']:
                # JSON fields
                set_clauses.append(f"{key} = ?")
                params.append(json.dumps(value))
            else:
                set_clauses.append(f"{key} = ?")
                params.append(value)

        if not set_clauses:
            return

        # Always update updated_at
        set_clauses.append("updated_at = ?")
        params.append(datetime.now(timezone.utc).isoformat())

        params.append(pattern_id)

        sql = f"UPDATE patterns SET {', '.join(set_clauses)} WHERE id = ?"

        db = await self._get_db()
        await db.execute(sql, params)
        await db.commit()

    async def delete_pattern(self, pattern_id: str) -> None:
        """
        Delete a pattern.

        Args:
            pattern_id: Pattern ID to delete
        """
        db = await self._get_db()
        await db.execute("DELETE FROM patterns WHERE id = ?", (pattern_id,))
        await db.commit()

    async def record_feedback(
        self,
        pattern_id: str,
        feedback: Dict[str, Any]
    ) -> None:
        """
        Record user feedback for learning.

        Args:
            pattern_id: Pattern ID
            feedback: Feedback dict with rating, accessed, etc.
        """
        db = await self._get_db()

        # Update confidence based on rating
        if 'rating' in feedback:
            async with db.execute(
                "SELECT confidence FROM patterns WHERE id = ?",
                (pattern_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    current_confidence = row[0]
                    rating = feedback['rating'] / 5.0  # Normalize to 0-1
                    # Blend current confidence with new rating
                    new_confidence = (current_confidence * self.config.feedback_decay +
                                    rating * (1 - self.config.feedback_decay))

                    await db.execute(
                        "UPDATE patterns SET confidence = ? WHERE id = ?",
                        (round(new_confidence, 2), pattern_id)
                    )

        # Update access count
        if 'accessed' in feedback:
            await db.execute(
                "UPDATE patterns SET times_accessed = times_accessed + 1 WHERE id = ?",
                (pattern_id,)
            )

        await db.commit()

    def get_patterns_by_category(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get patterns by category (pattern_type).

        Args:
            category: Category filter, or None for all

        Returns:
            List of patterns
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)

        if category:
            cursor = conn.execute(
                "SELECT * FROM patterns WHERE pattern_type = ? ORDER BY confidence DESC",
                (category,)
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM patterns ORDER BY pattern_type, confidence DESC"
            )

        # Convert to dicts synchronously
        patterns = []
        for row in cursor.fetchall():
            pattern = dict(row)
            # Parse JSON fields
            for field in ['tags', 'examples', 'conditions', 'related_patterns',
                         'prerequisites', 'alternatives', 'sources']:
                if pattern.get(field):
                    try:
                        pattern[field] = json.loads(pattern[field])
                    except:
                        pattern[field] = []
            patterns.append(pattern)

        conn.close()
        return patterns

    async def find_similar(
        self,
        query: str,
        threshold: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find patterns similar to query.

        Args:
            query: Query text
            threshold: Minimum similarity score (default: config.similarity_threshold)

        Returns:
            List of (pattern, similarity_score) tuples
        """
        if threshold is None:
            threshold = self.config.similarity_threshold

        results = await self.search(query, limit=self.config.max_results)

        scored = []
        for pattern in results:
            score = await self._calculate_similarity(query, pattern)
            if score >= threshold:
                scored.append((pattern, score))

        # Sort by similarity
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    # ========== Helper Methods ==========

    async def _row_to_dict(self, row: aiosqlite.Row) -> Dict[str, Any]:
        """Convert SQLite row to pattern dictionary."""
        # aiosqlite.Row needs to be converted manually
        pattern = {key: row[key] for key in row.keys()}

        # Parse JSON fields
        json_fields = ['tags', 'examples', 'conditions', 'related_patterns',
                      'prerequisites', 'alternatives', 'sources']

        for field in json_fields:
            if pattern.get(field):
                try:
                    pattern[field] = json.loads(pattern[field])
                except (json.JSONDecodeError, TypeError):
                    pass  # Keep as-is if not valid JSON
            else:
                pattern[field] = []

        # Convert llm_generated back to bool
        if pattern.get('llm_generated') is not None:
            pattern['llm_generated'] = bool(pattern['llm_generated'])

        # Add pattern_id for compatibility
        if 'pattern_id' not in pattern:
            pattern['pattern_id'] = pattern['id']

        # Add confidence_score for compatibility
        if 'confidence_score' not in pattern:
            pattern['confidence_score'] = pattern['confidence']

        return pattern

    def _extract_terms(self, query: str) -> List[str]:
        """
        Extract significant terms from query.

        Removes stop words and short terms.
        """
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are',
            'how', 'what', 'when', 'where', 'why', 'who', 'do', 'does',
            'can', 'could', 'would', 'should', 'i', 'you', 'we', 'they'
        }

        # Extract words
        words = re.findall(r'\b\w+\b', query.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]

    async def _calculate_relevance(
        self,
        pattern: Dict[str, Any],
        query: str,
        query_terms: List[str]
    ) -> float:
        """
        Calculate relevance score for a pattern.

        Combines FTS rank with pattern confidence.
        """
        # Start with base confidence
        base_confidence = pattern.get('confidence', 0.5)

        # FTS rank (higher is better in FTS5, but we normalize)
        fts_rank = pattern.get('fts_rank', 0)

        # Normalize FTS rank to 0-1 range
        if fts_rank < 0:
            fts_score = 1.0 / (1.0 + abs(fts_rank))
        else:
            fts_score = 1.0

        # Combine: 70% FTS relevance, 30% pattern confidence
        return (fts_score * 0.7) + (base_confidence * 0.3)

    async def _calculate_similarity(self, query: str, pattern: Dict[str, Any]) -> float:
        """
        Calculate similarity score (0-1).
        """
        query_lower = query.lower()
        query_terms = self._extract_terms(query_lower)

        if not query_terms:
            return 0.0

        # Simple term matching
        score = 0.0
        for term in query_terms:
            # Check name (highest weight)
            if term in pattern.get('name', '').lower():
                score += 2.0

            # Check problem
            if term in pattern.get('problem', '').lower():
                score += 1.0

            # Check solution
            if term in pattern.get('solution', '').lower():
                score += 0.5

        # Normalize
        max_score = len(query_terms) * 3.5
        return min(score / max_score, 1.0) if max_score > 0 else 0.0

    async def _get_recent_patterns(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent patterns when search has no valid terms."""
        db = await self._get_db()
        async with db.execute(
            "SELECT * FROM patterns ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
        return [await self._row_to_dict(row) for row in rows]

    async def health_check(self) -> Dict[str, Any]:
        """
        Check database health.

        Returns:
            Health status dict
        """
        db = await self._get_db()

        # Get pattern count
        count = await self.async_get_pattern_count()

        # Check FTS is working
        async with db.execute("SELECT COUNT(*) as count FROM patterns_fts") as cursor:
            fts_row = await cursor.fetchone()
            fts_count = fts_row[0] if fts_row else 0

        # Get database size
        db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

        return {
            'status': 'healthy',
            'patterns_loaded': count,
            'fts_index_size': fts_count,
            'database_size_mb': round(db_size / (1024 * 1024), 2),
            'categories': await self.async_get_all_categories(),
            'backend': self.name
        }
