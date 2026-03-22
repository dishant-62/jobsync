# JobSync - Job Platform API

A modern, async-first job platform API that crawls and aggregates job listings from multiple sources. Built with FastAPI, PostgreSQL, and Redis.

---

## 🚀 Quick Start - How to Run

### Fastest Way (Docker Compose - 2 minutes)

```bash
# Clone and navigate to project
git clone <repository-url>
cd JobSync

# Start all services
docker-compose up --build

# The API is now running at http://localhost:8000
```

✅ API: http://localhost:8000  
✅ Swagger Docs: http://localhost:8000/docs  
✅ PostgreSQL: localhost:5432  
✅ Redis: localhost:6379

**That's it!** Your job platform is running with all services configured.

### Quick Test Commands

```bash
# List all jobs
curl http://localhost:8000/jobs

# Search jobs
curl "http://localhost:8000/jobs?q=python"

# Health check
curl http://localhost:8000/health
```

### Want API Documentation?
Visit **http://localhost:8000/docs** in your browser for interactive Swagger documentation.

---

## 📖 Table of Contents

### Getting Started
- [🚀 Quick Start - How to Run](#-quick-start---how-to-run)
- [🔧 How to Setup (Detailed)](#-how-to-setup-detailed)

### Technical Documentation
- **[📚 Technical Details](#-technical-details)**
  - Overview
  - Technology Stack
  - System Architecture
  - Project Structure
  - API Endpoints Reference
  - Database Schema Design
  - Environment Configuration
  - Database Migrations
  - Data Crawlers & Pipelines
  - Bulk ATS Configuration System
  - Development & Testing
  - Structured Logging
  - API Usage Examples
  - Production Deployment
  - Troubleshooting & Support
  - Contributing & Development
  - Roadmap & Future Enhancements

### Configuration & Bulk Ingestion
- See [BULK_CONFIG_GUIDE.md](BULK_CONFIG_GUIDE.md) for comprehensive bulk ATS configuration documentation
- See [BULK_CONFIG_CHEATSHEET.md](BULK_CONFIG_CHEATSHEET.md) for quick reference commands
- See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for documentation navigation

---

## 🔧 How to Setup (Detailed)

### Prerequisites

**Option A: Docker (Recommended)**
- Docker and Docker Compose installed
- 4GB RAM available

**Option B: Local Development**
- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Poetry (Python package manager)

### Setup Option 1: Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd JobSync

# 2. Start all services (builds on first run)
docker-compose up --build

# Wait for messages:
# - "api | Application startup complete"
# - "postgres | database system is ready to accept connections"
# - "redis | Ready to accept connections"

# 3. Verify everything works
curl http://localhost:8000/health

# To stop services
docker-compose down
```

**What Docker Compose Sets Up:**
- PostgreSQL database with schemas
- Redis cache server
- FastAPI application server
- Automatic database migrations
- Health checks for all services

### Setup Option 2: Local Development

#### Step 1: Install Dependencies

```bash
# Install Poetry (Python package manager)
pip install poetry

# Clone repository
git clone <repository-url>
cd JobSync

# Install project dependencies
poetry install
```

#### Step 2: Configure Environment

```bash
# Create .env file from template
cp .env.example .env

# Edit .env with your local settings
# Typical local configuration:
# DATABASE_URL=postgresql+asyncpg://jobplatform:jobplatform@localhost:5432/jobplatform
# REDIS_URL=redis://localhost:6379/0
# ENVIRONMENT=development
# LOG_LEVEL=INFO
# JSON_LOGS=false
```

#### Step 3: Setup Database

```bash
# Make sure PostgreSQL is running
# Then run migrations
poetry run alembic upgrade head
```

#### Step 4: Start the Server

```bash
# Start FastAPI development server (auto-reloads on changes)
poetry run uvicorn job_platform.api.main:app --reload --host 0.0.0.0 --port 8000

# Server running at http://localhost:8000
```

### Verify Setup Works

After starting (either Docker or local), test these endpoints:

```bash
# Health check
curl http://localhost:8000/health

# List jobs
curl http://localhost:8000/jobs

# View API docs
open http://localhost:8000/docs
```

---

## 📚 Technical Details

### Overview

JobSync is designed to:
- **Fetch job listings** from Greenhouse-powered job boards via the Greenhouse Job Board API
- **Store jobs** in a PostgreSQL database with efficient indexing
- **Search and filter** jobs by title, description, and location
- **Cache results** using Redis for improved performance
- **Provide a REST API** for querying job listings
- **Track companies** and their associated job postings
- **Manage database migrations** with Alembic for easy version control

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Framework** | FastAPI | Modern, async Python web framework |
| **Database** | PostgreSQL 16 | Persistent job and company data storage |
| **Cache** | Redis 7 | Session caching and performance optimization |
| **ORM** | SQLAlchemy 2.0 | Async-compatible database abstraction |
| **Migrations** | Alembic | Database schema versioning |
| **HTTP Client** | httpx | Async HTTP requests to Greenhouse API |
| **Validation** | Pydantic | Data validation and serialization |
| **Logging** | structlog | Structured logging with JSON support |
| **Container** | Docker/Docker Compose | Containerization and orchestration |

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client / Frontend                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    FastAPI Server                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Job Routes (/jobs, /jobs/{id})               │ │
│  │  - List jobs (with search & pagination)                │ │
│  │  - Get individual job details                          │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────┐   ┌──────────┐   ┌──────────┐
   │Repository│  │ PostgreSQL│  │  Redis   │
   │ Pattern  │  │   Data    │  │  Cache   │
   └────────┘  └──────────┘  └──────────┘
   
┌─────────────────────────────────────────────────────────────┐
│           Crawler & Pipeline (Async Tasks)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Greenhouse Crawler: Fetch jobs from external boards  │ │
│  │  Pipeline: Transform, validate, and store in DB       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure & Organization

```
JobSync/
├── job_platform/              # Main application package
│   ├── api/                   # API endpoints
│   │   ├── main.py           # FastAPI app factory and configuration
│   │   ├── deps.py           # Dependency injection
│   │   └── routes/
│   │       └── jobs.py       # Job-related endpoints
│   ├── crawler/              # External data crawlers
│   │   └── greenhouse.py    # Greenhouse Job Board API crawler
│   ├── pipeline/            # Data processing pipelines
│   │   └── greenhouse_pipeline.py  # Greenhouse data ingestion
│   ├── db/                  # Database layer
│   │   ├── base.py         # SQLAlchemy declarative base
│   │   ├── models.py       # ORM models (Company, Job)
│   │   └── session.py      # Database session management
│   ├── repositories/        # Data access layer
│   │   ├── company.py      # Company CRUD operations
│   │   └── job.py          # Job CRUD operations
│   ├── schemas/            # Pydantic validation schemas
│   │   └── job.py          # Job request/response models
│   ├── utils/              # Utility functions
│   │   └── logging.py      # Logging configuration
│   └── config.py           # Application settings
├── alembic/                 # Database migrations
│   ├── versions/           # Migration files
│   │   ├── 0001_initial_companies_and_jobs.py
│   │   └── 0002_job_search_indexes.py
│   ├── env.py             # Alembic environment config
│   └── script.py.mako     # Migration template
├── Dockerfile             # Docker image specification
├── docker-compose.yml     # Multi-container orchestration
├── pyproject.toml        # Poetry project configuration
├── alembic.ini          # Alembic configuration
└── .env                 # Environment variables (not in repo)
```

### API Endpoints Reference

### Jobs
- **GET /jobs** - List all jobs with search and pagination
  - Query Parameters:
    - `q` (string, optional): Search in job title and description
    - `location` (string, optional): Filter by location
    - `limit` (integer, default=20, max=100): Results per page
    - `offset` (integer, default=0): Pagination offset
  - Response: `JobListResponse` with jobs array and total count

- **GET /jobs/{job_id}** - Get a single job by ID
  - Path Parameters:
    - `job_id` (UUID): Job identifier
  - Response: `JobRead` schema with full job details

### Health Check
- **GET /health** - Docker health check endpoint (implicit from FastAPI)

### Database Schema Design

### Companies Table
```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### Jobs Table
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    location VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    apply_url VARCHAR(2048) NOT NULL UNIQUE,
    posted_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    
    -- Indexes
    INDEX idx_company_id (company_id),
    INDEX idx_title (title),
    INDEX idx_location (location),
    FULLTEXT INDEX idx_search (title, description)
);
```

### Environment Configuration

The application is configured via environment variables (loaded from `.env` file):

```env
# Database connection (asyncpg + SQLAlchemy)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/jobplatform

# Redis cache (async client)
REDIS_URL=redis://localhost:6379/0

# Application environment
ENVIRONMENT=development  # or 'production'

# Logging
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
JSON_LOGS=false         # true for JSON output, false for colored console
```

### Default Values (in docker-compose.yml)
```yaml
PostgreSQL:
  Username: jobplatform
  Password: jobplatform
  Database: jobplatform
  Port: 5432

Redis:
  Port: 6379
  Database: 0

API:
  Port: 8000
```

### Database Migrations & Schema Management

### Why Alembic?
Alembic provides version-controlled database schema management, allowing safe and reversible database changes.

### Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description"

# Rollback to previous migration
alembic downgrade -1

# View migration history
alembic current
alembic history
```

### Existing Migrations
1. **0001_initial_companies_and_jobs.py**: Creates `companies` and `jobs` tables with relationships
2. **0002_job_search_indexes.py**: Adds indexes for search optimization

### Data Crawlers & Pipelines

### Greenhouse Crawler

**File:** [job_platform/crawler/greenhouse.py](job_platform/crawler/greenhouse.py)

Fetches jobs from Greenhouse-powered job boards:
- Uses the Greenhouse Job Board API: `https://boards-api.greenhouse.io/v1/boards/{company}/jobs`
- Handles pagination and retries with exponential backoff
- Parses job data: title, location, description, apply URL, posted date
- Async HTTP requests via `httpx`
- Timeout: 30 seconds (10s connection timeout)

```python
# Example usage
from job_platform.crawler.greenhouse import fetch_jobs

async def example():
    board_token = "your_company"
    jobs = await fetch_jobs(board_token)
    # Returns normalized job dictionaries
```

### Greenhouse Pipeline

**File:** [job_platform/pipeline/greenhouse_pipeline.py](job_platform/pipeline/greenhouse_pipeline.py)

Ingests Greenhouse jobs into the database:
- Validates and normalizes job data
- Handles duplicate detection (via unique `apply_url`)
- Associates jobs with companies
- Clips data to database column size limits
- Returns ingestion statistics

```python
# Example usage
from job_platform.pipeline.greenhouse_pipeline import run_greenhouse_pipeline

async def example():
    result = await run_greenhouse_pipeline("company-board-token")
    print(f"Inserted: {result.inserted}, Duplicates: {result.skipped_duplicates}")
```

### Bulk ATS Configuration System

JobSync includes a comprehensive bulk configuration management system for handling 20+ companies per ATS:

**Features:**
- Auto-generated SOURCES from company lists
- Automatic deduplication and validation
- CLI management interface (7 commands)
- Programmatic Python API
- Comprehensive testing (50+ tests)

**Current Configuration:**
- **Greenhouse**: 20 companies
- **Lever**: 10 companies  
- **Workday**: 5 companies
- **URL-based**: 3 aggregators
- **Total**: 38 sources

**Quick Start:**
```bash
# View configuration
python -m job_platform.crawler.sources config

# Add companies
python -m job_platform.crawler.sources add-companies greenhouse stripe airbnb

# Validate
python -m job_platform.crawler.sources validate
```

**Documentation:**
- [BULK_CONFIG_GUIDE.md](BULK_CONFIG_GUIDE.md) - Complete technical guide
- [BULK_CONFIG_CHEATSHEET.md](BULK_CONFIG_CHEATSHEET.md) - Quick reference
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Upgrade from old system
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) - Architecture & design
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - Navigation guide

### Development & Testing

### Project Dependencies (Poetry)

**Core:**
- `fastapi==0.115.0` - Async web framework
- `uvicorn==0.32.0` - ASGI server
- `sqlalchemy==2.0.36` - ORM with async support
- `asyncpg==0.30.0` - PostgreSQL async driver
- `pydantic==2.9.0` - Data validation
- `redis==5.2.0` - Redis async client
- `httpx==0.28.0` - Async HTTP client
- `structlog==24.4.0` - Structured logging
- `alembic==1.14.0` - Database migrations

**Development:**
- `pytest==8.3.0` - Testing framework
- `pytest-asyncio==0.24.0` - Async pytest support

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=job_platform

# Run specific test file
pytest tests/test_routes.py

# Run in watch mode
pytest-watch
```

### Code Style & Quality

```bash
# Format code
black job_platform/

# Run linter
pylint job_platform/

# Type checking
mypy job_platform/
```

### Structured Logging System

The application uses **structlog** for structured logging:

- **Development**: Colored console output with readable format
- **Production**: JSON format for easy parsing and aggregation

Configure via environment variables:
```env
LOG_LEVEL=DEBUG      # Increase verbosity
JSON_LOGS=true       # Enable JSON output
```

### API Usage Examples

### List All Jobs
```bash
curl "http://localhost:8000/jobs?limit=10&offset=0"
```

### Search Jobs
```bash
curl "http://localhost:8000/jobs?q=python&location=remote"
```

### Get Job Details
```bash
curl "http://localhost:8000/jobs/550e8400-e29b-41d4-a716-446655440000"
```

### Response Format
```json
{
  "jobs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "company_id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Senior Python Engineer",
      "location": "San Francisco, CA",
      "description": "We are looking for...",
      "apply_url": "https://example.greenhouse.io/jobs/123456",
      "posted_date": "2024-03-20",
      "created_at": "2024-03-22T10:30:00+00:00"
    }
  ],
  "total": 42
}
```

### Production Deployment & Operations

### Docker Compose Production

```bash
# Set production environment
export ENVIRONMENT=production
export JSON_LOGS=true

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api
```

### Health Checks
Docker automatically monitors service health:
- **API**: HTTP GET `/health` every 30s
- **PostgreSQL**: `pg_isready` check
- **Redis**: `PING` command

### Scaling Considerations
- Add Redis cluster for caching scale-out
- Configure PostgreSQL replication/backups
- Use load balancers for multiple API instances
- Implement job queue for crawler tasks (Celery, RQ, etc.)

### Troubleshooting & Support

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs postgres

# Verify connection string in .env
echo $DATABASE_URL
```

### Migration Failures
```bash
# Check current migration state
docker-compose exec api alembic current

# Downgrade to previous version if needed
docker-compose exec api alembic downgrade -1

# View migration history
docker-compose exec api alembic history
```

### Crawler Issues
- Verify Greenhouse board token is correct
- Check network connectivity to `boards-api.greenhouse.io`
- Monitor logs: `LOG_LEVEL=DEBUG`
- Ensure database and Redis are accessible

### Contributing & Development Workflow

### Development Workflow
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -m "Add feature"`
3. Write/update tests
4. Run tests and linting
5. Push and create a pull request

### Code Standards
- Follow PEP 8 style guide
- Use type hints for functions
- Write docstrings for modules, classes, and functions
- Keep functions small and focused
- Use async/await for I/O operations

## Roadmap & Future Enhancements

- [ ] Support for additional job board APIs (LinkedIn, Indeed, etc.)
- [ ] Job recommendation engine
- [ ] User authentication and saved jobs
- [ ] Email notifications for new jobs
- [ ] Advanced filtering and stored searches
- [ ] Analytics dashboard
- [ ] GraphQL API
- [ ] Test coverage improvement to 90%+

## License

[Specify your license - e.g., MIT]

## Support

For issues, questions, or suggestions, please open an issue on the repository or contact the maintainers.

---

**Last Updated**: March 22, 2026
