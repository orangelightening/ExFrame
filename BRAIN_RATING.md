# Brain Rating - Two Paths, One Platform

**Core Thesis:** Tao's learning pattern analysis has two legitimate, ethical applications:
1. **Hiring Intelligence** - Assess learning capacity during job candidate evaluation
2. **Cognitive Health** - Detect early signs of cognitive decline (Alzheimer's, dementia)

Both use the same underlying Tao platform. Both measure learning patterns through question-asking behavior.

---

## Shared Foundation: Tao Analysis Platform

### Core Metrics (Both Paths)
- **Learning Velocity** - How quickly user progresses from simple to complex questions
- **Question Sophistication** - Depth/complexity of questions asked (0-4.0 scale)
- **Chain Depth** - How many follow-up questions in exploration chains
- **Concept Retention** - Whether concepts reappear in later queries
- **Session Patterns** - Time gaps, query frequency, exploration style

### Tao Components (Already Built)
```
tao/
├── storage/          # Query/response history storage
│   └── storage.py    # Append-only, compressed, timestamped
├── analysis/         # Learning pattern analysis
│   ├── sessions.py   # Session detection (time gaps)
│   ├── chains.py     # Follow-up chain tracing
│   ├── sophistication.py # Learning velocity calculation
│   ├── depth.py      # Deep exploration detection
│   └── concepts.py   # Concept timeline tracking
└── api/              # REST API for analysis tools
    └── router.py     # /api/tao/* endpoints
```

**Status:** ✅ Core platform exists and operational

---

## Path 1: Hiring Intelligence (BrainUse)

**Status:** ✅ MVP Complete (80% done)

### Use Case
Assess job candidates' learning capacity during hiring process. Replace/augment traditional coding tests with curiosity-driven exploration.

### How It Works
1. **Candidate invited** to explore assessment domains (Python, Cloud, Leadership, etc.)
2. **10-day period** - candidate asks questions naturally through ExFrame
3. **Tao tracks patterns** - learning velocity, sophistication growth, exploration depth
4. **Report generated** - Tao Index score, percentile, hire/maybe/pass recommendation
5. **Recruiter reviews** - data-driven hiring decision

### Key Metrics
- **Tao Index** - Composite score (0-10): `0.3*velocity + 0.3*sophistication + 0.2*chain_depth + 0.2*retention`
- **Percentile** - Compared to benchmark for role (e.g., "91st percentile for Senior Backend Engineer")
- **Interest Ratio** - Performance in "boring" vs "interesting" domains (discipline measure)
- **Domain Scores** - Per-domain breakdown (Python: 0.45 velocity, Cloud: 0.32 velocity)

### Assessment Period
- **Duration:** 10 days
- **Frequency:** Candidate-driven (no mandated sessions)
- **Domains:** 3-5 technical/soft skill domains
- **Privacy:** Candidate consents, data used only for hiring decision

### Architecture
```
tao/vetting/              # BrainUse module
├── models.py             # Candidate, Assessment, Report
├── candidate_manager.py  # CRUD operations
├── benchmark_engine.py   # Role benchmarks, percentiles
├── report_generator.py   # Assessment reports
├── database.py           # PostgreSQL persistence
├── db_models.py          # SQLAlchemy models
├── api_router.py         # REST API
└── frontend/             # Recruiter dashboard + report viewer
    ├── index.html        # Dashboard
    ├── report.html       # Report viewer
    └── assets/           # JS/CSS
```

### API Endpoints
```
POST   /api/brainuse/candidates          # Create candidate
GET    /api/brainuse/candidates          # List candidates
GET    /api/brainuse/candidates/:id      # Get candidate
POST   /api/brainuse/candidates/:id/start   # Start assessment
POST   /api/brainuse/candidates/:id/complete # Complete assessment
GET    /api/brainuse/candidates/:id/report  # View report
```

### Database Schema
- **candidates** - Name, email, role, company, status, consent, assessment domains
- **assessments** - All metrics, domain scores, Tao Index, percentile
- **reports** - Recommendation, confidence, strengths, concerns, interview questions
- **benchmarks** - Role-based percentiles (p50, p75, p90 for each metric)

### Current Status
- ✅ Candidate management (create, list, update)
- ✅ Assessment flow (start, complete)
- ✅ Metric calculation (velocity, sophistication, chains, concepts)
- ✅ Report generation (recommendation, strengths, concerns)
- ✅ Recruiter dashboard (candidate list, filters, search)
- ✅ Report viewer (10-section comprehensive report)
- ✅ PostgreSQL persistence (4 tables)
- ⏳ Benchmark calibration (needs real data)
- ⏳ PDF export (server-side)
- ⏳ Pilot customer testing

### Next Steps (Week 6-8)
1. Calibrate benchmarks with pilot customer data
2. Add server-side PDF generation
3. Test with 5-10 real candidates
4. Iterate based on recruiter feedback
5. Production deployment

---

## Path 2: Cognitive Health Monitoring

**Status:** 🔄 Design Phase (Not Yet Built)

### Use Case
Detect early signs of cognitive decline (Alzheimer's, dementia) through longitudinal learning pattern analysis. Provide individuals with early warning signs to seek medical evaluation.

### How It Works
1. **Baseline established** - User explores topics of interest over initial period (1-3 months)
2. **Ongoing monitoring** - User continues natural ExFrame usage (no mandated sessions)
3. **Tao tracks changes** - Detects degradation in learning patterns over time
4. **Alerts triggered** - When decline patterns match cognitive health markers
5. **User notified** - Suggests consulting healthcare provider

### Key Differences from Hiring
| Aspect | Hiring | Cognitive Health |
|--------|--------|------------------|
| **Timeframe** | 10 days | Months to years |
| **Sessions** | Candidate-driven | Natural usage |
| **Baseline** | Role benchmark | Personal baseline |
| **Comparison** | Against peers | Against own history |
| **Privacy** | Shared with employer | Personal/medical data |
| **Output** | Hire/pass decision | Health alert |
| **Regulation** | Employment law | HIPAA/medical data |

### Cognitive Decline Indicators
1. **Declining Learning Velocity** - Takes longer to progress through sophistication levels
2. **Sophistication Regression** - Questions become simpler over time (regression curve)
3. **Reduced Chain Depth** - Fewer follow-up questions, shorter explorations
4. **Concept Repetition** - Asking same questions repeatedly (short-term memory loss)
5. **Session Fragmentation** - More frequent, shorter sessions (attention span)
6. **Temporal Disorientation** - Time-of-day patterns shift (circadian disruption)

### Temporal Markers (Critical for Cognitive Health)
- **Baseline period** - Establish personal "normal" (3-6 months)
- **Trend analysis** - Detect gradual decline over quarters/years
- **Velocity of decline** - How fast patterns are degrading
- **Reversibility** - Whether decline slows/reverses (treatment working?)
- **Time-of-day patterns** - Cognitive performance varies by time (sundowning)

### Architecture (Proposed)
```
tao/cognitive/            # NEW: Cognitive health module
├── models.py             # User, Baseline, Alert
├── baseline_manager.py   # Establish personal baseline
├── decline_detector.py   # Pattern degradation detection
├── alert_engine.py       # Trigger health alerts
├── timeline_analyzer.py  # Temporal pattern analysis
├── database.py           # Separate DB (medical privacy)
├── api_router.py         # REST API (HIPAA-compliant)
└── frontend/             # Personal dashboard
    ├── index.html        # Health tracking dashboard
    ├── timeline.html     # Temporal visualization
    └── assets/           # JS/CSS
```

### Database Schema (Proposed)
- **users** - User ID, baseline established, alert settings, privacy consent
- **baselines** - Personal metrics (velocity, sophistication, chain depth) during healthy period
- **measurements** - Monthly/quarterly snapshots of current metrics
- **alerts** - Decline detected, severity, date triggered, acknowledged
- **sessions_timeline** - Session patterns over time (for temporal analysis)

### Privacy & Ethics
- ✅ **Self-administered** - User controls their own data
- ✅ **No employer access** - Medical data, not employment data
- ✅ **HIPAA compliance** - Proper data handling (if used clinically)
- ✅ **Opt-in alerts** - User chooses whether to be notified
- ✅ **Medical disclaimer** - Not diagnostic, suggests consulting doctor
- ❌ **No insurance/employer reporting** - Data never shared without explicit consent

### Metrics Interpretation
```python
# Example: Detecting cognitive decline

# Baseline (healthy period)
baseline_velocity = 0.42  # levels/day
baseline_sophistication = 2.8
baseline_chain_depth = 4.2

# Current measurement (6 months later)
current_velocity = 0.28  # 33% decline
current_sophistication = 2.1  # 25% decline
current_chain_depth = 2.8  # 33% decline

# Alert trigger
if all([
    current_velocity < baseline_velocity * 0.7,  # >30% decline
    current_sophistication < baseline_sophistication * 0.75,  # >25% decline
    current_chain_depth < baseline_chain_depth * 0.7  # >30% decline
]):
    trigger_alert("Significant cognitive decline detected. Consider medical evaluation.")
```

### Clinical Validation Needed
⚠️ **This use case requires medical validation:**
- Partner with neurology researchers
- Controlled studies comparing Tao metrics to clinical assessments
- Establish sensitivity/specificity for early Alzheimer's detection
- Publish in medical journals
- FDA clearance if used diagnostically

### Market Opportunity
- **Early detection** - Alzheimer's diagnosed too late (80% diagnosed at moderate stage)
- **At-home monitoring** - Scalable, non-invasive, continuous assessment
- **Aging population** - 55M people with dementia worldwide (2020), growing to 78M (2030)
- **Personal tracking** - Individuals concerned about family history
- **Post-diagnosis monitoring** - Track treatment effectiveness

### Risks & Concerns
- **False positives** - Alerting healthy people unnecessarily (anxiety)
- **False negatives** - Missing true decline (false reassurance)
- **Medical liability** - If used as diagnostic tool
- **Privacy breach** - Highly sensitive medical data
- **Discrimination** - If data leaked to employers/insurers

### Next Steps (If Pursuing)
1. **Research partnership** - Find neurology lab/hospital partner
2. **Clinical study design** - Protocol for validation study
3. **IRB approval** - Institutional review board for human subjects research
4. **Pilot study** - 50-100 participants (healthy controls + early Alzheimer's)
5. **Validation** - Compare Tao metrics to clinical gold standard (MoCA, MMSE)
6. **Publication** - Peer-reviewed research establishing validity
7. **Regulatory** - FDA clearance if used diagnostically

---

## Path 3: Employee Monitoring (REJECTED)

**Status:** ❌ Not Building (Ethical Concerns)

### Why Not?
1. **Surveillance culture** - Dystopian workplace monitoring
2. **Weaponized metrics** - "Your learning speed is down 20%. You're fired."
3. **Stress/anxiety** - Constant performance pressure
4. **Gaming behavior** - Employees will game the system
5. **Legal liability** - Disability discrimination (ADA violations)
6. **Privacy invasion** - Invasive cognitive tracking by employer
7. **Power imbalance** - Employer has leverage over employee's livelihood

### Comparison to Other Use Cases
- **vs Hiring:** Hiring is voluntary (candidate opts in), one-time assessment, candidate expects evaluation
- **vs Cognitive Health:** Personal data, user-controlled, health benefit, no employer access

### Why It Seemed Similar
- Daily 15-minute sessions (like cognitive health ongoing monitoring)
- Learning velocity tracking (same metrics)
- Temporal patterns (like cognitive health timeline)
- BUT: Context matters - employer surveillance vs personal health tracking

### Slippery Slope
If we built this:
1. Start with "optional learning time"
2. Become "recommended learning time"
3. Become "required learning time"
4. Metrics used in performance reviews
5. Low performers get PIP (performance improvement plan)
6. Eventually: "Your Tao Index is below team average. We're letting you go."

### Bottom Line
**We do not build tools that enable workplace surveillance or cognitive discrimination.**

---

## Architecture: Shared Core, Separate Modules

```
eeframe/
├── tao/                          # Core Tao platform (shared)
│   ├── storage/                  # Query/response storage
│   ├── analysis/                 # Learning pattern analysis
│   └── api/                      # Analysis API
│
├── tao/vetting/                  # Path 1: Hiring (BrainUse)
│   ├── models.py
│   ├── candidate_manager.py
│   ├── benchmark_engine.py
│   ├── report_generator.py
│   ├── database.py               # PostgreSQL for hiring data
│   └── frontend/                 # Recruiter dashboard
│
└── tao/cognitive/                # Path 2: Cognitive Health (Future)
    ├── models.py
    ├── baseline_manager.py
    ├── decline_detector.py
    ├── alert_engine.py
    ├── database.py               # Separate DB (medical privacy)
    └── frontend/                 # Personal health dashboard
```

### Separation Strategy
- **Separate databases** - Hiring data ≠ Medical data (privacy firewall)
- **Separate frontends** - Recruiter dashboard ≠ Personal health dashboard
- **Separate APIs** - `/api/brainuse/*` vs `/api/cognitive/*`
- **Shared analysis** - Both use `tao/analysis/*` (same metrics, different interpretation)

---

## Technical Decision: Build Order

### Option 1: Finish Hiring MVP First (RECOMMENDED)
**Rationale:**
- Hiring MVP is 80% complete
- Has paying customers (recruiters/companies)
- Faster path to revenue
- Validate Tao metrics with real candidates
- Build credibility before tackling medical use case

**Timeline:**
- Week 6: Calibrate benchmarks with pilot data
- Week 7: Polish dashboard, add PDF export
- Week 8: Onboard first pilot customer
- Week 9-12: Iterate based on feedback, expand to 5 customers
- **Revenue:** Month 3-4

### Option 2: Build Cognitive Health in Parallel
**Rationale:**
- Core Tao platform is shared (already built)
- Can build `tao/cognitive/` while piloting `tao/vetting/`
- Longer path to market (clinical validation needed)
- But: demonstrates platform versatility

**Challenges:**
- Requires medical partnerships
- Clinical validation takes 12-18 months
- Regulatory complexity (HIPAA, FDA)
- No immediate revenue

### Recommendation: **Sequence (Option 1)**
1. ✅ **Now:** Finish Hiring MVP (Weeks 6-8)
2. ✅ **Next:** Pilot with 5 companies (Weeks 9-16)
3. ✅ **Then:** Start cognitive health (Weeks 17+)

**Why?**
- Hiring MVP is nearly done - finish what we started
- Revenue funds cognitive health development
- Real candidate data validates Tao metrics
- Proven platform attracts medical research partners
- Credibility: "Our hiring tool works" → easier to pitch cognitive health

---

## Metrics Comparison

| Metric | Hiring | Cognitive Health |
|--------|--------|------------------|
| **Learning Velocity** | Compare to role benchmark | Compare to personal baseline |
| **Sophistication** | Absolute level (0-4.0) | Change over time (decline?) |
| **Chain Depth** | Persistence in exploration | Attention span indicator |
| **Concept Retention** | Learn new concepts | Short-term memory marker |
| **Interest Ratio** | Discipline measure | Motivation/engagement marker |
| **Session Patterns** | Engagement level | Circadian disruption marker |
| **Timeframe** | 10 days (snapshot) | Months/years (longitudinal) |
| **Baseline** | Role benchmark | Personal baseline (healthy period) |
| **Output** | Hire/pass decision | Health alert (seek doctor) |

---

## Summary

### Core Platform (Already Built)
✅ Tao storage, analysis, and API are operational
✅ Learning velocity, sophistication, chains, concepts all working
✅ Query history tracking with timestamps and compression

### Path 1: Hiring Intelligence (80% Complete)
✅ Candidate management with PostgreSQL
✅ Assessment flow (start, complete)
✅ Metric calculation (Tao Index, percentiles)
✅ Report generation (hire/maybe/pass)
✅ Recruiter dashboard and report viewer
⏳ Benchmark calibration (needs real data)
⏳ Pilot customer testing

### Path 2: Cognitive Health (Design Phase)
🔄 Architecture designed
🔄 Metrics defined (decline indicators)
🔄 Privacy/ethics considerations mapped
⏳ Clinical validation needed
⏳ Medical partnerships required
⏳ Regulatory path unclear

### Path 3: Employee Monitoring (Rejected)
❌ Ethical concerns (surveillance, discrimination)
❌ Legal liability (ADA violations)
❌ Creates toxic workplace culture
❌ We do not build this

---

## Next Steps

### Immediate (Week 6)
1. ✅ Finish hiring MVP
2. Test with real candidate data
3. Calibrate benchmarks
4. Add PDF export

### Short-term (Weeks 7-12)
1. Onboard pilot customers (3-5 companies)
2. Iterate based on recruiter feedback
3. Expand benchmark data
4. Add features (interviewer notes, share reports)

### Long-term (Months 4+)
1. Explore cognitive health partnerships
2. Design clinical validation study
3. Build `tao/cognitive/` module
4. Navigate regulatory path

---

## Business Model

### Hiring (BrainUse)
- **B2B SaaS** - Subscription per company
- **Pricing:** $500-2000/month (based on hiring volume)
- **Customer:** Tech companies, startups, recruiters
- **GTM:** Direct sales, recruiter networks
- **Revenue:** Year 1 target: $50k MRR (10 customers)

### Cognitive Health (Future)
- **B2C Subscription** - Individual health tracking
- **Pricing:** $20-50/month (personal health monitoring)
- **Customer:** Individuals 50+ concerned about cognitive health
- **GTM:** Direct-to-consumer, medical referrals
- **Revenue:** Long-tail, high volume

---

**Bottom Line:** Core platform exists. Hiring MVP is almost done. Cognitive health is interesting but requires clinical validation. Employee monitoring is off the table due to ethical concerns. **Finish hiring MVP first.**

---

## Ethics Statement

**We build tools that:**
✅ Empower individuals (candidate choice, personal health)
✅ Respect privacy (consent-based, data ownership)
✅ Reduce bias (objective metrics vs subjective interviews)
✅ Enable agency (candidates/users control their data)

**We do not build tools that:**
❌ Enable surveillance (workplace monitoring)
❌ Create power imbalances (employer cognitive tracking)
❌ Weaponize metrics (fire people for learning speed)
❌ Invade privacy (mandatory cognitive assessment)

**Tao is for learning, not surveillance.**
