# 🏆 Livesport H2H Scraper - Multi-Sport Edition

Zaawansowany skrypt do automatycznego zbierania danych o bezpośrednich spotkaniach (H2H) z Livesport.com dla wielu sportów drużynowych.

## 🎯 Cel

Dla danego dnia zapisuje do pliku CSV mecze, w których **gospodarze lub goście wygrali co najmniej 60% bezpośrednich spotkań** (H2H).

**NOWOŚĆ:** Możliwość wyboru fokusa:
- **Tryb domyślny (GOSPODARZE):** Filtruje mecze gdzie gospodarze mają ≥60% wygranych w H2H
- **Tryb GOŚCIE (`--away-team-focus`):** Filtruje mecze gdzie goście mają ≥60% wygranych w H2H

## ⚽ Wspierane sporty

### Sporty drużynowe (≥2 wygrane w H2H):
- **Piłka nożna** (football/soccer)
- **Koszykówka** (basketball)
- **Siatkówka** (volleyball)  
- **Piłka ręczna** (handball)
- **Rugby** (rugby)
- **Hokej** (hockey/ice-hockey)

### Sporty indywidualne (więcej wygranych w H2H):
- **Tenis** (tennis) - zawodnik musi wygrać ≥1 mecz + mieć więcej wygranych niż przeciwnik

## 📋 Wymagania

- Python 3.9+
- Chrome browser
- Chromedriver (instalowany automatycznie przez `webdriver-manager`)

## 🚀 Instalacja

```bash
pip install -r requirements.txt
```

## ✨ NOWOŚCI:

### 🎯 Fokus na Drużynach Gości! **[NOWOŚĆ v6.4]**
Teraz możesz analizować mecze gdzie **GOŚCIE** mają przewagę w H2H!
- 🏃 **Tryb AWAY TEAMS** - mecze gdzie goście wygrali ≥60% H2H
- ⚽ **Wszystkie sporty drużynowe** - football, basketball, volleyball, handball, rugby, hockey
- 🎯 **Osobne pliki batch** - łatwe uruchamianie z `run_all_sports_away_focus.bat`
- 📊 **Pełna analiza formy** - tak samo jak dla gospodarzy

**Przykład użycia:**
```bash
# Wszystkie sporty - fokus na gościach
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football basketball --away-team-focus --headless

# Tylko piłka nożna - fokus na gościach
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football --away-team-focus --headless
```

**[Zobacz: AWAY_TEAM_FOCUS_GUIDE.md](AWAY_TEAM_FOCUS_GUIDE.md)**

### 💰 Pomijanie Meczów Bez Kursów! **[NOWOŚĆ v6.3]**
Wysyłaj emaile tylko z meczami, które mają KURSY BUKMACHERSKIE!
- 💰 **Tylko mecze z kursami** - pełne dane dla analizy
- 🎯 **Tryb Premium** - łącz z `--only-form-advantage` dla TOP meczów
- 📊 **Dla analityków** - idealne dla pracy z bukmacherami
- 🔧 **Opcjonalne** - wszystko działa jak wcześniej!

**[Zobacz: PRZEWODNIK_POMIJANIE_KURSOW.md](PRZEWODNIK_POMIJANIE_KURSOW.md)**

### 🔥 Filtrowanie po Przewadze Formy! **[NOWOŚĆ v6.2]**
Wysyłaj emaile tylko z meczami, gdzie gospodarze mają PRZEWAGĘ W FORMIE!
- 🎯 **30-50% mniej meczów** - tylko najlepsze okazje
- ⚡ **Przyspiesza proces** - szybsza analiza
- 🔥 **Większa precyzja** - gospodarze w dobrej formie + goście w słabej
- 📧 **Opcjonalne** - stara funkcjonalność działa bez zmian!

**[Zobacz: FORM_ADVANTAGE_GUIDE.md](FORM_ADVANTAGE_GUIDE.md)**

### 🎯 System Weryfikacji Przewidywań! **[NOWOŚĆ v6.0]**
Automatyczne sprawdzanie trafności typów z poprzednich dni + szczegółowe raporty!
- ✅ Trafność ogólna i per-sport (Tennis vs Team Sports)
- 💰 Analiza ROI (Return on Investment)
- 📊 Top 5 najlepszych i najgorszych typów
- 📧 Automatyczne wysyłanie raportów emailem

**[Zobacz: VERIFICATION_GUIDE.md](VERIFICATION_GUIDE.md)**

### 📧 Powiadomienia Email!
Automatycznie wysyłaj ładne powiadomienia email z kwalifikującymi się meczami!

### ⏰ Sortowanie chronologiczne!
Mecze automatycznie posortowane po godzinie!

### 🔄 Auto-Restart!
Chrome automatycznie restartuje się co 80 meczów - **zero crashów** nawet przy 1500+ meczach!

### 🌐 REST API!
Integruj scraper z dowolną aplikacją (web, mobile, desktop) przez REST API!

### Szybki start z API:

```bash
# Uruchom API server
python api_server.py

# API dostępne pod: http://localhost:5000
# Dokumentacja: API_QUICKSTART.md
```

### Szybki start z emailem:

```bash
# Scrapuj mecze i wyślij email w jednym kroku
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "twoje_app_password" \
  --headless

# 🔥 NOWE: Tylko mecze z PRZEWAGĄ FORMY (przyspiesza proces!)
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "twoje_app_password" \
  --headless \
  --only-form-advantage

# 💰 NOWE: Tylko mecze Z KURSAMI bukmacherskimi
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "twoje_app_password" \
  --headless \
  --skip-no-odds

# 🎯 TRYB PREMIUM: Forma + Kursy (najlepsze mecze!)
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "twoje_app_password" \
  --headless \
  --only-form-advantage \
  --skip-no-odds
```

**Opcje sortowania:**
- `--sort time` - po godzinie (domyślnie) ⏰
- `--sort wins` - po liczbie wygranych 🏆
- `--sort team` - alfabetycznie 📝

**📖 Pełna instrukcja:** Zobacz [EMAIL_SETUP.md](EMAIL_SETUP.md)

---

## 💻 Użycie

### Tryb 1: Lista URLi (`--mode urls`)

Przetwarzanie konkretnych meczów z pliku tekstowego:

```bash
python livesport_h2h_scraper.py --mode urls --date 2025-10-05 --input match_urls.txt --headless
```

Plik `match_urls.txt` powinien zawierać jeden URL na linię (patrz przykład w repozytorium).

### Tryb 2: Automatyczne zbieranie (`--mode auto`)

#### Dla jednego sportu:

```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --headless
```

#### Dla wielu sportów naraz:

```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball volleyball --headless
```

#### Wszystkie wspierane sporty:

```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball volleyball handball rugby hockey --headless
```

#### 🆕 Fokus na drużynach GOŚCI (away teams):

```bash
# Wszystkie sporty - goście z przewagą H2H
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball volleyball handball rugby hockey --away-team-focus --headless

# Tylko piłka nożna - goście z przewagą H2H
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --away-team-focus --headless
```

#### Z filtrowaniem po konkretnych ligach:

```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --leagues ekstraklasa premier-league --headless
```

#### Z zaawansowanym zbieraniem linków:

```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --advanced --headless
```

## 🎛️ Wszystkie parametry

| Parametr | Opis | Przykład |
|----------|------|----------|
| `--mode` | Tryb: `urls` (z pliku) lub `auto` (automatyczne) | `--mode auto` |
| `--date` | Data w formacie YYYY-MM-DD | `--date 2025-10-05` |
| `--input` | Plik z URLami (wymagany w trybie `urls`) | `--input match_urls.txt` |
| `--sports` | Lista sportów (w trybie `auto`) | `--sports football basketball` |
| `--leagues` | Filtrowanie po ligach | `--leagues ekstraklasa nba` |
| `--headless` | Uruchom Chrome bez GUI | `--headless` |
| `--advanced` | Zaawansowane zbieranie linków | `--advanced` |
| `--output-suffix` | Dodatkowy sufiks do nazwy pliku | `--output-suffix test1` |
| `--away-team-focus` | 🆕 Szukaj meczów gdzie GOŚCIE mają ≥60% H2H (zamiast gospodarzy) | `--away-team-focus` |

## 📁 Plik wyjściowy

Wyniki zapisywane są do: `outputs/livesport_h2h_YYYY-MM-DD_SPORT.csv`

**UWAGA:** W trybie `--away-team-focus` plik otrzymuje sufiks `_AWAY_FOCUS`:
- Przykład: `outputs/livesport_h2h_2025-10-12_football_AWAY_FOCUS.csv`

### Kolumny CSV:
- `match_url` - URL meczu
- `home_team` - nazwa drużyny gospodarzy
- `away_team` - nazwa drużyny gości
- `match_time` - czas meczu (jeśli dostępny)
- `h2h_last5` - lista ostatnich 5 H2H (jako string)
- `home_wins_in_h2h_last5` - liczba zwycięstw gospodarzy w ostatnich H2H
- `away_wins_in_h2h_last5` - 🆕 liczba zwycięstw gości w ostatnich H2H (nowe!)
- `h2h_count` - łączna liczba meczów H2H
- `win_rate` - procent wygranych (gospodarzy lub gości, zależnie od trybu)
- `qualifies` - czy mecz spełnia kryterium (≥60% wygranych)
- `focus_team` - 🆕 który tryb ('home' lub 'away')

## 🏟️ Wspierane ligi

### Piłka nożna (football)
- `ekstraklasa` - Polska Ekstraklasa
- `premier-league` - Premier League (Anglia)
- `la-liga` - La Liga (Hiszpania)
- `bundesliga` - Bundesliga (Niemcy)
- `serie-a` - Serie A (Włochy)
- `ligue-1` - Ligue 1 (Francja)
- `champions-league` - Liga Mistrzów UEFA
- `europa-league` - Liga Europy UEFA

### Koszykówka (basketball)
- `nba` - NBA
- `euroleague` - Euroliga
- `energa-basket-liga` - Energa Basket Liga (Polska)
- `pbl` - Polska Liga Koszykówki

### Siatkówka (volleyball)
- `plusliga` - PlusLiga (Polska - mężczyźni)
- `tauron-liga` - Tauron Liga (Polska - kobiety)

### Piłka ręczna (handball)
- `pgnig-superliga` - PGNiG Superliga (Polska)

### Rugby
- `premiership` - Premiership (Anglia)
- `top-14` - Top 14 (Francja)

### Hokej (hockey)
- `nhl` - NHL
- `khl` - KHL

## 📊 Przykładowe użycie - Scenariusze

### Scenariusz 1: Szybki test na piłce nożnej (GOSPODARZE)
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --headless
```

### Scenariusz 2: Analiza wszystkich sportów (GOSPODARZE)
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball volleyball handball rugby hockey --headless
```

### Scenariusz 3: Tylko top ligi europejskie (GOSPODARZE)
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --leagues premier-league la-liga bundesliga serie-a --headless
```

### 🆕 Scenariusz 4: Fokus na drużynach GOŚCI - piłka nożna
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --away-team-focus --headless
```

### 🆕 Scenariusz 5: Fokus na drużynach GOŚCI - wszystkie sporty
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball volleyball handball rugby hockey --away-team-focus --headless
```

### 🆕 Scenariusz 6: Fokus na drużynach GOŚCI - konkretne ligi
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --leagues premier-league la-liga --away-team-focus --headless
```

### Scenariusz 7: Debug mode (bez headless)
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football
```

### Scenariusz 8: Własna lista meczów
```bash
# 1. Przygotuj match_urls.txt z konkretnymi URLami
# 2. Uruchom:
python livesport_h2h_scraper.py --mode urls --date 2025-10-05 --input match_urls.txt --headless
```

## ⚠️ Ważne uwagi

### Przestrzegaj zasad użytkowania:
- ✅ Sprawdź `robots.txt` Livesport przed masowym scrapowaniem
- ✅ Skrypt ma wbudowane opóźnienia (1-2.5s między requestami)
- ✅ Przy dużej skali potrzebujesz zgody właściciela serwisu
- ✅ Rozważ oficjalne API jeśli jest dostępne
- ✅ Używaj odpowiedzialnie - to narzędzie do analizy, nie do przeciążania serwera

### Ograniczenia techniczne:
- 🔧 Livesport używa JavaScript - skrypt wymaga Selenium
- 🔧 Parsowanie H2H opiera się na heurystykach - może wymagać dostosowania przy zmianach HTML
- 🔧 Struktura strony może się zmieniać
- 🔧 Nie wszystkie mecze mają dostępne dane H2H
- 🔧 Automatyczne zbieranie URLi (tryb `auto`) może być mniej niezawodne niż tryb `urls`

### Rozwiązywanie problemów:

**Problem**: Nie znajduje żadnych meczów w trybie `auto`
```bash
# Rozwiązanie 1: Uruchom bez --headless aby zobaczyć co się dzieje
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football

# Rozwiązanie 2: Użyj trybu urls z ręcznie przygotowanymi linkami
python livesport_h2h_scraper.py --mode urls --date 2025-10-05 --input match_urls.txt
```

**Problem**: Chromedriver crashes
```bash
# Zaktualizuj Chrome i przeinstaluj zależności:
pip install --upgrade selenium webdriver-manager
```

**Problem**: Błędy parsowania H2H
- Struktura HTML Livesport mogła się zmienić
- Sprawdź aktualizacje skryptu lub dostosuj selektory w kodzie

## 📝 Licencja i odpowiedzialność

Skrypt jest dostarczony "AS IS". Użytkownik ponosi pełną odpowiedzialność za:
- Przestrzeganie warunków użytkowania Livesport.com
- Przestrzeganie robots.txt
- Odpowiedzialne użytkowanie (rate limiting, zgoda właściciela przy masowym scrapowaniu)

## 🤝 Contributing

Pull requesty mile widziane! Szczególnie:
- Ulepszenia selektorów HTML
- Wsparcie dla dodatkowych sportów
- Optymalizacje wydajności
- Testy jednostkowe

---

**Wersja**: 2.0 (Multi-Sport Edition)  
**Ostatnia aktualizacja**: 2025-10-05

#   l i v e s p o r t s c r a p e r 
 
 #   R a t u n e k 1 0 0  
 