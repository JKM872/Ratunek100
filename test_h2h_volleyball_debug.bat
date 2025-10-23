@echo off
echo ========================================
echo TEST H2H FIX v2.1 - VOLLEYBALL (FAST!)
echo ========================================
echo.
echo Ten skrypt uruchomi scraping ZOPTYMALIZOWANY
echo WERSJA 2.1: Szybciej, czytelniej!
echo.
echo UWAGA: Uruchomi tylko 5 meczow jako test!
echo.

REM Uruchom z datą - użyj prawdziwej daty z meczami
python scrape_and_notify.py --date 2025-10-24 --sports volleyball --to test@example.com --from-email test@example.com --password "dummy" --max-matches 5 --headless

echo.
echo ========================================
echo TEST ZAKONCZONY
echo ========================================
echo.
echo Sprawdz logi powyzej:
echo.
echo ✅ SUKCES jesli widzisz:
echo    "KWALIFIKUJE! Team A vs Team B"
echo    "H2H: X/5 (Y%%)"
echo.
echo ❌ PROBLEM jesli widzisz:
echo    "Brak H2H" dla WSZYSTKICH meczy
echo.
echo Czas trwania: ~1 minuta (bylo ~2.5 min w v2.0)
echo.

pause

