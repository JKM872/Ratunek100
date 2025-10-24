@echo off
REM =========================================================
REM TEST: Forma gości NA WYJEŹDZIE w emailach
REM =========================================================

echo.
echo ============================================================
echo  TEST: Czy forma gosci NA WYJEZDZIE wyswietla sie w emailu?
echo ============================================================
echo.

SET DATE=2025-10-24

echo Data: %DATE%
echo Sport: Volleyball (siatkówka)
echo Meczów: Max 3 (dla szybkości)
echo Email: jakub.majka.zg@gmail.com
echo.
echo SPRAWDŹ W EMAILU:
echo   ✈️ [Nazwa gości]:
echo     • Ogółem: [forma ogólna]
echo     • Na wyjeździe: [forma na wyjeździe] ← TO POWINNO SIĘ POJAWIĆ!
echo.

python scrape_and_notify.py --date %DATE% --sports volleyball --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx" --only-form-advantage --max-matches 3 --headless

echo.
echo ============================================================
echo  Gotowe! Sprawdź email.
echo ============================================================
echo.
pause



