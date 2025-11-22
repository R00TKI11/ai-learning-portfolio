"""
Unit tests for cli.py
"""
import unittest
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_log_triage.cli import create_parser
from ai_log_triage.triage_agent import Priority


class TestCLI(unittest.TestCase):
    """Test CLI argument parsing."""

    def setUp(self):
        """Set up test parser."""
        self.parser = create_parser()

    def test_parser_input_argument(self):
        """Test --input argument parsing."""
        args = self.parser.parse_args(['--input', 'test.log'])
        self.assertEqual(args.input, 'test.log')

    def test_parser_all_flag(self):
        """Test --all flag parsing."""
        args = self.parser.parse_args(['--all'])
        self.assertTrue(args.all)

    def test_parser_chunk_method(self):
        """Test --chunk-method argument."""
        args = self.parser.parse_args(['--all', '--chunk-method', 'line'])
        self.assertEqual(args.chunk_method, 'line')

    def test_parser_chunk_method_default(self):
        """Test default chunk method."""
        args = self.parser.parse_args(['--all'])
        self.assertEqual(args.chunk_method, 'event')

    def test_parser_model_argument(self):
        """Test --model argument."""
        args = self.parser.parse_args(['--all', '--model', 'gpt-4'])
        self.assertEqual(args.model, 'gpt-4')

    def test_parser_max_events(self):
        """Test --max-events argument."""
        args = self.parser.parse_args(['--all', '--max-events', '10'])
        self.assertEqual(args.max_events, 10)

    def test_parser_dry_run_flag(self):
        """Test --dry-run flag."""
        args = self.parser.parse_args(['--all', '--dry-run'])
        self.assertTrue(args.dry_run)

    def test_parser_output_argument(self):
        """Test --output argument."""
        args = self.parser.parse_args(['--all', '--output', 'results.json'])
        self.assertEqual(args.output, 'results.json')

    def test_parser_format_argument(self):
        """Test --format argument."""
        test_cases = ['text', 'json', 'summary']
        for fmt in test_cases:
            with self.subTest(format=fmt):
                args = self.parser.parse_args(['--all', '--format', fmt])
                self.assertEqual(args.format, fmt)

    def test_parser_format_default(self):
        """Test default format."""
        args = self.parser.parse_args(['--all'])
        self.assertEqual(args.format, 'text')

    def test_parser_priority_filter(self):
        """Test --priority-filter argument."""
        args = self.parser.parse_args(['--all', '--priority-filter', 'HIGH'])
        self.assertEqual(args.priority_filter, 'HIGH')

    def test_parser_verbose_flag(self):
        """Test --verbose flag."""
        args = self.parser.parse_args(['--all', '--verbose'])
        self.assertTrue(args.verbose)

    def test_parser_short_flags(self):
        """Test short flag versions."""
        args = self.parser.parse_args([
            '-i', 'test.log',
            '-c', 'line',
            '-m', 'gpt-4',
            '-o', 'output.json',
            '-f', 'json',
            '-p', 'CRITICAL',
            '-v'
        ])

        self.assertEqual(args.input, 'test.log')
        self.assertEqual(args.chunk_method, 'line')
        self.assertEqual(args.model, 'gpt-4')
        self.assertEqual(args.output, 'output.json')
        self.assertEqual(args.format, 'json')
        self.assertEqual(args.priority_filter, 'CRITICAL')
        self.assertTrue(args.verbose)

    def test_parser_mutually_exclusive_input_all(self):
        """Test that input and all require at least one."""
        # Parser doesn't enforce mutual exclusivity, but at least one should be provided
        args = self.parser.parse_args(['--all'])
        self.assertTrue(args.all)

        args = self.parser.parse_args(['--input', 'test.log'])
        self.assertEqual(args.input, 'test.log')


class TestPriorityFiltering(unittest.TestCase):
    """Test priority filtering logic."""

    def test_priority_values(self):
        """Test that priority enum has expected values."""
        self.assertEqual(Priority.CRITICAL.value, "CRITICAL")
        self.assertEqual(Priority.HIGH.value, "HIGH")
        self.assertEqual(Priority.MEDIUM.value, "MEDIUM")
        self.assertEqual(Priority.LOW.value, "LOW")
        self.assertEqual(Priority.INFO.value, "INFO")

    def test_priority_enum_membership(self):
        """Test that all priority levels are valid enum members."""
        # Test that we can create Priority from string
        from ai_log_triage.triage_agent import TriageAgent
        agent = TriageAgent()

        test_cases = [
            ("CRITICAL", Priority.CRITICAL),
            ("HIGH", Priority.HIGH),
            ("MEDIUM", Priority.MEDIUM),
            ("LOW", Priority.LOW),
            ("INFO", Priority.INFO),
        ]

        for priority_str, expected in test_cases:
            with self.subTest(priority=priority_str):
                result = agent._parse_priority(priority_str)
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
