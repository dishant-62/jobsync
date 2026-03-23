FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.8.4

COPY pyproject.toml ./
# Copy poetry.lock if it exists, otherwise dependencies will be resolved from pyproject.toml
COPY poetry.lock* ./
COPY alembic.ini ./

RUN poetry install --no-ansi --only main --no-root \
    && rm -rf "$POETRY_CACHE_DIR"

COPY alembic ./alembic
COPY job_platform ./job_platform

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn job_platform.api.main:app --host 0.0.0.0 --port 8000"]
