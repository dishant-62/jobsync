# JobSync

JobSync is an async job aggregation platform with three active layers:

- a FastAPI backend that serves versioned job APIs
- a multi-source ingestion pipeline for Greenhouse, Lever, Workday, job boards, and aggregators
- a React and Vite frontend for browsing jobs and saved jobs

## Latest update

- Added saved-job API routes and frontend pages for saved listings
- Standardized API access under `/api/v1`
- Expanded multi-source crawler configuration and pipeline CLI support
- Added a manual database verification script at `python -m job_platform.test_insert`

## Current stack

- Backend: FastAPI, SQLAlchemy asyncio, Pydantic, Alembic
- Data: PostgreSQL, Redis
- Crawling: httpx-based async crawlers with a unified pipeline
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Tooling: Poetry, Docker Compose, pytest

## Repo layout

```text
JobSync/
|- job_platform/
|  |- api/
|  |- crawler/
|  |- db/
|  |- parser/
|  |- pipeline/
|  |- repositories/
|  |- schemas/
|  \- test_insert.py
|- _frontend/
|- alembic/
|- docker-compose.yml
\- README.md
```

## Backend features

- `GET /health` for service health
- `GET /api/v1/jobs` with pagination and filters for query, location, experience level, and remote jobs
- `GET /api/v1/jobs/{job_id}` for job details
- `POST /api/v1/jobs/{job_id}/save` and `DELETE /api/v1/jobs/{job_id}/save` for saved jobs
- `GET /api/v1/saved-jobs` for the current saved-job list

## Run with Docker

```bash
docker-compose up --build
```

Services:

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Frontend dev server: run separately from `_frontend`
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Run locally

### 1. Install backend dependencies

```bash
pip install poetry
poetry install
```

### 2. Configure environment

Create a `.env` file in the repo root:

```env
DATABASE_URL=postgresql+asyncpg://jobplatform:jobplatform@localhost:5432/jobplatform
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
LOG_LEVEL=INFO
JSON_LOGS=false
```

### 3. Apply migrations

```bash
poetry run alembic upgrade head
```

### 4. Start the API

```bash
poetry run uvicorn job_platform.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start the frontend

```bash
cd _frontend
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:5173` and proxies `/api/v1` requests to the backend.

## Pipeline commands

```bash
python -m job_platform.pipeline.run_all_sources run
python -m job_platform.pipeline.run_all_sources run greenhouse
python -m job_platform.pipeline.run_all_sources list
python -m job_platform.crawler.sources config
python -m job_platform.crawler.sources validate
```

## Database verification

Use the built-in verification script when you want to confirm connectivity and write access:

```bash
python -m job_platform.test_insert
```

It masks the configured database URL, checks required tables, inserts a temporary job and company, verifies the write, and then removes the test records.

## Tests

```bash
poetry run pytest
```

## Documentation kept in this repo

- [ARCHITECTURE.md](ARCHITECTURE.md) for the crawler and pipeline design
- [BULK_CONFIG_GUIDE.md](BULK_CONFIG_GUIDE.md) for managing source configuration in bulk