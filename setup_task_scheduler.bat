@echo off
echo ========================================
echo KONFIGURACJA TASK SCHEDULER
echo ========================================
echo.
echo Ten skrypt pomoze Ci skonfigurowac automatyczne uruchamianie!
echo.
echo Co zostanie zrobione:
echo   1. Otworzenie Task Scheduler
echo   2. Instrukcje krok po kroku
echo.
echo WAZNE: Laptop MUSI byc podlaczony do zasilania!
echo.
pause

echo.
echo ========================================
echo KROK 1: Otwieranie Task Scheduler...
echo ========================================
echo.
start taskschd.msc
timeout /t 2

echo.
echo ========================================
echo KROK 2: CO ZROBIC W TASK SCHEDULER
echo ========================================
echo.
echo 1. Kliknij: "Create Task" (NIE "Create Basic Task"!)
echo.
echo 2. Zakladka GENERAL:
echo    - Name: Volleyball Scraper
echo    - [✓] Run whether user is logged on or not
echo    - [✓] Run with highest privileges
echo.
echo 3. Zakladka TRIGGERS:
echo    - New
echo    - Begin: On a schedule
echo    - Daily, 11:00 AM
echo.
echo 4. Zakladka ACTIONS:
echo    - New
echo    - Program: python.exe
echo    - Arguments: scrape_and_notify.py --date 2025-10-24 --sports volleyball --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx" --headless
echo    - Start in: %CD%
echo.
echo 5. Zakladka CONDITIONS:
echo    - [✓] Wake the computer to run this task  ← WAZNE!!!
echo.
echo 6. Zakladka SETTINGS:
echo    - [✓] Allow task to be run on demand
echo    - [✓] Run task as soon as possible after scheduled start
echo.
echo 7. Kliknij OK
echo.
echo ========================================
echo GOTOWE!
echo ========================================
echo.
echo Laptop bedzie sie budzil codziennie o 11:00
echo i uruchamial scraping automatycznie!
echo.
echo Wiecej informacji: URUCHAMIANIE_AUTOMATYCZNE.md
echo.
pause



