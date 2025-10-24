# 💤 URUCHAMIANIE SCRAPINGU AUTOMATYCZNIE

## ❌ PROBLEM: Laptop w uśpieniu

**Laptop w trybie uśpienia = programy NIE DZIAŁAJĄ!**

Windows wstrzymuje wszystkie procesy, więc scraping się nie wykona.

---

## ✅ ROZWIĄZANIA (5 opcji)

---

### **OPCJA 1: Windows Task Scheduler + "Wake to Run"** ⭐ NAJŁATWIEJSZE

**Zalety:**
- ✅ Darmowe
- ✅ Wbudowane w Windows
- ✅ Laptop sam się budzi przed zadaniem

**Wady:**
- ❌ Laptop musi być podłączony do zasilania
- ❌ Nie działa jeśli laptop jest wyłączony

**Jak skonfigurować:**

#### **Krok 1: Utwórz zadanie w Task Scheduler**
```
1. Uruchom: Task Scheduler (szukaj w Start)
2. Kliknij: Create Task (nie "Create Basic Task"!)
3. Zakładka "General":
   - Name: "Volleyball H2H Scraper"
   - ✅ Run whether user is logged on or not
   - ✅ Run with highest privileges
```

#### **Krok 2: Trigger (kiedy uruchamiać)**
```
Zakładka "Triggers" → New:
   - Begin the task: On a schedule
   - Settings: Daily, 11:00 AM
   - ✅ Enabled
```

#### **Krok 3: Action (co uruchamiać)**
```
Zakładka "Actions" → New:
   - Action: Start a program
   - Program/script: C:\Python311\python.exe
   - Add arguments: scrape_and_notify.py --date 2025-10-24 --sports volleyball --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx" --headless
   - Start in: C:\Users\jakub\Downloads\Ratowanie
```

#### **Krok 4: Warunki (KLUCZOWE!)** 🔑
```
Zakładka "Conditions":
   - Power:
     ✅ Wake the computer to run this task  ← WAŻNE!
     ⬜ Start only if computer is on AC power (opcjonalne)
```

#### **Krok 5: Settings**
```
Zakładka "Settings":
   ✅ Allow task to be run on demand
   ✅ Run task as soon as possible after scheduled start is missed
   ⬜ Stop the task if it runs longer than: (wyłącz to)
```

**Gotowe!** Laptop będzie się budził o 11:00 i uruchamiał scraping.

---

### **OPCJA 2: VPS/Cloud Server** 🌐 NAJLEPSZE

**Zalety:**
- ✅ Działa 24/7 (nawet jak laptop wyłączony)
- ✅ Szybki internet
- ✅ Zawsze dostępny

**Wady:**
- ❌ Kosztuje (~$5-10/miesiąc)
- ❌ Wymaga konfiguracji Linuxa

**Popularne opcje:**
1. **DigitalOcean** ($5/miesiąc) - najprostszy
2. **Google Cloud** (darmowe $300 kredytu na start)
3. **AWS EC2** (darmowy tier przez rok)
4. **Hetzner** ($3/miesiąc) - najtańszy

**Szybka konfiguracja (DigitalOcean):**
```bash
# 1. Utwórz Droplet (Ubuntu 22.04)
# 2. Połącz się SSH

# 3. Zainstaluj Python i Chrome
sudo apt update
sudo apt install python3 python3-pip chromium-browser chromium-chromedriver -y

# 4. Skopiuj pliki projektu
scp -r C:\Users\jakub\Downloads\Ratowanie/* root@YOUR_IP:/root/scraper/

# 5. Zainstaluj zależności
cd /root/scraper
pip3 install -r requirements.txt

# 6. Ustaw cron job (uruchamia codziennie o 11:00)
crontab -e

# Dodaj linię:
0 11 * * * cd /root/scraper && python3 scrape_and_notify.py --date $(date +\%Y-\%m-\%d) --sports volleyball --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx" --headless
```

---

### **OPCJA 3: Raspberry Pi** 🍓 NAJFAJNIEJSZE

**Zalety:**
- ✅ Jednorazowy koszt (~200-300 zł)
- ✅ Niskie zużycie prądu (~3W)
- ✅ Działa 24/7
- ✅ Masz pełną kontrolę

**Wady:**
- ❌ Wymaga zakupu sprzętu
- ❌ Konfiguracja Linuxa

**Co potrzebujesz:**
- Raspberry Pi 4 (4GB RAM) - ~200 zł
- Karta microSD 32GB - ~30 zł
- Zasilacz USB-C - ~40 zł
- Obudowa - ~30 zł

**Total:** ~300 zł (jednorazowo)

**Konfiguracja:** Identyczna jak VPS (opcja 2)

---

### **OPCJA 4: GitHub Actions** 🆓 DARMOWE!

**Zalety:**
- ✅ Całkowicie darmowe
- ✅ Działa w chmurze
- ✅ Nie wymaga serwera

**Wady:**
- ❌ Publiczne repo (kod widoczny dla wszystkich)
- ❌ Limit 2000 minut/miesiąc
- ❌ Trzeba ukryć hasło email

**Konfiguracja:**

#### **Krok 1: Utwórz repo na GitHub**
```
1. Idź na github.com
2. New Repository → "volleyball-scraper"
3. Upload plików projektu
```

#### **Krok 2: Dodaj secrets**
```
Settings → Secrets and variables → Actions → New repository secret

Dodaj:
- EMAIL_TO: jakub.majka.zg@gmail.com
- EMAIL_FROM: jakub.majka.zg@gmail.com  
- EMAIL_PASSWORD: vurb tcai zaaq itjx
```

#### **Krok 3: Utwórz workflow**

**Plik:** `.github/workflows/daily-scraping.yml`
```yaml
name: Daily Volleyball Scraping

on:
  schedule:
    # Uruchamia codziennie o 11:00 UTC (13:00 polskiego czasu)
    - cron: '0 11 * * *'
  
  # Możliwość ręcznego uruchomienia
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        
    - name: Install Chrome
      run: |
        sudo apt-get update
        sudo apt-get install -y chromium-browser chromium-chromedriver
    
    - name: Run scraping
      env:
        EMAIL_TO: ${{ secrets.EMAIL_TO }}
        EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
        EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
      run: |
        python scrape_and_notify.py \
          --date $(date +%Y-%m-%d) \
          --sports volleyball \
          --to $EMAIL_TO \
          --from-email $EMAIL_FROM \
          --password "$EMAIL_PASSWORD" \
          --headless
```

**Gotowe!** GitHub będzie uruchamiał scraping codziennie o 11:00 UTC.

---

### **OPCJA 5: Wyłącz uśpianie laptopa** 💻 NAJPROSTSZE (ale nieekologiczne)

**Zalety:**
- ✅ Bardzo proste
- ✅ Nie wymaga dodatkowej konfiguracji

**Wady:**
- ❌ Laptop musi być cały czas włączony
- ❌ Zużycie prądu (~50W = ~15 zł/miesiąc)
- ❌ Skraca żywotność laptopa

**Jak to zrobić:**
```
1. Ustawienia → System → Power & Sleep
2. Ustaw "Sleep" na "Never"
3. Ustaw Task Scheduler (Opcja 1) BEZ "Wake to run"
```

---

## 📊 PORÓWNANIE OPCJI

| Opcja | Koszt | Trudność | Działa 24/7 | Zalecane |
|-------|-------|----------|-------------|----------|
| **Task Scheduler + Wake** | Darmowe | ⭐ Łatwe | ⚠️ Tylko jeśli laptop podłączony | ✅ TAK (podstawowe) |
| **VPS/Cloud** | $5-10/m | ⭐⭐⭐ Trudne | ✅ Tak | ✅✅ TAK (najlepsze) |
| **Raspberry Pi** | ~300 zł jednorazowo | ⭐⭐⭐ Trudne | ✅ Tak | ✅ TAK (długoterminowe) |
| **GitHub Actions** | Darmowe | ⭐⭐ Średnie | ✅ Tak | ✅ TAK (jeśli publiczne repo OK) |
| **Wyłącz uśpianie** | ~15 zł/m prąd | ⭐ Łatwe | ⚠️ Tylko jeśli laptop włączony | ❌ NIE (nieekologiczne) |

---

## 🎯 MOJA REKOMENDACJA

### **Dla początkujących:**
**Opcja 1** (Task Scheduler + Wake to Run)
- Darmowe, łatwe, wystarczające

### **Dla średnio zaawansowanych:**
**Opcja 4** (GitHub Actions)
- Darmowe, działa w chmurze, niezawodne

### **Dla profesjonalistów:**
**Opcja 2** (VPS) lub **Opcja 3** (Raspberry Pi)
- Pełna kontrola, najszybsze, najbardziej niezawodne

---

## 📝 READY-TO-USE: Task Scheduler

Chcesz użyć Opcji 1? Stworzyłem gotowy skrypt:

**Plik:** `setup_task_scheduler.bat`
```batch
@echo off
echo ========================================
echo UTWÓRZ ZADANIE W TASK SCHEDULER
echo ========================================
echo.
echo Ten skrypt uruchomi Task Scheduler.
echo Postępuj według instrukcji w pliku:
echo   URUCHAMIANIE_AUTOMATYCZNE.md
echo.
echo Otwiera Task Scheduler za 3 sekundy...
timeout /t 3
start taskschd.msc
pause
```

Uruchom i postępuj według Kroku 1-5 powyżej!

---

**Pytania? Powiedz mi którą opcję wybierasz!** 🚀



