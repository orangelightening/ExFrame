# Query History Viewer

View compressed query/response history stored by Knowledge Cartography.

## Quick Start

```bash
# View full history for a domain
python3 scripts/view_history.py peter

# View last 10 entries
python3 scripts/view_history.py peter --limit 10

# Show only statistics
python3 scripts/view_history.py peter --stats-only

# Filter by confidence
python3 scripts/view_history.py psycho --min-confidence 0.8

# Filter by source
python3 scripts/view_history.py psycho --source brave-search

# Get JSON output (for scripts/tools)
python3 scripts/view_history.py peter --json
```

## What It Shows

### Summary Statistics
- Total entries stored
- Date range (first to last)
- Average confidence score
- Entries using patterns
- Breakdown by source (simple_echo, pattern_match, brave-search, etc.)

### Entry Details
For each query/response pair:
- Timestamp
- Query text
- Response text (truncated if long)
- Source (where answer came from)
- Confidence score
- Patterns used (if any)
- Evoked questions (if any)

## Storage Location

History files: `universes/MINE/domains/{domain}/query_history.json.gz`

These are automatically created and updated by the system. They're compressed with gzip to save space (typically 70-80% size reduction).

## Examples

### View Your Journal History
```bash
python3 scripts/view_history.py peter
```

Shows all your journal entries with timestamps, exactly as stored.

### Check Research Queries
```bash
python3 scripts/view_history.py psycho --source brave-search
```

Shows only queries that used Brave Search for answers.

### Find High-Confidence Entries
```bash
python3 scripts/view_history.py cooking --min-confidence 0.9
```

Shows only entries where the system had high confidence in the answer.

### Quick Stats Check
```bash
python3 scripts/view_history.py peter --stats-only
```

Just shows summary statistics without listing entries.

## Options Reference

| Option | Description | Example |
|--------|-------------|---------|
| `--limit N` | Show only last N entries | `--limit 20` |
| `--min-confidence X` | Filter by confidence >= X | `--min-confidence 0.7` |
| `--source SOURCE` | Filter by source type | `--source pattern_match` |
| `--stats-only` | Show only summary stats | `--stats-only` |
| `--json` | Output as JSON | `--json` |
| `--brief` | Truncate long responses | `--brief` |
| `--help` | Show help message | `--help` |

## Source Types

Common source values you'll see:

- `simple_echo` - Journal entries (poet persona, no AI)
- `pattern_match` - Answer from matching patterns
- `brave-search` - Web search via Brave API
- `internet` - Web search (general)
- `library` - Answer from library documents
- `generation` - LLM-generated answer

## Use Cases

### Debugging
Check what the system actually stored vs what you expected:
```bash
python3 scripts/view_history.py mydomain --limit 5
```

### Quality Audit
Find low-confidence queries that might need better patterns:
```bash
python3 scripts/view_history.py mydomain --min-confidence 0.0 | grep "Confidence: 0\.[0-3]"
```

### Export for Analysis
Get JSON for external tools:
```bash
python3 scripts/view_history.py mydomain --json > history_export.json
```

### Monitor Pattern Usage
See which patterns are actually being used:
```bash
python3 scripts/view_history.py mydomain | grep "Patterns:"
```

## Tips

1. **Start with stats** - Use `--stats-only` to get overview before diving into entries
2. **Filter first** - Use `--source` or `--min-confidence` to narrow down large histories
3. **Pipe to less** - For long histories: `python3 scripts/view_history.py peter | less`
4. **Combine filters** - You can use multiple filters together
5. **Check file size** - See storage used: `ls -lh universes/MINE/domains/*/query_history.json.gz`

## Next Steps

This viewer is Phase 1.5 of Knowledge Cartography. Coming next:

- **Phase 2**: Advanced analytics (pattern effectiveness, trends, gaps)
- **Phase 3**: Evocation chain analysis
- **Phase 4**: Concept network extraction
- **Phase 5**: Learning path visualization
- **Phase 6**: Interactive knowledge graph explorer

See `kcart.md` for the complete roadmap.
