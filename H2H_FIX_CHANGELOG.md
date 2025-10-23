# 🔧 CHANGELOG - Naprawa Scrapingu H2H

**Data:** 23 października 2025
**Problem:** Komunikat "⚠️ Brak H2H" dla wszystkich meczów siatkówki

---

## 🐛 Zidentyfikowane Problemy

### 1. **Błąd w parsowaniu wyniku (CRITICAL)**
**Plik:** `livesport_h2h_scraper.py`, linia 220 (poprzednia wersja)

**Problem:**
```python
else:
    score = ''
    winner = 'unknown'  # ❌ To nadpisywało poprawnie obliczoną wartość!
```

Zmienna `winner` była ustawiana na `'unknown'` nawet gdy została prawidłowo obliczona w liniach 207-217. To powodowało że wszystkie wyniki H2H były traktowane jako nierozstrzygnięte.

**Naprawa:**
- Usunięto nadpisywanie zmiennej `winner` poza blokiem `if`
- Dodano drugie sprawdzanie wyniku (fallback) gdy pierwsza metoda nie działa

---

### 2. **Brak alternatywnych selektorów CSS**
**Problem:**
Livesport używa różnych selektorów CSS dla różnych sportów:
- Piłka nożna: `a.h2h__row`
- Siatkówka: może używać `div.h2h__row` lub innych wariantów

**Naprawa:**
Dodano kaskadowe sprawdzanie różnych selektorów:
```python
# Główna metoda
match_rows = pojedynki_section.select('a.h2h__row')

# FALLBACK 1
if not match_rows:
    match_rows = pojedynki_section.select('div.h2h__row')

# FALLBACK 2
if not match_rows:
    match_rows = pojedynki_section.select('[class*="h2h__row"]')
```

---

### 3. **Za krótki czas oczekiwania na załadowanie**
**Problem:**
Strony siatkówki ładują się wolniej niż piłki nożnej.
Poprzedni czas: `2.0s`

**Naprawa:**
- Zwiększono czas oczekiwania do `3.5s` dla lepszej kompatybilności
- Dodano scrollowanie strony aby załadować lazy-loaded content:
```python
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(0.5)
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(0.5)
```
- Dodano dodatkowy `1.0s` sleep po załadowaniu dla renderowania JS

---

### 4. **Brak funkcji debugowania**
**Problem:**
Gdy scraping nie działał, nie było sposobu aby zobaczyć co jest na stronie.

**Naprawa:**
Dodano funkcję diagnostyczną która zapisuje HTML do pliku gdy nie znajdzie sekcji H2H:
```python
if not h2h_sections and debug_url:
    debug_file = 'outputs/debug_no_h2h.html'
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
```

---

## ✅ Wprowadzone Zmiany

### Plik: `livesport_h2h_scraper.py`

1. **Funkcja `parse_h2h_from_soup`** (linie 157-281):
   - ✅ Naprawiono bug z nadpisywaniem `winner`
   - ✅ Dodano alternatywne selektory CSS (fallback)
   - ✅ Dodano drugą metodę parsowania wyniku (regex na `result_text`)
   - ✅ Dodano funkcję debugowania (zapisywanie HTML)
   - ✅ Dodano parametr `debug_url` dla lepszego logowania

2. **Funkcja `process_match`** (linie 284-509):
   - ✅ Zwiększono czas oczekiwania z 2.0s do 3.5s
   - ✅ Dodano scrollowanie strony (lazy-loading)
   - ✅ Dodano dodatkowy 1.0s sleep dla renderowania JS
   - ✅ Zaktualizowano wywołanie `parse_h2h_from_soup` z parametrem `debug_url`

3. **Funkcja `process_match_tennis`** (linia 1394):
   - ✅ Zaktualizowano wywołanie `parse_h2h_from_soup` z parametrem `debug_url`

---

## 🧪 Jak Przetestować Naprawki

### Opcja 1: Użyj skryptu testowego
```bash
python test_h2h_fix.py
```
lub
```bash
test_h2h_volleyball.bat
```

Skrypt poprosi Cię o URL meczu i wyświetli:
- Nazwy drużyn
- Liczbę znalezionych meczów H2H
- Szczegóły ostatnich 5 meczów H2H
- Czy mecz kwalifikuje się (≥60% H2H)

### Opcja 2: Uruchom normalny scraping
```bash
python scrape_and_notify.py --date 2025-10-06 --sports volleyball \
  --to twoj@email.com --from-email twoj@email.com --password "haslo" \
  --headless --skip-no-odds --only-form-advantage --sort time
```

---

## 📊 Oczekiwane Rezultaty

**PRZED naprawą:**
```
[1/30] Przetwarzam...
   ⚠️  Brak H2H
[2/30] Przetwarzam...
   ⚠️  Brak H2H
...
```

**PO naprawie:**
```
[1/30] Przetwarzam...
   ✅ KWALIFIKUJE! Team A vs Team B
      H2H: 4/5 (80%)
      Ostatnie H2H:
        1. 15.10.2025  Team A 3-1 Team B
        2. 10.10.2025  Team A 3-0 Team B
        ...
[2/30] Przetwarzam...
   ❌ Nie kwalifikuje (1/5 = 20%)
...
```

---

## 🔍 Diagnostyka w Przypadku Problemów

Jeśli nadal widzisz "⚠️ Brak H2H":

1. **Sprawdź plik debug:**
   ```
   outputs/debug_no_h2h.html
   ```
   Znajdziesz tam HTML strony - sprawdź czy jest tam sekcja H2H.

2. **Uruchom bez headless:**
   ```bash
   python scrape_and_notify.py ... (usuń --headless)
   ```
   Zobaczysz co przeglądarka faktycznie ładuje.

3. **Zwiększ jeszcze bardziej czas oczekiwania:**
   W pliku `livesport_h2h_scraper.py`, linia 322:
   ```python
   time.sleep(3.5)  # Zmień na np. 5.0 lub 7.0
   ```

4. **Sprawdź URL:**
   Upewnij się że URL prowadzi do strony z H2H:
   ```
   https://www.livesport.com/pl/mecz/.../h2h/ogolem/
   ```

---

## 📝 Dodatkowe Uwagi

- Naprawki **NIE** zmieniają logiki programu ani formatu outputu
- Wszystkie mechanizmy (forma, kursy, away_team_focus) działają tak samo
- Zmieniono tylko sposób **pobierania** danych H2H, nie ich **przetwarzania**
- Kompatybilne ze wszystkimi sportami (football, basketball, volleyball, etc.)

---

## 🎯 Co Dalej?

Po przetestowaniu i potwierdzeniu że naprawki działają:

1. **Uruchom pełny scraping:**
   ```bash
   daily_scraper_all_sports.bat
   ```

2. **Sprawdź wyniki:**
   ```
   outputs/livesport_h2h_YYYY-MM-DD_volleyball.csv
   ```

3. **Monitoruj logi:**
   - Czy komunikat "Brak H2H" zniknął?
   - Ile meczów się kwalifikuje?
   - Czy dane H2H są poprawne?

---

**Autor naprawy:** AI Assistant
**Status:** ✅ Gotowe do testowania

