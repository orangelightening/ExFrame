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
LLM Prompts for Pattern Extraction

Specialized prompts for extracting different types of expertise patterns
from domain documentation using GLM-4.7.
"""

from enum import Enum


class PromptTemplate(str, Enum):
    """Prompt templates for different extraction tasks"""

    GENERAL_EXTRACTION = "general"
    QA_PATTERN = "qa"  # Extract from Q&A format
    PROCEDURE = "procedure"  # Extract from step-by-step instructions
    SUBSTITUTION = "substitution"  # Extract substitution rules
    TROUBLESHOOTING = "troubleshooting"  # Extract diagnostic patterns


# ============================================================================
# GENERAL PATTERN EXTRACTION
# ============================================================================

GENERAL_EXTRACTION_PROMPT = """You are an expertise extraction assistant. Your task is to
analyze text from the {domain} domain and extract practical patterns.

For each pattern you identify, provide:
1. **name**: A short descriptive title
2. **pattern_type**: One of: troubleshooting, procedure, substitution, decision, diagnostic, preparation, optimization, principle
3. **description**: One sentence explaining the value this provides
4. **problem**: What challenge does this help overcome?
5. **solution**: What makes this approach work well?
6. **steps**: Step-by-step procedure (if applicable)
7. **conditions**: If/then branches (if applicable)
8. **tags**: Relevant keywords

Output ONLY valid JSON. Use this exact structure:

[
  {{
    "name": "Pattern Name",
    "pattern_type": "troubleshooting",
    "description": "Brief description",
    "problem": "What challenge this helps overcome",
    "solution": "What makes this approach work",
    "steps": ["step 1", "step 2", "..."],
    "conditions": {{"if": "condition", "then": "action"}},
    "tags": ["tag1", "tag2"]
  }}
]

Text to analyze:
{text}
"""


# ============================================================================
# Q&A PATTERN EXTRACTION (Stack Overflow, forums, etc.)
# ============================================================================

QA_EXTRACTION_PROMPT = """You are analyzing a Q&A pair from {domain}. Extract the
practical pattern embedded in this exchange.

Focus on:
- The question being explored
- The solution that worked
- Key steps to follow
- Related insights mentioned

Output as JSON:

{{
  "name": "Pattern name based on the question",
  "pattern_type": "troubleshooting",
  "description": "One sentence summary",
  "problem": "The question being explored",
  "solution": "What worked to resolve it",
  "steps": ["key steps from the solution"],
  "tags": ["relevant", "tags"]
}}

**Question:**
{question}

**Answers:**
{answers}
"""


# ============================================================================
# PROCEDURE/RECIPE EXTRACTION
# ============================================================================

PROCEDURE_EXTRACTION_PROMPT = """You are analyzing a procedural guide from {domain}.
Extract the practical pattern from these steps.

Identify:
- What this procedure accomplishes
- The key steps (condense if too detailed)
- Any decision points or branches
- Prerequisites or preparation needed
- Potential variations

Output as JSON:

{{
  "name": "Procedure name",
  "pattern_type": "procedure",
  "description": "What this accomplishes",
  "problem": "What need this addresses",
  "solution": "Overview of the approach",
  "steps": ["condensed step 1", "condensed step 2", "..."],
  "prerequisites": ["thing needed 1", "thing needed 2"],
  "conditions": {{"if condition": "then action"}},
  "tags": ["relevant", "tags"]
}}

**Procedure:**
{procedure}
"""


# ============================================================================
# SUBSTITUTION RULE EXTRACTION
# ============================================================================

SUBSTITUTION_EXTRACTION_PROMPT = """You are looking for substitution patterns in {domain}.
These are rules about replacing X with Y.

Identify:
- What can be substituted
- What it can be replaced with
- The conversion ratio or rule
- Any limitations or caveats
- When this substitution works

Output as JSON:

{{
  "name": "Substitution: X → Y",
  "pattern_type": "substitution",
  "description": "Replace X with Y under these conditions",
  "problem": "When you need X but Y is available",
  "solution": "Use Y instead with this conversion",
  "steps": ["how to do the substitution"],
  "conditions": {{"works_when": "condition", "caveat": "limitation"}},
  "tags": ["substitution", "category"]
}}

**Text:**
{text}
"""


# ============================================================================
# TROUBLESHOOTING PATTERN EXTRACTION
# ============================================================================

TROUBLESHOOTING_PROMPT = """You are analyzing troubleshooting steps from {domain}.
Extract the diagnostic and repair pattern.

Identify:
- Symptoms or indicators
- Diagnostic steps (how to identify the cause)
- Solutions for each potential cause
- Progressive isolation approach
- Start with simple checks first

Output as JSON:

{{
  "name": "Troubleshooting: Problem Description",
  "pattern_type": "troubleshooting",
  "description": "How to diagnose and resolve this issue",
  "problem": "The symptoms being addressed",
  "solution": "General approach to resolution",
  "steps": [
    "Check simple thing first",
    "Then check this",
    "Finally try this"
  ],
  "conditions": {{"if symptom A": "check cause A", "if symptom B": "check cause B"}},
  "tags": ["troubleshooting", "category"]
}}

**Text:**
{text}
"""


# ============================================================================
# CROSS-DOMAIN PATTERN MATCHING
# ============================================================================

CROSS_DOMAIN_MATCH_PROMPT = """You are comparing two patterns from different domains
to find similarities in their problem-solving structure.

Analyze:
1. **Structural similarity**: Do both follow the same problem-solving approach?
2. **Abstract pattern**: What's the universal pattern beneath the surface?
3. **Domain differences**: How do the domains differ in specifics?

Output as JSON:

{{
  "similarity_score": 0.8,
  "shared_structure": [
    "Both use progressive isolation",
    "Both start with simple checks",
    "Both escalate to complex solutions"
  ],
  "universal_pattern": "Progressive isolation: eliminate possibilities systematically",
  "domain_variations": {{
    "{domain1}": "specific variation in domain 1",
    "{domain2}": "specific variation in domain 2"
  }}
}}

**Pattern from {domain1}:**
{pattern1}

**Pattern from {domain2}:**
{pattern2}
"""


# ============================================================================
# PATTERN ABSTRACTION
# ============================================================================

ABSTRACT_PATTERN_PROMPT = """You are analyzing multiple instances of a pattern across
different domains. Extract the universal, abstract pattern they all share.

Identify:
- What ALL instances have in common (core structure)
- What varies by domain (parameters)
- The abstract pattern name
- General description that applies to all domains

Output as JSON:

{{
  "abstract_name": "Universal Pattern Name",
  "description": "General description of this pattern",
  "common_elements": [
    "element 1 present in all",
    "element 2 present in all",
    "element 3 present in all"
  ],
  "parameters": {{
    "varies_by_domain": "what changes",
    "examples": {{
      "domain1": "specific example",
      "domain2": "specific example"
    }}
  }}
}}

**Pattern Instances:**
{patterns}
"""


# ============================================================================
# CONFIDENCE SCORING
# ============================================================================

CONFIDENCE_SCORING_PROMPT = """You are assessing the reliability and quality of an
extracted pattern from {domain}.

Rate this pattern on:
- **Clarity**: Is the pattern well-defined and actionable?
- **Generality**: Is this a reusable pattern or one-off solution?
- **Accuracy**: Does this seem correct for the domain?
- **Completeness**: Are all important steps included?

Output as JSON:

{{
  "confidence": 0.85,
  "clarity": 0.9,
  "generality": 0.8,
  "accuracy": 0.85,
  "completeness": 0.8,
  "issues": ["any concerns or limitations"],
  "suggestions": ["how to improve this pattern"]
}}

**Pattern:**
{pattern}
"""


def get_prompt(template: PromptTemplate, **kwargs) -> str:
    """Get a formatted prompt template"""

    templates = {
        PromptTemplate.GENERAL_EXTRACTION: GENERAL_EXTRACTION_PROMPT,
        PromptTemplate.QA_PATTERN: QA_EXTRACTION_PROMPT,
        PromptTemplate.PROCEDURE: PROCEDURE_EXTRACTION_PROMPT,
        PromptTemplate.SUBSTITUTION: SUBSTITUTION_EXTRACTION_PROMPT,
        PromptTemplate.TROUBLESHOOTING: TROUBLESHOOTING_PROMPT,
    }

    if template not in templates:
        raise ValueError(f"Unknown template: {template}")

    return templates[template].format(**kwargs)


if __name__ == "__main__":
    # Test prompts
    print("General extraction prompt:")
    print(get_prompt(PromptTemplate.GENERAL_EXTRACTION, domain="cooking", text="Some text here..."))

    print("\n\nQ&A prompt:")
    print(get_prompt(
        PromptTemplate.QA_PATTERN,
        domain="python",
        question="How do I fix this error?",
        answers="You need to import the module first."
    ))
