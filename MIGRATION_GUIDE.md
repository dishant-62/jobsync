"""
# 🔄 MIGRATION GUIDE: Old Config → Bulk Config System

## Overview

The bulk configuration system replaces manual source definition with auto-generated sources from company lists.

| Aspect | Old System | New System |
|--------|-----------|-----------|
| **Adding Company** | Edit SOURCES list manually | Add to company list, auto-generates |
| **# of Companies** | 3-8 sources per type | 20+ per type handled easily |
| **Deduplication** | Manual (easy to miss) | Automatic on every import |
| **Management** | Only programmatic | CLI + Programmatic |
| **Changes** | Require code restart | Immediate (or code for permanent) |
| **Validation** | Manual checking | Automatic validation |

---

## Before: Old Config System

```python
# crawler/sources/config.py (OLD)
from job_platform.crawler.sources.base import SourceConfig

SOURCES = [
    SourceConfig(
        name="Stripe",
        source_type="greenhouse",
        company="stripe",
    ),
    SourceConfig(
        name="Airbnb",
        source_type="greenhouse",
        company="airbnb",
    ),
    # ... would need to manually add 18 more for 20 companies ...
]
```

**Problems:**
- ❌ Repetitive - Same format repeated for each company
- ❌ Tedious - Manual entry for each company-ATS pair
- ❌ Error-prone - Duplicates easy to introduce
- ❌ Unmaintainable - Hard to see company list at a glance
- ❌ Rigid - No bulk operations

---

## After: New Bulk Config System

```python
# crawler/sources/config.py (NEW)
GREENHOUSE_COMPANIES = [
    "stripe",
    "airbnb",
    "notion",
    "robinhood",
    "discord",
    "coinbase",
    "shopify",
    "databricks",
    "figma",
    "stripe",  # Duplicate!
]

# Auto-generated (handles duplicates, validation, logging)
SOURCES = _generate_all_sources()
```

**Advantages:**
- ✅ Simple - Just list company names
- ✅ Efficient - Auto-generates all SourceConfig objects
- ✅ Safe - Automatic deduplication
- ✅ Maintainable - Clear company list visible
- ✅ Powerful - CLI + programmatic management

---

## Migration Steps

### Step 1: Extract Current Companies

**From old SOURCES list, extract all company names:**

```python
# OLD CONFIG
SOURCES = [
    SourceConfig(name="Stripe", source_type="greenhouse", company="stripe"),
    SourceConfig(name="Airbnb", source_type="greenhouse", company="airbnb"),
    SourceConfig(name="Netflix", source_type="lever", company="netflix"),
]

# EXTRACT TO:
GREENHOUSE_COMPANIES = ["stripe", "airbnb"]
LEVER_COMPANIES = ["netflix"]
```

### Step 2: Update config.py

Replace the old manual SOURCES list:

**BEFORE:**
```python
SOURCES = [
    SourceConfig(name="Stripe", source_type="greenhouse", company="stripe"),
    SourceConfig(name="Airbnb", source_type="greenhouse", company="airbnb"),
    SourceConfig(name="Figma", source_type="greenhouse", company="figma"),
    # ... 17 more entries manually typed ...
]
```

**AFTER:**
```python
GREENHOUSE_COMPANIES = [
    "stripe",
    "airbnb",
    "figma",
    # ... 17 more just names, auto-generates sources ...
]

SOURCES = _generate_all_sources()  # Auto-generated!
```

### Step 3: Import New Utilities

Add to your imports:

```python
from job_platform.crawler.sources import (
    add_companies,
    remove_companies,
    get_companies,
    validate_all_sources,
)
```

### Step 4: Update Any Custom Code

**Old way (still works):**
```python
# Accessing SOURCES directly
for source in SOURCES:
    print(source.name, source.source_type)
```

**New way (recommended):**
```python
# Using utility functions
sources = get_sources()
sources_by_type = get_sources_by_type("greenhouse")
```

### Step 5: Test Configuration

```bash
# Validate the new configuration
python -m job_platform.crawler.sources validate

# View summary
python -m job_platform.crawler.sources config

# Run pipeline with new config
python -m job_platform.pipeline.run_all_sources run
```

---

## Detailed Example

### Complete Migration Example

**BEFORE (Old Config):**
```python
# crawler/sources/config.py

SOURCES = [
    SourceConfig(
        name="Stripe",
        source_type="greenhouse",
        company="stripe",
    ),
    SourceConfig(
        name="Airbnb",
        source_type="greenhouse",
        company="airbnb",
    ),
    SourceConfig(
        name="Notion",
        source_type="greenhouse",
        company="notion",
    ),
    SourceConfig(
        name="Netflix",
        source_type="lever",
        company="netflix",
    ),
    SourceConfig(
        name="Uber",
        source_type="lever",
        company="uber",
    ),
]
```

**AFTER (New Config):**
```python
# crawler/sources/config.py

GREENHOUSE_COMPANIES = [
    "stripe",
    "airbnb",
    "notion",
]

LEVER_COMPANIES = [
    "netflix",
    "uber",
]

WORKDAY_COMPANIES = []

# Auto-generated from above lists
SOURCES = _generate_all_sources()
```

**Result:**
- ✅ 5x less code
- ✅ Much more readable
- ✅ Easy to add more companies
- ✅ Automatic deduplication
- ✅ Built-in validation

---

## Code Compatibility

### Old Code Still Works

Your existing code that uses SOURCES continues to work:

```python
# This still works!
def get_all_sources():
    return SOURCES

async def crawl_all():
    for source in SOURCES:
        crawler = registry.get_crawler(source.source_type)
        await crawler.fetch_jobs(source)
```

### New Code Can Use Utilities

But you can now also use convenience functions:

```python
# Get sources by type
gh_sources = get_sources_by_type("greenhouse")

# Add companies at runtime
add_companies("greenhouse", ["newcompany1", "newcompany2"])

# Get configuration stats
stats = get_source_stats()
print(f"Total sources: {stats['total']}")
```

---

## Common Migration Scenarios

### Scenario 1: Simple List Migration

**If you have 5-10 companies:**

Extract them to GREENHOUSE_COMPANIES, LEVER_COMPANIES lists.

```python
# Count before
OLD: SOURCES = [...20 entries...]

# Count after  
GREENHOUSE_COMPANIES = [20 company names]
SOURCES = _generate_all_sources()  # Generates 20 entries
```

### Scenario 2: Adding URL-Based Sources

**Keep URL sources separate:**

```python
# URL-based sources (not company-specific)
URL_SOURCES = [
    SourceConfig(name="Remote OK", source_type="remote_jobs", url="https://remoteok.io/jobs.json"),
    SourceConfig(name="Wellfound", source_type="wellfound", url="https://www.wellfound.com/jobs"),
]

# Company-based sources (auto-generated)
GREENHOUSE_COMPANIES = ["stripe", "airbnb"]

# Combined (auto-generated includes URL sources)
SOURCES = _generate_all_sources()
```

### Scenario 3: Gradual Migration

**Don't need to migrate all at once:**

```python
# Mix old and new (during transition)
GREENHOUSE_COMPANIES = ["stripe", "airbnb"]

_GENERATED_SOURCES = _generate_all_sources()

# Add any old-style entries
LEGACY_SOURCES = [
    SourceConfig(name="CustomCompany", source_type="greenhouse", company="custom"),
]

# Combine
SOURCES = _GENERATED_SOURCES + LEGACY_SOURCES
```

---

## Testing the Migration

### 1. Validate Configuration

```bash
python -m job_platform.crawler.sources validate
# Should pass with 0 errors
```

### 2. Check Source Count

```bash
python -m job_platform.crawler.sources config

# Output should match:
# Before: 20 sources
# After: 20 auto-generated sources (should be identical)
```

### 3. Test Crawling

```bash
# Run with new config
python -m job_platform.pipeline.run_all_sources run greenhouse

# Should work identically to before
```

### 4. Compare Outputs

```python
# Quick check
from job_platform.crawler.sources import get_source_stats

OLD_COUNT = 20  # From before migration
stats = get_source_stats()
NEW_COUNT = stats['total']

assert OLD_COUNT == NEW_COUNT, "Source count changed during migration!"
```

---

## Troubleshooting Migration

### Problem: "Source count changed"

**Cause:** Duplicates were in old config

**Solution:** Check for duplicates:
```python
from job_platform.crawler.sources import get_companies

# List all companies
for ats_type in ["greenhouse", "lever", "workday"]:
    companies = get_companies(ats_type)
    if len(companies) != len(set(companies)):
        print(f"Duplicates in {ats_type}!")
```

### Problem: "Validation errors after migration"

**Cause:** Missing required fields

**Solution:** Run validate and check errors:
```bash
python -m job_platform.crawler.sources validate
# Shows specific field errors
```

### Problem: "Pipeline doesn't find new sources"

**Cause:** Cached imports

**Solution:** Restart Python:
```bash
# Option 1: Restart shell
exit
python  # Start fresh

# Option 2: Force reload
import importlib
import job_platform.crawler.sources
importlib.reload(job_platform.crawler.sources)
```

---

## Performance Comparison

### Old System (Manual)

- Adding 20 companies: ~10 minutes of typing
- Finding a company: grep through SOURCES (manual search)
- Deduplicating: Manual inspection needed
- Validating: No built-in validation

### New System (Bulk)

- Adding 20 companies: Copy-paste to list (~30 seconds) or CLI (~2 minutes)
- Finding a company: `get_companies("greenhouse")` or `list greenhouse` command
- Deduplicating: Automatic - `_remove_duplicates()`
- Validating: Built-in `validate_all_sources()`

**Time savings: 5-10x faster for bulk operations**

---

## Rollback Plan

If you need to rollback:

1. Keep old `config.py` as `config.py.backup`
2. Revert to git version if tracked
3. Test with old config to verify

But really, the new system is backward compatible - you can:
- Still use SOURCES directly
- Still programmatically access sources
- Gradually add companies to company lists

---

## Best Practices After Migration

1. **Use company lists for new additions**
   ```python
   # Good
   GREENHOUSE_COMPANIES = ["existing", "companies", "new_company"]
   
   # Avoid
   SOURCES = [SourceConfig(...), SourceConfig(...)]  # Don't mix patterns
   ```

2. **Validate before deployment**
   ```bash
   python -m job_platform.crawler.sources validate
   ```

3. **Use CLI for quick changes**
   ```bash
   python -m job_platform.crawler.sources add-company greenhouse newcompany
   ```

4. **Track config in git**
   ```bash
   git add crawler/sources/config.py
   git commit -m "Add 5 new greenhouse companies"
   ```

5. **Backup exported config**
   ```bash
   python -m job_platform.crawler.sources export > config_backup_$(date +%Y%m%d).json
   ```

---

## FAQ on Migration

**Q: Will my old code break?**
A: No! SOURCES is still available and works the same way.

**Q: Can I mix old and new style?**
A: Yes, but not recommended. Better to migrate completely.

**Q: Do I need to update other files?**
A: No. Only `config.py` changes are needed.

**Q: Can I gradually migrate?**
A: Yes! Mix old SOURCES with new company lists during transition.

**Q: What about my custom crawlers?**
A: They work the same. Only configuration system changed.

**Q: Is there a performance difference?**
A: New system is slightly faster (deduplication is O(n) instead of manual).

---

## Next Steps

1. **Back up current config:**
   ```bash
   cp crawler/sources/config.py crawler/sources/config.py.backup
   ```

2. **Extract companies from old SOURCES**

3. **Create new config.py with company lists**

4. **Validate:**
   ```bash
   python -m job_platform.crawler.sources validate
   ```

5. **Test pipeline:**
   ```bash
   python -m job_platform.pipeline.run_all_sources run
   ```

6. **Commit to git:**
   ```bash
   git add crawler/sources/config.py
   git commit -m "Migrate to bulk configuration system"
   ```

---

**Ready to migrate? Start with step 1 above!** 🚀
"""
