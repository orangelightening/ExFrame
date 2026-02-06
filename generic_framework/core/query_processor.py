"""
Query processor with pattern override logic.

The core decision:
1. Search domain for patterns matching query
2. If patterns found → use them (override)
3. Else → use persona's data source
"""

from typing import Dict, Any, Optional, List
import logging
from pathlib import Path
from .personas import get_persona


logger = logging.getLogger("query_processor")


async def process_query(
    query: str,
    domain_name: str,
    context: Optional[Dict] = None,
    search_patterns: Optional[bool] = None,
    show_thinking: bool = False
) -> Dict[str, Any]:
    """
    Process query with pattern override logic.

    THE CORE DECISION:
    - If search_patterns=True → search for patterns, use them if found
    - If search_patterns=False → skip pattern search, use persona data source
    - If search_patterns=None → use domain config default

    Args:
        query: User query
        domain_name: Domain name
        context: Optional context dict
        search_patterns: Optional flag to control pattern search
                        - True: Search for patterns
                        - False: Skip pattern search, use persona data source
                        - None: Use domain config default (default)
        show_thinking: Whether to show step-by-step reasoning (default: False)

    Returns:
        Response dict with answer and metadata
    """
    logger.info(f"Processing query for domain: {domain_name}")

    # Load domain config
    domain_config = _load_domain_config(domain_name)

    # Get persona
    persona_type = domain_config.get("persona", "librarian")
    persona = get_persona(persona_type)

    logger.info(f"Using persona: {persona_type}")

    # THE SWITCH: Determine if we should search patterns
    # Priority: explicit flag > context flag > domain config > default True
    if search_patterns is not None:
        # Explicit parameter
        should_search_patterns = search_patterns
        logger.info(f"Pattern search from parameter: {should_search_patterns}")
    elif context and "search_patterns" in context:
        # From context dict
        should_search_patterns = context["search_patterns"]
        logger.info(f"Pattern search from context: {should_search_patterns}")
    else:
        # From domain config or default
        should_search_patterns = domain_config.get("enable_pattern_override", True)
        logger.info(f"Pattern search from config: {should_search_patterns}")

    # Search domain patterns (if enabled)
    patterns = None
    if should_search_patterns:
        patterns = _search_domain_patterns(domain_name, query)

        if patterns:
            logger.info(f"Found {len(patterns)} patterns for override")
        else:
            logger.info("No patterns found, using persona data source")
    else:
        logger.info("Pattern search disabled, using persona data source directly")

    # THE DECISION: Override or not?
    # Prepare context with show_thinking flag
    context = context or {}
    context["show_thinking"] = show_thinking

    if patterns and len(patterns) > 0:
        # Use patterns (override)
        response = await persona.respond(
            query,
            override_patterns=patterns,
            context=context
        )
    else:
        # Use persona's data source
        # For librarian persona, try to load documents if available
        if persona_type == "librarian":
            documents = _search_domain_documents(domain_name, domain_config, query)
            if documents:
                logger.info(f"Found {len(documents)} documents for library search")
                # Pass documents in context for persona to use
                context["library_documents"] = documents

        response = await persona.respond(query, context=context)

    # Add domain metadata
    response["domain"] = domain_name
    response["pattern_override_used"] = bool(patterns)
    response["persona_type"] = persona_type
    response["search_patterns_enabled"] = should_search_patterns

    return response


def _load_domain_config(domain_name: str) -> Dict[str, Any]:
    """
    Load domain configuration from domain.json file.

    Args:
        domain_name: Domain name

    Returns:
        Domain config dict
    """
    import json
    from pathlib import Path

    # Try common universe paths
    possible_paths = [
        f"/app/domains/{domain_name}/domain.json",  # Container path
        f"universes/MINE/domains/{domain_name}/domain.json",  # Local path
        f"domains/{domain_name}/domain.json"  # Alternate
    ]

    for path in possible_paths:
        try:
            config_path = Path(path)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)

                logger.info(f"Loaded config from {path}")

                # Extract persona or default
                persona = config.get("persona", "librarian")

                # Log what we found
                logger.info(f"Domain {domain_name}: persona={persona}")

                # Return full config (needed for document search, etc.)
                # But ensure key fields are set
                config["name"] = config.get("domain_id", domain_name)
                config["persona"] = persona
                if "enable_pattern_override" not in config:
                    config["enable_pattern_override"] = True

                return config

        except Exception as e:
            logger.debug(f"Could not load from {path}: {e}")
            continue

    # Fallback: return default config
    logger.warning(f"Could not find config file for {domain_name}, using defaults")
    return {
        "name": domain_name,
        "persona": "librarian",
        "enable_pattern_override": True
    }


def _search_domain_patterns(
    domain_name: str,
    query: str,
    max_results: int = 5
) -> Optional[list]:
    """
    Search domain for patterns matching query.

    Simple implementation for Phase 1: just reads patterns.json
    and returns first N patterns (no scoring yet).

    Args:
        domain_name: Domain name
        query: Search query
        max_results: Maximum patterns to return

    Returns:
        List of pattern dicts or None
    """
    import json
    from pathlib import Path

    # Try common universe paths for patterns.json
    possible_paths = [
        f"/app/domains/{domain_name}/patterns.json",  # Container path
        f"universes/MINE/domains/{domain_name}/patterns.json",  # Local path
        f"domains/{domain_name}/patterns.json"  # Alternate
    ]

    for path in possible_paths:
        try:
            patterns_path = Path(path)
            if patterns_path.exists():
                with open(patterns_path, 'r') as f:
                    data = json.load(f)

                # Extract patterns array
                if isinstance(data, dict) and 'patterns' in data:
                    patterns = data['patterns']
                elif isinstance(data, list):
                    patterns = data
                else:
                    logger.warning(f"Unexpected patterns format in {path}")
                    continue

                # Return first N patterns (simple for Phase 1)
                # TODO: Add proper semantic search in Phase 2
                if patterns and len(patterns) > 0:
                    logger.info(f"Found {len(patterns)} patterns in {domain_name}")
                    return patterns[:max_results]

                return None

        except Exception as e:
            logger.debug(f"Could not load patterns from {path}: {e}")
            continue

    logger.info(f"No patterns found for {domain_name}")
    return None


def _search_domain_documents(
    domain_name: str,
    domain_config: Dict[str, Any],
    query: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Search domain for documents to use as library context.

    Can use either:
    - Semantic search (if query provided and document_search_algorithm="semantic")
    - Filesystem order (default, legacy Phase 1 behavior)

    Simple approach:
    - library_base_path: Base directory to search
    - ignored.md: Optional file listing patterns to ignore (one per line)
    - Everything else: All .md files are fair game

    Args:
        domain_name: Domain name
        domain_config: Domain configuration dict
        query: Optional query for semantic ranking

    Returns:
        List of document dicts or None
    """
    # Check if semantic search is enabled and available
    doc_search_config = domain_config.get("document_search", {})
    algorithm = doc_search_config.get("algorithm", "filesystem")

    if algorithm == "semantic" and query:
        # Try semantic search
        result = _search_domain_documents_semantic(domain_name, domain_config, query)
        if result is not None:
            return result
        # Fall back to filesystem search if semantic fails
        logger.info(f"Semantic search failed, falling back to filesystem search")

    # Filesystem search (Phase 1 behavior)
    return _search_domain_documents_filesystem(domain_name, domain_config)


def _search_domain_documents_filesystem(
    domain_name: str,
    domain_config: Dict[str, Any]
) -> Optional[List[Dict[str, Any]]]:
    """
    Search domain for documents using filesystem order (Phase 1).

    This is the original implementation - loads first N documents.

    Args:
        domain_name: Domain name
        domain_config: Domain configuration dict

    Returns:
        List of document dicts or None
    """
    import glob
    from pathlib import Path

    logger.info(f"Searching documents for {domain_name}")

    # Get base path
    base_path = domain_config.get("library_base_path")
    if not base_path:
        # Fall back to plugin config (backward compatibility)
        plugins = domain_config.get("plugins", [])
        for plugin in plugins:
            config = plugin.get("config", {})
            research_strategy = config.get("research_strategy")
            if research_strategy and research_strategy.get("type") == "document":
                base_path = research_strategy.get("base_path", "/app/project")
                break

    if not base_path:
        logger.info(f"No library_base_path configured for {domain_name}")
        return None

    logger.info(f"Searching documents in {base_path}")

    try:
        base_dir = Path(base_path)
        if not base_dir.exists():
            logger.warning(f"Document base path does not exist: {base_path}")
            return None

        # Load ignore patterns from ignored.md if it exists
        ignore_patterns = []
        ignored_file = base_dir / "ignored.md"
        if ignored_file.exists():
            try:
                with open(ignored_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            ignore_patterns.append(line)
                logger.info(f"Loaded {len(ignore_patterns)} ignore patterns from ignored.md")
            except Exception as e:
                logger.warning(f"Could not read ignored.md: {e}")

        # Find all markdown files recursively
        all_files = glob.glob(str(base_dir / "**/*.md"), recursive=True)

        # Filter out ignored patterns
        filtered_files = []
        for file_path in all_files:
            rel_path = str(Path(file_path).relative_to(base_dir))

            # Skip ignored.md itself
            if rel_path == "ignored.md":
                continue

            # Check against ignore patterns
            excluded = False
            for pattern in ignore_patterns:
                if pattern in rel_path:
                    excluded = True
                    logger.debug(f"Excluding {rel_path} (matches pattern: {pattern})")
                    break

            if not excluded:
                filtered_files.append(file_path)

        if not filtered_files:
            logger.info("No documents found")
            return None

        logger.info(f"Found {len(filtered_files)} documents (after filtering)")

        # Load documents with configurable limits
        max_docs = domain_config.get("max_library_documents", 50)  # Default 50 docs
        max_chars_per_doc = domain_config.get("max_chars_per_document", 50000)  # Default 50k chars

        documents = []
        for file_path in filtered_files[:max_docs]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Only truncate if content exceeds limit
                    if len(content) > max_chars_per_doc:
                        content = content[:max_chars_per_doc]
                        logger.debug(f"Truncated {file_path} to {max_chars_per_doc} chars")

                    documents.append({
                        "path": file_path,
                        "content": content,
                        "name": Path(file_path).name
                    })
            except Exception as e:
                logger.debug(f"Could not read {file_path}: {e}")
                continue

        if documents:
            logger.info(f"Loaded {len(documents)} documents for library search")
            return documents

    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return None

    logger.info(f"No documents found")
    return None

def _search_domain_documents_semantic(
    domain_name: str,
    domain_config: Dict[str, Any],
    query: str
) -> Optional[List[Dict[str, Any]]]:
    """
    Search domain for documents using semantic similarity (Phase 2).

    Uses DocumentVectorStore to rank documents by relevance to query.
    Only loads the most relevant documents.

    Args:
        domain_name: Domain name
        domain_config: Domain configuration dict
        query: Search query for semantic ranking

    Returns:
        List of document dicts ordered by relevance, or None
    """
    import glob
    from pathlib import Path
    from .document_embeddings import get_document_store

    logger.info(f"[SEMANTIC] Searching documents for {domain_name}")

    # Get base path
    base_path = domain_config.get("library_base_path")
    if not base_path:
        logger.info(f"No library_base_path configured for {domain_name}")
        return None

    logger.info(f"[SEMANTIC] Library path: {base_path}")

    try:
        base_dir = Path(base_path)
        if not base_dir.exists():
            logger.warning(f"Document base path does not exist: {base_path}")
            return None

        # Get document search config
        doc_search_config = domain_config.get("document_search", {})
        max_docs = doc_search_config.get("max_documents", 10)  # Semantic: default 10 (not 50)
        min_similarity = doc_search_config.get("min_similarity", 0.3)
        max_chars_per_doc = domain_config.get("max_chars_per_document", 50000)
        auto_generate = doc_search_config.get("auto_generate_embeddings", True)

        # Load ignore patterns from ignored.md
        ignore_patterns = []
        ignored_file = base_dir / "ignored.md"
        if ignored_file.exists():
            try:
                with open(ignored_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            ignore_patterns.append(line)
                logger.info(f"[SEMANTIC] Loaded {len(ignore_patterns)} ignore patterns")
            except Exception as e:
                logger.warning(f"Could not read ignored.md: {e}")

        # Find all markdown files
        all_files = glob.glob(str(base_dir / "**/*.md"), recursive=True)

        # Filter out ignored patterns
        filtered_files = []
        for file_path in all_files:
            rel_path = str(Path(file_path).relative_to(base_dir))

            # Skip ignored.md itself
            if rel_path == "ignored.md":
                continue

            # Check against ignore patterns
            excluded = False
            for pattern in ignore_patterns:
                if pattern in rel_path:
                    excluded = True
                    logger.debug(f"[SEMANTIC] Excluding {rel_path} (matches pattern: {pattern})")
                    break

            if not excluded:
                filtered_files.append(file_path)

        if not filtered_files:
            logger.info("[SEMANTIC] No documents found")
            return None

        logger.info(f"[SEMANTIC] Found {len(filtered_files)} documents (after filtering)")

        # Get or create document store
        # Store in domain directory (same place as pattern embeddings)
        domain_path = _get_domain_path(domain_name)
        if not domain_path:
            logger.warning(f"[SEMANTIC] Could not find domain path for {domain_name}")
            return None

        doc_store = get_document_store(domain_name, domain_path)
        if not doc_store:
            logger.warning(f"[SEMANTIC] Document store not available (sentence-transformers not installed)")
            return None

        # Load existing embeddings
        doc_store.load()

        # Generate embeddings if needed
        if auto_generate:
            doc_store.generate_embeddings(filtered_files, force=False)

            # Clean up embeddings for documents that no longer exist
            doc_store.remove_missing_documents(filtered_files)

        # Search for relevant documents
        results = doc_store.search(
            query=query,
            top_k=max_docs,
            min_similarity=min_similarity
        )

        if not results:
            logger.info(f"[SEMANTIC] No relevant documents found above {min_similarity} similarity")
            return None

        logger.info(f"[SEMANTIC] Found {len(results)} relevant documents")

        # Load the relevant documents
        documents = []
        for doc_path, similarity in results:
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Truncate if needed
                    if len(content) > max_chars_per_doc:
                        content = content[:max_chars_per_doc]
                        logger.debug(f"[SEMANTIC] Truncated {Path(doc_path).name} to {max_chars_per_doc} chars")

                    documents.append({
                        "path": doc_path,
                        "content": content,
                        "name": Path(doc_path).name,
                        "similarity_score": similarity
                    })

                    logger.info(f"[SEMANTIC]   {Path(doc_path).name}: {similarity:.3f}")

            except Exception as e:
                logger.error(f"[SEMANTIC] Could not read {doc_path}: {e}")
                continue

        if documents:
            logger.info(f"[SEMANTIC] Loaded {len(documents)} relevant documents")
            return documents

    except Exception as e:
        logger.error(f"[SEMANTIC] Error in semantic search: {e}")
        import traceback
        traceback.print_exc()
        return None

    return None


def _get_domain_path(domain_name: str) -> Optional[Path]:
    """
    Get path to domain directory.

    Args:
        domain_name: Domain name

    Returns:
        Path to domain directory or None
    """
    import os
    from pathlib import Path

    universes_base = os.getenv("UNIVERSES_BASE", "/app/universes")
    domain_path = Path(universes_base) / "MINE" / "domains" / domain_name

    if domain_path.exists():
        return domain_path

    # Try alternate path
    domain_path = Path(f"universes/MINE/domains/{domain_name}")
    if domain_path.exists():
        return domain_path

    return None
