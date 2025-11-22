# FastAPI Quick Start Guide

Get the AI Log Triage Agent API running in 5 minutes!

---

## Prerequisites

- Python 3.8+
- OpenRouter API key (or compatible LLM API)

---

## Installation

### 1. Clone and Navigate

```bash
cd projects/ai-log-triage-agent
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Activate
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

### 4. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your API key
# LLM_OPENROUTER_API_KEY=your-key-here
```

---

## Run the API

### Development Mode

```bash
python run_api.py
```

Output:
```
Starting API server in DEVELOPMENT mode on 127.0.0.1:8000
Auto-reload is ENABLED

API Documentation:
  - Swagger UI: http://127.0.0.1:8000/docs
  - ReDoc:      http://127.0.0.1:8000/redoc
  - Health:     http://127.0.0.1:8000/health
```

---

## Test the API

> **Windows Users:** See [WINDOWS_QUICKSTART.md](WINDOWS_QUICKSTART.md) for PowerShell-specific commands

### 1. Health Check

**Unix/macOS/Linux:**
```bash
curl http://localhost:8000/health
```

**Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri http://localhost:8000/health -Method Get
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "llm_configured": true
}
```

### 2. Triage a Log

**Unix/macOS/Linux:**
```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "log_text": "2025-02-17 14:23:11 ERROR: NullPointerException at line 42"
  }'
```

**Windows PowerShell:**
```powershell
$body = @{
    log_text = "2025-02-17 14:23:11 ERROR: NullPointerException at line 42"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/triage -Method Post -Body $body -ContentType "application/json"
```

---

## Interactive Documentation (Recommended!)

**Best way to test on any platform:**

Open in your browser: **http://localhost:8000/docs**

Features:
- ✅ Try endpoints directly in browser (no curl needed!)
- ✅ See all request/response schemas
- ✅ View example payloads
- ✅ Download OpenAPI spec
- ✅ Works the same on Windows, Mac, and Linux

---

## Common Use Cases

### Python Client

```python
import requests

response = requests.post(
    "http://localhost:8000/triage",
    json={"log_text": "ERROR: Database connection failed"}
)

result = response.json()
print(f"Priority: {result['priority']}")
print(f"Summary: {result['summary']}")
```

### cURL Batch Processing

```bash
curl -X POST http://localhost:8000/triage/batch \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [
      "ERROR: Database timeout",
      "WARN: Memory usage high",
      "INFO: Request completed"
    ]
  }'
```

---

## Production Deployment

```bash
# Run with multiple workers
python run_api.py --production --workers 4 --host 0.0.0.0 --port 8000
```

---

## Troubleshooting

### API Key Not Configured

Error: `"llm_configured": false`

**Solution**: Check your `.env` file has:
```
LLM_OPENROUTER_API_KEY=your-actual-key
```

### Port Already in Use

**Solution**: Use a different port:
```bash
python run_api.py --port 5000
```

### Module Import Errors

**Solution**: Reinstall in editable mode:
```bash
pip install -e .
```

---

## Next Steps

- **Read the full guide**: [API_EXAMPLES.md](API_EXAMPLES.md)
- **Review the implementation**: [FASTAPI_SUMMARY.md](FASTAPI_SUMMARY.md)
- **Check API docs**: http://localhost:8000/docs
- **Run tests**: `python -m unittest tests.test_api`

---

## Quick Reference

| What | How |
|------|-----|
| Start API | `python run_api.py` |
| View docs | http://localhost:8000/docs |
| Health check | `curl http://localhost:8000/health` |
| Triage log | `POST /triage` with `{"log_text": "..."}` |
| Batch triage | `POST /triage/batch` with `{"logs": [...]}` |
| Run tests | `python -m unittest tests.test_api` |

---

**You're all set!** 🎉

The API is now running and ready to triage logs via HTTP requests.
