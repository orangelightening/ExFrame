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
Research Strategies Module

Provides pluggable research strategies for gathering context information
when patterns are not found or additional research is needed.

Usage:
    from core.research import create_research_strategy

    strategy = create_research_strategy({
        'type': 'document',
        'documents': [
            {'type': 'file', 'path': 'docs/context.md'}
        ]
    })

    results = await strategy.search("What is EEFrame?")
"""

from .base import ResearchStrategy, SearchResult
from .document_strategy import DocumentResearchStrategy, VectorDocumentResearchStrategy
from .internet_strategy import InternetResearchStrategy, BraveSearchInternetStrategy, GoogleSearchInternetStrategy


# Strategy registry
STRATEGY_TYPES = {
    'document': DocumentResearchStrategy,
    'vector_document': VectorDocumentResearchStrategy,
    'internet': InternetResearchStrategy,
    'brave': BraveSearchInternetStrategy,
    'google': GoogleSearchInternetStrategy,
}


def create_research_strategy(config: dict) -> ResearchStrategy:
    """
    Factory function to create a research strategy from configuration.

    Args:
        config: Configuration dictionary with 'type' field

    Returns:
        Instantiated research strategy

    Example:
        >>> strategy = create_research_strategy({
        ...     'type': 'document',
        ...     'documents': [{'type': 'file', 'path': 'context.md'}]
        ... })
    """
    strategy_type = config.get('type', 'document')

    if strategy_type not in STRATEGY_TYPES:
        raise ValueError(f"Unknown research strategy type: {strategy_type}. "
                        f"Available types: {list(STRATEGY_TYPES.keys())}")

    strategy_class = STRATEGY_TYPES[strategy_type]
    return strategy_class(config)


__all__ = [
    'ResearchStrategy',
    'SearchResult',
    'DocumentResearchStrategy',
    'VectorDocumentResearchStrategy',
    'InternetResearchStrategy',
    'BraveSearchInternetStrategy',
    'GoogleSearchInternetStrategy',
    'create_research_strategy',
]
