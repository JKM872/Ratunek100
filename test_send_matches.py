"""
Test - wyślij przykładowe mecze do Heroku przez webhook
"""
import requests
import json
from datetime import datetime

# Heroku webhook URL
WEBHOOK_URL = "https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/api/webhook/matches"
API_KEY = "super-secret-key-12345"

# Przykładowe mecze
test_matches = [
    {
        "sport": "Basketball",
        "home_team": "Test Home 1",
        "away_team": "Test Away 1",
        "match_date": "2025-11-08",
        "match_time": "20:00",
        "home_odds": 1.85,
        "away_odds": 2.10,
        "draw_odds": None,
        "home_win_percentage": 65.5,
        "away_win_percentage": 34.5,
        "avg_home_goals": 85.5,
        "avg_away_goals": 78.2,
        "qualifies": 1,
        "created_at": datetime.now().isoformat()
    },
    {
        "sport": "Volleyball",
        "home_team": "Test Volley Home",
        "away_team": "Test Volley Away",
        "match_date": "2025-11-08",
        "match_time": "18:30",
        "home_odds": 1.65,
        "away_odds": 2.35,
        "draw_odds": None,
        "home_win_percentage": 70.0,
        "away_win_percentage": 30.0,
        "avg_home_goals": 3.2,
        "avg_away_goals": 2.8,
        "qualifies": 1,
        "created_at": datetime.now().isoformat()
    },
    {
        "sport": "Handball",
        "home_team": "Test Handball Home",
        "away_team": "Test Handball Away",
        "match_date": "2025-11-08",
        "match_time": "19:00",
        "home_odds": 1.95,
        "away_odds": 2.05,
        "draw_odds": 15.0,
        "home_win_percentage": 60.0,
        "away_win_percentage": 40.0,
        "avg_home_goals": 28.5,
        "avg_away_goals": 26.8,
        "qualifies": 1,
        "created_at": datetime.now().isoformat()
    }
]

payload = {
    "date": "2025-11-08",
    "sport": "Test",
    "matches": test_matches
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("📤 Wysyłam 3 testowe mecze do Heroku...")
print(f"   URL: {WEBHOOK_URL}")
print(f"   Mecze: {len(test_matches)}")

try:
    response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=30)
    
    print(f"\n✅ Response: {response.status_code}")
    print(f"📨 Data: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n🎉 SUCCESS! Sprawdź UI: https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
