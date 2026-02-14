# ExFrame Model Selection Strategy

## Philosophy

**Match model capability to persona complexity**
- Simple tasks → Fast local models (llama3.2)
- Complex tasks → Larger capable models (glm-4.7+)

---

## Current Configuration

### 🎭 **Poet Persona** (Dual-Model)
- **Domain**: peter (journal)
- **Models**:
  - **Regular entries**: llama3.2 (3.2B, local via DMR) - ~231ms per query ⚡
  - **Search queries (** prefix)**: glm-4.7 (remote API via .env) - ~3-19s per query
- **Tasks**:
  - Regular: Timestamped echo of journal entries
  - Search: Answer questions by synthesizing from journal patterns
- **Rationale**: Single GPU model at a time (llama3.2) avoids memory conflicts. GLM for searches provides capability without GPU constraints.

**Examples**:
```
Regular Query: "buy milk"
Response: "[2026-02-14 12:25:06] buy milk"
Model: llama3.2 (local, fast)

Search Query: "** what do dogs love?"
Response: "According to your journal, dogs love beef."
Model: glm-4.7 (remote, capable)
```

**GPU Memory Strategy**: Only llama3.2 loads into GPU memory. GLM runs remotely, avoiding "out of memory" errors when both models would need to be in VRAM simultaneously.

---

### 📚 **Librarian Persona** (Complex)
- **Domain**: exframe, cooking, etc.
- **Model**: glm-4.7 (larger, via api.z.ai)
- **Performance**: ~3-19s per query 🐌
- **Tasks**:
  - Pattern synthesis
  - Document search
  - Knowledge retrieval
  - Complex Q&A
- **Rationale**: Requires sophisticated reasoning and context understanding

**Example**:
```
Query: "What is ExFrame?"
Response: [Detailed explanation synthesized from patterns and docs]
```

---

### 🔬 **Researcher Persona** (Complex)
- **Domains**: Research domains
- **Model**: glm-4.7 (larger, via api.z.ai)
- **Performance**: ~3-19s per query
- **Tasks**:
  - Multi-step research
  - Web search synthesis
  - Deep analysis
- **Rationale**: Research requires planning, context, and advanced reasoning

---

## Testing Results

### llama3.2 (3.2B) Testing

| Persona | Result | Performance | Notes |
|---------|--------|-------------|-------|
| Poet | ✅ **Perfect** | 231ms | Fast, accurate, reliable |
| Librarian | ❌ **Fails** | 300ms | Nonsense responses, unreliable |
| Researcher | ⚠️ **Not tested** | - | Likely too complex |

**Conclusion**: llama3.2 only suitable for simple, single-task personas

---

### glm-4.7 Testing

| Persona | Result | Performance | Notes |
|---------|--------|-------------|-------|
| Poet | ⚠️ **Weird** | 19s | Occasionally returns timestamped echoes (wrong context) |
| Librarian | ✅ **Works** | 3-19s | Capable, but slow |
| Researcher | ✅ **Expected to work** | 3-19s | Needs testing |

**Conclusion**: glm-4.7 works for complex personas but has occasional cross-contamination issues

---

## Known Issues

### 🐛 GLM Cross-Contamination
**Symptom**: glm-4.7 occasionally returns poet-style timestamped echoes when used by librarian

**Example**:
```
Domain: exframe (librarian)
Query: "Tuesday Weld is a great actress"
Expected: [Informative response about actress]
Actual: "[2026-02-14 12:25:06] Tuesday Weld is a great actress"
```

**Hypothesis**:
- API-level session state bleeding between domains
- Model has "learned" the pattern from repeated use
- Context contamination across conversations

**Investigation needed**: ⬜ TODO

---

## Optimization Opportunities

### Short Term
1. ✅ Use llama3.2 for simple poet role (done)
2. ✅ Dual-model routing for poet: llama3.2 for entries, qwen3 for ** searches (done)
3. ⬜ Investigate glm cross-contamination issue
4. ⬜ Test if larger local models (qwen3 8B) work for librarian

### Long Term
1. ⬜ Fine-tune llama3.2 specifically for poet role
2. ⬜ Deploy larger local model (7B-13B) for librarian/researcher
3. ⬜ Implement model router that auto-selects based on query complexity
4. ⬜ Add model warming to eliminate cold-start delays

---

## Model Selection Guidelines

### Use **Local llama3.2** when:
- ✅ Single, simple task (echo, format, simple extraction)
- ✅ Speed is critical (< 500ms required)
- ✅ No complex reasoning needed
- ✅ Deterministic behavior expected

### Use **Remote glm-4.7+** when:
- ✅ Complex reasoning required
- ✅ Multi-step processing
- ✅ Context understanding critical
- ✅ Synthesis from multiple sources
- ⚠️ Can tolerate 3-19s latency

---

## Performance Targets

| Persona | Model | Target | Current | Status |
|---------|-------|--------|---------|--------|
| Poet | llama3.2 | < 500ms | 231ms | ✅ |
| Librarian | glm-4.7 | < 5s | 3-19s | ⚠️ Variable |
| Researcher | glm-4.7 | < 10s | Not tested | ⬜ |

---

## Future Considerations

### Hybrid Approach
- Use fast local model for initial routing/classification
- Call remote model only when needed
- Combine results for best of both worlds

### Model Upgrade Path
1. **Current**: llama3.2 (3.2B) + glm-4.7 (remote)
2. **Next**: Add qwen3 (8B) local for mid-complexity tasks
3. **Future**: Deploy llama3 70B or similar for full local capability

---

## Testing Checklist

- [x] Poet with llama3.2
- [x] Librarian with llama3.2 (failed)
- [x] Librarian with glm-4.7 (works)
- [ ] Researcher with glm-4.7
- [ ] Investigate glm cross-contamination
- [ ] Test qwen3 (8B) for librarian role
- [ ] Benchmark end-to-end query performance

---

**Last Updated**: 2026-02-14
