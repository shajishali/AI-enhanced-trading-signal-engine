# PowerShell script to run Playwright tests
Write-Host "🚀 Starting Playwright Tests for AI Trading Engine..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Run the tests
python run_playwright_tests.py

Write-Host ""
Write-Host "✅ Tests completed!" -ForegroundColor Green
Read-Host "Press Enter to continue"



