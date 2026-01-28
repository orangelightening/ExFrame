"""
Domain Factory - Generate domain configurations based on domain type.

This module provides the core functionality for the domain type system (Types 1-5).
When creating a domain via the UI, the factory generates appropriate plugins,
enrichers, and knowledge base configuration based on the selected type.

**Domain Types:**
1. Creative Generator - Poems, stories, creative content
2. Knowledge Retrieval - How-to guides, FAQs, technical documentation
3. Document Store Search - External documentation, API docs, live data
4. Analytical Engine - Research, analysis, correlation, reports
5. Hybrid Assistant - General purpose, flexible, user choice
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class DomainConfigGenerator:
    """Generate domain.json configuration based on domain type."""

    @staticmethod
    def generate(
        domain_id: str,
        domain_name: str,
        description: str,
        categories: List[str],
        tags: List[str],
        specialists: List[Dict[str, Any]],
        domain_type: str,
        # Type 1: Creative
        creative_keywords: Optional[str] = None,
        # Type 2: Knowledge
        similarity_threshold: Optional[float] = None,
        max_patterns: Optional[int] = None,
        # Type 3: Document Store
        document_store_type: Optional[str] = None,
        remote_url: Optional[str] = None,
        api_key: Optional[str] = None,
        show_sources: Optional[bool] = None,
        # Type 4: Analytical
        max_research_steps: Optional[int] = None,
        research_timeout: Optional[int] = None,
        report_format: Optional[str] = None,
        enable_web_search: Optional[bool] = None,
        # Type 5: Hybrid
        require_confirmation: Optional[bool] = None,
        research_on_fallback: Optional[bool] = None,
        # Common
        temperature: Optional[float] = None,
        llm_min_confidence: Optional[float] = None,
        # Original fields
        storage_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete domain configuration based on domain type.

        Returns a dictionary suitable for writing to domain.json.
        """

        # Base configuration common to all domains
        config = {
            "domain_id": domain_id,
            "domain_name": domain_name,
            "description": description,
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "categories": categories or [],
            "tags": tags or [],
            "domain_type": domain_type,
            "pattern_schema": {
                "required_fields": ["id", "name", "pattern_type", "problem", "solution"],
                "optional_fields": [
                    "description", "steps", "conditions", "related_patterns",
                    "prerequisites", "alternatives", "confidence", "sources",
                    "tags", "examples", "domain", "created_at", "updated_at",
                    "times_accessed", "user_rating", "origin", "origin_query",
                    "llm_generated", "status"
                ]
            }
        }

        # Generate configuration based on domain type
        if domain_type == "1":
            config.update(DomainConfigGenerator._type1_creative(
                creative_keywords, temperature
            ))
            # Store type-specific fields at top level for UI/reuse
            config["temperature"] = temperature or 0.8
            config["creative_keywords"] = creative_keywords or "poem, story, write, create, make, generate, compose"
        elif domain_type == "2":
            config.update(DomainConfigGenerator._type2_knowledge(
                similarity_threshold, max_patterns, temperature
            ))
            # Store type-specific fields at top level for UI/reuse
            config["temperature"] = temperature or 0.4
            config["similarity_threshold"] = similarity_threshold or 0.3
            config["max_patterns"] = max_patterns or 10
        elif domain_type == "3":
            config.update(DomainConfigGenerator._type3_document_store(
                document_store_type, remote_url, show_sources, temperature
            ))
            # Store type-specific fields at top level for UI/reuse
            config["temperature"] = temperature or 0.6
            config["document_store_type"] = document_store_type or "exframe_instance"
            config["remote_url"] = remote_url or ""
            config["show_sources"] = show_sources if show_sources is not None else True
        elif domain_type == "4":
            config.update(DomainConfigGenerator._type4_analytical(
                max_research_steps, research_timeout, report_format,
                enable_web_search, temperature
            ))
            # Store type-specific fields at top level for UI/reuse
            config["temperature"] = temperature or 0.5
            config["max_research_steps"] = max_research_steps or 10
            config["research_timeout"] = research_timeout or 300
            config["report_format"] = report_format or "structured"
            config["enable_web_search"] = enable_web_search if enable_web_search is not None else False
        elif domain_type == "5":
            config.update(DomainConfigGenerator._type5_hybrid(
                similarity_threshold, llm_min_confidence,
                require_confirmation, research_on_fallback, temperature
            ))
            # Store type-specific fields at top level for UI/reuse
            config["temperature"] = temperature or 0.5
            config["similarity_threshold"] = similarity_threshold or 0.3
            config["llm_min_confidence"] = llm_min_confidence or 0.3
            config["require_confirmation"] = require_confirmation if require_confirmation is not None else True
            config["research_on_fallback"] = research_on_fallback if research_on_fallback is not None else False
        else:
            # No type specified or unknown - use default configuration
            config.update(DomainConfigGenerator._default())
            config["temperature"] = temperature or 0.5

        # Add specialists (common to all types)
        if specialists:
            # Generate plugins from specialist configs
            config["plugins"] = []
            for spec in specialists:
                config["plugins"].append({
                    "plugin_id": spec.get("specialist_id", f"{domain_id}_specialist"),
                    "name": spec.get("name", domain_name),
                    "description": spec.get("description", f"Expert in {domain_name}"),
                    "module": "plugins.generalist",
                    "class": "GeneralistPlugin",
                    "enabled": True,
                    "config": {
                        "name": spec.get("name", domain_name),
                        "keywords": spec.get("expertise_keywords", []),
                        "categories": spec.get("expertise_categories", []),
                        "threshold": spec.get("confidence_threshold", 0.3)
                    }
                })

            # Add specialists list for backward compatibility
            config["specialists"] = [
                {
                    "specialist_id": s.get("specialist_id", f"{domain_id}_specialist"),
                    "name": s.get("name", domain_name),
                    "description": s.get("description", ""),
                    "expertise_keywords": s.get("expertise_keywords", []),
                    "expertise_categories": s.get("expertise_categories", []),
                    "confidence_threshold": s.get("confidence_threshold", 0.6)
                }
                for s in specialists
            ]

        return config

    @staticmethod
    def _type1_creative(
        creative_keywords: Optional[str],
        temperature: Optional[float]
    ) -> Dict[str, Any]:
        """Type 1: Creative Generator configuration."""
        keywords = creative_keywords or "poem, story, write, create, make, generate, compose"
        temp = temperature or 0.8

        return {
            "plugins": [
                {
                    "plugin_id": "creative",
                    "name": "Creative",
                    "module": "plugins.generalist",
                    "class": "GeneralistPlugin",
                    "enabled": True,
                    "config": {
                        "name": "Creative",
                        "keywords": keywords.split(", ") if isinstance(keywords, str) else keywords,
                        "threshold": 0.1
                    }
                }
            ],
            "enrichers": [
                {
                    "module": "plugins.enrichers.llm_enricher",
                    "class": "LLMEnricher",
                    "enabled": True,
                    "config": {
                        "mode": "enhance",
                        "temperature": temp,
                        "creative_mode": True,
                        "max_patterns": 5
                    }
                }
            ],
            "knowledge_base": {
                "type": "json",
                "storage_path": "patterns.json",
                "pattern_format": "embedded",
                "auto_save": True,
                "similarity_threshold": 0.2
            }
        }

    @staticmethod
    def _type2_knowledge(
        similarity_threshold: Optional[float],
        max_patterns: Optional[int],
        temperature: Optional[float]
    ) -> Dict[str, Any]:
        """Type 2: Knowledge Retrieval configuration."""
        sim_thresh = similarity_threshold or 0.3
        max_pats = max_patterns or 10
        temp = temperature or 0.4

        return {
            "plugins": [
                {
                    "plugin_id": "generalist",
                    "name": "Knowledge",
                    "module": "plugins.generalist",
                    "class": "GeneralistPlugin",
                    "enabled": True,
                    "config": {
                        "name": "Knowledge",
                        "keywords": ["how", "what", "explain", "guide"],
                        "threshold": 0.2
                    }
                }
            ],
            "enrichers": [
                {
                    "module": "plugins.enrichers.llm_enricher",
                    "class": "LLMEnricher",
                    "enabled": True,
                    "config": {
                        "mode": "enhance",
                        "temperature": temp,
                        "max_patterns": max_pats
                    }
                }
            ],
            "knowledge_base": {
                "type": "json",
                "storage_path": "patterns.json",
                "pattern_format": "embedded",
                "auto_save": True,
                "similarity_threshold": sim_thresh
            }
        }

    @staticmethod
    def _type3_document_store(
        document_store_type: Optional[str],
        remote_url: Optional[str],
        show_sources: Optional[bool],
        temperature: Optional[float]
    ) -> Dict[str, Any]:
        """Type 3: Document Store Search configuration."""
        doc_type = document_store_type or "exframe_instance"
        show_src = show_sources if show_sources is not None else True
        temp = temperature or 0.6

        return {
            "plugins": [
                {
                    "plugin_id": "exframe_specialist",
                    "module": "plugins.exframe.exframe_specialist",
                    "class": "ExFrameSpecialistPlugin",
                    "enabled": True,
                    "config": {
                        "document_store_enabled": True,
                        "local_patterns_enabled": True,
                        "document_store_config": {
                            "type": doc_type,
                            "remote_url": remote_url or ""
                        },
                        "research_strategy": {
                            "type": "document",
                            "documents": [
                                {"type": "file", "path": "README.md"}
                            ]
                        }
                    }
                }
            ],
            "enrichers": [
                {
                    "module": "plugins.enrichers.reply_formation",
                    "class": "ReplyFormationEnricher",
                    "enabled": True,
                    "config": {
                        "combine_strategy": "document_first",
                        "max_results": 10,
                        "show_sources": show_src,
                        "show_results": False  # Only show AI reply, not pattern hits
                    }
                },
                {
                    "module": "plugins.enrichers.llm_enricher",
                    "class": "LLMEnricher",
                    "enabled": True,
                    "config": {
                        "mode": "enhance",
                        "temperature": temp
                    }
                }
            ],
            "knowledge_base": {
                "type": "json",
                "storage_path": "patterns.json",
                "pattern_format": "embedded",
                "auto_save": True,
                "similarity_threshold": 0.3
            }
        }

    @staticmethod
    def _type4_analytical(
        max_research_steps: Optional[int],
        research_timeout: Optional[int],
        report_format: Optional[str],
        enable_web_search: Optional[bool],
        temperature: Optional[float]
    ) -> Dict[str, Any]:
        """Type 4: Analytical Engine configuration."""
        steps = max_research_steps or 10
        timeout = research_timeout or 300
        fmt = report_format or "structured"
        web_search = enable_web_search if enable_web_search is not None else False
        temp = temperature or 0.5

        return {
            "plugins": [
                {
                    "plugin_id": "researcher",
                    "module": "plugins.research.research_specialist",
                    "class": "ResearchSpecialistPlugin",
                    "enabled": True,
                    "config": {
                        "max_steps": steps,
                        "timeout": timeout,
                        "enable_web_search": web_search
                    }
                }
            ],
            "enrichers": [
                {
                    "module": "plugins.enrichers.llm_enricher",
                    "class": "LLMEnricher",
                    "enabled": True,
                    "config": {
                        "mode": "enhance",
                        "temperature": temp,
                        "max_tokens": 8192
                    }
                }
            ],
            "knowledge_base": {
                "type": "json",
                "storage_path": "patterns.json",
                "pattern_format": "embedded",
                "auto_save": True,
                "similarity_threshold": 0.3
            }
        }

    @staticmethod
    def _type5_hybrid(
        similarity_threshold: Optional[float],
        llm_min_confidence: Optional[float],
        require_confirmation: Optional[bool],
        research_on_fallback: Optional[bool],
        temperature: Optional[float]
    ) -> Dict[str, Any]:
        """Type 5: Hybrid Assistant configuration."""
        sim_thresh = similarity_threshold or 0.3
        llm_conf = llm_min_confidence or 0.3
        require_conf = require_confirmation if require_confirmation is not None else True
        research_fallback = research_on_fallback if research_on_fallback is not None else False
        temp = temperature or 0.5

        return {
            "plugins": [
                {
                    "plugin_id": "hybrid",
                    "name": "Hybrid",
                    "module": "plugins.generalist",
                    "class": "GeneralistPlugin",
                    "enabled": True,
                    "config": {
                        "name": "Hybrid",
                        "threshold": 0.2
                    }
                }
            ],
            "enrichers": [
                {
                    "module": "plugins.enrichers.llm_fallback_enricher",
                    "class": "LLMFallbackEnricher",
                    "enabled": True,
                    "config": {
                        "mode": "fallback",
                        "min_confidence": llm_conf,
                        "require_confirmation": require_conf
                    }
                }
            ],
            "knowledge_base": {
                "type": "json",
                "storage_path": "patterns.json",
                "pattern_format": "embedded",
                "auto_save": True,
                "similarity_threshold": sim_thresh
            }
        }

    @staticmethod
    def _default() -> Dict[str, Any]:
        """Default configuration when no type specified."""
        return {
            "plugins": [
                {
                    "plugin_id": "generalist",
                    "name": "General",
                    "module": "plugins.generalist",
                    "class": "GeneralistPlugin",
                    "enabled": True,
                    "config": {
                        "name": "General",
                        "keywords": [],
                        "categories": [],
                        "threshold": 0.3
                    }
                }
            ],
            "enrichers": [
                {
                    "module": "plugins.enrichers.llm_enricher",
                    "class": "LLMEnricher",
                    "enabled": True,
                    "config": {
                        "mode": "enhance",
                        "temperature": 0.5
                    }
                }
            ],
            "knowledge_base": {
                "type": "json",
                "storage_path": "patterns.json",
                "pattern_format": "embedded",
                "auto_save": True,
                "similarity_threshold": 0.5
            }
        }
