# 🔗 JAK POŁĄCZYĆ SCRAPERA Z TWOJĄ APLIKACJĄ UI?

## ⚡ Szybki Start (5 minut)

### **Krok 1: Dodaj endpoint w swojej aplikacji UI** ⏱️ 2 min

Wybierz swój framework:

**React + Express (backend):**
```javascript
// server.js lub app.js
const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

app.post('/api/webhook/matches', (req, res) => {
  const { matches, date, sport, qualified_count } = req.body;
  
  console.log(`✅ Otrzymano ${matches.length} meczów (${sport})`);
  console.log(`   Kwalifikujących się: ${qualified_count}`);
  
  // TUTAJ: Zapisz do bazy lub state
  // matches.forEach(match => {
  //   db.saveMatch(match);
  // });
  
  res.json({ status: 'success', received: matches.length });
});

app.listen(3000, () => {
  console.log('🚀 Server on http://localhost:3000');
});
```

**Next.js:**
```typescript
// app/api/webhook/matches/route.ts
export async function POST(request: Request) {
  const { matches, date, sport } = await request.json();
  
  console.log(`✅ ${matches.length} meczów`);
  
  // TUTAJ: Zapisz do bazy
  
  return Response.json({ success: true });
}
```

**Python/FastAPI:**
```python
@app.post("/api/webhook/matches")
async def receive_matches(data: dict):
    matches = data['matches']
    print(f"✅ {len(matches)} meczów")
    
    # TUTAJ: Zapisz do bazy
    
    return {"status": "success"}
```

---

### **Krok 2: Test szybki** ⏱️ 1 min

```bash
python quick_test.py
```

Podaj URL aplikacji (np. `http://localhost:3000`)

---

### **Krok 3: Pełny test z prawdziwymi danymi** ⏱️ 2 min

```bash
test_integration_jakub.bat
```

Ten skrypt:
- ✅ Scrapuje 10 meczów (szybki test)
- ✅ Wysyła email
- ✅ Wysyła dane do aplikacji UI
- ✅ Wszystko automatycznie!

**UWAGA:** Edytuj plik i zmień `APP_URL` na URL swojej aplikacji!

---

## 📡 Co otrzymasz w aplikacji?

```json
{
  "date": "2025-10-11",
  "sport": "football",
  "matches": [
    {
      "match_url": "https://...",
      "home_team": "Real Madrid",
      "away_team": "Barcelona",
      "match_time": "20:00",
      "home_wins_in_h2h_last5": 3,
      "h2h_count": 5,
      "qualifies": true,
      "home_odds": 2.10,
      "away_odds": 3.50,
      "home_form_overall": ["W", "W", "L", "W", "D"],
      "away_form_overall": ["L", "L", "W", "L", "L"],
      "form_advantage": true,
      "win_rate": 0.60
    }
  ],
  "qualified_count": 15,
  "total_count": 150,
  "timestamp": "2025-10-11T10:30:00"
}
```

---

## 🚀 Produkcja - Pełna automatyzacja

### **1. Edytuj `daily_scraper_with_app_integration.bat`:**

```batch
SET APP_URL=http://localhost:3000  # Zmień na URL aplikacji
SET SPORTS=football basketball     # Sporty które chcesz
```

### **2. Dodaj do Task Scheduler:**

1. Win + R → `taskschd.msc`
2. Create Task
3. Trigger: Codziennie o 9:00
4. Action: Uruchom `daily_scraper_with_app_integration.bat`

### **3. Gotowe!**

Teraz **każdego dnia automatycznie**:
1. 🕘 9:00 - Scraper startuje
2. 🔄 Scrapuje mecze z Livesport
3. 📧 Wysyła email do Ciebie
4. 📡 Wysyła dane do aplikacji UI
5. 💾 Aplikacja zapisuje do bazy
6. 📱 Frontend wyświetla dane

**Wszystko bez Twojej interwencji!** 🎉

---

## 🎯 Twoje dane:

```bash
Email: jakub.majka.zg@gmail.com
Password: vurb tcai zaaq itjx (App Password)

# Przykład użycia w skrypcie:
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to jakub.majka.zg@gmail.com \
  --from-email jakub.majka.zg@gmail.com \
  --password "vurb tcai zaaq itjx" \
  --headless \
  --sort time \
  --app-url http://localhost:3000
```

---

## 🧪 3 sposoby testowania:

### **Test 1: Prosty (1 min)**
```bash
python quick_test.py
```

### **Test 2: Z prawdziwymi danymi (3 min)**
```bash
test_integration_jakub.bat
```

### **Test 3: Ręczny (elastyczny)**
```bash
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to jakub.majka.zg@gmail.com \
  --from-email jakub.majka.zg@gmail.com \
  --password "vurb tcai zaaq itjx" \
  --headless \
  --max-matches 5 \
  --app-url http://localhost:3000
```

---

## 🌍 Gdzie hostować?

### **Aplikacja UI:**
- **Railway** (NAJLEPSZE) - GitHub Student Pack
- **Render** - Darmowy tier
- **Vercel** - Świetne dla Next.js
- **Heroku** - $13/miesiąc z Student Pack

### **Scraper:**
- **Lokalnie** - Task Scheduler (Windows)
- **VPS** - DigitalOcean ($200 kredytu Student Pack)
- **Railway** - Cron jobs

---

## 🐛 Troubleshooting

### **"Connection refused"**
```
❌ Nie można połączyć się z aplikacją
```
**Rozwiązanie:**
- Sprawdź czy aplikacja działa: `curl http://localhost:3000/api/health`
- Użyj `http://127.0.0.1:3000` zamiast `localhost`

### **"404 Not Found"**
```
❌ Status: 404
```
**Rozwiązanie:**
- Sprawdź endpoint: `/api/webhook/matches` (bez końcowego `/`)
- Sprawdź routing w aplikacji

### **CORS Error**
```
❌ CORS policy blocked
```
**Rozwiązanie:**
```javascript
const cors = require('cors');
app.use(cors());
```

---

## 📚 Dokumentacja

- `INTEGRATION_QUICKSTART.md` - Szybki start
- `APP_INTEGRATION_GUIDE.md` - Pełny przewodnik
- `example_backend_endpoint.js` - Przykłady kodu
- `INTEGRATION_SUMMARY.md` - Podsumowanie

---

## ✅ Checklist

- [ ] Dodałem endpoint `/api/webhook/matches` w aplikacji UI
- [ ] Przetestowałem `python quick_test.py`
- [ ] Edytowałem `test_integration_jakub.bat` (zmienić APP_URL)
- [ ] Uruchomiłem test: `test_integration_jakub.bat`
- [ ] Aplikacja otrzymała dane poprawnie
- [ ] Skonfigurowałem automatyzację (Task Scheduler)

---

## 🎉 Gotowe!

**Teraz masz:**
- ✅ Automatyczny scraping
- ✅ Email notifications
- ✅ Integrację z aplikacją UI
- ✅ Wszystko działa 24/7

**Powodzenia z aplikacją! 🚀**

---

## 💡 Pytania?

1. Zobacz `APP_INTEGRATION_GUIDE.md` - pełna dokumentacja
2. Sprawdź `example_backend_endpoint.js` - przykłady
3. Uruchom `python test_app_integration.py` - advanced tester

**Enjoy! 😊**







