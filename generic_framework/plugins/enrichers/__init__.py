"""
Enrichment Plugins

Transform specialist responses before formatting.

Available enrichers:
- RelatedPatternEnricher: Add related patterns
- PatternLinkEnricher: Add bidirectional links
- CategoryOverviewEnricher: Add category distribution
- ExampleExpanderEnricher: Expand examples
- ExampleValidatorEnricher: Validate examples
- ExampleSorterEnricher: Sort examples
- CodeGeneratorEnricher: Generate code examples
- CodeSnippetEnricher: Extract code snippets
- UsageStatsEnricher: Add usage statistics
- TrendingEnricher: Add trending info
- FeedbackEnricher: Add user feedback
- QualityScoreEnricher: Calculate quality scores
- LLMEnricher: Use LLM to enhance responses
- LLMFallbackEnricher: LLM as fallback for low-confidence queries
- LLMSummarizerEnricher: Summarize multiple patterns
- LLMExplanationEnricher: Add LLM explanations to patterns
"""

from plugins.enrichers.related_pattern_enricher import (
    RelatedPatternEnricher,
    PatternLinkEnricher,
    CategoryOverviewEnricher
)
from plugins.enrichers.example_expander_enricher import (
    ExampleExpanderEnricher,
    ExampleValidatorEnricher,
    ExampleSorterEnricher
)
from plugins.enrichers.code_generator_enricher import (
    CodeGeneratorEnricher,
    CodeSnippetEnricher
)
from plugins.enrichers.usage_stats_enricher import (
    UsageStatsEnricher,
    TrendingEnricher,
    FeedbackEnricher,
    QualityScoreEnricher
)
from plugins.enrichers.llm_enricher import (
    LLMEnricher,
    LLMFallbackEnricher,
    LLMSummarizerEnricher,
    LLMExplanationEnricher
)

__all__ = [
    "RelatedPatternEnricher",
    "PatternLinkEnricher",
    "CategoryOverviewEnricher",
    "ExampleExpanderEnricher",
    "ExampleValidatorEnricher",
    "ExampleSorterEnricher",
    "CodeGeneratorEnricher",
    "CodeSnippetEnricher",
    "UsageStatsEnricher",
    "TrendingEnricher",
    "FeedbackEnricher",
    "QualityScoreEnricher",
    "LLMEnricher",
    "LLMFallbackEnricher",
    "LLMSummarizerEnricher",
    "LLMExplanationEnricher",
]
