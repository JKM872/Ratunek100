@echo off
REM ====================================================================
REM 🎯 WERYFIKACJA WYNIKÓW - BEZ EMAILA (tylko HTML)
REM ====================================================================

echo.
echo ====================================================================
echo  🎯 WERYFIKACJA PRZEWIDYWAŃ (bez emaila)
echo ====================================================================
echo.

REM Pytaj użytkownika o datę
set /p DATE="Podaj datę do weryfikacji (YYYY-MM-DD, np. 2025-10-23): "

echo.
echo 📅 Weryfikuję wyniki z: %DATE%
echo 💾 Raport zostanie zapisany tylko jako HTML (bez emaila)
echo.
echo Trwa weryfikacja...
echo.

python verify_predictions.py --date %DATE% --headless

echo.
echo ====================================================================
echo  ✅ GOTOWE!
echo ====================================================================
echo.
echo 📂 Raport HTML: outputs\verification_report_%DATE%.html
echo.
echo Otwórz plik HTML w przeglądarce!
echo.

REM Automatycznie otwórz raport w przeglądarce
start outputs\verification_report_%DATE%.html

pause



