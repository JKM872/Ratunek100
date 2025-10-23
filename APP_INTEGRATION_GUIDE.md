# 🔗 Przewodnik Integracji z Aplikacją UI

## 📋 Spis treści
1. [Szybki Start](#szybki-start)
2. [Metody Integracji](#metody-integracji)
3. [Konfiguracja](#konfiguracja)
4. [Endpoint w Twojej Aplikacji](#endpoint-w-twojej-aplikacji)
5. [Przykłady](#przykłady)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Szybki Start

### **Krok 1: Dodaj endpoint w Twojej aplikacji UI**

**Node.js/Express:**
```javascript
// backend/routes/webhooks.js
app.post('/api/webhook/matches', (req, res) => {
  const { date, sport, matches, qualified_count } = req.body;
  
  console.log(`✅ Otrzymano ${matches.length} meczów (${sport})`);
  
  // Zapisz do bazy danych lub zaktualizuj state
  db.saveMatches(matches);
  
  // Powiadom klientów przez WebSocket (opcjonalne)
  io.emit('matches-updated', { date, sport, matches });
  
  res.json({ status: 'success', received: matches.length });
});
```

**Python/FastAPI:**
```python
@app.post("/api/webhook/matches")
async def receive_matches(data: dict):
    matches = data.get('matches', [])
    sport = data.get('sport')
    
    print(f"✅ Otrzymano {len(matches)} meczów ({sport})")
    
    # Zapisz do bazy
    await db.save_matches(matches)
    
    return {"status": "success", "received": len(matches)}
```

### **Krok 2: Uruchom scraper z integracją**

**Opcja A: Przez parametry CLI:**
```bash
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to twoj@email.com \
  --from-email twoj@email.com \
  --password "haslo" \
  --headless \
  --app-url http://localhost:3000
```

**Opcja B: Przez plik konfiguracyjny:**
```bash
# 1. Skopiuj przykładowy plik
cp app_integration_config.example.json app_integration_config.json

# 2. Edytuj konfigurację
nano app_integration_config.json

# 3. Uruchom scraper (automatycznie użyje konfiguracji)
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to twoj@email.com \
  --from-email twoj@email.com \
  --password "haslo" \
  --headless
```

---

## 🎯 Metody Integracji

### **Metoda 1: Webhook (ZALECANA) ⭐**
Scraper wysyła dane do Twojej aplikacji po zakończeniu.

**Zalety:**
- ✅ Automatyczne powiadomienia
- ✅ Dane zawsze aktualne
- ✅ Proste do implementacji

**Wady:**
- ❌ Wymaga publicznego URL (lub ngrok dla lokalnego testu)

### **Metoda 2: API Polling**
Aplikacja odpytuje moje API co X minut.

**Zalety:**
- ✅ Już zaimplementowane w `api_server.py`
- ✅ Proste dla aplikacji UI

**Wady:**
- ❌ Opóźnienia w aktualizacji
- ❌ Więcej requestów

### **Metoda 3: Shared Database**
Obie aplikacje używają tej samej bazy danych.

**Zalety:**
- ✅ Najbardziej niezawodne
- ✅ Real-time

**Wady:**
- ❌ Wymaga konfiguracji bazy

---

## ⚙️ Konfiguracja

### **Plik `app_integration_config.json`:**

```json
{
  "app_url": "http://localhost:3000",
  "api_key": "optional-secret-key",
  "endpoints": {
    "matches": "/api/webhook/matches",
    "progress": "/api/webhook/progress"
  },
  "enabled": true
}
```

**Parametry:**
- `app_url` - URL Twojej aplikacji (bez końcowego `/`)
- `api_key` - Opcjonalny klucz API dla bezpieczeństwa
- `endpoints.matches` - Endpoint do odbierania meczów
- `endpoints.progress` - Endpoint do odbierania postępu (opcjonalne)
- `enabled` - Włącz/wyłącz automatyczne wysyłanie

---

## 📡 Endpoint w Twojej Aplikacji

### **Format danych wysyłanych przez scraper:**

```json
{
  "date": "2025-10-11",
  "sport": "football",
  "matches": [
    {
      "match_url": "https://www.livesport.com/pl/pilka-nozna/...",
      "home_team": "Real Madrid",
      "away_team": "Barcelona",
      "match_time": "20:00",
      "h2h_last5": ["W", "W", "L", "W", "D"],
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
  "timestamp": "2025-10-11T10:30:00",
  "source": "flashscore_scraper"
}
```

### **Implementacja endpointu:**

**React + Express (Full Stack):**

```javascript
// Backend (Express)
const express = require('express');
const app = express();

app.post('/api/webhook/matches', (req, res) => {
  const { date, sport, matches, qualified_count } = req.body;
  
  // Walidacja
  if (!matches || !Array.isArray(matches)) {
    return res.status(400).json({ error: 'Invalid data' });
  }
  
  // Zapisz do bazy
  db.collection('matches').insertMany(matches);
  
  // Powiadom frontend przez WebSocket
  io.emit('new-matches', { date, sport, count: qualified_count });
  
  res.json({ 
    status: 'success', 
    received: matches.length,
    message: `Zapisano ${qualified_count} kwalifikujących się meczów`
  });
});

// Frontend (React)
import { useEffect, useState } from 'react';
import io from 'socket.io-client';

function MatchesList() {
  const [matches, setMatches] = useState([]);
  
  useEffect(() => {
    // WebSocket connection
    const socket = io('http://localhost:3000');
    
    socket.on('new-matches', (data) => {
      console.log(`✅ Nowe mecze: ${data.count} (${data.sport})`);
      fetchMatches(data.date); // Odśwież listę
    });
    
    return () => socket.disconnect();
  }, []);
  
  async function fetchMatches(date) {
    const response = await fetch(`/api/matches?date=${date}`);
    const data = await response.json();
    setMatches(data.matches);
  }
  
  return (
    <div>
      {matches.map(match => (
        <MatchCard key={match.match_url} {...match} />
      ))}
    </div>
  );
}
```

**Next.js API Route:**

```typescript
// app/api/webhook/matches/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const data = await request.json();
  
  const { date, sport, matches, qualified_count } = data;
  
  // Zapisz do bazy danych
  await prisma.match.createMany({
    data: matches.map(m => ({
      url: m.match_url,
      homeTeam: m.home_team,
      awayTeam: m.away_team,
      matchTime: m.match_time,
      homeWins: m.home_wins_in_h2h_last5,
      qualifies: m.qualifies,
      sport: sport,
      date: new Date(date)
    }))
  });
  
  // Revalidate cache
  revalidatePath('/matches');
  
  return NextResponse.json({ 
    success: true, 
    count: qualified_count 
  });
}
```

---

## 💻 Przykłady Użycia

### **1. Podstawowa integracja (lokalnie):**

```bash
# Aplikacja UI działa na localhost:3000
# Scraper wysyła dane automatycznie

python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football \
  --to email@example.com \
  --from-email email@example.com \
  --password "password" \
  --headless \
  --app-url http://localhost:3000
```

### **2. Integracja z API Key (produkcja):**

```bash
python scrape_and_notify.py \
  --date 2025-10-11 \
  --sports football basketball \
  --to email@example.com \
  --from-email email@example.com \
  --password "password" \
  --headless \
  --app-url https://twoja-app.com \
  --app-api-key "secret-api-key-12345"
```

### **3. Test połączenia:**

```python
# test_integration.py
from app_integrator import AppIntegrator

# Utwórz integrator
integrator = AppIntegrator(
    app_url='http://localhost:3000',
    api_key='optional-key'
)

# Test połączenia
if integrator.test_connection():
    print("✅ Połączenie działa!")
    
    # Test wysyłania danych
    test_matches = [{
        'match_url': 'test',
        'home_team': 'Team A',
        'away_team': 'Team B',
        'qualifies': True
    }]
    
    integrator.send_matches(test_matches, '2025-10-11', 'football')
else:
    print("❌ Nie można połączyć się z aplikacją")
```

### **4. Użycie w Python code:**

```python
from app_integrator import AppIntegrator
import pandas as pd

# Wczytaj dane z CSV
df = pd.read_csv('outputs/livesport_h2h_2025-10-11_football_EMAIL.csv')
matches = df.to_dict('records')

# Wyślij do aplikacji
integrator = AppIntegrator('http://localhost:3000')
success = integrator.send_matches(matches, '2025-10-11', 'football')

if success:
    print("✅ Dane wysłane pomyślnie!")
```

---

## 🌍 Deployment (produkcja)

### **Opcja 1: Ngrok (dla testów lokalnych):**

```bash
# Terminal 1: Uruchom aplikację UI
npm start  # localhost:3000

# Terminal 2: Uruchom ngrok
ngrok http 3000
# Otrzymasz: https://abc123.ngrok.io

# Terminal 3: Użyj URL ngrok w scraperze
python scrape_and_notify.py \
  --app-url https://abc123.ngrok.io \
  ...
```

### **Opcja 2: Railway/Render (produkcja):**

```bash
# Aplikacja UI na Railway: https://twoja-app.railway.app

python scrape_and_notify.py \
  --app-url https://twoja-app.railway.app \
  --app-api-key $SECRET_KEY \
  ...
```

---

## 🐛 Troubleshooting

### **Problem 1: "Connection refused"**

```
❌ Błąd połączenia! Sprawdź czy aplikacja działa pod adresem: http://localhost:3000
```

**Rozwiązanie:**
1. Sprawdź czy Twoja aplikacja UI działa: `curl http://localhost:3000`
2. Sprawdź firewall
3. Użyj `http://127.0.0.1:3000` zamiast `localhost`

### **Problem 2: "404 Not Found"**

```
❌ Błąd! Status: 404
```

**Rozwiązanie:**
- Sprawdź czy endpoint istnieje: `/api/webhook/matches`
- Sprawdź routing w aplikacji UI
- Sprawdź logi backendu

### **Problem 3: "CORS Error"**

```
❌ CORS policy blocked
```

**Rozwiązanie w aplikacji UI:**
```javascript
// Express
const cors = require('cors');
app.use(cors());

// Next.js API route
export async function POST(request) {
  const response = NextResponse.json({ success: true });
  response.headers.set('Access-Control-Allow-Origin', '*');
  return response;
}
```

### **Problem 4: "API Key invalid"**

```
❌ Błąd! Status: 401
```

**Rozwiązanie:**
- Sprawdź czy API key jest poprawny
- Sprawdź format: `Authorization: Bearer YOUR_KEY`

---

## 📚 Dokumentacja API

### **Endpoint: POST /api/webhook/matches**

**Request:**
```json
{
  "date": "2025-10-11",
  "sport": "football",
  "matches": [...],
  "qualified_count": 15,
  "total_count": 150
}
```

**Response (success):**
```json
{
  "status": "success",
  "received": 15,
  "message": "Zapisano mecze"
}
```

**Response (error):**
```json
{
  "status": "error",
  "message": "Invalid data"
}
```

---

## 🎉 Gotowe!

Twój scraper jest teraz połączony z aplikacją UI! 

**Co dalej?**
1. ✅ Dodaj więcej endpointów (np. `/progress` dla real-time updates)
2. ✅ Dodaj WebSocket dla live updates
3. ✅ Dodaj dashboard analytics
4. ✅ Ustaw automatyczne scraping przez Task Scheduler/Cron

**Masz pytania?** Zobacz dokumentację lub napisz! 🚀







