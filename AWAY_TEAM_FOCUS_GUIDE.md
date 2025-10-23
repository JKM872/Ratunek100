# 🏃 Przewodnik: Fokus na Drużynach Gości (Away Team Focus)

## 📖 Co to jest?

**Away Team Focus** to nowy tryb scrapera, który filtruje mecze gdzie **GOŚCIE** (away teams) mają przewagę w bezpośrednich spotkaniach (H2H).

## 🎯 Kiedy używać?

### Tryb domyślny (GOSPODARZE):
Szukasz meczów gdzie **gospodarze** mają przewagę:
- ✅ Drużyna gra u siebie
- ✅ Ma historyczne przewagę nad przeciwnikiem
- ✅ Tradycyjne podejście: "gospodarze są faworytem"

### Tryb GOŚCIE (`--away-team-focus`):
Szukasz meczów gdzie **goście** mają przewagę:
- 🎯 Drużyna jedzie na wyjazdowe zwycięstwo
- 🎯 Ma historyczną przewagę nad gospodarzami
- 🎯 Nietypowe okazje: "goście jako faworyci"

## 🚀 Jak używać?

### Podstawowe użycie

```bash
# Wszystkie sporty - fokus na gościach
python livesport_h2h_scraper.py \
  --mode auto \
  --date 2025-10-12 \
  --sports football basketball volleyball handball rugby hockey \
  --away-team-focus \
  --headless
```

### Tylko piłka nożna

```bash
python livesport_h2h_scraper.py \
  --mode auto \
  --date 2025-10-12 \
  --sports football \
  --away-team-focus \
  --headless
```

### Konkretne ligi

```bash
python livesport_h2h_scraper.py \
  --mode auto \
  --date 2025-10-12 \
  --sports football \
  --leagues premier-league la-liga bundesliga \
  --away-team-focus \
  --headless
```

## 🎬 Szybkie uruchamianie - pliki .bat

Stworzyliśmy gotowe pliki batch dla Windows:

### 1. `run_all_sports_away_focus.bat`
Wszystkie sporty, fokus na gościach:
```batch
run_all_sports_away_focus.bat
```

### 2. `run_football_away_focus.bat`
Tylko piłka nożna, fokus na gościach:
```batch
run_football_away_focus.bat
```

### 3. `daily_scraper_away_focus.bat`
Dzienny scraper (automatyczna data), fokus na gościach:
```batch
daily_scraper_away_focus.bat
```

**UWAGA:** Pamiętaj aby edytować datę w plikach batch przed uruchomieniem!

## 📊 Wyniki

### Nazwa pliku

W trybie `--away-team-focus` plik otrzymuje sufiks `_AWAY_FOCUS`:

```
outputs/livesport_h2h_2025-10-12_football_AWAY_FOCUS.csv
outputs/livesport_h2h_2025-10-12_basketball_AWAY_FOCUS.csv
```

### Kolumny CSV

Plik zawiera wszystkie standardowe kolumny + nowe:

| Kolumna | Opis |
|---------|------|
| `home_wins_in_h2h_last5` | Liczba zwycięstw gospodarzy w H2H |
| `away_wins_in_h2h_last5` | 🆕 **Liczba zwycięstw gości w H2H** |
| `win_rate` | Procent wygranych (gości w tym trybie) |
| `qualifies` | Czy mecz się kwalifikuje (≥60% dla gości) |
| `focus_team` | Który tryb ('away' w tym przypadku) |

### Przykładowy output

```csv
match_url,home_team,away_team,match_time,home_wins_in_h2h_last5,away_wins_in_h2h_last5,h2h_count,win_rate,qualifies,focus_team
https://...,Arsenal,Liverpool,18:00,1,4,5,0.80,True,away
https://...,Man City,Chelsea,20:45,2,3,5,0.60,True,away
```

## 📈 Interpretacja wyników

### Mecz się kwalifikuje (qualifies=True)

**Przykład:**
- Arsenal vs Liverpool
- `away_wins_in_h2h_last5 = 4`
- `h2h_count = 5`
- `win_rate = 0.80` (80%)

**Interpretacja:**
✅ Liverpool wygrał 4 z 5 ostatnich meczów z Arsenalem (80%)
✅ Mimo że grają na wyjeździe, mają historyczną przewagę
✅ To potencjalnie dobra okazja do typowania gości

### Forma drużyn

Tak jak w trybie domyślnym, scraper analizuje formę:

```
✅ KWALIFIKUJE + PRZEWAGA FORMY GOŚCI! 🔥
   Zespół fokusowany: Liverpool
   H2H: 4/5 (80%)
   Forma: Arsenal [L-L-D-W-L] | Liverpool [W-W-W-W-D]
```

## 🎯 Przypadki użycia

### 1. Analiza "silnych gości"

Znajdź drużyny które regularnie wygrywają na wyjazdach:

```bash
python livesport_h2h_scraper.py \
  --mode auto \
  --date 2025-10-12 \
  --sports football \
  --away-team-focus \
  --headless
```

### 2. Specjalne sytuacje

- 🏆 **Drużyny z dobrej ligi** grają na wyjeździe z drużynami z niższej ligi
- ⭐ **Top zespoły** które są mocne niezależnie od miejsca gry
- 🎯 **Derby** gdzie goście mają przewagę psychologiczną

### 3. Typy bukmacherskie

Wykorzystaj do znajdowania "value bets":
- Bukmacherzy często przeceniają gospodarzy
- Goście z przewagą H2H mogą mieć lepsze kursy
- Połącz z analizą form dla jeszcze lepszych typów

## ⚖️ Porównanie trybów

| Aspekt | Domyślny (GOSPODARZE) | AWAY FOCUS (GOŚCIE) |
|--------|----------------------|---------------------|
| **Fokus** | Gospodarze ≥60% H2H | Goście ≥60% H2H |
| **Typowe scenariusze** | Mecze "pewne" dla gospodarzy | Nietypowe okazje dla gości |
| **Liczba meczów** | ~średnia | ~mniejsza (rzadziej) |
| **Potencjał value** | Standardowy | Wyższy (kursy dla gości) |
| **Sufiks pliku** | `_football.csv` | `_football_AWAY_FOCUS.csv` |

## 💡 Wskazówki

### ✅ Dobre praktyki

1. **Łącz z analizą formy** - goście w dobrej formie + przewaga H2H = mocny typ
2. **Sprawdzaj kontekst** - czy to derby? Czy liga jest jednolita?
3. **Kursy bukmacherskie** - użyj `--skip-no-odds` aby filtrować tylko mecze z kursami
4. **Weryfikuj wyniki** - użyj `verify_predictions.py` aby sprawdzić trafność

### ❌ Czego unikać

1. **Nie ignoruj kontekstu** - H2H to nie wszystko
2. **Nie typuj ślepo** - zawsze sprawdź aktualną formę i skład
3. **Nie przeceniaj historii** - drużyny się zmieniają

## 🔧 Zaawansowane

### Łączenie z innymi opcjami

```bash
# Tylko mecze z przewagą formy GOŚCI
python livesport_h2h_scraper.py \
  --mode auto \
  --date 2025-10-12 \
  --sports football \
  --away-team-focus \
  --headless

# Potem analizuj forme ręcznie w CSV
```

### Automatyzacja

Dodaj do Task Scheduler (Windows) lub cron (Linux):

```batch
REM daily_away_focus.bat
python livesport_h2h_scraper.py ^
  --mode auto ^
  --date %TODAY% ^
  --sports football basketball ^
  --away-team-focus ^
  --headless
```

## 🆘 Rozwiązywanie problemów

### Brak kwalifikujących się meczów

**Rozwiązanie:** To normalne! Goście z przewagą ≥60% H2H są rzadsze niż gospodarze.

```bash
# Spróbuj obniżyć próg (wymaga modyfikacji kodu)
# lub
# Zwiększ zakres sportów
python livesport_h2h_scraper.py \
  --mode auto \
  --date 2025-10-12 \
  --sports football basketball volleyball handball rugby hockey \
  --away-team-focus \
  --headless
```

### Plik nie ma sufiksu _AWAY_FOCUS

**Rozwiązanie:** Sprawdź czy użyłeś flagi `--away-team-focus`:

```bash
# ❌ BEZ flagi
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football --headless

# ✅ Z flagą
python livesport_h2h_scraper.py --mode auto --date 2025-10-12 --sports football --away-team-focus --headless
```

## 📚 Zobacz także

- [README.md](README.md) - Główna dokumentacja
- [FORM_ADVANTAGE_GUIDE.md](FORM_ADVANTAGE_GUIDE.md) - Przewaga formy
- [VERIFICATION_GUIDE.md](VERIFICATION_GUIDE.md) - Weryfikacja typów
- [EMAIL_SETUP.md](EMAIL_SETUP.md) - Powiadomienia email

## 🤝 Feedback

Masz pytania lub sugestie? Otwórz issue na GitHub!

---

**Wersja:** 6.4  
**Data aktualizacji:** 2025-10-12

