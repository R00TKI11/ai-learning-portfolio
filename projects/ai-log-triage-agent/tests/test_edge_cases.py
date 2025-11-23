"""
Edge case and validation tests for AI Log Triage Agent

Tests parsing and handling of unusual, malformed, and edge case inputs.

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""
import unittest
from unittest.mock import patch
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_log_triage.log_parser import LogParser, LogEvent
from ai_log_triage.triage_agent import TriageAgent, Priority
from ai_log_triage.config import settings


class TestEmptyAndWhitespaceHandling(unittest.TestCase):
    """Test handling of empty and whitespace-only inputs."""

    def setUp(self):
        """Set up test environment."""
        self.parser = LogParser()

    def test_empty_string(self):
        """Test parsing empty string."""
        events = list(self.parser.chunk_by_event("", source_file="test.log"))
        self.assertEqual(len(events), 0)

    def test_whitespace_only(self):
        """Test parsing whitespace-only string."""
        events = list(self.parser.chunk_by_event("   \n  \t  \n   ", source_file="test.log"))
        self.assertEqual(len(events), 0)

    def test_single_empty_line(self):
        """Test parsing single empty line."""
        events = list(self.parser.chunk_by_event("\n", source_file="test.log"))
        self.assertEqual(len(events), 0)

    def test_multiple_empty_lines(self):
        """Test parsing multiple empty lines."""
        events = list(self.parser.chunk_by_event("\n\n\n\n", source_file="test.log"))
        self.assertEqual(len(events), 0)

    def test_lines_between_empty_lines(self):
        """Test parsing logs with many empty lines between entries."""
        log_content = "ERROR: First\n\n\n\nERROR: Second\n\n\nERROR: Third"
        events = list(self.parser.chunk_by_line(log_content, source_file="test.log"))

        # Line-by-line mode should parse each non-empty line
        self.assertGreater(len(events), 0)
        # Verify the content exists somewhere
        all_content = "".join([e.raw_content for e in events])
        self.assertIn("First", all_content)
        self.assertIn("Second", all_content)
        self.assertIn("Third", all_content)


class TestMalformedLogEntries(unittest.TestCase):
    """Test handling of malformed log entries."""

    def setUp(self):
        """Set up test environment."""
        self.parser = LogParser()

    def test_no_timestamp(self):
        """Test parsing log without timestamp."""
        events = list(self.parser.chunk_by_event(
            "ERROR: Something bad happened",
            source_file="test.log"
        ))

        # Parser should still create events even without timestamp
        self.assertGreater(len(events), 0)
        # Timestamp may be None
        # Content should be present
        self.assertIn("ERROR", events[0].raw_content)

    def test_no_log_level(self):
        """Test parsing log without log level."""
        events = list(self.parser.chunk_by_event(
            "2025-02-17 14:23:11 Something happened",
            source_file="test.log"
        ))

        # Should still parse
        self.assertGreater(len(events), 0)
        # Content should be preserved
        self.assertIn("Something happened", events[0].raw_content)

    def test_malformed_timestamp(self):
        """Test parsing log with malformed timestamp."""
        events = list(self.parser.chunk_by_event(
            "2025-99-99 99:99:99 ERROR: Invalid timestamp",
            source_file="test.log"
        ))

        # Should still parse even if timestamp is invalid
        self.assertGreater(len(events), 0)
        self.assertIn("ERROR", events[0].raw_content)

    def test_unusual_log_level(self):
        """Test parsing log with unusual log level."""
        unusual_levels = ["TRACE", "VERBOSE", "FATAL", "EMERGENCY", "DEBUG1"]

        for level in unusual_levels:
            with self.subTest(level=level):
                events = list(self.parser.chunk_by_event(
                    f"{level}: Something happened",
                    source_file="test.log"
                ))

                # Should parse
                self.assertGreater(len(events), 0)
                # Should extract the level
                self.assertEqual(events[0].log_level, level)

    def test_mixed_case_log_level(self):
        """Test parsing log with mixed case log level."""
        events = list(self.parser.chunk_by_event(
            "ErRoR: Mixed case level",
            source_file="test.log"
        ))

        # Should parse
        self.assertGreater(len(events), 0)
        # Should normalize to uppercase
        self.assertEqual(events[0].log_level, "ERROR")


class TestSpecialCharactersAndEncoding(unittest.TestCase):
    """Test handling of special characters and encoding issues."""

    def setUp(self):
        """Set up test environment."""
        self.parser = LogParser()

    def test_unicode_characters(self):
        """Test parsing log with Unicode characters."""
        events = list(self.parser.chunk_by_event(
            "ERROR: User 'José García' failed to authenticate 中文",
            source_file="test.log"
        ))

        self.assertEqual(len(events), 1)
        self.assertIn("José García", events[0].raw_content)
        self.assertIn("中文", events[0].raw_content)

    def test_special_characters(self):
        """Test parsing log with special characters."""
        special_chars = "!@#$%^&*(){}[]<>?/\\|~`"
        events = list(self.parser.chunk_by_event(
            f"ERROR: Special chars: {special_chars}",
            source_file="test.log"
        ))

        self.assertEqual(len(events), 1)
        self.assertIn(special_chars, events[0].raw_content)

    def test_newlines_in_message(self):
        """Test parsing log with embedded newlines."""
        log_content = 'ERROR: Message with\nnewline\ninside'
        events = list(self.parser.chunk_by_line(log_content, source_file="test.log"))

        # In line mode, should split into multiple events
        self.assertGreater(len(events), 1)

    def test_tabs_and_mixed_whitespace(self):
        """Test parsing log with tabs and mixed whitespace."""
        events = list(self.parser.chunk_by_event(
            "ERROR:\tTab\tseparated\t\t  mixed   spaces",
            source_file="test.log"
        ))

        self.assertEqual(len(events), 1)
        self.assertIn("Tab", events[0].raw_content)


class TestVeryLongContent(unittest.TestCase):
    """Test handling of very long log content."""

    def setUp(self):
        """Set up test environment."""
        self.parser = LogParser()

    def test_very_long_single_line(self):
        """Test parsing very long single line."""
        long_line = "ERROR: " + "A" * 10000
        events = list(self.parser.chunk_by_event(long_line, source_file="test.log"))

        self.assertEqual(len(events), 1)
        self.assertEqual(len(events[0].raw_content), len(long_line))

    def test_very_long_multiline_event(self):
        """Test parsing very long multi-line event."""
        lines = ["ERROR: Start"] + [f"    Line {i}" for i in range(1000)]
        log_content = "\n".join(lines)

        events = list(self.parser.chunk_by_event(log_content, source_file="test.log"))

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].raw_content, log_content)

    def test_truncation_behavior(self):
        """Test that truncation works correctly for long content."""
        long_content = "\n".join([f"Line {i}" for i in range(100)])
        event = LogEvent(
            raw_content=long_content,
            line_number=1,
            source_file="test.log"
        )

        truncated = event.truncate_content(max_lines=10, max_chars=500)

        # Should be truncated
        self.assertLess(len(truncated), len(long_content))
        self.assertIn("truncated", truncated.lower())


class TestMixedLogFormats(unittest.TestCase):
    """Test handling of mixed log formats in single file."""

    def setUp(self):
        """Set up test environment."""
        self.parser = LogParser()

    def test_mixed_timestamp_formats(self):
        """Test parsing logs with different timestamp formats."""
        log_content = """2025-02-17 14:23:11 ERROR: Format 1
[2025-02-17 14:24:00] WARN: Format 2
2025-02-17T14:25:00Z INFO: Format 3
Feb 17 14:26:00 ERROR: Format 4"""

        events = list(self.parser.chunk_by_event(log_content, source_file="test.log"))

        self.assertEqual(len(events), 4)
        # All should have timestamps extracted (or None)
        for event in events:
            self.assertIsNotNone(event.raw_content)

    def test_mixed_log_levels(self):
        """Test parsing logs with mixed log level styles."""
        log_content = """ERROR: Style 1
[ERROR] Style 2
<ERROR> Style 3
E: Style 4"""

        events = list(self.parser.chunk_by_event(log_content, source_file="test.log"))

        # Should parse all lines
        self.assertEqual(len(events), 4)

    def test_structured_and_unstructured_logs(self):
        """Test parsing mix of structured and unstructured logs."""
        log_content = """{"level":"ERROR","msg":"JSON log"}
ERROR: Plain text log
<log level="WARN">XML style log</log>"""

        events = list(self.parser.chunk_by_event(log_content, source_file="test.log"))

        # Should parse all formats
        self.assertEqual(len(events), 3)


class TestStackTraceParsing(unittest.TestCase):
    """Test handling of stack traces and multi-line errors."""

    def setUp(self):
        """Set up test environment."""
        self.parser = LogParser()

    def test_java_stack_trace(self):
        """Test parsing Java-style stack trace."""
        log_content = """2025-02-17 14:23:11 ERROR: NullPointerException
    at com.example.Service.process(Service.java:42)
    at com.example.Handler.handle(Handler.java:15)
    at com.example.Main.main(Main.java:8)"""

        events = list(self.parser.chunk_by_event(log_content, source_file="test.log"))

        # Should be parsed as single event
        self.assertEqual(len(events), 1)
        self.assertIn("Service.java:42", events[0].raw_content)
        self.assertIn("Handler.handle", events[0].raw_content)

    def test_python_stack_trace(self):
        """Test parsing Python-style stack trace."""
        log_content = """2025-02-17 14:23:11 ERROR: Exception in process
Traceback (most recent call last):
  File "main.py", line 42, in process
    result = do_work()
  File "worker.py", line 15, in do_work
    raise ValueError("Invalid input")
ValueError: Invalid input"""

        events = list(self.parser.chunk_by_event(log_content, source_file="test.log"))

        # Should be parsed as single event
        self.assertEqual(len(events), 1)
        self.assertIn("Traceback", events[0].raw_content)
        self.assertIn("ValueError", events[0].raw_content)

    def test_deeply_nested_stack_trace(self):
        """Test parsing very deep stack trace."""
        lines = ["ERROR: Exception"] + [f"    at frame{i}" for i in range(50)]
        log_content = "\n".join(lines)

        events = list(self.parser.chunk_by_event(log_content, source_file="test.log"))

        # Should keep all frames together
        self.assertEqual(len(events), 1)
        self.assertIn("frame0", events[0].raw_content)
        self.assertIn("frame49", events[0].raw_content)


class TestConfigurationEdgeCases(unittest.TestCase):
    """Test configuration handling edge cases."""

    @patch.object(settings, 'LLM_API_KEY', None)
    def test_missing_required_config(self):
        """Test behavior with missing required configuration."""
        is_valid, errors = settings.validate()
        self.assertFalse(is_valid)
        # Should have an error about API key
        error_str = " ".join(errors)
        self.assertIn("LLM_API_KEY", error_str)

    @patch.object(settings, 'LLM_TIMEOUT', -1)
    def test_invalid_timeout_config(self):
        """Test behavior with invalid timeout value."""
        is_valid, errors = settings.validate()
        self.assertFalse(is_valid)
        error_str = " ".join(errors)
        self.assertIn("LLM_TIMEOUT", error_str)

    @patch.object(settings, 'LLM_MAX_TOKENS', 0)
    def test_invalid_max_tokens_config(self):
        """Test behavior with invalid max_tokens value."""
        is_valid, errors = settings.validate()
        self.assertFalse(is_valid)
        error_str = " ".join(errors)
        self.assertIn("LLM_MAX_TOKENS", error_str)


class TestLLMResponseEdgeCases(unittest.TestCase):
    """Test handling of unusual LLM responses."""

    def setUp(self):
        """Set up test environment."""
        self.agent = TriageAgent()

    def test_incomplete_json_response(self):
        """Test handling of incomplete JSON from LLM."""
        event = LogEvent(
            raw_content="ERROR: Test",
            line_number=1,
            source_file="test.log"
        )

        # Valid JSON but missing fields
        incomplete_response = '{"summary": "Test summary"}'

        result = self.agent.parse_llm_response(incomplete_response, event)

        # Should have the summary that was provided
        self.assertEqual(result.summary, "Test summary")
        # Should have defaults for missing fields
        self.assertEqual(result.classification, "Unknown")
        self.assertEqual(result.priority, Priority.MEDIUM)
        self.assertEqual(result.suggested_owner, "DevOps")


class TestBoundaryConditions(unittest.TestCase):
    """Test boundary conditions and limits."""

    def setUp(self):
        """Set up test environment."""
        self.parser = LogParser()

    def test_single_character_log(self):
        """Test parsing single character log."""
        events = list(self.parser.chunk_by_event("E", source_file="test.log"))
        self.assertEqual(len(events), 1)

    def test_maximum_line_length(self):
        """Test parsing line at maximum typical length."""
        # Many systems have 8KB line limits
        long_line = "ERROR: " + "X" * 8192
        events = list(self.parser.chunk_by_event(long_line, source_file="test.log"))

        # Should parse the long line
        self.assertGreater(len(events), 0)
        # Content should be preserved (may be split or kept together)
        total_content = "".join([e.raw_content for e in events])
        self.assertIn("ERROR", total_content)

    def test_many_small_events(self):
        """Test parsing many small events."""
        lines = [f"ERROR {i}" for i in range(100)]  # Reduced to 100 for faster tests
        log_content = "\n".join(lines)

        events = list(self.parser.chunk_by_line(log_content, source_file="test.log"))

        # Line mode should create separate events
        self.assertGreater(len(events), 50)  # At least half should parse

    def test_zero_line_number(self):
        """Test handling of zero line number."""
        event = LogEvent(
            raw_content="Test",
            line_number=0,
            source_file="test.log"
        )

        self.assertEqual(event.line_number, 0)

    def test_negative_line_number(self):
        """Test handling of negative line number."""
        event = LogEvent(
            raw_content="Test",
            line_number=-1,
            source_file="test.log"
        )

        # Should accept negative (though unusual)
        self.assertEqual(event.line_number, -1)


if __name__ == "__main__":
    unittest.main()
