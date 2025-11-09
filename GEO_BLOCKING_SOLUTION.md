# 🇵🇱 GEO-BLOCKING SOLUTION - Polish Bookmakers

## 🚨 Problem

GitHub Actions (USA servers) nie ma dostępu do polskich bukmacherów:
- **Fortuna** → `403 Forbidden` (geo-blocking)
- **Superbet** → `403 Forbidden` (geo-blocking)
- **STS** → `403 Forbidden` (geo-blocking)

**Rezultat**: Email pokazuje "Brak kursów" dla wszystkich meczów ❌

---

## ✅ Rozwiązanie - Dual-Source Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Twój Komputer (Polska IP)                                      │
│                                                                  │
│  1. local_bookmaker_scraper.py                                  │
│     - Scrapa Fortuna/Superbet/STS                               │
│     - Normalizuje nazwy drużyn                                  │
│     - Działa codziennie o 21:00                                 │
│                                                                  │
│  2. Wysyła do Supabase                                          │
│     ↓ INSERT INTO bookmaker_odds                                │
└──────────────────┼──────────────────────────────────────────────┘
                   │
                   ▼
     ┌─────────────────────────────┐
     │  Supabase PostgreSQL        │
     │  (Cloud, dostępny globalnie)│
     │                              │
     │  Tabela: bookmaker_odds      │
     │  - match_key                 │
     │  - bookmakers (JSON)         │
     │  - match_date                │
     └─────────────┬────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│  GitHub Actions (USA server)                                     │
│                                                                   │
│  1. scrape_and_notify.py                                         │
│     - Próbuje LiveSport API (może nie działać dla PL)           │
│                                                                   │
│  2. FALLBACK: get_polish_bookmaker_odds_from_supabase()          │
│     ↓ SELECT FROM bookmaker_odds WHERE match_key = ...          │
│     ✅ Pobiera kursy Fortuna/Superbet/STS                        │
│                                                                   │
│  3. Email z pełnymi kursami!                                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📦 Komponenty

### 1. **supabase_bookmaker_odds_schema.sql**
Schemat bazy danych dla kursów:
- Tabela `bookmaker_odds`
- Indeksy dla szybkiego wyszukiwania
- Funkcje normalizacji nazw drużyn
- Automatyczne czyszczenie starych danych (>30 dni)

**Użycie**:
```sql
-- W Supabase SQL Editor
-- Paste całą zawartość pliku i uruchom
```

### 2. **local_bookmaker_scraper.py**
Scraper działający lokalnie (Polska):
- Scrapa Fortuna/Superbet/STS
- Normalizuje nazwy drużyn (lowercase, bez polskich znaków)
- Wysyła do Supabase
- **Wymaga Python 3.11+**

**Instalacja**:
```bash
pip install requests beautifulsoup4 cloudscraper supabase
```

**Uruchomienie**:
```bash
# Set credentials
set SUPABASE_URL=https://bfslhqnxsgmdyptrqshj.supabase.co
set SUPABASE_KEY=your_service_role_key_here

# Run
python local_bookmaker_scraper.py
```

### 3. **test_local_scraper.bat**
Test script dla Windows:
- Sprawdza dependencies
- Weryfikuje IP (czy Polska)
- Testuje połączenie z Supabase
- Uruchamia scraper

**Użycie**:
```bash
# Double-click lub:
test_local_scraper.bat
```

### 4. **setup_windows_task_scheduler.bat**
Automatyczna konfiguracja Windows Task Scheduler:
- Tworzy scheduled task "PolishBookmakerScraper"
- Uruchamia codziennie o 21:00 (9 PM)
- Zapisuje logi

**Użycie**:
```bash
# Right-click → Run as Administrator
setup_windows_task_scheduler.bat
```

### 5. **livesport_h2h_scraper.py** (zmodyfikowany)
Dodano funkcję `get_polish_bookmaker_odds_from_supabase()`:
- Automatyczny fallback gdy LiveSport API zawodzi
- Normalizuje nazwy drużyn (matching)
- Pobiera z Supabase
- Format zgodny z API response

**Priorytet sourcesów**:
1. LiveSport API (primary)
2. **Supabase** (Polish bookmakers fallback) ← NOWE
3. Selenium scraping (last resort)

---

## 🚀 Setup Instructions

### KROK 1: Supabase - Create Table

1. Idź do: https://supabase.com/dashboard/project/bfslhqnxsgmdyptrqshj/editor
2. Kliknij "SQL Editor"
3. Nowy query → Wklej całą zawartość `supabase_bookmaker_odds_schema.sql`
4. Uruchom (Run)
5. Sprawdź czy tabela `bookmaker_odds` istnieje

### KROK 2: Get Supabase Service Role Key

1. Idź do: https://supabase.com/dashboard/project/bfslhqnxsgmdyptrqshj/settings/api
2. Skopiuj **service_role** key (NIE anon key!)
3. To jest `SUPABASE_KEY` dla local scraper

### KROK 3: Setup Local Scraper (Twój Komputer)

```bash
# 1. Install Python dependencies
pip install requests beautifulsoup4 cloudscraper supabase

# 2. Set environment variables
set SUPABASE_URL=https://bfslhqnxsgmdyptrqshj.supabase.co
set SUPABASE_KEY=your_service_role_key_from_step2

# 3. Test scraper
python test_local_scraper.bat

# 4. Verify your IP is in Poland
# The test script will show your country

# 5. Check Supabase
# Go to: https://supabase.com/dashboard/project/bfslhqnxsgmdyptrqshj/editor
# Table: bookmaker_odds
# Should see new rows with today's matches
```

### KROK 4: Schedule Daily Execution

```bash
# Run as Administrator
setup_windows_task_scheduler.bat

# Follow prompts:
# - Enter SUPABASE_KEY
# - Verify task creation
# - Test manually: schtasks /Run /TN "PolishBookmakerScraper"
```

### KROK 5: GitHub Actions - Add Supabase Secrets

1. Idź do: https://github.com/JKM872/Ratunek100/settings/secrets/actions
2. Dodaj secret:
   - Name: `SUPABASE_KEY`
   - Value: `your_service_role_key` (same as local)
3. `SUPABASE_URL` już istnieje (nie zmieniaj)

### KROK 6: Test End-to-End

```bash
# 1. Local scraper should run (manual or scheduled at 21:00)
python local_bookmaker_scraper.py

# 2. Check Supabase - should have data
# https://supabase.com/dashboard/.../editor (bookmaker_odds table)

# 3. Run GitHub Actions workflow
# https://github.com/JKM872/Ratunek100/actions
# Click "All Sports Scraping" → Run workflow

# 4. Check logs for:
#    "🇵🇱 API failed - trying Supabase (Polish bookmakers)..."
#    "✅ Supabase SUCCESS: ['Fortuna', 'Superbet', 'STS']"

# 5. Email should show Fortuna/Superbet/STS odds (not "Brak kursów")
```

---

## 📊 Data Flow Example

### Local Scraper Output (21:00 daily):
```json
{
  "match_key": "legia_warszawa_vs_lech_poznan",
  "match_date": "2025-01-15",
  "home_team_original": "Legia Warszawa",
  "away_team_original": "Lech Poznań",
  "bookmakers": {
    "fortuna": {"home_odds": 2.10, "away_odds": 1.65, "draw_odds": 3.20},
    "superbet": {"home_odds": 2.05, "away_odds": 1.70, "draw_odds": 3.10},
    "sts": {"home_odds": 2.15, "away_odds": 1.60, "draw_odds": 3.25}
  },
  "sport": "football"
}
```

### GitHub Actions (next day):
```
[1/150] Processing: Legia Warszawa vs Lech Poznań
   🌐 Trying LiveSport API...
   ⚠️ API returned no odds (geo-blocking)
   🇵🇱 API failed - trying Supabase (Polish bookmakers)...
   ✅ Supabase SUCCESS: ['Fortuna', 'Superbet', 'STS']
   📊 Best odds: 2.15 (STS) / 1.70 (Superbet)
```

### Email Output:
```html
Legia Warszawa vs Lech Poznań | 20:00

🔴 Fortuna (PRIORYTET): 2.10 / 3.20 / 1.65
🔵 Superbet: 2.05 / 3.10 / 1.70  
🟢 STS: 2.15 / 3.25 / 1.60

H2H: 3-2 (z 5)
```

---

## 🔧 Customization

### Change Scraping Time

Edit Task Scheduler:
```bash
# Open Task Scheduler GUI
taskschd.msc

# Find: PolishBookmakerScraper
# Right-click → Properties
# Triggers → Edit
# Change time from 21:00 to desired time
```

Or re-run setup script with different time:
```bash
# Edit setup_windows_task_scheduler.bat
# Find line: /ST 21:00
# Change to: /ST 20:00 (or any HH:MM)
```

### Add More Bookmakers

Edit `local_bookmaker_scraper.py`:
```python
# Add new scraper class
class EtotoScraperPL(BookmakerScraperBase):
    def scrape_football_odds(self):
        # ... implement scraping logic
        
# Add to orchestrator
def run_daily_scraping(self):
    fortuna = self.fortuna.scrape_football_odds()
    superbet = self.superbet.scrape_football_odds()
    sts = self.sts.scrape_football_odds()
    etoto = EtotoScraperPL().scrape_football_odds()  # NEW
    
    merged = self.uploader.merge_odds(fortuna, superbet, sts, etoto)
```

### Change Sports

Currently: **Football only**

To add basketball/volleyball:
```python
# In local_bookmaker_scraper.py

class FortunaScraperPL:
    def scrape_basketball_odds(self):
        url = f"{self.BASE_URL}/zaklady-bukmacherskie/koszykowka"
        # ... similar to scrape_football_odds()
        
# Update orchestrator
def run_daily_scraping(self):
    # Football
    football_odds = self.scrape_all_bookmakers('football')
    self.upload(football_odds, sport='football')
    
    # Basketball
    basketball_odds = self.scrape_all_bookmakers('basketball')
    self.upload(basketball_odds, sport='basketball')
```

---

## 🐛 Troubleshooting

### Problem: "Brak kursów" w emailu
**Możliwe przyczyny**:
1. Local scraper nie działa
2. Supabase jest pusty
3. GitHub Actions nie ma SUPABASE_KEY

**Rozwiązanie**:
```bash
# 1. Check local scraper
python local_bookmaker_scraper.py

# 2. Check Supabase
# https://supabase.com/.../editor
# SELECT * FROM bookmaker_odds WHERE match_date = CURRENT_DATE;

# 3. Check GitHub secrets
# https://github.com/.../settings/secrets/actions
# Verify SUPABASE_KEY exists

# 4. Check GitHub Actions logs
# Search for "Supabase" in logs
# Should see: "✅ Supabase SUCCESS"
```

### Problem: Task Scheduler nie działa
```bash
# Check task status
schtasks /Query /TN "PolishBookmakerScraper" /V

# Check logs
type c:\Users\jakub\Downloads\Ratowanie\scraper_log.txt

# Run manually
schtasks /Run /TN "PolishBookmakerScraper"

# Delete and recreate
schtasks /Delete /TN "PolishBookmakerScraper" /F
setup_windows_task_scheduler.bat
```

### Problem: CloudFlare blocking
**Symptom**: "403 Forbidden" even on Polish IP

**Solution**: Install cloudscraper
```bash
pip install cloudscraper[ssl]
```

### Problem: Wrong team names (no matching)
**Symptom**: Supabase has data but GitHub Actions doesn't find it

**Debug**:
```python
# In livesport_h2h_scraper.py, add print:
match_key = generate_match_key(home_team, away_team)
print(f"DEBUG: Looking for match_key: {match_key}")

# Compare with Supabase:
SELECT match_key FROM bookmaker_odds WHERE match_date = CURRENT_DATE;

# If different, check normalization logic
```

---

## 📈 Expected Results

### Before (Geo-blocking):
```
❌ Fortuna: Brak kursów
❌ Superbet: Brak kursów  
❌ STS: Brak kursów
```

### After (Supabase fallback):
```
✅ Fortuna: 2.10 / 3.20 / 1.65
✅ Superbet: 2.05 / 3.10 / 1.70
✅ STS: 2.15 / 3.25 / 1.60
```

### Success Metrics:
- ✅ Local scraper runs daily at 21:00
- ✅ Supabase has 50-100+ matches daily
- ✅ GitHub Actions finds 80%+ matches via Supabase
- ✅ Email shows Polish bookmakers odds
- ✅ No more "Brak kursów" messages

---

## 📚 Files Summary

| File | Purpose | Location |
|------|---------|----------|
| `supabase_bookmaker_odds_schema.sql` | Database schema | Run in Supabase SQL Editor |
| `local_bookmaker_scraper.py` | Local scraper (Poland) | Run on your computer |
| `test_local_scraper.bat` | Test script | Double-click to test |
| `setup_windows_task_scheduler.bat` | Auto-schedule | Run as Administrator |
| `livesport_h2h_scraper.py` | Modified scraper | Already committed |
| `GEO_BLOCKING_SOLUTION.md` | This guide | Reference |

---

## 🎯 Next Steps

1. ✅ **Create Supabase table** (Step 1)
2. ✅ **Test local scraper** (Step 3)
3. ✅ **Schedule daily** (Step 4)
4. ✅ **Add GitHub secret** (Step 5)
5. ✅ **Test end-to-end** (Step 6)

**Status**: Ready to deploy! 🚀

---

## ⚠️ IMPORTANT NOTES

1. **Local scraper must run on POLISH IP**
   - VPN won't work reliably
   - Proxy may be detected
   - Best: Run on computer in Poland

2. **Service Role Key = Full access**
   - Keep it SECRET
   - Never commit to Git
   - Store in environment variables only

3. **Rate limiting**
   - Local scraper has delays (3s between bookmakers)
   - Don't run too frequently
   - Once daily at 21:00 is optimal

4. **Data freshness**
   - Odds are from previous day (21:00)
   - Good enough for next day's matches
   - Real-time odds not guaranteed

5. **HTML structure changes**
   - Bookmaker websites may change HTML
   - Scrapers need periodic updates
   - Monitor error logs

---

**Made with ❤️ by AI Assistant**
**Version: 1.0**
**Date: 2025-01-15**
