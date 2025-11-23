# API Examples and Integration Guide

This guide provides comprehensive examples for using the AI Log Triage Agent REST API.

## Table of Contents

- [Getting Started](#getting-started)
- [Single Log Triage](#single-log-triage)
- [Batch Log Triage](#batch-log-triage)
- [Error Handling](#error-handling)
- [Client Libraries](#client-libraries)
- [Integration Patterns](#integration-patterns)

---

## Getting Started

### Starting the Server

```bash
# Development mode with auto-reload
python run_api.py

# Production mode
python run_api.py --production --workers 4

# Custom configuration
python run_api.py --host 0.0.0.0 --port 5000
```

### Health Check

Verify the API is running:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "llm_configured": true
}
```

---

## Single Log Triage

### Basic Request

```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "log_text": "2025-02-17 14:23:11 ERROR: NullPointerException at UserService.getUser"
  }'
```

### With Optional Parameters

```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "log_text": "2025-02-17 14:23:11 ERROR: Database connection timeout",
    "source_file": "webserver.log",
    "chunk_method": "event",
    "max_tokens": 2048,
    "model": "your-preferred-model"
  }'
```

### Multi-line Log (Stack Trace)

```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "log_text": "2025-02-17 14:23:11 ERROR: NullPointerException\n    at com.example.UserService.getUser(UserService.java:42)\n    at com.example.UserController.handleRequest(UserController.java:87)",
    "source_file": "application.log"
  }'
```

---

## Batch Log Triage

### Basic Batch Request

```bash
curl -X POST http://localhost:8000/triage/batch \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [
      "2025-02-17T13:05:22Z WARN  AuthService - Failed login attempt",
      "[2025-02-17 14:23:11] ERROR RequestID=ab12ef Route=/api/v1/users/42",
      "INFO: Request completed"
    ]
  }'
```

### Batch Response Example

```json
{
  "total_events": 3,
  "results": [
    {
      "source_file": "batch_request_1.log",
      "line_number": 1,
      "timestamp": "2025-02-17T13:05:22",
      "log_level": "WARN",
      "summary": "A failed login attempt was detected by the AuthService, indicating an authentication issue.",
      "classification": "Authentication Failure",
      "priority": "MEDIUM",
      "suggested_owner": "Security Team",
      "root_cause": "Potential causes include incorrect credentials entered by a user, a brute-force attack attempt, or a misconfiguration in the authentication service.",
      "action_items": [
        "Review authentication logs for patterns (e.g., multiple failed attempts from the same IP/user)",
        "Verify if the authentication service configuration is correct",
        "Check for system vulnerabilities or compromised accounts",
        "Monitor for additional failed attempts to determine if this is an isolated incident or part of an attack"
      ],
      "original_log": "2025-02-17T13:05:22Z WARN  AuthService - Failed login attempt"
    },
    {
      "source_file": "batch_request_2.log",
      "line_number": 2,
      "timestamp": "2025-02-17 14:23:11",
      "log_level": "ERROR",
      "summary": "An error occurred during processing of an API request for user ID 42, indicating a failed operation.",
      "classification": "API Error",
      "priority": "HIGH",
      "suggested_owner": "Backend Team",
      "root_cause": "Likely caused by invalid user ID reference, missing user data, or backend processing failure for the specified resource.",
      "action_items": [
        "1. Check full error stack trace in application logs correlated with RequestID=ab12ef",
        "2. Verify existence and accessibility of user record 42 in database",
        "3. Inspect API endpoint /api/v1/users/{id} handler implementation",
        "4. Review recent deployments/changes to user service components"
      ],
      "original_log": "[2025-02-17 14:23:11] ERROR RequestID=ab12ef Route=/api/v1/users/42"
    },
    {
      "source_file": "batch_request_3.log",
      "line_number": 3,
      "timestamp": null,
      "log_level": "INFO",
      "summary": "Informational log indicating successful completion of a request without errors.",
      "classification": "General",
      "priority": "INFO",
      "suggested_owner": "DevOps",
      "root_cause": "Normal operation of a service or batch job completing as expected.",
      "action_items": [
        "Confirm successful request completion in related logs or systems.",
        "Verify this entry aligns with expected application behavior.",
        "Ensure log verbosity settings appropriately capture informational events."
      ],
      "original_log": "INFO: Request completed"
    }
  ],
  "priority_breakdown": {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 1,
    "LOW": 0,
    "INFO": 1
  }
}
```

---

## Error Handling

### Validation Errors (422)

```bash
# Empty log text
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"log_text": ""}'
```

Response:
```json
{
  "detail": "log_text cannot be empty",
  "error_type": "ValidationError"
}
```

### Server Errors (500)

When LLM API fails:
```json
{
  "detail": "LLM processing error: API key not configured",
  "error_type": "RuntimeError"
}
```

---

## Client Libraries

### Python with `requests`

```python
import requests

API_URL = "http://localhost:8000"

def triage_log(log_text: str, source_file: str = None):
    """Triage a single log entry."""
    response = requests.post(
        f"{API_URL}/triage",
        json={
            "log_text": log_text,
            "source_file": source_file
        }
    )
    response.raise_for_status()
    return response.json()

def triage_batch(logs: list, source_file: str = None):
    """Triage multiple log entries."""
    response = requests.post(
        f"{API_URL}/triage/batch",
        json={
            "logs": logs,
            "source_file": source_file
        }
    )
    response.raise_for_status()
    return response.json()

# Usage
if __name__ == "__main__":
    # Single log
    result = triage_log("2025-02-17 ERROR: Database timeout")
    print(f"Priority: {result['priority']}")
    print(f"Summary: {result['summary']}")

    # Batch logs
    results = triage_batch([
        "2025-02-17 ERROR: Database timeout",
        "2025-02-17 WARN: High CPU usage"
    ])
    print(f"Total events: {results['total_events']}")
    print(f"Critical: {results['priority_breakdown']['CRITICAL']}")
```

### Python with `httpx` (async)

```python
import httpx
import asyncio

API_URL = "http://localhost:8000"

async def triage_log_async(log_text: str):
    """Async triage of a log entry."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/triage",
            json={"log_text": log_text}
        )
        response.raise_for_status()
        return response.json()

# Usage
async def main():
    result = await triage_log_async("ERROR: Connection failed")
    print(result['summary'])

asyncio.run(main())
```

### JavaScript/Node.js

```javascript
const API_URL = "http://localhost:8000";

async function triageLog(logText, sourceFile = null) {
  const response = await fetch(`${API_URL}/triage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      log_text: logText,
      source_file: sourceFile
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return await response.json();
}

async function triageBatch(logs, sourceFile = null) {
  const response = await fetch(`${API_URL}/triage/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ logs, source_file: sourceFile })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return await response.json();
}

// Usage
(async () => {
  const result = await triageLog("2025-02-17 ERROR: Database timeout");
  console.log(`Priority: ${result.priority}`);
  console.log(`Summary: ${result.summary}`);
})();
```

### cURL Scripts

Save as `triage.sh`:

```bash
#!/bin/bash
# Triage a single log file

API_URL="${API_URL:-http://localhost:8000}"
LOG_FILE="$1"

if [ -z "$LOG_FILE" ]; then
  echo "Usage: $0 <log_file>"
  exit 1
fi

LOG_CONTENT=$(cat "$LOG_FILE")

curl -X POST "$API_URL/triage" \
  -H "Content-Type: application/json" \
  -d "{\"log_text\": $(echo "$LOG_CONTENT" | jq -Rs .), \"source_file\": \"$LOG_FILE\"}" \
  | jq .
```

---

## Integration Patterns

### Log Monitoring Integration

```python
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

API_URL = "http://localhost:8000"

class LogFileHandler(FileSystemEventHandler):
    """Monitor log files and triage new entries."""

    def __init__(self, log_file):
        self.log_file = log_file
        self.last_position = 0

    def on_modified(self, event):
        if event.src_path == self.log_file:
            self.process_new_lines()

    def process_new_lines(self):
        """Read new lines and triage them."""
        with open(self.log_file, 'r') as f:
            f.seek(self.last_position)
            new_lines = f.readlines()
            self.last_position = f.tell()

        if new_lines:
            # Batch triage new lines
            response = requests.post(
                f"{API_URL}/triage/batch",
                json={"logs": [line.strip() for line in new_lines]}
            )

            results = response.json()
            # Alert on critical issues
            for result in results['results']:
                if result['priority'] in ['CRITICAL', 'HIGH']:
                    self.send_alert(result)

    def send_alert(self, result):
        """Send alert for critical issues."""
        print(f"ALERT: {result['classification']}")
        print(f"Priority: {result['priority']}")
        print(f"Action: {result['action_items']}")

# Usage
handler = LogFileHandler("/var/log/application.log")
observer = Observer()
observer.schedule(handler, path="/var/log", recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

### Webhook Integration

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
TRIAGE_API = "http://localhost:8000"

@app.route('/webhook/logs', methods=['POST'])
def receive_logs():
    """Receive logs from external system and triage."""
    data = request.json
    logs = data.get('logs', [])

    # Triage the logs
    response = requests.post(
        f"{TRIAGE_API}/triage/batch",
        json={"logs": logs}
    )

    triage_results = response.json()

    # Filter high-priority issues
    critical_issues = [
        r for r in triage_results['results']
        if r['priority'] in ['CRITICAL', 'HIGH']
    ]

    return jsonify({
        "total_processed": triage_results['total_events'],
        "critical_issues": len(critical_issues),
        "issues": critical_issues
    })

if __name__ == '__main__':
    app.run(port=9000)
```

### Slack Bot Integration

```python
from slack_bolt import App
import requests

app = App(token="xoxb-your-token")
TRIAGE_API = "http://localhost:8000"

@app.message("triage")
def triage_log_message(message, say):
    """Triage a log when user types 'triage' followed by log text."""
    log_text = message['text'].replace('triage', '').strip()

    response = requests.post(
        f"{TRIAGE_API}/triage",
        json={"log_text": log_text}
    )

    result = response.json()

    say(
        f"*Log Triage Result*\n"
        f"Priority: `{result['priority']}`\n"
        f"Classification: {result['classification']}\n"
        f"Summary: {result['summary']}\n"
        f"Suggested Owner: {result['suggested_owner']}\n"
        f"\n*Action Items:*\n" +
        "\n".join(f"• {item}" for item in result['action_items'])
    )

if __name__ == "__main__":
    app.start(port=3000)
```

---

## Best Practices

1. **Rate Limiting**: Implement rate limiting when making many requests
2. **Batching**: Use batch endpoint for multiple logs to reduce API calls
3. **Error Handling**: Always handle 422 and 500 errors gracefully
4. **Timeouts**: Set appropriate request timeouts (LLM processing can take time)
5. **Caching**: Cache results for identical log entries
6. **Monitoring**: Monitor API health endpoint for uptime tracking

---

## OpenAPI/Swagger

The API provides interactive documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

You can use the OpenAPI spec to generate client libraries in any language using tools like:
- [openapi-generator](https://openapi-generator.tech/)
- [swagger-codegen](https://swagger.io/tools/swagger-codegen/)
