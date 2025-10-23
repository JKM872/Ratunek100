@echo off
echo ========================================
echo UPLOAD DO GITHUB - KROK PO KROKU
echo ========================================
echo.
echo UWAGA: Ten skrypt przygotuje kod do uploadu.
echo.
echo ========================================
echo KROK 1: Czy utworzyles juz repo na GitHub?
echo ========================================
echo.
echo 1. Wejdz na: https://github.com/JKM2828
echo 2. Kliknij: New repository
echo 3. Nazwa: volleyball-scraper
echo 4. Zaznacz: Private
echo 5. Zaznacz: Add a README file
echo 6. Kliknij: Create repository
echo.
pause
echo.
echo ========================================
echo KROK 2: Inicjalizacja Git
echo ========================================
echo.
git init
git add .
git commit -m "Initial commit - volleyball scraper with GitHub Actions"
git branch -M main
echo.
echo ✅ Git zainicjalizowany!
echo.
echo ========================================
echo KROK 3: Podlacz do GitHub
echo ========================================
echo.
echo Wklej adres swojego repo (np. https://github.com/JKM2828/volleyball-scraper.git)
echo.
set /p REPO_URL="Adres repo: "
echo.
git remote add origin %REPO_URL%
echo.
echo ========================================
echo KROK 4: Wyslij kod na GitHub
echo ========================================
echo.
echo UWAGA: Zostaniesz poproszony o login i haslo do GitHub
echo Login: JKM2828
echo Haslo: Twoje haslo GitHub (lub Personal Access Token)
echo.
pause
echo.
git push -u origin main
echo.
echo ========================================
echo ✅ KOD WRZUCONY NA GITHUB!
echo ========================================
echo.
echo KROK 5: Dodaj EMAIL_PASSWORD secret
echo.
echo 1. Wejdz na: %REPO_URL%
echo 2. Settings → Secrets and variables → Actions
echo 3. New repository secret
echo 4. Name: EMAIL_PASSWORD
echo 5. Secret: vurb tcai zaaq itjx
echo 6. Add secret
echo.
echo KROK 6: Uruchom test
echo.
echo 1. Zakladka: Actions
echo 2. Wybierz: All Sports Scraping (Manual)
echo 3. Run workflow
echo 4. Poczekaj 3-5 minut
echo 5. Sprawdz email!
echo.
echo ========================================
echo SZCZEGOLOWA INSTRUKCJA:
echo GITHUB_QUICK_START.md
echo ========================================
echo.
pause

