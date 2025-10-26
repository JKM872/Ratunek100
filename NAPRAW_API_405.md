# 🔧 Naprawa Błędu 405 Method Not Allowed

**Błąd:** `405 Client Error: Method Not Allowed`  
**Endpoint:** `https://www.livesport.com/req/api/v2/configurator/data`

---

## 🐛 Co Się Stało?

LiveSport API zwraca **405 Method Not Allowed** gdy próbujemy POST request.

**Możliwe przyczyny:**
1. Endpoint wymaga GET zamiast POST
2. Endpoint się zmienił (LiveSport zaktualizował API)
3. Wymagana jest autoryzacja/tokeny
4. Nagłówki HTTP są niepoprawne

---

## ✅ Co Zostało Naprawione?

### 1. Dodano Fallback z GET Request

Teraz system próbuje:
1. **POST** do GraphQL endpoint (oryginalna metoda)
2. Jeśli 405 → **GET** do prostszego endpointa: `/api/v1/event/{event_id}/odds`

```python
# Metoda 1: POST (GraphQL)
response = requests.post(api_url, json=query)

# Jeśli 405:
# Metoda 2: GET (prostszy endpoint)
simple_url = f"https://www.livesport.com/api/v1/event/{event_id}/odds"
response = requests.get(simple_url, params={'bookmakerId': '165'})
```

### 2. Ulepszone Nagłówki HTTP

Dodano więcej nagłówków aby symulować prawdziwą przeglądarkę:
- `Sec-Fetch-*` headers
- `sec-ch-ua-*` headers  
- Lepszy `Accept-Encoding`

---

## 🧪 Jak Przetestować Ponownie?

```bash
python test_odds_api.py
```

Wklej ten sam URL i zobacz czy teraz działa.

**Jeśli nadal 405**, to znaczy że LiveSport zmienił API i musimy znaleźć nowy endpoint.

---

## 🔍 JAK ZNALEŹĆ WŁAŚCIWY ENDPOINT (Developer Tools)

Jeśli nadal nie działa, możemy znaleźć właściwy endpoint przez DevTools:

### Krok 1: Otwórz Mecz w Przeglądarce

```
https://www.livesport.com/pl/mecz/pilka-nozna/atl-madryt-jaarqpLQ/betis-vJbTeCGP/?mid=SMhtyWoI
```

### Krok 2: Otwórz DevTools

- **Windows:** `F12` lub `Ctrl+Shift+I`
- **Mac:** `Cmd+Option+I`

### Krok 3: Przejdź do zakładki "Network"

- Kliknij "Network" (Sieć)
- Jeśli nic nie ma, odśwież stronę (`F5`)

### Krok 4: Szukaj Requestów z Kursami

W filtrze wpisz: **"odds"** lub **"bookmaker"**

**Szukaj:**
- Request URL zawierający "odds"
- Request Method: `GET` lub `POST`
- Response zawierający liczby (kursy)

### Krok 5: Sprawdź Request Details

Kliknij na request → zakładka "Headers"

**Znajdź:**
1. **Request URL** - to jest endpoint!
2. **Request Method** - GET czy POST?
3. **Query String Parameters** - jakie parametry?
4. **Request Headers** - jakie nagłówki?

### Krok 6: Sprawdź Response

Zakładka "Response" lub "Preview"

**Szukaj struktur JSON:**
```json
{
  "odds": {
    "home": 1.85,
    "draw": 3.50,
    "away": 4.20
  }
}
```

### Krok 7: Zaktualizuj Kod

Jeśli znalazłeś nowy endpoint, zaktualizuj:

```python
# livesport_odds_api_client.py, linia 32
self.api_url = "NOWY_ENDPOINT_TUTAJ"
```

---

## 🆘 ALTERNATYWNE ROZWIĄZANIE

Jeśli API w ogóle nie działa, możemy:

### Opcja A: Użyć Selenium (Fallback)

System już ma fallback do scrapowania HTML przez Selenium.

**Włącz VERBOSE aby zobaczyć:**
```python
# livesport_h2h_scraper.py, linia 65
VERBOSE = True
```

**W logach zobaczysz:**
```
💰 Próbuję pobrać kursy przez GraphQL API...
⚠️ API: Brak kursów dla tego meczu
⚠️ API nie zwróciło kursów, próbuję fallback...
💰 DEBUG: Znaleziono kontener kursów w HTML
```

### Opcja B: Zewnętrzne API Kursów

Użyć zewnętrznego serwisu kursów:
- **Odds API** (https://the-odds-api.com/)
- **API Football** (https://www.api-football.com/)
- **RapidAPI Sports**

**Wymaga:**
- Rejestracja
- API Key (często płatny)

### Opcja C: Scrapować Bezpośrednio Nordic Bet

Zamiast LiveSport, scrapować bezpośrednio z:
```
https://www.nordicbet.com/pl/zakłady/piłka-nożna
```

**Wymaga:**
- Znaleźć ID meczu na Nordic Bet
- Scrapować ich stronę

---

## 📧 Co Zrobić Teraz?

### Plan A: Czekaj na Automatyczny Fallback

System automatycznie spróbuje scrapować HTML jeśli API nie działa.

**W mailach nadal będziesz miał kursy** (jeśli są dostępne w HTML).

### Plan B: Wyłącz Kursy Tymczasowo

Jeśli kursy nie są krytyczne, możesz je wyłączyć:

```python
# livesport_h2h_scraper.py, linia ~622
# ZAKOMENTUJ te linie:
# odds = extract_betting_odds_with_selenium(driver, soup, url=url)
# out['home_odds'] = odds.get('home_odds')
# out['away_odds'] = odds.get('away_odds')

# ZAMIAST:
out['home_odds'] = None
out['away_odds'] = None
```

### Plan C: Znajdź Właściwy Endpoint (DevTools)

Użyj instrukcji powyżej aby znaleźć nowy endpoint.

**Gdy znajdziesz, daj znać!** Zaktualizuję kod.

---

## 🔍 DEBUG: Co Sprawdzić?

1. **Test z innym meczem:**
   ```bash
   python test_odds_api.py
   # Wklej URL meczu który dopiero się odbędzie (nie skończony)
   ```

2. **Test połączenia z API:**
   ```bash
   curl -X GET "https://www.livesport.com/api/v1/event/SMhtyWoI/odds?bookmakerId=165"
   ```

3. **Test czy mecz ma kursy na stronie:**
   - Otwórz URL w przeglądarce
   - Sprawdź czy widzisz kursy na stronie
   - Jeśli nie ma - API też nie będzie miało

---

## 📝 Następne Kroki

1. ✅ **Przetestuj ponownie** z poprawkami
2. ⚠️ **Jeśli nadal 405** → użyj DevTools aby znaleźć endpoint
3. ✅ **Alternatywnie** → system użyje fallback (HTML scraping)
4. ✅ **Commit & Push** → system będzie działał z fallback

---

**Status:** ⚠️ W trakcie naprawy  
**Data:** 27 października 2025, 00:15

**PS:** Jeśli znajdziesz właściwy endpoint przez DevTools, daj znać - zaktualizuję kod! 🔧

