# Poetry Domain Cross-Reference Phenomenon

**Date**: 2026-01-19
**Status**: Observed but not fully explained

## Observation

When querying the `poetry_domain` (newly created domain for poetry and literary arts), the AI expert appears to be:

1. **Reading through the entire pattern store** - not just poetry patterns
2. **Cross-referencing content across domains** - finding poems and references in unrelated patterns
3. **Synthesizing connections** - creating outputs that reference patterns from cooking, diy, and other domains

## Example Behaviors Observed

- Queries about "poetry forms" return results that reference cooking metaphors found in cooking patterns
- The AI appears to have "read" patterns from other domains and is making literary connections
- Responses include "As mentioned in the chicken recipe pattern..." type cross-references

## Possible Explanations

### 1. LLM Context Window Effect
The LLM enricher may be receiving pattern content in its context window and making associations across all loaded patterns, not just the current domain's patterns.

### 2. Cross-Domain Pattern Matching
The search algorithm (`json_kb.py`) searches across all pattern fields including `solution`, which may contain literary references or metaphorical language that the AI interprets as poetry-relevant.

### 3. Specialist Behavior
The poetry generalist specialist may have a personality/behavior that encourages making connections and finding metaphors across different knowledge areas.

### 4. Enricher Configuration
The LLM fallback enricher might be configured with a high temperature (0.8 for poetry) which encourages more creative, associative responses.

## Files Involved

- `universes/default/domains/poetry_domain/domain.json` - Poetry domain config with temperature 0.8
- `generic_framework/knowledge/json_kb.py` - Pattern search algorithm
- `generic_framework/plugins/enrichers/llm_enricher.py` - LLM fallback behavior

## Implications

This phenomenon could be:
- **Desirable**: Demonstrates the AI's ability to synthesize knowledge across domains
- **Undesirable**: Results in unexpected or confusing cross-domain references
- **Emergent**: Unintended behavior arising from the interaction of multiple systems

## Next Steps for Investigation

1. **Isolate the cause**: Determine if it's the search algorithm, enricher, or specialist
2. **Test with other domains**: See if similar cross-reference happens elsewhere
3. **Configuration tuning**: Adjust temperature, context windows, or search parameters
4. **User expectation**: Decide if this behavior should be encouraged or prevented

## Related Issues

- Pattern search ranking fixes (substring matching for origin_query)
- Index key consistency between save_pattern and load_patterns
- File permission issues with pattern.json writes
