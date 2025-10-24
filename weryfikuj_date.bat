@echo off
REM ====================================================================
REM 🎯 WERYFIKACJA WYNIKÓW - Wybierz datę
REM ====================================================================

echo.
echo ====================================================================
echo  🎯 WERYFIKACJA PRZEWIDYWAŃ
echo ====================================================================
echo.

REM Pytaj użytkownika o datę
set /p DATE="Podaj datę do weryfikacji (YYYY-MM-DD, np. 2025-10-23): "

echo.
echo 📅 Weryfikuję wyniki z: %DATE%
echo 📧 Raport zostanie wysłany na: jakub.majka.zg@gmail.com
echo.
echo Trwa weryfikacja...
echo.

python verify_predictions.py --date %DATE% --headless --send-email --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx"

echo.
echo ====================================================================
echo  ✅ GOTOWE!
echo ====================================================================
echo.
echo 📧 Raport wysłany na email
echo 📂 Raport HTML: outputs\verification_report_%DATE%.html
echo.
echo Otwórz plik HTML w przeglądarce aby zobaczyć szczegóły!
echo.
pause



