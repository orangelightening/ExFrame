# EEFrame Development Guide

**Purpose**: Comprehensive guide for developers working on the EEFrame project, covering setup, workflow, testing, and deployment.

**Last Updated**: 2026-01-07
**Status**: Complete development environment with modern tooling

---

## Overview

EEFrame is a multi-system project with two main subsystems:

1. **OMV Co-Pilot**: AI-powered assistant for OpenMediaVault server management
2. **Expertise Scanner**: Pattern extraction and knowledge graph system for any domain

This guide covers development setup, workflow, testing, and deployment for both systems.

---

## Development Environment Setup

### Prerequisites

#### Core Requirements
- **Python**: 3.11+ (tested on 3.13.7)
- **Node.js**: 18+ (for frontend development)
- **Docker & Docker Compose**: For monitoring stack
- **Git**: Version control

#### Optional (for OMV Co-Pilot)
- **OpenMediaVault server**: For full functionality testing
- **GLM API key**: For LLM integration (or compatible LLM provider: OpenAI, Anthropic)

### Quick Setup

#### Using Setup Script
```bash
cd /home/peter/development/eeframe
./scripts/setup.sh  # Comprehensive environment setup
```

#### Manual Setup Steps

1. **Clone and navigate**:
   ```bash
   git clone <repository-url>
   cd eeframe
   ```

2. **Create Python virtual environment**:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development tools
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Start monitoring stack** (optional):
   ```bash
   docker-compose up -d
   ```

### Frontend Setup

#### OMV Co-Pilot Frontend:
```bash
cd /home/peter/development/eeframe/frontend
npm install
npm run dev  # Development server on port 3000
```

#### Expertise Scanner Frontend:
```bash
cd /home/peter/development/eeframe/expertise_scanner/frontend
npm install
npm run dev  # Development server on port 5173
```

### Environment Variables

Configure in `.env` file:

```bash
# OMV Server (OMV Co-Pilot only)
OMV_HOSTNAME=your-omv-server.local
OMV_USERNAME=admin
OMV_PASSWORD=your-password

# LLM Integration (all systems)
LLM_PROVIDER=GLM  # or OpenAI, Anthropic
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.z.ai/v1  # GLM international endpoint
LLM_MODEL=GLM-4.7

# Monitoring (OMV Co-Pilot)
MONITORING_PROMETHEUS_URL=http://localhost:9090
MONITORING_LOKI_URL=http://localhost:3100

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

---

## Project Structure

```
eeframe/
├── src/                          # Main Python source code
│   ├── omv_copilot/             # OMV Co-Pilot module
│   │   ├── api/                 # FastAPI endpoints (app.py, routes/)
│   │   ├── assist/              # LLM integration & prompts
│   │   ├── collectors/          # Data collectors (SSH, OMV RPC)
│   │   ├── knowledge/           # Knowledge base & pattern matching
│   │   ├── alerting/            # Smart alerting system
│   │   ├── cli/                 # Command line interface
│   │   ├── tracing/             # Execution tracing
│   │   └── settings.py          # Configuration management
│   ├── meta_expertise/          # Meta expertise framework
│   └── main.py                  # Main application entry point
├── expertise_scanner/            # Expertise Scanner subsystem
│   ├── src/                     # Python backend
│   │   ├── api/                 # FastAPI application
│   │   ├── extraction/          # Pattern extraction logic
│   │   ├── ingestion/           # Content ingestion pipeline
│   │   ├── knowledge/           # Knowledge graph management
│   │   └── storage/             # Data persistence
│   ├── frontend/                # React frontend (port 5173)
│   ├── data/                    # Pattern storage (JSON files)
│   └── config/                  # Scanner configuration
├── frontend/                     # OMV Co-Pilot React frontend (port 3000)
├── config/                       # Monitoring stack configurations
│   ├── prometheus/              # Prometheus configuration
│   ├── grafana/                 # Grafana dashboards
│   ├── loki/                    # Loki log aggregation
│   └── promtail/                # Promtail configuration
├── tests/                        # Test files
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── docs/                         # Documentation (this guide)
├── scripts/                      # Development scripts
├── patterns/                     # Manual pattern definitions (YAML)
├── data/                         # Runtime data storage
├── archive/                      # Archived code and experiments
└── docker-compose.yml           # Monitoring stack definition
```

---

## Development Workflow

### Code Quality Tools

Configured in `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = [
    "E", "W", "F",  # pycodestyle, pyflakes
    "I",            # isort
    "B",            # flake8-bugbear
    "C4",           # flake8-comprehensions
    "UP",           # pyupgrade
]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
strict = true
```

### Development Commands

#### Code Formatting and Linting
```bash
# Format code with Black
black src/

# Lint code with Ruff
ruff check src/
ruff check --fix src/  # Auto-fix where possible

# Type checking with MyPy
mypy src/
```

#### Testing
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run with verbose output
pytest -v tests/
```

#### Application Development
```bash
# Run OMV Co-Pilot API (development mode)
uvicorn omv_copilot.api.app:create_app --host 0.0.0.0 --port 8888 --reload

# Run Expertise Scanner API
cd expertise_scanner
uvicorn src.api.main:app --host 0.0.0.0 --port 8889 --reload

# Run OMV Co-Pilot CLI
python -m src.omv_copilot.cli.main --help
```

### Git Workflow

#### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical production fixes

#### Commit Guidelines
- Use descriptive commit messages
- Reference issues/tickets when applicable
- Keep commits focused and atomic
- Follow conventional commits format:
  ```
  feat: add new pattern ingestion endpoint
  fix: resolve CORS configuration issue
  docs: update API reference documentation
  refactor: simplify pattern matching logic
  test: add integration tests for OMV collector
  ```

---

## Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── omv_copilot/        # OMV Co-Pilot unit tests
│   └── expertise_scanner/   # Expertise Scanner unit tests
├── integration/             # Integration tests
│   ├── api/                # API endpoint tests
│   ├── collectors/         # Data collector tests
│   └── patterns/           # Pattern system tests
└── conftest.py             # Pytest configuration
```

### Writing Tests

#### Example Unit Test
```python
# tests/unit/omv_copilot/test_pattern_matching.py
import pytest
from src.omv_copilot.knowledge.pattern_matcher import PatternMatcher

def test_pattern_matcher_initialization():
    """Test pattern matcher initializes with empty patterns."""
    matcher = PatternMatcher()
    assert len(matcher.patterns) == 0
    assert matcher.initialized is False

def test_pattern_loading():
    """Test loading patterns from YAML file."""
    matcher = PatternMatcher()
    patterns = matcher.load_patterns("patterns/manual.yaml")
    assert len(patterns) > 0
    assert all("pattern_id" in p for p in patterns)
```

#### Example API Test
```python
# tests/integration/api/test_assist_endpoints.py
import pytest
from fastapi.testclient import TestClient

def test_query_endpoint(client: TestClient):
    """Test the assist/query endpoint."""
    response = client.post(
        "/api/v1/assist/query",
        json={"query": "Test query", "include_logs": False}
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "confidence" in data
    assert 0 <= data["confidence"] <= 1
```

### Test Configuration

Configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["src"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-ra",
]
markers = [
    "unit: unit tests",
    "integration: integration tests",
    "slow: tests that take a long time",
]
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific marker
pytest -m unit
pytest -m integration

# Run tests with coverage report
pytest --cov=src --cov-report=term --cov-report=html

# Run tests in parallel
pytest -n auto

# Run specific test file
pytest tests/unit/omv_copilot/test_pattern_matching.py

# Run specific test function
pytest tests/unit/omv_copilot/test_pattern_matching.py::test_pattern_loading
```

---

## Frontend Development

### OMV Co-Pilot Frontend

**Location**: `frontend/`
**Tech Stack**: React + Vite + TypeScript + Tailwind CSS

#### Development
```bash
cd frontend
npm install           # Install dependencies
npm run dev          # Start dev server (port 3000)
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # Lint code
npm run test         # Run tests
```

#### Key Files
- `frontend/vite.config.js`: Vite configuration
- `frontend/tailwind.config.js`: Tailwind CSS configuration
- `frontend/src/main.tsx`: Application entry point
- `frontend/src/App.tsx`: Main application component

### Expertise Scanner Frontend

**Location**: `expertise_scanner/frontend/`
**Tech Stack**: React + Vite + TypeScript + Tailwind CSS v3

#### Development
```bash
cd expertise_scanner/frontend
npm install
npm run dev          # Start dev server (port 5173)
npm run build
npm run preview
npm run lint
```

#### Key Features
- Pattern browser with filtering
- Domain overview pages
- Ingestion forms (URL, text, batch)
- Knowledge graph visualization
- Real-time ingestion progress tracking

---

## Monitoring Stack

### Docker Compose Services

File: `docker-compose.yml`

```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - ./config/grafana/provisioning:/etc/grafana/provisioning
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./config/loki:/etc/loki
      - loki_data:/loki
    command: -config.file=/etc/loki/config.yml

  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./config/promtail:/etc/promtail
      - /var/log:/var/log:ro
    command: -config.file=/etc/promtail/config.yml
```

### Management Commands
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
docker-compose logs -f prometheus  # Specific service

# Rebuild services
docker-compose up -d --build

# Check service status
docker-compose ps
```

### Access Points
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100

---

## Adding New Features

### Adding New API Endpoints

1. **Create route module** in appropriate directory:
   ```python
   # src/omv_copilot/api/routes/new_feature.py
   from fastapi import APIRouter, Depends
   from pydantic import BaseModel

   router = APIRouter(prefix="/new-feature", tags=["new-feature"])

   class NewFeatureRequest(BaseModel):
       param1: str
       param2: int

   @router.post("/")
   async def create_feature(request: NewFeatureRequest):
       """Create new feature."""
       # Implementation here
       return {"status": "created", "param1": request.param1}
   ```

2. **Register route** in main app:
   ```python
   # src/omv_copilot/api/app.py
   from .routes import new_feature

   app.include_router(new_feature.router)
   ```

3. **Add OpenAPI documentation** using docstrings and Pydantic models

4. **Write tests** in corresponding test directory

### Adding New Patterns

#### OMV Co-Pilot Patterns (YAML)
1. Edit `patterns/manual.yaml`
2. Add new pattern with unique `pattern_id`:
   ```yaml
   pattern_id: "omv-new-001"
   title: "New Pattern Title"
   category: "services"
   symptoms: ["symptom description"]
   diagnostics: [{name: "Check", command: "cmd", expected: "output"}]
   solutions: [{priority: 1, action: "Action", command: "cmd", explanation: "why"}]
   confidence: 0.85
   ```

#### Expertise Scanner Patterns (JSON/API)
1. Use API endpoint:
   ```bash
   curl -X POST http://localhost:8889/api/patterns \
     -H "Content-Type: application/json" \
     -d '{
       "domain": "cooking",
       "name": "New Pattern",
       "pattern_type": "procedure",
       "description": "...",
       "problem": "...",
       "solution": "..."
     }'
   ```

2. Or add directly to JSON file in `expertise_scanner/data/patterns/{domain}/`

### Adding New Domains (Expertise Scanner)

1. **Create domain configuration**:
   ```yaml
   # generic_framework/config/domains/new_domain.yaml
   domain:
     domain_id: "new_domain"
     domain_name: "New Domain"
     description: "Description of new domain"
     categories: ["category1", "category2"]
     pattern_storage_path: "/expertise_scanner/data/patterns/new_domain"
   ```

2. **Create pattern storage directory**:
   ```bash
   mkdir -p expertise_scanner/data/patterns/new_domain
   echo "[]" > expertise_scanner/data/patterns/new_domain/patterns.json
   ```

3. **Update domain registry** if applicable

---

## Code Standards

### Python Standards

#### Type Hints
```python
# Use type hints for all function signatures
def process_query(query: str, include_logs: bool = False) -> Dict[str, Any]:
    """Process a user query with optional log inclusion."""
    # Implementation
```

#### Docstrings
```python
def calculate_confidence(pattern: Pattern, symptoms: List[str]) -> float:
    """
    Calculate confidence score for pattern matching.

    Args:
        pattern: The pattern to evaluate
        symptoms: List of symptoms from user query

    Returns:
        Confidence score between 0.0 and 1.0

    Raises:
        ValueError: If pattern has invalid confidence value
    """
    # Implementation
```

#### Error Handling
```python
try:
    result = await external_api.call()
except APIConnectionError as e:
    logger.error(f"API connection failed: {e}")
    raise ServiceUnavailableError("External service unavailable") from e
except ValidationError as e:
    logger.warning(f"Validation error: {e}")
    raise
```

### Frontend Standards

#### React Components
```typescript
// Use TypeScript interfaces for props
interface PatternCardProps {
  pattern: Pattern;
  onSelect: (patternId: string) => void;
  isSelected: boolean;
}

// Functional components with hooks
const PatternCard: React.FC<PatternCardProps> = ({
  pattern,
  onSelect,
  isSelected,
}) => {
  // Component logic
  return (
    <div className={`pattern-card ${isSelected ? 'selected' : ''}`}>
      {/* JSX */}
    </div>
  );
};
```

#### State Management
- Use React hooks (`useState`, `useEffect`, `useContext`)
- Consider Zustand or similar for complex state
- Keep state as local as possible

---

## Debugging

### Python Debugging

#### Logging Configuration
```python
import logging

logger = logging.getLogger(__name__)

def complex_operation():
    logger.debug("Starting complex operation")
    try:
        result = perform_operation()
        logger.info(f"Operation completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        raise
```

#### Debugging with PDB
```python
import pdb

def problematic_function():
    # Set breakpoint
    pdb.set_trace()

    # Code execution will pause here
    result = calculate_value()

    # Use pdb commands: n (next), s (step), c (continue), p (print)
    return result
```

#### Debugging FastAPI Applications
```bash
# Run with debug mode
uvicorn app:app --reload --log-level debug

# Use debug middleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(debug=True)
```

### Frontend Debugging

#### Browser DevTools
- **React DevTools**: Component inspection
- **Redux DevTools**: State management debugging
- **Network tab**: API request inspection
- **Console**: JavaScript errors and logging

#### Debug Logging
```typescript
// Use console logging with levels
console.debug("Debug information:", data);
console.info("Informational message:", info);
console.warn("Warning:", warning);
console.error("Error occurred:", error);

// Conditional logging
if (process.env.NODE_ENV === 'development') {
  console.log("Debug info only in development");
}
```

---

## Performance Optimization

### Python Performance

#### Async/Await Pattern
```python
# Use async for I/O bound operations
async def fetch_multiple_sources(sources: List[str]) -> List[Dict]:
    tasks = [fetch_source(source) for source in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]
```

#### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param: str) -> Result:
    """Cache results of expensive calculations."""
    return perform_expensive_operation(param)
```

#### Database/File Optimization
- Use connection pooling for databases
- Implement pagination for large datasets
- Use streaming for large file operations

### Frontend Performance

#### Code Splitting
```typescript
// Dynamic imports for code splitting
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <HeavyComponent />
    </Suspense>
  );
}
```

#### Memoization
```typescript
// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }: Props) => {
  // Component implementation
});

// Use useMemo for expensive calculations
const processedData = useMemo(() => {
  return expensiveProcessing(data);
}, [data]);

// Use useCallback for stable function references
const handleClick = useCallback(() => {
  // Handler logic
}, [dependencies]);
```

---

## Deployment

### Development Deployment

#### Local Development Stack
```bash
# Start all services
./scripts/start-dev.sh

# Or start individually
docker-compose up -d                    # Monitoring stack
uvicorn omv_copilot.api.app:create_app --host 0.0.0.0 --port 8888 --reload
cd frontend && npm run dev             # OMV Co-Pilot frontend
cd expertise_scanner/frontend && npm run dev  # Expertise Scanner frontend
```

### Production Considerations

#### Security Hardening
- Use environment variables for secrets
- Implement proper authentication/authorization
- Configure CORS appropriately
- Enable HTTPS with valid certificates
- Set up rate limiting
- Implement request validation

#### Monitoring and Observability
- Enable application metrics export
- Set up centralized logging
- Configure health check endpoints
- Implement distributed tracing
- Set up alerting rules

#### Scaling Considerations
- Use production ASGI server (Uvicorn with workers)
- Implement database connection pooling
- Add caching layer (Redis)
- Consider load balancing for multiple instances
- Implement background task queue (Celery)

### Containerization

#### Dockerfile Example
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY patterns/ ./patterns/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV ENVIRONMENT=production

# Run application
CMD ["uvicorn", "omv_copilot.api.app:create_app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Docker Compose for Production
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
```

---

## Troubleshooting

### Common Issues

#### Python Import Errors
```bash
# Ensure Python path is set
export PYTHONPATH=/home/peter/development/eeframe/src:$PYTHONPATH

# Or install in development mode
pip install -e .
```

#### Missing Dependencies
```bash
# Reinstall all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Clear pip cache if needed
pip cache purge
```

#### Docker Issues
```bash
# Check Docker service status
sudo systemctl status docker

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Clean up unused resources
docker system prune -a
```

#### Frontend Build Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+

# Clear build cache
npm run clean  # If available
rm -rf dist/ build/
```

#### Database/File Permission Issues
```bash
# Check directory permissions
ls -la data/

# Fix permissions if needed
chmod -R 755 data/
chown -R $(whoami) data/
```

### Debugging Tools

#### Python Debugging
```bash
# Run with debug logging
python -m src.main --debug

# Use Python debugger
python -m pdb -m src.main

# Profile performance
python -m cProfile -o profile.stats src/main.py
```

#### Network Debugging
```bash
# Check API endpoints
curl http://localhost:8888/health
curl http://localhost:8889/api/patterns?limit=1

# Check Docker services
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3001/api/health  # Grafana

# Check network connectivity
nc -zv localhost 8888
nc -zv localhost 8889
```

#### Log Inspection
```bash
# View application logs
tail -f logs/app.log

# View Docker logs
docker-compose logs -f app
docker-compose logs -f prometheus

# View system logs
journalctl -u docker.service -f
```

---

## Contributing

### Contribution Process

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make changes**: Follow code standards and write tests
4. **Run tests**: Ensure all tests pass
5. **Commit changes**: Use descriptive commit messages
6. **Push to branch**: `git push origin feature/new-feature`
7. **Create Pull Request**: Describe changes and link issues

### Code Review Checklist

- [ ] Code follows project standards
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced
- [ ] Performance implications considered
- [ ] Backward compatibility maintained

### Issue Reporting

When reporting issues, include:
- **Description**: Clear problem description
- **Steps to reproduce**: Specific steps to trigger the issue
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, dependencies
- **Logs**: Relevant error messages or logs
- **Screenshots**: If applicable

---

## Resources

### Documentation
- `docs/01-system-architecture.md`: System architecture
- `docs/02-omv-co-pilot-guide.md`: OMV Co-Pilot guide
- `docs/03-expertise-scanner-guide.md`: Expertise Scanner guide
- `docs/04-state-machines.md`: State machine documentation
- `docs/05-api-reference.md`: API reference
- `docs/06-pattern-catalog.md`: Pattern catalog
- `README.md`: Project overview and quick start

### External Resources
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **Python Documentation**: https://docs.python.org/3/
- **Docker Documentation**: https://docs.docker.com/
- **Tailwind CSS Documentation**: https://tailwindcss.com/

### Development Tools
- **Black**: Python code formatter
- **Ruff**: Python linter
- **MyPy**: Python type checker
- **Pytest**: Python testing framework
- **ESLint**: JavaScript/TypeScript linter
- **Prettier**: Code formatter

---

## Getting Help

### Internal Channels
- Project documentation (this guide)
- Code comments and docstrings
- Test examples
- Existing implementation patterns

### External Support
- Framework documentation (FastAPI, React, etc.)
- Stack Overflow for specific issues
- GitHub Issues for bug reports
- Community forums for related technologies

### Emergency Contact
For critical production issues, follow escalation procedures documented in operations guide.

---

## Summary

This development guide provides comprehensive instructions for setting up, developing, testing, and deploying the EEFrame project. The project uses modern development practices with proper tooling, testing, and documentation to ensure maintainable and reliable code.

Key takeaways:
1. **Use the virtual environment** for Python development
2. **Follow code standards** with Black, Ruff, and MyPy
3. **Write tests** for all new functionality
4. **Document changes** in code and documentation
5. **Use development scripts** for common tasks
6. **Monitor application health** with the provided stack

Happy coding!