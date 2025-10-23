# Przykładowy Output - Livesport H2H Scraper

## Jak wygląda plik CSV?

Po uruchomieniu skryptu, w katalogu `outputs/` zostanie utworzony plik CSV, np:
- `livesport_h2h_2025-10-05.csv`
- `livesport_h2h_2025-10-05_football.csv`
- `livesport_h2h_2025-10-05_basketball.csv`

## Struktura pliku CSV

```csv
match_url,home_team,away_team,match_time,h2h_last5,home_wins_in_h2h_last5,qualifies
https://www.livesport.com/pl/pilka-nozna/.../legia-warszawa-cracovia/ABC123/,Legia Warszawa,Cracovia,"[{'home': 'Legia', 'away': 'Cracovia', 'score': '3-1', 'winner': 'home'}, {'home': 'Cracovia', 'away': 'Legia', 'score': '0-2', 'winner': 'away'}, ...]",4,True
https://www.livesport.com/pl/pilka-nozna/.../lech-poznan-gornik/DEF456/,Lech Poznań,Górnik Zabrze,"[...]",1,False
```

## Kolumny w pliku

| Kolumna | Typ | Opis | Przykład |
|---------|-----|------|----------|
| `match_url` | String | Pełny URL do meczu na Livesport | `https://www.livesport.com/...` |
| `home_team` | String | Nazwa drużyny gospodarzy | `Legia Warszawa` |
| `away_team` | String | Nazwa drużyny gości | `Cracovia` |
| `match_time` | String/Null | Czas meczu (jeśli dostępny) | `18:00` lub `null` |
| `h2h_last5` | String (JSON) | Lista ostatnich 5 H2H jako string | `[{'home': '...', 'score': '2-1', ...}]` |
| `home_wins_in_h2h_last5` | Integer | Liczba zwycięstw gospodarzy | `0`, `1`, `2`, `3`, `4`, `5` |
| `qualifies` | Boolean | Czy mecz spełnia kryterium (≥2 wygrane) | `True` lub `False` |

## Przykład 1: Mecz kwalifikujący się

```csv
match_url,home_team,away_team,home_wins_in_h2h_last5,qualifies
https://www.livesport.com/.../legia-cracovia/123,Legia Warszawa,Cracovia,4,True
```

**Interpretacja**: 
- Legia Warszawa (gospodarze) wygrała 4 z ostatnich 5 bezpośrednich spotkań z Cracovią
- ✅ Mecz **KWALIFIKUJE SIĘ** (≥2 wygrane)

## Przykład 2: Mecz NIE kwalifikujący się

```csv
match_url,home_team,away_team,home_wins_in_h2h_last5,qualifies
https://www.livesport.com/.../wisla-slask/456,Wisła Kraków,Śląsk Wrocław,1,False
```

**Interpretacja**:
- Wisła Kraków (gospodarze) wygrała tylko 1 z ostatnich 5 H2H ze Śląskiem
- ❌ Mecz **NIE kwalifikuje się** (<2 wygrane)

## Jak przetwarzać wyniki?

### W Excelu:
1. Otwórz plik CSV w Excel
2. Zastosuj filtr (Data → Filtr)
3. Filtruj kolumnę `qualifies` = `TRUE`
4. Zobaczysz tylko mecze spełniające kryterium!

### W Pythonie:
```python
import pandas as pd

# Wczytaj wyniki
df = pd.read_csv('outputs/livesport_h2h_2025-10-05_football.csv')

# Filtruj kwalifikujące się mecze
qualified = df[df['qualifies'] == True]

print(f"Znaleziono {len(qualified)} meczów kwalifikujących się")
print(qualified[['home_team', 'away_team', 'home_wins_in_h2h_last5']])
```

### W Google Sheets:
1. Wgraj plik CSV do Google Drive
2. Otwórz w Google Sheets
3. Użyj funkcji `=FILTER(A:G, G:G=TRUE)` aby zobaczyć tylko kwalifikujące się mecze

## Statystyki przykładowe

Dla 100 sprawdzonych meczów piłki nożnej:

```
📊 PODSUMOWANIE:
   Przetworzono meczów: 100
   Kwalifikujących się: 23 (23.0%)
   Zapisano do: outputs/livesport_h2h_2025-10-05_football.csv
```

**Typowy rozkład**:
- 0 wygranych gospodarzy: ~10%
- 1 wygrana gospodarzy: ~25%
- 2 wygrane gospodarzy: ~30% ✅ (kwalifikuje się)
- 3 wygrane gospodarzy: ~20% ✅
- 4 wygrane gospodarzy: ~10% ✅
- 5 wygranych gospodarzy: ~5% ✅

## Format h2h_last5 (szczegóły)

Kolumna `h2h_last5` zawiera string reprezentujący listę słowników Python:

```python
[
    {
        'home': 'Legia Warszawa',
        'away': 'Cracovia',
        'score': '3-1',
        'winner': 'home',
        'raw': 'Legia Warszawa 3:1 Cracovia | Ekstraklasa | 2024-09-15'
    },
    {
        'home': 'Cracovia',
        'away': 'Legia Warszawa',
        'score': '0-2',
        'winner': 'away',
        'raw': '...'
    },
    # ... do 5 meczów
]
```

**Uwaga**: W CSV jest to zapisane jako jeden długi string. Aby przetworzyć w Pythonie:

```python
import ast
import pandas as pd

df = pd.read_csv('outputs/livesport_h2h_2025-10-05.csv')

# Przekonwertuj string na listę
df['h2h_parsed'] = df['h2h_last5'].apply(lambda x: ast.literal_eval(x) if x else [])

# Teraz możesz pracować z listą słowników
for idx, row in df.iterrows():
    print(f"{row['home_team']} vs {row['away_team']}")
    for match in row['h2h_parsed']:
        print(f"  - {match['home']} {match['score']} {match['away']} (winner: {match['winner']})")
```

## Console Output (logi)

Podczas działania skryptu zobaczysz coś takiego:

```
============================================================
🏆 Livesport H2H Scraper - Multi-Sport Edition
============================================================
📅 Data: 2025-10-05
🎮 Tryb: auto
⚽ Sporty: football, basketball
============================================================

🔍 Zbieranie linków dla: football
   ✓ Znaleziono 45 meczów dla football

🔍 Zbieranie linków dla: basketball
   ✓ Znaleziono 18 meczów dla basketball

✅ Znaleziono 63 meczów do sprawdzenia

============================================================
🔄 Rozpoczynam przetwarzanie meczów...
============================================================

[1/63] 🔍 Przetwarzam: https://www.livesport.com/pl/pilka-nozna/polska/ekstraklasa/leg...
   ✅ KWALIFIKUJE SIĘ! (4/5 wygranych gospodarzy)
      Legia Warszawa vs Cracovia

[2/63] 🔍 Przetwarzam: https://www.livesport.com/pl/pilka-nozna/polska/ekstraklasa/lec...
   ❌ Nie kwalifikuje się (1/5)

...

============================================================
💾 Zapisywanie wyników...
============================================================

📊 PODSUMOWANIE:
   Przetworzono meczów: 63
   Kwalifikujących się: 15 (23.8%)
   Zapisano do: outputs/livesport_h2h_2025-10-05.csv

✨ Gotowe!
```

## Tips & Tricks

### Tip 1: Sortowanie po liczbie wygranych
```python
df = pd.read_csv('outputs/livesport_h2h_2025-10-05.csv')
df_sorted = df.sort_values('home_wins_in_h2h_last5', ascending=False)
# Najlepsze mecze (najwięcej wygranych gospodarzy) na górze
```

### Tip 2: Statystyki per sport
```python
# Jeśli masz wiele sportów w jednym pliku
df['sport'] = df['match_url'].apply(lambda x: 'football' if 'pilka-nozna' in x else 'basketball' if 'koszykowka' in x else 'other')
print(df.groupby('sport')['qualifies'].value_counts())
```

### Tip 3: Export tylko kwalifikujących się
```python
df = pd.read_csv('outputs/livesport_h2h_2025-10-05.csv')
qualified_only = df[df['qualifies'] == True]
qualified_only.to_csv('outputs/qualified_only.csv', index=False)
```

---

**Masz pytania?** Sprawdź `README.md` lub `QUICKSTART.md`!

