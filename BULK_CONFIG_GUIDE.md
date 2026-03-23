"""
# 📋 BULK ATS CONFIGURATION SYSTEM

## Overview

The bulk configuration system allows you to manage 20+ companies per ATS efficiently:

- **Zero Duplication**: Each company defined once
- **Auto-Generated Sources**: SOURCES list generated automatically
- **Validation**: Built-in validation and duplicate detection
- **CLI Management**: Easy-to-use command-line tools
- **Logging**: Comprehensive logging of configuration changes

---

## 🎯 Quick Start

### View Configuration Summary

```bash
python -m job_platform.crawler.sources config
```

Output:
```
======================================================================
JOB AGGREGATION CONFIGURATION SUMMARY
======================================================================

ATS-Based Sources (Company-Specific):
  Greenhouse: 20 companies
  Lever:      10 companies
  Workday:    5 companies

URL-Based Sources (Aggregators):
  Remote Jobs:  2 sources
  Wellfound:    1 sources
  Job Boards:   0 sources

Summary:
  ATS Sources:  35
  URL Sources:  3
  Total:        38
======================================================================
```

### List Companies for an ATS

```bash
python -m job_platform.crawler.sources list greenhouse
```

Output:
```
======================================================================
GREENHOUSE Companies
======================================================================

   1. stripe
   2. airbnb
   3. notion
   4. robinhood
   5. discord
   6. coinbase
   7. shopify
   8. datadog
   9. snowflake
  10. figma

Total: 20 companies
```

### Add Companies

```bash
# Add single company
python -m job_platform.crawler.sources add-company greenhouse stripe

# Add multiple companies
python -m job_platform.crawler.sources add-companies lever uber lyft palantir
```

### Remove Companies

```bash
python -m job_platform.crawler.sources remove-company greenhouse stripe
```

### Validate Configuration

```bash
python -m job_platform.crawler.sources validate
```

Output (success):
```
✓ Configuration is valid!
  All sources validated successfully.
```

---

## 🏗️ How It Works

### Configuration Structure

```python
# 1. Define company lists
GREENHOUSE_COMPANIES = [
    "stripe",
    "airbnb",
    "notion",
    ...
]

LEVER_COMPANIES = [
    "netflix",
    "uber",
    ...
]

# 2. Auto-generate SOURCES
SOURCES = _generate_all_sources()  # Called at import time
# - Reads all company lists
# - Creates SourceConfig for each
# - Removes duplicates
# - Validates all entries
# - Logs summary

# 3. Use SOURCES in pipeline
from job_platform.crawler.sources import get_sources
sources = get_sources()  # ~35+ sources automatically configured
```

### Generated Sources Example

For `GREENHOUSE_COMPANIES = ["stripe", "airbnb"]`, this generates:

```python
SourceConfig(
    name="Stripe Greenhouse",
    source_type="greenhouse",
    company="stripe",
)

SourceConfig(
    name="Airbnb Greenhouse",
    source_type="greenhouse",
    company="airbnb",
)
```

### Duplicate Detection

If a company appears in multiple ATS lists, or the same company is added twice:

```python
SOURCES = [
    SourceConfig(..., company="stripe", source_type="greenhouse"),
    SourceConfig(..., company="stripe", source_type="greenhouse"),  # Duplicate!
]

# After deduplication:
SOURCES = [
    SourceConfig(..., company="stripe", source_type="greenhouse"),  # Kept first
]
```

---

## 📝 Adding Companies

### Method 1: Edit Config File Directly

Edit `job_platform/crawler/sources/config.py`:

```python
GREENHOUSE_COMPANIES = [
    # ... existing companies ...
    
    # Add new companies
    "twilio",
    "instacart",
    "yelp",
    "asana",
]
```

**Pros:**
- Direct control
- Easy to see all companies at once
- History visible in git

**Cons:**
- Requires code deployment
- Need to reload Python

### Method 2: CLI Management

```bash
python -m job_platform.crawler.sources add-companies greenhouse twilio instacart yelp asana
```

**Pros:**
- No code changes
- Immediate effect
- Runtime changes

**Cons:**
- Changes not persisted (if you restart the system)
- Need to document changes elsewhere

### Method 3: Programmatic

```python
from job_platform.crawler.sources import add_companies

# Add companies programmatically
add_companies("greenhouse", ["spotify", "databricks", "canva"])

# Verify they were added
from job_platform.crawler.sources import get_companies
all_gh = get_companies("greenhouse")
print(f"Greenhouse companies: {len(all_gh)}")
```

---

## 🔧 CLI Command Reference

### `config` — View Summary

```bash
python -m job_platform.crawler.sources config
```

Shows:
- Companies per ATS type
- Total sources
- Breakdown by source type

### `list <type>` — List Companies

```bash
python -m job_platform.crawler.sources list greenhouse
python -m job_platform.crawler.sources list lever
python -m job_platform.crawler.sources list workday
```

Shows all companies for that ATS type.

### `add-company <type> <company>`

```bash
python -m job_platform.crawler.sources add-company greenhouse spotify
```

Adds a single company.

**Validation:**
- Company name must be non-empty string
- Duplicate check (skips if already exists)
- Logs the addition

### `add-companies <type> <c1> <c2> ...`

```bash
python -m job_platform.crawler.sources add-companies lever netflix uber lyft
```

Adds multiple companies at once. Useful for bulk imports.

### `remove-company <type> <company>`

```bash
python -m job_platform.crawler.sources remove-company greenhouse datado
```

Removes a company from the list.

### `validate` — Check Configuration

```bash
python -m job_platform.crawler.sources validate
```

Validates all sources:
- Check for invalid configurations
- Verify required fields
- Report validation errors

### `export` — Export as JSON

```bash
python -m job_platform.crawler.sources export > config.json
```

Exports current company lists as JSON:

```json
{
  "greenhouse": [
    "stripe",
    "airbnb",
    "notion"
  ],
  "lever": [
    "netflix",
    "uber",
    "lyft"
  ],
  "workday": [
    "microsoft",
    "meta",
    "amazon"
  ]
}
```

Useful for:
- Sharing configuration
- Backing up configuration
- Importing to external tools
- Version control

### `help` — Show Help

```bash
python -m job_platform.crawler.sources help
```

Shows all available commands and examples.

---

## 🎓 Common Use Cases

### Scale from 3 to 20+ Companies

**Before (old system):**
```python
SOURCES = [
    SourceConfig("Stripe", "greenhouse", company="stripe"),
    SourceConfig("Airbnb", "greenhouse", company="airbnb"),
    SourceConfig("Figma", "greenhouse", company="figma"),
    # ... manually add 17 more lines ...
]
```

**After (bulk system):**
```python
GREENHOUSE_COMPANIES = [
    "stripe",
    "airbnb",
    "figma",
    # ... 17 more companies, auto-generates SOURCES
]
```

Time saved: 10+ minutes per ATS

### Add Companies Dynamically

```python
# During runtime, add more companies
from job_platform.crawler.sources import add_companies, get_source_stats

add_companies("greenhouse", ["spotify", "databricks"])

stats = get_source_stats()
print(f"Now have {stats['greenhouse']} Greenhouse sources!")
```

### Import from External List

```python
# CSV file: companies.csv
# stripe,airbnb,notion,robinhood

import csv
from job_platform.crawler.sources import add_companies

with open("companies.csv") as f:
    companies = [line.strip() for line in f]

add_companies("greenhouse", companies)
```

### Validate Before Deployment

```bash
# Before deploying configuration changes
python -m job_platform.crawler.sources validate

# If validation fails, don't deploy!
echo $?  # Exit code 1 = failed
```

---

## ✅ Best Practices

### 1. **Use Bulk Mode for Similar Companies**

Do this:
```python
GREENHOUSE_COMPANIES = ["stripe", "airbnb", "notion", ...]  # All Greenhouse
```

NOT this:
```python
SOURCES = [
    SourceConfig("Stripe", "greenhouse", company="stripe"),
    SourceConfig("Netflix", "lever", company="netflix"),
    SourceConfig("Stripe", "lever", company="stripe"),  # Confusing!
]
```

### 2. **Validate After Changes**

```bash
# After adding companies
python -m job_platform.crawler.sources validate

# If there are errors, fix them
```

### 3. **Use Consistent Company Names**

All lowercase, no spaces:
- ✓ "stripe", "airbnb", "databricks"
- ✗ "Stripe", "Air BnB", "DataBricks"

### 4. **Document Custom Configurations**

```python
# companies added 2024-03-23
GREENHOUSE_COMPANIES = [
    "stripe",      # High priority
    "airbnb",      # High priority
    "figma",       # Team request (john@company.com)
]
```

### 5. **Test New Crawlers**

```bash
# After adding companies to a new ATS
python -m job_platform.pipeline.run_all_sources run greenhouse

# Check that all jobs were fetched
```

---

## 📊 Configuration Statistics

### Current Configuration

```
Greenhouse:  20 companies
Lever:       10 companies
Workday:     5 companies
────────────────────────
ATS Sources: 35 companies
+ 3 URL sources
────────────────────────
TOTAL:       38 sources
```

### Estimated Ingestion Time

- Per company: 2-5 seconds (with API calls)
- Parallel (max_concurrent=5): 35 companies ≈ 20-30 seconds total
- Total with database: 30-40 seconds

### Estimated Data Volume

- Per company: 50-200 jobs
- 35 companies × 100 jobs avg: ~3,500 jobs
- ~500KB compressed database storage

---

## 🔄 Adding a New ATS Type

### Step 1: Create Crawler Class

```python
# crawler/sources/myats.py
class MyAtsCrawler(BaseCrawler):
    async def fetch_jobs_from_company(self, company, client):
        ...
```

### Step 2: Add to Registry

```python
# crawler/sources/registry.py
self._crawlers["myats"] = MyAtsCrawler()
```

### Step 3: Add Company List

```python
# crawler/sources/config.py
MYATS_COMPANIES = [
    "company1",
    "company2",
    ...
]
```

### Step 4: Add Generation Function

```python
def _generate_myats_sources():
    return [
        SourceConfig(
            name=f"{company.title()} MyAts",
            source_type="myats",
            company=company.lower(),
        )
        for company in MYATS_COMPANIES
    ]
```

### Step 5: Update Main Generation

```python
def _generate_all_sources():
    all_sources = []
    ...
    all_sources.extend(_generate_myats_sources())
    ...
```

Then it works automatically!

---

## 🛡️ Error Handling

### Duplicate Companies

```bash
$ python -m job_platform.crawler.sources add-companies greenhouse stripe stripe

# Log message:
# WARNING: duplicate_companies_in_list - stripe appears multiple times
# ✓ Added 1 company (duplicate skipped)
```

### Invalid Company Names

```python
add_companies("greenhouse", ["", None, "stripe"])
# Error: Invalid company identifiers: ['', None]
```

### Unknown ATS Type

```bash
$ python -m job_platform.crawler.sources list invalid_ats

# Error: Unknown ATS type 'invalid_ats'
# Valid types: greenhouse, lever, workday
```

### Validation Failures

```bash
$ python -m job_platform.crawler.sources validate

# ✗ Configuration validation failed!
# Errors (2):
#     1. Stripe Greenhouse: greenhouse requires 'company' field
#     2. RemoteOK: remote_jobs requires 'url' field
```

---

## 📚 API Reference

### Configuration Functions

```python
from job_platform.crawler.sources import (
    get_sources,                      # All sources
    get_sources_by_type("greenhouse"), # Type filter
    get_source_by_name("Stripe ..."),  # Find by name
    get_source_stats(),                # Count per type
    GREENHOUSE_COMPANIES,              # Company list
)
```

### Management Functions

```python
from job_platform.crawler.sources import (
    add_companies("greenhouse", [...]),
    remove_companies("greenhouse", [...]),
    get_companies("greenhouse"),
    print_configuration_summary(),
    export_configuration_as_dict(),
    validate_all_sources(),
)
```

---

## 🎯 Next Steps

1. **View current configuration**
   ```bash
   python -m job_platform.crawler.sources config
   ```

2. **List companies for an ATS**
   ```bash
   python -m job_platform.crawler.sources list greenhouse
   ```

3. **Add new companies**
   ```bash
   python -m job_platform.crawler.sources add-companies lever spotify databricks
   ```

4. **Validate configuration**
   ```bash
   python -m job_platform.crawler.sources validate
   ```

5. **Run pipeline with new companies**
   ```bash
   python -m job_platform.pipeline.run_all_sources run
   ```

---

## ❓ FAQ

**Q: How many companies can I add?**
A: As many as you want! The system scales efficiently with 100+.

**Q: Do changes persist after restart?**
A: If you edit `config.py` yes. If you use CLI, they're in memory only.

**Q: Can I add the same company to multiple ATS?**
A: Yes! The system deduplicates by (source_type, company).

**Q: How do I make changes permanent?**
A: Edit `job_platform/crawler/sources/config.py` and commit to git.

**Q: What if a company has multiple job boards?**
A: You can add them as separate sources with different types.

---

**Ready to scale to 20+ companies?** Start with `python -m job_platform.crawler.sources config`! 🚀
"""
