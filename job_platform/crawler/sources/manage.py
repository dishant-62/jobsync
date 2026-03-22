"""
Configuration management CLI for bulk ATS company management.

Usage:
    python -m job_platform.crawler.sources.manage config
    python -m job_platform.crawler.sources.manage add-company greenhouse stripe
    python -m job_platform.crawler.sources.manage add-companies lever uber lyft palantir
    python -m job_platform.crawler.sources.manage remove-company greenhouse stripe
    python -m job_platform.crawler.sources.manage list <ats-type>
    python -m job_platform.crawler.sources.manage validate
"""

from __future__ import annotations

import sys
from typing import Literal

from job_platform.crawler.sources.config_utils import (
    add_companies,
    export_configuration_as_dict,
    get_companies,
    print_configuration_summary,
    remove_companies,
    validate_all_sources,
)
from job_platform.utils.logging import configure_logging, get_logger

logger = get_logger("job_platform.crawler.sources.manage")

AtsType = Literal["greenhouse", "lever", "workday"]


def _print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 70}", file=sys.stdout)
    print(f"  {text}", file=sys.stdout)
    print(f"{'=' * 70}\n", file=sys.stdout)


def cmd_config() -> int:
    """Show configuration summary."""
    _print_header("Configuration Summary")
    print_configuration_summary()
    return 0


def cmd_list(ats_type: str) -> int:
    """List companies for a specific ATS type."""
    try:
        ats_type_lower = ats_type.lower()
        if ats_type_lower not in {"greenhouse", "lever", "workday"}:
            print(f"Error: Unknown ATS type '{ats_type}'", file=sys.stderr)
            print(f"Valid types: greenhouse, lever, workday", file=sys.stderr)
            return 1
        
        _print_header(f"{ats_type.upper()} Companies")
        
        companies = get_companies(ats_type_lower)  # type: ignore
        
        if not companies:
            print(f"No companies configured for {ats_type}", file=sys.stdout)
            return 0
        
        for i, company in enumerate(companies, 1):
            print(f"  {i:2d}. {company}", file=sys.stdout)
        
        print(f"\nTotal: {len(companies)} companies\n", file=sys.stdout)
        return 0
        
    except Exception as e:
        logger.error("list_command_error", error=str(e))
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_add_company(ats_type: str, company: str) -> int:
    """Add a single company to an ATS type."""
    try:
        ats_type_lower = ats_type.lower()
        if ats_type_lower not in {"greenhouse", "lever", "workday"}:
            print(f"Error: Unknown ATS type '{ats_type}'", file=sys.stderr)
            return 1
        
        _print_header(f"Adding Company to {ats_type.upper()}")
        
        add_companies(ats_type_lower, [company], validate=True)  # type: ignore
        print(f"✓ Added '{company}' to {ats_type}\n", file=sys.stdout)
        return 0
        
    except Exception as e:
        logger.error("add_company_error", error=str(e))
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_add_companies(ats_type: str, companies: list[str]) -> int:
    """Add multiple companies to an ATS type."""
    try:
        ats_type_lower = ats_type.lower()
        if ats_type_lower not in {"greenhouse", "lever", "workday"}:
            print(f"Error: Unknown ATS type '{ats_type}'", file=sys.stderr)
            return 1
        
        _print_header(f"Adding {len(companies)} Companies to {ats_type.upper()}")
        
        add_companies(ats_type_lower, companies, validate=True)  # type: ignore
        
        for company in companies:
            print(f"  ✓ {company}", file=sys.stdout)
        
        print(f"\n✓ Added {len(companies)} companies to {ats_type}\n", file=sys.stdout)
        return 0
        
    except Exception as e:
        logger.error("add_companies_error", error=str(e))
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_remove_company(ats_type: str, company: str) -> int:
    """Remove a single company from an ATS type."""
    try:
        ats_type_lower = ats_type.lower()
        if ats_type_lower not in {"greenhouse", "lever", "workday"}:
            print(f"Error: Unknown ATS type '{ats_type}'", file=sys.stderr)
            return 1
        
        _print_header(f"Removing Company from {ats_type.upper()}")
        
        remove_companies(ats_type_lower, [company])  # type: ignore
        print(f"✓ Removed '{company}' from {ats_type}\n", file=sys.stdout)
        return 0
        
    except Exception as e:
        logger.error("remove_company_error", error=str(e))
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_validate() -> int:
    """Validate all configured sources."""
    _print_header("Validating Configuration")
    
    is_valid, errors = validate_all_sources()
    
    if is_valid:
        print("✓ Configuration is valid!", file=sys.stdout)
        print(f"  All sources validated successfully.\n", file=sys.stdout)
        return 0
    else:
        print("✗ Configuration validation failed!", file=sys.stderr)
        print(f"\n  Errors ({len(errors)}):\n", file=sys.stderr)
        for i, error in enumerate(errors, 1):
            print(f"    {i}. {error}", file=sys.stderr)
        print("", file=sys.stderr)
        return 1


def cmd_export() -> int:
    """Export configuration as JSON (for external tools)."""
    _print_header("Exporting Configuration")
    
    try:
        import json
        config = export_configuration_as_dict()
        config_json = json.dumps(config, indent=2)
        print(config_json, file=sys.stdout)
        return 0
    except Exception as e:
        logger.error("export_error", error=str(e))
        print(f"Error: {e}", file=sys.stderr)
        return 1


def print_help() -> None:
    """Print help message."""
    _print_header("Configuration Management CLI")
    
    print("""
  Configuration management for bulk ATS company ingestion.
  
  Commands:
    config                          Show configuration summary
    list <ats-type>                 List companies for ATS type
    add-company <type> <comp>       Add single company
    add-companies <type> <c1> <c2>  Add multiple companies
    remove-company <type> <comp>    Remove company
    validate                        Validate all sources
    export                          Export config as JSON
    help                            Show this help
    
  ATS Types: greenhouse, lever, workday
    
  Examples:
    # Show summary
    python -m job_platform.crawler.sources.manage config
    
    # List all Greenhouse companies
    python -m job_platform.crawler.sources.manage list greenhouse
    
    # Add one company
    python -m job_platform.crawler.sources.manage add-company greenhouse stripe
    
    # Add multiple companies
    python -m job_platform.crawler.sources.manage add-companies lever uber lyft
    
    # Remove a company
    python -m job_platform.crawler.sources.manage remove-company lever uber
    
    # Validate all sources
    python -m job_platform.crawler.sources.manage validate
    
    # Export to JSON
    python -m job_platform.crawler.sources.manage export > config.json
    """, file=sys.stdout)


def main() -> int:
    """Main CLI entry point."""
    configure_logging()
    
    args = sys.argv[1:]
    
    if not args or args[0] in {"help", "--help", "-h"}:
        print_help()
        return 0
    
    command = args[0]
    
    try:
        if command == "config":
            return cmd_config()
        
        elif command == "list":
            if len(args) < 2:
                print("Error: list requires <ats-type> argument", file=sys.stderr)
                return 1
            return cmd_list(args[1])
        
        elif command == "add-company":
            if len(args) < 3:
                print("Error: add-company requires <ats-type> and <company> arguments", file=sys.stderr)
                return 1
            return cmd_add_company(args[1], args[2])
        
        elif command == "add-companies":
            if len(args) < 3:
                print("Error: add-companies requires <ats-type> and at least one <company>", file=sys.stderr)
                return 1
            return cmd_add_companies(args[1], args[2:])
        
        elif command == "remove-company":
            if len(args) < 3:
                print("Error: remove-company requires <ats-type> and <company> arguments", file=sys.stderr)
                return 1
            return cmd_remove_company(args[1], args[2])
        
        elif command == "validate":
            return cmd_validate()
        
        elif command == "export":
            return cmd_export()
        
        else:
            print(f"Error: Unknown command '{command}'", file=sys.stderr)
            print("Run with 'help' for usage information", file=sys.stderr)
            return 1
    
    except Exception as e:
        logger.error("cli_error", error=str(e))
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
