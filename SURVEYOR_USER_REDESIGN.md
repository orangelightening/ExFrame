# Surveyor User Experience Redesign

**Current Problem**: The UI is overwhelming with too many options, confusing terminology, and complex workflows. Users don't understand "Neighbourhoods", "Source Types", "Collection Instructions" vs "Extraction Instructions", etc.

---

## Current User Flow (Too Complex)

```
1. Click "Surveyor" tab
2. Click "+ New Survey"
3. Fill out 15-field form:
   - Survey Name
   - Description
   - Level: Domain/Neighbourhood/Universe (3 choices)
   - Universe selection
   - If Neighbourhood: Define neighbourhood (text field)
   - If Domain: Select domain
   - Source Type: Web/Documents (2 choices)
   - If Web: Seed URL + Additional URLs + Collection Instructions
   - If Documents: Path + Document list + Chunk size + Overlap + Extraction Instructions
   - Target Patterns
   - Min Confidence
4. Click "Create Survey"
5. Select survey from list
6. Click "Start"
7. Watch progress
```

**User friction**: High cognitive load, multiple decisions, confusing terms.

---

## What Users Actually Want

### Primary Use Cases

1. **"I found a great cooking website. I want to collect 50 recipes from it as patterns."**
2. **"I have some Python documentation files. Extract patterns from them."**
3. **"Collect all cookie recipes from AllRecipes."**

That's it. Three simple use cases.

---

## Proposed Redesign: Simple & Direct

### Approach: Smart Defaults + Progressive Disclosure

**Principle**: Make the common case simple, advanced options hidden.

---

## New User Flow

### Step 1: One-Click Create (Smart Defaults)

```
┌─────────────────────────────────────────┐
│  Collect Patterns                       │
├─────────────────────────────────────────┤
│  Where from?                            │
│  ○ Web (URL)                            │
│  ○ Local documents                      │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ https://allrecipes.com/recipes/ │   │
│  │ or file path...                  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  How many patterns?                    │
│  [ 50 ]                                │
│                                         │
│  Which domain?                         │
│  [ cooking ▼]                          │
│                                         │
│  [ Start Collection → ]                │
│                                         │
│  ▼ Advanced options                    │
└─────────────────────────────────────────┘
```

**That's it.** 4 fields:
1. Where from? (Web or Docs)
2. URL or path
3. How many?
4. Which domain?

**Everything else has smart defaults**:
- Min confidence: 0.8 (standard)
- Rate limiting: 1 req/sec (polite)
- Chunk size: 1000 chars (sensible)
- Instructions: Auto-generated from domain

---

### Step 2: Advanced Options (Progressive Disclosure)

Only show these if user clicks "Advanced options":

```
┌─────────────────────────────────────────┐
│  Advanced Options                       │
├─────────────────────────────────────────┤
│  Quality Control                        │
│  Min confidence: [0.8] (0-1)            │
│  □ Enable 5-judge certification panel   │
│                                         │
│  Polite Scraping                        │
│  Rate limit: [1] req/sec               │
│  □ Stealth mode (rotate user agents)   │
│                                         │
│  Scope                                  │
│  ○ Single domain                       │
│  ○ Multiple domains (search all)       │
│                                         │
│  Instructions (optional)                │
│  ┌─────────────────────────────────┐   │
│  │ Focus on cookie baking...       │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Timeline                               │
│  Stop after: [24] hours                 │
└─────────────────────────────────────────┘
```

---

## Revised Fields Mapping

| Current Field | New Approach | Rationale |
|---------------|--------------|-----------|
| **Survey Name** | Auto-generate from URL/domain | User doesn't care, just wants it done |
| **Description** | Auto-generate | Not necessary for basic use |
| **Level (Domain/Neighbourhood/Universe)** | Hide under "Scope: Single vs Multiple domains" | Too technical, simplify to "one or many" |
| **Universe** | Default to "MINE", hide in advanced | Only have one universe currently |
| **Neighbourhood definition** | "Multiple domains" option with filter | Simpler term: "search all domains" |
| **Domain selection** | Keep, required | Essential |
| **Source Type (Web/Documents)** | Keep, first choice | Essential distinction |
| **Seed URL** | Keep, main input field | Primary use case |
| **Additional URLs** | Move to advanced | Power user feature |
| **Collection Instructions** | Auto-generate from domain | Simplify: "cooking" → "extract cooking patterns" |
| **Extraction Instructions** | Same as above | Duplicate field, remove |
| **Documents path** | Keep (for docs source) | Essential for document ingestion |
| **Documents list** | Keep | Essential |
| **Chunk size** | Default to 1000, hide in advanced | Technical detail |
| **Chunk overlap** | Default to 100, hide in advanced | Technical detail |
| **Target Patterns** | Keep, required | Essential |
| **Min Confidence** | Default to 0.8, optional in advanced | Good default |

---

## New Form Structure

### Basic View (Default)

```
╔══════════════════════════════════════════════════════════════╗
║  Collect Patterns from Web                                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Source URL                                                   ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │ https://www.allrecipes.com/recipes/17562/dinner/       │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║  ⓘ The scraper will start here and follow recipe links    ║
║                                                               ║
║  Target Domain                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │ cooking ▼                                               │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  How many patterns to collect?                              ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │ [ 100 ]                                                  │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │                        [ Start Collection → ]            │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ▼ Show more options                                          ║
╚══════════════════════════════════════════════════════════════╝
```

### Advanced View (Optional)

```
╔══════════════════════════════════════════════════════════════╗
║  Advanced Options                                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Additional URLs (one per line)                              ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │ https://www.foodnetwork.com/recipes/...                 │  ║
║  │ https://www.tasty.co/recipe/...                         │  ║
║  │                                                          │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  Quality Threshold                                           ║
║  Min confidence: [0.8] (0-1)                                ║
║  □ Enable 5-judge certification panel                       ║
║                                                               ║
║  Polite Scraping                                             ║
║  Requests per second: [1]                                   ║
║  □ Stealth mode (rotate user agents)                        ║
║                                                               ║
║  Collection Instructions (optional)                         ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │ Focus on cookie baking techniques, temperature          │  ║
║  │ settings, ingredient substitutions...                   │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  Time Limit                                                   ║
║  Stop after: [24] hours                                     ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Alternative: Template-Based Approach

Even simpler - use templates for common tasks:

```
╔══════════════════════════════════════════════════════════════╗
║  Collect Patterns                                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  What do you want to collect?                                ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │ 🍳 Recipe Collection                                    │  ║
║  │    Collect recipes from cooking websites               │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │ 🐍 Python Code Patterns                                 │  ║
║  │    Extract patterns from Python documentation          │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │ 🛠️ DIY & Home Improvement                               │  ║
║  │    Collect DIY patterns from how-to sites              │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │ 📄 Custom Collection                                    │  ║
║  │    From any URL or document                            │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
```

**When user selects "Recipe Collection"**:

```
╔══════════════════════════════════════════════════════════════╗
║  Recipe Collection                                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Starting URL                                                ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │ https://www.allrecipes.com/recipes/17562/dinner/       │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  How many recipes?                                          ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │ [ 100 ]                                                  │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  Save to domain: [ cooking ]                                ║
║                                                               ║
║  [ Start Collecting Recipes → ]                             ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Monitoring UI: Simplify

### Current: Too many panels, complex metrics

```
┌──────────────┬───────────────────┬─────────────┐
│ Survey List  │  Survey Detail    │ Metrics     │
│              │  - Progress       │ - Pulse     │
│ - Culinary   │  - Scope          │ - Judges    │
│ - Python     │  - Activity Log   │ - Errors    │
│ - DIY        │                   │ - Focus     │
└──────────────┴───────────────────┴─────────────┘
```

### Proposed: One clean view

```
╔══════════════════════════════════════════════════════════════╗
║  Collecting Recipes: AllRecipes Dinner Category               ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Progress: ████████░░░░░░░░░░ 47/100 recipes                   ║
║                                                               ║
║  Live Activity                                               ║
║  ✓ Scraped: Creamy Tuscan Chicken (2.3s)                    ║
║  ✓ Extracted 3 patterns from Tuscan Chicken (1.1s)          ║
║  ✓ Certified: "Cream Sauce Base" pattern (0.92 confidence)   ║
║  ✓ Certified: "Italian Seasoning Blend" pattern (0.87)      ║
║  ⚠ Flagged: "Pan Selection" (needs review)                  ║
║  ▶ Scraping: Lemon Herb Roasted Chicken...                  ║
║                                                               ║
║  Stats                                                        ║
║  ✓ Certified: 42 patterns                                    ║
║  ⚠ Flagged: 3 patterns (needs review)                        ║
║  ✗ Rejected: 2 patterns (low quality)                        ║
║                                                               ║
║  Elapsed: 00:23:45  |  ETA: 00:15:30  |  Rate: 2.3 recipes/min ║
║                                                               ║
║  [ Pause ]  [ Stop ]  [ View Patterns ]                       ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
```

**Simpler**:
- One panel instead of three
- Progress bar at top
- Live activity feed (not a static log)
- Key metrics (certified/flagged/rejected)
- ETA and rate

---

## Key Changes Summary

### 1. **Reduce Form Fields**: 15 → 4 (basic view)
### 2. **Smart Defaults**: Auto-generate name, description, instructions
### 3. **Progressive Disclosure**: Hide advanced options
### 4. **Better Terminology**:
   - "Neighbourhood" → "Search across domains"
   - "Source type" → "Where from?"
   - "Collection/Extraction instructions" → Just "Instructions"
### 5. **Template-Based**: Quick-start for common tasks
### 6. **Cleaner Monitoring**: One panel with live activity feed

---

## Implementation Priority

### Phase 1: Simplify Create Form (1 day)
1. Create new "simple" form with 4 fields
2. Auto-generate: name, description, instructions
3. Add "Advanced options" toggle
4. Test with basic use case

### Phase 2: Simplify Monitoring UI (1 day)
1. Combine three panels into one
2. Live activity feed (not static log)
3. Show key metrics at top
4. Add ETA and rate

### Phase 3: Add Templates (optional, 1 day)
1. Create template system
2. Pre-configure for: Recipes, Python, DIY
3. One-click collection

---

## Questions

1. **Keep the old complex form as "Advanced" mode?** Or remove entirely?

2. **Template approach appealing?** Or stick with simple form + advanced options?

3. **Should "domain" be selected first?** Or inferred from URL/docs?

4. **What about batch collection?** User provides 10 URLs, collect from all?

5. **Rename "Surveyor"?** Maybe "Collector" or "Pattern Collector"?

---

**Want me to implement the simplified form?** Or refine this design first?
