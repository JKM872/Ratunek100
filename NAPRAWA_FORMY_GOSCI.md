# 🔧 NAPRAWA: Forma Gości NA WYJEŹDZIE w Emailach

## Problem
W emailach nie wyświetlała się forma gości **na wyjeździe**, pomimo że dane były zbierane.

## Przyczyna
W funkcji `_extract_form_from_h2h_page()` była błędna logika przypisywania danych z różnych stron H2H:

### Jak działa Livesport:
- `/h2h/ogolem/` → pokazuje 2 sekcje: home (sekcja 0) + away (sekcja 1)
- `/h2h/u-siebie/` → pokazuje 1 sekcję: forma gospodarzy U SIEBIE (sekcja 0)
- `/h2h/na-wyjezdzie/` → pokazuje 1 sekcję: forma gości NA WYJEŹDZIE (sekcja 0)

### Stary kod (BŁĘDNY):
```python
for idx, section in enumerate(h2h_sections[:2]):
    # ... pobieranie danych ...
    
    # ZAWSZE przypisywał idx=0 do home, idx=1 do away
    if idx == 0:
        home_form = temp_form
    elif idx == 1:
        away_form = temp_form

# Problem: na stronie /h2h/na-wyjezdzie/ jest tylko 1 sekcja (idx=0),
# więc przypisywał do home_form zamiast away_form!
```

### Nowy kod (POPRAWNY):
```python
# Przypisanie zależy od KONTEKSTU (jaka strona H2H):
if context == 'overall':
    # Na /h2h/ogolem/ są 2 sekcje
    if idx == 0:
        home_form = temp_form
    elif idx == 1:
        away_form = temp_form
elif context == 'home':
    # Na /h2h/u-siebie/ jest 1 sekcja (gospodarze)
    if idx == 0:
        home_form = temp_form
elif context == 'away':
    # Na /h2h/na-wyjezdzie/ jest 1 sekcja (goście)
    if idx == 0:
        away_form = temp_form  # ← TERAZ POPRAWNE!
```

## Dodatkowe poprawki

### 1. Fallback logic
Stary kod używał fallback metody nawet gdy nowa metoda działała poprawnie (bo sprawdzał `if not home_form OR not away_form`).

Nowy kod:
```python
needs_fallback = False
if context == 'overall' and (not home_form or not away_form):
    needs_fallback = True
elif context == 'home' and not home_form:
    needs_fallback = True
elif context == 'away' and not away_form:
    needs_fallback = True
```

### 2. Debug logging
Dodano logging aby zobaczyć co się dzieje:
```python
if context == 'away' and away_form:
    print(f"      ✓ Forma gości NA WYJEŹDZIE: {away_form}")
```

## Jak przetestować

### Opcja 1: Szybki test
```bash
test_h2h_email_format.bat
```

### Opcja 2: Pełny test z emailem
```bash
run_volleyball_away_email.bat
```

W emailu powinieneś teraz zobaczyć:

```
✈️ Kepco:
  • Ogółem: ❌ ❌ ❌ ❌ ✅
  • Na wyjeździe: ❌ ❌ ❌ 🟡 ❌  ← TO POWINNO SIĘ POJAWIĆ!
```

## Pliki zmienione
- `livesport_h2h_scraper.py` - funkcja `_extract_form_from_h2h_page()` (linie 705-820)

## Wersja
v6.2 - 23.10.2025



