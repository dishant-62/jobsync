"""
# 🏗️ SCALABLE JOB AGGREGATION ARCHITECTURE

## Overview

This document describes the scalable, modular architecture for aggregating jobs from 20+ sources with minimal code duplication and easy extensibility.

## 🎯 Architecture Principles

1. **No Hardcoding**: Each source is configured once, then reused
2. **Type-Based Grouping**: Crawlers grouped by behavior (ATS, job board, aggregator)
3. **Unified Interface**: All crawlers return the same `NormalizedJob` format
4. **Async-First**: Full async/await support for concurrency
5. **Error Resilience**: One source failure doesn't stop others
6. **Clean Separation**: Configuration, implementation, and orchestration separated

---

## 🏛️ ARCHITECTURE COMPONENTS

### 1. **BaseCrawler** (`job_platform/crawler/base.py`)

Abstract base class defining the crawler interface.

```python
class BaseCrawler(ABC):
    async def fetch_jobs_from_company(company: str, client) -> list[NormalizedJob]
    async def fetch_jobs_from_url(url: str, client, **kwargs) -> list[NormalizedJob]
```

**Supports two patterns:**
- **Company-based** (ATS): Greenhouse, Lever, Workday → fetch by company identifier
- **URL-based** (Job boards): RemoteOK, WeWorkRemotely → fetch from any URL

### 2. **Crawler Implementations** (`job_platform/crawler/sources/`)

#### **GreenhouseCrawler** (`greenhouse.py`)
- Public board API: `https://boards-api.greenhouse.io/v1/boards/{company}/jobs`
- Company-based fetching
- Extracts: title, location, absolute_url, content, updated_at

#### **LeverCrawler** (`lever.py`)
- Public API: `https://api.lever.co/v0/postings/{company}`
- Company-based fetching
- Extracts: text, categories, description, hostedUrl, createdAt

#### **WorkdayCrawler** (`workday.py`)
- Pattern: `https://{company}.myworkdayjobs.com/en-US/`
- Company-based fetching
- Extracts: title, description, jobPostingUrl, location fields

#### **RemoteJobsCrawler** (`remote_jobs.py`)
- **RemoteOK**: JSON API at `https://remoteok.com/api`
- **WeWorkRemotely**: HTML parsing with selectors
- URL-based fetching

#### **JobBoardCrawler** (`job_board.py`)
- Generic crawler for any job board with CSS selectors
- URL-based fetching with configurable selectors
- Template for BeautifulSoup integration

#### **WellfoundCrawler** (`wellfound.py`)
- Startup jobs: `https://api.wellfound.com/v1/jobs`
- Both company and URL-based modes
- Extracts: title, description, locations, startup details

### 3. **NormalizedJob** (`job_platform/crawler/base.py`)

Unified job format from all crawlers:

```python
@dataclass
class NormalizedJob:
    title: str
    location: str
    apply_url: str
    description: str
    posted_date: datetime
    company_name: str
```

### 4. **Source Configuration** (`job_platform/crawler/sources/config.py`)

Centralized configuration for all sources:

```python
@dataclass
class SourceConfig:
    name: str                          # Human name
    source_type: str                   # Crawler type
    company: str | None                # For ATS
    url: str | None                    # For job boards
    selectors: dict[str, str]          # CSS selectors (if needed)
    config: dict[str, Any]             # Extra options

# Usage
SOURCES = [
    SourceConfig("Stripe Greenhouse", "greenhouse", company="stripe"),
    SourceConfig("Netflix Lever", "lever", company="netflix"),
    SourceConfig("RemoteOK", "remote_jobs", url="https://remoteok.com"),
]
```

### 5. **Crawler Registry** (`job_platform/crawler/sources/registry.py`)

Maps crawler types to implementations:

```python
registry = CrawlerRegistry()
crawler = registry.get("greenhouse")  # Returns GreenhouseCrawler instance
```

### 6. **Unified Pipeline** (`job_platform/pipeline/multi_source_pipeline.py`)

Orchestrates fetching and inserting from all sources:

```python
# Run all sources in parallel
result = await run_all_sources(parallel=True, max_concurrent=3)

# Run by type
result = await run_sources_by_type("greenhouse")

# Result includes:
# - total_fetched, total_inserted, total_duplicates
# - per-source error tracking
```

### 7. **CLI Runner** (`job_platform/pipeline/run_all_sources.py`)

Command-line interface for running the pipeline:

```bash
# Run all sources
python -m job_platform.pipeline.run_all_sources run

# Run specific type
python -m job_platform.pipeline.run_all_sources run greenhouse

# List configured sources
python -m job_platform.pipeline.run_all_sources list
```

---

## 🚀 ADDING A NEW CRAWLER (Complete Example)

### Step 1: Create Crawler Class

Create `job_platform/crawler/sources/my_source.py`:

```python
from job_platform.crawler.base import BaseCrawler, NormalizedJob
import httpx

class MySourceCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("my_source")
    
    async def fetch_jobs_from_url(self, url, client, **kwargs):
        # Call your API
        response = await client.get(url)
        jobs = response.json()
        
        # Normalize each job
        normalized = []
        for job in jobs:
            normalized_job = NormalizedJob(
                title=job["title"],
                location=job["location"],
                apply_url=job["url"],
                description=job["description"],
                posted_date=datetime.fromisoformat(job["posted_date"]),
                company_name=job.get("company", "My Source")
            )
            if self._validate_normalized_job(normalized_job):
                normalized.append(normalized_job)
        
        return normalized
```

### Step 2: Register Crawler

Update `job_platform/crawler/sources/__init__.py`:

```python
from job_platform.crawler.sources.my_source import MySourceCrawler

__all__ = [..., "MySourceCrawler"]
```

### Step 3: Update Registry

Auto-registered if following naming convention, or manually add to `registry.py`:

```python
self._crawlers["my_source"] = MySourceCrawler()
```

### Step 4: Add to Configuration

Update `job_platform/crawler/sources/config.py`:

```python
SOURCES = [
    ...,
    SourceConfig(
        name="My Source Jobs",
        source_type="my_source",
        url="https://mysource.com/api/jobs",
        config={"limit": 100}
    )
]
```

### Step 5: Done!

The crawler is now included in:
- `python -m job_platform.pipeline.run_all_sources run`
- Parallel execution with error handling
- Database insertion with deduplication

---

## 📊 DATA FLOW

```
┌─────────────────┐
│   SOURCES       │
│  Configuration  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│   CrawlerRegistry   │  (Maps type → crawler)
└────────┬────────────┘
         │
         ▼
┌───────────────────────────────────────┐
│   MultiSourcePipeline                 │
│  1. Iterate over SOURCES              │
│  2. Get crawler by type               │
│  3. Fetch jobs (company or URL)       │
│  4. Normalize to unified schema       │
│  5. Check for duplicates              │
│  6. Insert into database              │
│  7. Log errors per source             │
└────────┬────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│    Database      │
│  Companies/Jobs  │
└──────────────────┘
```

---

## 🔄 EXECUTION MODES

### Sequential
```python
result = await run_all_sources(parallel=False)
```
- One source at a time
- Simpler debugging
- Slower overall

### Parallel (Default)
```python
result = await run_all_sources(parallel=True, max_concurrent=3)
```
- Max 3 concurrent sources
- Better throughput
- Respects API rate limits

### By Type
```python
result = await run_sources_by_type("greenhouse")
```
- Run only Greenhouse sources
- Useful for testing/debugging

---

## 🛡️ ERROR HANDLING

**Per-Source Isolation:**
- One failing source doesn't stop others
- Errors logged with source context
- Returned in result for visibility

```python
result = await run_all_sources()

for source_result in result.source_results:
    if source_result.error:
        print(f"Error in {source_result.source_name}: {source_result.error}")
```

**Retry Logic:**
- Built into each crawler
- Exponential backoff on transient errors (5xx, 429)
- 3 attempts by default

---

## 📈 SCALING TO 20+ SOURCES

**Supported patterns:**
1. **Public ATS Boards**: Greenhouse, Lever, Workday, etc.
2. **JSON APIs**: RemoteOK, Wellfound, etc.
3. **HTML Scrapers**: Generic job boards with CSS selectors
4. **Authentication**: API tokens in config

**Example: Add 10 more sources in ~10 minutes:**

```python
SOURCES = [
    # Just add one line per source
    SourceConfig("Company1 Greenhouse", "greenhouse", company="company1"),
    SourceConfig("Company2 Lever", "lever", company="company2"),
    SourceConfig("JobBoard1", "job_board", url="https://jobs1.com"),
    # ... 7 more lines
]
```

No new crawler code needed for similar source types.

---

## 🧪 TESTING

**Unit tests with mocks:**

```bash
pytest tests/test_crawlers.py -v
```

Tests include:
- Crawler functionality (normalized jobs)
- API error handling
- Job validation
- Config validation
- Registry retrieval

**Mock API responses in tests:**

```python
@pytest.mark.asyncio
async def test_fetch_jobs():
    mock_response = {"jobs": [...]}
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=MagicMock(json=Mock(...)))
    
    crawler = GreenhouseCrawler()
    jobs = await crawler.fetch_jobs_from_company("stripe", mock_client)
    
    assert len(jobs) > 0
```

---

## 🔧 CONFIGURATION EXTENSION

Add source-specific options in `SourceConfig.config`:

```python
SourceConfig(
    name="RemoteOK (Tech only)",
    source_type="remote_jobs",
    url="https://remoteok.com",
    config={
        "category": "tech",
        "limit": 100,
        "min_salary": 100000,
    }
)
```

Pass to crawler via kwargs:
```python
jobs = await crawler.fetch_jobs_from_url(url, client, **source.config)
```

---

## 📦 DEPENDENCIES

- `httpx`: Async HTTP client
- `SQLAlchemy`: Async ORM
- `pydantic`: Validation
- `pytest`: Testing (optional)

---

## 🎓 KEY DESIGN PATTERNS

1. **Template Method**: BaseCrawler defines interface
2. **Strategy**: Each crawler implements different fetching logic
3. **Registry**: Mapping of types to instances
4. **Factory**: Registry creates crawlers
5. **Decorator**: Async wrappers with retries
6. **Dataclass**: Configuration objects

---

## 🚨 COMMON GOTCHAS

**1. Missing validation**
```python
# ❌ Bad: Not validating job before returning
return NormalizedJob(...)

# ✅ Good: Validate before returning
if self._validate_normalized_job(job):
    return job
```

**2. Incorrect timezone handling**
```python
# ❌ Bad: Naive datetime
dt = datetime.fromisoformat(str_date)

# ✅ Good: Timezone-aware
dt = datetime.fromisoformat(str_date).replace(tzinfo=UTC)
```

**3. Hardcoded API endpoints**
```python
# ❌ Bad: Limited to one endpoint
URL = "https://api.example.com/jobs"

# ✅ Good: Configurable
url = f"https://{company}.myworkdayjobs.com/api"
```

**4. Not catching exceptions**
```python
# ❌ Bad: Pipeline crashes on one source error
await crawler.fetch_jobs(...)

# ✅ Good: Graceful error handling
try:
    jobs = await crawler.fetch_jobs(...)
except Exception as e:
    logger.error(f"Error: {e}")
    return []
```

---

## 📚 Additional Resources

- `job_platform/crawler/base.py`: BaseCrawler abstract class
- `job_platform/crawler/sources/`: Concrete crawler implementations
- `job_platform/pipeline/multi_source_pipeline.py`: Orchestration logic
- `tests/test_crawlers.py`: Example tests and mocking patterns
"""

# This is documentation only - not executable code
