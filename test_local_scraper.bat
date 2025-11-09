@echo off
REM ============================================================================
REM Test Local Bookmaker Scraper
REM ============================================================================
REM Run this to test if scraper works on your Polish IP
REM ============================================================================

echo ============================================================================
echo TESTING LOCAL BOOKMAKER SCRAPER
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11+
    pause
    exit /b 1
)

echo [1/5] Checking Python...
python --version
echo.

REM Check if required packages are installed
echo [2/5] Checking dependencies...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo Installing requests...
    pip install requests
)

pip show beautifulsoup4 >nul 2>&1
if errorlevel 1 (
    echo Installing beautifulsoup4...
    pip install beautifulsoup4
)

pip show cloudscraper >nul 2>&1
if errorlevel 1 (
    echo Installing cloudscraper...
    pip install cloudscraper
)

pip show supabase >nul 2>&1
if errorlevel 1 (
    echo Installing supabase...
    pip install supabase
)

echo Dependencies OK!
echo.

REM Check environment variables
echo [3/5] Checking environment variables...

if "%SUPABASE_URL%"=="" (
    echo WARNING: SUPABASE_URL not set!
    echo Setting default...
    set SUPABASE_URL=https://bfslhqnxsgmdyptrqshj.supabase.co
)
echo SUPABASE_URL: %SUPABASE_URL%

if "%SUPABASE_KEY%"=="" (
    echo ERROR: SUPABASE_KEY not set!
    echo.
    echo Please set it:
    echo   set SUPABASE_KEY=your_service_role_key_here
    echo.
    echo Get the key from Supabase dashboard:
    echo   https://supabase.com/dashboard/project/bfslhqnxsgmdyptrqshj/settings/api
    echo.
    pause
    exit /b 1
)
echo SUPABASE_KEY: [HIDDEN - first 10 chars: %SUPABASE_KEY:~0,10%...]
echo.

REM Check IP location (should be Poland)
echo [4/5] Checking your IP location...
echo This should show POLAND for scraper to work!
echo.

python -c "import requests; r = requests.get('https://ipapi.co/json/', timeout=10); print(f\"IP: {r.json()['ip']}\"); print(f\"Country: {r.json()['country_name']}\"); print(f\"City: {r.json()['city']}\")"

echo.
echo NOTE: If not in Poland, bookmakers may block you!
echo.

REM Run the scraper
echo [5/5] Running scraper (TEST MODE)...
echo ============================================================================
echo.

python local_bookmaker_scraper.py

echo.
echo ============================================================================
echo TEST COMPLETE!
echo ============================================================================
echo.
echo Check Supabase dashboard to see if data was uploaded:
echo https://supabase.com/dashboard/project/bfslhqnxsgmdyptrqshj/editor
echo.
echo Table: bookmaker_odds
echo.
pause
