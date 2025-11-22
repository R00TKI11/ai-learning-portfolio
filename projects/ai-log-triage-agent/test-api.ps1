# AI Log Triage API - PowerShell Test Script
# This script tests all API endpoints

$ApiUrl = "http://localhost:8000"

Write-Host "`n=== AI Log Triage API Test ===" -ForegroundColor Cyan
Write-Host "API URL: $ApiUrl`n" -ForegroundColor Gray

# Test 1: Health Check
Write-Host "[1/4] Testing health endpoint..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$ApiUrl/health" -Method Get
    Write-Host "  Status: $($health.status)" -ForegroundColor Green
    Write-Host "  Version: $($health.version)" -ForegroundColor Green
    Write-Host "  LLM Configured: $($health.llm_configured)" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Is the API running? Try: python run_api.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Single Log Triage
Write-Host "[2/4] Testing single log triage..." -ForegroundColor Cyan
$singleBody = @{
    log_text = "2025-02-17 14:23:11 ERROR: Database connection timeout"
    source_file = "app.log"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$ApiUrl/triage" -Method Post -Body $singleBody -ContentType "application/json"

    Write-Host "  Priority: $($result.priority)" -ForegroundColor $(
        switch ($result.priority) {
            "CRITICAL" { "Red" }
            "HIGH" { "Yellow" }
            "MEDIUM" { "Cyan" }
            "LOW" { "Gray" }
            "INFO" { "White" }
            default { "White" }
        }
    )
    Write-Host "  Classification: $($result.classification)" -ForegroundColor White
    Write-Host "  Summary: $($result.summary)" -ForegroundColor Gray
    Write-Host "  Suggested Owner: $($result.suggested_owner)" -ForegroundColor Gray
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Batch Log Triage
Write-Host "[3/4] Testing batch log triage..." -ForegroundColor Cyan
$batchBody = @{
    logs = @(
        "ERROR: Database timeout",
        "WARN: High memory usage detected",
        "CRITICAL: Service unavailable"
    )
    source_file = "batch_test.log"
} | ConvertTo-Json

try {
    $batchResult = Invoke-RestMethod -Uri "$ApiUrl/triage/batch" -Method Post -Body $batchBody -ContentType "application/json"

    Write-Host "  Total events: $($batchResult.total_events)" -ForegroundColor Green
    Write-Host "  Priority breakdown:" -ForegroundColor White

    $breakdown = $batchResult.priority_breakdown
    $priorities = @("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")

    foreach ($priority in $priorities) {
        $count = $breakdown.$priority
        if ($count -gt 0) {
            $color = switch ($priority) {
                "CRITICAL" { "Red" }
                "HIGH" { "Yellow" }
                "MEDIUM" { "Cyan" }
                "LOW" { "Gray" }
                "INFO" { "White" }
            }
            Write-Host "    $priority : $count" -ForegroundColor $color
        }
    }
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 4: Error Handling (Empty Log)
Write-Host "[4/4] Testing error handling..." -ForegroundColor Cyan
$errorBody = @{
    log_text = ""
} | ConvertTo-Json

try {
    $errorResult = Invoke-RestMethod -Uri "$ApiUrl/triage" -Method Post -Body $errorBody -ContentType "application/json"
    Write-Host "  UNEXPECTED: Should have failed with validation error" -ForegroundColor Red
} catch {
    Write-Host "  Validation error caught (expected): " -ForegroundColor Green -NoNewline
    Write-Host "$($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Tests Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  - View interactive docs: " -NoNewline
Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  - Check README: " -NoNewline
Write-Host "README.md" -ForegroundColor Cyan
Write-Host "  - Windows guide: " -NoNewline
Write-Host "WINDOWS_QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""
