@echo off
echo ========================================
echo DIAGNOZA H2H - Test pojedynczego meczu
echo ========================================
echo.
echo Ten skrypt otworzy przeglądarkę (NIE headless)
echo i pokaże DOKŁADNIE co się dzieje!
echo.
echo Zobaczysz:
echo   1. Jak strona się ładuje
echo   2. Czy są elementy H2H
echo   3. Zapis HTML do pliku
echo.
echo WAŻNE: Przeglądarka pozostanie otwarta!
echo        Możesz zobaczyć stronę H2H na własne oczy
echo.
pause

python test_h2h_single_debug.py

pause



