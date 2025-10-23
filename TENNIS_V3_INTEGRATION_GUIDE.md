# 🔌 Przewodnik Integracji Tennis V3 Enhanced

## 📋 **JAK PRZEŁĄCZYĆ Z V2 NA V3 ENHANCED**

---

## ⚠️ **PRZED ROZPOCZĘCIEM:**

1. **Backup**: Skopiuj aktualny `livesport_h2h_scraper.py`
2. **Test**: Najpierw przetestuj na małym zbiorze danych
3. **Porównanie**: Uruchom oba systemy równolegle przez kilka dni

---

## 🔧 **KROK 1: Zmiana importu w livesport_h2h_scraper.py**

### BYŁO (V2):
```python
from tennis_advanced import TennisMatchAnalyzer

analyzer = TennisMatchAnalyzer()
```

### BĘDZIE (V3 Enhanced):
```python
from tennis_advanced_v3 import TennisMatchAnalyzerV3

analyzer = TennisMatchAnalyzerV3()
```

---

## 🔧 **KROK 2: Aktualizacja wywołania analyze_match()**

### Minimalna zmiana (backwards compatible):

Jeśli Twój scraper już zbiera wszystkie potrzebne dane, po prostu zmień import. System V3 Enhanced jest kompatybilny wstecz:

```python
# Stare wywołanie NADAL DZIAŁA:
analysis = analyzer.analyze_match(
    player_a=home_name,
    player_b=away_name,
    h2h_matches=h2h_data,
    form_a=form_a,
    form_b=form_b,
    surface=surface,
    surface_stats_a=stats_a,
    surface_stats_b=stats_b
)
```

### Rozszerzona zmiana (wykorzystuje nowe funkcje):

```python
# Nowe wywołanie z dodatkowymi parametrami:
analysis = analyzer.analyze_match(
    player_a=home_name,
    player_b=away_name,
    h2h_matches=h2h_data,
    form_a=form_a,
    form_b=form_b,
    surface=surface,
    surface_stats_a=stats_a,
    surface_stats_b=stats_b,
    tournament_info=match_url,  # ← NOWE! (opcjonalne)
    debug=False                 # ← NOWE! (opcjonalne)
)
```

---

## 🔧 **KROK 3: Aktualizacja zbierania danych (opcjonalne, ale zalecane)**

### A) Dodaj pole 'surface' do formy:

**BYŁO:**
```python
form_a = [
    {'result': 'W', 'date': '01.10.25', 'opponent_rank': 15, 'score': '2-0'},
    ...
]
```

**BĘDZIE:**
```python
form_a = [
    {'result': 'W', 'date': '01.10.25', 'opponent_rank': 15, 'score': '2-0', 'surface': 'hard'},
    ...
]
```

**Jak dodać?** - Jeśli scraper już wie jaka jest nawierzchnia, dodaj to pole podczas zbierania formy.

### B) Przekaż URL meczu jako tournament_info:

```python
# W funkcji process_match():
analysis = analyzer.analyze_match(
    ...,
    tournament_info=url  # System automatycznie wykryje typ turnieju z URL
)
```

---

## 🔧 **KROK 4: Aktualizacja zapisu wyników (opcjonalne)**

### Zapisz nowe pola do CSV/JSON:

```python
# Dodaj nowe kolumny do CSV:
match_data = {
    'home_team': player_a,
    'away_team': player_b,
    'qualifies': analysis['qualifies'],
    'total_score': analysis['total_score'],
    'confidence': analysis['confidence'],
    
    # NOWE POLA:
    'win_probability': analysis['details']['win_probability'],
    'win_probability_pct': analysis['details']['win_probability_pct'],
    'tournament_tier': analysis['details'].get('tournament_tier', 'unknown'),
    'threshold_used': analysis['details'].get('threshold_used', 45),
}
```

---

## 📝 **PRZYKŁAD PEŁNEJ INTEGRACJI:**

```python
# livesport_h2h_scraper.py

from tennis_advanced_v3 import TennisMatchAnalyzerV3  # ← ZMIANA

def process_match_tennis(url: str, driver) -> Dict:
    """Przetwarza mecz tenisowy"""
    
    # ... zbieranie danych (bez zmian) ...
    
    # Analiza V3 Enhanced
    analyzer = TennisMatchAnalyzerV3()
    
    # Podstawowe wywołanie (backwards compatible)
    analysis = analyzer.analyze_match(
        player_a=home_name,
        player_b=away_name,
        h2h_matches=h2h_data,
        form_a=form_a,
        form_b=form_b,
        surface=surface,
        surface_stats_a=stats_a,
        surface_stats_b=stats_b,
        tournament_info=url,  # ← NOWE (opcjonalne)
        debug=False           # ← NOWE (opcjonalne)
    )
    
    # Przygotuj wynik
    result = {
        'home_team': home_name,
        'away_team': away_name,
        'match_time': match_time,
        'qualifies': analysis['qualifies'],
        'total_score': analysis['total_score'],
        'confidence': analysis['confidence'],
        
        # NOWE POLA (opcjonalne):
        'win_probability_pct': analysis['details'].get('win_probability_pct', 'N/A'),
        'tournament_tier': analysis['details'].get('tournament_tier', 'unknown'),
        'threshold_used': analysis['details'].get('threshold_used', 45),
        
        # Stare pola (bez zmian):
        'h2h_score': analysis['breakdown']['h2h_score'],
        'form_score': analysis['breakdown']['current_form_score'],
        'surface_score': analysis['breakdown']['surface_form_score'],
        'momentum_score': analysis['breakdown']['momentum_score'],
    }
    
    return result
```

---

## 🧪 **KROK 5: Testowanie**

### Test 1: Porównanie V2 vs V3 Enhanced

```python
# Uruchom oba systemy na tych samych danych
from tennis_advanced import TennisMatchAnalyzer  # V2
from tennis_advanced_v3 import TennisMatchAnalyzerV3  # V3

analyzer_v2 = TennisMatchAnalyzer()
analyzer_v3 = TennisMatchAnalyzerV3()

# Test na tych samych danych
analysis_v2 = analyzer_v2.analyze_match(...)
analysis_v3 = analyzer_v3.analyze_match(...)

print(f"V2: {analysis_v2['total_score']:.1f} - Qualifies: {analysis_v2['qualifies']}")
print(f"V3: {analysis_v3['total_score']:.1f} - Qualifies: {analysis_v3['qualifies']}")
print(f"V3 Probability: {analysis_v3['details']['win_probability_pct']}")
```

### Test 2: Quick test na przykładowych danych

```bash
# Uruchom przykład z tennis_advanced_v3.py
python tennis_advanced_v3.py
```

### Test 3: Test na prawdziwych danych

```bash
# Uruchom scraper na małym zbiorze (5-10 meczów)
python livesport_h2h_scraper.py --date today --sports tennis --limit 10
```

---

## 📊 **KROK 6: Monitorowanie wyników**

### Porównaj metryki:

| Metryka | V2 | V3 Enhanced | Zmiana |
|---------|----|-----------|----|
| Kwalifikowane mecze | X | Y | +Z% |
| Średni score | X | Y | +Z |
| Dokładność predykcji | 61.5% | ? | Mierz! |

### Śledź przez tydzień:

```python
# Zapisuj wyniki do logu
{
    'date': '2025-10-08',
    'version': 'v3_enhanced',
    'matches_analyzed': 50,
    'qualified': 12,
    'qualification_rate': 0.24,
    'avg_score': 52.3,
    'avg_probability': 0.78
}
```

---

## ⚙️ **KROK 7: Fine-tuning (opcjonalne)**

### Jeśli zbyt dużo/mało kwalifikowanych:

```python
# Dostosuj konfigurację
custom_config = SCORING_CONFIG.copy()
custom_config['threshold'] = 42.0  # Obniż próg bazowy
custom_config['adaptive_threshold'] = True  # Włącz/wyłącz adaptację

analyzer = TennisMatchAnalyzerV3(config=custom_config)
```

### Jeśli chcesz zmienić wagi turniejowe:

```python
# W tennis_advanced_v3.py
TOURNAMENT_WEIGHTS = {
    'grand_slam': 1.6,    # Zwiększ z 1.5
    'masters_1000': 1.4,  # Zwiększ z 1.3
    'atp_500': 1.2,       # Zwiększ z 1.1
    'atp_250': 1.0,
}
```

---

## 🚨 **TROUBLESHOOTING:**

### Problem 1: "Zbyt wiele kwalifikowanych meczów"

**Rozwiązanie:**
- Zwiększ `threshold` z 45 na 48-50
- Wyłącz `adaptive_threshold`
- Zmniejsz wagi turniejowe

### Problem 2: "Zbyt mało kwalifikowanych meczów"

**Rozwiązanie:**
- Obniż `threshold` z 45 na 42-43
- Włącz `adaptive_threshold` (jeśli wyłączony)
- Sprawdź czy dane wejściowe są kompletne

### Problem 3: "TypeError: missing argument"

**Rozwiązanie:**
- Nowe parametry są opcjonalne!
- Stare wywołania powinny działać bez zmian
- Sprawdź czy importujesz `TennisMatchAnalyzerV3` (nie `TennisMatchAnalyzer`)

### Problem 4: "Scoring wygląda dziwnie"

**Rozwiązanie:**
- Włącz `debug=True` w analyze_match()
- Sprawdź breakdown - które komponenty dają najwięcej punktów
- Zweryfikuj dane wejściowe (szczególnie daty)

---

## 📋 **CHECKLIST INTEGRACJI:**

- [ ] Backup obecnego kodu
- [ ] Import zmieniony na `TennisMatchAnalyzerV3`
- [ ] Test na przykładowych danych (uruchom `python tennis_advanced_v3.py`)
- [ ] Test na prawdziwych danych (5-10 meczów)
- [ ] Porównanie V2 vs V3 (co najmniej 20 meczów)
- [ ] Aktualizacja zapisu wyników (nowe pola)
- [ ] Dodanie `tournament_info` (opcjonalne)
- [ ] Dodanie `surface` do formy (opcjonalne)
- [ ] Monitorowanie przez tydzień
- [ ] Fine-tuning progów (jeśli potrzebne)
- [ ] Dokumentacja zaktualizowana

---

## 🎯 **ZALECENIA:**

### 1. **Stopniowa migracja:**
```python
# Dzień 1-3: Test równoległy (oba systemy)
# Dzień 4-7: V3 Enhanced jako główny, V2 jako backup
# Dzień 8+: Tylko V3 Enhanced
```

### 2. **Zbieraj metryki:**
```python
# Zapisuj wszystkie wyniki do logu
# Porównuj accuracy po tygodniu
# Dostosuj progi jeśli potrzeba
```

### 3. **Wykorzystaj nowe funkcje:**
```python
# Prawdopodobieństwo w emailach:
"Alcaraz vs Rune - 86.7% pewności (Grand Slam)"

# Filtruj po pewności:
if analysis['details']['win_probability'] > 0.80:
    send_email(...)
```

---

## 📧 **WSPARCIE:**

Jeśli napotkasz problemy:
1. Sprawdź `debug=True` output
2. Przeczytaj `TENNIS_V3_ENHANCED.md`
3. Sprawdź przykład w `tennis_advanced_v3.py`

---

**Powodzenia z integracją! 🚀**

---

**Data:** 2025-10-08  
**Wersja:** V3 Enhanced Integration Guide v1.0  
**Status:** ✅ Gotowe do użycia


