# 🚀 GitHub Actions - Instrukcja Krok Po Kroku

## ✅ Dlaczego GitHub Actions?

**Z GitHub Student Pack masz:**
- ✅ **3000 minut/miesiąc** GitHub Actions (wystarczy na ~90 dni scrapingu!)
- ✅ **7 GB RAM** (14x więcej niż Heroku Basic!)
- ✅ **Całkowicie darmowe**
- ✅ Chrome już zainstalowany
- ✅ Działa 24/7 bez laptopa
- ✅ Prywatne repozytoria

**vs Heroku Basic ($13/m):**
- ❌ Tylko 512 MB RAM (za mało dla Selenium!)
- ❌ Zawiesza się przy 30 meczach
- ❌ Trzeba płacić $13/m

---

## 📋 KROK PO KROKU

### **KROK 1: Utwórz repo na GitHub** (2 minuty)

1. Wejdź na: https://github.com/JKM2828
2. Kliknij: **New repository** (zielony przycisk)
3. Wypełnij:
   - **Repository name**: `volleyball-scraper`
   - **Description**: `Automatyczny scraper meczów siatkówki z Livesport`
   - ✅ **Private** (WAŻNE! Kod będzie prywatny)
   - ✅ **Add a README file** (opcjonalne)
4. Kliknij: **Create repository**

---

### **KROK 2: Upload kodu** (5 minut)

#### **Opcja A: Przez przeglądarkę (ŁATWIEJSZE)**

1. Na stronie swojego repo kliknij: **Add file** → **Upload files**
2. Przeciągnij WSZYSTKIE pliki z `C:\Users\jakub\Downloads\Ratowanie\`
   - ✅ `livesport_h2h_scraper.py`
   - ✅ `scrape_and_notify.py`
   - ✅ `email_notifier.py`
   - ✅ `requirements.txt`
   - ✅ `.gitignore`
   - ✅ Folder `.github/` (WAŻNE!)
   - ✅ Wszystkie inne pliki Python
3. Commit message: `Initial commit - volleyball scraper`
4. Kliknij: **Commit changes**

#### **Opcja B: Przez git (ZAAWANSOWANE)**

```bash
# W PowerShell w folderze C:\Users\jakub\Downloads\Ratowanie
git init
git add .
git commit -m "Initial commit - volleyball scraper"
git branch -M main
git remote add origin https://github.com/JKM2828/volleyball-scraper.git
git push -u origin main
```

---

### **KROK 3: Dodaj hasło email jako Secret** (1 minuta) 🔒

**WAŻNE!** Nigdy nie wklejaj hasła email w kodzie!

1. Na GitHub w swoim repo kliknij: **Settings**
2. W menu po lewej: **Secrets and variables** → **Actions**
3. Kliknij: **New repository secret**
4. Wypełnij:
   - **Name**: `EMAIL_PASSWORD`
   - **Secret**: `vurb tcai zaaq itjx`
5. Kliknij: **Add secret**

✅ Gotowe! Hasło jest bezpiecznie ukryte.

---

### **KROK 4: Uruchom pierwszy test** (1 minuta) 🎯

1. Kliknij zakładkę: **Actions** (na górze)
2. Zobaczysz 2 workflows:
   - **Daily Volleyball Scraping** - automatyczny (codziennie o 11:00)
   - **All Sports Scraping** - ręczny (kiedy chcesz)

3. Kliknij: **All Sports Scraping (Manual)**
4. Kliknij: **Run workflow** (po prawej)
5. Zostaw domyślne ustawienia:
   - Sports: `volleyball basketball handball`
   - Date: (puste = dzisiaj)
6. Kliknij: **Run workflow** (zielony przycisk)

7. **Odśwież stronę** i zobaczysz działające zadanie!
8. Kliknij na nazwę zadania, żeby zobaczyć logi na żywo

---

### **KROK 5: Sprawdź wyniki** (1 minuta) 📊

Po zakończeniu zadania:

1. **Email**: Sprawdź `jakub.majka.zg@gmail.com` - dostaniesz email z wynikami!
2. **Artifacts**: 
   - W zakończonym zadaniu kliknij: **scraping-results-XXX**
   - Pobierz plik CSV z wynikami
3. **Logi**: 
   - Zobacz szczegółowe logi w zakładce Actions

---

## ⏰ AUTOMATYCZNE URUCHAMIANIE (codziennie o 11:00)

**To już działa!** 🎉

Workflow `daily-scraping.yml` automatycznie uruchomi się:
- **Codziennie o 11:00** polskiego czasu (09:00 UTC)
- Scrapuje tylko **volleyball**
- Wysyła email na **jakub.majka.zg@gmail.com**

### **Jak zmienić godzinę?**

Edytuj plik `.github/workflows/daily-scraping.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # 09:00 UTC = 11:00 PL
```

**Przykłady:**
- `'0 7 * * *'` = 09:00 PL (07:00 UTC)
- `'0 10 * * *'` = 12:00 PL (10:00 UTC)
- `'0 20 * * *'` = 22:00 PL (20:00 UTC)

### **Jak dodać więcej sportów?**

Zmień linię w `daily-scraping.yml`:

```yaml
--sports volleyball \
```

na:

```yaml
--sports volleyball basketball handball \
```

---

## 🎯 JAK URUCHOMIĆ RĘCZNIE?

**Kiedy:**
- Chcesz przetestować
- Potrzebujesz wyników teraz
- Chcesz scraping dla konkretnej daty

**Jak:**
1. Zakładka: **Actions**
2. Wybierz: **All Sports Scraping (Manual)**
3. Kliknij: **Run workflow**
4. Możesz zmienić:
   - **sports**: `volleyball basketball handball football`
   - **date**: `2025-10-24` (lub zostaw puste dla dzisiaj)
5. Kliknij: **Run workflow**

---

## 📊 MONITORING

### **Gdzie zobaczyć historię?**

1. Zakładka: **Actions**
2. Zobacz wszystkie uruchomienia:
   - ✅ Zielony = sukces
   - ❌ Czerwony = błąd
   - 🟡 Żółty = w trakcie

### **Jak zobaczyć logi?**

1. Kliknij na nazwę zadania
2. Zobacz szczegółowe logi każdego kroku
3. Sprawdź co zostało zescrapowane

### **Jak pobrać CSV?**

1. W zakończonym zadaniu scroll w dół
2. Sekcja **Artifacts**
3. Pobierz: `scraping-results-XXX.zip`
4. Rozpakuj i zobacz CSV

---

## ⚠️ TROUBLESHOOTING

### **Problem: Email nie przychodzi**

**Sprawdź:**
1. Czy secret `EMAIL_PASSWORD` jest poprawny?
   - Settings → Secrets → Actions → EMAIL_PASSWORD
2. Czy email nie wpadł do SPAM?
3. Czy są jakieś mecze spełniające kryteria?
   - Sprawdź logi w Actions

**Fix:**
```yaml
# Edytuj daily-scraping.yml, dodaj --skip-no-odds
--headless \
--skip-no-odds \  # Pomija mecze bez kursów
--sort-by time
```

### **Problem: Workflow nie uruchamia się automatycznie**

**Przyczyny:**
1. Repo nie ma aktywności przez 60 dni (GitHub pauzuje workflows)
2. Workflow nie został włączony

**Fix:**
1. Zakładka: **Actions**
2. Znajdź: **Daily Volleyball Scraping**
3. Kliknij: **Enable workflow**

### **Problem: Timeout (przekroczony czas)**

**Przyczyna:** Za dużo meczów (>50)

**Fix:**
```yaml
# Edytuj workflow, zwiększ timeout
timeout-minutes: 60  # było 30
```

### **Problem: Brak RAM**

**Nie powinno się zdarzyć** (GitHub ma 7 GB RAM!)

Ale jeśli tak:
```yaml
# Dodaj w scrape_and_notify.py limiter
--max-matches 30  # Max 30 meczów
```

---

## 💰 LIMITY GITHUB STUDENT PACK

**Masz:**
- ✅ **3000 minut/miesiąc** (normalnie 2000)
- ✅ **Nielimitowane prywatne repo**

**Zużycie:**
- Jeden scraping volleyball: ~3-5 minut
- Codziennie: ~5 min × 30 dni = **150 minut/m**
- **Zostaje:** 2850 minut na testy/eksperymenty!

**Jeśli przekroczysz limit:**
- Workflows się zatrzymają
- Nic się nie stanie (brak opłat)
- Zresetuje się 1. dnia miesiąca

---

## 🔧 DODATKOWE KONFIGURACJE

### **Scraping wielu sportów codziennie**

Stwórz nowy workflow: `.github/workflows/daily-all-sports.yml`

```yaml
name: Daily All Sports

on:
  schedule:
    - cron: '0 9 * * *'  # 11:00 PL
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y chromium-browser chromium-chromedriver
        pip install -r requirements.txt
    
    - name: Run scraping
      run: |
        python scrape_and_notify.py \
          --date $(date +%Y-%m-%d) \
          --sports volleyball basketball handball \
          --to jakub.majka.zg@gmail.com \
          --from-email jakub.majka.zg@gmail.com \
          --password "${{ secrets.EMAIL_PASSWORD }}" \
          --headless
```

### **Różne godziny dla różnych sportów**

**volleyball.yml** - codziennie o 11:00
**football.yml** - codziennie o 14:00
**basketball.yml** - codziennie o 17:00

Każdy sport w osobnym workflow!

---

## 📈 STATYSTYKI

**Jak sprawdzić zużycie minut?**

1. GitHub → Your profile → Settings
2. **Billing and plans**
3. **Plans and usage**
4. Zobacz: "Actions minutes used this month"

---

## ✅ CHECKLIST

Po wykonaniu wszystkich kroków powinieneś mieć:

- [x] Repo na GitHub (prywatne)
- [x] Kod wrzucony
- [x] Secret EMAIL_PASSWORD dodany
- [x] Test ręczny zakończony sukcesem
- [x] Email otrzymany
- [x] Automatyczny workflow włączony

**Gotowe! Teraz scraper działa 24/7 bez Twojego laptopa!** 🎉

---

## 🆘 POTRZEBUJESZ POMOCY?

**Problemy z:**
- GitHub repo? → Zobacz sekcję KROK 1
- Upload kodu? → Użyj opcji A (przez przeglądarkę)
- Email nie działa? → Sprawdź Troubleshooting
- Workflow nie działa? → Zobacz logi w Actions

**GitHub Issues:**
Możesz stworzyć Issue w swoim repo i opisać problem.

---

**Powodzenia! 🚀**

Your scraper is now running in the cloud, completely free, with GitHub Student Pack! 🎓

