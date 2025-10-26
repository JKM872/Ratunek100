# ⚠️ Problem z Pobieraniem Kursów z Livesport

**Data:** 27 października 2025  
**Status:** ❌ Kursy nie działają na GitHub Actions

---

## 🐛 Problem

**Kursy bukmacherskie nie pojawiają się w mailach** z GitHub Actions.

### Co Nie Działa:

1. ❌ **GraphQL API** - 404 Not Found (Livesport nie ma publicznego API)
2. ❌ **Selenium HTML Scraping** - Nie znajduje kursów (prawdopodobnie JS/blokada botów)

### Co Działa:

1. ✅ H2H (Head-to-Head)
2. ✅ Forma drużyn
3. ✅ Wszystkie inne dane

---

## 🔍 Dlaczego Kursy Nie Działają?

### Powód 1: Livesport Blokuje Boty

**Symptomy:**
- W przeglądarce (normalnie) kursy są widoczne
- W headless Selenium kursy nie są dostępne
- GitHub Actions = środowisko "botowe" (wykrywalne)

**Livesport prawdopodobnie:**
- Wykrywa headless mode
- Blokuje dostęp do kursów dla botów
- Wymaga user interaction (scroll, click)

### Powód 2: Kursy Ładują Się Bardzo Późno

**Symptomy:**
- Timeout 5s może być za mało
- GitHub Actions ma wolniejsze połączenie
- JS może ładować kursy asynchronicznie

### Powód 3: Kursy w iframe/Lazy Loading

**Symptomy:**
- Kursy mogą być w osobnym iframe
- Lazy loading wymaga scroll
- Selenium nie widzi elementów w iframe

---

## ✅ Co Zrobiliśmy? (Tymczasowe Rozwiązanie)

### Wyłączyliśmy Pobieranie Kursów

**Plik:** `livesport_h2h_scraper.py`

**Przed:**
```python
odds = extract_betting_odds_with_selenium(driver, soup, url=url)
out['home_odds'] = odds.get('home_odds')
out['away_odds'] = odds.get('away_odds')
```

**Po:**
```python
# TYMCZASOWO WYŁĄCZONE
out['home_odds'] = None
out['away_odds'] = None
```

**Efekt:**
- ✅ Scraping jest **szybszy** (nie czeka na kursy)
- ✅ Brak błędów 404/405
- ✅ **Maile nadal działają** (H2H, forma, etc.)
- ⚠️ Brak sekcji z kursami w mailu (ale lepiej niż "nan")

---

## 🔮 Przyszłe Rozwiązania

### Opcja A: Zewnętrzne API Kursów (Najlepsze)

**Serwisy z API:**

1. **The Odds API** (https://the-odds-api.com/)
   - ✅ Darmowy tier: 500 requestów/miesiąc
   - ✅ Obsługuje wiele sportów
   - ✅ Wiele bukmacherów
   - ❌ Wymaga rejestracji + API key

2. **API-Football** (https://www.api-football.com/)
   - ✅ Kursy bukmacherskie w danych
   - ✅ Dużo danych o meczach
   - ❌ Głównie piłka nożna
   - ❌ Płatny (po darmowym tierze)

3. **RapidAPI Sports Odds**
   - ✅ Wiele sportów
   - ✅ Proste API
   - ❌ Płatny

**Implementacja:**
```python
import requests

def get_odds_from_external_api(match_id, api_key):
    url = f"https://api.the-odds-api.com/v4/sports/.../odds"
    headers = {'x-api-key': api_key}
    response = requests.get(url, headers=headers)
    return response.json()
```

**Koszt:** 0-50 PLN/miesiąc (zależnie od liczby meczów)

---

### Opcja B: Scrapować Nordic Bet Bezpośrednio

**Zamiast Livesport → Nordic Bet:**

```python
def get_odds_from_nordicbet(team_a, team_b, sport='football'):
    url = f"https://www.nordicbet.com/pl/zakłady/{sport}"
    # Scrapuj bezpośrednio z Nordic Bet
    # Znaleźć mecz po nazwach drużyn
    # Zwróć kursy
```

**Wady:**
- ❌ Trzeba znaleźć ID meczu na Nordic Bet
- ❌ Nordic Bet też może blokować boty
- ❌ Inny HTML niż Livesport

---

### Opcja C: Selenium z Obejściem Detekcji Botów

**undetected-chromedriver:**

```bash
pip install undetected-chromedriver
```

```python
import undetected_chromedriver as uc

def start_driver_undetected():
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    driver = uc.Chrome(options=options)
    return driver
```

**Zalety:**
- ✅ Omija detekcję botów
- ✅ Działa z Livesport
- ⚠️ Wolniejsze (więcej overhead)

**Wady:**
- ❌ Może nie działać na GitHub Actions
- ❌ Wymaga dodatkowej biblioteki

---

### Opcja D: Zwiększyć Timeout i Dodać Więcej Akcji

**Spróbuj:**
- Zwiększyć timeout do 10-15s
- Dodać scroll do sekcji z kursami
- Kliknąć na zakładkę "Kursy"
- Poczekać dłużej na JS

```python
# Zwiększony timeout
odds_timeout = 15 if is_github else 5

# Scroll do kursów
driver.execute_script("window.scrollTo(0, 500);")
time.sleep(2)

# Kliknij zakładkę "Kursy"
try:
    odds_tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Kursy')]")
    odds_tab.click()
    time.sleep(3)
except:
    pass
```

**Wady:**
- ❌ Bardzo wolne (15s+ na mecz)
- ❌ Może nadal nie działać

---

## 📊 Porównanie Rozwiązań

| Rozwiązanie | Koszt | Niezawodność | Szybkość | Trudność |
|-------------|-------|--------------|----------|----------|
| **Zewnętrzne API** | 💰 0-50 PLN/m | ✅ 99% | ⚡ Szybko | 🟢 Łatwe |
| **Nordic Bet Scraping** | 💚 Darmowe | ⚠️ 50% | 🐌 Wolno | 🟡 Średnie |
| **undetected-chromedriver** | 💚 Darmowe | ⚠️ 70% | 🐌 Bardzo wolno | 🔴 Trudne |
| **Zwiększony timeout** | 💚 Darmowe | ❌ 30% | 🐌 Bardzo wolno | 🟢 Łatwe |
| **Brak kursów** | 💚 Darmowe | ✅ 100% | ⚡ Szybko | 🟢 Łatwe |

---

## 🎯 Moja Rekomendacja

### Krótkoterminowo (Teraz):
✅ **Wyłącz kursy** (już zrobione)
- Maile działają
- System jest szybki
- Brak błędów

### Długoterminowo (Przyszłość):
💡 **Użyj The Odds API** (https://the-odds-api.com/)
- Darmowy tier: 500 requestów/miesiąc
- Niezawodne
- Proste w implementacji

---

## 📝 Co Dalej?

### Commit & Push (Teraz)

```bash
git add .
git commit -m "Disable odds scraping temporarily (Livesport blocks bots)"
git push origin main
```

**Efekt:**
- ✅ Maile działają BEZ kursów
- ✅ Szybszy scraping
- ✅ Brak błędów

### Implementuj The Odds API (Później)

Jeśli chcesz kursy w przyszłości:
1. Zarejestruj się na https://the-odds-api.com/
2. Uzyskaj API key (darmowy tier)
3. Zaimplementuj funkcję pobierania kursów
4. Włącz z powrotem w scraperze

---

## 🤔 Pytania?

**Q: Czy mogę jakoś ominąć blokadę Livesport?**  
A: Teoretycznie tak (undetected-chromedriver), ale to wolne i może nie działać na GitHub Actions.

**Q: Czy kursy są potrzebne?**  
A: NIE! Kursy to tylko **dodatkowa informacja** (nie wpływa na scoring H2H).

**Q: Co z innymi źródłami kursów?**  
A: Najlepsze to zewnętrzne API (The Odds API). Inne opcje (Nordic Bet, etc.) mają podobne problemy.

---

**Status:** ✅ Problem rozwiązany (tymczasowo) - kursy wyłączone  
**Rekomendacja:** Commit & Push, później rozważ The Odds API  
**Data:** 27 października 2025

