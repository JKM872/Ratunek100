# 🎨 Przewodnik budowania interfejsu z Flashscore API

## 🚀 Quick Start (3 kroki)

### 1️⃣ Uruchom API
```bash
python api_server.py
```

API działa na: `http://localhost:5000`

### 2️⃣ Testuj endpointy
Otwórz w przeglądarce:
```
http://localhost:5000/api/health
```

### 3️⃣ Zbuduj interfejs

---

## 📱 Przykładowy interfejs - React

### **Kompletny przykład aplikacji:**

```jsx
import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = 'http://localhost:5000/api';

function App() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [sport, setSport] = useState('');
  const [sports, setSports] = useState([]);

  // Załaduj dostępne sporty
  useEffect(() => {
    fetch(`${API_BASE}/sports`)
      .then(r => r.json())
      .then(data => setSports(data.sports));
  }, []);

  // Załaduj mecze
  const loadMatches = async () => {
    setLoading(true);
    try {
      let url = `${API_BASE}/matches?date=${date}`;
      if (sport) url += `&sport=${sport}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (response.ok) {
        setMatches(data.matches);
      } else {
        alert(data.error);
      }
    } catch (error) {
      alert('Błąd połączenia: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header>
        <h1>⚽ Kwalifikujące się mecze</h1>
      </header>

      {/* FILTRY */}
      <div className="filters">
        <input 
          type="date" 
          value={date} 
          onChange={(e) => setDate(e.target.value)}
        />
        
        <select value={sport} onChange={(e) => setSport(e.target.value)}>
          <option value="">Wszystkie sporty</option>
          {sports.map(s => (
            <option key={s.id} value={s.id}>
              {s.icon} {s.name}
            </option>
          ))}
        </select>
        
        <button onClick={loadMatches} disabled={loading}>
          {loading ? 'Ładowanie...' : 'Szukaj'}
        </button>
      </div>

      {/* LISTA MECZÓW */}
      <div className="matches">
        {matches.length === 0 && !loading && (
          <p className="empty">Brak meczów. Kliknij "Szukaj"</p>
        )}

        {matches.map((match, i) => (
          <MatchCard key={i} match={match} />
        ))}
      </div>
    </div>
  );
}

// Komponent karty meczu
function MatchCard({ match }) {
  const [details, setDetails] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  const toggleDetails = async () => {
    if (!showDetails && !details) {
      // Załaduj szczegóły
      const response = await fetch(`${API_BASE}/match/${match.id}`);
      const data = await response.json();
      if (response.ok) {
        setDetails(data.match);
      }
    }
    setShowDetails(!showDetails);
  };

  return (
    <div className="match-card">
      {/* NAGŁÓWEK */}
      <div className="match-header" onClick={toggleDetails}>
        <div className="match-teams">
          <strong>{match.home_team}</strong> vs {match.away_team}
        </div>
        <div className="match-time">{match.match_time}</div>
      </div>

      {/* STATYSTYKI PODSTAWOWE */}
      <div className="match-stats">
        {match.is_tennis ? (
          <div className="tennis-stats">
            🎾 Advanced Score: <strong>{match.advanced_score?.toFixed(1)}/100</strong>
            {match.favorite && (
              <span className="favorite"> | Faworytem: {
                match.favorite === 'player_a' ? match.home_team : match.away_team
              }</span>
            )}
          </div>
        ) : (
          <div className="team-stats">
            📊 H2H: <strong>{match.home_wins}/{match.h2h_count}</strong>
            {match.win_rate && ` (${(match.win_rate * 100).toFixed(0)}%)`}
            {match.form_advantage && <span className="advantage"> 🔥 Przewaga formy!</span>}
          </div>
        )}

        {/* KURSY */}
        {match.home_odds && match.away_odds && (
          <div className="odds">
            🎲 Kursy: <span className="odd">{match.home_odds.toFixed(2)}</span> | 
            <span className="odd">{match.away_odds.toFixed(2)}</span>
          </div>
        )}
      </div>

      {/* SZCZEGÓŁY (rozwijane) */}
      {showDetails && details && (
        <div className="match-details">
          {/* FORMA */}
          {details.home_form_overall && (
            <div className="form-section">
              <h4>📊 Forma (ostatnie 5 meczów)</h4>
              <div className="form-row">
                <span>🏠 {details.home_team}:</span>
                <FormDisplay form={details.home_form_overall} />
              </div>
              <div className="form-row">
                <span>✈️ {details.away_team}:</span>
                <FormDisplay form={details.away_form_overall} />
              </div>
            </div>
          )}

          {/* H2H DETAILS */}
          {details.h2h_details && details.h2h_details.length > 0 && (
            <div className="h2h-section">
              <h4>🔄 Ostatnie pojedynki</h4>
              {details.h2h_details.slice(0, 5).map((h2h, i) => (
                <div key={i} className="h2h-item">
                  {h2h.home} vs {h2h.away} - <strong>{h2h.score}</strong>
                </div>
              ))}
            </div>
          )}

          <a href={match.match_url} target="_blank" rel="noopener noreferrer" className="view-link">
            Zobacz na Livesport →
          </a>
        </div>
      )}
    </div>
  );
}

// Wyświetlanie formy (W/L/D)
function FormDisplay({ form }) {
  const emoji = {
    'W': '✅',
    'L': '❌',
    'D': '🟡'
  };
  
  return (
    <div className="form-display">
      {form.map((result, i) => (
        <span key={i} className="form-item">{emoji[result] || result}</span>
      ))}
    </div>
  );
}

export default App;
```

### **CSS (App.css):**

```css
.App {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 10px;
  margin-bottom: 30px;
  text-align: center;
}

header h1 {
  margin: 0;
  font-size: 2em;
}

/* FILTRY */
.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.filters input,
.filters select {
  flex: 1;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
}

.filters button {
  padding: 12px 30px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}

.filters button:hover {
  background: #5568d3;
}

.filters button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* LISTA MECZÓW */
.matches {
  display: grid;
  gap: 20px;
}

.empty {
  text-align: center;
  padding: 60px;
  color: #999;
  font-size: 18px;
}

/* KARTA MECZU */
.match-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.match-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.match-header {
  padding: 20px;
  background: #f8f9fa;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.match-teams {
  font-size: 18px;
  flex: 1;
}

.match-teams strong {
  color: #667eea;
}

.match-time {
  font-size: 14px;
  color: #FF5722;
  font-weight: bold;
  background: #FFE0D8;
  padding: 5px 15px;
  border-radius: 20px;
}

.match-stats {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.tennis-stats,
.team-stats {
  margin-bottom: 10px;
}

.favorite {
  color: #4CAF50;
  font-weight: bold;
}

.advantage {
  color: #FF5722;
  font-weight: bold;
}

.odds {
  font-size: 14px;
  margin-top: 8px;
}

.odd {
  background: #FFD700;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
  margin: 0 5px;
}

/* SZCZEGÓŁY */
.match-details {
  padding: 20px;
  background: #f8f9fa;
  border-top: 2px solid #e0e0e0;
}

.form-section,
.h2h-section {
  margin-bottom: 20px;
}

.form-section h4,
.h2h-section h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 8px 0;
}

.form-display {
  display: flex;
  gap: 5px;
}

.form-item {
  font-size: 20px;
}

.h2h-item {
  padding: 8px;
  background: white;
  border-radius: 5px;
  margin: 5px 0;
  font-size: 14px;
}

.view-link {
  display: inline-block;
  margin-top: 15px;
  padding: 10px 20px;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 5px;
  transition: background 0.3s;
}

.view-link:hover {
  background: #5568d3;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .filters {
    flex-direction: column;
  }
  
  .match-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
```

---

## 🔥 Funkcje do dodania w interfejsie

### 1. **Scraping z poziomu UI**
```jsx
function ScrapingPanel() {
  const [scraping, setScraping] = useState(false);
  const [status, setStatus] = useState(null);

  const startScraping = async () => {
    const response = await fetch(`${API_BASE}/scrape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        date: '2025-10-09',
        sports: ['football', 'tennis']
      })
    });
    
    if (response.ok) {
      setScraping(true);
      pollStatus();
    }
  };

  const pollStatus = () => {
    const interval = setInterval(async () => {
      const response = await fetch(`${API_BASE}/scrape/status`);
      const data = await response.json();
      setStatus(data);
      
      if (!data.is_running) {
        clearInterval(interval);
        setScraping(false);
      }
    }, 3000);
  };

  return (
    <div className="scraping-panel">
      <button onClick={startScraping} disabled={scraping}>
        {scraping ? 'Scrapowanie...' : 'Uruchom scraping'}
      </button>
      
      {status && scraping && (
        <div className="progress">
          <div className="progress-bar" style={{ width: `${status.percent}%` }}>
            {status.percent}%
          </div>
          <p>Kwalifikujących się: {status.qualifying_count}</p>
        </div>
      )}
    </div>
  );
}
```

### 2. **Filtrowanie zaawansowane**
```jsx
function AdvancedFilters({ onFilter }) {
  const [filters, setFilters] = useState({
    minWins: 3,
    minScore: 50, // dla tenisa
    hasOdds: true,
    formAdvantage: false
  });

  return (
    <div className="advanced-filters">
      <label>
        Min. wygranych H2H:
        <input 
          type="number" 
          value={filters.minWins}
          onChange={(e) => setFilters({...filters, minWins: e.target.value})}
        />
      </label>
      
      <label>
        <input 
          type="checkbox"
          checked={filters.hasOdds}
          onChange={(e) => setFilters({...filters, hasOdds: e.target.checked})}
        />
        Tylko z kursami
      </label>
      
      <label>
        <input 
          type="checkbox"
          checked={filters.formAdvantage}
          onChange={(e) => setFilters({...filters, formAdvantage: e.target.checked})}
        />
        Tylko z przewagą formy
      </label>
    </div>
  );
}
```

### 3. **Sortowanie**
```jsx
const [sortBy, setSortBy] = useState('time');

// W URL:
const url = `${API_BASE}/matches?date=${date}&sort=${sortBy}`;

// UI:
<select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
  <option value="time">⏰ Według godziny</option>
  <option value="wins">📊 Według wygranych</option>
  <option value="team">🔤 Alfabetycznie</option>
</select>
```

### 4. **Historia scrapingów**
```jsx
function History() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/history?limit=10`)
      .then(r => r.json())
      .then(data => setHistory(data.history));
  }, []);

  return (
    <div className="history">
      <h3>📜 Historia scrapingów</h3>
      {history.map((item, i) => (
        <div key={i} className="history-item">
          <strong>{item.date}</strong> - 
          {item.qualified_count} kwalifikujących się z {item.total_matches} meczów
          <a href={`${API_BASE}/download/${item.date}`}>⬇️ Pobierz CSV</a>
        </div>
      ))}
    </div>
  );
}
```

---

## 📱 Mobile App (React Native)

```jsx
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';

const API_BASE = 'http://192.168.1.100:5000/api'; // Zmień na swoje IP!

function MatchesScreen() {
  const [matches, setMatches] = useState([]);

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    const response = await fetch(`${API_BASE}/matches?date=2025-10-09&sport=football`);
    const data = await response.json();
    setMatches(data.matches);
  };

  const renderMatch = ({ item }) => (
    <TouchableOpacity style={styles.card}>
      <Text style={styles.teams}>
        {item.home_team} vs {item.away_team}
      </Text>
      <Text style={styles.time}>{item.match_time}</Text>
      <Text style={styles.stats}>
        {item.is_tennis 
          ? `🎾 Score: ${item.advanced_score?.toFixed(1)}/100`
          : `📊 H2H: ${item.home_wins}/${item.h2h_count}`
        }
      </Text>
      {item.home_odds && (
        <Text style={styles.odds}>
          🎲 {item.home_odds.toFixed(2)} | {item.away_odds.toFixed(2)}
        </Text>
      )}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.header}>⚽ Kwalifikujące się mecze</Text>
      <FlatList
        data={matches}
        renderItem={renderMatch}
        keyExtractor={(item, index) => index.toString()}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 15,
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    marginTop: 40,
  },
  card: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  teams: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  time: {
    color: '#FF5722',
    fontWeight: 'bold',
    marginBottom: 5,
  },
  stats: {
    color: '#666',
    marginBottom: 5,
  },
  odds: {
    backgroundColor: '#FFD700',
    padding: 5,
    borderRadius: 5,
    alignSelf: 'flex-start',
  }
});

export default MatchesScreen;
```

---

## 🔧 Deployment API

### **1. Lokalne (LAN)**
API działa na `0.0.0.0:5000` - dostępne z innych urządzeń w sieci:
```
http://[IP_KOMPUTERA]:5000/api/matches
```

### **2. Ngrok (tymczasowy publiczny URL)**
```bash
# Terminal 1
python api_server.py

# Terminal 2
ngrok http 5000
```
Dostaniesz: `https://xyz.ngrok.io`

### **3. Heroku (darmowy hosting)**
Potrzebujesz:
- `requirements.txt`
- `Procfile` z: `web: gunicorn api_server:app`

```bash
heroku create flashscore-api
git push heroku main
```

---

## 💡 Wskazówki

1. **CORS** - już skonfigurowany w API (`flask-cors`)
2. **Rate limiting** - API ma auto-restart co 40 meczów
3. **Checkpointy** - dane są zapisywane co 30 meczów
4. **Filtrowanie** - mecze bez kursów są automatycznie odfiltrowane
5. **Tennis** - rozpoznawany automatycznie po URL (`/tenis/`)

---

## 🎯 Przykładowe use cases

### **Use case 1: Dashboard dzisiejszych meczów**
```
GET /api/matches?date=2025-10-09&sort=time
```

### **Use case 2: Tylko mecze z przewagą formy**
Pobierz wszystkie, filtruj w JS:
```js
const topMatches = matches.filter(m => m.form_advantage);
```

### **Use case 3: Tenis z wysokim scoringiem**
```js
const topTennis = matches.filter(m => m.is_tennis && m.advanced_score >= 60);
```

### **Use case 4: Live scraping z progress barem**
```
POST /api/scrape + polling GET /api/scrape/status
```

---

## 📞 Potrzebujesz pomocy?

Jeśli masz pytania o:
- Konkretny framework (Angular, Vue, Svelte, etc.)
- Mobile (Flutter, Swift, Kotlin)
- Backend integration (Django, Express, ASP.NET)

**Daj znać! Pomogę! 😊**

---

**Powodzenia z budowaniem interfejsu! 🚀**













