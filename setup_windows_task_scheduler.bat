@echo off
REM ============================================================================
REM Setup Windows Task Scheduler for Daily Bookmaker Scraping
REM ============================================================================
REM This will schedule the scraper to run daily at 21:00 (9 PM)
REM ============================================================================

echo ============================================================================
echo WINDOWS TASK SCHEDULER SETUP
echo ============================================================================
echo This will create a scheduled task to run the bookmaker scraper
echo daily at 21:00 (9 PM Polish time)
echo.
echo IMPORTANT: Run this as Administrator!
echo ============================================================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: Not running as Administrator!
    echo.
    echo Right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo Running as Administrator... OK
echo.

REM Get current directory
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%local_bookmaker_scraper.py"

echo Current directory: %SCRIPT_DIR%
echo Python script: %PYTHON_SCRIPT%
echo.

REM Check if script exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: Script not found!
    echo Expected: %PYTHON_SCRIPT%
    pause
    exit /b 1
)

echo Script found... OK
echo.

REM Find Python executable
for /f "tokens=*" %%i in ('where python') do set PYTHON_EXE=%%i

if "%PYTHON_EXE%"=="" (
    echo ERROR: Python not found in PATH!
    echo Please install Python or add it to PATH
    pause
    exit /b 1
)

echo Python found: %PYTHON_EXE%
echo.

REM Prompt for Supabase credentials
echo ============================================================================
echo SUPABASE CREDENTIALS
echo ============================================================================
echo.

set /p SUPABASE_URL="Enter SUPABASE_URL (or press Enter for default): "
if "%SUPABASE_URL%"=="" (
    set SUPABASE_URL=https://bfslhqnxsgmdyptrqshj.supabase.co
)

echo SUPABASE_URL: %SUPABASE_URL%
echo.

set /p SUPABASE_KEY="Enter SUPABASE_KEY (service_role key): "
if "%SUPABASE_KEY%"=="" (
    echo ERROR: SUPABASE_KEY is required!
    pause
    exit /b 1
)

echo SUPABASE_KEY: [HIDDEN]
echo.

REM Create a wrapper batch file with environment variables
set "WRAPPER_SCRIPT=%SCRIPT_DIR%run_bookmaker_scraper_scheduled.bat"

echo Creating wrapper script: %WRAPPER_SCRIPT%
echo.

(
echo @echo off
echo REM Auto-generated wrapper for scheduled task
echo REM Generated on: %DATE% %TIME%
echo.
echo REM Set environment variables
echo set SUPABASE_URL=%SUPABASE_URL%
echo set SUPABASE_KEY=%SUPABASE_KEY%
echo.
echo REM Change to script directory
echo cd /d "%SCRIPT_DIR%"
echo.
echo REM Run Python script
echo "%PYTHON_EXE%" "%PYTHON_SCRIPT%"
echo.
echo REM Log completion
echo echo [%DATE% %TIME%] Scraper completed >> "%SCRIPT_DIR%scraper_log.txt"
) > "%WRAPPER_SCRIPT%"

echo Wrapper script created... OK
echo.

REM Delete existing task (if exists)
echo Removing old task (if exists)...
schtasks /Delete /TN "PolishBookmakerScraper" /F >nul 2>&1
echo.

REM Create scheduled task
echo Creating scheduled task...
echo Task Name: PolishBookmakerScraper
echo Schedule: Daily at 21:00 (9 PM)
echo Script: %WRAPPER_SCRIPT%
echo.

schtasks /Create ^
    /TN "PolishBookmakerScraper" ^
    /TR "\"%WRAPPER_SCRIPT%\"" ^
    /SC DAILY ^
    /ST 21:00 ^
    /RL HIGHEST ^
    /F

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create scheduled task!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo SUCCESS! Task created successfully
echo ============================================================================
echo.
echo Task Name: PolishBookmakerScraper
echo Schedule: Every day at 21:00 (9 PM)
echo Script: %WRAPPER_SCRIPT%
echo.
echo ============================================================================
echo VERIFICATION
echo ============================================================================
echo.

REM Show task details
schtasks /Query /TN "PolishBookmakerScraper" /FO LIST /V

echo.
echo ============================================================================
echo MANUAL TESTING
echo ============================================================================
echo.
echo To test if it works, you can:
echo.
echo 1. Run the wrapper script manually:
echo    %WRAPPER_SCRIPT%
echo.
echo 2. Run the task from Task Scheduler:
echo    schtasks /Run /TN "PolishBookmakerScraper"
echo.
echo 3. Open Task Scheduler GUI:
echo    taskschd.msc
echo.
echo ============================================================================
echo LOGS
echo ============================================================================
echo.
echo Scraper execution log: %SCRIPT_DIR%scraper_log.txt
echo Python output will be logged there
echo.
echo ============================================================================
echo NEXT STEPS
echo ============================================================================
echo.
echo 1. Test the task manually first:
echo    schtasks /Run /TN "PolishBookmakerScraper"
echo.
echo 2. Check Supabase for uploaded data:
echo    https://supabase.com/dashboard/project/bfslhqnxsgmdyptrqshj/editor
echo.
echo 3. Verify logs:
echo    type "%SCRIPT_DIR%scraper_log.txt"
echo.
echo 4. If all works, the scraper will run automatically every day at 21:00
echo.
echo ============================================================================
echo.
pause
