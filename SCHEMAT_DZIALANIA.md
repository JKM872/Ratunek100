# 📊 SCHEMAT DZIAŁANIA - Scraper → Aplikacja UI

## Kompletna architektura systemu

```
┌─────────────────────────────────────────────────────────────────────┐
│                          GITHUB ACTIONS                             │
│                    (Scraper - Hosting 24/7)                         │
│                                                                     │
│  ⏰ Harmonogram:                                                    │
│     • Codziennie o 00:00 (północ)                                  │
│     • Automatyczne uruchomienie                                    │
│     • Timeout: 360 minut (6 godzin)                                │
│                                                                     │
│  🔄 Proces:                                                         │
│     1. Instalacja Chrome + ChromeDriver                            │
│     2. Instalacja zależności Python                                │
│     3. Scrapowanie LiveSport API (Selenium + GraphQL)              │
│     4. Analiza H2H (≥60% win rate)                                 │
│     5. Pobieranie kursów (8 bukmacherów, 3 retry)                  │
│     6. Filtrowanie meczów (qualifies=True)                         │
│     7. Zapis do CSV                                                │
│     8. ✨ NOWE: Wysyłka do aplikacji UI                            │
│     9. Wysyłka email z wynikami                                    │
│                                                                     │
│  📊 Statystyki typowego uruchomienia:                              │
│     • Football: ~2500 meczów → ~25 kwalifikujących                │
│     • Basketball: ~800 meczów → ~15 kwalifikujących               │
│     • Volleyball: ~400 meczów → ~10 kwalifikujących               │
│     • Tennis: ~600 meczów → ~20 kwalifikujących                   │
│                                                                     │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       │ 🌐 HTTP POST
                       │ URL: /api/webhook/matches
                       │ Headers: Authorization: Bearer API_KEY
                       │ Body (JSON):
                       │   {
                       │     "date": "2025-10-26",
                       │     "sport": "football",
                       │     "matches": [...150 meczów...],
                       │     "qualified_count": 15,
                       │     "total_count": 150,
                       │     "timestamp": "2025-10-26T00:15:30.000Z"
                       │   }
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       APLIKACJA UI                                  │
│            (Railway/Render/localhost + ngrok)                       │
│                                                                     │
│  📥 Backend (Node.js + Express):                                    │
│     • Odbiera webhook ze scrapera                                  │
│     • Weryfikuje API Key (bezpieczeństwo)                          │
│     • Zapisuje do bazy SQLite                                      │
│     • Udostępnia REST API dla frontendu                            │
│                                                                     │
│  💾 Baza danych (SQLite):                                           │
│     • Tabela: matches (30+ kolumn)                                 │
│     • Indeksy: date, sport, qualifies                              │
│     • JSON fields: bookmakers, odds, h2h, form                     │
│                                                                     │
│  📊 REST API Endpoints:                                             │
│     GET  /api/health          - Status aplikacji                   │
│     POST /api/webhook/matches - Odbierz dane ze scrapera ⭐        │
│     GET  /api/matches         - Lista meczów (z filtrami)          │
│     GET  /api/stats           - Statystyki bazy danych             │
│     GET  /api/sports          - Lista sportów                      │
│                                                                     │
│  🖥️ Frontend (przyszłość):                                         │
│     • Dashboard ze statystykami                                    │
│     • Filtry: sport, data, kwalifikujące się                       │
│     • Karty meczów z kursami i H2H                                 │
│     • Auto-refresh co 30 sekund                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                       │
                       │ 📱 HTTP GET
                       │ /api/matches?qualifies=true
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      UŻYTKOWNIK                                     │
│                                                                     │
│  💻 Frontend (React/Next.js/Vue):                                   │
│     • Wyświetla mecze                                              │
│     • Sortuje po dacie/sporcie                                     │
│     • Pokazuje kursy + bukmacherów                                 │
│     • H2H stats + forma zespołów                                   │
│                                                                     │
│  📧 Email (Gmail):                                                  │
│     • Codzienne podsumowanie o północy                             │
│     • 2 maile:                                                     │
│       1. Przewaga formy + kursy                                    │
│       2. Wszystkie kwalifikujące + kursy                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📈 FLOW DANYCH (szczegółowo)

### 1️⃣ **SCRAPOWANIE (GitHub Actions)**

```python
# scrape_and_notify.py
python scrape_and_notify.py \
  --date 2025-10-26 \
  --sports football \
  --headless \
  --app-url "https://twoja-app.railway.app" \
  --app-api-key "tajny-klucz"
```

**Co się dzieje:**
1. Selenium otwiera Chrome (headless)
2. Wchodzi na LiveSport API (`https://global.ds.lsapp.eu/odds/pq_graphql`)
3. Pobiera listę meczów dla daty
4. Dla każdego meczu:
   - Analizuje H2H (ostatnie 5 meczów)
   - Oblicza win rate
   - Pobiera kursy z 8 bukmacherów (STS, Fortuna, Superbet, Bet365, etc.)
   - Analizuje formę zespołów
   - Określa czy qualifies (H2H ≥60%, forma, kursy)
5. Zapisuje do CSV (`outputs/football_2025-10-26.csv`)

---

### 2️⃣ **WYSYŁKA DO APLIKACJI (NOWE!)**

```python
# app_integrator.py
integrator = AppIntegrator(
    app_url="https://twoja-app.railway.app",
    api_key="tajny-klucz"
)

integrator.send_matches(
    matches=rows,           # Lista 150 meczów
    date="2025-10-26",
    sport="football"
)
```

**HTTP Request:**
```http
POST /api/webhook/matches HTTP/1.1
Host: twoja-app.railway.app
Authorization: Bearer tajny-klucz
Content-Type: application/json

{
  "date": "2025-10-26",
  "sport": "football",
  "matches": [
    {
      "home_team": "Real Madrid",
      "away_team": "Barcelona",
      "match_time": "20:00",
      "home_odds": 2.15,
      "draw_odds": 3.40,
      "away_odds": 3.10,
      "best_home_bookmaker": "STS",
      "best_away_bookmaker": "Fortuna",
      "bookmakers_found": ["STS", "Fortuna", "Superbet"],
      "all_odds": {
        "STS": {"home": 2.15, "draw": 3.40, "away": 3.10},
        "Fortuna": {"home": 2.10, "draw": 3.50, "away": 3.20}
      },
      "h2h_count": 10,
      "home_wins_in_h2h_last5": 3,
      "win_rate": 0.7,
      "qualifies": true,
      "form_advantage": true,
      ...
    },
    ... 149 więcej meczów ...
  ],
  "qualified_count": 15,
  "total_count": 150,
  "timestamp": "2025-10-26T00:15:30.000Z"
}
```

---

### 3️⃣ **ODBIÓR W APLIKACJI**

```javascript
// server.js (Express)
app.post('/api/webhook/matches', verifyApiKey, async (req, res) => {
  const { date, sport, matches, qualified_count } = req.body;
  
  console.log(`📥 Otrzymano ${matches.length} meczów (${sport})`);
  
  // Zapisz do SQLite
  for (const match of matches) {
    db.run(`
      INSERT OR REPLACE INTO matches (
        match_date, home_team, away_team,
        home_odds, draw_odds, away_odds,
        h2h_count, win_rate, qualifies, ...
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ...)
    `, [match.match_date, match.home_team, ...]);
  }
  
  res.json({ 
    success: true, 
    saved: matches.length 
  });
});
```

**Baza danych:**
```sql
-- SQLite: data/matches.db
CREATE TABLE matches (
  id INTEGER PRIMARY KEY,
  match_date TEXT,
  match_time TEXT,
  sport TEXT,
  league TEXT,
  home_team TEXT,
  away_team TEXT,
  home_odds REAL,
  draw_odds REAL,
  away_odds REAL,
  best_home_bookmaker TEXT,
  best_away_bookmaker TEXT,
  bookmakers_found TEXT,  -- JSON array
  all_odds TEXT,          -- JSON object
  h2h_count INTEGER,
  home_wins_in_h2h_last5 INTEGER,
  win_rate REAL,
  h2h_last5 TEXT,         -- JSON array
  home_form_overall TEXT, -- JSON array
  away_form_overall TEXT, -- JSON array
  form_advantage BOOLEAN,
  qualifies BOOLEAN,
  scraped_at TIMESTAMP,
  ...
);
```

---

### 4️⃣ **DOSTĘP PRZEZ API**

```bash
# Frontend pobiera mecze
GET /api/matches?sport=football&qualifies=true

Response:
{
  "success": true,
  "matches": [
    {
      "id": 1,
      "home_team": "Real Madrid",
      "away_team": "Barcelona",
      "home_odds": 2.15,
      "qualifies": true,
      ...
    },
    ...
  ],
  "count": 15
}
```

---

### 5️⃣ **WYŚWIETLANIE (Frontend)**

```jsx
// React/Next.js example
function MatchesList() {
  const [matches, setMatches] = useState([]);
  
  useEffect(() => {
    fetch('https://twoja-app.railway.app/api/matches?qualifies=true')
      .then(res => res.json())
      .then(data => setMatches(data.matches));
  }, []);
  
  return (
    <div>
      {matches.map(match => (
        <MatchCard 
          key={match.id}
          homeTeam={match.home_team}
          awayTeam={match.away_team}
          odds={{ home: match.home_odds, away: match.away_odds }}
          bookmaker={match.best_home_bookmaker}
        />
      ))}
    </div>
  );
}
```

---

## ⏱️ TIMELINE (codzienne uruchomienie)

```
00:00:00 - GitHub Actions trigger (cron)
00:00:30 - Instalacja Chrome + Python
00:01:00 - Start scrapera (football)
00:01:30 - Pobieranie listy meczów
00:02:00 - Start analizy H2H
00:10:00 - Pobieranie kursów (8 bukmacherów × 150 meczów)
00:15:00 - Filtrowanie (15/150 qualifies)
00:15:30 - 📤 Wysyłka do aplikacji UI ⭐ NOWE!
00:15:32 - 💾 Zapis w aplikacji (SQLite)
00:16:00 - 📧 Wysyłka email 1/2 (forma + kursy)
00:16:30 - 📧 Wysyłka email 2/2 (wszystkie + kursy)
00:17:00 - ✅ DONE!
```

---

## 🔒 BEZPIECZEŃSTWO

### Warstwa 1: API Key

```
GitHub Actions                    Aplikacja UI
    |                                 |
    | Authorization:                  |
    | Bearer tajny-klucz-12345    --> | Weryfikacja
    |                                 | if (key != API_KEY) → 401
    |                                 |
```

### Warstwa 2: HTTPS

```
Railway/Render → Darmowy SSL → https://
```

### Warstwa 3: Rate Limiting (opcjonalny)

```javascript
// Express rate limit
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minut
  max: 100 // max 100 requestów
});

app.use('/api/', limiter);
```

---

## 📊 STATYSTYKI SYSTEMU

### Typowe uruchomienie (o północy):

| Sport      | Meczów | Kwalifikuje | Czas   |
|------------|--------|-------------|--------|
| Football   | 2500   | ~25         | 15 min |
| Basketball | 800    | ~15         | 8 min  |
| Volleyball | 400    | ~10         | 5 min  |
| Tennis     | 600    | ~20         | 10 min |
| **TOTAL**  | **4300** | **~70** | **38 min** |

### Wykorzystanie zasobów:

- **GitHub Actions:** ~40 minut/dzień (z 2000 minut/miesiąc darmowych)
- **Railway:** ~10 MB bazy/miesiąc, minimalny CPU
- **Bandwidth:** ~5 MB/dzień (webhook + API calls)

---

## 🎯 ZALETY NOWEJ ARCHITEKTURY

### ❌ Stare (tylko CSV + Email):
- ✗ Dane tylko w emailu
- ✗ Brak API
- ✗ Brak historii
- ✗ Brak frontendu
- ✗ Trudna analiza

### ✅ Nowe (Scraper → Aplikacja UI):
- ✓ Dane w bazie SQLite
- ✓ REST API dla frontendu
- ✓ Historia meczów (30 dni)
- ✓ Łatwa integracja z UI
- ✓ Statystyki + filtry
- ✓ Dalej email + CSV (backup)

---

## 📚 DOKUMENTACJA

- **Quick Start:** `QUICK_START_INTEGRACJA.md`
- **Pełna instrukcja:** `INSTRUKCJA_WDROZENIA_KOMPLETNA.md`
- **Dokumentacja aplikacji:** `example_ui_app/README.md`
- **API Examples:** `API_EXAMPLES.md`
- **Integracja:** `APP_INTEGRATION_GUIDE.md`

---

## 🚀 NASTĘPNE KROKI

1. ✅ **Wdrożenie aplikacji UI** (Railway/Render) - 5 minut
2. ✅ **Konfiguracja GitHub Secrets** - 2 minuty
3. ✅ **Test ręczny** - 5 minut
4. ⏳ **Czekaj do północy** - automatyczne uruchomienie
5. 🎉 **Profit!** - Dane płyną codziennie

---

**Pytania?** Sprawdź `QUICK_START_INTEGRACJA.md` lub `INSTRUKCJA_WDROZENIA_KOMPLETNA.md`!
