## Structured Testing Guide

Machine-readable, automation-friendly test output for dashboards, CI/CD, and analysis.

---

## Overview

The AI Log Triage Agent now supports **structured test output** in multiple formats:
- **JSON** - For dashboards, APIs, and data processing
- **Markdown** - For reports and documentation
- **YAML** - For configuration-driven tools

All formats maintain human readability while being machine-parseable.

---

## Quick Start

### Run Tests with Structured Output

```bash
# JSON output (default)
python run_tests.py --format json --output test-results.json

# Markdown report
python run_tests.py --format markdown --output test-report.md

# YAML output
python run_tests.py --format yaml --output test-results.yaml

# With pytest
pytest tests/ --json-report=pytest-results.json
```

---

## Output Schema

### JSON Format

```json
{
  "summary": {
    "total_tests": 100,
    "passed": 95,
    "failed": 3,
    "errors": 1,
    "skipped": 1,
    "duration_seconds": 3.5,
    "timestamp": "2025-11-23T19:30:00.000Z",
    "success_rate": 95.0
  },
  "tests": [
    {
      "test_id": "tests.test_api.TestAPIEndpoints.test_health_endpoint",
      "module": "tests",
      "class": "test_api",
      "method": "TestAPIEndpoints",
      "status": "passed",
      "duration_seconds": 0.023,
      "timestamp": "2025-11-23T19:30:00.100Z",
      "message": null
    }
  ]
}
```

### Field Descriptions

**Summary Fields:**
- `total_tests` - Total number of tests run
- `passed` - Number of passing tests
- `failed` - Number of failed tests
- `errors` - Number of tests with errors
- `skipped` - Number of skipped tests
- `duration_seconds` - Total execution time
- `timestamp` - ISO 8601 timestamp
- `success_rate` - Percentage of passing tests

**Test Fields:**
- `test_id` - Unique test identifier
- `module` - Test module name
- `class` - Test class name
- `method` - Test method name
- `status` - Test outcome (passed/failed/error/skipped)
- `duration_seconds` - Individual test execution time
- `timestamp` - Test completion timestamp
- `message` - Error/failure message (if any)

---

## Usage Examples

### 1. Dashboard Integration

```python
import json

# Load test results
with open('test-results.json') as f:
    results = json.load(f)

# Extract metrics for dashboard
metrics = {
    'total': results['summary']['total_tests'],
    'passed': results['summary']['passed'],
    'success_rate': results['summary']['success_rate'],
    'duration': results['summary']['duration_seconds']
}

# Send to dashboard API
import requests
requests.post('https://dashboard.example.com/api/metrics', json=metrics)
```

### 2. GitHub Actions Integration

```yaml
- name: Run tests
  run: python run_tests.py --format json --output test-results.json

- name: Upload results
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: test-results.json

- name: Parse and comment
  run: |
    import json
    with open('test-results.json') as f:
        data = json.load(f)
    summary = data['summary']
    print(f"✓ {summary['passed']}/{summary['total_tests']} tests passed")
```

### 3. Jira Automation

```python
import json
from jira import JIRA

# Load results
with open('test-results.json') as f:
    results = json.load(f)

# Create Jira issues for failures
jira = JIRA('https://your-org.atlassian.net', basic_auth=('user', 'token'))

for test in results['tests']:
    if test['status'] == 'failed':
        jira.create_issue(
            project='PROJ',
            summary=f"Test Failure: {test['method']}",
            description=f"Test {test['test_id']} failed\n\n{test['message']}",
            issuetype={'name': 'Bug'}
        )
```

### 4. Benchmarking & Performance Tracking

```python
import json
from datetime import datetime

# Load current results
with open('test-results.json') as f:
    current = json.load(f)

# Load historical results
with open('historical-results.json') as f:
    historical = json.load(f)

# Compare performance
current_duration = current['summary']['duration_seconds']
historical_duration = historical[-1]['summary']['duration_seconds']

perf_change = ((current_duration - historical_duration) / historical_duration) * 100

print(f"Performance change: {perf_change:+.2f}%")

# Add to historical data
historical.append({
    'timestamp': datetime.now().isoformat(),
    'summary': current['summary']
})

with open('historical-results.json', 'w') as f:
    json.dump(historical, f, indent=2)
```

### 5. Slack Notifications

```python
import json
import requests

with open('test-results.json') as f:
    results = json.load(f)

summary = results['summary']

# Format message
message = {
    "text": f"Test Results: {summary['passed']}/{summary['total_tests']} passed",
    "attachments": [{
        "color": "good" if summary['failed'] == 0 else "danger",
        "fields": [
            {"title": "Success Rate", "value": f"{summary['success_rate']}%", "short": True},
            {"title": "Duration", "value": f"{summary['duration_seconds']}s", "short": True},
            {"title": "Failed", "value": str(summary['failed']), "short": True},
            {"title": "Errors", "value": str(summary['errors']), "short": True}
        ]
    }]
}

# Send to Slack
requests.post('https://hooks.slack.com/services/YOUR/WEBHOOK/URL', json=message)
```

---

## CI/CD Integration

### GitHub Actions

See [.github/workflows/tests.yml](.github/workflows/tests.yml) for complete workflow.

**Key features:**
- Runs on multiple OS (Ubuntu, Windows, macOS)
- Tests multiple Python versions (3.10, 3.11, 3.12)
- Uploads structured results as artifacts
- Generates combined markdown report
- Comments PR with test results

### GitLab CI

```yaml
test:
  stage: test
  script:
    - pip install -e .
    - pip install -r requirements-dev.txt
    - python run_tests.py --format json --output test-results.json
  artifacts:
    reports:
      junit: test-results.json
    paths:
      - test-results.json
    expire_in: 30 days
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'pip install -e .'
                sh 'pip install -r requirements-dev.txt'
                sh 'python run_tests.py --format json --output test-results.json'
            }
        }
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'test-results.json'
                publishHTML([
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
            }
        }
    }
}
```

---

## Advanced Usage

### Custom Test Runner

```python
from tests.test_reporter import StructuredTestRunner
import unittest

# Create custom runner
runner = StructuredTestRunner(
    output_format='json',
    output_file='custom-results.json',
    verbosity=2
)

# Load tests
loader = unittest.TestLoader()
suite = loader.discover('tests', pattern='test_*.py')

# Run with custom settings
result = runner.run(suite)
```

### Filtering Results

```python
import json

with open('test-results.json') as f:
    results = json.load(f)

# Get only failed tests
failed = [t for t in results['tests'] if t['status'] == 'failed']

# Get slow tests (> 1 second)
slow = [t for t in results['tests'] if t['duration_seconds'] > 1.0]

# Get tests by module
api_tests = [t for t in results['tests'] if 'test_api' in t['module']]

print(f"Failed: {len(failed)}")
print(f"Slow: {len(slow)}")
print(f"API Tests: {len(api_tests)}")
```

### Trend Analysis

```python
import json
from pathlib import Path
import pandas as pd

# Load multiple test runs
results_dir = Path('test-history')
all_results = []

for file in sorted(results_dir.glob('test-results-*.json')):
    with open(file) as f:
        data = json.load(f)
        all_results.append({
            'date': data['summary']['timestamp'],
            'total': data['summary']['total_tests'],
            'passed': data['summary']['passed'],
            'duration': data['summary']['duration_seconds']
        })

# Create DataFrame
df = pd.DataFrame(all_results)
df['date'] = pd.to_datetime(df['date'])

# Analyze trends
print("Average success rate:", df['passed'].mean() / df['total'].mean() * 100)
print("Performance trend:", df['duration'].pct_change().mean() * 100, "%")
```

---

## Pytest Integration

### Basic Usage

```bash
# Run with JSON output
pytest tests/ --json-report=pytest-results.json

# With coverage
pytest tests/ --json-report=results.json --cov=src/ai_log_triage
```

### Custom Markers

```python
# Mark tests for different purposes
@pytest.mark.unit
def test_parser():
    pass

@pytest.mark.integration
def test_full_workflow():
    pass

@pytest.mark.slow
def test_large_dataset():
    pass
```

```bash
# Run only unit tests
pytest -m unit --json-report=unit-results.json

# Skip slow tests
pytest -m "not slow" --json-report=fast-results.json
```

---

## Schema Validation

Validate test output against schema:

```python
import json
import jsonschema

# Define schema
schema = {
    "type": "object",
    "required": ["summary", "tests"],
    "properties": {
        "summary": {
            "type": "object",
            "required": ["total_tests", "passed", "failed", "success_rate"],
            "properties": {
                "total_tests": {"type": "integer", "minimum": 0},
                "passed": {"type": "integer", "minimum": 0},
                "failed": {"type": "integer", "minimum": 0},
                "success_rate": {"type": "number", "minimum": 0, "maximum": 100}
            }
        },
        "tests": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["test_id", "status", "duration_seconds"]
            }
        }
    }
}

# Validate
with open('test-results.json') as f:
    data = json.load(f)

jsonschema.validate(data, schema)
print("✓ Test results valid!")
```

---

## Best Practices

### 1. **Store Historical Data**
```bash
# Timestamp your results
python run_tests.py --format json --output "test-results-$(date +%Y%m%d-%H%M%S).json"
```

### 2. **Separate by Environment**
```bash
python run_tests.py --output "test-results-${CI_ENVIRONMENT_NAME}.json"
```

### 3. **Track Performance**
```python
# Compare with baseline
baseline_duration = 3.5  # seconds
current_duration = results['summary']['duration_seconds']

if current_duration > baseline_duration * 1.1:  # 10% slower
    print("⚠️  Tests are running slower than baseline!")
```

### 4. **Fail on Quality Gates**
```python
with open('test-results.json') as f:
    results = json.load(f)

success_rate = results['summary']['success_rate']

if success_rate < 95.0:
    print(f"❌ Success rate {success_rate}% below threshold 95%")
    exit(1)
```

---

## Troubleshooting

### Output file not created

**Problem:** No output file generated

**Solution:**
- Check file permissions
- Verify output directory exists
- Use absolute paths: `--output /full/path/to/results.json`

### Invalid JSON

**Problem:** JSON file is malformed

**Solution:**
- Check for disk space
- Ensure tests complete (don't interrupt)
- Use `--verbosity 0` to reduce noise

### Results missing tests

**Problem:** Not all tests appear in output

**Solution:**
- Tests may have been skipped
- Check test discovery: `pytest --collect-only`
- Verify test pattern: `--pattern "test_*.py"`

---

## Future Enhancements

Planned features:
- [ ] Real-time streaming results
- [ ] WebSocket support for live dashboards
- [ ] Test result diff/comparison tool
- [ ] Automatic regression detection
- [ ] Integration with popular dashboards (Grafana, DataDog)
- [ ] ML-based flaky test detection

---

## Related Documentation

- [Test Suite Documentation](tests/README.md)
- [Testing Summary](TESTING_SUMMARY.md)
- [CI/CD Workflows](.github/workflows/)

---

**Last Updated:** 2025-11-23
