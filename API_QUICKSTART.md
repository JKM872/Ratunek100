# ⚡ API QUICK START - 5 minut do działającego API!

## 🎯 **W 3 krokach:**

### **1️⃣ Zainstaluj zależności**
```bash
pip install flask flask-cors
```

### **2️⃣ Uruchom API**
```bash
python api_server.py
```

Zobaczysz:
```
🌐 FLASHSCORE API SERVER
========================================================
🚀 Server uruchomiony!
📍 URL: http://localhost:5000
```

### **3️⃣ Testuj!**

Otwórz przeglądarkę: **http://localhost:5000/api/health**

Zobaczysz:
```json
{
  "status": "OK",
  "timestamp": "2025-10-05T12:00:00",
  "version": "1.0.0"
}
```

**✅ DZIAŁA!** 🎉

---

## 🧪 **TESTY:**

### **Test 1: Health Check**
```bash
curl http://localhost:5000/api/health
```

### **Test 2: Pobierz mecze (jeśli masz dane)**
```bash
curl "http://localhost:5000/api/matches?date=2025-10-05"
```

### **Test 3: Uruchom scraping**
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-10-05", "sports": ["football"], "max_matches": 10}'
```

### **Test 4: Sprawdź status**
```bash
curl http://localhost:5000/api/scrape/status
```

---

## 📱 **TEST W PRZEGLĄDARCE:**

Otwórz w przeglądarce:

1. **Health Check:**  
   `http://localhost:5000/api/health`

2. **Lista sportów:**  
   `http://localhost:5000/api/sports`

3. **Historia:**  
   `http://localhost:5000/api/history`

4. **Mecze:**  
   `http://localhost:5000/api/matches?date=2025-10-05&sport=football&min_wins=3`

---

## 💻 **PRZYKŁAD: JavaScript w przeglądarce**

Otwórz konsolę przeglądarki (F12) i wklej:

```javascript
// Pobierz mecze
fetch('http://localhost:5000/api/matches?date=2025-10-05&sport=football')
  .then(r => r.json())
  .then(data => {
    console.log(`✅ Znaleziono ${data.qualified_count} meczów!`);
    data.matches.forEach(m => {
      console.log(`⚽ ${m.home_team} vs ${m.away_team} (${m.home_wins}/5)`);
    });
  });
```

---

## 🔥 **PRZYKŁAD: Pełny workflow**

```javascript
// 1. Uruchom scraping
fetch('http://localhost:5000/api/scrape', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    date: '2025-10-05',
    sports: ['football'],
    max_matches: 20
  })
})
.then(r => r.json())
.then(data => console.log('✅ Scraping rozpoczęty!', data));

// 2. Sprawdź status (uruchom po 10 sekundach)
setTimeout(() => {
  fetch('http://localhost:5000/api/scrape/status')
    .then(r => r.json())
    .then(status => {
      console.log(`📊 Postęp: ${status.percent}%`);
      console.log(`⚽ Kwalifikujących się: ${status.qualifying_count}`);
    });
}, 10000);

// 3. Po zakończeniu pobierz wyniki
setTimeout(() => {
  fetch('http://localhost:5000/api/matches?date=2025-10-05')
    .then(r => r.json())
    .then(data => {
      console.log(`✅ Gotowe! ${data.qualified_count} meczów`);
    });
}, 30000);
```

---

## 📖 **DOKUMENTACJA:**

### **Wszystkie endpointy:**

| Endpoint | Metoda | Opis |
|----------|--------|------|
| `/api/health` | GET | Status API |
| `/api/matches` | GET | Lista meczów |
| `/api/scrape` | POST | Uruchom scraping |
| `/api/scrape/status` | GET | Status scrapingu |
| `/api/sports` | GET | Dostępne sporty |
| `/api/history` | GET | Historia scrapingów |
| `/api/download/<date>` | GET | Pobierz CSV |

### **Query params dla `/api/matches`:**

| Param | Typ | Domyślnie | Opis |
|-------|-----|-----------|------|
| `date` | string | today | Data (YYYY-MM-DD) |
| `sport` | string | all | Sport (football, basketball, etc.) |
| `min_wins` | int | 2 | Minimum wygranych gospodarzy |
| `limit` | int | all | Limit wyników |
| `sort` | string | time | Sortowanie (time/wins/team) |

### **Body dla `/api/scrape` (JSON):**

```json
{
  "date": "2025-10-05",
  "sports": ["football", "basketball"],
  "max_matches": 100
}
```

---

## 🌍 **DOSTĘP Z INNEGO URZĄDZENIA:**

### **1. Znajdź IP swojego komputera:**

**Windows:**
```bash
ipconfig
```
Szukaj: `IPv4 Address` (np. `192.168.1.100`)

### **2. Użyj IP zamiast localhost:**

```javascript
// Zamiast:
fetch('http://localhost:5000/api/health')

// Użyj:
fetch('http://192.168.1.100:5000/api/health')
```

### **3. Upewnij się że firewall zezwala na port 5000**

---

## 🛠️ **INTEGRACJA Z TWOJĄ APLIKACJĄ:**

### **React:**
Zobacz: `API_EXAMPLES.md` sekcja "JavaScript / React"

### **Flutter:**
Zobacz: `API_EXAMPLES.md` sekcja "Flutter / Dart"

### **React Native:**
Zobacz: `API_EXAMPLES.md` sekcja "React Native"

### **Python:**
Zobacz: `API_EXAMPLES.md` sekcja "Python"

### **.NET / C#:**
Zobacz: `API_EXAMPLES.md` sekcja "C# / .NET"

---

## 🚀 **CO DALEJ?**

1. **✅ API działa lokalnie** → Integruj z swoją aplikacją
2. **🌍 Chcesz API publiczne** → Zobacz sekcję "Deployment" w `API_EXAMPLES.md`
3. **📱 Budujesz mobilną aplikację** → Użyj IP lokalnego lub deploy na Heroku
4. **💻 Budujesz web app** → CORS jest już skonfigurowany, używaj fetch/axios

---

## 🐛 **PROBLEMY?**

### **"Connection refused"**
- ✅ Sprawdź czy API działa: `python api_server.py`
- ✅ Sprawdź port: `http://localhost:5000/api/health`

### **"CORS error" w przeglądarce**
- ✅ API ma już CORS skonfigurowany (flask-cors)
- ✅ Sprawdź czy używasz poprawnego URL

### **"404 Not Found" dla `/api/matches`**
- ✅ Najpierw uruchom scraping: `POST /api/scrape`
- ✅ Lub skopiuj istniejący CSV do folderu `outputs/`

### **API nie widać z telefonu**
- ✅ Użyj IP komputera zamiast `localhost`
- ✅ Sprawdź firewall Windows
- ✅ Upewnij się że telefon jest w tej samej sieci WiFi

---

## 📞 **POMOC:**

Jeśli coś nie działa, daj znać! Chętnie pomogę! 😊

**Powodzenia! 🎉**


