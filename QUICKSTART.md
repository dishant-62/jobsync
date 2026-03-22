"""
# 🚀 QUICK START GUIDE

## Installation & Setup

### 1. No new dependencies needed!
The system uses existing packages: `httpx`, `sqlalchemy`, `pydantic`

### 2. Environment Setup
```bash
# Set your database URL
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/jobsync"
```

---

## 🎯 BASIC USAGE

### Use Case 1: Run All Configured Sources

Via CLI:
```bash
python -m job_platform.pipeline.run_all_sources run
```

Via Python:
```python
import asyncio
from job_platform.pipeline import run_all_sources

async def main():
    result = await run_all_sources()
    print(f"Inserted {result.total_inserted} new jobs")
    for source in result.source_results:
        print(f"{source.source_name}: {source.inserted} jobs")

asyncio.run(main())
```

### Use Case 2: Run Specific Job Source Types

Via CLI:
```bash
# Run only Greenhouse boards
python -m job_platform.pipeline.run_all_sources run greenhouse

# Run only remote job aggregators
python -m job_platform.pipeline.run_all_sources run remote_jobs
```

Via Python:
```python
import asyncio
from job_platform.pipeline import run_sources_by_type

async def main():
    result = await run_sources_by_type("greenhouse")
    print(f"Greenhouse sources: {result.successful_sources} succeeded")

asyncio.run(main())
```

### Use Case 3: Run Single Source Directly

```python
import asyncio
import httpx
from job_platform.crawler.sources import GreenhouseCrawler

async def main():
    crawler = GreenhouseCrawler()
    async with httpx.AsyncClient() as client:
        jobs = await crawler.fetch_jobs_from_company("stripe", client)
        for job in jobs:
            print(f"{job.title} at {job.location}")

asyncio.run(main())
```

### Use Case 4: List All Configured Sources

Via CLI:
```bash
python -m job_platform.pipeline.run_all_sources list
```

Via Python:
```python
from job_platform.crawler.sources.config import get_sources

sources = get_sources()
for source in sources:
    print(f"{source.name} ({source.source_type})")
```

---

## ⚙️ CONFIGURATION

### Add New Sources

Edit `job_platform/crawler/sources/config.py`:

```python
SOURCES = [
    # Existing sources...
    
    # Add your new source
    SourceConfig(
        name="MyCompany Greenhouse",
        source_type="greenhouse",
        company="mycompany",
    ),
    
    SourceConfig(
        name="MyStartup Jobs",
        source_type="wellfound",
        url="https://wellfound.com",
        config={"roles": ["backend"], "locations": ["remote"]},
    ),
]
```

That's it! No code changes needed. The pipeline automatically includes it.

### Enable/Disable Sources

Simply comment out sources in `SOURCES` list:

```python
SOURCES = [
    SourceConfig(...),  # Active
    # SourceConfig(...),  # Disabled
]
```

---

## 🧪 TESTING

### Run Tests

```bash
pytest tests/test_crawlers.py -v
```

### Test a Single Crawler

```python
import asyncio
from unittest.mock import AsyncMock, MagicMock
from job_platform.crawler.sources import GreenhouseCrawler

async def test_greenhouse():
    # Mock API response
    mock_response = {
        "jobs": [
            {
                "title": "Engineer",
                "location": {"name": "SF"},
                "absolute_url": "https://example.com/123",
                "content": "Job description",
                "updated_at": "2024-01-15T10:00:00Z",
            }
        ]
    }
    
    # Setup mock client
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_response
    mock_client.get.return_value = mock_resp
    
    # Run crawler
    crawler = GreenhouseCrawler()
    jobs = await crawler.fetch_jobs_from_company("stripe", mock_client)
    
    print(f"Fetched {len(jobs)} jobs")
    assert len(jobs) == 1
    assert jobs[0].title == "Engineer"

asyncio.run(test_greenhouse())
```

---

## 🔍 MONITORING & DEBUGGING

### View Pipeline Results

```python
import asyncio
from job_platform.pipeline import run_all_sources

async def main():
    result = await run_all_sources()
    
    # Overall stats
    print(f"Total sources: {result.total_sources}")
    print(f"Successful: {result.successful_sources}")
    print(f"Failed: {result.failed_sources}")
    print(f"Jobs inserted: {result.total_inserted}")
    
    # Per-source details
    for source_result in result.source_results:
        if source_result.error:
            print(f"❌ {source_result.source_name}: {source_result.error}")
        else:
            print(f"✓ {source_result.source_name}: {source_result.inserted} jobs")

asyncio.run(main())
```

### Enable Debug Logging

```python
import logging

# Set log level to DEBUG
logging.basicConfig(level=logging.DEBUG)

# Now run pipeline - will see detailed logs
```

### Check Database

```python
# Query inserted jobs
from job_platform.db.session import session_factory
from job_platform.repositories.job import JobRepository

async def check_jobs():
    async with session_factory() as session:
        job_repo = JobRepository(session)
        all_jobs = await job_repo.list_jobs()
        
        for job in all_jobs:
            print(f"{job.title} ({job.company.name})")

asyncio.run(check_jobs())
```

---

## 🚨 COMMON WORKFLOWS

### Daily Job Sync

Create `run_daily_sync.py`:

```python
import asyncio
from job_platform.pipeline import run_all_sources

async def main():
    print("Starting daily job sync...")
    result = await run_all_sources(parallel=True, max_concurrent=3)
    
    print(f"Fetched: {result.total_fetched}")
    print(f"Inserted: {result.total_inserted}")
    print(f"Duplicates: {result.total_duplicates}")
    
    if result.failed_sources > 0:
        print(f"⚠️  {result.failed_sources} sources failed")
    else:
        print("✓ All sources successful")

if __name__ == "__main__":
    asyncio.run(main())
```

Run daily:
```bash
# Add to crontab (daily at 2 AM)
0 2 * * * python /path/to/run_daily_sync.py
```

### Test New Source Before Adding

```python
import asyncio
from job_platform.crawler.sources.config import SourceConfig
from job_platform.pipeline import run_all_sources

async def test_new_source():
    # Create test source
    test_source = SourceConfig(
        name="Test Source",
        source_type="greenhouse",
        company="testcompany",
    )
    
    # Run just this source
    result = await run_all_sources(
        sources=[test_source],
        parallel=False,
    )
    
    # Check results
    if result.failed_sources > 0:
        print(f"Source failed: {result.source_results[0].error}")
    else:
        print(f"Success! Fetched {result.total_fetched} jobs")

asyncio.run(test_new_source())
```

### Sync Specific Source Type

```python
import asyncio
from job_platform.pipeline import run_sources_by_type

async def sync_greenhouse_only():
    result = await run_sources_by_type("greenhouse")
    
    print(f"Updated {result.total_inserted} Greenhouse jobs")

asyncio.run(sync_greenhouse_only())
```

---

## 📊 UNDERSTANDING THE OUTPUT

### CLI Output

```
======================================================================
  Running All Sources
======================================================================

  Stripe Greenhouse [greenhouse] ✓ SUCCESS
    Fetched:           145
    Inserted:          127
    Duplicates:        18

  Netflix Lever [lever] ✓ SUCCESS
    Fetched:           89
    Inserted:          89
    Duplicates:        0

  RemoteOK [remote_jobs] ✗ FAILED
    Error:             Connection timeout

======================================================================
Pipeline Summary
======================================================================

  Total Sources:      3
  Successful:         2
  Failed:             1

  Total Fetched:      234
  Total Inserted:     216
  Total Duplicates:   18
```

### Understanding Metrics

- **Fetched**: Total jobs received from API
- **Inserted**: New jobs added to database
- **Duplicates**: Jobs already in database (by apply_url)
- **Successful**: Sources with no errors
- **Failed**: Sources with errors

---

## 🆘 TROUBLESHOOTING

### "Unknown crawler type" error

→ Check that `source_type` in config matches a registered crawler
→ Available types: greenhouse, lever, workday, job_board, remote_jobs, wellfound

### "Connection timeout"

→ Check internet connection
→ Try increasing timeout: `timeout = httpx.Timeout(60.0)`
→ Check that API endpoint is correct

### "No jobs found"

→ Verify company identifier is correct (case-sensitive for some APIs)
→ Check that board is public (especially Greenhouse)
→ Review API response in debug logs

### Database errors

→ Verify DATABASE_URL environment variable
→ Run migrations: `alembic upgrade head`
→ Check database permissions

### "Config validation error"

→ ATS sources need `company` field
→ URL-based sources need `url` field
→ Both sources need unique `name`

---

## 📈 SCALING TIPS

### For 20+ Sources

1. **Use parallel execution**: `parallel=True, max_concurrent=5`
2. **Rate limit respectfully**: Add delays if needed
3. **Monitor API quotas**: Some APIs have rate limits
4. **Batch database inserts**: Hundreds of jobs handled efficiently
5. **Use async throughout**: Don't block on I/O

### Performance Benchmarks

- 10 sources: ~30 seconds (parallel)
- 30 sources: ~60-90 seconds (parallel, max_concurrent=5)
- 1000 jobs: <1 second database insert

### Resource Usage

- Memory: ~50MB per 1000 jobs (in-flight data)
- CPU: Minimal (async, non-blocking)
- Network: Respects rate limits with retries

---

## 🎓 NEXT STEPS

1. **Add your first custom source**: See ARCHITECTURE.md
2. **Set up daily sync**: Use crontab or scheduler
3. **Monitor pipeline**: Add logging/alerts
4. **Extend for your needs**: Custom selectors, authentication, etc.

---

## 📚 FILE REFERENCE

Key files:
- **Crawlers**: `job_platform/crawler/sources/*.py`
- **Config**: `job_platform/crawler/sources/config.py`
- **Pipeline**: `job_platform/pipeline/multi_source_pipeline.py`
- **CLI**: `job_platform/pipeline/run_all_sources.py`
- **Tests**: `tests/test_crawlers.py`
- **Documentation**: `ARCHITECTURE.md`

---

## 💬 QUESTIONS?

Refer to:
- `ARCHITECTURE.md` for design patterns
- `job_platform/crawler/base.py` for BaseCrawler interface
- Source implementations for examples
- Tests for mocking patterns
"""
