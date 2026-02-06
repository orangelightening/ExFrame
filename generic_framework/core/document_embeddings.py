"""
Document Embeddings - Vector Store for Documents

Provides semantic search over document libraries using embeddings.
Stores all embeddings in a single doc_embeddings.json file per domain.
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Optional import - will fail gracefully if not installed
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


logger = logging.getLogger("document_embeddings")


class DocumentVectorStore:
    """
    Vector store for document embeddings.

    Stores all document embeddings in a single doc_embeddings.json file.
    Includes metadata for staleness detection and incremental updates.
    """

    def __init__(self, domain_name: str, storage_path: Path, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize document vector store.

        Args:
            domain_name: Name of the domain (for logging)
            storage_path: Path to domain directory (where doc_embeddings.json lives)
            model_name: SentenceTransformer model name
        """
        self.domain_name = domain_name
        self.storage_path = storage_path
        self.embeddings_file = storage_path / "doc_embeddings.json"
        self.model_name = model_name
        self.model = None
        self.data = {
            "metadata": {
                "model": model_name,
                "generated": None,
                "document_count": 0
            },
            "documents": {}
        }

    @property
    def is_available(self) -> bool:
        """Check if sentence-transformers is available."""
        return SENTENCE_TRANSFORMERS_AVAILABLE

    def load(self) -> bool:
        """
        Load embeddings from doc_embeddings.json.

        Returns:
            True if loaded successfully, False if file doesn't exist
        """
        if not self.embeddings_file.exists():
            logger.info(f"[{self.domain_name}] No doc embeddings file at {self.embeddings_file}")
            return False

        try:
            with open(self.embeddings_file) as f:
                self.data = json.load(f)

            doc_count = len(self.data.get("documents", {}))
            logger.info(f"[{self.domain_name}] Loaded {doc_count} document embeddings")
            return True

        except Exception as e:
            logger.error(f"[{self.domain_name}] Error loading doc embeddings: {e}")
            return False

    def save(self) -> None:
        """Save all embeddings to doc_embeddings.json."""
        self.data["metadata"]["generated"] = datetime.utcnow().isoformat()
        self.data["metadata"]["document_count"] = len(self.data["documents"])

        # Ensure directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

        with open(self.embeddings_file, 'w') as f:
            json.dump(self.data, f, indent=2)

        logger.info(f"[{self.domain_name}] Saved {len(self.data['documents'])} embeddings to {self.embeddings_file.name}")

    def _hash_file(self, file_path: Path) -> str:
        """Compute SHA256 hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"[{self.domain_name}] Error hashing {file_path}: {e}")
            return ""

    def is_stale(self, doc_path: str) -> bool:
        """
        Check if embedding is stale (document changed or missing).

        Args:
            doc_path: Absolute path to document

        Returns:
            True if embedding needs regeneration
        """
        # No embedding exists
        if doc_path not in self.data["documents"]:
            return True

        # Check if file still exists
        if not Path(doc_path).exists():
            logger.warning(f"[{self.domain_name}] Document no longer exists: {doc_path}")
            return False  # Don't try to regenerate missing files

        # Compare file hash
        stored_hash = self.data["documents"][doc_path].get("hash", "")
        current_hash = self._hash_file(Path(doc_path))

        return stored_hash != current_hash

    def get_stale_documents(self, doc_paths: List[str]) -> List[str]:
        """
        Find all documents with stale or missing embeddings.

        Args:
            doc_paths: List of document paths to check

        Returns:
            List of paths that need (re-)embedding
        """
        stale = []
        for doc_path in doc_paths:
            if self.is_stale(doc_path):
                stale.append(doc_path)

        if stale:
            logger.info(f"[{self.domain_name}] Found {len(stale)} stale/missing embeddings")

        return stale

    def get_embedding(self, doc_path: str) -> Optional[np.ndarray]:
        """
        Get embedding for a document.

        Args:
            doc_path: Path to document

        Returns:
            Embedding as numpy array, or None if not found
        """
        doc_data = self.data["documents"].get(doc_path)
        if doc_data and "code" in doc_data:
            return np.array(doc_data["code"])
        return None

    def set_embedding(self, doc_path: str, embedding: np.ndarray) -> None:
        """
        Store embedding for a document.

        Args:
            doc_path: Path to document
            embedding: Embedding vector
        """
        path = Path(doc_path)

        self.data["documents"][doc_path] = {
            "code": embedding.tolist(),
            "hash": self._hash_file(path),
            "size": path.stat().st_size if path.exists() else 0,
            "modified": path.stat().st_mtime if path.exists() else 0
        }

    def _load_model(self) -> None:
        """Lazy load the SentenceTransformer model."""
        if self.model is None:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )

            logger.info(f"[{self.domain_name}] Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"[{self.domain_name}] Model loaded")

    def generate_embeddings(
        self,
        doc_paths: List[str],
        force: bool = False
    ) -> int:
        """
        Generate embeddings for documents.

        Only generates for stale/missing embeddings unless force=True.

        Args:
            doc_paths: List of document paths
            force: If True, regenerate all embeddings

        Returns:
            Number of embeddings generated
        """
        # Load model if needed
        self._load_model()

        # Find which documents need embedding
        if force:
            to_embed = doc_paths
            logger.info(f"[{self.domain_name}] Force regenerating {len(to_embed)} embeddings")
        else:
            to_embed = self.get_stale_documents(doc_paths)

        if not to_embed:
            logger.info(f"[{self.domain_name}] All embeddings current!")
            return 0

        # Generate embeddings
        generated = 0
        for i, doc_path in enumerate(to_embed):
            try:
                logger.info(f"[{self.domain_name}] [{i+1}/{len(to_embed)}] Embedding {Path(doc_path).name}...")

                # Read document
                with open(doc_path, encoding='utf-8') as f:
                    content = f.read()

                # Generate embedding
                embedding = self.model.encode(content)

                # Store
                self.set_embedding(doc_path, embedding)
                generated += 1

            except Exception as e:
                logger.error(f"[{self.domain_name}] Error embedding {doc_path}: {e}")
                continue

        # Save to disk
        if generated > 0:
            self.save()

        logger.info(f"[{self.domain_name}] Generated {generated} new embeddings")
        return generated

    def search(
        self,
        query: str,
        top_k: int = 10,
        min_similarity: float = 0.3
    ) -> List[Tuple[str, float]]:
        """
        Search for most similar documents.

        Args:
            query: Search query text
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of (doc_path, similarity_score) sorted by relevance (descending)
        """
        if not self.data["documents"]:
            logger.warning(f"[{self.domain_name}] No document embeddings available for search")
            return []

        # Load model if needed
        self._load_model()

        # Generate query embedding
        query_emb = self.model.encode(query)

        # Compute similarities
        similarities = []
        for doc_path, doc_data in self.data["documents"].items():
            # Skip if no code stored
            if "code" not in doc_data:
                continue

            doc_emb = np.array(doc_data["code"])

            # Cosine similarity
            similarity = np.dot(query_emb, doc_emb) / (
                np.linalg.norm(query_emb) * np.linalg.norm(doc_emb)
            )

            if similarity >= min_similarity:
                similarities.append((doc_path, float(similarity)))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        logger.info(f"[{self.domain_name}] Found {len(similarities)} documents above {min_similarity} similarity")

        return similarities[:top_k]

    def remove_missing_documents(self, valid_doc_paths: List[str]) -> int:
        """
        Remove embeddings for documents that no longer exist.

        Args:
            valid_doc_paths: List of currently valid document paths

        Returns:
            Number of embeddings removed
        """
        valid_set = set(valid_doc_paths)
        to_remove = [
            doc_path for doc_path in self.data["documents"].keys()
            if doc_path not in valid_set
        ]

        for doc_path in to_remove:
            del self.data["documents"][doc_path]

        if to_remove:
            logger.info(f"[{self.domain_name}] Removed {len(to_remove)} stale embeddings")
            self.save()

        return len(to_remove)

    def get_stats(self) -> Dict:
        """Get statistics about the document embeddings."""
        return {
            "total_documents": len(self.data["documents"]),
            "model": self.data["metadata"]["model"],
            "last_generated": self.data["metadata"].get("generated"),
            "embeddings_file": str(self.embeddings_file),
            "embeddings_exist": self.embeddings_file.exists()
        }


# Singleton cache for document stores per domain
_document_stores: Dict[str, DocumentVectorStore] = {}


def get_document_store(
    domain_name: str,
    storage_path: Path,
    model_name: str = "all-MiniLM-L6-v2"
) -> Optional[DocumentVectorStore]:
    """
    Get or create a document vector store for a domain.

    Args:
        domain_name: Name of the domain
        storage_path: Path to domain directory
        model_name: SentenceTransformer model name

    Returns:
        DocumentVectorStore instance, or None if not available
    """
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        logger.warning(f"[{domain_name}] sentence-transformers not available, semantic search disabled")
        return None

    # Return cached store if available
    cache_key = f"{domain_name}:{storage_path}"
    if cache_key in _document_stores:
        return _document_stores[cache_key]

    # Create new store
    store = DocumentVectorStore(domain_name, storage_path, model_name)
    _document_stores[cache_key] = store

    return store
