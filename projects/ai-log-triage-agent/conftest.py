"""
Pytest configuration and fixtures for AI Log Triage Agent.

This file is automatically loaded by pytest and provides:
- Structured JSON test results
- Custom markers
- Shared fixtures

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""
import json
import pytest
from datetime import datetime
from pathlib import Path


# Test result collector
class StructuredResultCollector:
    """Collects test results in structured format."""

    def __init__(self):
        self.results = []
        self.start_time = None

    def add_result(self, nodeid, outcome, duration, longrepr=None):
        """Add a test result."""
        parts = nodeid.split("::")

        result = {
            "test_id": nodeid,
            "file": parts[0] if len(parts) > 0 else "unknown",
            "class": parts[1] if len(parts) > 1 else None,
            "method": parts[2] if len(parts) > 2 else parts[1] if len(parts) > 1 else "unknown",
            "outcome": outcome,  # passed, failed, skipped, error
            "duration_seconds": round(duration, 3),
            "timestamp": datetime.now().isoformat(),
            "error_message": str(longrepr) if longrepr else None
        }

        self.results.append(result)

    def get_summary(self):
        """Get summary statistics."""
        total = len(self.results)
        passed = len([r for r in self.results if r["outcome"] == "passed"])
        failed = len([r for r in self.results if r["outcome"] == "failed"])
        skipped = len([r for r in self.results if r["outcome"] == "skipped"])
        errors = len([r for r in self.results if r["outcome"] == "error"])

        return {
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "success_rate": round((passed / total * 100), 2) if total > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "tests": self.results
        }


# Global collector instance
collector = StructuredResultCollector()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to collect test results."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":  # Only collect the actual test call, not setup/teardown
        collector.add_result(
            nodeid=item.nodeid,
            outcome=report.outcome,
            duration=report.duration,
            longrepr=report.longreprtext if hasattr(report, 'longreprtext') else None
        )


def pytest_sessionfinish(session, exitstatus):
    """Hook called after all tests complete."""
    # Get output format from command line option (if available)
    output_file = session.config.getoption("--json-report", default=None)

    if output_file:
        summary = collector.get_summary()

        # Write JSON report
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\nStructured test results written to: {output_file}")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--json-report",
        action="store",
        default=None,
        help="Path to JSON output file for structured test results"
    )


# Shared fixtures

@pytest.fixture
def mock_llm_response():
    """Fixture providing a mock LLM response."""
    return """{
        "summary": "Test error occurred",
        "classification": "Test Error",
        "priority": "HIGH",
        "suggested_owner": "Test Team",
        "root_cause": "Test root cause",
        "action_items": ["Action 1", "Action 2"]
    }"""


@pytest.fixture
def sample_log_event():
    """Fixture providing a sample LogEvent for testing."""
    from ai_log_triage.log_parser import LogEvent

    return LogEvent(
        raw_content="2025-02-17 14:23:11 ERROR: Test error",
        line_number=1,
        source_file="test.log",
        timestamp="2025-02-17 14:23:11",
        log_level="ERROR",
        category="general"
    )


@pytest.fixture
def temp_log_file(tmp_path):
    """Fixture providing a temporary log file."""
    log_file = tmp_path / "test.log"
    log_file.write_text("2025-02-17 14:23:11 ERROR: Test error\n")
    return log_file
