"""
Test data generator z avg_goals dla finalnego testu
"""

import requests

# Test matches z avg_goals
test_matches = [
    {
        'sport': 'football',
        'match_date': '2025-11-07',
        'match_time': '20:00',
        'home_team': 'Real Madrid',
        'away_team': 'Barcelona',
        'home_odds': 2.10,
        'away_odds': 3.40,
        'draw_odds': 3.20,
        'home_win_percentage': 45.0,
        'away_win_percentage': 65.0,
        'draw_percentage': 25.0,
        'avg_home_goals': 2.4,  # NOWE!
        'avg_away_goals': 1.8,  # NOWE!
        'qualifies': 1
    },
    {
        'sport': 'basketball',
        'match_date': '2025-11-07',
        'match_time': '21:30',
        'home_team': 'Lakers',
        'away_team': 'Warriors',
        'home_odds': 1.85,
        'away_odds': 2.95,
        'home_win_percentage': 55.0,
        'away_win_percentage': 70.0,
        'avg_home_goals': 108.5,  # NOWE!
        'avg_away_goals': 112.3,  # NOWE!
        'qualifies': 1
    },
    {
        'sport': 'volleyball',
        'match_date': '2025-11-08',
        'match_time': '18:00',
        'home_team': 'Zaksa Kędzierzyn-Koźle',
        'away_team': 'Jastrzębski Węgiel',
        'home_odds': 2.40,
        'away_odds': 1.60,
        'home_win_percentage': 40.0,
        'away_win_percentage': 60.0,
        'avg_home_goals': 3.2,  # Sets
        'avg_away_goals': 3.5,
        'qualifies': 1
    }
]

print('\n📊 Wysyłam 3 nowe mecze z avg_goals...')

response = requests.post(
    'https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/api/webhook/matches',
    json={
        'matches': test_matches,
        'date': '2025-11-07',
        'sport': 'all'
    },
    headers={'Authorization': 'Bearer super-secret-key-12345'}
)

print(f'✅ Response: {response.status_code}')
if response.status_code == 200:
    result = response.json()
    print(f"✅ Saved: {result.get('saved', 0)}/{result.get('total', 0)}")
    print(f"ℹ️  Duplicates: {result.get('duplicates', 0)}")
    print(f"❌ Errors: {result.get('errors', 0)}")
else:
    print(f"❌ Error: {response.text[:200]}")
