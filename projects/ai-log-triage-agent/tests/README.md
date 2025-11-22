# Unit Tests

This directory contains comprehensive unit tests for the AI Log Triage Agent.

## Running Tests

### Run All Tests

```bash
# From project root
python -m unittest discover -s tests -v

# Or using pytest (if installed)
pytest tests/ -v
```

### Run Specific Test File

```bash
python -m unittest tests.test_log_parser -v
python -m unittest tests.test_triage_agent -v
python -m unittest tests.test_cli -v
```

### Run Specific Test Class

```bash
python -m unittest tests.test_log_parser.TestLogParser -v
```

### Run Specific Test Method

```bash
python -m unittest tests.test_log_parser.TestLogParser.test_extract_timestamp_iso_format -v
```

## Test Coverage

### test_log_parser.py
Tests for log parsing functionality:
- **TestLogEvent**: Tests for LogEvent dataclass
  - to_dict conversion
  - Content truncation (by lines and characters)
- **TestLogParser**: Tests for LogParser class
  - Timestamp extraction (ISO, bracketed formats)
  - Log level extraction
  - Category detection (auth, web, database, security, deployment)
  - Continuation line detection (stack traces)
  - Event-based chunking (multi-line events)
  - Line-by-line chunking

### test_triage_agent.py
Tests for triage agent functionality:
- **TestTriageAgent**: Tests for TriageAgent class
  - Prompt building (with/without truncation)
  - LLM response parsing (valid JSON, missing fields, priority variations)
  - Triage result formatting (text and JSON)
  - Summary report generation

### test_cli.py
Tests for CLI interface:
- **TestCLI**: Tests for argument parsing
  - Input/output arguments
  - Flags (--all, --dry-run, --verbose)
  - Format options (text, json, summary)
  - Chunk methods (event, line)
  - Priority filtering
  - Model selection
  - Short flags (-i, -o, -f, etc.)
- **TestPriorityFiltering**: Tests for priority enum
  - Priority values
  - Priority parsing from strings

## Test Structure

All tests follow the standard Python unittest framework:
- Each test file contains one or more `TestCase` classes
- Test methods start with `test_` prefix
- setUp methods initialize test fixtures
- Assertions verify expected behavior

## Adding New Tests

When adding new functionality:
1. Create corresponding test methods in the appropriate test file
2. Use descriptive test method names (e.g., `test_parse_timestamp_with_milliseconds`)
3. Include docstrings explaining what the test verifies
4. Use `self.subTest()` for parameterized tests
5. Run tests to verify they pass before committing

## Example Test Pattern

```python
def test_new_feature(self):
    """Test description of what this verifies."""
    # Arrange
    input_data = "test input"

    # Act
    result = function_under_test(input_data)

    # Assert
    self.assertEqual(result, expected_value)
```
