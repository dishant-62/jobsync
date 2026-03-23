"""
# ✅ GETTING STARTED CHECKLIST

## Phase 1: Understand the System (30 minutes)

- [ ] Read this file (5 min)
- [ ] Skim `IMPLEMENTATION_SUMMARY.md` (10 min)
- [ ] Look at `PROJECT_STRUCTURE.md` directory layout (5 min)
- [ ] Glance at `crawler/sources/config.py` to see example sources (5 min)

**Reading Order for Deeper Understanding:**
1. `IMPLEMENTATION_SUMMARY.md` - Get the big picture
2. `PROJECT_STRUCTURE.md` - Understand file organization
3. `ARCHITECTURE.md` - Learn design patterns
4. `QUICKSTART.md` - See usage examples

---

## Phase 2: Set Up Environment (10 minutes)

- [ ] Ensure `DATABASE_URL` is set in `.env`
  ```bash
  export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/jobsync"
  ```

- [ ] Verify dependencies are installed
  ```bash
  pip install httpx sqlalchemy pydantic
  ```

- [ ] Run database migrations (if needed)
  ```bash
  alembic upgrade head
  ```

---

## Phase 3: List Available Sources (2 minutes)

- [ ] Run CLI command to see what's configured
  ```bash
  python -m job_platform.pipeline.run_all_sources list
  ```
  
Expected output shows sources like:
```
1. Stripe Greenhouse
2. Netflix Lever
3. RemoteOK Jobs
...
```

---

## Phase 4: Run Your First Pipeline (5 minutes)

### Option A: Run All Sources (Parallel)
```bash
python -m job_platform.pipeline.run_all_sources run
```

Wait for completion, then check output:
```
======================================================================
Pipeline Summary
======================================================================

  Total Sources:      8
  Successful:         7
  Failed:             1

  Total Fetched:      312
  Total Inserted:     287
  Total Duplicates:   25
```

### Option B: Run Specific Source Type
```bash
# Just Greenhouse sources
python -m job_platform.pipeline.run_all_sources run greenhouse

# Just remote job aggregators
python -m job_platform.pipeline.run_all_sources run remote_jobs
```

### Option C: Run via Python
```python
import asyncio
from job_platform.pipeline import run_all_sources

async def main():
    result = await run_all_sources()
    print(f"✓ Inserted {result.total_inserted} new jobs")

asyncio.run(main())
```

---

## Phase 5: Verify Results in Database (5 minutes)

```python
import asyncio
from job_platform.db.session import session_factory
from job_platform.repositories.job import JobRepository

async def check():
    async with session_factory() as session:
        repo = JobRepository(session)
        jobs = await repo.list_jobs()
        for job in jobs[:5]:  # First 5
            print(f"{job.title} @ {job.company.name}")

asyncio.run(check())
```

---

## Phase 6: Add Your First Custom Source (15 minutes)

### Step 1: Find a source you want to add
Example: Add your company's Greenhouse board

### Step 2: Edit `crawler/sources/config.py`
```python
SOURCES = [
    # ... existing sources ...
    
    # Add your source (just 1 line!)
    SourceConfig(
        name="YourCompany Greenhouse",
        source_type="greenhouse",
        company="yourcompany",
    ),
]
```

### Step 3: Verify board is public
- Go to: `https://boards.greenhouse.io/yourcompany`
- If it works, your board token is "yourcompany" ✓

### Step 4: Test it!
```bash
python -m job_platform.pipeline.run_all_sources run greenhouse
```

### Step 5: Check results
- How many jobs were fetched?
- How many were inserted?
- Any errors?

---

## Phase 7: Run Tests (5 minutes)

```bash
pytest tests/test_crawlers.py -v
```

You should see:
```
test_crawlers.py::TestNormalizedJob::test_normalized_job_creation PASSED
test_crawlers.py::TestGreenhouseCrawler::test_fetch_jobs_from_company PASSED
test_crawlers.py::TestLeverCrawler::test_fetch_jobs_from_company PASSED
...
```

If all pass: ✓ System is working!

---

## Phase 8: Schedule Daily Runs (Optional, 10 minutes)

### Option A: Using crontab
```bash
# Add to crontab (runs every 4 hours)
0 */4 * * * cd /path/to/jobsync && python -m job_platform.pipeline.run_all_sources run >> /var/log/jobsync.log 2>&1
```

### Option B: Using systemd timer
Create `/etc/systemd/system/jobsync.service`:
```ini
[Unit]
Description=JobSync Pipeline
After=network.target

[Service]
Type=oneshot
User=jobsync
WorkingDirectory=/path/to/jobsync
ExecStart=/usr/bin/python -m job_platform.pipeline.run_all_sources run
Environment="DATABASE_URL=postgresql+asyncpg://..."
```

Then create `/etc/systemd/system/jobsync.timer`:
```ini
[Unit]
Description=JobSync Pipeline Timer

[Timer]
OnBootSec=10min
OnUnitActiveSec=4h
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable jobsync.timer
sudo systemctl start jobsync.timer
```

---

## Phase 9: Monitor & Debug (As Needed)

### View Recent Errors
```python
import asyncio
from job_platform.pipeline import run_all_sources

async def check_errors():
    result = await run_all_sources()
    for src in result.source_results:
        if src.error:
            print(f"❌ {src.source_name}: {src.error}")

asyncio.run(check_errors())
```

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run pipeline - you'll see detailed debug output
```

### Check Specific Crawler
```python
# Test just one source
from job_platform.crawler.sources.config import SourceConfig
from job_platform.pipeline import run_all_sources

test_source = SourceConfig(
    "Test",
    "greenhouse",
    company="testcompany"
)

result = await run_all_sources(sources=[test_source], parallel=False)
```

---

## Phase 10: Extend to Production (30 minutes to 1 hour)

### Setup Monitoring
```python
# log_pipeline_metrics.py
import asyncio
from job_platform.pipeline import run_all_sources

async def run_and_monitor():
    result = await run_all_sources()
    
    # Send to your monitoring service
    send_metric("jobsync.total_inserted", result.total_inserted)
    send_metric("jobsync.sources_failed", result.failed_sources)
    send_metric("jobsync.total_fetched", result.total_fetched)
    
    if result.failed_sources > 0:
        send_alert(f"JobSync: {result.failed_sources} sources failed!")

asyncio.run(run_and_monitor())
```

### Setup Backups
```bash
# Backup job database weekly
0 0 * * 0 pg_dump $DATABASE_URL | gzip > /backups/jobsync-$(date +%Y%m%d).sql.gz
```

### Document Configuration
```markdown
# JobSync Configuration

## Active Sources
- Greenhouse: stripe, airbnb, figma
- Lever: netflix, notion
- Remote: remoteok.com, weworkremotely.com

## Schedule
- Runs every 4 hours
- Approximately 5-10 minutes per run
- ~200-300 new jobs per day

## Contacts
- Alert to: #jobs-stream in Slack
- On-call: @platform-team
```

---

## SUCCESS CRITERIA

✅ You've completed setup when:

1. **List Command Works**
   ```bash
   python -m job_platform.pipeline.run_all_sources list
   # Shows your sources
   ```

2. **Pipeline Runs Successfully**
   ```bash
   python -m job_platform.pipeline.run_all_sources run
   # Completes with results
   ```

3. **Jobs in Database**
   - Database has Company records
   - Database has Job records
   - Verified via Python query

4. **Custom Source Added**
   - Config updated with your company
   - Pipeline runs without errors
   - Jobs appear in database

5. **Tests Pass**
   ```bash
   pytest tests/test_crawlers.py -v
   # All pass
   ```

6. **You Can Answer:**
   - "How do I add a new source?" → Edit config.py
   - "How do I run the pipeline?" → python -m pipeline.run_all_sources
   - "What crawlers are supported?" → greenhouse, lever, workday, etc.
   - "How do I debug a crawler?" → Check logs, look at tests

---

## COMMON ISSUES & SOLUTIONS

### Issue: "Unknown crawler type: greenhouse"
**Solution:** 
- Check `crawler/sources/config.py` source_type is correct
- Verify source_type is one of: greenhouse, lever, workday, job_board, remote_jobs, wellfound

### Issue: "Connection timeout"
**Solution:**
- Check internet connection
- Verify API endpoint is correct
- Try increasing timeout

### Issue: "No jobs inserted"
**Solution:**
- Are there jobs on the board? (Check in browser)
- Did the pipeline complete successfully?
- Check for duplicate URLs (apply_url)

### Issue: Tests fail
**Solution:**
- Ensure pytest is installed: `pip install pytest pytest-asyncio`
- Run full test suite: `pytest tests/ -v`
- Check Python version (needs 3.10+)

### Issue: Database connection error
**Solution:**
- Verify DATABASE_URL is set: `echo $DATABASE_URL`
- Check PostgreSQL is running
- Verify credentials are correct

---

## WHAT TO DO NEXT

### Immediately (Today)
1. ✅ Run the Phase 1-5 checklist above
2. ✅ Verify database has jobs
3. ✅ Add one custom source

### Soon (This Week)
1. ✅ Set up daily job sync (Phase 8)
2. ✅ Read `ARCHITECTURE.md` for deeper understanding
3. ✅ Plan which additional sources to add

### Later (This Month)
1. ✅ Add 5+ more sources
2. ✅ Set up monitoring & alerts
3. ✅ Configure backups
4. ✅ Document your setup
5. ✅ Train team members

### Future (As Needed)
1. ✅ Implement custom crawlers for proprietary job boards
2. ✅ Add authentication/API tokens
3. ✅ Implement advanced filtering
4. ✅ Build reporting dashboard

---

## QUICK REFERENCE COMMANDS

```bash
# List sources
python -m job_platform.pipeline.run_all_sources list

# Run all sources
python -m job_platform.pipeline.run_all_sources run

# Run specific type
python -m job_platform.pipeline.run_all_sources run greenhouse

# Run tests
pytest tests/test_crawlers.py -v

# View help
python -m job_platform.pipeline.run_all_sources help
```

---

## KEY FILES TO KNOW

| File | What It Does | Edit to... |
|------|--------------|-----------|
| `crawler/sources/config.py` | Defines all sources | Add sources |
| `crawler/sources/registry.py` | Maps types to crawlers | Add crawler types |
| `crawler/sources/*.py` | Crawler implementations | Fix crawler bugs |
| `pipeline/multi_source_pipeline.py` | Runs all sources | Change pipeline logic |
| `pipeline/run_all_sources.py` | CLI interface | Modify CLI |
| `tests/test_crawlers.py` | Tests & mocks | Add tests for new crawlers |

---

## ESTIMATED TIME INVESTMENT

| Task | Time | Difficulty |
|------|------|-----------|
| Set up & understand | 1-2 hours | Easy |
| Run first pipeline | 5 minutes | Very Easy |
| Add 1 source | 5 minutes | Very Easy |
| Add 10 similar sources | 10 minutes | Easy |
| Create new crawler type | 2-3 hours | Medium |
| Production deployment | 1-2 hours | Medium |
| Full mastery | 8-10 hours | Medium |

---

## HELPFUL LINKS

- PostgreSQL: https://www.postgresql.org/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- httpx Documentation: https://www.python-httpx.org/
- pytest: https://docs.pytest.org/

---

## READY TO START?

1. Open terminal
2. Run: `python -m job_platform.pipeline.run_all_sources list`
3. See your sources? ✓ System is ready!
4. Go to **Phase 4** above to run your first pipeline

**Questions?** Check the troubleshooting section or read the QUICKSTART.md guide!

Good luck! 🚀
"""
