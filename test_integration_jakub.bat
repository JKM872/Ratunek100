@echo off
REM ============================================
REM TEST INTEGRACJI - Jakub
REM ============================================
REM Szybki test połączenia scrapera z aplikacją UI
REM ============================================

echo.
echo ========================================
echo   TEST INTEGRACJI SCRAPERA Z APLIKACJĄ
echo ========================================
echo.

REM Przejdź do katalogu projektu
cd /d C:\Users\jakub\Downloads\Flashscore2

REM Ustaw kodowanie UTF-8
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

REM Pobierz dzisiejszą datę w formacie YYYY-MM-DD
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TODAY=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%

REM ===== KONFIGURACJA =====

REM URL Twojej aplikacji UI (ZMIEŃ TO!)
SET APP_URL=http://localhost:3000

REM Twoje dane email
SET EMAIL_TO=jakub.majka.zg@gmail.com
SET EMAIL_FROM=jakub.majka.zg@gmail.com
SET EMAIL_PASSWORD=vurb tcai zaaq itjx

REM Sport do testu (mało meczów = szybki test)
SET SPORTS=football

REM Limit meczów dla testu (szybsze)
SET MAX_MATCHES=10

REM ========================

echo.
echo 🔧 KONFIGURACJA TESTU:
echo   Data: %TODAY%
echo   Sport: %SPORTS%
echo   Limit: %MAX_MATCHES% meczów (test)
echo   URL aplikacji: %APP_URL%
echo.
echo ⚠️  UPEWNIJ SIĘ ŻE TWOJA APLIKACJA UI DZIAŁA!
echo.
pause

echo.
echo 🚀 Uruchamiam scraper z integracją...
echo ========================================
echo.

REM Uruchom scraper z integracją
python scrape_and_notify.py ^
  --date %TODAY% ^
  --sports %SPORTS% ^
  --to %EMAIL_TO% ^
  --from-email %EMAIL_FROM% ^
  --password "%EMAIL_PASSWORD%" ^
  --headless ^
  --sort time ^
  --max-matches %MAX_MATCHES% ^
  --app-url %APP_URL%

echo.
echo ========================================
echo ✅ TEST ZAKOŃCZONY!
echo ========================================
echo.
echo 📊 SPRAWDŹ:
echo   1. Czy otrzymałeś email?
echo   2. Czy aplikacja UI otrzymała dane?
echo   3. Czy logi wyglądają OK?
echo.
echo 💾 Wyniki zapisane w: outputs\livesport_h2h_%TODAY%_*
echo 📝 Log zapisany w: scraper_log.txt
echo.

REM Zapisz log
echo %date% %time% - Integration test completed >> scraper_log.txt

pause







