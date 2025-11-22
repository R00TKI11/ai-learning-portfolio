"""
Unit tests for FastAPI endpoints

Tests the API endpoints without requiring actual LLM calls.
"""
import unittest
from unittest.mock import Mock, patch
from pathlib import Path
import sys
import json

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from ai_log_triage.api import app
from ai_log_triage.triage_agent import TriageResult, Priority
from ai_log_triage.log_parser import LogEvent


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints."""

    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test root endpoint returns API information."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("name", data)
        self.assertIn("version", data)
        self.assertIn("docs", data)
        self.assertEqual(data["docs"], "/docs")

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("version", data)
        self.assertIn("llm_configured", data)

    def test_triage_single_validation_empty_text(self):
        """Test triage endpoint rejects empty log text."""
        response = self.client.post(
            "/triage",
            json={"log_text": ""}
        )

        self.assertEqual(response.status_code, 422)

    def test_triage_single_validation_too_large(self):
        """Test triage endpoint rejects oversized log text."""
        large_text = "x" * 200000  # 200KB
        response = self.client.post(
            "/triage",
            json={"log_text": large_text}
        )

        self.assertEqual(response.status_code, 422)

    @patch('ai_log_triage.api.TriageAgent')
    def test_triage_single_success(self, mock_agent_class):
        """Test successful single triage request."""
        # Mock the triage agent
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        # Create mock result
        mock_event = LogEvent(
            raw_content="ERROR: Test error",
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
            raw_llm_response="Test response"
        )
        mock_agent.triage_event.return_value = mock_result

        # Make request
        response = self.client.post(
            "/triage",
            json={
                "log_text": "2025-02-17 14:23:11 ERROR: Test error",
                "source_file": "test.log"
            }
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["summary"], "Test summary")
        self.assertEqual(data["classification"], "Test Error")
        self.assertEqual(data["priority"], "HIGH")

    def test_triage_batch_validation_empty_list(self):
        """Test batch triage rejects empty log list."""
        response = self.client.post(
            "/triage/batch",
            json={"logs": []}
        )

        self.assertEqual(response.status_code, 422)

    def test_triage_batch_validation_too_many(self):
        """Test batch triage rejects too many logs."""
        response = self.client.post(
            "/triage/batch",
            json={"logs": ["test"] * 200}  # Exceeds max of 100
        )

        self.assertEqual(response.status_code, 422)

    @patch('ai_log_triage.api.TriageAgent')
    def test_triage_batch_success(self, mock_agent_class):
        """Test successful batch triage request."""
        # Mock the triage agent
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        # Create mock results
        mock_event1 = LogEvent(
            raw_content="ERROR: Error 1",
            line_number=1,
            source_file="test.log"
        )
        mock_event2 = LogEvent(
            raw_content="WARN: Warning 1",
            line_number=2,
            source_file="test.log"
        )

        mock_result1 = TriageResult(
            log_event=mock_event1,
            summary="Error summary",
            classification="Error",
            priority=Priority.CRITICAL,
            suggested_owner="Team A",
            root_cause="Cause 1",
            action_items=["Fix 1"],
            raw_llm_response="Response 1"
        )
        mock_result2 = TriageResult(
            log_event=mock_event2,
            summary="Warning summary",
            classification="Warning",
            priority=Priority.MEDIUM,
            suggested_owner="Team B",
            root_cause="Cause 2",
            action_items=["Fix 2"],
            raw_llm_response="Response 2"
        )

        mock_agent.triage_batch.return_value = [mock_result1, mock_result2]

        # Make request
        response = self.client.post(
            "/triage/batch",
            json={
                "logs": [
                    "2025-02-17 14:23:11 ERROR: Error 1",
                    "2025-02-17 14:24:12 WARN: Warning 1"
                ]
            }
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_events"], 2)
        self.assertEqual(len(data["results"]), 2)
        self.assertIn("priority_breakdown", data)
        self.assertEqual(data["priority_breakdown"]["CRITICAL"], 1)
        self.assertEqual(data["priority_breakdown"]["MEDIUM"], 1)

    def test_openapi_schema(self):
        """Test that OpenAPI schema is accessible."""
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertIn("openapi", schema)
        self.assertIn("info", schema)
        self.assertIn("paths", schema)
        # Verify our endpoints are documented
        self.assertIn("/health", schema["paths"])
        self.assertIn("/triage", schema["paths"])
        self.assertIn("/triage/batch", schema["paths"])


class TestAPIModels(unittest.TestCase):
    """Test Pydantic models for API."""

    def test_triage_request_single_defaults(self):
        """Test TriageRequestSingle with default values."""
        from ai_log_triage.api import TriageRequestSingle, ChunkMethod

        request = TriageRequestSingle(log_text="Test log")

        self.assertEqual(request.log_text, "Test log")
        self.assertIsNone(request.source_file)
        self.assertEqual(request.chunk_method, ChunkMethod.EVENT)
        self.assertEqual(request.max_tokens, 1024)
        self.assertIsNone(request.model)

    def test_triage_request_single_validation(self):
        """Test TriageRequestSingle validation."""
        from ai_log_triage.api import TriageRequestSingle
        from pydantic import ValidationError

        # Empty text should fail
        with self.assertRaises(ValidationError):
            TriageRequestSingle(log_text="")

        # Too large should fail
        with self.assertRaises(ValidationError):
            TriageRequestSingle(log_text="x" * 200000)

    def test_triage_request_batch_validation(self):
        """Test TriageRequestBatch validation."""
        from ai_log_triage.api import TriageRequestBatch
        from pydantic import ValidationError

        # Empty list should fail
        with self.assertRaises(ValidationError):
            TriageRequestBatch(logs=[])

        # Too many logs should fail
        with self.assertRaises(ValidationError):
            TriageRequestBatch(logs=["test"] * 200)


if __name__ == "__main__":
    # Check if fastapi is installed
    try:
        import fastapi
        from fastapi.testclient import TestClient
    except ImportError:
        print("Error: FastAPI or test dependencies not installed.")
        print("Install with: pip install fastapi[all]")
        sys.exit(1)

    unittest.main()
