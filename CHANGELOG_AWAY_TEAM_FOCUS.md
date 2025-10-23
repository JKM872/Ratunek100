# 🆕 CHANGELOG v6.4 - Fokus na Drużynach Gości

## Data: 2025-10-12

## 🎯 Główne zmiany

### Nowa funkcjonalność: Away Team Focus

Dodano możliwość analizy meczów gdzie **GOŚCIE** (away teams) mają przewagę w bezpośrednich spotkaniach (H2H) zamiast gospodarzy.

---

## ✨ Co nowego?

### 1. **Nowy argument wiersza poleceń**
- `--away-team-focus` - przełącza scraper w tryb analizy drużyn gości

**Przykład:**
```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football --away-team-focus --headless
```

### 2. **Rozszerzona funkcja `process_match()`**
- Dodano parametr `away_team_focus: bool = False`
- Funkcja liczy teraz zwycięstwa zarówno gospodarzy jak i gości
- Automatyczne przełączanie logiki kwalifikacji w zależności od trybu

**Nowe kolumny w wynikach:**
- `away_wins_in_h2h_last5` - liczba zwycięstw gości w H2H
- `focus_team` - który tryb jest aktywny ('home' lub 'away')

### 3. **Pliki batch dla łatwego uruchamiania**

Utworzono 4 nowe pliki batch:
- `run_all_sports_away_focus.bat` - wszystkie sporty, fokus na gościach
- `run_football_away_focus.bat` - tylko piłka nożna, fokus na gościach
- `daily_scraper_away_focus.bat` - dzienny scraper (automatyczna data)
- `daily_scraper_away_focus_with_email.bat` - dzienny scraper z opcją email

### 4. **Zaktualizowana dokumentacja**

Nowe pliki:
- `AWAY_TEAM_FOCUS_GUIDE.md` - pełny przewodnik po nowej funkcjonalności
- `AWAY_TEAM_QUICKSTART.md` - szybki start (5 minut)
- `CHANGELOG_AWAY_TEAM_FOCUS.md` - ten plik

Zaktualizowane pliki:
- `README.md` - dodano sekcję o nowej funkcjonalności
- `livesport_h2h_scraper.py` - rozszerzona funkcjonalność

### 5. **Ulepszone komunikaty**

Scraper pokazuje teraz w konsoli:
```
🎯 Fokus: GOŚCIE (away teams) z ≥60% H2H
...
📊 Podstawowo kwalifikuje (GOŚCIE: Liverpool, H2H: 80%) - sprawdzam formę...
✅ KWALIFIKUJE + PRZEWAGA FORMY GOŚCI! 🔥
   Zespół fokusowany: Liverpool
   H2H: 4/5 (80%)
```

### 6. **Automatyczne nazewnictwo plików**

Pliki wynikowe otrzymują sufiks `_AWAY_FOCUS`:
- `livesport_h2h_2025-10-12_football_AWAY_FOCUS.csv`
- `livesport_h2h_2025-10-12_basketball_AWAY_FOCUS.csv`

---

## 🔧 Zmiany techniczne

### Modyfikacje w kodzie

#### `process_match()` - linie ~238-510
```python
def process_match(url: str, driver: webdriver.Chrome, away_team_focus: bool = False) -> Dict:
    # ... (nowa logika)
    out['away_wins_in_h2h_last5'] = cnt_away  # NOWE
    out['focus_team'] = 'away' if away_team_focus else 'home'  # NOWE
    
    if away_team_focus:
        # Tryb GOŚCIE
        win_rate = (cnt_away / len(h2h)) if len(h2h) > 0 else 0.0
    else:
        # Tryb GOSPODARZE (domyślny)
        win_rate = (cnt_home / len(h2h)) if len(h2h) > 0 else 0.0
```

#### `main()` - linie ~1559-1807
```python
# Nowy argument
parser.add_argument('--away-team-focus', action='store_true', 
                   help='Szukaj meczów gdzie GOŚCIE mają >=60%% zwycięstw w H2H')

# Wywołanie z nowym parametrem
info = process_match(url, driver, away_team_focus=args.away_team_focus)
```

#### Nazewnictwo plików - linie ~1776-1785
```python
# Dodaj sufiks dla trybu away_team_focus
if args.away_team_focus:
    suffix = f'{suffix}_AWAY_FOCUS'
```

---

## 🎯 Wspierane sporty

Tryb away-team-focus działa dla wszystkich sportów drużynowych:
- ⚽ Piłka nożna (football)
- 🏀 Koszykówka (basketball)
- 🏐 Siatkówka (volleyball)
- 🤾 Piłka ręczna (handball)
- 🏉 Rugby (rugby)
- 🏒 Hokej (hockey)

---

## 📊 Przykłady użycia

### Podstawowe
```bash
# Wszystkie sporty
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football basketball volleyball handball rugby hockey --away-team-focus --headless

# Tylko piłka nożna
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football --away-team-focus --headless
```

### Z filtrowaniem
```bash
# Konkretne ligi
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football --leagues premier-league la-liga --away-team-focus --headless
```

### Windows batch
```batch
# Edytuj datę w pliku i kliknij dwukrotnie
run_all_sports_away_focus.bat
```

---

## 🔍 Struktura wyników CSV

### Nowe kolumny:
| Kolumna | Typ | Opis |
|---------|-----|------|
| `away_wins_in_h2h_last5` | int | Liczba zwycięstw gości w H2H |
| `focus_team` | str | 'home' lub 'away' - który tryb |

### Istniejące kolumny (zachowane):
- `match_url`, `home_team`, `away_team`, `match_time`
- `home_wins_in_h2h_last5` - teraz zawsze obliczane
- `h2h_count`, `win_rate`, `qualifies`
- `home_form`, `away_form`, `form_advantage`

---

## ⚠️ Kompatybilność wsteczna

✅ **Pełna kompatybilność wsteczna!**

- Wszystkie istniejące komendy działają bez zmian
- Domyślne zachowanie (fokus na gospodarzach) zachowane
- Istniejące pliki batch działają jak wcześniej
- API nie zmienione

---

## 🐛 Poprawione błędy

- Naprawiono escape % w help string (ValueError)
- Dodano obsługę away_wins w fallback logic

---

## 📚 Dokumentacja

Nowe przewodniki:
1. **AWAY_TEAM_FOCUS_GUIDE.md** - kompletny przewodnik (200+ linii)
2. **AWAY_TEAM_QUICKSTART.md** - szybki start (50 linii)

Zaktualizowane:
- **README.md** - sekcja "NOWOŚCI v6.4"
- **Wszystkie parametry** - dodano `--away-team-focus`
- **Przykłady użycia** - 3 nowe scenariusze

---

## 🚀 Migracja

### Nie wymagana!
Jeśli używasz scrapera w trybie domyślnym, wszystko działa jak wcześniej.

### Opcjonalnie - wypróbuj nowy tryb:
```bash
# Stare (nadal działa)
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football --headless

# Nowe (fokus na gościach)
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football --away-team-focus --headless
```

---

## 👥 Autorzy

- **Jakub Majka** - implementacja nowej funkcjonalności

---

## 🔜 Plany na przyszłość

Potencjalne ulepszenia:
- Integracja z `scrape_and_notify.py` (email dla trybu away)
- API endpoint dla trybu away-team-focus
- Automatyczna analiza "value bets" dla gości
- Statystyki porównawcze home vs away

---

**Wersja:** 6.4  
**Data:** 2025-10-12  
**Status:** ✅ Stable

