"""
# 📚 DOCUMENTATION INDEX - Bulk ATS Configuration System

## Start Here

Choose based on your needs:

### 🏃 **I Just Want to Use It**
→ See **[BULK_CONFIG_CHEATSHEET.md](BULK_CONFIG_CHEATSHEET.md)** (2 min read)
- CLI commands cheat sheet
- Quick Python API examples
- Common workflows

### 📖 **I Want Complete Details**
→ See **[BULK_CONFIG_GUIDE.md](BULK_CONFIG_GUIDE.md)** (15 min read)
- How everything works
- Detailed examples
- Best practices
- Troubleshooting
- FAQ

### 🔄 **I'm Migrating from Old System**
→ See **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** (10 min read)
- Step-by-step migration
- Backward compatibility
- Testing your migration
- Rollback plan

### 🏗️ **I Want System Overview**
→ See **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** (10 min read)
- Architecture overview
- What was built
- Current configuration
- Use cases
- Performance characteristics

---

## Quick Navigation

| What I Want | Time | Document |
|------------|------|----------|
| Just run a command | 1 min | CHEATSHEET |
| Copy-paste example | 2 min | CHEATSHEET |
| Understand how it works | 10 min | SYSTEM_OVERVIEW |
| Full reference guide | 15 min | BULK_CONFIG_GUIDE |
| Migrate from old system | 15 min | MIGRATION_GUIDE |
| Debug an issue | 10 min | BULK_CONFIG_GUIDE (Troubleshooting) |

---

## By Use Case

### Adding Companies
📍 **Quick:** `CHEATSHEET` → Add Companies section  
📍 **Detailed:** `BULK_CONFIG_GUIDE` → Adding Companies section  
📍 **CLI:** `python -m job_platform.crawler.sources help`

### Managing Configuration
📍 **Commands:** `CHEATSHEET` → CLI Commands section  
📍 **Guide:** `BULK_CONFIG_GUIDE` → How It Works section

### Troubleshooting
📍 **Common Issues:** `BULK_CONFIG_GUIDE` → Troubleshooting section  
📍 **Error Codes:** `CHEATSHEET` → Error Codes table  
📍 **Migration Issues:** `MIGRATION_GUIDE` → Troubleshooting Migration

### Integration
📍 **API Reference:** `CHEATSHEET` → Python API section  
📍 **Pipeline Integration:** `SYSTEM_OVERVIEW` → Integration Points section  
📍 **Database Integration:** `SYSTEM_OVERVIEW` → Integration Points section

### Understanding System
📍 **Architecture:** `SYSTEM_OVERVIEW` → Architecture section  
📍 **Features:** `SYSTEM_OVERVIEW` → Core Features section  
📍 **Configuration Stats:** `SYSTEM_OVERVIEW` → Current Configuration section

---

## Documents Explained

### 1. BULK_CONFIG_CHEATSHEET.md
**Best for:** Quick reference, copy-paste examples

**Contains:**
- CLI commands reference
- Python API examples
- Configuration structure
- Common workflows
- Error handling
- File locations
- Environment info

**Length:** ~200 lines  
**Read time:** 2-5 minutes

### 2. BULK_CONFIG_GUIDE.md
**Best for:** Complete understanding, learning

**Contains:**
- Quick start
- CLI command reference with examples
- How it works (deep dive)
- Adding companies (3 methods)
- Common use cases
- Best practices
- Adding new ATS types
- Error handling details
- API reference
- FAQ

**Length:** ~500 lines  
**Read time:** 15 minutes

### 3. MIGRATION_GUIDE.md
**Best for:** Upgrading from old system

**Contains:**
- Overview of changes
- Migration steps
- Detailed examples
- Code compatibility
- Common scenarios
- Testing migration
- Troubleshooting migration
- Performance comparison
- Rollback plan
- FAQ on migration

**Length:** ~400 lines  
**Read time:** 15 minutes

### 4. SYSTEM_OVERVIEW.md
**Best for:** High-level understanding, architecture

**Contains:**
- Feature summary
- Files added/modified list
- Current configuration
- Use cases
- Architecture overview
- Key improvements
- Quick start (5 min version)
- Integration points
- Testing info
- Logging details
- Common patterns
- Performance characteristics
- Roadmap

**Length:** ~400 lines  
**Read time:** 10 minutes

---

## Reading Paths

### Path 1: Quick Start (5 minutes)
1. Read **CHEATSHEET** - CLI Commands section
2. Run `python -m job_platform.crawler.sources config`
3. Run `python -m job_platform.crawler.sources add-company greenhouse yourcompany`
4. Done! You're using the bulk system

### Path 2: Complete Understanding (45 minutes)
1. Read **SYSTEM_OVERVIEW** (10 min) - Get the big picture
2. Read **BULK_CONFIG_GUIDE** (15 min) - Learn details
3. Read **CHEATSHEET** (5 min) - Bookmark for reference
4. Experiment: Run commands, add companies, validate
5. Done! You understand the system completely

### Path 3: Migration (30 minutes)
1. Read **MIGRATION_GUIDE** intro (5 min)
2. Follow migration steps (10 min)
3. Test with CHEATSHEET examples (10 min)
4. Read **BULK_CONFIG_GUIDE** troubleshooting (5 min)
5. Done! Your config is migrated

### Path 4: Integration (30 minutes)
1. Read **SYSTEM_OVERVIEW** → Integration Points (5 min)
2. Read **BULK_CONFIG_GUIDE** → API Reference (10 min)
3. Read **CHEATSHEET** → Python API (5 min)
4. Implement integration
5. Test with CHEATSHEET examples (10 min)

---

## By Department/Role

### 👨‍💼 **Manager**
Want to understand what was built?
→ **SYSTEM_OVERVIEW** (10 min)
- What Just Shipped section
- Current Configuration
- Use Cases

### 🛠️ **Engineer (New)**
Want to start using the system?
→ **CHEATSHEET** (2 min) + **BULK_CONFIG_GUIDE** (15 min)
- Quick commands
- How It Works
- Best Practices

### 🔧 **Engineer (Maintaining)**
Want to integrate/maintain?
→ **BULK_CONFIG_GUIDE** (15 min) + **SYSTEM_OVERVIEW** (10 min)
- API Reference
- Integration Points
- Architecture

### 📚 **Documentation**
Want to explain to users?
→ All documents (30 min total)
- SYSTEM_OVERVIEW for overview
- BULK_CONFIG_GUIDE for detailed docs
- CHEATSHEET for quick ref
- MIGRATION_GUIDE for upgraders

---

## Key Concepts (Quick Reference)

### Auto-Generation
> Automatically creates SourceConfig objects from company lists. See BULK_CONFIG_GUIDE → How It Works

### Deduplication
> Removes duplicate (source_type, company) pairs automatically. See SYSTEM_OVERVIEW → Architecture

### Validation
> Multi-layer validation of company names and SourceConfig objects. See BULK_CONFIG_GUIDE → Error Handling

### CLI Management
> Command-line interface for add/remove/export operations. See CHEATSHEET → CLI Commands

### Programmatic API
> Python functions for runtime configuration changes. See CHEATSHEET → Python API

---

## Command Lookup

| I want to... | Command | See Document |
|-------------|---------|--------------|
| View config summary | `config` | CHEATSHEET |
| List companies | `list <type>` | CHEATSHEET |
| Add company | `add-company <type> <co>` | CHEATSHEET |
| Bulk add | `add-companies <type> <c1> ...` | CHEATSHEET |
| Remove company | `remove-company <type> <co>` | CHEATSHEET |
| Validate | `validate` | CHEATSHEET |
| Export config | `export` | CHEATSHEET |
| Show help | `help` | CHEATSHEET |

---

## Troubleshooting Lookup

| Problem | Solution | Document |
|---------|----------|----------|
| Don't know what to do | Start here! | CHEATSHEET |
| Command not working | Check CLI Commands section | CHEATSHEET |
| Configuration invalid | Check Error Handling | BULK_CONFIG_GUIDE |
| Changes not persisting | Check Best Practices | BULK_CONFIG_GUIDE |
| Migration issues | Check Troubleshooting Migration | MIGRATION_GUIDE |
| Integration questions | Check Integration Points | SYSTEM_OVERVIEW |

---

## Learning Objectives by Document

### After reading CHEATSHEET:
✓ Know basic CLI commands  
✓ Know Python API functions  
✓ Have copy-paste examples ready  

### After reading BULK_CONFIG_GUIDE:
✓ Understand how auto-generation works  
✓ Know 3 methods to add companies  
✓ Can troubleshoot common issues  
✓ Know best practices  

### After reading MIGRATION_GUIDE:
✓ Can migrate from old system  
✓ Know backward compatibility info  
✓ Can test migration  
✓ Have rollback plan  

### After reading SYSTEM_OVERVIEW:
✓ Understand architecture  
✓ Know what files were changed  
✓ Know current configuration  
✓ Understand use cases  

---

## File Locations for Reference

```
Documentation:
├── BULK_CONFIG_CHEATSHEET.md        (Quick reference - 2 min)
├── BULK_CONFIG_GUIDE.md             (Complete guide - 15 min)
├── MIGRATION_GUIDE.md               (Upgrading - 15 min)
├── SYSTEM_OVERVIEW.md               (Architecture - 10 min)
└── DOCUMENTATION_INDEX.md           (This file)

Code:
├── job_platform/crawler/sources/
│   ├── config.py                    (Company lists + auto-generation)
│   ├── config_utils.py              (Utility functions)
│   ├── manage.py                    (CLI implementation)
│   ├── __init__.py                  (Public API exports)
│   └── __main__.py                  (Module entry point)
└── tests/
    └── test_config_bulk.py          (50+ test cases)
```

---

## Next Steps

### Right Now:
1. Pick a document based on your need above
2. Read the relevant section
3. Try the example commands

### Next 30 minutes:
1. Run `python -m job_platform.crawler.sources config`
2. Run `python -m job_platform.crawler.sources list greenhouse`
3. Add a test company
4. Run `python -m job_platform.crawler.sources validate`

### This Week:
1. Integrate with your workflow
2. Add your actual companies to the lists
3. Run the pipeline with new config
4. Validate everything works

---

## Questions?

**Quick question?** → Check CHEATSHEET FAQ section  
**How does X work?** → Check BULK_CONFIG_GUIDE  
**Integrating?** → Check SYSTEM_OVERVIEW Integration section  
**Upgrading?** → Check MIGRATION_GUIDE  

---

## Document Summary Table

| Doc | Best For | Time | Length | Focus |
|-----|----------|------|--------|-------|
| **CHEATSHEET** | Quick ref | 2 min | 200 lines | Commands & examples |
| **BULK_CONFIG_GUIDE** | Learning | 15 min | 500 lines | Details & practices |
| **MIGRATION_GUIDE** | Upgrading | 15 min | 400 lines | Transition & testing |
| **SYSTEM_OVERVIEW** | Understanding | 10 min | 400 lines | Architecture & design |

---

**Last updated:** Phase 2 completion - Bulk configuration system ready  
**Status:** ✅ Complete and documented  
**Test coverage:** 50+ test cases  

🚀 **Happy reading!**
"""
