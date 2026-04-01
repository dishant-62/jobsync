"""
Root conftest.py — ensures the project root is on sys.path so that
`job_platform` is always importable regardless of how pytest is invoked.
"""
import sys
from pathlib import Path

# Project root is one directory above this conftest.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
