@echo off
REM ============================================================================
REM Wrapper script for Windows Task Scheduler
REM Activates venv and runs the scraper with logging
REM ============================================================================

cd /d "%~dp0"

echo [%date% %time%] Starting Polish Bookmaker Scraper... >> logs\task_scheduler.log

REM Activate venv
call venv\Scripts\activate.bat

REM Run scraper
python local_bookmaker_scraper.py >> logs\task_scheduler.log 2>&1

REM Log exit code
if %errorlevel% == 0 (
    echo [%date% %time%] SUCCESS: Scraper completed with exit code 0 >> logs\task_scheduler.log
) else (
    echo [%date% %time%] ERROR: Scraper failed with exit code %errorlevel% >> logs\task_scheduler.log
)

exit /b %errorlevel%
