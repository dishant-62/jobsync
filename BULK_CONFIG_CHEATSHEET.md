"""
# ⚡ BULK CONFIG QUICK REFERENCE

## CLI Commands Cheat Sheet

```bash
# View Configuration
python -m job_platform.crawler.sources config

# List Companies by ATS
python -m job_platform.crawler.sources list greenhouse
python -m job_platform.crawler.sources list lever
python -m job_platform.crawler.sources list workday

# Add Companies
python -m job_platform.crawler.sources add-company greenhouse stripe
python -m job_platform.crawler.sources add-companies lever netflix uber lyft

# Remove Company
python -m job_platform.crawler.sources remove-company greenhouse stripe

# Validate Configuration
python -m job_platform.crawler.sources validate

# Export Configuration
python -m job_platform.crawler.sources export > companies.json

# Help
python -m job_platform.crawler.sources help
```

## Python API Cheat Sheet

```python
from job_platform.crawler.sources import (
    # Get sources
    get_sources(),
    get_sources_by_type("greenhouse"),
    
    # Manage companies
    add_companies("greenhouse", ["stripe", "airbnb"]),
    remove_companies("greenhouse", ["stripe"]),
    get_companies("greenhouse"),
    
    # Config info
    get_source_stats(),
    print_configuration_summary(),
    export_configuration_as_dict(),
    validate_all_sources(),
)

# Examples
stats = get_source_stats()
print(stats)  # {'greenhouse': 20, 'lever': 10, 'workday': 5, 'total': 35}

is_valid, errors = validate_all_sources()
if not is_valid:
    for error in errors:
        print(f"  ✗ {error}")
```

## Config File Reference

Location: `job_platform/crawler/sources/config.py`

```python
# Define company lists
GREENHOUSE_COMPANIES = ["stripe", "airbnb", ...]
LEVER_COMPANIES = ["netflix", "uber", ...]
WORKDAY_COMPANIES = ["microsoft", "meta", ...]

# Auto-generated at module load
SOURCES: list[SourceConfig] = _generate_all_sources()

# Get individual sources
sources = get_sources()
gh_sources = get_sources_by_type("greenhouse")
```

## Key Classes & Types

```python
from job_platform.crawler.sources.config import SourceConfig

# SourceConfig definition
@dataclass(frozen=True)
class SourceConfig:
    name: str              # E.g., "Stripe Greenhouse"
    source_type: str       # "greenhouse", "lever", "workday"
    company: Optional[str] # Company name for ATS-based sources
    url: Optional[str]     # URL for aggregator sources

# Valid ATS types
AtsType = Literal["greenhouse", "lever", "workday"]
```

## Common Workflows

### Add 10 New Companies

```bash
python -m job_platform.crawler.sources add-companies greenhouse \
  company1 company2 company3 company4 company5 \
  company6 company7 company8 company9 company10
```

Or via Python:

```python
from job_platform.crawler.sources import add_companies
add_companies("greenhouse", [
    "company1", "company2", "company3", "company4", "company5",
    "company6", "company7", "company8", "company9", "company10",
])
```

### Validate Before Deployment

```bash
python -m job_platform.crawler.sources validate
echo $?  # Exit code 0 = success, 1 = error
```

### Export for Backup

```bash
python -m job_platform.crawler.sources export > backup_$(date +%Y%m%d).json
```

### View Statistics

```bash
python -m job_platform.crawler.sources config
# Shows: greenhouse: 20, lever: 10, workday: 5, total: 35+
```

## Configuration Structure

```
SOURCES (auto-generated list)
├── Greenhouse sources
│   ├── SourceConfig(name="Stripe Greenhouse", source_type="greenhouse", company="stripe")
│   ├── SourceConfig(name="Airbnb Greenhouse", source_type="greenhouse", company="airbnb")
│   └── ... (20 companies total)
├── Lever sources
│   ├── SourceConfig(name="Netflix Lever", source_type="lever", company="netflix")
│   ├── SourceConfig(name="Uber Lever", source_type="lever", company="uber")
│   └── ... (10 companies total)
├── Workday sources
│   ├── SourceConfig(name="Microsoft Workday", source_type="workday", company="microsoft")
│   └── ... (5 companies total)
└── URL sources
    ├── SourceConfig(name="Remote OK", source_type="remote_jobs", url="...")
    └── ... (3 aggregators)
```

## Error Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | Validation failed, error occurred |

## Useful Combinations

```bash
# List all companies then add new ones
python -m job_platform.crawler.sources list greenhouse
python -m job_platform.crawler.sources add-company greenhouse newcompany

# Validate then deploy
python -m job_platform.crawler.sources validate && \
  python -m job_platform.pipeline.run_all_sources run

# Export for documentation
python -m job_platform.crawler.sources export | jq .greenhouse[]

# Count companies
python -m job_platform.crawler.sources config | grep "Greenhouse:"
```

## Logging Context

When running commands, check logs for:

```
structured logs showing:
  - Operation: add_company/remove_company/validate
  - AtsType: greenhouse/lever/workday
  - CompaniesAdded/Removed: count
  - ValidationErrors: list of issues
```

## Performance Tips

- **Adding many companies?** Use `add-companies` (bulk) instead of multiple `add-company` calls
- **Validating?** Run `validate` before deploying to catch issues early
- **Exporting?** Use `export` to share config or backup

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Command not found | Run from project root: `pwd` should contain `/JobSync` |
| Unknown ATS type | Check valid types with `--help` |
| Duplicate company | `add_companies` automatically skips duplicates |
| Validation error | Run `validate` to see specific errors |
| Changes not persisting | Edit `config.py` directly for permanent storage |

## File Locations

| File | Purpose |
|------|---------|
| `crawler/sources/config.py` | Company lists & auto-generation |
| `crawler/sources/config_utils.py` | Management functions |
| `crawler/sources/manage.py` | CLI implementation |
| `crawler/sources/__init__.py` | Public API exports |
| `tests/test_config_bulk.py` | Tests for bulk functions |

## Environment

- Python: 3.10+
- Module path: `job_platform.crawler.sources`
- Entry point: `python -m job_platform.crawler.sources.manage <cmd>`

## Next Steps

1. Run: `python -m job_platform.crawler.sources config`
2. Try: `python -m job_platform.crawler.sources list greenhouse`
3. Add: `python -m job_platform.crawler.sources add-companies lever spotify databricks`
4. Validate: `python -m job_platform.crawler.sources validate`
5. Deploy: `python -m job_platform.pipeline.run_all_sources run`

---
**More details?** See `BULK_CONFIG_GUIDE.md` 📖
"""
