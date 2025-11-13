@echo off@echo off

REM ============================================================================REM ============================================================================

REM Setup Windows Task Scheduler for Daily Polish Bookmaker ScrapingREM Setup Windows Task Scheduler for Daily Bookmaker Scraping

REM Runs daily at 21:00 (9:00 PM Polish time)REM ============================================================================

REM ============================================================================REM This will schedule the scraper to run daily at 21:00 (9 PM)

REM ============================================================================

REM Check for admin rights

net session >nul 2>&1echo ============================================================================

if errorlevel 1 (echo WINDOWS TASK SCHEDULER SETUP

    echo.echo ============================================================================

    echo ╔════════════════════════════════════════════════════════╗echo This will create a scheduled task to run the bookmaker scraper

    echo ║  ⚠️  ADMINISTRATOR PRIVILEGES REQUIRED                ║echo daily at 21:00 (9 PM Polish time)

    echo ╠════════════════════════════════════════════════════════╣echo.

    echo ║                                                        ║echo IMPORTANT: Run this as Administrator!

    echo ║  Right-click this script and select:                  ║echo ============================================================================

    echo ║  "Run as administrator"                               ║echo.

    echo ║                                                        ║

    echo ╚════════════════════════════════════════════════════════╝REM Check if running as Administrator

    echo.net session >nul 2>&1

    pauseif errorlevel 1 (

    exit /b 1    echo ERROR: Not running as Administrator!

)    echo.

    echo Right-click this file and select "Run as Administrator"

echo.    echo.

echo ╔════════════════════════════════════════════════════════╗    pause

echo ║  📅 SETUP WINDOWS TASK SCHEDULER                       ║    exit /b 1

echo ╚════════════════════════════════════════════════════════╝)

echo.

echo Running as Administrator... OK

REM Get current directoryecho.

set "SCRIPT_DIR=%~dp0"

set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"REM Get current directory

set "SCRIPT_DIR=%~dp0"

echo ✅ Script directory: %SCRIPT_DIR%set "PYTHON_SCRIPT=%SCRIPT_DIR%local_bookmaker_scraper.py"



REM Check if run_scraper.bat existsecho Current directory: %SCRIPT_DIR%

if not exist "%SCRIPT_DIR%\run_scraper.bat" (echo Python script: %PYTHON_SCRIPT%

    echo ❌ run_scraper.bat not found!echo.

    echo    Run setup_local_scraper.bat first

    pauseREM Check if script exists

    exit /b 1if not exist "%PYTHON_SCRIPT%" (

)    echo ERROR: Script not found!

    echo Expected: %PYTHON_SCRIPT%

echo ✅ Found run_scraper.bat    pause

    exit /b 1

REM Check if logs directory exists)

if not exist "%SCRIPT_DIR%\logs" (

    mkdir "%SCRIPT_DIR%\logs"echo Script found... OK

    echo ✅ Created logs directoryecho.

)

REM Find Python executable

REM Delete existing task if it existsfor /f "tokens=*" %%i in ('where python') do set PYTHON_EXE=%%i

echo.

echo 🗑️  Removing old task (if exists)...if "%PYTHON_EXE%"=="" (

schtasks /delete /tn "PolishBookmakerScraper" /f >nul 2>&1    echo ERROR: Python not found in PATH!

echo ✅ Old task removed (if any)    echo Please install Python or add it to PATH

    pause

REM Create scheduled task    exit /b 1

echo.)

echo 📅 Creating scheduled task...

echo    Task name: PolishBookmakerScraperecho Python found: %PYTHON_EXE%

echo    Schedule: Daily at 21:00 (9:00 PM)echo.

echo    Script: run_scraper.bat

REM Prompt for Supabase credentials

schtasks /create ^echo ============================================================================

    /tn "PolishBookmakerScraper" ^echo SUPABASE CREDENTIALS

    /tr "\"%SCRIPT_DIR%\run_scraper.bat\"" ^echo ============================================================================

    /sc daily ^echo.

    /st 21:00 ^

    /ru "%USERNAME%" ^set /p SUPABASE_URL="Enter SUPABASE_URL (or press Enter for default): "

    /rl HIGHEST ^if "%SUPABASE_URL%"=="" (

    /f    set SUPABASE_URL=https://bfslhqnxsgmdyptrqshj.supabase.co

)

if errorlevel 1 (

    echo ❌ Failed to create scheduled taskecho SUPABASE_URL: %SUPABASE_URL%

    pauseecho.

    exit /b 1

)set /p SUPABASE_KEY="Enter SUPABASE_KEY (service_role key): "

if "%SUPABASE_KEY%"=="" (

echo ✅ Scheduled task created successfully    echo ERROR: SUPABASE_KEY is required!

    pause

REM Verify task    exit /b 1

echo.)

echo 🔍 Verifying task...

schtasks /query /tn "PolishBookmakerScraper" /fo LIST /vecho SUPABASE_KEY: [HIDDEN]

echo.

if errorlevel 1 (

    echo ❌ Failed to verify taskREM Create a wrapper batch file with environment variables

    pauseset "WRAPPER_SCRIPT=%SCRIPT_DIR%run_bookmaker_scraper_scheduled.bat"

    exit /b 1

)echo Creating wrapper script: %WRAPPER_SCRIPT%

echo.

echo.

echo ╔════════════════════════════════════════════════════════╗(

echo ║  ✅ TASK SCHEDULER SETUP COMPLETE!                     ║echo @echo off

echo ╠════════════════════════════════════════════════════════╣echo REM Auto-generated wrapper for scheduled task

echo ║                                                        ║echo REM Generated on: %DATE% %TIME%

echo ║  Task details:                                         ║echo.

echo ║  • Name: PolishBookmakerScraper                       ║echo REM Set environment variables

echo ║  • Schedule: Daily at 21:00 (9:00 PM)                 ║echo set SUPABASE_URL=%SUPABASE_URL%

echo ║  • Script: run_scraper.bat                            ║echo set SUPABASE_KEY=%SUPABASE_KEY%

echo ║  • Logs: logs\task_scheduler.log                      ║echo.

echo ║                                                        ║echo REM Change to script directory

echo ║  Manual test run:                                      ║echo cd /d "%SCRIPT_DIR%"

echo ║  schtasks /run /tn "PolishBookmakerScraper"           ║echo.

echo ║                                                        ║echo REM Run Python script

echo ║  View task:                                            ║echo "%PYTHON_EXE%" "%PYTHON_SCRIPT%"

echo ║  schtasks /query /tn "PolishBookmakerScraper"         ║echo.

echo ║                                                        ║echo REM Log completion

echo ║  Delete task:                                          ║echo echo [%DATE% %TIME%] Scraper completed >> "%SCRIPT_DIR%scraper_log.txt"

echo ║  schtasks /delete /tn "PolishBookmakerScraper" /f     ║) > "%WRAPPER_SCRIPT%"

echo ║                                                        ║

echo ║  Next scraping: Today at 21:00 (if after setup)       ║echo Wrapper script created... OK

echo ║                 or tomorrow at 21:00                   ║echo.

echo ║                                                        ║

echo ╚════════════════════════════════════════════════════════╝REM Delete existing task (if exists)

echo.echo Removing old task (if exists)...

schtasks /Delete /TN "PolishBookmakerScraper" /F >nul 2>&1

pauseecho.


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
