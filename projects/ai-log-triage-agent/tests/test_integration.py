"""
Integration tests for AI Log Triage Agent

Tests the full stack: CLI + API + Parser + Triage Agent working together.
Uses mocked LLM responses to avoid real API calls.

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import json
import tempfile
import shutil

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from ai_log_triage.api import app
from ai_log_triage.cli import main as cli_main
from ai_log_triage.triage_agent import TriageResult, Priority
from ai_log_triage.log_parser import LogEvent


# Mock LLM response for integration tests
MOCK_LLM_RESPONSE = """{
    "summary": "Database connection timeout occurred.",
    "classification": "Database Error",
    "priority": "HIGH",
    "suggested_owner": "Database Team",
    "root_cause": "Connection pool exhausted.",
    "action_items": [
        "Review connection pool configuration",
        "Check for connection leaks"
    ]
}"""


class TestCLIToAPIIntegration(unittest.TestCase):
    """Test CLI interacting with API endpoints."""

    def setUp(self):
        """Set up test environment."""
        self.client = TestClient(app)
        self.test_dir = tempfile.mkdtemp()
        self.test_log = Path(self.test_dir) / "test.log"

        # Create a test log file
        self.test_log.write_text(
            "2025-02-17 14:23:11 ERROR: Database connection failed\n"
            "2025-02-17 14:24:00 WARN: Retry attempt 1\n"
        )

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('ai_log_triage.llm_client.call_llm')
    def test_cli_processes_log_file(self, mock_llm):
        """Test CLI can process a log file end-to-end."""
        mock_llm.return_value = MOCK_LLM_RESPONSE

        # Run CLI with test file
        exit_code = cli_main([
            '--input', str(self.test_log),
            '--max-events', '1',
            '--format', 'json'
        ])

        self.assertEqual(exit_code, 0)
        mock_llm.assert_called_once()

    @patch('ai_log_triage.llm_client.call_llm')
    def test_cli_dry_run_no_llm_calls(self, mock_llm):
        """Test CLI dry-run mode doesn't call LLM."""
        # Run CLI in dry-run mode
        exit_code = cli_main([
            '--input', str(self.test_log),
            '--dry-run'
        ])

        self.assertEqual(exit_code, 0)
        mock_llm.assert_not_called()

    @patch('ai_log_triage.api.TriageAgent')
    def test_api_triage_flow(self, mock_agent_class):
        """Test API triage flow end-to-end."""
        # Mock the agent
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_event = LogEvent(
            raw_content="ERROR: Test",
            line_number=1,
            source_file="test.log"
        )
        mock_result = TriageResult(
            log_event=mock_event,
            summary="Test summary",
            classification="Test Error",
            priority=Priority.HIGH,
            suggested_owner="Test Team",
            root_cause="Test cause",
            action_items=["Fix it"],
            raw_llm_response=MOCK_LLM_RESPONSE
        )
        mock_agent.triage_event.return_value = mock_result

        # Call API
        response = self.client.post(
            "/triage",
            json={"log_text": "ERROR: Test"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["priority"], "HIGH")
        self.assertIn("action_items", data)


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete workflows from log file to triage result."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.output_file = Path(self.test_dir) / "results.json"

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('ai_log_triage.llm_client.call_llm')
    def test_full_cli_workflow_with_output(self, mock_llm):
        """Test complete CLI workflow: parse -> triage -> save results."""
        mock_llm.return_value = MOCK_LLM_RESPONSE

        # Create test log
        test_log = Path(self.test_dir) / "test.log"
        test_log.write_text("2025-02-17 14:23:11 ERROR: Test error\n")

        # Run CLI
        exit_code = cli_main([
            '--input', str(test_log),
            '--output', str(self.output_file),
            '--format', 'json'
        ])

        self.assertEqual(exit_code, 0)

        # Verify output file was created
        self.assertTrue(self.output_file.exists())

        # Verify output content
        with open(self.output_file, 'r') as f:
            results = json.load(f)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn("summary", results[0])
        self.assertIn("priority", results[0])

    @patch('ai_log_triage.llm_client.call_llm')
    def test_batch_processing_workflow(self, mock_llm):
        """Test batch processing multiple log entries."""
        mock_llm.return_value = MOCK_LLM_RESPONSE

        # Create test log with multiple entries
        test_log = Path(self.test_dir) / "test.log"
        test_log.write_text(
            "2025-02-17 14:23:11 ERROR: Error 1\n"
            "2025-02-17 14:24:00 ERROR: Error 2\n"
            "2025-02-17 14:25:00 WARN: Warning 1\n"
        )

        # Run CLI
        exit_code = cli_main([
            '--input', str(test_log),
            '--max-events', '3',
            '--format', 'summary'
        ])

        self.assertEqual(exit_code, 0)
        # LLM should be called for each event
        self.assertEqual(mock_llm.call_count, 3)


class TestParserToTriageFlow(unittest.TestCase):
    """Test data flow from parser to triage agent."""

    @patch('ai_log_triage.llm_client.call_llm')
    def test_parser_output_to_triage_input(self, mock_llm):
        """Test that parser output correctly feeds into triage agent."""
        from ai_log_triage.log_parser import LogParser
        from ai_log_triage.triage_agent import TriageAgent

        mock_llm.return_value = MOCK_LLM_RESPONSE

        # Parse a log entry
        parser = LogParser()
        log_content = "2025-02-17 14:23:11 ERROR: Database timeout"
        events = list(parser.chunk_by_event(log_content, source_file="test.log"))

        self.assertEqual(len(events), 1)
        event = events[0]

        # Triage the parsed event
        agent = TriageAgent()
        result = agent.triage_event(event)

        # Verify the result
        self.assertIsInstance(result, TriageResult)
        self.assertEqual(result.log_event, event)
        self.assertIn("Database", result.summary)

    @patch('ai_log_triage.llm_client.call_llm')
    def test_multiline_event_parsing_and_triage(self, mock_llm):
        """Test parsing multi-line events and triaging them."""
        from ai_log_triage.log_parser import LogParser
        from ai_log_triage.triage_agent import TriageAgent

        mock_llm.return_value = MOCK_LLM_RESPONSE

        # Multi-line log entry
        log_content = """2025-02-17 14:23:11 ERROR: NullPointerException
    at com.example.Service.process(Service.java:42)
    at com.example.Handler.handle(Handler.java:15)
2025-02-17 14:24:00 INFO: Recovery attempted"""

        parser = LogParser()
        events = list(parser.chunk_by_event(log_content, source_file="test.log"))

        # Should parse into 2 events
        self.assertEqual(len(events), 2)

        # Triage the first (multi-line) event
        agent = TriageAgent()
        result = agent.triage_event(events[0])

        # Verify multi-line content was preserved
        self.assertIn("Service.java", result.log_event.raw_content)
        self.assertIn("Handler.handle", result.log_event.raw_content)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in integration scenarios."""

    @patch('ai_log_triage.llm_client.call_llm')
    def test_llm_error_handling(self, mock_llm):
        """Test graceful handling of LLM errors."""
        # Simulate LLM error
        mock_llm.side_effect = RuntimeError("LLM API error")

        test_dir = tempfile.mkdtemp()
        try:
            test_log = Path(test_dir) / "test.log"
            test_log.write_text("ERROR: Test\n")

            # CLI should handle the error gracefully
            exit_code = cli_main([
                '--input', str(test_log),
                '--max-events', '1'
            ])

            # Should exit with error code
            self.assertNotEqual(exit_code, 0)

        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_invalid_log_file(self):
        """Test handling of non-existent log file."""
        exit_code = cli_main([
            '--input', '/nonexistent/file.log'
        ])

        self.assertNotEqual(exit_code, 0)

    def test_api_invalid_request(self):
        """Test API error handling for invalid requests."""
        client = TestClient(app)

        # Missing required field
        response = client.post("/triage", json={})
        self.assertEqual(response.status_code, 422)

        # Invalid JSON
        response = client.post(
            "/triage",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 422)


class TestConfigurationIntegration(unittest.TestCase):
    """Test configuration loading and usage across components."""

    @patch('ai_log_triage.config.settings')
    def test_config_used_by_llm_client(self, mock_settings):
        """Test that LLM client uses configuration settings."""
        from ai_log_triage import llm_client

        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_ENDPOINT = "https://test.api"
        mock_settings.LLM_DEFAULT_MODEL = "test-model"
        mock_settings.LLM_TIMEOUT = 60
        mock_settings.LLM_MAX_TOKENS = 512
        mock_settings.validate.return_value = (True, [])

        with patch('ai_log_triage.llm_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": MOCK_LLM_RESPONSE}}]
            }
            mock_post.return_value = mock_response

            result = llm_client.call_llm("test prompt")

            # Verify correct settings were used
            mock_post.assert_called_once()
            call_args = mock_post.call_args

            self.assertEqual(call_args[0][0], "https://test.api")
            self.assertIn("Authorization", call_args[1]["headers"])
            self.assertEqual(call_args[1]["timeout"], 60)
            self.assertEqual(call_args[1]["json"]["max_tokens"], 512)


if __name__ == "__main__":
    # Check for required dependencies
    try:
        import fastapi
        from fastapi.testclient import TestClient
    except ImportError:
        print("Error: FastAPI not installed.")
        print("Install with: pip install -r requirements-dev.txt")
        sys.exit(1)

    unittest.main()
