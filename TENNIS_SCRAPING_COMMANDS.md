# 🎾 Komendy do Scrapingu Tenisa

## 📋 **GOTOWE PLIKI BAT:**

### 1. **daily_scraper_tennis.bat** (Automatyczna data - DZISIAJ)
```
Kliknij dwukrotnie → Scrapuje dzisiejsze mecze tenisowe
```

### 2. **run_tennis_only.bat** (Szybkie uruchomienie)
```
Kliknij dwukrotnie → Scrapuje dzisiejsze mecze tenisowe z pausą na końcu
```

### 3. **test_tennis_quick.bat** (Test na 10 meczach)
```
Kliknij dwukrotnie → Szybki test na 10 meczach
```

---

## ⚡ **BEZPOŚREDNIE KOMENDY:**

### A) Dzisiejsze mecze (automatyczna data):

**PowerShell:**
```powershell
$today = Get-Date -Format "yyyy-MM-dd"
python scrape_and_notify.py --date $today --sports tennis --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx" --headless --sort time
```

**CMD:**
```cmd
for /f "tokens=2 delims==" %I in ('wmic os get localdatetime /value') do set datetime=%I
set TODAY=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%
python scrape_and_notify.py --date %TODAY% --sports tennis --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx" --headless --sort time
```

### B) Konkretna data:

```powershell
python scrape_and_notify.py --date 2025-10-09 --sports tennis --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx" --headless --sort time
```

### C) Tylko 10 meczów (szybki test):

```powershell
python scrape_and_notify.py --date 2025-10-08 --sports tennis --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx" --max-matches 10 --headless --sort time
```

### D) Bez emaila (tylko CSV):

```powershell
python livesport_h2h_scraper.py --mode auto --date 2025-10-08 --sports tennis --headless
```

---

## 🔧 **PARAMETRY:**

| Parametr | Opis | Przykład |
|----------|------|----------|
| `--date` | Data meczów (YYYY-MM-DD) | `--date 2025-10-09` |
| `--sports` | Sport do scrapowania | `--sports tennis` |
| `--to` | Email odbiorcy | `--to twoj@email.com` |
| `--from-email` | Email nadawcy | `--from-email twoj@gmail.com` |
| `--password` | Hasło aplikacji Gmail | `--password "xxxx xxxx xxxx xxxx"` |
| `--headless` | Tryb bez okna przeglądarki | `--headless` |
| `--sort` | Sortowanie (time/score) | `--sort time` |
| `--max-matches` | Limit meczów (test) | `--max-matches 10` |

---

## 📅 **USTAWIANIE W HARMONOGRAMIE ZADAŃ:**

### Windows Task Scheduler:

1. **Otwórz**: Task Scheduler (Harmonogram zadań)
2. **Utwórz zadanie podstawowe**: Nazwa: "Tennis Daily Scraping"
3. **Wyzwalacz**: Codziennie o 10:00
4. **Akcja**: Uruchom program
   - **Program**: `C:\Users\jakub\Downloads\Flashscore2\daily_scraper_tennis.bat`
5. **Gotowe!**

---

## 🎯 **RÓŻNE SCENARIUSZE:**

### 1. Codzienny scraping rano (10:00):
```
→ Ustaw daily_scraper_tennis.bat w Task Scheduler
→ Każdego dnia automatyczny email z meczami
```

### 2. Tylko weekendy (Sobota, Niedziela):
```
→ Ustaw run_tennis_only.bat w Task Scheduler
→ Wyzwalacz: Tylko Sobota i Niedziela
```

### 3. Przed ważnymi turniejami (Grand Slam):
```powershell
# Więcej meczów, dłuższy scraping
python scrape_and_notify.py --date 2025-10-09 --sports tennis --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx" --headless --sort score
```

### 4. Quick test (sprawdzenie czy działa):
```
→ Kliknij: test_tennis_quick.bat
→ Tylko 10 meczów, szybki test
```

---

## 💡 **TIPS & TRICKS:**

### Zbierz więcej danych:
```powershell
# Bez limitu meczów (może trwać dłużej)
python scrape_and_notify.py --date 2025-10-09 --sports tennis --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx" --headless
```

### Sortowanie po wyniku (najlepsze typy na górze):
```powershell
--sort score  # Zamiast --sort time
```

### Tryb debug (więcej informacji):
```powershell
# Bez --headless (zobaczysz przeglądarkę)
python scrape_and_notify.py --date 2025-10-09 --sports tennis --to jakub.majka.zg@gmail.com --from-email jakub.majka.zg@gmail.com --password "vurb tcai zaaq itjx" --sort time
```

---

## 📊 **CO OTRZYMASZ:**

Po uruchomieniu dostaniesz:

1. **Email** na `jakub.majka.zg@gmail.com`:
   - Lista zakwalifikowanych meczów
   - Scoring dla każdego
   - Prawdopodobieństwo wygranej (np. 86.7%)
   - Typ turnieju (Grand Slam, Masters, ATP 250)

2. **Plik CSV** w `outputs/`:
   - `livesport_h2h_YYYY-MM-DD_tennis_EMAIL.csv`
   - Pełne dane wszystkich meczów
   - Breakdown scoringu

3. **Log** w `scraper_log.txt`:
   - Historia uruchomień
   - Data i czas każdego scrapingu

---

## 🚀 **REKOMENDACJA:**

### Dla codziennego użytku:
```
1. Ustaw daily_scraper_tennis.bat w Task Scheduler (10:00 rano)
2. Każdego dnia dostajesz email z analizą
3. Sprawdzasz email, wybierasz najlepsze typy
```

### Dla testów:
```
1. Kliknij test_tennis_quick.bat
2. Poczekaj 2-3 minuty
3. Sprawdź czy dostałeś email
```

### Dla ręcznego użycia:
```
1. Kliknij run_tennis_only.bat
2. Poczekaj aż skończy
3. Sprawdź wyniki
```

---

## 🎾 **PRZYKŁAD WYJŚCIA:**

```
========================================
  FLASHSCORE SCRAPER - TENIS 🎾
========================================

Start: 2025-10-08 10:00:15

Scrapuję mecze tenisowe na dzień: 2025-10-09
System: Tennis V3 Enhanced

[Processing...] 25 matches found
[Analysis...] Using V3 Enhanced scoring
[Qualified...] 8 matches passed threshold

Results:
✅ Alcaraz vs Rune - Score: 63.8 - Prob: 86.7% - Grand Slam
✅ Djokovic vs Nadal - Score: 71.2 - Prob: 91.3% - Masters 1000
...

========================================
Zakończono: 2025-10-08 10:23:47
========================================

Sprawdź email oraz katalog outputs/
```

---

**Gotowe do użycia!** 🚀

Wybierz opcję która Ci odpowiada i uruchom! 🎾


