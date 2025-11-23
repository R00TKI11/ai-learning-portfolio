#!/usr/bin/env python3
"""
Convenience script to run tests with structured output.

Usage:
    python run_tests.py                                    # Run all tests
    python run_tests.py --format json --output results.json
    python run_tests.py --format markdown --output report.md
    python run_tests.py --module test_api                  # Run specific module

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tests.test_reporter import run_with_structured_output
import unittest


def main():
    parser = argparse.ArgumentParser(
        description="Run AI Log Triage Agent tests with structured output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests with JSON output
  python run_tests.py --format json --output test-results.json

  # Run all tests with Markdown report
  python run_tests.py --format markdown --output test-report.md

  # Run specific test module
  python run_tests.py --module test_api

  # Run with minimal output
  python run_tests.py --verbosity 0

  # Run tests matching pattern
  python run_tests.py --pattern "test_integration*.py"
        """
    )

    parser.add_argument(
        "--format",
        choices=["json", "yaml", "markdown"],
        default="json",
        help="Output format for structured results (default: json)"
    )

    parser.add_argument(
        "--output",
        help="Output file path for structured results"
    )

    parser.add_argument(
        "--verbosity", "-v",
        type=int,
        choices=[0, 1, 2],
        default=2,
        help="Verbosity level: 0=quiet, 1=normal, 2=verbose (default: 2)"
    )

    parser.add_argument(
        "--module", "-m",
        help="Run specific test module (e.g., test_api, test_integration)"
    )

    parser.add_argument(
        "--pattern", "-p",
        default="test_*.py",
        help="Test file pattern (default: test_*.py)"
    )

    parser.add_argument(
        "--failfast", "-f",
        action="store_true",
        help="Stop on first failure"
    )

    args = parser.parse_args()

    # Build test suite
    loader = unittest.TestLoader()

    if args.module:
        # Run specific module
        try:
            suite = loader.loadTestsFromName(f"tests.{args.module}")
        except Exception as e:
            print(f"Error loading module 'tests.{args.module}': {e}")
            print(f"Make sure the module exists and is named correctly.")
            return 1
    else:
        # Discover all tests
        suite = loader.discover('tests', pattern=args.pattern)

    # Run tests
    result = run_with_structured_output(
        test_suite=suite,
        output_format=args.format,
        output_file=args.output,
        verbosity=args.verbosity
    )

    # Print output file location
    if args.output:
        print(f"\nStructured results written to: {args.output}")

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
