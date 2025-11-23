# Testing Overview

**Version:** 0.1.0
**Last Updated:** 2025-11-23

---

## Overview

The AI Log Triage Agent has a comprehensive test suite with **100+ tests** covering unit, integration, and edge case scenarios. The testing strategy focuses on structure/contract validation rather than exact output matching, which is appropriate for LLM-based applications where responses are non-deterministic.

---

## Test Suite Structure

### Unit Tests (55 tests)
- **`tests/test_log_parser.py`** - Log parsing and event extraction
- **`tests/test_triage_agent.py`** - LLM-based triage logic
- **`tests/test_cli.py`** - Command-line interface
- **`tests/test_api.py`** - REST API endpoints

### Integration Tests (25+ tests)
**File:** `tests/test_integration.py`

- **CLI + API Integration** - Components working together
- **End-to-End Workflows** - Complete processing pipelines
- **Parser → Triage Flow** - Data flow validation
- **Error Handling** - Error propagation across stack
- **Configuration** - Config usage verification

### Edge Case Tests (40+ tests)
**File:** `tests/test_edge_cases.py`

- **Empty & Whitespace** - Empty logs, whitespace handling
- **Malformed Entries** - Missing timestamps/levels
- **Special Characters** - Unicode, special chars
- **Large Content** - Performance with large inputs
- **Mixed Formats** - Different log formats
- **Stack Traces** - Multi-line stack traces
- **Invalid Config** - Invalid configuration values
- **Malformed LLM Responses** - Incomplete/invalid API responses
- **Boundary Conditions** - Limits and edge values

---

## Test Coverage

| Module | Unit | Integration | Edge Cases | Total Coverage |
|--------|------|-------------|------------|----------------|
| `log_parser.py` | 12 | 3 | 15 | ~95% |
| `triage_agent.py` | 8 | 4 | 8 | ~90% |
| `cli.py` | 26 | 5 | 5 | ~85% |
| `api.py` | 12 | 3 | 2 | ~90% |
| `config.py` | 2 | 3 | 5 | ~75% |
| `llm_client.py` | 1 | 2 | 3 | ~65% |

**Overall Coverage:** ~85%

---

## Mocking Strategy

### What Gets Mocked

**LLM API Calls** - Always mocked
- Avoids real API costs
- Eliminates network dependencies
- Ensures fast, deterministic tests
- Uses predefined mock responses

**File System** - Temporary files via `tempfile`
- Creates temporary directories
- Automatic cleanup after tests
- Prevents test pollution

**Configuration** - Patched for specific scenarios
- Tests configuration validation
- Tests edge cases with invalid values

### What Doesn't Get Mocked

- **Core Logic** - Parser and agent logic tested directly
- **Data Structures** - LogEvent, TriageResult used as-is
- **Validation** - Pydantic validation tested without mocking

### Example Mock Patterns

```python
# Mock LLM calls
@patch('ai_log_triage.llm_client.call_llm')
def test_triage(self, mock_llm):
    mock_llm.return_value = MOCK_LLM_RESPONSE
    result = agent.triage_event(event)

# Mock configuration
@patch.object(settings, 'LLM_TIMEOUT', 60)
def test_timeout(self):
    is_valid, errors = settings.validate()
```

---

## Running Tests

### All Tests
```bash
# Using unittest
python -m unittest discover tests -v

# Using pytest (recommended)
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/ai_log_triage --cov-report=html
```

### Specific Test Suites
```bash
# Unit tests only
python -m unittest tests.test_log_parser tests.test_triage_agent tests.test_cli tests.test_api

# Integration tests
python -m unittest tests.test_integration

# Edge case tests
python -m unittest tests.test_edge_cases
```

### Performance
- Core unit tests: ~0.5 seconds
- Integration tests: ~2 seconds
- Edge case tests: ~1 second
- **Total: ~3.5 seconds**

---

## Test Quality

✅ **Descriptive names** - Clear test purpose from name
✅ **AAA pattern** - Arrange, Act, Assert structure
✅ **Proper cleanup** - setUp/tearDown for resource management
✅ **Parameterized tests** - subTest for similar test cases
✅ **Clear documentation** - Docstrings explain test purpose

---

## Why No Golden Output Tests?

Golden output tests (exact content matching) are **not used** for LLM-based functionality because:

- LLM responses are non-deterministic by nature
- Tests would be brittle and break with response variations
- Provides false sense of security
- Better to focus on structure/contract validation

**Instead, we test:**
- ✅ Response structure (has required fields)
- ✅ Field types (Priority enum, list types, etc.)
- ✅ JSON serialization
- ✅ Contract adherence (responses can be parsed)
- ✅ Graceful handling of malformed responses

---

## Development Dependencies

```txt
pytest>=8.0.0          # Modern test framework
pytest-cov>=4.1.0      # Coverage reporting
pytest-mock>=3.12.0    # Enhanced mocking
httpx>=0.26.0          # FastAPI TestClient
```

Install with:
```bash
pip install -r requirements-dev.txt
```

---

## Related Documentation

- [Test Suite README](tests/README.md) - Detailed test documentation
- [Structured Testing](STRUCTURED_TESTING.md) - Test output formats
- [Main README](README.md) - Project overview

---

**Status:** ✅ Production Ready

The test suite ensures code quality, prevents regressions, and supports confident refactoring and feature development.
