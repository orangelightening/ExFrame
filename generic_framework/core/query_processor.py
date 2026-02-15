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
from .knowledge_cartography import get_kcart


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
    import time
    t_start = time.time()

    logger.info(f"Processing query for domain: {domain_name}")

    # Load domain config
    t0 = time.time()
    domain_config = _load_domain_config(domain_name)
    logger.info(f"⏱ Config load: {(time.time()-t0)*1000:.1f}ms")

    # Get persona
    persona_type = domain_config.get("persona", "librarian")
    persona = get_persona(persona_type)

    logger.info(f"Using persona: {persona_type}")

    # ==================== KNOWLEDGE CARTOGRAPHY (Query/Response History) ====================
    # Initialize KCart for this domain to track all query/response pairs
    # This enables dialectical knowledge mapping and conversational context
    from pathlib import Path as PathlibPath
    domain_path = PathlibPath("/app/universes/MINE/domains") / domain_name
    kcart = get_kcart(str(domain_path), domain_config)
    # ==================== END KCART INIT ====================

    # ==================== ROLE CONTEXT (Always loaded, never skipped) ====================
    # Role context defines how the AI behaves for this domain. It is stored in domain.json
    # and always injected as the LLM system message, independent of conversation memory mode.
    role_context = domain_config.get("role_context")
    if role_context:
        context = context or {}
        context["role_context"] = role_context
        logger.info(f"Loaded role_context from domain config ({len(role_context)} chars)")
    # ==================== END ROLE CONTEXT ====================

    # ==================== LLM CONFIG (Per-domain LLM override) ====================
    # Allows each domain to use a different LLM provider/model (e.g., local DMR for journal,
    # remote model for research). Falls back to global env vars if not set.
    # Supports dual-model routing: use fast local model for regular entries,
    # remote model (from .env) for ** searches to avoid GPU memory conflicts
    llm_config = domain_config.get("llm_config")
    if llm_config:
        context = context or {}
        # For ** search queries: use remote model (from .env) instead of local model
        # This avoids loading multiple models into GPU memory simultaneously
        if query.strip().startswith("**"):
            logger.info(f"⏱ ** query detected: using remote model from .env (not local model)")
            # Don't pass llm_config - will fall back to global .env settings
        else:
            # Regular query: use fast local model from domain config
            context["llm_config"] = llm_config
            logger.info(f"⏱ Using local model: {llm_config.get('model', 'default')}")
            logger.info(f"Loaded llm_config from domain config: model={llm_config.get('model', 'default')}, base_url={llm_config.get('base_url', 'default')}")
    # ==================== END LLM CONFIG ====================

    # ==================== CONVERSATION MEMORY (Load from domain_log.md) ====================
    # Conversation Memory: Load previous conversations from domain_log.md into LLM context
    # This gives the AI memory of past conversations without a separate file
    memory_content = None
    memory_config = domain_config.get("conversation_memory", {})

    if memory_config.get("enabled", False):
        mode = memory_config.get("mode", "all")
        max_chars = memory_config.get("max_context_chars", 5000)

        should_load_memory = False

        if mode == "all":
            # Load conversation history for all queries
            should_load_memory = True
            logger.info(f"Conversation memory mode 'all': loading context from domain_log.md")
        elif mode == "triggers":
            # Only load context on trigger phrases
            trigger_phrases = memory_config.get("trigger_phrases", [])
            if trigger_phrases and _check_memory_trigger(query, trigger_phrases):
                should_load_memory = True
                logger.info(f"Conversation memory mode 'triggers': triggered by query, loading context from domain_log.md")
        elif mode == "question":
            # Only load context when query starts with ** prefix
            if query.strip().startswith("**"):
                should_load_memory = True
                logger.info(f"Conversation memory mode 'question': ** prefix detected, loading context from domain_log.md")
            else:
                logger.info(f"Conversation memory mode 'question': no ** prefix, skipping memory")
        elif mode == "journal":
            # Never load conversation memory — fast path for simple journal entries
            logger.info(f"Conversation memory mode 'journal': skipping memory for fast entry")
        elif mode == "journal_patterns":
            if query.strip().startswith("**"):
                context = context or {}
                context["journal_pattern_search"] = True
                context["journal_query"] = query.strip()[2:].strip()
                logger.info("Conversation memory mode 'journal_patterns': ** prefix, will search patterns")
            else:
                logger.info("Conversation memory mode 'journal_patterns': regular entry, skipping memory")

        if should_load_memory:
            memory_content = _load_conversation_memory(domain_name, max_chars)

            if memory_content:
                # Prepend memory content to context
                context = context or {}
                context["memory_content"] = memory_content
                context["conversation_memory_used"] = True
                context["conversation_memory_mode"] = mode
                logger.info(f"Loaded {len(memory_content)} chars of conversation memory from domain_log.md")
    # ==================== END CONVERSATION MEMORY ====================

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
    t1 = time.time()
    patterns = None
    if should_search_patterns:
        patterns = _search_domain_patterns(domain_name, query)

        if patterns:
            logger.info(f"Found {len(patterns)} patterns for override")
        else:
            logger.info("No patterns found, using persona data source")
    else:
        logger.info("Pattern search disabled, using persona data source directly")
    logger.info(f"⏱ Pattern search: {(time.time()-t1)*1000:.1f}ms")

    # Journal pattern search: override patterns with semantic journal search
    if context and context.get("journal_pattern_search"):
        journal_query = context.get("journal_query", query)
        # Limit to 5 patterns for faster processing with qwen3
        journal_patterns = _search_journal_patterns(domain_name, journal_query, max_results=5)
        if journal_patterns:
            patterns = journal_patterns
            logger.info(f"Journal pattern search found {len(patterns)} relevant entries")

    # ==================== SIMPLE ECHO FOR POET (No AI needed) ====================
    # For poet persona: if query doesn't start with **, just add timestamp and echo
    # This eliminates the need for any AI/LLM for simple journal entries
    # Configurable via domain config: "use_simple_echo": true (default for poet)
    use_simple_echo = domain_config.get("use_simple_echo", persona_type == "poet")

    if use_simple_echo and persona_type == "poet" and not query.strip().startswith("**"):
        import os
        from datetime import datetime
        import zoneinfo

        # Use configured timezone (default: America/Vancouver)
        tz_name = os.getenv("APP_TIMEZONE", "America/Vancouver")
        try:
            tz = zoneinfo.ZoneInfo(tz_name)
            timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.warning(f"Invalid timezone '{tz_name}', falling back to UTC: {e}")
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        simple_response = f"[{timestamp}] {query}"

        logger.info(f"⏱ Simple echo (no AI): 0.0ms - instant response")

        response = {
            "answer": simple_response,
            "confidence": 1.0,
            "source": "simple_echo",
            "persona": persona_type,
            "patterns_used": [],
            "trace": []
        }

        # Log the journal entry
        t3 = time.time()
        logging_config = domain_config.get("logging", {"enabled": True})
        if logging_config.get("enabled", True):
            log_file = logging_config.get("output_file", "domain_log.md")
            format_type = logging_config.get("format", "markdown")
            log_entry = f"Query: {query}\n\n{simple_response}\n"

            success = _append_to_log(
                domain_name,
                log_file,
                query,
                log_entry,
                format_type,
                custom_entry=True
            )

            if success:
                response["logging_updated"] = True
                logger.info(f"Response appended to domain log: {log_file}")

        logger.info(f"⏱ Logging: {(time.time()-t3)*1000:.1f}ms")

        # Pattern autogeneration for journal entries
        auto_create_enabled = domain_config.get("auto_create_patterns", False)
        if memory_config.get("mode") == "journal_patterns":
            auto_create_enabled = True

        if auto_create_enabled:
            import asyncio
            asyncio.create_task(_create_journal_pattern_async(domain_name, query, simple_response))
            logger.info(f"Pattern autogeneration triggered for domain: {domain_name}")

        # Save to KCart (simple echo path)
        kcart.save_query_response(
            query=query,
            response=simple_response,
            metadata={
                "source": "simple_echo",
                "confidence": 1.0,
                "patterns_used": []
            }
        )

        total_time = (time.time() - t_start) * 1000
        response["query_time_ms"] = total_time
        logger.info(f"⏱ TOTAL QUERY TIME: {total_time:.1f}ms")

        return response
    # ==================== END SIMPLE ECHO ====================

    # ==================== KCART CONVERSATIONAL CONTEXT ====================
    # Load recent query/response pairs for conversational memory
    # This gives personas context of recent interactions (last 20 turns by default)
    t_kcart = time.time()
    kcart_context = kcart.load_recent_context()
    if kcart_context:
        context = context or {}
        context["kcart_history"] = kcart_context
        logger.info(f"Loaded {len(kcart_context)} messages from KCart for conversational context")
    logger.info(f"⏱ KCart context load: {(time.time()-t_kcart)*1000:.1f}ms")
    # ==================== END KCART CONTEXT ====================

    # THE DECISION: Override or not?
    # Prepare context with show_thinking flag
    context = context or {}
    context["show_thinking"] = show_thinking

    # If memory content exists, inject it into the prompt
    if memory_content:
        # Add staleness warning if there are web search results
        staleness_warning = ""
        if "[WEB_SEARCH" in memory_content:
            staleness_warning = "⚠️ IMPORTANT: Some previous responses include web search results with timestamps. "
            staleness_warning += "If a web search result is more than a few hours old, consider it STALE and search again. "
            staleness_warning += "Always prioritize current information over cached web search results.\n\n"

        # Add memory content as a prefix to the context
        context["memory_prefix"] = f"Previous conversation:\n\n{staleness_warning}{memory_content}\n\n---\n\n"
        logger.info("Injected conversation memory into prompt")

    t2 = time.time()
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
            t_doc = time.time()
            documents = _search_domain_documents(domain_name, domain_config, query)
            if documents:
                logger.info(f"Found {len(documents)} documents for library search")
                logger.info(f"⏱ Document search: {(time.time()-t_doc)*1000:.1f}ms")
                # Pass documents in context for persona to use
                context["library_documents"] = documents

        response = await persona.respond(query, context=context)
    logger.info(f"⏱ LLM call (persona.respond): {(time.time()-t2)*1000:.1f}ms")

    # ==================== LOGGING (Single Log File) ====================
    # Universal Logging: Always append query/response to domain_log.md
    # Web search results are logged WITH TIMESTAMP to indicate freshness

    t3 = time.time()
    logging_config = domain_config.get("logging", {"enabled": True})
    if logging_config.get("enabled", True):
        log_file = logging_config.get("output_file", "domain_log.md")
        format_type = logging_config.get("format", "markdown")

        response_source = response.get("source", "")
        answer = response.get("answer", "")

        # For web search, add timestamp to help AI know when data is stale
        if response_source == "internet":
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Add timestamp metadata to help identify stale results
            log_entry = f"[WEB_SEARCH - {timestamp}]\n\nQuery: {query}\n\n{answer}\n"
            logger.info(f"Web search response - logging with timestamp: {timestamp}")
        else:
            # Patterns, library, generation - log normally
            log_entry = f"Query: {query}\n\n{answer}\n"

        success = _append_to_log(
            domain_name,
            log_file,
            query,
            log_entry,  # Pass our formatted entry instead of just answer
            format_type,
            custom_entry=True  # Flag to indicate we're passing a pre-formatted entry
        )

        if success:
            response["logging_updated"] = True
            response["log_file"] = log_file
            logger.info(f"Response appended to domain log: {log_file}")
        else:
            response["logging_updated"] = False
            logger.warning("Failed to append response to domain log")
    logger.info(f"⏱ Logging: {(time.time()-t3)*1000:.1f}ms")
    # ==================== END LOGGING ====================

    # ==================== PATTERN AUTOGENERATION ====================
    # Auto-create patterns from queries if enabled (configurable per domain)
    # Excludes ** queries (those are for searching, not creating)
    auto_create_enabled = domain_config.get("auto_create_patterns", False)

    # Legacy support: journal_patterns mode also enables auto-creation
    if memory_config.get("mode") == "journal_patterns":
        auto_create_enabled = True

    if auto_create_enabled and not query.strip().startswith("**"):
        import asyncio
        answer_text = response.get("answer", "")
        asyncio.create_task(_create_journal_pattern_async(domain_name, query, answer_text))
        logger.info(f"Pattern autogeneration triggered for domain: {domain_name}")
    # ==================== END PATTERN AUTOGENERATION ====================

    # Add domain metadata
    response["domain"] = domain_name
    response["pattern_override_used"] = bool(patterns)
    response["persona_type"] = persona_type
    response["search_patterns_enabled"] = should_search_patterns

    # Add conversation memory metadata
    if memory_content is not None:
        response["conversation_memory_used"] = True

    # ==================== SAVE TO KCART ====================
    # Save query/response pair to compressed history for knowledge cartography
    kcart.save_query_response(
        query=query,
        response=response.get("answer", ""),
        metadata={
            "source": response.get("source", "unknown"),
            "confidence": response.get("confidence", 0.0),
            "patterns_used": response.get("patterns_used", []),
            "evoked_questions": response.get("evoked_questions", [])
        }
    )
    # ==================== END KCART SAVE ====================

    # Add timing metadata
    total_time = (time.time() - t_start) * 1000
    response["query_time_ms"] = total_time
    logger.info(f"⏱ TOTAL QUERY TIME: {total_time:.1f}ms")

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


# ==================== LOGGING FUNCTIONS ====================

def _append_to_log(domain_name: str, output_file: str, query: str, response: str, format_type: str = "markdown", custom_entry: bool = False) -> bool:
    """
    Append new query/response to domain log file (universal logging).

    Args:
        domain_name: Domain name
        output_file: Relative path to log file
        query: User query
        response: LLM response OR pre-formatted log entry
        format_type: Format type (markdown, plain, etc.)
        custom_entry: If True, response is a pre-formatted entry to write directly

    Returns:
        True if successful, False otherwise
    """
    from pathlib import Path
    from datetime import datetime

    domain_path = _get_domain_path(domain_name)
    if not domain_path:
        logger.warning(f"Cannot append to log: domain path not found for {domain_name}")
        return False

    log_path = domain_path / output_file

    # Create directory if it doesn't exist
    log_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Check if file exists to determine if we need a header
        file_exists = log_path.exists()

        with open(log_path, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if format_type == "markdown":
                if not file_exists:
                    f.write(f"# Domain Log\nCreated: {timestamp}\n\n")

                if custom_entry:
                    # Write pre-formatted entry directly (for web search with timestamp)
                    f.write(f"## {timestamp}\n\n")
                    f.write(f"{response}\n\n")
                    f.write("---\n\n")
                else:
                    # Standard format: Query: ... Response: ...
                    f.write(f"## {timestamp}\n\n")
                    f.write(f"**Query:** {query}\n\n")
                    f.write(f"{response}\n\n")
                    f.write("---\n\n")
            else:
                # Plain text format
                if not file_exists:
                    f.write(f"Domain Log - Created: {timestamp}\n\n")

                f.write(f"[{timestamp}]\n")
                f.write(f"Query: {query}\n")
                f.write(f"Response: {response}\n")
                f.write("\n" + "-"*80 + "\n\n")

        logger.info(f"Appended to domain log: {log_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to append to domain log: {e}")
        return False


# ==================== CONVERSATION MEMORY FUNCTIONS ====================

def _check_memory_trigger(query: str, trigger_phrases: List[str]) -> bool:
    """
    Check if query contains any memory trigger phrases.

    Args:
        query: User query string
        trigger_phrases: List of trigger phrases

    Returns:
        True if any trigger phrase found in query (case-insensitive)
    """
    query_lower = query.lower()
    return any(phrase.lower() in query_lower for phrase in trigger_phrases)


def _load_conversation_memory(domain_name: str, max_chars: int = 5000) -> Optional[str]:
    """
    Load conversation history from domain_log.md for memory.

    This reads the last N characters from the domain log file,
    giving the AI memory of past conversations.

    Args:
        domain_name: Domain name
        max_chars: Maximum characters to load (default: 5000)

    Returns:
        Conversation history string or None if file doesn't exist
    """
    from pathlib import Path

    domain_path = _get_domain_path(domain_name)
    if not domain_path:
        logger.warning(f"Cannot load conversation memory: domain path not found for {domain_name}")
        return None

    # Load from domain_log.md (same file used for universal logging)
    log_path = domain_path / "domain_log.md"

    if not log_path.exists():
        logger.info(f"domain_log.md not found: {log_path}")
        return None

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for web search entries and warn about staleness
        if "[WEB_SEARCH" in content:
            from datetime import datetime
            # Count web search entries
            web_search_count = content.count("[WEB_SEARCH")
            # Extract the most recent web search timestamp
            import re
            timestamps = re.findall(r'\[WEB_SEARCH - (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', content)
            if timestamps:
                latest_search = timestamps[-1]  # Most recent
                logger.warning(f"Conversation memory contains {web_search_count} web search results (latest: {latest_search})")
                logger.warning("Web search results may be stale - AI will be informed of retrieval times")

        # Take last N chars (most recent conversations)
        if len(content) > max_chars:
            content = content[-max_chars:]
            logger.info(f"Conversation memory truncated to {max_chars} chars (most recent)")

        logger.info(f"Loaded {len(content)} chars from domain_log.md for conversation memory")
        return content

    except Exception as e:
        logger.error(f"Failed to load conversation memory from domain_log.md: {e}")
        return None


# ==================== JOURNAL PATTERN FUNCTIONS ====================

def _create_journal_pattern(domain_name: str, query: str, response: str) -> None:
    """
    Auto-create a pattern from a journal entry.

    Creates a pattern with pattern_type "journal_entry" and generates
    an embedding for semantic search.

    Args:
        domain_name: Domain name
        query: The journal entry query
        response: The LLM response (timestamped echo)
    """
    import json
    from datetime import datetime

    domain_path = _get_domain_path(domain_name)
    if not domain_path:
        logger.warning(f"Cannot create journal pattern: domain path not found for {domain_name}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pattern_id = f"{domain_name}_{timestamp}"

    pattern = {
        "id": pattern_id,
        "name": query[:80],
        "pattern_type": "journal_entry",
        "problem": query,
        "solution": response,
        "created_at": datetime.now().isoformat(),
        "tags": ["journal"]
    }

    # Load existing patterns
    patterns_path = domain_path / "patterns.json"
    try:
        if patterns_path.exists():
            with open(patterns_path, 'r') as f:
                data = json.load(f)
        else:
            data = {"patterns": []}

        if isinstance(data, dict) and 'patterns' in data:
            data['patterns'].append(pattern)
        elif isinstance(data, list):
            data.append(pattern)
        else:
            data = {"patterns": [pattern]}

        with open(patterns_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Created journal pattern: {pattern_id}")

    except Exception as e:
        logger.error(f"Failed to create journal pattern: {e}")
        return

    # Generate embedding for the new pattern
    _generate_journal_embedding(domain_path, pattern_id, pattern)


def _generate_journal_embedding(domain_path: Path, pattern_id: str, pattern: dict) -> None:
    """
    Generate and store an embedding for a journal pattern.

    Args:
        domain_path: Path to domain directory
        pattern_id: Pattern ID
        pattern: Pattern dictionary
    """
    from .embeddings import get_embedding_service, VectorStore

    try:
        service = get_embedding_service()
        if not service or not service.is_available:
            logger.info("Embedding service not available, skipping journal embedding")
            return

        store = VectorStore(domain_path)
        store.load()

        embedding = service.encode_pattern(pattern)
        store.set(pattern_id, embedding)
        store.save()

        logger.info(f"Generated embedding for journal pattern: {pattern_id}")

    except Exception as e:
        logger.warning(f"Failed to generate journal embedding (non-fatal): {e}")


async def _create_journal_pattern_async(domain_name: str, query: str, response: str) -> None:
    """
    Async wrapper for _create_journal_pattern to run in background.

    This prevents blocking the response while generating embeddings.
    """
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _create_journal_pattern, domain_name, query, response)


def _search_journal_patterns(
    domain_name: str,
    query: str,
    max_results: int = 10,
    threshold: float = 0.1
) -> Optional[list]:
    """
    Search journal patterns using semantic similarity.

    Filters patterns to only journal_entry types, then uses
    embedding similarity to find the most relevant entries.

    Args:
        domain_name: Domain name
        query: Search query (with ** prefix already stripped)
        max_results: Maximum patterns to return
        threshold: Minimum similarity score (low to let LLM decide relevance)

    Returns:
        List of matching pattern dicts or None
    """
    import json
    from .embeddings import get_embedding_service, VectorStore

    domain_path = _get_domain_path(domain_name)
    if not domain_path:
        logger.warning(f"Cannot search journal patterns: domain path not found for {domain_name}")
        return None

    # Load patterns and filter to journal entries
    patterns_path = domain_path / "patterns.json"
    if not patterns_path.exists():
        logger.info(f"No patterns.json found for {domain_name}")
        return None

    try:
        with open(patterns_path, 'r') as f:
            data = json.load(f)

        if isinstance(data, dict) and 'patterns' in data:
            all_patterns = data['patterns']
        elif isinstance(data, list):
            all_patterns = data
        else:
            return None

        journal_patterns = [p for p in all_patterns if p.get("pattern_type") == "journal_entry"]

        if not journal_patterns:
            logger.info(f"No journal patterns found in {domain_name}")
            return None

        logger.info(f"Found {len(journal_patterns)} journal patterns, searching semantically")

        # Build pattern lookup by ID
        pattern_data = {p["id"]: p for p in journal_patterns}

        # Try semantic search with embeddings (should be pre-loaded at startup)
        service = get_embedding_service()
        if service and service.is_available and service.is_loaded:
            store = VectorStore(domain_path)
            store.load()

            all_embeddings = store.get_all()

            # Filter to only journal pattern embeddings
            journal_embeddings = {
                pid: emb for pid, emb in all_embeddings.items()
                if pid in pattern_data
            }

            if journal_embeddings:
                results = service.find_most_similar(
                    query=query,
                    pattern_embeddings=journal_embeddings,
                    pattern_data=pattern_data,
                    top_k=max_results,
                    threshold=threshold
                )

                if results:
                    matched = [pattern for pattern, score in results]
                    for pattern, score in results:
                        logger.info(f"  Journal match: {pattern.get('id')} (score: {score:.3f})")
                    return matched

                logger.info("Semantic search returned no results above threshold")
            else:
                logger.info("No embeddings found for journal patterns, falling back")
        else:
            logger.info("Embedding model not loaded, using recent patterns fallback")

        # Fallback: return most recent journal patterns
        logger.info(f"Returning {max_results} most recent journal patterns")
        return journal_patterns[-max_results:]

    except Exception as e:
        logger.error(f"Failed to search journal patterns: {e}")
        return None

