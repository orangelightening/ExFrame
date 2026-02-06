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
Citation Checker Enricher - Validates responses contain required citations.

This enricher checks if responses that reference external sources (internet,
library, documents) contain at least one citation. If no citations are found,
the response is replaced with a message indicating insufficient information.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from core.enrichment_plugin import EnrichmentPlugin

logger = logging.getLogger(__name__)


class CitationCheckerEnricher(EnrichmentPlugin):
    """
    Validates that responses contain required citations.

    For domains that reference external sources (Type 3: Document Store,
    Type 4: Analytical Engine), this checker ensures the AI response
    includes at least one citation. If no citations are found, the response
    is replaced with a fallback message.

    Configuration:
        - require_for_types: List of domain types that require citations (default: ["3", "4"])
        - fallback_message: Message to show when no citations found (default: "Insufficient information to provide a response")
        - min_citations: Minimum number of citations required (default: 1)
    """

    name: str = "CitationCheckerEnricher"

    # Citation patterns to detect
    CITATION_PATTERNS = [
        # [filename]: or [source: filename]:
        r'\[\s*(?:source:\s*)?[^\]]+\s*\]:',
        # According to [filename]:
        r'According\s+to\s+\[[^\]]+\]:',
        # URLs in parentheses or as bare links
        r'https?://[^\s\)]+',
        # Source: URL or "Source:" header
        r'Source:\s*https?://[^\s]+',
        r'Source:\s*\[[^\]]+\]',
        # (Source: filename) style
        r'\(\s*Source:\s*[^\)]+\)',
        # Numbered citation style [1], [2] with a source list
        r'\[\d+\]',
        # @filename or @source style
        r'@[\w\d_-]+',
    ]

    def __init__(self, config: Dict[str, Any]):
        """Initialize citation checker.

        Args:
            config: Configuration dictionary with:
                - require_for_types: Domain types requiring citations (default: ["3", "4"])
                - fallback_message: Message when no citations (default: "Insufficient information to provide a response")
                - min_citations: Minimum citations required (default: 1)
        """
        self.config = config
        self.require_for_types = set(config.get("require_for_types", ["3", "4"]))
        self.fallback_message = config.get("fallback_message", "Insufficient information to provide a response")
        self.min_citations = config.get("min_citations", 1)

        logger.info(
            f"[CitationChecker] Initialized: "
            f"require_for_types={self.require_for_types}, "
            f"min_citations={self.min_citations}"
        )

    async def enrich(self, response_data: Dict, context: Optional[Dict] = None) -> Dict:
        """
        Check response for required citations.

        Args:
            response_data: Response data from previous enrichers
            context: Optional context with domain_type

        Returns:
            Modified response_data with citation check applied
        """
        # Get domain type from context
        domain_type = None
        if context:
            if hasattr(context, 'domain_type'):
                domain_type = context.domain_type
            elif isinstance(context, dict):
                domain_type = context.get('domain_type')

        # Skip check if domain type doesn't require citations
        if domain_type not in self.require_for_types:
            logger.debug(f"[CitationChecker] Domain type {domain_type} not in require_for_types, skipping")
            return response_data

        # Get the response text to check
        # Check multiple possible response keys
        response_text = None
        for key in ['llm_enhancement', 'llm_response', 'llm_fallback', 'response']:
            if key in response_data and response_data[key]:
                response_text = response_data[key]
                logger.debug(f"[CitationChecker] Checking response from key: {key}")
                break

        if not response_text:
            logger.debug("[CitationChecker] No response text found to check")
            return response_data

        # Count citations
        citation_count = self._count_citations(response_text)

        logger.info(
            f"[CitationChecker] Found {citation_count} citation(s) in response "
            f"(domain_type={domain_type}, required={self.min_citations})"
        )

        # If insufficient citations, replace response
        if citation_count < self.min_citations:
            logger.warning(
                f"[CitationChecker] Insufficient citations: {citation_count} < {self.min_citations}. "
                f"Replacing with fallback message."
            )

            # Replace the response key we found
            for key in ['llm_enhancement', 'llm_response', 'llm_fallback', 'response']:
                if key in response_data and response_data[key] == response_text:
                    response_data[key] = self.fallback_message
                    # Mark that citation check failed
                    response_data['_citation_check_failed'] = True
                    response_data['_citation_count'] = citation_count
                    break

            # Also update the top-level response if it exists
            if 'response' in response_data:
                response_data['response'] = self.fallback_message

        return response_data

    def _count_citations(self, text: str) -> int:
        """
        Count citations in the response text.

        Args:
            text: Response text to scan

        Returns:
            Number of unique citations found
        """
        if not text:
            return 0

        # Find all matches using all patterns
        all_matches = []
        for pattern in self.CITATION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            all_matches.extend(matches)

        # Deduplicate to avoid counting the same citation multiple times
        unique_citations = len(set(all_matches))

        # Also check for explicit source list markers
        # Like "Sources:" section headers
        if re.search(r'###*\s*Sources?:', text, re.IGNORECASE):
            unique_citations = max(unique_citations, 1)

        return unique_citations

    def requires_citation(self, response_data: Dict) -> bool:
        """
        Check if a response should have citations based on its content.

        This is a heuristic to determine if the response is making
        factual claims that should be cited.

        Args:
            response_data: Response data to check

        Returns:
            True if citations likely required, False otherwise
        """
        # Get response text
        response_text = response_data.get('llm_enhancement') or response_data.get('response') or ""

        if not response_text:
            return False

        # Indicators that citations might be needed:
        citation_indicators = [
            r'according\s+to',
            r'research\s+shows',
            r'studies?\s+(have\s+)?find',
            r'data\s+indicates?',
            r'reported\s+that',
            r'found\s+that',
            r'suggests?\s+that',
        ]

        for indicator in citation_indicators:
            if re.search(indicator, response_text, re.IGNORECASE):
                return True

        return False

    def get_citation_count(self, response_data: Dict) -> int:
        """
        Get the citation count for a response (for debugging/display).

        Args:
            response_data: Response data to check

        Returns:
            Number of citations found
        """
        response_text = response_data.get('llm_enhancement') or response_data.get('response') or ""
        return self._count_citations(response_text)
