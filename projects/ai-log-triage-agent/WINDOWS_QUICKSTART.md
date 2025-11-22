# Windows PowerShell Quick Start

This guide shows how to use the API from Windows PowerShell.

---

## Starting the API

```powershell
python run_api.py
```

---

## Testing with PowerShell

### Option 1: Using Invoke-RestMethod (Recommended)

**Health Check:**
```powershell
Invoke-RestMethod -Uri http://localhost:8000/health -Method Get
```

**Single Log Triage:**
```powershell
$body = @{
    log_text = "2025-02-17 14:23:11 ERROR: Connection failed"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/triage -Method Post -Body $body -ContentType "application/json"
```

**Batch Log Triage:**
```powershell
$body = @{
    logs = @(
        "ERROR: Database timeout",
        "WARN: High memory usage",
        "CRITICAL: Service unavailable"
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/triage/batch -Method Post -Body $body -ContentType "application/json"
```

### Option 2: Using curl.exe (Windows 10+)

Windows 10+ includes `curl.exe` which works like Unix curl:

```powershell
curl.exe -X POST http://localhost:8000/triage `
  -H "Content-Type: application/json" `
  -d '{\"log_text\": \"ERROR: Connection failed\"}'
```

**Note:** Use backticks `` ` `` for line continuation in PowerShell, and escape quotes with `\`

### Option 3: PowerShell Script

Create `test-api.ps1`:

```powershell
# Test AI Log Triage API

$ApiUrl = "http://localhost:8000"

# Test health
Write-Host "Testing health endpoint..." -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$ApiUrl/health" -Method Get
Write-Host "Status: $($health.status)" -ForegroundColor Green
Write-Host "Version: $($health.version)" -ForegroundColor Green
Write-Host ""

# Test single triage
Write-Host "Testing single log triage..." -ForegroundColor Cyan
$singleBody = @{
    log_text = "2025-02-17 14:23:11 ERROR: Database connection timeout"
    source_file = "app.log"
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "$ApiUrl/triage" -Method Post -Body $singleBody -ContentType "application/json"

Write-Host "Priority: $($result.priority)" -ForegroundColor Yellow
Write-Host "Classification: $($result.classification)" -ForegroundColor Yellow
Write-Host "Summary: $($result.summary)" -ForegroundColor White
Write-Host ""

# Test batch triage
Write-Host "Testing batch log triage..." -ForegroundColor Cyan
$batchBody = @{
    logs = @(
        "ERROR: Database timeout",
        "WARN: High memory usage detected",
        "CRITICAL: Service unavailable"
    )
} | ConvertTo-Json

$batchResult = Invoke-RestMethod -Uri "$ApiUrl/triage/batch" -Method Post -Body $batchBody -ContentType "application/json"

Write-Host "Total events: $($batchResult.total_events)" -ForegroundColor Green
Write-Host "Priority breakdown:" -ForegroundColor White
$batchResult.priority_breakdown | Format-Table -AutoSize

Write-Host "`nDone!" -ForegroundColor Green
```

Run it:
```powershell
.\test-api.ps1
```

---

## Common PowerShell Patterns

### Pretty Print JSON Response

```powershell
$result = Invoke-RestMethod -Uri http://localhost:8000/health -Method Get
$result | ConvertTo-Json -Depth 10
```

### Save Response to File

```powershell
$body = @{ log_text = "ERROR: Failed" } | ConvertTo-Json
$result = Invoke-RestMethod -Uri http://localhost:8000/triage -Method Post -Body $body -ContentType "application/json"
$result | ConvertTo-Json -Depth 10 | Out-File result.json
```

### Handle Errors

```powershell
try {
    $body = @{ log_text = "" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri http://localhost:8000/triage -Method Post -Body $body -ContentType "application/json"
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    $_.Exception.Response
}
```

### Loop Through Multiple Logs

```powershell
$logs = @(
    "ERROR: Connection timeout",
    "WARN: Memory usage high",
    "INFO: Request completed"
)

foreach ($log in $logs) {
    $body = @{ log_text = $log } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri http://localhost:8000/triage -Method Post -Body $body -ContentType "application/json"

    Write-Host "`nLog: $log" -ForegroundColor Cyan
    Write-Host "Priority: $($result.priority)" -ForegroundColor Yellow
    Write-Host "Owner: $($result.suggested_owner)" -ForegroundColor Yellow
}
```

---

## Python Client (Also Works on Windows)

```python
import requests

# Single log
response = requests.post(
    "http://localhost:8000/triage",
    json={"log_text": "ERROR: Connection failed"}
)
result = response.json()
print(f"Priority: {result['priority']}")
print(f"Summary: {result['summary']}")

# Batch logs
response = requests.post(
    "http://localhost:8000/triage/batch",
    json={
        "logs": [
            "ERROR: Database timeout",
            "WARN: High memory usage"
        ]
    }
)
batch = response.json()
print(f"Total: {batch['total_events']}")
print(f"Critical: {batch['priority_breakdown']['CRITICAL']}")
```

---

## Quick Reference

### PowerShell vs Unix curl

| Task | PowerShell | Unix/curl.exe |
|------|-----------|---------------|
| GET request | `Invoke-RestMethod -Uri $url -Method Get` | `curl http://url` |
| POST JSON | `Invoke-RestMethod -Uri $url -Method Post -Body $json -ContentType "application/json"` | `curl -X POST http://url -H "Content-Type: application/json" -d '{}'` |
| Save to file | `... \| Out-File file.json` | `curl ... > file.txt` |

### Common Issues

**Issue:** `Cannot convert to JSON`
**Solution:** Use `ConvertTo-Json`:
```powershell
$body = @{ log_text = "test" } | ConvertTo-Json
```

**Issue:** Quotes in JSON
**Solution:** Use PowerShell hashtables and `ConvertTo-Json`:
```powershell
# Good
$body = @{ log_text = "my text" } | ConvertTo-Json

# Bad
$body = '{"log_text": "my text"}'  # Hard to escape
```

**Issue:** Multi-line commands
**Solution:** Use backticks for continuation:
```powershell
Invoke-RestMethod `
    -Uri http://localhost:8000/triage `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

---

## Environment Setup (PowerShell)

```powershell
# Create and activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install
pip install -e .

# Copy env file
Copy-Item .env.example .env

# Edit .env (use notepad or your editor)
notepad .env
```

---

## Next Steps

- Use the Python client for easier integration
- Try the PowerShell script above for testing
- Or use Windows Terminal with curl.exe
- View interactive docs at http://localhost:8000/docs (works great in browser!)

---

**Tip:** For the best experience on Windows, use the browser-based Swagger UI at http://localhost:8000/docs - it's fully interactive and doesn't require any command-line tools!
