# Assessment Domains Guide

**Status:** Ready for Testing
**Date:** February 16, 2026

---

## Overview

Three assessment domains created for BrainUse hiring intelligence:
1. **Cloud Infrastructure** - AWS/GCP basics → Scalability → Distributed systems
2. **Technical Leadership** - Team dynamics → Project management → Strategic thinking
3. **API Design** - REST basics → Design principles → Distributed APIs

All use **"Librarian" personas** - progressive learning guides that adapt to learner sophistication.

---

## Librarian Persona Pattern

### Philosophy
**You don't test learners - you assess through observation.**

Librarians:
- Guide exploration progressively (Level 1 → 4)
- Match response depth to question sophistication
- Encourage natural curiosity-driven learning
- Never quiz or grade

### Sophistication Levels

| Level | Range | Focus | Example Questions |
|-------|-------|-------|-------------------|
| **1: Fundamentals** | 0-1.5 | Definitions, mechanics | "What is EC2?" |
| **2: Practical** | 1.5-2.5 | Patterns, trade-offs | "When to use RDS vs DynamoDB?" |
| **3: Advanced** | 2.5-3.5 | System design, scaling | "How to design for 99.99% uptime?" |
| **4: Expert** | 3.5-4.0 | Architecture, constraints | "CAP theorem implications?" |

---

## Domain: Cloud Infrastructure

**Domain ID:** `cloud_assessment`
**Persona:** `cloud_librarian`

### Learning Path
1. **Fundamentals** - EC2, S3, VPC, basic services
2. **Practical** - Load balancing, auto-scaling, databases, IAM
3. **Advanced** - Multi-region, distributed systems, consistency, observability
4. **Expert** - Global scale, CAP theorem, network partitions, optimization

### Example Progression
```
Session 1 (Beginner):
  "What is S3?" → Definition
  "How do I store files?" → S3 upload basics

Session 3 (Intermediate):
  "When should I use S3 vs EBS?" → Trade-offs
  "How do I design HA architecture?" → Multi-AZ patterns

Session 6 (Advanced):
  "How to handle eventual consistency?" → Distributed systems
  "Multi-region vs multi-AZ trade-offs?" → Reliability design

Session 9 (Expert):
  "CAP theorem for S3's consistency model?" → Deep architecture
  "How does AWS handle network partition?" → Failure modes
```

### Metrics This Tests
- **Learning velocity:** Beginner → Expert in 10 days
- **Chain depth:** Follow-up questions on same topic
- **Sophistication:** Question complexity evolution
- **Persistence:** Deep exploration vs shallow browsing

---

## Domain: Technical Leadership

**Domain ID:** `leadership_assessment`
**Persona:** `leadership_librarian`

### Learning Path
1. **Team Basics** - 1-on-1s, feedback, delegation
2. **Team Dynamics** - Motivation, conflict, stakeholders
3. **Strategic** - Culture, org design, scaling teams
4. **Executive** - Cross-functional, business alignment, change management

### Example Progression
```
Session 1 (Beginner):
  "How to run effective 1-on-1?" → Framework
  "How often to meet with team?" → Frequency advice

Session 4 (Intermediate):
  "How to resolve engineer conflict?" → Mediation
  "How to estimate timelines?" → Project management

Session 7 (Advanced):
  "How to build strong culture?" → Systems thinking
  "When to split teams?" → Org design

Session 10 (Expert):
  "How to align eng + business strategy?" → Executive perspective
  "How to drive change across 500 people?" → Organizational dynamics
```

### What This Measures
- **Empathy:** People-first thinking
- **Systems thinking:** Second-order effects
- **Maturity:** Tactical → Strategic progression
- **Self-awareness:** Reflection on leadership style

---

## Domain: API Design

**Domain ID:** `api_assessment`
**Persona:** `api_librarian`

### Learning Path
1. **HTTP Fundamentals** - Methods, status codes, REST basics
2. **Design Principles** - Versioning, pagination, error handling
3. **Distributed APIs** - Microservices, consistency, idempotency
4. **Architecture** - Backward compatibility, evolution, governance

### Example Progression
```
Session 1 (Beginner):
  "What's GET vs POST?" → HTTP basics
  "How to return errors?" → Status codes

Session 3 (Intermediate):
  "PUT vs PATCH?" → Semantic differences
  "How to version APIs?" → Versioning strategies

Session 6 (Advanced):
  "How to maintain consistency across services?" → Distributed systems
  "How to design idempotent APIs?" → Reliability patterns

Session 9 (Expert):
  "How to design for 10-year backward compat?" → API evolution
  "Trade-offs: REST vs GraphQL vs gRPC?" → Architectural decisions
```

### What This Measures
- **Precision:** Understanding of specifications
- **Design thinking:** Trade-offs and implications
- **Pragmatism:** Real-world constraints
- **Evolution thinking:** Long-term planning

---

## Synthesizing Test Data

### Quick Start

```bash
# Generate test candidate with average learning profile
python scripts/synthesize_test_candidate.py \
  --candidate-name "Alice Johnson" \
  --profile average

# Fast learner (high velocity)
python scripts/synthesize_test_candidate.py \
  --candidate-name "Bob Chen" \
  --profile fast

# Slow learner (low velocity)
python scripts/synthesize_test_candidate.py \
  --candidate-name "Charlie Davis" \
  --profile slow
```

### What Gets Generated

For each domain:
- **6-10 sessions** over 10 days
- **3-8 questions per session** (total 30-50 queries)
- **Progressive sophistication** (Level 1 → Level 3-4)
- **Realistic timestamps** (workday hours, spaced sessions)
- **Variation** (some backtracking, some jumps ahead)

### Learning Profiles

| Profile | Velocity | Expected Tao Index | Percentile | Outcome |
|---------|----------|-------------------|------------|---------|
| **Slow** | 0.20 levels/day | 4.5-6.0 | 30-50th | Pass/Maybe |
| **Average** | 0.35 levels/day | 6.5-7.5 | 60-75th | Maybe/Hire |
| **Fast** | 0.50 levels/day | 8.0-9.0 | 85-95th | Hire |

---

## Testing Workflow

### 1. Synthesize Test Candidate

```bash
python scripts/synthesize_test_candidate.py --candidate-name "Test Engineer"
```

Output:
```
Synthesizing candidate: Test Engineer
  Profile: average (velocity: 0.35 levels/day)
  Domains: cloud_assessment, leadership_assessment, api_assessment

  ✓ Saved 42 entries to domains/cloud_assessment/query_history.json.gz
  ✓ Saved 38 entries to domains/leadership_assessment/query_history.json.gz
  ✓ Saved 41 entries to domains/api_assessment/query_history.json.gz

✓ Candidate synthesized: Test Engineer
  Total queries: 121
  Assessment period: 10 days
```

### 2. Create Candidate in Dashboard

```bash
open http://localhost:3000/brainuse
```

**Click "New Candidate":**
- Name: `Test Engineer`
- Email: `test@example.com`
- Role: `Senior Backend Engineer`
- Company: `TestCorp`
- Domains: `Cloud Infrastructure`, `Technical Leadership`, `API Design`
- Click "Create"

### 3. Start Assessment

- Click candidate card
- Click "Give Consent" (simulate)
- Click "Start Assessment"
- Status changes to "In Progress"

### 4. Complete Assessment

- Click "Complete Assessment"
- Metrics calculated from query history
- Assessment saved to database

### 5. View Report

- Click "View Report"
- See 10-section comprehensive report:
  - Executive summary (Hire/Maybe/Pass)
  - Metrics dashboard (velocity, sophistication, persistence, discipline)
  - Percentile visualization
  - Strengths & concerns
  - Domain breakdown
  - Learning trajectory
  - Interview questions
  - Standout metrics
  - Assessment details
  - Print/PDF

---

## Expected Results (Average Profile)

### Metrics
- **Learning Velocity:** 0.30-0.40 levels/day
- **Sophistication:** 2.2-2.8 (out of 4.0)
- **Chain Depth:** 3.5-4.5 queries/chain
- **Tao Index:** 6.5-7.5 (out of 10)
- **Percentile:** 65-75th for Senior Backend Engineer

### Recommendation
**Maybe** or **Hire** (depending on exact scores)

### Report Highlights
**Strengths:**
- Progressed from fundamentals to advanced concepts
- Demonstrated curiosity through follow-up questions
- Explored multiple domains with consistent engagement

**Concerns:**
- Did not reach expert level in some domains
- Some topics explored shallowly

**Interview Questions:**
- "Can you explain a time you designed a distributed system?"
- "How do you handle trade-offs between speed and reliability?"
- "Tell me about a leadership challenge you faced."

---

## Customizing Test Data

### Multiple Candidates

```bash
# High performer
python scripts/synthesize_test_candidate.py \
  --candidate-name "Alice Expert" \
  --profile fast

# Average performer
python scripts/synthesize_test_candidate.py \
  --candidate-name "Bob Average" \
  --profile average

# Weak performer
python scripts/synthesize_test_candidate.py \
  --candidate-name "Charlie Weak" \
  --profile slow
```

### Different Domains

```bash
# Cloud + API only
python scripts/synthesize_test_candidate.py \
  --candidate-name "DevOps Specialist" \
  --domains cloud_assessment api_assessment

# Leadership only
python scripts/synthesize_test_candidate.py \
  --candidate-name "Engineering Manager" \
  --domains leadership_assessment \
  --profile average
```

---

## Adding Real Patterns (Optional)

You can add pattern files to make responses more realistic:

```bash
# Create patterns file
cat > domains/cloud_assessment/patterns.json << 'EOF'
[
  {
    "pattern_id": "cloud_001",
    "query": "What is EC2?",
    "response": "EC2 (Elastic Compute Cloud) is AWS's virtual server service..."
  },
  {
    "pattern_id": "cloud_002",
    "query": "When should I use RDS vs DynamoDB?",
    "response": "Choose RDS for relational data with complex queries..."
  }
]
EOF
```

But for testing BrainUse, synthesized responses are fine - we're testing **learning patterns**, not response quality.

---

## Troubleshooting

### Issue: "No history found for domain"

**Symptom:** Complete assessment fails with "No history found"
**Cause:** Query history not in correct location
**Fix:** Check file exists at `domains/{domain}/query_history.json.gz`

### Issue: "All metrics are zero"

**Symptom:** Report shows 0 for all metrics
**Cause:** Query history doesn't have sophistication metadata
**Fix:** Re-run synthesis script (adds sophistication field)

### Issue: "Percentile is 0%"

**Symptom:** Report shows 0th percentile
**Cause:** Role not in benchmarks OR Tao Index is very low
**Fix:** Check benchmark seeded for role, or verify learning velocity > 0

---

## Real Candidate Usage

Once you're ready for real candidates:

1. **Remove synthesized data:**
   ```bash
   rm domains/*/query_history.json.gz
   ```

2. **Candidate explores naturally:**
   - Give candidate ExFrame access
   - Invite them to explore assessment domains
   - No time pressure, no mandated sessions
   - 10-day assessment window

3. **Query history tracked automatically:**
   - Tao storage writes query_history.json.gz
   - Timestamps, sophistication, source all recorded
   - No additional instrumentation needed

4. **Complete assessment:**
   - After 10 days (or when candidate finishes)
   - Click "Complete Assessment" in dashboard
   - Metrics calculated from actual query history

---

## Summary

**Created:**
- ✅ 3 assessment domains (cloud, leadership, API)
- ✅ 3 librarian personas (progressive learning guides)
- ✅ Synthesis script (generate realistic test data)

**How to Test:**
1. Run synthesis script
2. Create candidate in dashboard
3. Start + complete assessment
4. View report with metrics

**Expected Outcome:**
- Tao Index: 6.5-7.5 (average profile)
- Percentile: 65-75th
- Recommendation: Maybe/Hire
- Comprehensive 10-section report

**Next:** Test with synthesized data, validate metrics, then pilot with real candidates.
