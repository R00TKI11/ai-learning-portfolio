"""
Test Reporter for AI Log Triage Agent

Provides structured, machine-readable test output in multiple formats
while maintaining human readability.

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""
import json
import time
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys


class StructuredTestResult(unittest.TextTestResult):
    """Enhanced test result that captures structured data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_results = []
        self.start_time = None
        self.end_time = None
        self.suite_start_time = time.time()

    def startTest(self, test):
        """Called when a test starts."""
        super().startTest(test)
        self.start_time = time.time()

    def addSuccess(self, test):
        """Called when a test passes."""
        super().addSuccess(test)
        self._record_result(test, "passed", None)

    def addError(self, test, err):
        """Called when a test has an error."""
        super().addError(test, err)
        self._record_result(test, "error", self._exc_info_to_string(err, test))

    def addFailure(self, test, err):
        """Called when a test fails."""
        super().addFailure(test, err)
        self._record_result(test, "failed", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        """Called when a test is skipped."""
        super().addSkip(test, reason)
        self._record_result(test, "skipped", reason)

    def _record_result(self, test, status: str, message: Optional[str]):
        """Record structured test result."""
        duration = time.time() - self.start_time if self.start_time else 0

        # Parse test information
        test_id = test.id()
        parts = test_id.split('.')

        result = {
            "test_id": test_id,
            "module": parts[0] if len(parts) > 0 else "unknown",
            "class": parts[1] if len(parts) > 1 else "unknown",
            "method": parts[2] if len(parts) > 2 else "unknown",
            "status": status,
            "duration_seconds": round(duration, 3),
            "timestamp": datetime.now().isoformat(),
            "message": message
        }

        self.test_results.append(result)

    def get_summary(self) -> Dict[str, Any]:
        """Get structured summary of test run."""
        total_duration = time.time() - self.suite_start_time

        return {
            "summary": {
                "total_tests": self.testsRun,
                "passed": len([r for r in self.test_results if r["status"] == "passed"]),
                "failed": len(self.failures),
                "errors": len(self.errors),
                "skipped": len(self.skipped),
                "duration_seconds": round(total_duration, 3),
                "timestamp": datetime.now().isoformat(),
                "success_rate": round((len([r for r in self.test_results if r["status"] == "passed"]) / self.testsRun * 100), 2) if self.testsRun > 0 else 0
            },
            "tests": self.test_results
        }


class StructuredTestRunner(unittest.TextTestRunner):
    """Test runner that produces structured output."""

    resultclass = StructuredTestResult

    def __init__(self, output_format="json", output_file=None, *args, **kwargs):
        """
        Initialize runner.

        Args:
            output_format: Format for structured output (json, yaml, or markdown)
            output_file: Optional file to write structured output to
        """
        super().__init__(*args, **kwargs)
        self.output_format = output_format
        self.output_file = output_file

    def run(self, test):
        """Run tests and generate structured output."""
        result = super().run(test)

        # Generate structured output
        summary = result.get_summary()

        # Write to file if specified
        if self.output_file:
            self._write_structured_output(summary)

        # Also print to console
        self._print_structured_summary(summary)

        return result

    def _write_structured_output(self, summary: Dict[str, Any]):
        """Write structured output to file."""
        output_path = Path(self.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.output_format == "json":
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2)

        elif self.output_format == "markdown":
            with open(output_path, 'w') as f:
                f.write(self._format_markdown(summary))

        elif self.output_format == "yaml":
            try:
                import yaml
                with open(output_path, 'w') as f:
                    yaml.dump(summary, f, default_flow_style=False)
            except ImportError:
                print("Warning: PyYAML not installed. Install with: pip install pyyaml")
                # Fallback to JSON
                with open(output_path, 'w') as f:
                    json.dump(summary, f, indent=2)

    def _print_structured_summary(self, summary: Dict[str, Any]):
        """Print human-readable summary to console."""
        s = summary["summary"]

        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Total Tests:    {s['total_tests']}")
        print(f"Passed:         {s['passed']} ✓")
        print(f"Failed:         {s['failed']} ✗")
        print(f"Errors:         {s['errors']} ⚠")
        print(f"Skipped:        {s['skipped']} ○")
        print(f"Success Rate:   {s['success_rate']}%")
        print(f"Duration:       {s['duration_seconds']}s")
        print(f"Timestamp:      {s['timestamp']}")
        print("=" * 70)

        # Show failed/error tests
        failed_tests = [t for t in summary["tests"] if t["status"] in ["failed", "error"]]
        if failed_tests:
            print("\nFAILED/ERROR TESTS:")
            for test in failed_tests:
                print(f"  ✗ {test['class']}.{test['method']} ({test['status']})")
                if test['message']:
                    # Print first line of message
                    first_line = test['message'].split('\n')[0]
                    print(f"    {first_line[:70]}...")

        print()

    def _format_markdown(self, summary: Dict[str, Any]) -> str:
        """Format summary as markdown."""
        s = summary["summary"]

        md = f"""# Test Results

**Generated:** {s['timestamp']}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {s['total_tests']} |
| Passed | {s['passed']} ✓ |
| Failed | {s['failed']} ✗ |
| Errors | {s['errors']} ⚠ |
| Skipped | {s['skipped']} ○ |
| Success Rate | {s['success_rate']}% |
| Duration | {s['duration_seconds']}s |

## Test Results by Module

"""
        # Group by module
        by_module = {}
        for test in summary["tests"]:
            module = test["module"]
            if module not in by_module:
                by_module[module] = {"passed": 0, "failed": 0, "error": 0, "skipped": 0}

            status = test["status"]
            if status == "passed":
                by_module[module]["passed"] += 1
            elif status == "failed":
                by_module[module]["failed"] += 1
            elif status == "error":
                by_module[module]["error"] += 1
            elif status == "skipped":
                by_module[module]["skipped"] += 1

        md += "| Module | Passed | Failed | Errors | Skipped |\n"
        md += "|--------|--------|--------|--------|--------|\n"
        for module, counts in sorted(by_module.items()):
            md += f"| {module} | {counts['passed']} | {counts['failed']} | {counts['error']} | {counts['skipped']} |\n"

        # Failed tests detail
        failed_tests = [t for t in summary["tests"] if t["status"] in ["failed", "error"]]
        if failed_tests:
            md += "\n## Failed Tests\n\n"
            for test in failed_tests:
                md += f"### {test['class']}.{test['method']}\n"
                md += f"- **Status:** {test['status']}\n"
                md += f"- **Duration:** {test['duration_seconds']}s\n"
                if test['message']:
                    md += f"- **Message:**\n```\n{test['message'][:500]}\n```\n"
                md += "\n"

        return md


def run_with_structured_output(
    test_suite=None,
    output_format="json",
    output_file=None,
    verbosity=2
):
    """
    Run tests with structured output.

    Args:
        test_suite: Test suite to run (if None, discovers all tests)
        output_format: Format for output (json, yaml, markdown)
        output_file: Path to output file
        verbosity: Verbosity level (0, 1, 2)

    Returns:
        Test result object
    """
    if test_suite is None:
        loader = unittest.TestLoader()
        test_suite = loader.discover('tests', pattern='test_*.py')

    runner = StructuredTestRunner(
        output_format=output_format,
        output_file=output_file,
        verbosity=verbosity
    )

    return runner.run(test_suite)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run tests with structured output")
    parser.add_argument(
        "--format",
        choices=["json", "yaml", "markdown"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--output",
        help="Output file path"
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        choices=[0, 1, 2],
        default=2,
        help="Verbosity level"
    )
    parser.add_argument(
        "--pattern",
        default="test_*.py",
        help="Test file pattern"
    )

    args = parser.parse_args()

    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern=args.pattern)

    # Run with structured output
    result = run_with_structured_output(
        test_suite=suite,
        output_format=args.format,
        output_file=args.output,
        verbosity=args.verbosity
    )

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
