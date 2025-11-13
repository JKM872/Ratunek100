@echo off
REM ============================================================================
REM Setup Local Polish Bookmaker Scraper
REM ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  🇵🇱 SETUP LOCAL POLISH BOOKMAKER SCRAPER             ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Install Python 3.11+ from python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create venv
echo.
echo 🔧 Creating virtual environment...
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate venv
echo.
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated

REM Upgrade pip
echo.
echo 📦 Upgrading pip...
python -m pip install --upgrade pip --quiet

echo.
echo 📦 Installing dependencies...
echo    This may take a few minutes...

pip install requests beautifulsoup4 cloudscraper supabase python-dotenv lxml --quiet

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Create .env file if not exists
if not exist .env (
    echo.
    echo 🔑 Creating .env file...
    (
        echo # Supabase Configuration
        echo SUPABASE_URL=https://bfslhqnxsgmdyptrqshj.supabase.co
        echo SUPABASE_KEY=
        echo.
        echo # Logging
        echo LOG_LEVEL=INFO
        echo.
        echo # Created: %date% %time%
    ) > .env
    
    echo ✅ .env file created
    echo.
    echo ⚠️  IMPORTANT: Edit .env and add your SUPABASE_KEY!
    echo     Get it from: https://supabase.com/dashboard/project/bfslhqnxsgmdyptrqshj/settings/api
    echo     Use the "service_role" key (secret)
) else (
    echo ✅ .env file already exists
)

REM Create logs directory
if not exist logs (
    mkdir logs
    echo ✅ Created logs directory
)

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  ✅ SETUP COMPLETE!                                    ║
echo ╠════════════════════════════════════════════════════════╣
echo ║                                                        ║
echo ║  Next steps:                                           ║
echo ║  1. Edit .env and add your SUPABASE_KEY               ║
echo ║  2. Test run: python local_bookmaker_scraper.py       ║
echo ║  3. Schedule: setup_windows_task_scheduler.bat        ║
echo ║                                                        ║
echo ║  To activate venv later:                              ║
echo ║  venv\Scripts\activate.bat                            ║
echo ║                                                        ║
echo ╚════════════════════════════════════════════════════════╝
echo.

pause
