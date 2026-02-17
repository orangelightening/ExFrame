# BrainUse Installation Guide

**Hiring Intelligence System for ExFrame**

---

## Prerequisites

- Docker & Docker Compose
- Git
- 2GB free disk space
- Ports 3000, 5432 available

---

## Quick Start (5 minutes)

```bash
# 1. Clone repository
git clone <repo-url>
cd eeframe

# 2. Build and start
docker compose up -d --build

# 3. Wait for initialization (30 seconds)
# Check logs: docker compose logs -f eeframe-app

# 4. Open dashboard
open http://localhost:3000/brainuse

# 5. Seed benchmarks (first time only)
docker compose exec eeframe-app python -m tao.vetting.seed_benchmarks
```

**Done!** BrainUse is running.

---

## What Gets Installed

### Services
- **ExFrame App** (port 3000) - Main application
- **PostgreSQL** (port 5432) - Database for candidates/assessments
- **Prometheus** (port 9090) - Metrics (optional)
- **Grafana** (port 3001) - Dashboards (optional)

### Modules
- **tao/vetting/** - BrainUse hiring intelligence module
- **Assessment Domains** - Cloud, Leadership, API (3 domains)
- **Librarian Personas** - Progressive learning guides

### Database
- PostgreSQL 16 with 4 tables:
  - `candidates` - Candidate information
  - `assessments` - Calculated metrics
  - `reports` - Generated reports
  - `benchmarks` - Role benchmarks

---

## Detailed Installation

### Step 1: Environment Variables (Optional)

Create `.env` file if you need custom configuration:

```bash
# LLM Configuration
OPENAI_API_KEY=your-key-here
LLM_MODEL=gpt-4

# Database (defaults work fine)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=brainuse
POSTGRES_USER=brainuse
POSTGRES_PASSWORD=brainuse_dev_password
```

### Step 2: Build

```bash
docker compose build eeframe-app
```

This installs:
- Python 3.12
- FastAPI
- SQLAlchemy + psycopg2
- Sentence transformers
- All ExFrame dependencies

**Build time:** 2-3 minutes

### Step 3: Start Services

```bash
docker compose up -d
```

Starts:
- eeframe-app
- postgres
- prometheus (optional)
- grafana (optional)
- loki (optional)
- promtail (optional)

**Startup time:** 30 seconds

### Step 4: Verify Installation

```bash
# Check all services running
docker compose ps

# Should see:
# - eeframe-app (healthy)
# - postgres (healthy)

# Check logs
docker compose logs eeframe-app | tail -20

# Should see:
# ✓ Database initialized
# ✓ Database tables created
# ✓ BrainUse API mounted at /api/brainuse
# ExFrame Runtime Ready
```

### Step 5: Seed Benchmarks

**First time only:**

```bash
docker compose exec eeframe-app python -m tao.vetting.seed_benchmarks
```

Output:
```
✓ Added benchmark: Senior Backend Engineer (n=50)
✓ Added benchmark: Senior Frontend Engineer (n=42)
✓ Added benchmark: Staff Engineer (n=38)
✓ Added benchmark: Engineering Manager (n=35)
✓ Added benchmark: Data Engineer (n=45)
✓ Added benchmark: DevOps Engineer (n=40)
✓ Added benchmark: Machine Learning Engineer (n=33)
✓ Added benchmark: Product Manager (n=30)
✓ Seeded 8 benchmark roles
```

### Step 6: Access Dashboard

```bash
open http://localhost:3000/brainuse
```

You should see:
- Empty candidate list
- "New Candidate" button
- Filter/search bar
- Stats header (0 candidates)

---

## Test Installation

### Create Test Candidate

```bash
# Generate test data
python3 scripts/synthesize_test_candidate.py \
  --candidate-name "Test Engineer" \
  --profile average
```

Output:
```
✓ Saved 56 entries to universes/MINE/domains/cloud_assessment/query_history.json.gz
✓ Saved 36 entries to universes/MINE/domains/leadership_assessment/query_history.json.gz
✓ Saved 38 entries to universes/MINE/domains/api_assessment/query_history.json.gz
```

### Complete Assessment Flow

1. **Create Candidate**
   - Open http://localhost:3000/brainuse
   - Click "New Candidate"
   - Name: "Test Engineer"
   - Email: "test@example.com"
   - Role: "Senior Backend Engineer"
   - Company: "TestCorp"
   - Domains: Cloud, Leadership, API
   - Click "Create Candidate"

2. **Give Consent**
   - Click candidate card
   - Check "Candidate has given consent"
   - Consent recorded ✓

3. **Start Assessment**
   - Click "Start Assessment" (now enabled)
   - Status → "In Progress"

4. **Complete Assessment**
   - Click "Complete Assessment"
   - Metrics calculated
   - Toast shows Tao Index

5. **View Report**
   - Click "View Report"
   - See full assessment report
   - Print or save PDF

---

## Troubleshooting

### Database Connection Error

**Symptom:** "Database not initialized"

**Fix:**
```bash
# Restart services
docker compose restart

# Check PostgreSQL is healthy
docker compose ps postgres
```

### Port Already in Use

**Symptom:** "Bind for 0.0.0.0:3000 failed: port is already allocated"

**Fix:**
```bash
# Stop conflicting service
lsof -ti:3000 | xargs kill -9

# Or change port in docker-compose.yml
ports:
  - "3001:3000"  # Use 3001 instead
```

### Missing Benchmarks

**Symptom:** Reports show 0th percentile

**Fix:**
```bash
# Seed benchmarks
docker compose exec eeframe-app python -m tao.vetting.seed_benchmarks

# Verify seeded
docker compose exec postgres psql -U brainuse -d brainuse -c "SELECT COUNT(*) FROM benchmarks;"
# Should show: count = 8
```

### No Test Data

**Symptom:** "No history found for domain"

**Fix:**
```bash
# Generate test data
python3 scripts/synthesize_test_candidate.py \
  --candidate-name "Your Candidate Name"

# Verify files created
ls -lh universes/MINE/domains/cloud_assessment/query_history.json.gz
```

---

## Directory Structure

```
eeframe/
├── docker-compose.yml          # Service definitions
├── requirements.txt            # Python dependencies
├── tao/                        # Tao subsystem
│   ├── storage/                # Query history storage
│   ├── analysis/               # Learning analytics
│   └── vetting/                # BrainUse module
│       ├── models.py           # Data models
│       ├── database.py         # DB connection
│       ├── db_models.py        # ORM models
│       ├── candidate_manager.py
│       ├── benchmark_engine.py
│       ├── report_generator.py
│       ├── api_router.py       # REST API
│       ├── seed_benchmarks.py  # Benchmark seeding
│       └── frontend/           # Dashboard UI
├── universes/MINE/domains/     # Assessment domains
│   ├── cloud_assessment/
│   ├── leadership_assessment/
│   └── api_assessment/
├── data/personas/              # Librarian personas
│   ├── cloud_librarian.md
│   ├── leadership_librarian.md
│   └── api_librarian.md
└── scripts/
    └── synthesize_test_candidate.py
```

---

## Uninstall

```bash
# Stop and remove all containers
docker compose down

# Remove volumes (data will be lost!)
docker compose down -v

# Remove images
docker rmi $(docker images 'eeframe*' -q)
```

---

## Production Deployment

### Environment Variables

```bash
# Use strong passwords
POSTGRES_PASSWORD=<strong-random-password>

# Use production LLM
OPENAI_API_KEY=<production-key>
LLM_MODEL=gpt-4

# Set timezone
APP_TIMEZONE=America/New_York
```

### Database Backup

```bash
# Backup
docker compose exec postgres pg_dump -U brainuse brainuse > backup.sql

# Restore
cat backup.sql | docker compose exec -T postgres psql -U brainuse brainuse
```

### SSL/HTTPS

Use reverse proxy (nginx, Caddy, Traefik) for HTTPS.

Example nginx config:
```nginx
server {
    listen 443 ssl;
    server_name brainuse.company.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Updates

```bash
# Pull latest code
git pull

# Rebuild
docker compose down
docker compose up -d --build

# Database migrations (if any)
# TBD: Will use Alembic in future versions
```

---

## Support

- **Issues:** Check logs first: `docker compose logs -f eeframe-app`
- **Database:** Access with: `docker compose exec postgres psql -U brainuse -d brainuse`
- **API Docs:** http://localhost:3000/docs (FastAPI auto-docs)
- **Health Check:** http://localhost:3000/api/brainuse/health

---

## Summary

**Installation is 4 commands:**
```bash
git clone <repo>
cd eeframe
docker compose up -d --build
docker compose exec eeframe-app python -m tao.vetting.seed_benchmarks
```

**Access at:** http://localhost:3000/brainuse

**That's it!** 🚀
