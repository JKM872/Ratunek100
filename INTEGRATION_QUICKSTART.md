# ⚡ Szybki Start - Integracja z Aplikacją UI

## 🎯 W 3 krokach połącz scraper z aplikacją!

### **Krok 1: Dodaj endpoint w aplikacji UI** (2 minuty)

Wybierz swój framework i dodaj ten kod:

**Express.js:**
```javascript
app.post('/api/webhook/matches', (req, res) => {
  const { matches, date, sport } = req.body;
  console.log(`✅ ${matches.length} meczów`);
  
  // TUTAJ: Zapisz do bazy lub zaktualizuj state
  
  res.json({ status: 'success' });
});
```

**Next.js:**
```typescript
// app/api/webhook/matches/route.ts
export async function POST(request) {
  const { matches } = await request.json();
  // TUTAJ: Zapisz do bazy
  return Response.json({ success: true });
}
```

**Python/FastAPI:**
```python
@app.post("/api/webhook/matches")
async def receive_matches(data: dict):
    matches = data['matches']
    # TUTAJ: Zapisz do bazy
    return {"status": "success"}
```

### **Krok 2: Testuj połączenie** (1 minuta)

```bash
python test_app_integration.py
```

Podaj URL aplikacji (np. `http://localhost:3000`) i sprawdź czy działa!

### **Krok 3: Uruchom scraper z integracją** (1 minuta)

```bash
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to email@example.com \
  --from-email email@example.com \
  --password "haslo" \
  --headless \
  --app-url http://localhost:3000
```

**LUB** utwórz `app_integration_config.json`:
```json
{
  "app_url": "http://localhost:3000",
  "enabled": true
}
```

I uruchom normalnie - dane pójdą automatycznie!

---

## 📦 Co otrzymasz w swojej aplikacji?

```json
{
  "date": "2025-10-11",
  "sport": "football",
  "matches": [
    {
      "match_url": "...",
      "home_team": "Real Madrid",
      "away_team": "Barcelona",
      "match_time": "20:00",
      "home_wins_in_h2h_last5": 3,
      "qualifies": true,
      "home_odds": 2.10,
      "away_odds": 3.50
    }
  ],
  "qualified_count": 15,
  "total_count": 150
}
```

---

## 🔧 Przykłady użycia w frontendzie

**React:**
```jsx
function Matches() {
  const [matches, setMatches] = useState([]);
  
  // Real-time updates przez WebSocket
  useEffect(() => {
    socket.on('matches-updated', (data) => {
      setMatches(data.matches);
    });
  }, []);
  
  return (
    <div>
      {matches.map(m => (
        <div key={m.match_url}>
          {m.home_team} vs {m.away_team}
          {m.qualifies && <span>✅</span>}
        </div>
      ))}
    </div>
  );
}
```

---

## 🌍 Deployment

**Lokalnie:**
```bash
--app-url http://localhost:3000
```

**Produkcja (Railway/Render):**
```bash
--app-url https://twoja-app.railway.app
```

**Testowo (ngrok):**
```bash
# Terminal 1
ngrok http 3000

# Terminal 2  
--app-url https://abc123.ngrok.io
```

---

## 🎉 Gotowe!

Twój scraper jest teraz połączony z aplikacją!

**Pełna dokumentacja:** `APP_INTEGRATION_GUIDE.md`  
**Przykłady endpointów:** `example_backend_endpoint.js`  
**Test integracji:** `python test_app_integration.py`

**Powodzenia! 🚀**







