# ExFrame User Guide

**Version**: 1.3.0
**Last Updated**: 2026-01-12

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Query Assistant](#query-assistant)
4. [Pattern Management](#pattern-management)
5. [Domain Management](#domain-management)
6. [Surveyor: Autonomous Learning](#surveyor-autonomous-learning)
7. [Universes](#universes)
8. [Diagnostics](#diagnostics)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

ExFrame is a domain-agnostic expertise assistant framework. It stores knowledge as **patterns** in **domains** within **universes**, and lets you query that knowledge through natural language.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Pattern** | A reusable knowledge unit (recipe, code pattern, technique) |
| **Domain** | Area of expertise (cooking, python, gardening, mathematical-concept, scientific-principle) |
| **Neighbourhood** | User-defined filter spanning multiple domains |
| **Universe** | Complete knowledge environment (production, testing) |
| **Query** | Natural language question answered using patterns |
| **Survey** | Autonomous learning session to collect patterns |

### The Hierarchy

```
MULTIVERSE
    └── UNIVERSE (e.g., "production")
        └── NEIGHBOURHOOD (filter: "quick recipes")
            └── DOMAIN (e.g., "cooking")
                └── PATTERNS (individual knowledge units)
```

---

## Getting Started

### Prerequisites

- Docker and Docker Compose (recommended) OR
- Python 3.10+ and pip

### Quick Start (Docker)

```bash
# Clone the repository
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame

# Start the services
docker-compose up -d

# Open the web interface
open http://localhost:3000
```

### Quick Start (Local)

```bash
# Navigate to the generic framework
cd generic_framework

# Install dependencies
pip install -r requirements.txt

# Start the API server
python -m api.app

# Open the web interface
open http://localhost:3000
```

---

## Query Assistant

The Query Assistant is your main interface for asking questions and getting answers from the knowledge base.

### How to Query

1. Click the **Query** tab in the navigation
2. Select your **domain** from the dropdown (e.g., "cooking", "python")
3. Type your question in natural language
4. Click **Submit** or press Enter

### Example Queries

**Cooking Domain:**
- "How do I cook chicken breast?"
- "My cake is too dense, what did I do wrong?"
- "Can I substitute oil for butter?"
- "I need a quick dinner tonight"

**Python Domain:**
- "How do I detect when an LLM is hallucinating?"
- "What are common failure modes in autonomous agents?"
- "How can I monitor for quality drift in LLM responses?"

### Understanding Query Results

Each query result shows:

| Field | Description |
|-------|-------------|
| **Response** | The answer generated from matched patterns |
| **Specialist** | Which AI specialist handled the query |
| **Confidence** | How confident the system is in the answer (0-100%) |
| **Patterns Used** | Which knowledge patterns were referenced |
| **Processing Time** | How long the query took (milliseconds) |

### Query Tips

- **Be specific**: "How long to bake chicken at 400°F?" is better than "How to cook chicken?"
- **Use context**: If you're following up, reference the previous answer
- **Check confidence**: Low confidence (<70%) means the system is unsure
- **Review patterns**: Click on pattern IDs to see source knowledge

---

## Pattern Management

View, search, and manage the knowledge patterns in your domains.

### Viewing Patterns

1. Click the **Patterns** tab
2. Select a **domain** from the dropdown
3. Browse all patterns or filter by category
4. Click a pattern ID to see full details

### Pattern Details

Each pattern contains:

| Field | Description |
|-------|-------------|
| **Name** | Brief title |
| **Type** | Pattern category (recipe, technique, code, etc.) |
| **Description** | What this pattern does |
| **Problem** | The problem this pattern solves |
| **Solution** | The solution or answer |
| **Tags** | Keywords for discovery |
| **Status** | Certified (✓) or Candidate (?) |
| **Confidence** | Quality score (0.0-1.0) |

### Searching Patterns

Use the **Sources** tab to:
- Search across all domains
- Filter by pattern type or status
- View recently accessed patterns
- See usage statistics

---

## Domain Management

Domains are areas of expertise that contain related patterns.

### Viewing Domains

1. Click the **Domains** tab
2. See all configured domains with statistics:
   - Pattern count
   - Specialist count
   - Categories
   - Load status

### Creating a Domain

1. Click **Create Domain** in the Domains tab
2. Fill in the form:
   - **Domain ID**: Unique identifier (e.g., "baking")
   - **Domain Name**: Display name (e.g., "Baking & Pastry")
   - **Description**: What this domain covers
   - **Categories**: Topic categories (e.g., "cookies", "cakes", "bread")
   - **Tags**: Discovery keywords
   - **Specialists**: AI specialists for this domain

3. Click **Create Domain**

### Editing a Domain

1. Find the domain in the list
2. Click the **Edit** (pencil) icon
3. Update the fields
4. Click **Save Changes**

### Domain Best Practices

- **Start narrow**: Create focused domains (e.g., "cookies" not "desserts")
- **Use categories**: Group patterns into logical sub-topics
- **Add specialists**: Configure specialists for different aspects
- **Document well**: Clear descriptions help with pattern discovery

---

## Surveyor: Autonomous Learning

The **Surveyor** is ExFrame's autonomous learning system. It can scrape web sources, extract knowledge patterns, and certify them through a 5-judge AI panel.

### Survey Levels

| Level | Icon | Description | When to Use |
|-------|------|-------------|-------------|
| **Domain** | 📁 | Survey a single domain | One specific area of expertise |
| **Neighbourhood** | 🔍 | Filter across multiple domains | Cross-cutting topics like "quick recipes" |
| **Universe** | 🌌 | Survey everything | Comprehensive knowledge gathering |

### Creating a Survey

1. Click the **Surveyor** tab
2. Click **+ New Survey**
3. **Basic Info**:
   - Name: "Quick Baking Recipes"
   - Description: "Collect baking recipes under 30 minutes"

4. **Select Scope**:
   - Choose Domain, Neighbourhood, or Universe
   - Read the explanation for each scope type
   - For Neighbourhood, define your filter criteria

5. **Scraping Control** ⚙️:
   - **Seed URL**: Where to start (e.g., `https://allrecipes.com/recipes/17215/cookies`)
   - **Additional URLs**: Extra sources (one per line)
   - **Collection Instructions**: Tell the AI what to look for:
     ```
     Focus on cookie baking techniques. Look for:
     - Temperature settings and their effects
     - Ingredient ratios and substitutions
     - Baking times and pan types
     - Common mistakes and troubleshooting
     ```

6. **Targets**:
   - Target Patterns: How many patterns to collect
   - Min Confidence: Minimum quality threshold (0.0-1.0)

7. Click **Create Survey**

### Understanding Neighbourhood Surveys

A **Neighbourhood** is a user-defined filter that searches across ALL domains:

| Your Definition | What It Does |
|-----------------|--------------|
| "baking under 30 minutes" | Finds quick baking recipes from cooking, baking, dessert domains |
| "ML model evaluation" | Finds evaluation patterns from python, data_science, ML domains |
| "authentication security" | Finds security patterns from webdev, backend, security domains |

**Key Difference**:
- **Domain**: "I want everything from X"
- **Neighbourhood**: "I want everything about Y, wherever it is"

### Controlling a Survey

From the Survey Detail panel:

| Control | Function |
|---------|----------|
| **▶ Start** | Begin autonomous learning |
| **⏸ Pause** | Pause the survey (resumable) |
| **■ Stop** | Stop the survey (requires confirmation) |
| **✏️ Edit** | Modify survey settings |

### Monitoring Progress

The **Real-time Metrics** panel shows:

| Metric | What It Means |
|--------|---------------|
| **Pulse** | Agent health (●●●●● = healthy) |
| **Progress** | Percentage complete |
| **Certified** | Patterns approved by judges |
| **Flagged** | Patterns needing human review |
| **Rejected** | Patterns that failed certification |
| **Judge Activity** | How busy each judge is (J1-J4 are AI, J5 is human) |

### Reading the Activity Log

The activity log shows real-time events:

```
22:19  Survey loaded
10:30  Started scraping: allrecipes.com
10:32  Certified pattern: Chocolate Chip Cookies
10:33  Flagged for review: Cake Temperature Guide
```

### Editing a Survey

1. Select the survey from the list
2. Click **✏️ Edit**
3. Update:
   - Name and description
   - Scraping URLs
   - Collection instructions
   - Targets and confidence
4. Click **Save Changes**

**Note**: You cannot change the survey level (Domain/Neighbourhood/Universe) after creation.

---

## Universes

Universes are complete, isolated knowledge environments.

### Viewing Universes

1. Click the **Universes** tab
2. See available universes with:
   - Domain count
   - Total patterns
   - Load status

### Universe Operations

| Operation | Description |
|-----------|-------------|
| **Load** | Activate a universe for queries |
| **Create** | Create a new universe |
| **Merge** | Combine two universes (admin only) |

### Default Universe

The **default** universe is loaded automatically on startup and contains all your configured domains.

---

## Diagnostics

Monitor system health, search quality, and pattern status.

### Health Dashboard

The **Diagnostics** tab shows:

1. **System Health**
   - Overall system status
   - Component health (API, domains, patterns)
   - Recent errors or warnings

2. **Search Metrics**
   - Search quality (confidence distribution)
   - Outcome distribution (success/failure/no results)
   - Recent traces

3. **Pattern Health**
   - Patterns by domain
   - Health scores
   - Issues detected

### Interpreting Health Scores

| Score Range | Status | Meaning |
|-------------|--------|---------|
| 90-100% | 🟢 Excellent | Healthy, no action needed |
| 70-89% | 🟡 Good | Minor issues, monitor |
| <70% | 🔴 Poor | Attention needed |

### Running Self-Tests

Click **Run Self-Test** to:
- Test search functionality
- Validate pattern access
- Check API connectivity
- Generate diagnostic report

---

## Advanced Features

### Pattern Formats

Patterns can be stored in different formats:

| Format | Extension | Description |
|--------|-----------|-------------|
| **JSON** | .json | Structured, machine-readable |
| **Markdown** | .md | Human-readable documentation |

### Enrichment Plugins

Enhance patterns with additional information:

| Plugin | Description |
|--------|-------------|
| **Related Patterns** | Link similar patterns together |
| **Example Expander** | Add usage examples |
| **Usage Stats** | Track pattern popularity |
| **Code Generator** | Generate code from patterns |

### Routers

Control how patterns are matched:

| Router | Description |
|--------|-------------|
| **Confidence** | Highest confidence first |
| **Multi-Specialist** | Multiple specialists collaborate |
| **Hierarchy** | Domain hierarchy aware |
| **Aggregator** | Combine multiple results |

---

## Troubleshooting

### Common Issues

#### Query Returns No Results

**Symptoms**: Query returns "No matching patterns found"

**Solutions**:
1. Check you selected the correct domain
2. Try rephrasing your question
3. Browse patterns manually to find relevant ones
4. Check diagnostics for domain health

#### Low Confidence Results

**Symptoms**: Query succeeds but confidence is <70%

**Solutions**:
1. Your question may be too broad
2. The domain may lack relevant patterns
3. Consider creating a survey to add more patterns
4. Check if another domain is more appropriate

#### Survey Not Progressing

**Symptoms**: Survey shows "Running" but progress stalls

**Solutions**:
1. Check Pulse metric (should be ●●●●●)
2. Check seed URL is accessible
3. Review scraping errors in activity log
4. Try pausing and resuming

#### Survey Status: Failed

**Symptoms**: Survey shows "Failed" status

**Solutions**:
1. Check error message in survey details
2. Verify seed URL and additional URLs
3. Check collection instructions are clear
4. Review system diagnostics

### Getting Help

1. **Check Logs**: Look at system logs for detailed errors
2. **Run Diagnostics**: Use the Diagnostics tab to check system health
3. **Review Documentation**: See `context.md` for architecture details
4. **Check GitHub**: https://github.com/orangelightening/ExFrame/issues

---

## Glossary

| Term | Definition |
|------|------------|
| **Pattern** | Reusable knowledge unit with problem/solution structure |
| **Domain** | Area of expertise containing related patterns |
| **Neighbourhood** | User-defined filter spanning multiple domains |
| **Universe** | Complete knowledge environment containing domains |
| **Specialist** | AI agent that handles queries in a domain |
| **Router** | Algorithm that selects patterns for queries |
| **Formatter** | Converts query results to different formats |
| **Enricher** | Adds additional information to patterns |
| **Survey** | Autonomous learning session to collect patterns |
| **Certification** | 5-judge AI panel that validates patterns |
| **Seed URL** | Starting point for web scraping |
| **Collection Instructions** | AI guidance on what patterns to extract |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + K` | Focus query input |
| `Ctrl/Cmd + Enter` | Submit query |
| `Escape` | Close modals |
| `Ctrl/Cmd + /` | Open this help |

---

## Best Practices

### For Users

1. **Start with specific questions** before broad exploration
2. **Check confidence scores** to gauge answer reliability
3. **Review source patterns** to understand answer origins
4. **Provide feedback** when answers are incorrect
5. **Use surveys** to expand knowledge in your areas of interest

### For Domain Creators

1. **Keep domains focused** on specific expertise areas
2. **Use clear, descriptive pattern names**
3. **Add comprehensive descriptions** to patterns
4. **Tag patterns generously** for better discovery
5. **Create surveys** to populate domains autonomously

### For Surveyors

1. **Start with Domain surveys** to build foundational knowledge
2. **Use Neighbourhood surveys** for cross-cutting topics
3. **Be specific** in collection instructions
4. **Provide quality seed URLs** to start scraping
5. **Monitor progress** and adjust settings as needed

---

**Document Version**: 1.0
**Last Updated**: 2026-01-12
**Maintained By**: ExFrame Development Team
