# 🚀 Plan Implementacji Tennis Scoring V3

## 📅 Data rozpoczęcia: 2025-10-07

---

## 🎯 **CEL:**

Rozbudować scraper aby zbierał wszystkie dane wymagane przez V3:
1. ✅ H2H z datami
2. ✅ Forma (10 meczów + rankingi przeciwników + wyniki setowe)
3. ✅ Forma NA konkretnej nawierzchni
4. ✅ Statystyki nawierzchni (win rate, doświadczenie)

---

## 📋 **KROK 1: Nowe funkcje pomocnicze** (30 min)

### 1.1. `extract_h2h_with_dates()` - H2H z datami i wynikami setowymi
```python
def extract_h2h_with_dates(soup, player_a, player_b) -> List[Dict]:
    """
    Zwraca:
    [
        {
            'date': '15.08.24',
            'winner': 'player_a' lub 'player_b',
            'score': '2-0',  # Wynik setowy
            'surface': 'hard'
        },
        ...
    ]
    """
```

**Źródło danych:** Strona H2H już zawiera daty w kolumnie

**Selektory:**
- Data: `div.h2h__row` → szukaj tekstu z datą (regex: `\d{2}\.\d{2}\.\d{2,4}`)
- Wynik: `div.h2h__result` → parsuj sety (np. "6-4, 7-5" → "2-0")
- Surface: z nazwy turnieju lub dedykowana strona `/h2h/clay/`, `/h2h/hard/`

---

### 1.2. `extract_player_detailed_form()` - Rozszerzona forma (10 meczów)
```python
def extract_player_detailed_form(driver, player_name, player_url=None) -> List[Dict]:
    """
    Zbiera ostatnie 10 meczów zawodnika.
    
    Zwraca:
    [
        {
            'result': 'W' lub 'L',
            'date': '01.10.25',
            'opponent': 'Novak Djokovic',
            'opponent_rank': 15,
            'score': '2-0',  # Wynik setowy
            'surface': 'hard'
        },
        ...
    ]
    """
```

**Źródło danych:**
1. **Strona gracza:** `/gracz/{player-id}/wyniki/`
   - Lista ostatnich meczów
   - Przeciwnicy
   - Wyniki

2. **Alternatywa:** Strona H2H + dedykowane requesty

**Jak znaleźć URL gracza:**
- Z linku na stronie meczu: `a.participant__participantName[href]`
- Format: `/gracz/djokovic-novak-AAA123BB/`

---

### 1.3. `extract_player_ranking_from_profile()` - Dokładny ranking
```python
def extract_player_ranking_from_profile(driver, player_url) -> Optional[int]:
    """
    Pobiera aktualny ranking ATP/WTA ze strony gracza.
    """
```

**Źródło:** Profil gracza → sekcja "Ranking"

---

### 1.4. `extract_surface_statistics()` - Statystyki na nawierzchniach
```python
def extract_surface_statistics(driver, player_url) -> Dict[str, Dict]:
    """
    Zbiera statystyki gracza na różnych nawierzchniach.
    
    Zwraca:
    {
        'clay': {
            'wins': 45,
            'total': 60,
            'win_rate': 0.75,
            'recent_form': ['W', 'W', 'L', 'W', 'W']  # Ostatnie 5 NA CLAY
        },
        'hard': {...},
        'grass': {...}
    }
    """
```

**Źródło:**
1. **Strona statystyk gracza:** `/gracz/{id}/statystyki/`
2. **Alternatywa:** Przeanalizuj H2H na każdej nawierzchni:
   - `/h2h/clay/` → policz mecze
   - `/h2h/hard/` → policz mecze
   - `/h2h/grass/` → policz mecze

---

## 📋 **KROK 2: Modyfikacja głównej funkcji** (15 min)

### 2.1. Zaktualizuj `process_match_tennis()`

```python
def process_match_tennis(url: str, driver: webdriver.Chrome) -> Dict:
    # ... istniejący kod ...
    
    # NOWE: Rozszerzone zbieranie danych
    
    # 1. H2H z datami (zamiast prostego H2H)
    h2h_matches = extract_h2h_with_dates(soup, player_a, player_b)
    out['h2h_matches'] = h2h_matches  # NOWE POLE
    
    # 2. Znajdź URLe graczy
    player_a_url = find_player_url(soup, player_a)
    player_b_url = find_player_url(soup, player_b)
    
    # 3. Rozszerzona forma (10 meczów + szczegóły)
    if player_a_url:
        out['form_a_detailed'] = extract_player_detailed_form(driver, player_a, player_a_url)
    
    if player_b_url:
        out['form_b_detailed'] = extract_player_detailed_form(driver, player_b, player_b_url)
    
    # 4. Statystyki nawierzchni
    if player_a_url:
        out['surface_stats_a'] = extract_surface_statistics(driver, player_a_url)
    
    if player_b_url:
        out['surface_stats_b'] = extract_surface_statistics(driver, player_b_url)
    
    # 5. Użyj V3 analyzer (zamiast V2)
    from tennis_advanced_v3 import TennisMatchAnalyzerV3
    
    analyzer = TennisMatchAnalyzerV3()
    
    analysis = analyzer.analyze_match(
        player_a=player_a,
        player_b=player_b,
        h2h_matches=out['h2h_matches'],         # ✅ Z datami
        form_a=out['form_a_detailed'],          # ✅ Rozszerzona
        form_b=out['form_b_detailed'],          # ✅ Rozszerzona
        surface=out['surface'],
        surface_stats_a=out['surface_stats_a'], # ✅ Pełne statystyki
        surface_stats_b=out['surface_stats_b']  # ✅ Pełne statystyki
    )
    
    # ... reszta kodu ...
```

---

## 📋 **KROK 3: Optymalizacja wydajności** (20 min)

### Problem: Dodatkowe requesty spowalniają scraping

**Rozwiązanie 1: Cache**
```python
# Cache URLi graczy (aby nie szukać za każdym razem)
player_url_cache = {}

def get_player_url_cached(soup, player_name):
    if player_name in player_url_cache:
        return player_url_cache[player_name]
    
    url = find_player_url(soup, player_name)
    player_url_cache[player_name] = url
    return url
```

**Rozwiązanie 2: Równoległe pobieranie**
```python
from concurrent.futures import ThreadPoolExecutor

def fetch_player_data_parallel(driver, player_a_url, player_b_url):
    """Pobiera dane obu graczy równocześnie"""
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(extract_player_detailed_form, driver, player_a_url)
        future_b = executor.submit(extract_player_detailed_form, driver, player_b_url)
        
        return future_a.result(), future_b.result()
```

**Rozwiązanie 3: Tryb "fast" (bez dodatkowych danych)**
```python
# Argument: --tennis-mode fast (V2) lub --tennis-mode full (V3)
if args.tennis_mode == 'full':
    # Zbierz wszystkie dane dla V3
    out['form_a_detailed'] = extract_player_detailed_form(...)
else:
    # Tylko podstawowe dane dla V2
    out['form_a'] = extract_player_form_simple(...)
```

---

## 📋 **KROK 4: Testy** (30 min)

### 4.1. Test jednostkowy - pojedyncze funkcje
```python
# test_scraper_v3.py

def test_extract_h2h_with_dates():
    # Test czy poprawnie parsuje daty i wyniki
    pass

def test_extract_player_detailed_form():
    # Test czy zbiera 10 meczów z detalami
    pass
```

### 4.2. Test integracyjny - pełny mecz
```bash
python livesport_h2h_scraper.py \
  --mode urls \
  --input test_tennis_urls.txt \
  --tennis-mode full \
  --headless
```

### 4.3. Test wydajności
```python
# Zmierz czas:
# - V2 (bez dodatkowych danych): ~3-5 sek/mecz
# - V3 (z pełnymi danymi): ~10-15 sek/mecz
# - V3 z cache: ~7-10 sek/mecz
```

---

## 📋 **KROK 5: Dokumentacja** (15 min)

### 5.1. Aktualizuj README
```markdown
## Tennis Scoring V3

### Nowe funkcje:
- Zbiera ostatnie 10 meczów (było: 5)
- Rankingi przeciwników w formie
- Wyniki setowe (2-0, 2-1)
- Statystyki na nawierzchniach
- Dokładność: 75-85% (vs V2: 61%)

### Użycie:
```bash
# V3 (pełne dane, wolniejsze)
python livesport_h2h_scraper.py --tennis-mode full

# V2 (szybsze, mniej dokładne)
python livesport_h2h_scraper.py --tennis-mode fast
```

---

## 📊 **HARMONOGRAM:**

| Krok | Czas | Status |
|------|------|--------|
| 1. Nowe funkcje | 30 min | ⏳ Pending |
| 2. Modyfikacja głównej funkcji | 15 min | ⏳ Pending |
| 3. Optymalizacja | 20 min | ⏳ Pending |
| 4. Testy | 30 min | ⏳ Pending |
| 5. Dokumentacja | 15 min | ⏳ Pending |
| **RAZEM** | **~2 godziny** | |

---

## ⚠️ **POTENCJALNE PROBLEMY:**

### 1. **Livesport może zablokować częste requesty**
**Rozwiązanie:** 
- Dodaj opóźnienia między requestami (sleep 2-3 sek)
- Użyj rotujących proxy (opcjonalnie)
- Cache danych graczy

### 2. **Selektory mogą się zmienić**
**Rozwiązanie:**
- Użyj wielu metod fallback
- Loguj błędy parsowania
- Graceful degradation (jeśli brak danych → użyj V2)

### 3. **Wolne pobieranie**
**Rozwiązanie:**
- Cache URLi graczy
- Równoległe requesty (ThreadPool)
- Tryb "fast" vs "full"

---

## ✅ **KRYTERIA SUKCESU:**

1. ✅ Scraper zbiera wszystkie dane wymagane przez V3
2. ✅ Czas scrapingu: <15 sek/mecz
3. ✅ V3 kwalifikuje 20-30% meczów (vs obecne 7%)
4. ✅ V3 dokładność: >75% (vs V2: 61%)
5. ✅ Zero błędów parsowania na testowych meczach

---

## 🚀 **START IMPLEMENTACJI:**

Gotowy do rozpoczęcia? Zacznę od **KROKU 1** - nowe funkcje pomocnicze.

---

**Data utworzenia:** 2025-10-07  
**Szacowany czas:** 2 godziny  
**Priorytet:** 🔥 WYSOKI  
**Status:** ⏳ OCZEKUJE NA POTWIERDZENIE


















