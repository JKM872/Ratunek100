@echo off
REM ====================================================================
REM 🎯 WERYFIKACJA WCZORAJSZYCH PRZEWIDYWAŃ
REM ====================================================================
REM Automatycznie sprawdza wyniki wczorajszych typów i wysyła raport

echo ====================================================================
echo 🎯 WERYFIKACJA PRZEWIDYWAŃ - Wczorajsze typy
echo ====================================================================
echo.

REM Pobierz wczorajszą datę (wymaga PowerShell)
for /f "tokens=*" %%a in ('powershell -Command "(Get-Date).AddDays(-1).ToString('yyyy-MM-dd')"') do set YESTERDAY=%%a

echo 📅 Sprawdzam wyniki z: %YESTERDAY%
echo.

REM Uruchom weryfikację
python verify_predictions.py --date %YESTERDAY% --headless --send-email --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx"

echo.
echo ====================================================================
echo ✅ WERYFIKACJA ZAKOŃCZONA!
echo ====================================================================
pause

