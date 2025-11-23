# Test Suite Documentation

Comprehensive test suite for the AI Log Triage Agent with 100+ tests covering unit, integration, and edge cases.

---

## Quick Start

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m unittest discover tests -v

# Run with pytest (recommended)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/ai_log_triage --cov-report=html
```

---

## Test Structure

### Core Unit Tests (55 tests)

#### `test_log_parser.py` - Log Parsing & Chunking
**Coverage:**
- Event-based and line-by-line chunking
- Timestamp extraction (ISO, bracketed formats)
- Log level detection
- Category detection (auth, web, database, security, deployment)
- Content truncation
- Continuation line detection (stack traces)

**Example:**
```python
def test_extract_timestamp_iso_format(self):
    """Test timestamp extraction with ISO format."""
    parser = LogParser()
    timestamp = parser.extract_timestamp("2025-02-17T14:23:11Z ERROR: Test")
    self.assertEqual(timestamp, "2025-02-17T14:23:11")
```

#### `test_triage_agent.py` - Triage Logic & Formatting
**Coverage:**
- Prompt building (with/without truncation)
- LLM response parsing (valid JSON, missing fields, priority variations)
- Result serialization (JSON, text)
- Summary report generation

**Mocking:** No LLM calls (uses mock responses)

#### `test_cli.py` - CLI Argument Parsing
**Coverage:**
- All command-line flags and options
- Short and long flag formats
- Default values
- Priority filtering logic

**Example:**
```python
def test_parser_input_argument(self):
    """Test --input argument parsing."""
    args = self.parser.parse_args(['--input', 'test.log'])
    self.assertEqual(args.input, 'test.log')
```

#### `test_api.py` - FastAPI Endpoints & Validation
**Coverage:**
- Health check endpoint
- Single and batch triage endpoints
- Request validation (size limits, required fields)
- Response format
- OpenAPI schema generation

**Mocking:** TriageAgent mocked to avoid LLM calls

---

### Integration Tests (25+ tests)

#### `test_integration.py` - Full Stack Integration
**Purpose:** Test complete workflows from input to output

**Test Classes:**
1. **TestCLIToAPIIntegration** - CLI and API working together
2. **TestEndToEndWorkflow** - Complete processing workflows
3. **TestParserToTriageFlow** - Data flow between components
4. **TestErrorHandling** - Error propagation and handling
5. **TestConfigurationIntegration** - Config usage across components

**Example Scenario:**
```python
@patch('ai_log_triage.llm_client.call_llm')
def test_full_cli_workflow_with_output(self, mock_llm):
    """Test complete CLI workflow: parse → triage → save results."""
    mock_llm.return_value = MOCK_LLM_RESPONSE

    # Create test log
    test_log.write_text("ERROR: Test error\n")

    # Run CLI
    exit_code = cli_main(['--input', str(test_log), '--output', str(output_file)])

    # Verify output created
    self.assertTrue(output_file.exists())
```

---

### Edge Case Tests (40+ tests)

#### `test_edge_cases.py` - Edge Case & Error Handling
**Purpose:** Test unusual and edge case inputs

**Test Classes:**
1. **TestEmptyAndWhitespaceHandling** - Empty logs, whitespace
2. **TestMalformedLogEntries** - Missing timestamp/level, malformed data
3. **TestSpecialCharactersAndEncoding** - Unicode, special chars
4. **TestVeryLongContent** - Long lines, many events
5. **TestMixedLogFormats** - Different timestamp/level formats
6. **TestStackTraceParsing** - Java, Python stack traces
7. **TestConfigurationEdgeCases** - Invalid config values
8. **TestLLMResponseEdgeCases** - Malformed LLM responses
9. **TestBoundaryConditions** - Limits and boundaries

**Example:**
```python
def test_unicode_characters(self):
    """Test parsing log with Unicode characters."""
    events = list(self.parser.chunk_by_event(
        "ERROR: User 'José García' failed 中文",
        source_file="test.log"
    ))

    self.assertIn("José García", events[0].raw_content)
    self.assertIn("中文", events[0].raw_content)
```

---

## Running Tests

### Run All Tests
```bash
python -m unittest discover tests -v
pytest tests/ -v
```

### Run Specific Test Modules
```bash
# Core unit tests
python -m unittest tests.test_log_parser
python -m unittest tests.test_triage_agent
python -m unittest tests.test_cli
python -m unittest tests.test_api

# Integration tests
python -m unittest tests.test_integration

# Validation tests
python -m unittest tests.test_edge_cases
```

### Run Specific Test Classes
```bash
python -m unittest tests.test_edge_cases.TestMalformedLogEntries
python -m unittest tests.test_integration.TestCLIToAPIIntegration
```

### Run with Coverage
```bash
# HTML report
pytest tests/ --cov=src/ai_log_triage --cov-report=html

# Terminal report
pytest tests/ --cov=src/ai_log_triage --cov-report=term-missing

# XML report (for CI)
pytest tests/ --cov=src/ai_log_triage --cov-report=xml
```

---

## Test Dependencies

Install with:
```bash
pip install -r requirements-dev.txt
```

**Required packages:**
- `pytest>=8.0.0` - Modern testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-mock>=3.12.0` - Enhanced mocking
- `httpx>=0.26.0` - FastAPI TestClient support

---

## Test Coverage Summary

| Module | Unit Tests | Integration | Edge Cases | Total Coverage |
|--------|-----------|-------------|------------|----------------|
| `log_parser.py` | ✅ 12 tests | ✅ 3 tests | ✅ 15 tests | ~95% |
| `triage_agent.py` | ✅ 8 tests | ✅ 4 tests | ✅ 8 tests | ~90% |
| `cli.py` | ✅ 26 tests | ✅ 5 tests | ✅ 5 tests | ~85% |
| `api.py` | ✅ 12 tests | ✅ 3 tests | ✅ 2 tests | ~90% |
| `config.py` | ⚠️ 2 tests | ✅ 3 tests | ✅ 5 tests | ~75% |
| `llm_client.py` | ⚠️ 1 test | ✅ 2 tests | ✅ 3 tests | ~65% |

**Total: 100+ tests**

**Legend:**
- ✅ Comprehensive coverage
- ⚠️ Basic coverage (could be improved)

---

## Mocking Strategy

### What We Mock

1. **LLM API Calls** - Always mocked to avoid:
   - Real API costs
   - Network dependencies
   - Slow test execution
   - Non-deterministic results

2. **File System** - Mocked using `tempfile` in integration tests

3. **Configuration** - Patched for specific test scenarios

### What We Don't Mock

1. **Core Logic** - Parser and agent logic tested directly
2. **Data Structures** - LogEvent, TriageResult used as-is
3. **Validation** - Pydantic validation tested without mocking

### Mock Examples

```python
# Mock LLM calls
@patch('ai_log_triage.llm_client.call_llm')
def test_triage(self, mock_llm):
    mock_llm.return_value = '{"summary": "Test"}'
    result = agent.triage_event(event)

# Mock configuration
@patch('ai_log_triage.config.settings.LLM_TIMEOUT', 60)
def test_timeout(self):
    self.assertEqual(settings.LLM_TIMEOUT, 60)

# Mock TriageAgent in API tests
@patch('ai_log_triage.api.TriageAgent')
def test_api(self, mock_agent_class):
    mock_agent = Mock()
    mock_agent_class.return_value = mock_agent
```

---

## Writing New Tests

### Guidelines

1. **Descriptive names:** `test_<what>_<scenario>_<expected>`
2. **AAA pattern:** Arrange, Act, Assert
3. **One concept per test** (when possible)
4. **Mock external dependencies** (especially LLM)
5. **Use subTest for similar tests**
6. **Clean up resources** with `setUp`/`tearDown`

### Test Template

```python
def test_feature_does_something_correctly(self):
    """Test that feature behaves correctly under normal conditions."""
    # Arrange
    input_data = "test input"
    expected = "expected output"

    # Act
    result = function_under_test(input_data)

    # Assert
    self.assertEqual(result, expected)
```

---

## Performance

**Current Performance (v0.1.0):**
- Unit tests: ~0.5 seconds (55 tests)
- Integration tests: ~2 seconds (25 tests)
- Edge case tests: ~1 second (40 tests)
- **Total: ~3.5 seconds (100+ tests)**

**Performance Targets:**
- Unit tests: < 5 seconds
- Integration tests: < 30 seconds
- All tests: < 60 seconds

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'ai_log_triage'"

**Solution:** Install package in development mode:
```bash
pip install -e .
```

### "ImportError: cannot import name 'TestClient'"

**Solution:** Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

### Tests fail with "LLM client not properly configured"

**Solution:** Mock the settings validation:
```python
@patch('ai_log_triage.config.settings.validate')
def test_something(self, mock_validate):
    mock_validate.return_value = (True, [])
    # ... test code
```

### "FileNotFoundError" in integration tests

**Solution:** Tests use `tempfile` - ensure cleanup in `tearDown`:
```python
def tearDown(self):
    shutil.rmtree(self.test_dir, ignore_errors=True)
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e .
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/ --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## Test Maintenance

### When to Update Tests

1. **New features** → Write tests first (TDD)
2. **Bug fixes** → Add regression test
3. **Refactoring** → Ensure existing tests pass
4. **API changes** → Update integration tests

### Test Organization

- Group related tests in test classes
- Use descriptive test names
- Keep tests focused on single functionality
- Document complex test scenarios

---

## Related Documentation

- [Main README](../README.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [API Examples](../API_EXAMPLES.md)
- [Configuration Guide](../CONFIGURATION_GUIDE.md)

---

**Last Updated:** 2025-11-23
**Test Count:** 100+ tests
**Coverage:** ~85% overall

---

## Why No Golden Output Tests?

This is an LLM-based application where responses are non-deterministic by nature. Instead of testing for exact output matches (which would be brittle and provide false confidence), we focus on:

- ✅ **Structure validation** - Responses have required fields
- ✅ **Type correctness** - Fields are correct types (Priority enum, list of strings, etc.)
- ✅ **Contract testing** - LLM responses can be parsed into our data model
- ✅ **Integration flows** - Data flows correctly through the pipeline
- ✅ **Edge case handling** - Malformed responses are handled gracefully

This approach is more appropriate for LLM applications where the value is in the AI's analysis, not in deterministic output matching.
