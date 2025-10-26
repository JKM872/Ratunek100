# 🎯 PROBLEM: Scraper nie znajduje kursów dla GOŚCI

## 📋 Diagnoza użytkownika:

> "Wydaje mi się że to bardziej problem ze scrappingiem gości gospodarzy sobrze znajduje i jestem z tego zadowolony"

**To ma sens!** Problem nie polega na duplikacji, ale na tym że:
- ✅ Scraper **DOBRZE znajduje kurs gospodarzy**
- ❌ Scraper **NIE ZNAJDUJE kursu gości** (lub znajduje go źle)
- ❌ W rezultacie używa tego samego kursu dla obu → identyczne wartości

---

## 🔍 Przykład problemu:

### W emailu widzisz:
```
🎲 Kursy: Ziraat Bankasi 1.23 | Fenerbahce 1.23
```

### Co się naprawdę dzieje w scraperze:

1. Scraper wchodzi na stronę `/h2h/` meczu
2. Znajduje kurs gospodarzy: `1.23` ✓
3. Próbuje znaleźć kurs gości: **NIE ZNAJDUJE** ✗
4. Używa tego samego kursu ponownie: `1.23` (błąd!)

### Prawdziwe kursy powinny być np.:
```
🎲 Kursy: Ziraat Bankasi 1.23 | Fenerbahce 4.50
```

---

## 🔧 CO ZOSTAŁO NAPRAWIONE

### 1. **Dedykowane wyszukiwanie dla home i away**

Kod teraz próbuje **3 różne metody** w kolejności:

#### Metoda 1: Dedykowane elementy (NOWA)
```python
# Szukaj elementów z 'home' w klasie
home_elements = driver.find_elements(..., "contains(@class, 'home')")

# Szukaj elementów z 'away' w klasie
away_elements = driver.find_elements(..., "contains(@class, 'away')")
```

To powinno znaleźć kursy **osobno** dla każdej drużyny.

#### Metoda 2: Inteligentne rozpoznanie (NOWA)
```python
# Zbierz wszystkie kursy Z KONTEKSTEM (klasy HTML)
for elem in odds_elements:
    odds_with_context.append((kurs, klasy_HTML))

# Rozpoznaj który kurs jest dla kogo:
if 'home' in klasy:
    home_candidates.append(kurs)
elif 'away' in klasy:
    away_candidates.append(kurs)
```

#### Metoda 3: Pozycyjna (fallback)
```python
# Jeśli powyższe nie zadziałały - użyj pozycji:
home_odds = unique_odds[0]  # Pierwszy
away_odds = unique_odds[1]  # Drugi (lub ostatni)
```

### 2. **Maksymalne debugowanie**

Zobaczysz w logach **dokładnie** co scraper znajduje:

```
🏠 DEBUG: Znaleziono kurs gospodarzy: 1.23
✈️  DEBUG: Znaleziono kurs gości: 4.50
💰 Znaleziono kursy (dedykowana metoda): 1.23 - 4.50
```

Lub jeśli problem:

```
🏠 DEBUG: Znaleziono kurs gospodarzy: 1.23
✈️  DEBUG: Nie znaleziono kursu gości
⚠️  Znaleziono tylko 1 kurs: 1.23 - brak kursu dla gości!
```

---

## 🧪 JAK PRZETESTOWAĆ

### Test 1: Prosty test z prawdziwym meczem

```bash
python test_away_odds_debug.py "https://www.livesport.com/pl/koszykowka/turcja/tbsl/ziraat-bankasi-fenerbahce/xxx/"
```

**Zamień URL** na prawdziwy mecz który miał problem (np. Ziraat Bankasi vs Fenerbahce).

**Co zobaczysz:**
- Przeglądarka otworzy się (widoczna)
- Scraper załaduje stronę
- **DEBUG messages** pokażą co scraper znajduje
- Wynik: ✅ lub ❌

### Test 2: Pełny scraping z debug mode

```bash
python livesport_h2h_scraper.py --mode auto --date 2025-10-25 --sports basketball --headless
```

W logach zobaczysz dla **każdego meczu**:

```
[15/50] Ziraat Bankasi vs Fenerbahce
   🏠 DEBUG: Znaleziono kurs gospodarzy: 1.23
   🔍 DEBUG: Kurs 1.23 w elemencie z klasą: odds-home-value...
   🔍 DEBUG: Kurs 4.50 w elemencie z klasą: odds-away-value...
   ✈️  DEBUG: Znaleziono kurs gości: 4.50
   💰 Znaleziono kursy (dedykowana metoda): 1.23 - 4.50
```

### Test 3: Sprawdź wyniki

```bash
python verify_identical_odds.py
```

Jeśli fix działa:
```
✅ Wszystkie kursy są RÓŻNE (home != away)
```

---

## 💡 MOŻLIWE PRZYCZYNY PROBLEMU

### 1. **Livesport nie pokazuje kursów gości na stronie H2H**

Scraper otwiera `/h2h/ogolem/` aby pobrać historię H2H.  
**Kursy mogą być tylko na głównej stronie meczu!**

**Przykład:**
- Główna strona: `https://livesport.com/.../mecz/.../szczegoly/` - kursy WIDOCZNE
- Strona H2H: `https://livesport.com/.../mecz/.../h2h/ogolem/` - kursy NIEWIDOCZNE lub NIEPEŁNE

**Rozwiązanie:**
- Kod teraz próbuje 3 metody znalezienia kursów
- Jeśli żadna nie działa - zwróci `None` (lepiej brak niż błędne)

### 2. **Struktura HTML dla gości jest inna**

Livesport może używać różnych klas dla kursów gości:
- `odds-away-value` (stary format)
- `bookmaker-away` (nowy format)
- `guest-odds` (międzynarodowy)

**Rozwiązanie:**
- Kod teraz szuka wielu wariantów klas
- Debug mode pokaże które klasy są używane

### 3. **Kursy gości ładują się później (lazy loading)**

Kurs gospodarzy może być w HTML od razu, ale kurs gości ładuje się dynamicznie.

**Rozwiązanie:**
- Kod czeka na elementy z kursami (WebDriverWait)
- Scroll down/up aby wywołać lazy loading

---

## 📊 OCZEKIWANE WYNIKI

### Scenariusz A: Fix działa idealnie

```
🏠 DEBUG: Znaleziono kurs gospodarzy: 1.23
✈️  DEBUG: Znaleziono kurs gości: 4.50
💰 Znaleziono kursy (dedykowana metoda): 1.23 - 4.50
```

**W emailu:**
```
🎲 Kursy: Ziraat Bankasi 1.23 | Fenerbahce 4.50 ✓
```

### Scenariusz B: Livesport nie pokazuje kursu gości

```
🏠 DEBUG: Znaleziono kurs gospodarzy: 1.23
❌ DEBUG: Nie znaleziono kursu gości
⚠️  Znaleziono tylko 1 kurs: 1.23 - brak kursu dla gości!
💡 Livesport prawdopodobnie nie pokazuje obu kursów na stronie H2H
```

**W emailu:**
```
(brak sekcji z kursami - kursy niedostępne)
```

To jest **poprawne zachowanie** - lepiej brak kursów niż błędne!

### Scenariusz C: Rozpoznanie kontekstu działa

```
🔍 DEBUG: Znalezione kursy (unikalne, fallback): [1.23, 4.50]
🔍 DEBUG: Kurs 1.23 w elemencie z klasą: odds-home-value...
🔍 DEBUG: Kurs 4.50 w elemencie z klasą: odds-away-value...
🏠 Kandydaci HOME: [1.23]
✈️  Kandydaci AWAY: [4.50]
💰 Znaleziono kursy (rozpoznanie kontekstu): 1.23 - 4.50
```

---

## 🎯 AKCJA WYMAGANA OD CIEBIE

### 1. Przetestuj z prawdziwym meczem

Znajdź mecz który miał problem (np. Ziraat Bankasi vs Fenerbahce):

```bash
python test_away_odds_debug.py "https://www.livesport.com/pl/koszykowka/[URL_MECZU]"
```

### 2. Sprawdź logi

Prześlij mi **dokładny output** z debug messages:
- Co scraper znalazł?
- Które klasy HTML były używane?
- Czy znalazł oba kursy czy tylko jeden?

### 3. Sprawdź czy strona H2H ma kursy

Otwórz ręcznie stronę meczu na Livesport:
1. Przejdź do meczu
2. Kliknij zakładkę "H2H"
3. **Czy widzisz kursy bukmacherskie na tej stronie?**

Jeśli NIE - to wyjaśnia problem! Kursy są tylko na głównej stronie.

---

## 🔧 MOŻLIWE DALSZE KROKI

Jeśli test pokazuje że Livesport nie ma kursów gości na stronie H2H:

### Opcja 1: Ładuj główną stronę meczu dla kursów

```python
# Najpierw otwórz główną stronę dla kursów
driver.get(match_url)  # szczegoly/
odds = extract_odds()

# Potem przejdź na H2H dla historii
driver.get(h2h_url)  # h2h/ogolem/
h2h_data = extract_h2h()
```

### Opcja 2: Użyj API bukmacherskiego (jeśli dostępne)

Niektóre bukmacherzy mają publiczne API z kursami.

### Opcja 3: Akceptuj brak kursów gości

Kursy są opcjonalne - mecze kwalifikują się przez H2H + formę.

---

## 📞 PYTANIA?

**Q: Dlaczego kursy gospodarzy działają a gości nie?**  
A: Livesport może pokazywać je w różnych miejscach HTML. Kod teraz szuka w wielu miejscach.

**Q: Co jeśli test pokazuje że kursy gości są na stronie?**  
A: Prześlij mi screenshot + debug output - znajdziemy odpowiednie selektory!

**Q: Czy to wpłynie na kwalifikację meczów?**  
A: NIE! Kursy są tylko dodatkową informacją. Mecze kwalifikują się przez H2H + formę.

---

**Przetestuj i daj znać co pokazał debug!** 🔍



