@echo off
echo Starting Playwright Tests for AI Trading Engine...
echo.

REM Activate virtual environment
call "venv\Scripts\activate.bat"

REM Run the tests
python run_playwright_tests.py

echo.
echo Tests completed!
pause
















