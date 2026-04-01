# JobSync

> **Full-stack async job aggregation platform** — crawl, parse, rank, and browse jobs from Greenhouse, Lever, Workday, and more.

---

## Quick start

### Option A — Docker (all services in one command)

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| FastAPI (Python) | http://localhost:8000 |
| Swagger / OpenAPI | http://localhost:8000/docs |
| Auth server (Node.js) | http://localhost:4000 |
| Frontend (Vite) | http://localhost:5173 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

> The frontend dev server is **not** included in Docker — start it separately (step 5 below).

---

### Option B — Local development

#### Prerequisites

- Python 3.12+, [Poetry](https://python-poetry.org/)
- Node.js 18+, npm
- PostgreSQL 16 running locally (or use `docker-compose up postgres redis` to start only the databases)
- MongoDB (for the auth server)

#### 1. Clone and install Python dependencies

```bash
git clone https://github.com/dishant-62/jobsync.git
cd jobsync
pip install poetry
poetry install
```

#### 2. Configure the Python backend

Create a `.env` file in the repo root:

```env
DATABASE_URL=postgresql+asyncpg://jobplatform:jobplatform@localhost:5432/jobplatform
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
LOG_LEVEL=INFO
JSON_LOGS=false
```

#### 3. Run database migrations

```bash
poetry run alembic upgrade head
```

#### 4. Start the FastAPI server

```bash
poetry run uvicorn job_platform.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:5173` and proxies all `/api/v1` requests to the FastAPI backend.

#### 6. Start the auth server (Node.js)

Copy the example env file and fill in your credentials:

```bash
cd backend/auth
cp .env.example .env   # then edit .env
npm install
npm run dev            # starts on http://localhost:4000
```

Minimum required values in `backend/auth/.env`:

```env
PORT=4000
MONGODB_URI=mongodb://localhost:27017/jobsync
JWT_SECRET=<generate with: node -e "console.log(require('crypto').randomBytes(64).toString('hex'))">
FRONTEND_URL=http://localhost:5173
```

---

## What's in this repo

### Stack

| Layer | Technology |
|---|---|
| Python API | FastAPI, SQLAlchemy (async), Pydantic v2, Alembic |
| Database | PostgreSQL 16, Redis 7 |
| Auth server | Node.js, Express, Passport.js (Google + LinkedIn + local), MongoDB |
| Crawling | httpx async crawlers — Greenhouse, Lever, Workday, RemoteOK, WeWorkRemotely, Wellfound |
| Job parsing | Custom regex parser — skills, salary, experience level, remote detection |
| Frontend | React 18, React Router 7, TypeScript, Vite, Tailwind CSS, Axios |
| Tooling | Poetry, Docker Compose, pytest |

### API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `GET` | `/api/v1/jobs` | List jobs — supports `q`, `location`, `experience_level`, `is_remote`, `page`, `page_size` |
| `GET` | `/api/v1/jobs/{job_id}` | Job detail |
| `POST` | `/api/v1/jobs/{job_id}/save` | Save a job |
| `DELETE` | `/api/v1/jobs/{job_id}/save` | Unsave a job |
| `GET` | `/api/v1/saved-jobs` | List saved jobs |

### Auth endpoints (port 4000)

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Email / password registration |
| `POST` | `/auth/login` | Email / password login |
| `GET` | `/auth/google` | Google OAuth |
| `GET` | `/auth/linkedin` | LinkedIn OAuth |
| `GET` | `/auth/me` | Current user (JWT cookie) |
| `POST` | `/auth/logout` | Clear session cookie |

---

## Repo layout

```text
JobSync/
├── job_platform/               # Python FastAPI backend package
│   ├── api/                    # Routes, deps, app factory
│   ├── crawler/                # Crawler framework + source implementations
│   │   └── sources/            # Greenhouse, Lever, Workday, RemoteOK, Wellfound, job board
│   ├── db/                     # SQLAlchemy models, session, base
│   ├── models/domain/          # Pydantic domain models (RawJob → ParsedJob → FinalJob)
│   ├── parser/                 # Job description parser (skills, salary, remote, level)
│   ├── pipeline/               # Ingestion pipelines (crawler → scraper → DB)
│   ├── repositories/           # Data access layer (Job, Company, SavedJob)
│   ├── schemas/                # Pydantic API response schemas
│   ├── scraper/                # HTML normalizer / unified scraper
│   └── utils/                  # Logging, ranking, deterministic job IDs
├── backend/auth/               # Node.js Express auth server (JWT + OAuth)
│   ├── controllers/
│   ├── middleware/
│   ├── models/                 # Mongoose User, Resume
│   ├── routes/
│   └── config/                 # DB + Passport strategies
├── frontend/                   # React + Vite frontend (TypeScript)
│   └── src/
│       ├── api/                # Axios jobApi client
│       ├── components/         # Reusable UI components + index barrel
│       ├── context/            # AuthContext + useAuth hook
│       ├── hooks/              # Custom React hooks
│       ├── pages/              # Route-level pages
│       ├── services/           # Fetch-based API helpers + index barrel
│       └── types/              # Shared TypeScript interfaces
├── alembic/                    # PostgreSQL migration scripts
├── tests/                      # pytest unit tests (run by default)
│   └── integration/            # DB-dependent tests (need --integration flag)
├── scripts/                    # One-off maintenance and backfill scripts
├── docs/                       # Architecture and configuration guides
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

---

## Crawler pipeline

Run the full ingestion pipeline (all sources):

```bash
python -m job_platform.pipeline.run_all_sources run
```

Run a specific source:

```bash
python -m job_platform.pipeline.run_all_sources run greenhouse
python -m job_platform.pipeline.run_all_sources run lever
python -m job_platform.pipeline.run_all_sources run workday
```

List configured sources:

```bash
python -m job_platform.pipeline.run_all_sources list
```

Manage source configuration:

```bash
python -m job_platform.crawler.sources config      # view all sources
python -m job_platform.crawler.sources validate    # validate configuration
python -m job_platform.crawler.sources add-companies greenhouse stripe airbnb
python -m job_platform.crawler.sources remove-company greenhouse stripe
```

Run the extended crawler with 50+ companies:

```bash
python scripts/run_extended_crawler.py
```

---

## Tests

Run unit tests (no database required):

```bash
poetry run pytest
```

Run integration tests (requires a running PostgreSQL database):

```bash
poetry run pytest --integration tests/integration/
```

Run individual integration scripts directly:

```bash
python tests/integration/test_api_e2e.py
python tests/integration/test_job_ranking.py
python tests/integration/test_saved_jobs.py
```

---

## Maintenance scripts

These scripts live in `scripts/` and run against a live database:

```bash
# Generate job_id hashes for existing jobs (run once after migration)
python scripts/backfill_job_ids.py

# Calculate and store job scores for existing jobs
python scripts/backfill_job_scores.py

# Verify database connectivity and write access
python -m job_platform.test_insert

# Debug a Lever API endpoint
python scripts/check_lever.py
```

---

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — crawler design, adding new sources, pipeline architecture
- [docs/BULK_CONFIG_GUIDE.md](docs/BULK_CONFIG_GUIDE.md) — managing 20+ companies per ATS in bulk
