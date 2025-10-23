# 🔥 Przykłady Użycia - Przewaga Formy

## Szybki Start

### 1. Podstawowe użycie (z wiersza poleceń)

#### Standardowy tryb - wszystkie kwalifikujące mecze
```bash
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to twoj@email.com \
  --from twoj@email.com \
  --password "twoje_app_password" \
  --headless
```

#### 🔥 NOWY: Tylko mecze z przewagą formy
```bash
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to twoj@email.com \
  --from twoj@email.com \
  --password "twoje_app_password" \
  --headless \
  --only-form-advantage
```

---

## Przykłady dla różnych scenariuszy

### Scenariusz 1: Codzienne powiadomienie o najlepszych meczach
```bash
# Uruchamiaj codziennie o 10:00 rano
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football basketball \
  --to manager@firma.com \
  --from bot@firma.com \
  --password "app_password_123" \
  --provider gmail \
  --headless \
  --only-form-advantage
```

**Efekt:** Otrzymasz email tylko z meczami, gdzie gospodarze mają przewagę formy 🔥

---

### Scenariusz 2: Weekend - wszystkie mecze
```bash
# Sobota/Niedziela - pokaż wszystkie możliwości
python scrape_and_notify.py \
  --date 2025-10-12 \
  --sports football basketball handball volleyball \
  --to analityk@firma.com \
  --from bot@firma.com \
  --password "app_password_123" \
  --headless
```

**Efekt:** Otrzymasz email ze WSZYSTKIMI kwalifikującymi się meczami (większy przegląd)

---

### Scenariusz 3: Szybka analiza dzisiejszych TOP meczów
```bash
# Przed południem - szybki przegląd najlepszych meczów
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to director@firma.com \
  --from bot@firma.com \
  --password "app_password_123" \
  --headless \
  --only-form-advantage \
  --sort time
```

**Efekt:** Email z najlepszymi meczami posortowanymi chronologicznie ⏰

---

### Scenariusz 4: Test na małej próbce
```bash
# Testuj nową funkcję na 10 meczach
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to test@email.com \
  --from twoj@email.com \
  --password "haslo" \
  --max-matches 10 \
  --only-form-advantage
```

**Efekt:** Szybki test - tylko 10 meczów, tylko z przewagą formy

---

## Użycie pliku .bat (Windows)

### Krok 1: Edytuj `daily_scraper_form_advantage_only.bat`

```batch
REM Adres email odbiorcy
set TO_EMAIL=twoj@email.com

REM Adres email nadawcy (Gmail)
set FROM_EMAIL=twoj@gmail.com

REM Hasło aplikacji Gmail
set PASSWORD=twoje_app_password

REM Sporty do scrapowania
set SPORTS=football basketball
```

### Krok 2: Uruchom plik
- Kliknij dwukrotnie na `daily_scraper_form_advantage_only.bat`
- Lub uruchom z wiersza poleceń:
```bash
daily_scraper_form_advantage_only.bat
```

---

## Porównanie: Standardowy vs Form Advantage

### Przykład: Liga angielska 2025-10-11

#### Standardowy tryb wysyła (10 meczów):
```
📧 Email: "10 kwalifikujących się meczów - 2025-10-11"

1. ⚽ Arsenal vs Chelsea (H2H: 60%)
2. ⚽ Liverpool vs Man City (H2H: 80%) 🔥
3. ⚽ Tottenham vs Brighton (H2H: 60%)
4. ⚽ Man United vs Everton (H2H: 70%)
5. ⚽ Newcastle vs West Ham (H2H: 75%) 🔥
6. ⚽ Aston Villa vs Wolves (H2H: 60%)
7. ⚽ Fulham vs Brentford (H2H: 65%)
8. ⚽ Crystal Palace vs Bournemouth (H2H: 70%)
9. ⚽ Nottingham vs Luton (H2H: 80%) 🔥
10. ⚽ Burnley vs Sheffield (H2H: 60%)
```

#### Tryb `--only-form-advantage` wysyła (3 mecze):
```
📧 Email: "🔥 3 meczów z PRZEWAGĄ FORMY - 2025-10-11"

1. ⚽ Liverpool vs Man City (H2H: 80%) 🔥
   🏠 Liverpool: W✅ W✅ W✅ W✅ W✅
   ✈️  Man City: L❌ L❌ D🟡 L❌ W✅

2. ⚽ Newcastle vs West Ham (H2H: 75%) 🔥
   🏠 Newcastle: W✅ W✅ D🟡 W✅ W✅
   ✈️  West Ham: L❌ D🟡 L❌ L❌ D🟡

3. ⚽ Nottingham vs Luton (H2H: 80%) 🔥
   🏠 Nottingham: W✅ W✅ W✅ D🟡 W✅
   ✈️  Luton: L❌ L❌ L❌ L❌ W✅
```

**Różnica:** 
- ⚡ **70% mniej meczów** do analizy
- 🎯 **Tylko najlepsze** okazje
- 📧 **Krótszy email**, łatwiejszy do przejrzenia

---

## Automatyzacja (Windows Task Scheduler)

### Konfiguracja 1: Codziennie o 11:00 - najlepsze mecze
```
Zadanie: "Najlepsze mecze dnia"
Wyzwalacz: Codziennie o 11:00
Akcja: daily_scraper_form_advantage_only.bat
```

### Konfiguracja 2: Codziennie o 8:00 - wszystkie mecze
```
Zadanie: "Wszystkie mecze dnia"
Wyzwalacz: Codziennie o 8:00
Akcja: daily_scraper_all_sports.bat
```

**Efekt:** Otrzymujesz 2 emaile:
- 🌅 8:00 - pełny przegląd wszystkich meczów
- ☀️ 11:00 - tylko TOP mecze z przewagą formy

---

## Kombinacje z innymi opcjami

### Sortowanie po liczbie wygranych + przewaga formy
```bash
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to twoj@email.com \
  --from twoj@email.com \
  --password "haslo" \
  --only-form-advantage \
  --sort wins
```

### Wiele sportów + przewaga formy
```bash
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football basketball handball volleyball \
  --to twoj@email.com \
  --from twoj@email.com \
  --password "haslo" \
  --only-form-advantage
```

### Tryb widoczny (bez headless) + przewaga formy
```bash
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to twoj@email.com \
  --from twoj@email.com \
  --password "haslo" \
  --only-form-advantage
  # Brak flagi --headless = widoczna przeglądarka
```

---

## Testowanie z istniejącym plikiem CSV

Jeśli już masz wyskrapowane dane, możesz przetestować filtrowanie:

```bash
# Test 1: Standardowy email (wszystkie kwalifikujące)
python email_notifier.py \
  --csv outputs/livesport_h2h_2025-10-11_football.csv \
  --to test@email.com \
  --from twoj@email.com \
  --password "haslo"

# Test 2: Tylko z przewagą formy
python email_notifier.py \
  --csv outputs/livesport_h2h_2025-10-11_football.csv \
  --to test@email.com \
  --from twoj@email.com \
  --password "haslo" \
  --only-form-advantage
```

---

## FAQ - Przykłady

### Q: Jak wysłać email z meczami jutrzejszymi?
```bash
python scrape_and_notify.py \
  --date 2025-10-12 \
  --sports football \
  --to twoj@email.com \
  --from twoj@email.com \
  --password "haslo" \
  --only-form-advantage
```

### Q: Jak sprawdzić dane bez wysyłania emaila?
```bash
# 1. Scrapuj dane zwykłym scraperem
python livesport_h2h_scraper.py \
  --mode auto \
  --date 2025-10-11 \
  --sports football \
  --headless

# 2. Sprawdź plik CSV
# outputs/livesport_h2h_2025-10-11_football.csv
# Kolumna "form_advantage" pokazuje True/False
```

### Q: Jak zmienić provider emaila na Outlook?
```bash
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to twoj@outlook.com \
  --from twoj@outlook.com \
  --password "haslo" \
  --provider outlook \
  --only-form-advantage
```

---

## Wsparcie

Więcej informacji:
- 📖 `FORM_ADVANTAGE_GUIDE.md` - Pełny przewodnik
- 📧 `EMAIL_SETUP.md` - Konfiguracja emaili
- 🧪 `test_form_advantage.py` - Uruchom testy

---

**Powodzenia!** 🎯🔥




