# 🎯 Aplikacja UI - Odbieranie danych ze scrapera

Ta aplikacja odbiera dane z GitHub Actions scrapera i wyświetla je w interfejsie użytkownika.

## 🚀 Szybki Start

### 1. Instalacja

```bash
cd example_ui_app
npm install
```

### 2. Konfiguracja

Utwórz plik `.env`:

```bash
cp .env.example .env
```

Edytuj `.env` i ustaw swój API Key:

```env
PORT=3000
SCRAPER_API_KEY=twoj-super-tajny-klucz-12345
NODE_ENV=development
```

### 3. Uruchomienie

```bash
npm start
```

Aplikacja uruchomi się na `http://localhost:3000`

### 4. Test połączenia

```bash
npm test
```

## 📊 API Endpoints

### Health Check
```bash
GET /api/health
```

**Odpowiedź:**
```json
{
  "status": "ok",
  "message": "Aplikacja UI działa!",
  "timestamp": "2025-10-26T12:00:00.000Z"
}
```

### Webhook (odbierz dane ze scrapera)
```bash
POST /api/webhook/matches
Authorization: Bearer twoj-api-key

{
  "date": "2025-10-26",
  "sport": "football",
  "matches": [...],
  "qualified_count": 15,
  "total_count": 150
}
```

**Odpowiedź:**
```json
{
  "success": true,
  "received": 150,
  "saved": 150,
  "errors": 0,
  "message": "Zapisano 150 meczów do bazy danych"
}
```

### Pobierz mecze
```bash
GET /api/matches?sport=football&date=2025-10-26&qualifies=true
```

**Parametry:**
- `sport` - filtruj po sporcie (football, basketball, etc.)
- `date` - filtruj po dacie (YYYY-MM-DD)
- `qualifies` - tylko kwalifikujące się mecze (true/false)
- `limit` - maksymalna liczba wyników (domyślnie 1000)

**Odpowiedź:**
```json
{
  "success": true,
  "matches": [...],
  "count": 15
}
```

### Statystyki
```bash
GET /api/stats
```

**Odpowiedź:**
```json
{
  "success": true,
  "stats": {
    "total_matches": 500,
    "qualifying_matches": 50,
    "unique_sports": 5,
    "date_range": "2025-10-01 - 2025-10-26",
    "dates": 26,
    "last_update": "2025-10-26T12:00:00.000Z"
  }
}
```

### Lista sportów
```bash
GET /api/sports
```

**Odpowiedź:**
```json
{
  "success": true,
  "sports": [
    {
      "sport": "football",
      "total_count": 300,
      "qualifying_count": 30
    },
    ...
  ]
}
```

## 🌐 Deployment

### Railway (Zalecane)

1. Zaloguj się: https://railway.app
2. New Project → Deploy from GitHub repo
3. Wybierz folder `example_ui_app`
4. Dodaj zmienne środowiskowe:
   - `SCRAPER_API_KEY=twoj-klucz`
5. Deploy!

### Render

1. Zaloguj się: https://render.com
2. New → Web Service
3. Connect to GitHub
4. Build Command: `npm install`
5. Start Command: `npm start`
6. Environment Variables:
   - `SCRAPER_API_KEY=twoj-klucz`

### Localhost + ngrok (Development)

1. Uruchom aplikację:
```bash
npm start
```

2. W innym terminalu:
```bash
ngrok http 3000
```

3. Skopiuj URL ngrok (np. `https://abc123.ngrok.io`)

4. Użyj w GitHub Actions:
```yaml
--app-url "https://abc123.ngrok.io"
--app-api-key "twoj-klucz"
```

## 🔧 Konfiguracja GitHub Actions

Dodaj do `.github/workflows/your-workflow.yml`:

```yaml
- name: Run scraper with app integration
  run: |
    python scrape_and_notify.py \
      --date $(date +%Y-%m-%d) \
      --sports football \
      --app-url "${{ secrets.APP_URL }}" \
      --app-api-key "${{ secrets.APP_API_KEY }}"
```

Dodaj Secrets w GitHub:
- `APP_URL` = `https://twoja-app.railway.app`
- `APP_API_KEY` = `twoj-super-tajny-klucz`

## 📁 Struktura bazy danych

SQLite database: `data/matches.db`

**Tabela: matches**
- Podstawowe: match_date, match_time, sport, league
- Zespoły: home_team, away_team
- Kursy: home_odds, draw_odds, away_odds, bookmakers
- H2H: h2h_count, home_wins, away_wins, win_rate
- Forma: home_form_overall, away_form_overall, form_advantage
- Qualifikacja: qualifies
- Metadata: scraped_at, source

## 🐛 Troubleshooting

### Błąd: "SQLITE_CANTOPEN"
```bash
mkdir data
chmod 755 data
```

### Błąd: "401 Unauthorized"
Sprawdź czy API Key się zgadza:
- W aplikacji: `.env` → `SCRAPER_API_KEY`
- W scraperze: `--app-api-key`
- W GitHub: Secret `APP_API_KEY`

### Błąd: "Connection refused"
Sprawdź czy aplikacja działa:
```bash
curl http://localhost:3000/api/health
```

## 📞 Pomoc

Masz problem? Sprawdź:
1. Logi serwera (terminal gdzie uruchomiłeś `npm start`)
2. Logi GitHub Actions
3. Test webhook: `npm test`
