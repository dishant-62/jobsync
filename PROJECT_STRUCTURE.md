"""
# 📂 PROJECT STRUCTURE - SCALABLE JOB AGGREGATION

## Complete Directory Layout

```
JobSync/
├── job_platform/
│   ├── __init__.py
│   ├── config.py                    # App config
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── jobs.py              # API endpoints
│   │
│   ├── crawler/                     # ⭐ JOB CRAWLER MODULE
│   │   ├── __init__.py
│   │   ├── base.py                  # ⭐ BaseCrawler abstract class
│   │   │                            #    NormalizedJob schema
│   │   ├── greenhouse.py            # Original crawler (kept for compat)
│   │   └── sources/                 # ⭐ NEW: Organized crawlers
│   │       ├── __init__.py          # Exports all crawlers
│   │       ├── base.py              # ⭐ NEW: BaseCrawler moved here
│   │       ├── config.py            # ⭐ NEW: Source configuration
│   │       ├── registry.py          # ⭐ NEW: Crawler registry
│   │       │
│   │       ├── greenhouse.py        # ⭐ NEW: GreenhouseCrawler (refactored)
│   │       ├── lever.py             # ⭐ NEW: LeverCrawler
│   │       ├── workday.py           # ⭐ NEW: WorkdayCrawler
│   │       ├── remote_jobs.py       # ⭐ NEW: RemoteJobsCrawler
│   │       ├── job_board.py         # ⭐ NEW: JobBoardCrawler (generic)
│   │       ├── wellfound.py         # ⭐ NEW: WellfoundCrawler
│   │       └── __pycache__/
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                  # SQLAlchemy declarative base
│   │   ├── models.py                # Company, Job ORM models
│   │   ├── session.py               # AsyncSession factory
│   │   └── __pycache__/
│   │
│   ├── pipeline/                    # ⭐ PIPELINE & ORCHESTRATION
│   │   ├── __init__.py              # 🔄 UPDATED: Exports new functions
│   │   ├── __main__.py              # ⭐ NEW: CLI entry point
│   │   ├── greenhouse_pipeline.py   # Original pipeline (kept for compat)
│   │   ├── multi_source_pipeline.py # ⭐ NEW: Unified multi-source pipeline
│   │   ├── run_all_sources.py       # ⭐ NEW: CLI runner
│   │   └── __pycache__/
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── company.py               # 🔄 UPDATED: Multi-source support
│   │   ├── job.py                   # Job persistence
│   │   └── __pycache__/
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── job.py                   # Pydantic schemas
│   │   └── __pycache__/
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logging.py               # Logging setup
│   │   └── __pycache__/
│   │
│   └── __pycache__/
│
├── tests/                           # ⭐ TESTING
│   ├── __init__.py
│   └── test_crawlers.py             # ⭐ NEW: Comprehensive crawler tests
│
├── _frontend/                       # Frontend app
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   ├── JobCard.tsx
│   │   │   ├── JobList.tsx
│   │   │   ├── Pagination.tsx
│   │   │   └── SearchBar.tsx
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   └── ...config files
│
├── alembic/                         # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_initial_companies_and_jobs.py
│       └── 0002_job_search_indexes.py
│
├── 📄 ARCHITECTURE.md               # ⭐ NEW: Architecture guide
├── 📄 QUICKSTART.md                 # ⭐ NEW: Quick start guide
├── 📄 IMPLEMENTATION_SUMMARY.md      # ⭐ NEW: This summary
├── README.md
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── pyproject.toml
└── .env                             # Database URL, config
```

---

## 🎯 HOW TO USE EACH COMPONENT

### FOR CONFIGURATION
**File**: `job_platform/crawler/sources/config.py`

```python
# Add sources here - that's it!
SOURCES = [
    SourceConfig("Stripe", "greenhouse", company="stripe"),
    SourceConfig("Netflix", "lever", company="netflix"),
    SourceConfig("RemoteOK", "remote_jobs", url="https://remoteok.com"),
]
```

### FOR RUNNING THE PIPELINE
**Files**: `pipeline/multi_source_pipeline.py`, `pipeline/run_all_sources.py`

```bash
# Via CLI
python -m job_platform.pipeline.run_all_sources run

# Via Python API
from job_platform.pipeline import run_all_sources
result = await run_all_sources()
```

### FOR IMPLEMENTING CRAWLERS
**Base**: `crawler/base.py`
**Examples**: `crawler/sources/greenhouse.py`, `crawler/sources/lever.py`

```python
from job_platform.crawler.base import BaseCrawler, NormalizedJob

class MyCrawler(BaseCrawler):
    async def fetch_jobs_from_company(self, company, client):
        # Fetch and return list[NormalizedJob]
        ...
```

### FOR TESTING
**File**: `tests/test_crawlers.py`

```bash
pytest tests/test_crawlers.py -v
```

### FOR UNDERSTANDING DESIGN
**Files** (in order):
1. `IMPLEMENTATION_SUMMARY.md` - Overview
2. `ARCHITECTURE.md` - Deep dive
3. `QUICKSTART.md` - Examples
4. `crawler/base.py` - Interface
5. `crawler/sources/greenhouse.py` - Example implementation

---

## 📊 DEPENDENCY GRAPH

```
1. Configuration Layer
   └─ crawler/sources/config.py
      └─ Defines SOURCES list

2. Registry Layer
   └─ crawler/sources/registry.py
      └─ Maps type → crawler instance

3. Crawler Layer
   └─ crawler/sources/*.py
      └─ Each returns list[NormalizedJob]

4. Pipeline Layer
   └─ pipeline/multi_source_pipeline.py
      └─ Iterates SOURCES → gets crawler → fetches → inserts

5. CLI Layer
   └─ pipeline/run_all_sources.py
      └─ Entry point for users
```

---

## 🔄 DATA FLOW

```
User runs: python -m job_platform.pipeline.run_all_sources run

    ↓

run_all_sources.py:main() starts

    ↓

multi_source_pipeline.py:run_all_sources()

    ├─ Load SOURCES from config.py
    └─ For each source (parallel with max_concurrent=3):
        ├─ Get crawler from registry
        ├─ Call crawler.fetch_jobs_from_company() or .fetch_jobs_from_url()
        ├─ Get list[NormalizedJob]
        ├─ For each job:
        │  ├─ Check for duplicate (apply_url)
        │  └─ If new: Insert into database
        └─ Record metrics (fetched, inserted, errors)

    ↓

Return PipelineRunResult (summary)

    ↓

Print summary to console
```

---

## 👥 COMPONENT INTERACTIONS

### Config & Registry Interaction
```
config.SOURCES (list of SourceConfig)
    └─ registry.get_crawler(source.source_type)
       └─ Returns BaseCrawler instance
```

### Crawler & NormalizedJob Interaction
```
crawler.fetch_jobs_from_company()
    └─ Returns list[NormalizedJob]
       └─ All crawlers return same format
          └─ Database knows one format
```

### Pipeline & Database Interaction
```
pipeline.run_all_sources()
    ├─ company_repo.get_or_create_for_source()
    │  └─ Creates Company record if needed
    │
    └─ job_repo.create_job()
       ├─ Check for duplicate first
       └─ Insert if new
```

---

## 🎯 KEY FILES BY TASK

| I want to... | Go to... |
|---|---|
| Add a new source | `crawler/sources/config.py` |
| Implement new crawler | `crawler/sources/mytype.py` (copy lever.py) |
| Run the pipeline | `python -m pipeline.run_all_sources` |
| Understand design | Read `ARCHITECTURE.md` |
| See examples | Check `QUICKSTART.md` |
| Debug a crawler | Look at `tests/test_crawlers.py` |
| Modify registry | `crawler/sources/registry.py` |
| Understand schema | `crawler/base.py` → NormalizedJob |
| Check pipeline logic | `pipeline/multi_source_pipeline.py` |
| See all sources | `crawler/sources/config.py` → SOURCES |

---

## 📈 Adding Sources: By the Numbers

### To add 1 source:
- Lines of code: **1** (in config.py)
- Files to modify: **1**
- Time: **30 seconds**

### To add 10 similar sources:
- Lines of code: **10** (in config.py)
- Files to modify: **1**
- Time: **5 minutes**

### To add 1 new crawler type:
- New files: **1** (mytype.py)
- Files to modify: **3** (__init__.py, registry.py, config.py)
- Lines of code: **150-300** (crawler implementation)
- Time: **1-2 hours** (including testing)

---

## 🏗️ ARCHITECTURAL PATTERNS USED

```
┌──────────────────────────────────────────────────┐
│              DESIGN PATTERNS                     │
├──────────────────────────────────────────────────┤
│                                                  │
│ 1. ABSTRACT BASE CLASS (abc)                     │
│    └─ BaseCrawler defines interface             │
│                                                  │
│ 2. TEMPLATE METHOD                              │
│    └─ Concrete crawlers implement abstract      │
│                                                  │
│ 3. REGISTRY (Factory)                           │
│    └─ Map type strings to crawler instances     │
│                                                  │
│ 4. DATACLASS (Configuration)                    │
│    └─ SourceConfig with validation              │
│                                                  │
│ 5. ASYNC/AWAIT (Concurrency)                    │
│    └─ Non-blocking I/O with semaphore           │
│                                                  │
│ 6. STRATEGY                                     │
│    └─ Each crawler has different fetching logic │
│                                                  │
│ 7. DECORATOR (Retry Logic)                      │
│    └─ Exponential backoff on failures           │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 🔐 SEPARATION OF CONCERNS

```
┌─────────────────────────────────────────────┐
│     CONFIGURATION LAYER                     │
│  What sources to use                        │
│  (crawler/sources/config.py)               │
└──────────────┬──────────────────────────────┘

┌──────────────────────────────────────────────┐
│     DISCOVERY LAYER                          │
│  How to find crawlers                        │
│  (crawler/sources/registry.py)              │
└──────────────┬───────────────────────────────┘

┌──────────────────────────────────────────────┐
│     IMPLEMENTATION LAYER                     │
│  How to fetch jobs                           │
│  (crawler/sources/*.py)                     │
└──────────────┬───────────────────────────────┘

┌──────────────────────────────────────────────┐
│     ORCHESTRATION LAYER                      │
│  How to run everything                       │
│  (pipeline/multi_source_pipeline.py)         │
└──────────────┬───────────────────────────────┘

┌──────────────────────────────────────────────┐
│     DATABASE LAYER                           │
│  How to store jobs                           │
│  (repositories/*.py, db/models.py)          │
└──────────────────────────────────────────────┘
```

Each layer is independent and testable!

---

## ✨ FEATURES AT A GLANCE

| Feature | Location | Example |
|---------|----------|---------|
| Crawler types | sources/*.py | GreenhouseCrawler, LeverCrawler |
| Configuration | sources/config.py | SOURCES list |
| Registry | sources/registry.py | get_crawler("greenhouse") |
| Pipeline | pipeline/multi_source_pipeline.py | run_all_sources() |
| CLI | pipeline/run_all_sources.py | python -m pipeline.run_all_sources |
| Tests | tests/test_crawlers.py | TestGreenhouseCrawler, etc. |
| Documentation | ARCHITECTURE.md, QUICKSTART.md | Full guides |

---

## 🎓 LEARNING PATH

**Day 1: Get Oriented**
- [ ] Read IMPLEMENTATION_SUMMARY.md
- [ ] Skim ARCHITECTURE.md (sections 1-3)
- [ ] Run: `python -m pipeline.run_all_sources list`
- [ ] Time: 30 minutes

**Day 2: Run Pipeline**
- [ ] Edit config.py (add 1 source)
- [ ] Run: `python -m pipeline.run_all_sources run`
- [ ] Check database for results
- [ ] Time: 15 minutes

**Day 3: Understand Code**
- [ ] Read crawler/base.py
- [ ] Read one crawler implementation (greenhouse.py)
- [ ] Read pipeline/multi_source_pipeline.py
- [ ] Time: 1 hour

**Day 4: Extend System**
- [ ] Create new crawler type (copy lever.py)
- [ ] Add to registry
- [ ] Add to config
- [ ] Run tests
- [ ] Time: 2-3 hours

**Total Learning Time: 5-6 hours** to be productive!

---

## 💾 File Size Reference

```
crawler/base.py                    ~150 lines
crawler/sources/
  ├─ greenhouse.py               ~120 lines
  ├─ lever.py                    ~150 lines
  ├─ workday.py                  ~170 lines
  ├─ remote_jobs.py              ~200 lines
  ├─ job_board.py                ~180 lines
  ├─ wellfound.py                ~180 lines
  ├─ config.py                   ~120 lines
  └─ registry.py                 ~80 lines

pipeline/
  ├─ multi_source_pipeline.py     ~280 lines
  └─ run_all_sources.py          ~200 lines

repositories/company.py            ~80 lines (updated)

tests/test_crawlers.py            ~350 lines

Documentation:
  ├─ ARCHITECTURE.md             ~300 lines
  ├─ QUICKSTART.md               ~400 lines
  ├─ IMPLEMENTATION_SUMMARY.md    ~400 lines
  └─ This file                    ~400 lines

TOTAL NEW/MODIFIED CODE: ~4000 lines
```

---

## 🚀 Production Deployment Checklist

- [ ] Review all source configurations
- [ ] Set environment variables (DATABASE_URL, etc.)
- [ ] Run migrations (alembic upgrade head)
- [ ] Test with one source first
- [ ] Run full pipeline test
- [ ] Set up cron job or scheduler
- [ ] Configure monitoring/alerts
- [ ] Document API tokens in vault
- [ ] Train team on adding new sources
- [ ] Set up backups for job database

---

## 📞 QUICK HELP

**"How do I...?"**

| Question | Answer |
|----------|--------|
| Add a source? | Edit `crawler/sources/config.py` (1 line) |
| Run pipeline? | `python -m pipeline.run_all_sources run` |
| Test crawler? | `pytest tests/test_crawlers.py` |
| Add crawler type? | Copy `lever.py`, modify, register |
| Understand design? | Read `ARCHITECTURE.md` |
| Debug issue? | Check `QUICKSTART.md` → Troubleshooting |

---

Done! You're ready to use this system. Start with:
```bash
python -m job_platform.pipeline.run_all_sources list
```

Then check what sources are available, and read QUICKSTART.md for next steps! 🎉
"""
