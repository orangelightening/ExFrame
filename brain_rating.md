# Brain Rating: Universal Intelligence Assessment Platform

**Core Insight:** The same metrics that predict job performance also detect cognitive decline.

**Why?** Because both measure the brain's fundamental capability: **learning efficiency**.

---

## The Universal Brain Metrics

### 1. **Learning Velocity** (Levels per Day)

**What it measures:** How fast someone progresses from novice (L1) to expert (L4) questions

**Hiring use:**
```
Candidate A: L1→L4 in 6 days = 0.50 velocity (Exceptional)
Candidate B: L1→L3 in 8 days = 0.25 velocity (Average)
```
**Interpretation:** Candidate A learns 2x faster → Better hire for fast-paced role

**Cognitive health use:**
```
Baseline (Age 45): L1→L4 in 6 days = 0.50 velocity
Age 52 (7 years later): L1→L4 in 9 days = 0.33 velocity (-34%)
```
**Interpretation:** Learning velocity declined 34% over 7 years → Red flag (normal aging: <10% decline)

### 2. **Question Sophistication** (Average Level)

**What it measures:** Complexity of questions asked (L1=basic, L4=expert)

**Hiring use:**
```
Candidate A questions:
- Day 1: "What is Python?" (L1)
- Day 3: "How do lists compare to tuples?" (L2)
- Day 5: "How does Python's GIL affect threading?" (L4)

Average level: 2.8 → Rapid sophistication growth
```
**Interpretation:** Deep, sophisticated thinking → Strong analytical ability

**Cognitive health use:**
```
Age 45 baseline:
- Avg level: 2.8 (mix of L2, L3, L4 questions)

Age 55 (10 years later):
- Avg level: 1.9 (mostly L1, L2 questions)

Regression: -32%
```
**Interpretation:** Cognitive complexity declining → Possible MCI

### 3. **Chain Depth** (Follow-up Questions)

**What it measures:** How far someone pursues a line of inquiry

**Hiring use:**
```
Candidate A:
Q1: "What is backpropagation?"
Q2: "How does chain rule apply?"
Q3: "Why does it work backward?"
Q4: "What are the computational costs?"
Q5: "Are there alternatives?"

Chain depth: 5 → High persistence/curiosity
```
**Interpretation:** Deep exploration → Self-directed learner

**Cognitive health use:**
```
Age 40 baseline:
- Average chain depth: 4.5

Age 48 (8 years later):
- Average chain depth: 1.8 (-60%)

Pattern: Asks one question, then stops (no follow-through)
```
**Interpretation:** Executive function impairment → Possible frontal lobe decline

### 4. **Concept Retention** (Queries to Re-master)

**What it measures:** How well knowledge is retained over time

**Hiring use:**
```
Day 2: Learn "gradient descent" (5 queries to master)
Day 8: Return to topic (2 queries to recall)

Retention: 60% (3 queries saved)
```
**Interpretation:** Good retention → Knowledge sticks

**Cognitive health use:**
```
2019: Learn "gradient descent" (5 queries to master)
2019 + 4 weeks: Retest (3 queries to recall) → 60% retention ✅ Good

2025: Learn "transformers" (8 queries to master)
2025 + 4 weeks: Retest (8 queries to recall) → 0% retention 🚨 Complete forgetting
```
**Interpretation:** Short-term memory consolidation failing → Early dementia marker

### 5. **Interest Ratio** (Interesting vs. Boring Performance)

**What it measures:** Disciplined learning ability (can they learn when unmotivated?)

**Hiring use:**
```
High-interest domain (Machine Learning): Tao Index 0.82
Low-interest domain (Compliance): Tao Index 0.31

Interest ratio: 2.65 (0.82 / 0.31)
```
**Interpretation:** Motivated learner only → Bad for roles with tedious work

**Cognitive health use:**
*Less relevant for cognitive health (not assessing discipline)*

### 6. **Tao Index** (Composite Score)

**Formula:**
```python
tao_index = (
    learning_velocity * 0.30 +
    avg_sophistication * 0.30 +
    chain_depth * 0.20 +
    retention_score * 0.20
)

Range: 0.0 - 1.0
```

**Hiring use:**
- **0.80+** = Exceptional (Top 5%)
- **0.70-0.79** = Excellent (Top 20%)
- **0.60-0.69** = Good (Above average)
- **0.50-0.59** = Average
- **<0.50** = Below average

**Cognitive health use:**
- Track absolute Tao Index over time
- **>10% decline over 5 years** = Red flag
- **>20% decline over 5 years** = Clinical referral needed

---

## Use Case 1: Hiring Intelligence (BrainUse)

### Objective
Identify candidates with:
1. High learning ability (fast L1→L4 progression)
2. Deep thinking (sophisticated questions)
3. Persistence (long chain depth)
4. Disciplined learning (low interest ratio for roles with tedious work)

### Assessment Protocol

**Duration:** 10 days
**Domains:** 3 (1 interesting, 1 neutral, 1 boring to candidate)
**Frequency:** Natural (candidate explores at their pace)

**Metrics Measured:**
- Learning velocity (per domain)
- Question sophistication distribution (L1/L2/L3/L4 %)
- Chain depth (average and max)
- Interest ratio (interesting vs. boring domain performance)
- Cross-domain analogies (systems thinking)
- Tao Index (composite score)

**Benchmarking:**
Compare to:
- Typical candidate for this role
- Top 10% performers
- Company-specific benchmarks (if available)

**Output:** Candidate Assessment Report
- Overall rating (Exceptional / Excellent / Good / Average / Below Average)
- Domain-by-domain breakdown
- Interest ratio analysis (job fit recommendations)
- Interview question suggestions (based on actual behavior)
- Hiring recommendation (Strong Hire / Hire / Maybe / Pass)

### Example: Senior Engineer Hire

**Candidate: Sarah Chen**

**Domain Performance:**
| Domain | Interest | Tao Index | Velocity | Avg Level | Chain Depth | Questions |
|--------|----------|-----------|----------|-----------|-------------|-----------|
| Machine Learning | High | 0.84 | 0.52 | 3.1 | 5.2 | 47 |
| API Design | Medium | 0.71 | 0.38 | 2.8 | 4.1 | 38 |
| Compliance | Low | 0.68 | 0.34 | 2.6 | 3.8 | 32 |

**Interest Ratio:** 1.24 (0.84 / 0.68)

**Interpretation:**
- **Exceptional learner** (0.84 Tao Index on high-interest topic)
- **Disciplined** (only 19% performance drop on boring material)
- **Consistent depth** (chain depth 3.8-5.2 across all domains)
- **Strong fit** for full-stack roles (handles both interesting architecture and boring docs)

**Recommendation:** 🚀 **Strong Hire** - Fast-track to offer

**Percentile Rankings:**
- Learning velocity: Top 3%
- Question sophistication: Top 8%
- Disciplined learning: Top 12%
- Overall: Top 5%

---

## Use Case 2: Cognitive Health Monitoring (CogniTao Health)

### Objective
Detect early cognitive decline by:
1. Establishing healthy baseline
2. Tracking longitudinal changes (years)
3. Alerting to abnormal decline patterns
4. Recommending clinical assessment when needed

### Assessment Protocol

**Duration:** Longitudinal (years)
**Frequency:**
- Age 40-50: Annual baseline
- Age 50-60: Annual monitoring
- Age 60-70: Biannual monitoring
- Age 70+: Quarterly monitoring
- If red flags: Quarterly monitoring at any age

**Domains:** Same domains retested periodically (e.g., "Python Programming" or "Photography" - doesn't matter what, consistency matters)

**Metrics Measured:**
- Learning velocity (change from baseline)
- Question sophistication (regression toward simpler questions)
- Chain depth (executive function proxy)
- Concept retention (memory consolidation)
- Tao Index (overall trend)

**Benchmarking:**
Compare to:
- Personal baseline (age 45 or first test)
- Age-matched norms
- Expected aging trajectory (5-10% decline per decade is normal)

**Output:** Cognitive Health Report
- 5-10 year trend analysis
- Learning velocity trajectory (graph)
- Retention curve (mastered concepts over time)
- Risk assessment (Normal / Monitor / Clinical Referral)
- Recommended next steps (continue monitoring vs. see neurologist)

### Example: Early Decline Detection

**Patient: John Smith, Age 52**

**Longitudinal Data:**
| Year | Age | Tao Index | Velocity | Avg Level | Chain Depth | Retention |
|------|-----|-----------|----------|-----------|-------------|-----------|
| 2019 | 45  | 0.75      | 0.42     | 2.8       | 4.5         | 75% |
| 2021 | 47  | 0.72      | 0.40     | 2.7       | 4.2         | 72% |
| 2023 | 49  | 0.68      | 0.36     | 2.5       | 3.5         | 68% |
| 2025 | 51  | 0.62      | 0.32     | 2.2       | 2.8         | 55% |
| 2026 | 52  | 0.58      | 0.29     | 1.9       | 1.8         | 40% |

**Trends:**
- **Learning velocity:** -31% over 7 years (expected: <10%)
- **Question sophistication:** -32% over 7 years (regression to simpler questions)
- **Chain depth:** -60% over 7 years (executive function collapse)
- **Retention:** -47% over 7 years (memory consolidation failing)
- **Tao Index:** -23% over 7 years (overall cognitive decline)

**Risk Assessment:** 🚨 **HIGH RISK - Multiple red flags**

**Clinical Recommendation:**
- **Urgent:** Schedule cognitive assessment with neurologist
- **Tests:** MRI, MoCA, detailed neuropsychological evaluation
- **Biomarkers:** Consider CSF testing (Aβ42, tau, p-tau)
- **Lifestyle:** Immediate brain-healthy interventions (exercise, sleep, Mediterranean diet)

**Differential Diagnosis:**
- Mild Cognitive Impairment (MCI) - most likely
- Early Alzheimer's Disease - possible
- Vascular cognitive impairment - possible
- Depression/anxiety - rule out
- Sleep disorder - rule out

**Follow-up:** Quarterly monitoring + medical workup

---

## Key Differences: Hiring vs. Cognitive Health

| Aspect | Hiring (BrainUse) | Cognitive Health (CogniTao) |
|--------|-------------------|----------------------------|
| **Timeframe** | 10 days (one-time) | Years (longitudinal) |
| **Baseline** | Benchmark to other candidates | Personal baseline over time |
| **Goal** | Rank candidates (who's best?) | Detect decline (are they declining?) |
| **Domains** | 3 domains (varied interest) | 1-2 domains (consistent retest) |
| **Frequency** | Once per hiring process | Annual / quarterly |
| **Users** | Job candidates | Aging adults (50+) |
| **Market** | B2B (HR departments) | B2C (individuals) or B2B2C (healthcare) |
| **Revenue** | $150 per assessment | $10-20/month subscription |
| **Compliance** | EEOC, bias auditing | HIPAA, medical data privacy |
| **Output** | Hiring recommendation | Clinical referral decision |
| **False positive cost** | Miss a good hire | Unnecessary doctor visit |
| **False negative cost** | Bad hire ($100K) | Missed early Alzheimer's (years of decline) |
| **Data retention** | 1 year post-hire | Lifetime (or per user request) |

---

## Shared Infrastructure (Already Built) ✅

**Core Tao Platform:**
1. ✅ Storage - Compressed query/response history (`query_history.json.gz`)
2. ✅ Classification - L1-L4 sophistication (automatic on save)
3. ✅ Learning Velocity - Calculation module (`tao/analysis/sophistication.py`)
4. ✅ Causality - Parent query tracking (`parent_query_id`)
5. ✅ Analysis - Sessions, chains, concepts, depth (`tao/analysis/`)
6. ✅ API - 11 REST endpoints (`/api/tao/*`)
7. ✅ Frontend - Web UI for viewing analysis (`/tao`)

**What Works Out-of-the-Box:**
- Save query/response with auto-classification ✅
- Calculate learning velocity over time ✅
- Track question sophistication distribution ✅
- Trace query chains (persistence) ✅
- Detect related queries (cross-domain thinking) ✅

---

## What Needs to Be Built (MVP)

### For Hiring (BrainUse MVP)

**Priority 1 (Must-Have):**
1. **Assessment Domains** (3-5 curated domains for hiring)
   - Python Programming
   - Cloud Architecture
   - Team Leadership
   - Database Design
   - API Design

2. **Candidate Module** (`tao/vetting/candidate.py`)
   - Candidate data model
   - Domain assignment logic
   - Interest ratio calculation

3. **Benchmarking** (`tao/vetting/benchmarks.py`)
   - Store typical performance by role
   - Percentile calculations
   - Compare candidate to benchmarks

4. **Report Generation** (`tao/vetting/reports.py`)
   - PDF report generator
   - Hiring recommendation logic
   - Interview question suggestions

5. **Assessment Portal** (Simple web interface)
   - Candidate login/onboarding
   - Progress dashboard
   - "Thanks for completing" page

**Priority 2 (Nice-to-Have):**
6. Job profile matching (interest ratio → role fit)
7. ATS integration (Greenhouse, Lever APIs)
8. Multi-candidate comparison dashboard

**Estimated Time:** 2-3 weeks for MVP

### For Cognitive Health (CogniTao Health MVP)

**Priority 1 (Must-Have):**
1. **Longitudinal Storage** (already supported - just use existing storage over time)

2. **Trend Analysis** (`tao/health/trends.py`)
   - Calculate % change from baseline
   - Detect abnormal decline patterns
   - Risk scoring (Normal / Monitor / Refer)

3. **Baseline Establishment** (First-time user flow)
   - "Establishing your cognitive baseline" messaging
   - Explain why they need to test when healthy
   - Set reminders for annual retests

4. **Alert Thresholds** (`tao/health/alerts.py`)
   - Define normal aging vs. abnormal decline
   - Generate clinical referral recommendations
   - Export data for doctors

5. **Health Dashboard** (Web UI)
   - Multi-year trend graphs
   - Risk assessment display
   - "Share with doctor" button (PDF export)

**Priority 2 (Nice-to-Have):**
6. Retention tracking (spaced repetition for memory testing)
7. Medical portal integration (share data with physicians)
8. Family/caregiver access (with permission)

**Estimated Time:** 2-3 weeks for MVP

---

## Technical Architecture

### Database Schema (PostgreSQL)

**For Hiring:**
```sql
-- Candidates table
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    company_id INTEGER,
    assigned_domains JSONB,  -- {domain: interest_level}
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Assessments table
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id),
    domain VARCHAR(100),
    tao_index DECIMAL(3,2),
    learning_velocity DECIMAL(4,3),
    avg_level DECIMAL(3,2),
    chain_depth DECIMAL(3,2),
    question_count INTEGER,
    completed_at TIMESTAMP
);

-- Benchmarks table
CREATE TABLE benchmarks (
    id SERIAL PRIMARY KEY,
    role VARCHAR(100),
    seniority VARCHAR(50),
    metric_name VARCHAR(100),
    p10 DECIMAL(4,3),  -- 10th percentile
    p50 DECIMAL(4,3),  -- Median
    p90 DECIMAL(4,3),  -- 90th percentile
    sample_size INTEGER,
    updated_at TIMESTAMP
);

-- Reports table
CREATE TABLE candidate_reports (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id),
    report_data JSONB,  -- Full report as JSON
    pdf_path VARCHAR(500),
    recommendation VARCHAR(50),  -- Strong Hire, Hire, Maybe, Pass
    overall_rating DECIMAL(3,2),
    created_at TIMESTAMP
);
```

**For Cognitive Health:**
```sql
-- Users table
CREATE TABLE health_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    date_of_birth DATE,
    baseline_age INTEGER,
    baseline_established_at TIMESTAMP,
    subscription_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cognitive assessments table
CREATE TABLE cognitive_assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES health_users(id),
    assessment_date DATE,
    age_at_assessment INTEGER,
    domain VARCHAR(100),
    tao_index DECIMAL(3,2),
    learning_velocity DECIMAL(4,3),
    avg_level DECIMAL(3,2),
    chain_depth DECIMAL(3,2),
    retention_score DECIMAL(3,2),
    pct_change_from_baseline DECIMAL(5,2),  -- % change
    completed_at TIMESTAMP
);

-- Risk assessments table
CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES health_users(id),
    assessment_date DATE,
    risk_level VARCHAR(50),  -- Normal, Monitor, Refer
    decline_velocity DECIMAL(5,2),  -- % per year
    red_flags JSONB,  -- Array of red flag descriptions
    recommendation TEXT,
    created_at TIMESTAMP
);

-- Medical exports table (HIPAA-compliant audit log)
CREATE TABLE medical_exports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES health_users(id),
    exported_at TIMESTAMP,
    exported_by VARCHAR(255),  -- user or physician
    export_format VARCHAR(50),  -- PDF, CSV, FHIR
    export_path VARCHAR(500),
    recipient_email VARCHAR(255)
);
```

### API Endpoints (New)

**Hiring:**
```
POST   /api/brainuse/candidates              # Create candidate
GET    /api/brainuse/candidates/{id}         # Get candidate data
POST   /api/brainuse/assessments             # Submit assessment
GET    /api/brainuse/reports/{candidate_id}  # Generate report
GET    /api/brainuse/benchmarks/{role}       # Get role benchmarks
POST   /api/brainuse/compare                 # Compare candidates
```

**Cognitive Health:**
```
POST   /api/cognitao/users                   # Create user
GET    /api/cognitao/users/{id}/baseline     # Get baseline data
POST   /api/cognitao/assessments             # Submit assessment
GET    /api/cognitao/trends/{user_id}        # Get longitudinal trends
GET    /api/cognitao/risk/{user_id}          # Get risk assessment
POST   /api/cognitao/export                  # Export for doctor
GET    /api/cognitao/alerts/{user_id}        # Get alert status
```

---

## Pricing Models

### Hiring (BrainUse)

**Per-Candidate Pricing:**
- $150 per candidate assessed
- Volume discounts: 50+ = $120, 100+ = $100
- No monthly minimums

**Subscription Pricing:**
- $2,500/month for up to 20 candidates
- $5,000/month for up to 50 candidates
- $10,000/month for up to 100 candidates

**Enterprise:**
- Custom pricing ($150K-500K/year)
- White-label option
- Custom domains
- Dedicated support

### Cognitive Health (CogniTao Health)

**Consumer Direct:**
- $10/month individual
- $15/month family (up to 4 members)
- $99/year (2 months free)

**Healthcare Provider:**
- $5/month per patient (bulk discount)
- $50K/year for 1,000 patients
- Medical portal integration included

**Medicare/Insurance:**
- Seek reimbursement as "cognitive screening service"
- Target: $20-30 per assessment (4x/year = $80-120/year)

---

## Go-to-Market Strategy

### Hiring MVP (First 6 Months)

**Target:** 5 pilot customers, 50 candidates assessed

**Tactics:**
1. Outreach to VP Engineering / Head of Talent (cold email + LinkedIn)
2. Offer: Free pilot (assess 10 candidates free)
3. Case study after successful hire (prove ROI)
4. Expand within company (50+ candidates)
5. Referral program (1 free assessment per referral)

**Success Metric:** 1 customer converts to paid ($2,500/month) after pilot

### Cognitive Health (12-18 Months Out)

**Target:** 100 early adopters (beta users)

**Tactics:**
1. Content marketing: "Early Alzheimer's detection" blog posts
2. Partner with Alzheimer's Association (non-profit credibility)
3. Medical conference presence (American Academy of Neurology)
4. Doctor referrals (neurologists recommend to patients)
5. Clinical validation study (publish results)

**Success Metric:** 100 monthly subscribers ($1,000 MRR)

---

## Success Metrics (KPIs)

### Hiring (BrainUse)

**Product Metrics:**
- Candidate completion rate (target: >85%)
- Report generation time (target: <30 min)
- Benchmark database size (target: 1,000+ candidates by end of Year 1)

**Business Metrics:**
- MRR (target: $10K Month 6, $50K Month 12)
- Customers (target: 5 Month 6, 20 Month 12)
- Candidates assessed (target: 50 Month 6, 500 Month 12)

**Outcome Metrics:**
- New hire success rate (target: improve from 54% to 75%)
- Customer retention (target: >90% annually)
- Referral rate (target: 30% of customers refer others)

### Cognitive Health (CogniTao)

**Product Metrics:**
- Baseline establishment rate (target: >90% of users complete first test)
- Retest compliance (target: >70% return for annual retest)
- Clinical referral rate (target: 5-10% of users referred to doctors)

**Business Metrics:**
- MRR (target: $1K Month 12, $10K Month 18, $100K Month 24)
- Subscribers (target: 100 Month 12, 1,000 Month 18, 10,000 Month 24)
- Churn rate (target: <5% monthly)

**Outcome Metrics:**
- Early detection rate (how many MCI cases found?)
- Time to diagnosis (how much earlier than typical?)
- Medical validation (% of referrals confirmed by neurologist)

---

## Risks & Mitigations

### Hiring Risks

**Risk:** Customers don't see ROI
**Mitigation:** Track hiring outcomes (90-day retention, manager satisfaction), prove value

**Risk:** Candidates find it too time-consuming
**Mitigation:** Optimize to <1 hour per day, emphasize learning value (they get knowledge)

**Risk:** Legal challenges (discrimination, bias)
**Mitigation:** Regular bias audits, legal review, transparent methodology

### Cognitive Health Risks

**Risk:** False positives (healthy people flagged)
**Mitigation:** Conservative thresholds, "screening tool not diagnosis" disclaimer

**Risk:** Medical liability
**Mitigation:** HIPAA compliance, liability insurance, medical advisory board

**Risk:** Users don't return for retests
**Mitigation:** Automated reminders, gamification, family accountability features

---

## Next Steps (Hiring MVP)

**Week 1-2: Domain Library**
1. Create 5 assessment domains (Python, Cloud, Leadership, Database, API)
2. Curate 20-30 patterns per domain
3. Write documents for librarian persona to search

**Week 3-4: Vetting Module**
4. Build candidate data model
5. Implement interest ratio calculation
6. Create benchmarking infrastructure

**Week 5-6: Report Generation**
7. Build PDF report generator
8. Implement recommendation logic
9. Create interview question suggestions

**Week 7-8: Testing & Pilot**
10. Test with 5 internal candidates
11. Refine based on feedback
12. Launch with first pilot customer

---

**Document Status:** Comprehensive brain rating framework
**Last Updated:** 2026-02-16
**Next:** Implement hiring MVP (Weeks 1-8)
