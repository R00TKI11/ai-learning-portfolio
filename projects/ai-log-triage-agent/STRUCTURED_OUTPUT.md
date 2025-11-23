# Structured Output Guide

Machine-readable, automation-friendly output for dashboards, CI/CD, and analysis.

---

## Overview

The AI Log Triage Agent supports **structured output** in multiple formats for both CLI and API:
- **JSON** - For dashboards, APIs, and data processing
- **YAML** - For configuration-driven tools
- **Markdown** - For reports and documentation

All formats maintain human readability while being machine-parseable, with rich metadata including:
- Summary statistics (counts, duration, performance metrics)
- Priority, classification, and owner breakdowns
- Actionable item tracking
- Individual triage results with full context

---

## CLI Usage

### Basic Formats

```bash
# Simple JSON (basic triage results)
ai-log-triage --input logs/app.log --format json --output results.json

# Structured JSON (with rich metadata)
ai-log-triage --input logs/app.log --format structured-json --output results.json

# YAML output
ai-log-triage --input logs/app.log --format yaml --output results.yaml

# Markdown report
ai-log-triage --input logs/app.log --format markdown --output report.md
```

### Output to Console

```bash
# Print structured JSON to console
ai-log-triage --input logs/app.log --format structured-json

# Print markdown report to console
ai-log-triage --input logs/app.log --format markdown
```

---

## Output Schema

### Structured JSON/YAML Format

```json
{
  "summary": {
    "total_events_analyzed": 25,
    "total_results": 25,
    "duration_seconds": 12.45,
    "timestamp": "2025-11-23T19:30:00.000Z",
    "events_per_second": 2.01,
    "priority_breakdown": {
      "CRITICAL": 2,
      "HIGH": 5,
      "MEDIUM": 10,
      "LOW": 6,
      "INFO": 2
    },
    "classification_breakdown": {
      "Database Error": 5,
      "Authentication Failure": 3,
      "Performance Issue": 7,
      "Configuration Error": 4,
      "Network Error": 6
    },
    "owner_breakdown": {
      "Database Team": 5,
      "Security Team": 3,
      "Backend Team": 10,
      "DevOps": 7
    },
    "critical_count": 2,
    "high_count": 5,
    "actionable_count": 7
  },
  "results": [
    {
      "source_file": "webserver.log",
      "line_number": 42,
      "timestamp": "2025-02-17 14:23:11",
      "log_level": "ERROR",
      "category": "webserver",
      "summary": "Database connection timeout occurred during user authentication",
      "classification": "Database Error",
      "priority": "HIGH",
      "suggested_owner": "Database Team",
      "root_cause": "Connection pool exhausted due to long-running queries",
      "action_items": [
        "Review connection pool configuration",
        "Identify and optimize slow queries",
        "Implement connection timeout monitoring"
      ],
      "original_log": "2025-02-17 14:23:11 ERROR: Database connection timeout..."
    }
  ]
}
```

### Field Descriptions

**Summary Fields:**
- `total_events_analyzed` - Total number of log events processed
- `total_results` - Number of triage results generated
- `duration_seconds` - Total processing time in seconds
- `timestamp` - ISO 8601 timestamp of when analysis completed
- `events_per_second` - Processing throughput metric
- `priority_breakdown` - Count of events by priority level
- `classification_breakdown` - Count of events by classification type
- `owner_breakdown` - Count of events by suggested team/owner
- `critical_count` - Number of CRITICAL priority events
- `high_count` - Number of HIGH priority events
- `actionable_count` - Combined CRITICAL + HIGH events requiring immediate action

**Result Fields:**
- `source_file` - Original log file name
- `line_number` - Line number in source file
- `timestamp` - Log entry timestamp
- `log_level` - Severity level (ERROR, WARN, INFO, etc.)
- `category` - Log category (webserver, database, auth, etc.)
- `summary` - Brief summary of the issue (1-2 sentences)
- `classification` - Issue classification (Database Error, Auth Failure, etc.)
- `priority` - Priority level (CRITICAL/HIGH/MEDIUM/LOW/INFO)
- `suggested_owner` - Recommended team or person to handle
- `root_cause` - Analysis of what likely caused the issue
- `action_items` - List of specific steps to resolve or investigate
- `original_log` - Full original log content

---

## API Usage

### Single Log Triage

```bash
curl -X POST "http://localhost:8000/triage" \
  -H "Content-Type: application/json" \
  -d '{
    "log_text": "2025-02-17 14:23:11 ERROR: Database connection failed",
    "source_file": "app.log"
  }'
```

### Batch Triage (Simple)

```bash
curl -X POST "http://localhost:8000/triage/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [
      "2025-02-17 14:23:11 ERROR: Database timeout",
      "2025-02-17 14:24:15 WARN: High memory usage"
    ],
    "source_file": "app.log"
  }'
```

**Response:**
```json
{
  "total_events": 2,
  "priority_breakdown": {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 1,
    "LOW": 0,
    "INFO": 0
  },
  "results": [...]
}
```

### Batch Triage (Structured) - Recommended for Automation

```bash
curl -X POST "http://localhost:8000/triage/batch/structured" \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [
      "2025-02-17 14:23:11 ERROR: Database timeout",
      "2025-02-17 14:24:15 WARN: High memory usage"
    ],
    "source_file": "app.log"
  }'
```

**Response includes rich metadata:**
```json
{
  "summary": {
    "total_events_analyzed": 2,
    "total_results": 2,
    "duration_seconds": 1.23,
    "timestamp": "2025-11-23T19:30:00.000Z",
    "events_per_second": 1.63,
    "priority_breakdown": {...},
    "classification_breakdown": {...},
    "owner_breakdown": {...},
    "actionable_count": 1
  },
  "results": [...]
}
```

---

## Integration Examples

### 1. Dashboard Integration

```python
import requests
import json

# Call the structured API endpoint
response = requests.post(
    'http://localhost:8000/triage/batch/structured',
    json={
        'logs': log_entries,
        'source_file': 'production.log'
    }
)

data = response.json()
summary = data['summary']

# Send metrics to dashboard
dashboard_metrics = {
    'total_events': summary['total_events_analyzed'],
    'critical': summary['critical_count'],
    'high': summary['high_count'],
    'actionable': summary['actionable_count'],
    'throughput': summary['events_per_second'],
    'top_classifications': summary['classification_breakdown']
}

requests.post('https://dashboard.example.com/api/metrics', json=dashboard_metrics)
```

### 2. GitHub Issues Automation

```python
import json
from github import Github

# Load triage results
with open('triage-results.json') as f:
    data = json.load(f)

# Create GitHub issues for critical/high priority events
g = Github('your-token')
repo = g.get_repo('your-org/your-repo')

for result in data['results']:
    if result['priority'] in ['CRITICAL', 'HIGH']:
        title = f"[{result['priority']}] {result['classification']} in {result['source_file']}"
        body = f"""
## Summary
{result['summary']}

## Root Cause
{result['root_cause']}

## Action Items
{chr(10).join(f"- {item}" for item in result['action_items'])}

## Details
- **File:** {result['source_file']}:{result['line_number']}
- **Priority:** {result['priority']}
- **Owner:** {result['suggested_owner']}
- **Timestamp:** {result['timestamp']}

## Original Log
```
{result['original_log']}
```
"""
        repo.create_issue(
            title=title,
            body=body,
            labels=['bug', 'log-triage', result['priority'].lower()],
            assignees=[result['suggested_owner'].replace(' Team', '').lower()]
        )
```

### 3. Jira Automation

```python
from jira import JIRA
import json

# Load results
with open('triage-results.json') as f:
    data = json.load(f)

jira = JIRA('https://your-org.atlassian.net', basic_auth=('user', 'token'))

for result in data['results']:
    if result['priority'] in ['CRITICAL', 'HIGH']:
        issue_dict = {
            'project': {'key': 'OPS'},
            'summary': f"{result['classification']}: {result['summary'][:50]}...",
            'description': f"""
h2. Summary
{result['summary']}

h2. Root Cause
{result['root_cause']}

h2. Action Items
{chr(10).join(f"* {item}" for item in result['action_items'])}

h2. Details
* *File:* {result['source_file']}:{result['line_number']}
* *Priority:* {result['priority']}
* *Timestamp:* {result['timestamp']}

h2. Original Log
{{code}}
{result['original_log']}
{{code}}
            """,
            'issuetype': {'name': 'Bug'},
            'priority': {'name': result['priority'].capitalize()}
        }
        jira.create_issue(fields=issue_dict)
```

### 4. Slack Notifications

```python
import requests
import json

with open('triage-results.json') as f:
    data = json.load(f)

summary = data['summary']

# Build Slack message
message = {
    "text": f"Log Triage Report - {summary['actionable_count']} Actionable Issues",
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚨 Log Triage Report - {summary['timestamp']}"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Total Events:*\n{summary['total_events_analyzed']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Duration:*\n{summary['duration_seconds']}s"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Critical:*\n{summary['critical_count']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*High:*\n{summary['high_count']}"
                }
            ]
        }
    ]
}

# Add critical issues
for result in data['results']:
    if result['priority'] == 'CRITICAL':
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🔴 CRITICAL: {result['classification']}*\n{result['summary']}\n_Owner: {result['suggested_owner']}_"
            }
        })

requests.post(
    'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    json=message
)
```

### 5. Performance Tracking

```python
import json
from datetime import datetime
import pandas as pd

# Load current results
with open('triage-results.json') as f:
    current = json.load(f)

# Load historical data
try:
    history = pd.read_json('triage-history.jsonl', lines=True)
except FileNotFoundError:
    history = pd.DataFrame()

# Append current run
new_row = {
    'timestamp': current['summary']['timestamp'],
    'total_events': current['summary']['total_events_analyzed'],
    'duration': current['summary']['duration_seconds'],
    'throughput': current['summary']['events_per_second'],
    'critical_count': current['summary']['critical_count'],
    'high_count': current['summary']['high_count'],
    'actionable_count': current['summary']['actionable_count']
}

history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)

# Calculate trends
print(f"Average throughput: {history['throughput'].mean():.2f} events/sec")
print(f"Peak throughput: {history['throughput'].max():.2f} events/sec")
print(f"Average actionable items: {history['actionable_count'].mean():.1f}")

# Save updated history
history.to_json('triage-history.jsonl', orient='records', lines=True)
```

### 6. CI/CD Pipeline Integration

**GitHub Actions:**
```yaml
- name: Run log triage
  run: |
    ai-log-triage \
      --input logs/ \
      --format structured-json \
      --output triage-results.json

- name: Check for critical issues
  run: |
    python -c "
    import json, sys
    with open('triage-results.json') as f:
        data = json.load(f)
    critical = data['summary']['critical_count']
    if critical > 0:
        print(f'❌ Found {critical} CRITICAL issues!')
        sys.exit(1)
    print('✓ No critical issues found')
    "

- name: Upload results
  uses: actions/upload-artifact@v4
  with:
    name: triage-results
    path: triage-results.json
```

**GitLab CI:**
```yaml
triage:
  stage: test
  script:
    - ai-log-triage --input logs/ --format structured-json --output triage.json
    - |
      python - << EOF
      import json, sys
      with open('triage.json') as f:
          data = json.load(f)
      actionable = data['summary']['actionable_count']
      if actionable > 10:
          print(f"⚠️  Warning: {actionable} actionable issues")
          sys.exit(1)
      EOF
  artifacts:
    reports:
      dotenv: triage.json
    paths:
      - triage.json
    expire_in: 30 days
```

---

## Markdown Report Format

The markdown format generates a beautifully formatted report with:
- Summary statistics table
- Priority breakdown with emoji indicators
- Classification and owner breakdowns
- Detailed results sorted by priority
- Full log context for each issue

**Example output:**
```markdown
# AI Log Triage Report

**Generated:** 2025-11-23T19:30:00.000Z
**Duration:** 12.45s (2.01 events/sec)

---

## Summary

- **Total Events Analyzed:** 25
- **Results Generated:** 25
- **Actionable Items:** 7 (Critical: 2, High: 5)

### Priority Breakdown

| Priority | Count |
|----------|-------|
| CRITICAL | 2 |
| HIGH | 5 |
| MEDIUM | 10 |
| LOW | 6 |
| INFO | 2 |

...

### 1. 🔴 Database Error - CRITICAL

**File:** `webserver.log:42`
**Timestamp:** 2025-02-17 14:23:11
**Owner:** Database Team

**Summary:** Database connection timeout occurred during user authentication

**Root Cause:** Connection pool exhausted due to long-running queries

**Action Items:**
- Review connection pool configuration
- Identify and optimize slow queries
- Implement connection timeout monitoring

**Original Log:**
```
2025-02-17 14:23:11 ERROR: Database connection timeout...
```
```

---

## Best Practices

### 1. Use Structured Formats for Automation

```bash
# ✅ Good - Structured output for scripts
ai-log-triage --all --format structured-json --output results.json

# ❌ Less ideal - Text output harder to parse
ai-log-triage --all --format text > results.txt
```

### 2. Store Historical Data

```bash
# Timestamp your results
ai-log-triage --all \
  --format structured-json \
  --output "triage-$(date +%Y%m%d-%H%M%S).json"
```

### 3. Set Quality Gates

```python
with open('triage-results.json') as f:
    data = json.load(f)

actionable = data['summary']['actionable_count']
if actionable > 5:
    print(f"❌ Quality gate failed: {actionable} actionable issues (threshold: 5)")
    exit(1)
```

### 4. Monitor Performance

```python
summary = data['summary']
throughput = summary['events_per_second']

if throughput < 1.0:
    print(f"⚠️  Performance degraded: {throughput} events/sec")
```

---

## Comparison: Simple vs Structured Output

**Simple JSON** (`--format json`):
- Basic triage results only
- No metadata or summary stats
- Suitable for simple integrations

**Structured JSON** (`--format structured-json`):
- Complete summary metadata
- Priority/classification/owner breakdowns
- Duration and performance metrics
- Actionable item tracking
- Suitable for dashboards, automation, analytics

**Use structured formats when you need:**
- Dashboard integration
- Performance tracking
- Trend analysis
- Automated alerting
- Quality gates in CI/CD

---

## Related Documentation

- [Test Suite Structured Output](STRUCTURED_TESTING.md)
- [API Examples](API_EXAMPLES.md)
- [CLI Documentation](README.md)

---

**Last Updated:** 2025-11-23
