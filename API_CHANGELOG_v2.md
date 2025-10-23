# 🚀 API Changelog v2.0

## ✨ Nowe funkcje

### 1. **Wsparcie dla TENISA**
- ✅ Advanced scoring (≥50/100 punktów)
- ✅ Multi-factor analysis: H2H + ranking + forma + powierzchnia
- ✅ Automatyczne rozpoznawanie meczów tenisowych po URL
- ✅ Dedykowane pola: `advanced_score`, `favorite`, `ranking_a/b`, `surface`

### 2. **Filtrowanie meczów bez kursów**
- ✅ Automatyczne odfiltrowanie meczów bez `home_odds` i `away_odds`
- ✅ W emailach i API - tylko mecze które możesz znaleźć w zakładach

### 3. **Szczegółowe dane meczów**
- ✅ Forma drużyn/zawodników (3 źródła):
  - `home_form_overall` - forma ogólna gospodarzy
  - `home_form_home` - forma gospodarzy u siebie
  - `away_form_away` - forma gości na wyjeździe
- ✅ Przewaga formy (`form_advantage`)
- ✅ Win rate (`win_rate`)
- ✅ Kursy bukmacherskie (`home_odds`, `away_odds`)

### 4. **Nowe endpointy**

#### `/api/match/<id>` - Pojedynczy mecz
```http
GET /api/match/abc123?date=2025-10-09
```

Zwraca pełne szczegóły meczu:
- Wszystkie statystyki H2H
- Forma (wszystkie źródła)
- Tennis-specific data (jeśli tenis)
- Kursy bukmacherskie
- Historia H2H

#### Zaktualizowany `/api/matches`
- Automatyczne filtrowanie meczów bez kursów
- Rozpoznawanie tenisa (`is_tennis: true/false`)
- Wszystkie szczegółowe dane w odpowiedzi

#### Zaktualizowany `/api/sports`
- Dodano `tennis` z informacją o advanced scoring
- Typ sportu: `team` vs `individual`
- Info o kryteriach kwalifikacji

### 5. **Ulepszony scraping**
- ✅ Auto-wykrywanie tenisa z URL
- ✅ Użycie `process_match_tennis()` dla meczów tenisowych
- ✅ Zachowane wszystkie safety features (auto-restart, checkpointy)

---

## 📊 Porównanie wersji

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Sporty drużynowe | ✅ | ✅ |
| Tenis | ❌ | ✅ |
| Filtrowanie kursów | ❌ | ✅ |
| Forma (3 źródła) | ❌ | ✅ |
| Single match endpoint | ❌ | ✅ |
| Advanced scoring | ❌ | ✅ (tenis) |
| Kursy w API | ❌ | ✅ |

---

## 🔄 Breaking Changes

### ⚠️ BRAK! Wsteczna kompatybilność zachowana

API v2.0 jest w pełni kompatybilne z v1.0:
- Wszystkie stare endpointy działają
- Nowe pola są opcjonalne
- Stare aplikacje będą działać bez zmian

**Jedyna zmiana:** Mecze bez kursów są teraz automatycznie odfiltrowane z `/api/matches`

---

## 📝 Przykłady użycia nowych funkcji

### **1. Pobierz mecze tenisowe**
```javascript
fetch('http://localhost:5000/api/matches?date=2025-10-09&sport=tennis')
  .then(r => r.json())
  .then(data => {
    data.matches.forEach(match => {
      console.log(`${match.home_team} vs ${match.away_team}`);
      console.log(`Score: ${match.advanced_score}/100`);
      console.log(`Favorite: ${match.favorite}`);
    });
  });
```

### **2. Filtruj mecze z wysokim scoringiem (tenis)**
```javascript
const topTennis = matches.filter(m => 
  m.is_tennis && m.advanced_score >= 60
);
```

### **3. Pobierz szczegóły pojedynczego meczu**
```javascript
fetch('http://localhost:5000/api/match/abc123?date=2025-10-09')
  .then(r => r.json())
  .then(data => {
    const match = data.match;
    
    // Wyświetl formę
    console.log('Forma gospodarzy:', match.home_form_overall);
    console.log('Forma gości:', match.away_form_overall);
    
    // Tennis-specific
    if (match.is_tennis) {
      console.log('Ranking A:', match.ranking_a);
      console.log('Ranking B:', match.ranking_b);
      console.log('Surface:', match.surface);
    }
  });
```

### **4. Sprawdź przewagę formy**
```javascript
const advantageMatches = matches.filter(m => m.form_advantage);
console.log(`${advantageMatches.length} meczów z przewagą formy`);
```

---

## 🎯 Response Format (przykład)

### Mecz drużynowy:
```json
{
  "id": "abc123",
  "home_team": "Manchester United",
  "away_team": "Liverpool",
  "match_time": "09.10.2025 15:00",
  "match_url": "https://...",
  "qualifies": true,
  "is_tennis": false,
  "home_wins": 3,
  "h2h_count": 5,
  "win_rate": 0.6,
  "form_advantage": true,
  "home_odds": 2.15,
  "away_odds": 3.40,
  "home_form_overall": ["W", "W", "D", "W", "L"],
  "home_form_home": ["W", "W", "D"],
  "away_form_overall": ["L", "L", "W", "L", "D"],
  "away_form_away": ["L", "L", "D"],
  "h2h_details": [...]
}
```

### Mecz tenisowy:
```json
{
  "id": "xyz789",
  "home_team": "Rafael Nadal",
  "away_team": "Novak Djokovic",
  "match_time": "09.10.2025 18:00",
  "match_url": "https://...",
  "qualifies": true,
  "is_tennis": true,
  "advanced_score": 67.5,
  "favorite": "player_a",
  "ranking_a": 2,
  "ranking_b": 1,
  "surface": "clay",
  "home_odds": 2.80,
  "away_odds": 1.45,
  "home_form_overall": ["W", "W", "W", "L", "W"],
  "away_form_overall": ["W", "L", "W", "W", "W"],
  "h2h_details": [...]
}
```

---

## 🔧 Migracja z v1.0 do v2.0

### **Krok 1: Aktualizuj API**
```bash
git pull
# Lub skopiuj nowy api_server.py
```

### **Krok 2: Brak zmian w kodzie!**
Jeśli używałeś tylko podstawowych pól, wszystko działa tak samo.

### **Krok 3: (Opcjonalnie) Wykorzystaj nowe pola**

**Przed (v1.0):**
```javascript
{
  home_team: "...",
  away_team: "...",
  home_wins: 3,
  qualifies: true
}
```

**Po (v2.0) - wszystko powyżej + dodatkowo:**
```javascript
{
  // ... wszystkie poprzednie pola ...
  is_tennis: false,
  form_advantage: true,
  home_odds: 2.15,
  away_odds: 3.40,
  home_form_overall: ["W", "W", "L"],
  win_rate: 0.6
}
```

---

## 📚 Nowa dokumentacja

- **API_INTERFACE_GUIDE.md** - Kompletny przewodnik budowania interfejsu
- **example_interface.html** - Gotowy przykład HTML/CSS/JS
- **API_EXAMPLES.md** - Zaktualizowane przykłady (React, Vue, Flutter, etc.)

---

## 🐛 Poprawione błędy

1. ✅ Brak wsparcia dla tenisa - NAPRAWIONE
2. ✅ Brak filtrowania po kursach - NAPRAWIONE
3. ✅ Brak szczegółów formy w API - NAPRAWIONE

---

## 🎉 Co dalej?

### **Planowane features (v2.1):**
- 🔮 WebSocket dla real-time updates podczas scrapingu
- 📊 Endpoint `/api/stats` - statystyki ogólne
- 🎯 Endpoint `/api/predictions` - predykcje z ML
- 🔔 Webhook notifications

---

## 📞 Wsparcie

Pytania? Problemy? **Daj znać!** 😊

**API v2.0 - Gotowe do użycia! 🚀**














