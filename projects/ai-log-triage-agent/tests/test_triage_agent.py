"""
Unit tests for triage_agent.py
"""
import unittest
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_log_triage.triage_agent import TriageAgent, TriageResult, Priority
from ai_log_triage.log_parser import LogEvent


class TestTriageAgent(unittest.TestCase):
    """Test TriageAgent functionality."""

    def setUp(self):
        """Set up test agent."""
        self.agent = TriageAgent()

    def test_build_prompt_includes_all_fields(self):
        """Test that build_prompt includes all log event fields."""
        event = LogEvent(
            raw_content="ERROR: Database connection failed",
            line_number=42,
            timestamp="2025-02-17 14:23:11",
            log_level="ERROR",
            source_file="db.log",
            category="database"
        )

        prompt = self.agent.build_prompt(event, use_truncation=False)

        self.assertIn("db.log", prompt)
        self.assertIn("42", prompt)
        self.assertIn("2025-02-17 14:23:11", prompt)
        self.assertIn("ERROR", prompt)
        self.assertIn("database", prompt)
        self.assertIn("Database connection failed", prompt)

    def test_build_prompt_with_truncation(self):
        """Test that build_prompt uses truncation when enabled."""
        long_content = "\n".join([f"Line {i}" for i in range(100)])
        event = LogEvent(
            raw_content=long_content,
            line_number=1,
            source_file="test.log"
        )

        prompt_truncated = self.agent.build_prompt(event, use_truncation=True)
        prompt_full = self.agent.build_prompt(event, use_truncation=False)

        # Truncated version should be shorter
        self.assertLess(len(prompt_truncated), len(prompt_full))
        self.assertIn("truncated", prompt_truncated)

    def test_parse_llm_response_valid(self):
        """Test parsing a valid LLM response."""
        event = LogEvent(
            raw_content="ERROR: Test error",
            line_number=1,
            source_file="test.log"
        )

        llm_response = """{
    "summary": "Database connection timeout occurred.",
    "classification": "Database Error",
    "priority": "HIGH",
    "suggested_owner": "Database Team",
    "root_cause": "Connection pool exhausted due to unclosed connections.",
    "action_items": [
        "Review connection pool configuration",
        "Check for connection leaks in application code",
        "Monitor database connection metrics"
    ]
}"""

        result = self.agent.parse_llm_response(llm_response, event)

        self.assertIsInstance(result, TriageResult)
        self.assertIn("Database connection timeout", result.summary)
        self.assertIn("Database Error", result.classification)
        self.assertEqual(result.priority, Priority.HIGH)
        self.assertIn("Database Team", result.suggested_owner)
        self.assertIn("Connection pool", result.root_cause)
        self.assertIsInstance(result.action_items, list)
        self.assertGreater(len(result.action_items), 0)

    def test_parse_llm_response_missing_fields(self):
        """Test parsing LLM response with missing fields."""
        event = LogEvent(
            raw_content="ERROR: Test error",
            line_number=1,
            source_file="test.log"
        )

        llm_response = """{
    "summary": "Something went wrong."
}"""

        result = self.agent.parse_llm_response(llm_response, event)

        self.assertIsInstance(result, TriageResult)
        self.assertIn("Something went wrong", result.summary)
        # Should have defaults for missing fields
        self.assertEqual(result.classification, "Unknown")
        self.assertEqual(result.priority, Priority.MEDIUM)

    def test_parse_llm_response_priority_variations(self):
        """Test priority parsing with various formats."""
        event = LogEvent(
            raw_content="ERROR: Test",
            line_number=1,
            source_file="test.log"
        )

        test_cases = [
            ("CRITICAL", Priority.CRITICAL),
            ("critical", Priority.CRITICAL),
            ("High", Priority.HIGH),
            ("medium", Priority.MEDIUM),
            ("low", Priority.LOW),
            ("info", Priority.INFO),
            ("unknown", Priority.MEDIUM),  # Default for unknown
        ]

        for priority_value, expected_priority in test_cases:
            with self.subTest(priority=priority_value):
                llm_response = f'{{"summary": "Test", "priority": "{priority_value}"}}'
                result = self.agent.parse_llm_response(llm_response, event)
                self.assertEqual(result.priority, expected_priority)

    def test_format_triage_result_text(self):
        """Test text formatting of triage result using __str__."""
        event = LogEvent(
            raw_content="ERROR: Test error\nStack trace line",
            line_number=42,
            timestamp="2025-02-17 14:23:11",
            log_level="ERROR",
            source_file="test.log",
            category="general"
        )

        result = TriageResult(
            log_event=event,
            summary="Test summary",
            classification="Test Error",
            priority=Priority.HIGH,
            suggested_owner="Test Team",
            root_cause="Test root cause",
            action_items=["Action 1", "Action 2"],
            raw_llm_response="Raw response"
        )

        formatted = str(result)

        self.assertIn("test.log", formatted)
        self.assertIn("42", formatted)
        self.assertIn("HIGH", formatted)
        self.assertIn("Test Error", formatted)
        self.assertIn("Test Team", formatted)
        self.assertIn("Test summary", formatted)
        self.assertIn("Test root cause", formatted)
        self.assertIn("Action 1", formatted)
        self.assertIn("Action 2", formatted)

    def test_format_triage_result_json(self):
        """Test JSON formatting of triage result using to_dict."""
        import json

        event = LogEvent(
            raw_content="ERROR: Test",
            line_number=1,
            source_file="test.log"
        )

        result = TriageResult(
            log_event=event,
            summary="Test",
            classification="Test Error",
            priority=Priority.HIGH,
            suggested_owner="Team",
            root_cause="Cause",
            action_items=["Action"],
            raw_llm_response="Raw"
        )

        result_dict = result.to_dict()

        # Should be valid dict that can be converted to JSON
        self.assertEqual(result_dict['summary'], "Test")
        self.assertEqual(result_dict['classification'], "Test Error")
        self.assertEqual(result_dict['priority'], "HIGH")

    def test_generate_summary_report_empty(self):
        """Test summary report with no results."""
        report = self.agent.generate_summary_report([])

        self.assertIn("No triage results", report)

    def test_generate_summary_report_with_results(self):
        """Test summary report with multiple results."""
        event1 = LogEvent(raw_content="Error 1", line_number=1, source_file="test.log")
        event2 = LogEvent(raw_content="Error 2", line_number=2, source_file="test.log")

        results = [
            TriageResult(
                log_event=event1,
                summary="First error",
                classification="Type A",
                priority=Priority.CRITICAL,
                suggested_owner="Team A",
                root_cause="Cause 1",
                action_items=["Action 1"],
                raw_llm_response="Raw 1"
            ),
            TriageResult(
                log_event=event2,
                summary="Second error",
                classification="Type B",
                priority=Priority.HIGH,
                suggested_owner="Team B",
                root_cause="Cause 2",
                action_items=["Action 2"],
                raw_llm_response="Raw 2"
            ),
        ]

        report = self.agent.generate_summary_report(results)

        self.assertIn("2", report)
        self.assertIn("CRITICAL", report)
        self.assertIn("HIGH", report)
        self.assertIn("Type A", report)
        self.assertIn("Type B", report)


if __name__ == "__main__":
    unittest.main()
