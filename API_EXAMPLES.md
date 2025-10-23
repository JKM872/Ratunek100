# 🌐 FLASHSCORE API - Przykłady użycia

## 📋 Spis treści
1. [Uruchomienie API](#uruchomienie-api)
2. [JavaScript / React / Vue / Angular](#javascript--react--vue--angular)
3. [Python](#python)
4. [Flutter / Dart](#flutter--dart)
5. [React Native](#react-native)
6. [C# / .NET](#c--net)
7. [PHP](#php)
8. [cURL (Terminal)](#curl-terminal)

---

## 🚀 Uruchomienie API

### **Instalacja zależności:**
```bash
pip install flask flask-cors pandas
```

### **Uruchom server:**
```bash
python api_server.py
```

API będzie dostępne pod: `http://localhost:5000`

**💡 Dla zdalnego dostępu:** API działa na `0.0.0.0:5000`, więc możesz się połączyć z innego urządzenia w tej samej sieci lokalnej używając `http://[IP_TWOJEGO_KOMPUTERA]:5000`

---

## 📱 PRZYKŁADY UŻYCIA

### 1. **JavaScript / React / Vue / Angular**

#### **Przykład: React Hook**

```javascript
import { useState, useEffect } from 'react';

// Custom Hook do pobierania meczów
function useMatches(date, sport = null, minWins = 2) {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        setLoading(true);
        
        let url = `http://localhost:5000/api/matches?date=${date}&min_wins=${minWins}`;
        if (sport) url += `&sport=${sport}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (response.ok) {
          setMatches(data.matches);
        } else {
          setError(data.error);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
  }, [date, sport, minWins]);

  return { matches, loading, error };
}

// Komponent React
function MatchList() {
  const today = new Date().toISOString().split('T')[0];
  const { matches, loading, error } = useMatches(today, 'football', 3);

  if (loading) return <div>Ładowanie...</div>;
  if (error) return <div>Błąd: {error}</div>;

  return (
    <div className="match-list">
      <h1>Kwalifikujące się mecze ({matches.length})</h1>
      {matches.map((match, index) => (
        <div key={index} className="match-card">
          <div className="match-time">{match.match_time}</div>
          <div className="match-teams">
            <strong>{match.home_team}</strong> vs {match.away_team}
          </div>
          <div className="match-stats">
            H2H: {match.home_wins}/{match.h2h_count} wygranych gospodarzy
          </div>
          <a href={match.match_url} target="_blank">Zobacz szczegóły</a>
        </div>
      ))}
    </div>
  );
}

// Uruchom scraping
async function startScraping(date, sports = ['football']) {
  const response = await fetch('http://localhost:5000/api/scrape', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ date, sports })
  });
  
  const data = await response.json();
  return data;
}

// Sprawdź status scrapingu
async function checkScrapingStatus() {
  const response = await fetch('http://localhost:5000/api/scrape/status');
  const data = await response.json();
  return data;
}
```

#### **Przykład: Vue 3 Composition API**

```javascript
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const matches = ref([]);
    const loading = ref(true);

    const fetchMatches = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/matches?date=2025-10-05&sport=football');
        const data = await response.json();
        matches.value = data.matches;
      } catch (error) {
        console.error('Błąd:', error);
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchMatches);

    return { matches, loading };
  }
};
```

#### **Przykład: Axios (uniwersalny)**

```javascript
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

// Pobierz mecze
async function getMatches(date, sport = null, minWins = 2) {
  const params = { date, min_wins: minWins };
  if (sport) params.sport = sport;
  
  const response = await axios.get(`${API_BASE}/matches`, { params });
  return response.data;
}

// Uruchom scraping
async function startScraping(date, sports) {
  const response = await axios.post(`${API_BASE}/scrape`, { date, sports });
  return response.data;
}

// Użycie
const matches = await getMatches('2025-10-05', 'football', 3);
console.log(matches);
```

---

### 2. **Python**

#### **Przykład: requests**

```python
import requests
import time

API_BASE = 'http://localhost:5000/api'

# Pobierz mecze
def get_matches(date, sport=None, min_wins=2, limit=None):
    params = {
        'date': date,
        'min_wins': min_wins
    }
    if sport:
        params['sport'] = sport
    if limit:
        params['limit'] = limit
    
    response = requests.get(f'{API_BASE}/matches', params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Błąd: {response.status_code}')
        return None

# Uruchom scraping
def start_scraping(date, sports=['football', 'basketball']):
    data = {
        'date': date,
        'sports': sports
    }
    
    response = requests.post(f'{API_BASE}/scrape', json=data)
    
    if response.status_code == 202:
        print('✅ Scraping rozpoczęty!')
        return response.json()
    else:
        print(f'❌ Błąd: {response.json()}')
        return None

# Sprawdź status scrapingu
def check_scraping_status():
    response = requests.get(f'{API_BASE}/scrape/status')
    return response.json()

# Czekaj na zakończenie scrapingu
def wait_for_scraping(check_interval=5):
    """Czeka aż scraping się zakończy"""
    print('⏳ Czekam na zakończenie scrapingu...')
    
    while True:
        status = check_scraping_status()
        
        if not status['is_running']:
            if status.get('error'):
                print(f'❌ Błąd: {status["error"]}')
            else:
                print(f'✅ Zakończono! Kwalifikujących się: {status["qualifying_count"]}')
            break
        
        progress = status.get('percent', 0)
        current = status.get('current_match', '')[:50]
        print(f'📊 Postęp: {progress}% - {current}...')
        
        time.sleep(check_interval)

# Przykład użycia
if __name__ == '__main__':
    # Uruchom scraping
    start_scraping('2025-10-05', ['football', 'basketball'])
    
    # Czekaj na zakończenie
    wait_for_scraping()
    
    # Pobierz wyniki
    data = get_matches('2025-10-05', sport='football', min_wins=3)
    
    print(f'\n📊 Znaleziono {data["qualified_count"]} meczów:')
    for match in data['matches'][:5]:  # Pokaż 5 pierwszych
        print(f'  ⚽ {match["home_team"]} vs {match["away_team"]} ({match["home_wins"]}/5)')
```

#### **Przykład: Django/Flask integracja**

```python
# views.py (Django) lub routes.py (Flask)
import requests

def matches_view(request):
    """Widok Django pobierający mecze z API"""
    date = request.GET.get('date', '2025-10-05')
    sport = request.GET.get('sport', 'football')
    
    # Pobierz z API
    response = requests.get(
        'http://localhost:5000/api/matches',
        params={'date': date, 'sport': sport, 'min_wins': 3}
    )
    
    if response.status_code == 200:
        data = response.json()
        matches = data['matches']
    else:
        matches = []
    
    return render(request, 'matches.html', {'matches': matches})
```

---

### 3. **Flutter / Dart**

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class FlashscoreAPI {
  static const String baseUrl = 'http://localhost:5000/api';
  
  // Model danych
  static Future<MatchesResponse> getMatches({
    required String date,
    String? sport,
    int minWins = 2,
    int? limit,
  }) async {
    final params = {
      'date': date,
      'min_wins': minWins.toString(),
      if (sport != null) 'sport': sport,
      if (limit != null) 'limit': limit.toString(),
    };
    
    final uri = Uri.parse('$baseUrl/matches').replace(queryParameters: params);
    final response = await http.get(uri);
    
    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return MatchesResponse.fromJson(json);
    } else {
      throw Exception('Failed to load matches');
    }
  }
  
  // Uruchom scraping
  static Future<void> startScraping({
    required String date,
    List<String> sports = const ['football'],
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/scrape'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'date': date,
        'sports': sports,
      }),
    );
    
    if (response.statusCode != 202) {
      throw Exception('Failed to start scraping');
    }
  }
  
  // Sprawdź status
  static Future<ScrapingStatus> getScrapingStatus() async {
    final response = await http.get(Uri.parse('$baseUrl/scrape/status'));
    
    if (response.statusCode == 200) {
      return ScrapingStatus.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load status');
    }
  }
}

// Models
class MatchesResponse {
  final String date;
  final int totalMatches;
  final int qualifiedCount;
  final List<Match> matches;
  
  MatchesResponse({
    required this.date,
    required this.totalMatches,
    required this.qualifiedCount,
    required this.matches,
  });
  
  factory MatchesResponse.fromJson(Map<String, dynamic> json) {
    return MatchesResponse(
      date: json['date'],
      totalMatches: json['total_matches'],
      qualifiedCount: json['qualified_count'],
      matches: (json['matches'] as List)
          .map((m) => Match.fromJson(m))
          .toList(),
    );
  }
}

class Match {
  final String homeTeam;
  final String awayTeam;
  final String matchTime;
  final int homeWins;
  final String matchUrl;
  
  Match({
    required this.homeTeam,
    required this.awayTeam,
    required this.matchTime,
    required this.homeWins,
    required this.matchUrl,
  });
  
  factory Match.fromJson(Map<String, dynamic> json) {
    return Match(
      homeTeam: json['home_team'],
      awayTeam: json['away_team'],
      matchTime: json['match_time'] ?? '',
      homeWins: json['home_wins'],
      matchUrl: json['match_url'],
    );
  }
}

// Widget Flutter
class MatchesScreen extends StatefulWidget {
  @override
  _MatchesScreenState createState() => _MatchesScreenState();
}

class _MatchesScreenState extends State<MatchesScreen> {
  List<Match> matches = [];
  bool loading = true;
  
  @override
  void initState() {
    super.initState();
    loadMatches();
  }
  
  Future<void> loadMatches() async {
    try {
      final response = await FlashscoreAPI.getMatches(
        date: '2025-10-05',
        sport: 'football',
        minWins: 3,
      );
      
      setState(() {
        matches = response.matches;
        loading = false;
      });
    } catch (e) {
      print('Error: $e');
      setState(() => loading = false);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (loading) {
      return Center(child: CircularProgressIndicator());
    }
    
    return ListView.builder(
      itemCount: matches.length,
      itemBuilder: (context, index) {
        final match = matches[index];
        return ListTile(
          title: Text('${match.homeTeam} vs ${match.awayTeam}'),
          subtitle: Text('H2H: ${match.homeWins}/5 wygranych'),
          trailing: Text(match.matchTime),
        );
      },
    );
  }
}
```

---

### 4. **React Native**

```javascript
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, ActivityIndicator } from 'react-native';

const API_BASE = 'http://192.168.1.100:5000/api'; // Zmień na IP Twojego komputera!

function MatchesScreen() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/matches?date=2025-10-05&sport=football&min_wins=3`
      );
      const data = await response.json();
      setMatches(data.matches);
    } catch (error) {
      console.error('Błąd:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <ActivityIndicator size="large" />;
  }

  return (
    <FlatList
      data={matches}
      keyExtractor={(item, index) => index.toString()}
      renderItem={({ item }) => (
        <View style={{ padding: 16, borderBottomWidth: 1 }}>
          <Text style={{ fontSize: 16, fontWeight: 'bold' }}>
            {item.home_team} vs {item.away_team}
          </Text>
          <Text>⏰ {item.match_time}</Text>
          <Text>📊 H2H: {item.home_wins}/5 wygranych gospodarzy</Text>
        </View>
      )}
    />
  );
}

export default MatchesScreen;
```

**💡 WAŻNE dla React Native:** Zmień `localhost` na faktyczny IP komputera w sieci lokalnej (np. `192.168.1.100`)

---

### 5. **C# / .NET**

```csharp
using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.Generic;

public class FlashscoreAPI
{
    private static readonly HttpClient client = new HttpClient();
    private const string API_BASE = "http://localhost:5000/api";

    // Model danych
    public class Match
    {
        public string HomeTeam { get; set; }
        public string AwayTeam { get; set; }
        public string MatchTime { get; set; }
        public int HomeWins { get; set; }
        public string MatchUrl { get; set; }
    }

    public class MatchesResponse
    {
        public string Date { get; set; }
        public int TotalMatches { get; set; }
        public int QualifiedCount { get; set; }
        public List<Match> Matches { get; set; }
    }

    // Pobierz mecze
    public static async Task<MatchesResponse> GetMatches(
        string date, 
        string sport = null, 
        int minWins = 2)
    {
        var url = $"{API_BASE}/matches?date={date}&min_wins={minWins}";
        if (sport != null) url += $"&sport={sport}";

        var response = await client.GetAsync(url);
        response.EnsureSuccessStatusCode();

        var json = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<MatchesResponse>(json);
    }

    // Przykład użycia
    public static async Task Main()
    {
        var data = await GetMatches("2025-10-05", "football", 3);
        
        Console.WriteLine($"Znaleziono {data.QualifiedCount} meczów:");
        foreach (var match in data.Matches)
        {
            Console.WriteLine($"⚽ {match.HomeTeam} vs {match.AwayTeam} ({match.HomeWins}/5)");
        }
    }
}
```

---

### 6. **PHP**

```php
<?php

class FlashscoreAPI {
    private const API_BASE = 'http://localhost:5000/api';
    
    // Pobierz mecze
    public static function getMatches($date, $sport = null, $minWins = 2) {
        $url = self::API_BASE . "/matches?date={$date}&min_wins={$minWins}";
        if ($sport) $url .= "&sport={$sport}";
        
        $response = file_get_contents($url);
        return json_decode($response, true);
    }
    
    // Uruchom scraping
    public static function startScraping($date, $sports = ['football']) {
        $url = self::API_BASE . '/scrape';
        $data = json_encode([
            'date' => $date,
            'sports' => $sports
        ]);
        
        $options = [
            'http' => [
                'method' => 'POST',
                'header' => 'Content-Type: application/json',
                'content' => $data
            ]
        ];
        
        $context = stream_context_create($options);
        $response = file_get_contents($url, false, $context);
        return json_decode($response, true);
    }
}

// Przykład użycia
$data = FlashscoreAPI::getMatches('2025-10-05', 'football', 3);

echo "Znaleziono {$data['qualified_count']} meczów:\n";
foreach ($data['matches'] as $match) {
    echo "⚽ {$match['home_team']} vs {$match['away_team']} ({$match['home_wins']}/5)\n";
}
?>
```

---

### 7. **cURL (Terminal)**

```bash
# Health check
curl http://localhost:5000/api/health

# Pobierz mecze
curl "http://localhost:5000/api/matches?date=2025-10-05&sport=football&min_wins=3"

# Uruchom scraping
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-10-05", "sports": ["football", "basketball"]}'

# Sprawdź status
curl http://localhost:5000/api/scrape/status

# Pobierz dostępne sporty
curl http://localhost:5000/api/sports

# Historia scrapingów
curl http://localhost:5000/api/history

# Pobierz CSV
curl -O http://localhost:5000/api/download/2025-10-05
```

---

## 🔧 **ZAAWANSOWANE UŻYCIE**

### **1. Polling status scrapingu (JavaScript)**

```javascript
async function waitForScraping() {
  return new Promise((resolve) => {
    const intervalId = setInterval(async () => {
      const status = await fetch('http://localhost:5000/api/scrape/status')
        .then(r => r.json());
      
      console.log(`Postęp: ${status.percent}%`);
      
      if (!status.is_running) {
        clearInterval(intervalId);
        resolve(status);
      }
    }, 5000); // Sprawdzaj co 5 sekund
  });
}

// Użycie
await startScraping('2025-10-05', ['football']);
await waitForScraping();
const matches = await getMatches('2025-10-05');
```

### **2. WebSocket dla real-time updates (opcjonalnie)**

Jeśli chcesz real-time updates, możemy dodać WebSocket support do API!

---

## 🌍 **ZDALNE POŁĄCZENIE (z innego urządzenia)**

### **Krok 1: Znajdź IP swojego komputera**

**Windows:**
```bash
ipconfig
```
Szukaj: `IPv4 Address` (np. `192.168.1.100`)

**Mac/Linux:**
```bash
ifconfig
```

### **Krok 2: Zmień URL w aplikacji**

Zamiast `localhost` użyj IP:
```javascript
const API_BASE = 'http://192.168.1.100:5000/api'; // Twoje IP!
```

### **Krok 3: Firewall**

Upewnij się że port 5000 jest otwarty w firewallu Windows.

---

## 🚀 **DEPLOYMENT (produkcja)**

Jeśli chcesz API dostępne publicznie:

### **Opcja 1: Heroku (darmowe)**
```bash
# Install Heroku CLI
heroku create flashscore-api
git push heroku main
```

### **Opcja 2: ngrok (tunelowanie)**
```bash
# Uruchom API lokalnie
python api_server.py

# W innym terminalu
ngrok http 5000
```

Dostaniesz publiczny URL: `https://xyz123.ngrok.io`

---

## 📞 **WSPARCIE**

Jeśli masz pytania lub potrzebujesz pomocy z integracją w konkretnym frameworku, daj znać!

**Powodzenia! 🎉**


