# 🔧 Naprawa Kursów i Maili - Dodatkowa Poprawka

**Data:** 26 października 2025  
**Kontekst:** Użytkownik testował naprawy z GitHub Actions i znalazł dodatkowe problemy

---

## 🐛 Nowe Problemy Odkryte

### 1. **Kursy Nadal Nie Pobierają Się** ❌
- Pokazują "nan" w mailach
- Timeout 2s był za krótki dla GitHub Actions

### 2. **Tylko 1 Mail Zamiast 2** ❌
- Brakuje maila z przewagą formy
- Dostał tylko mail ze wszystkimi kwalifikującymi

---

## ✅ Dodatkowe Naprawy

### Naprawa 1: Zwiększony Timeout dla Kursów (GitHub Actions)

**Problem:**
- Kursy ładują się przez JavaScript dynamicznie
- GitHub Actions działa wolniej niż lokalnie
- Timeout 2s to za mało

**Rozwiązanie:**
```python
# PRZED (livesport_h2h_scraper.py linia 1026):
odds_container = WebDriverWait(driver, 2).until(...)  # Za krótko!

# PO (linie 1025-1037):
is_github = os.environ.get('GITHUB_ACTIONS') == 'true'
odds_timeout = 5 if is_github else 2  # GitHub: 5s, Lokalnie: 2s

odds_container = WebDriverWait(driver, odds_timeout).until(...)

# GitHub Actions: dłuższe opóźnienie dla pełnego załadowania
sleep_time = 0.8 if is_github else 0.3
time.sleep(sleep_time)
```

**Efekt:**
- GitHub Actions: **5 sekund** na załadowanie kursów (+ 0.8s sleep)
- Lokalnie: **2 sekundy** (+ 0.3s sleep) - bez spowolnienia dla ciebie

---

### Naprawa 2: Poprawione Wyświetlanie "nan" w HTML

**Problem:**
```python
# email_notifier.py linia 265 (PRZED):
if home_odds and away_odds:
    # To PRZEPUSZCZA pandas NaN!
    # W Pythonie: bool(NaN) = True (!)
    odds_html = f'{home_odds:.2f}'  # Daje "nan"
```

**Dlaczego to nie działało:**
- pandas konwertuje `None` → `NaN`
- Python: `bool(NaN)` = `True` (truthy!)
- Więc `if home_odds and away_odds:` przepuszczał NaN
- Formatowanie `{NaN:.2f}` daje string "nan"

**Rozwiązanie:**
```python
# PO (linie 266-285):
has_valid_odds = False
try:
    if home_odds is not None and away_odds is not None:
        # Sprawdź czy to LICZBY (nie NaN)
        if not (pd.isna(home_odds) or pd.isna(away_odds)):
            # Dodatkowo: zakres 1.0-100.0
            if 1.0 <= float(home_odds) <= 100.0 and 1.0 <= float(away_odds) <= 100.0:
                has_valid_odds = True
except (ValueError, TypeError):
    pass

if has_valid_odds:
    # Pokaż kursy
```

**Efekt:**
- Mecze bez kursów: **nie pokazują sekcji kursów w ogóle**
- Mecze z NaN: **nie pokazują "nan"**
- Tylko mecze z PRAWDZIWYMI kursami pokażą sekcję 🎲

---

## 📧 Co Się Stało z Mailami

### Przed Naprawą:
1. **Mail 1** (przewaga formy + skip-no-odds):
   - Wszystkie mecze handball nie miały kursów (timeout za krótki)
   - Filtr `--skip-no-odds` usunął wszystkie mecze
   - **0 meczów → mail nie wysłany** ✅ (to prawidłowe zachowanie)

2. **Mail 2** (wszystkie + skip-no-odds):
   - Te same mecze, nadal bez kursów
   - Ale NaN przechodził przez sprawdzanie w HTML
   - **Mail wysłany z "nan"** ❌ (bug)

### Po Naprawie:
1. **Mail 1** (przewaga formy + skip-no-odds):
   - Timeout 5s → więcej meczów będzie miało kursy
   - Jeśli jakieś mecze mają przewagę formy + kursy → **wysłany**
   - Jeśli żaden mecz nie spełnia kryteriów → **nie wysłany** (OK!)

2. **Mail 2** (wszystkie + skip-no-odds):
   - Timeout 5s → więcej meczów będzie miało kursy
   - Właściwe sprawdzanie NaN → nie pokazuje "nan"
   - **Wysłany tylko z meczami z PRAWDZIWYMI kursami**

---

## 🧪 Jak Przetestować

### Test 1: Sprawdź Logi GitHub Actions

Szukaj w logach:
```bash
💰 DEBUG: Znaleziono kontener kursów (timeout: 5s)
# LUB
⚠️ DEBUG: Timeout przy ładowaniu kursów (po 5s)
```

Jeśli widzisz pierwszy komunikat → kursy są pobierane! ✅

### Test 2: Sprawdź Email HTML

**✅ SUKCES - Mecz Z kursami:**
```html
🎲 Kursy: Team A 1.85 | Team B 2.10
```

**✅ SUKCES - Mecz BEZ kursów:**
```html
(brak sekcji z kursami - po prostu jej nie ma)
```

**❌ BŁĄD (jeśli nadal widzisz):**
```html
🎲 Kursy: Team A nan | Team B nan
```

### Test 3: Sprawdź Ile Maili Przyszło

**Scenariusz A:** 2 maile
- Mail 1: "🔥 PRZEWAGA FORMY + 💰 Z KURSAMI"
- Mail 2: "💰 Z KURSAMI"
- **Status:** ✅ DZIAŁA!

**Scenariusz B:** 1 mail
- Mail 2: "💰 Z KURSAMI"
- **Przyczyna:** Brak meczów z przewagą formy (albo wszystkie bez kursów)
- **Status:** ✅ OK (prawidłowe zachowanie jeśli faktycznie nie ma)

**Scenariusz C:** 0 maili
- **Przyczyna:** Wszystkie mecze bez kursów
- **Status:** ✅ OK (z flagą `--skip-no-odds` to prawidłowe)

---

## 🔍 Debug: Włącz VERBOSE

Jeśli nadal są problemy, włącz debug mode:

```python
# Plik: livesport_h2h_scraper.py, linia 65
VERBOSE = True  # Zmień z False na True
```

Commit, push i uruchom ponownie. W logach zobaczysz:
```
🔍 DEBUG Tennis Analysis:
   H2H matches: X
   Form A: Y, Form B: Z
   ...
💰 DEBUG: Znaleziono kontener kursów (timeout: 5s)
⚠️ DEBUG: Timeout przy ładowaniu kursów (po 5s)
```

---

## 📊 Podsumowanie Zmian

| Plik | Linie | Zmiana |
|------|-------|--------|
| `livesport_h2h_scraper.py` | 1025-1046 | Timeout kursów: 2s → 5s (GitHub) |
| `email_notifier.py` | 266-285 | Właściwe sprawdzanie NaN |
| `email_notifier.py` | 11 | Import `math` |

---

## 🎯 Oczekiwany Rezultat

Po tych naprawach:
1. ✅ **Więcej meczów będzie miało kursy** (dłuższy timeout)
2. ✅ **"nan" nie pojawi się w mailach** (właściwe sprawdzanie)
3. ✅ **Mecze bez kursów nie będą w mailach** (filtr działa)
4. ✅ **2 maile jeśli są mecze z przewagą formy**
5. ✅ **1 mail jeśli są tylko mecze bez przewagi formy**
6. ✅ **0 maili jeśli wszystkie mecze bez kursów** (z `--skip-no-odds`)

---

## 🚀 Commit & Push

```bash
git add .
git commit -m "Fix: Zwiększony timeout dla kursów (GitHub Actions) + poprawione wyświetlanie NaN w HTML"
git push origin main
```

Następnie uruchom ponownie GitHub Actions i sprawdź wyniki!

---

**Status:** ✅ Gotowe do testowania  
**Data:** 26 października 2025, 23:45

