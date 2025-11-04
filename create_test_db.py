import sqlite3
import os
from datetime import datetime

# Create outputs directory
os.makedirs('outputs', exist_ok=True)

# Connect to database
db = sqlite3.connect('outputs/matches.db')
cursor = db.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sport TEXT,
    match_date TEXT,
    match_time TEXT,
    home_team TEXT,
    away_team TEXT,
    home_odds REAL,
    away_odds REAL,
    draw_odds REAL,
    home_win_percentage REAL,
    draw_percentage REAL,
    away_win_percentage REAL,
    avg_home_goals REAL,
    avg_away_goals REAL,
    qualifies INTEGER,
    created_at TEXT,
    all_odds TEXT,
    bookmaker_name TEXT,
    bookmaker_url TEXT
)
''')

# Insert test data
test_matches = [
    ('football', '2025-11-04', '20:00', 'Manchester United', 'Liverpool', 2.1, 3.5, 3.2, 45, 28, 27, 1.8, 2.1, 1, datetime.now().isoformat(), None, 'NordicBet', None),
    ('football', '2025-11-04', '18:30', 'Arsenal', 'Chelsea', 1.95, 3.4, 4.2, 48, 26, 26, 2.0, 1.7, 1, datetime.now().isoformat(), None, 'Bet365', None),
    ('football', '2025-11-04', '21:00', 'Barcelona', 'Real Madrid', 2.3, 3.1, 3.3, 42, 30, 28, 2.2, 2.0, 1, datetime.now().isoformat(), None, 'Unibet', None),
    ('basketball', '2025-11-04', '19:00', 'Lakers', 'Warriors', 1.85, None, 2.15, 52, None, 48, None, None, 1, datetime.now().isoformat(), None, 'NordicBet', None),
    ('volleyball', '2025-11-04', '17:00', 'Poland', 'Italy', 2.5, None, 1.65, 38, None, 62, None, None, 1, datetime.now().isoformat(), None, 'Bet365', None),
]

cursor.executemany('''
INSERT INTO matches (sport, match_date, match_time, home_team, away_team, 
                    home_odds, away_odds, draw_odds, home_win_percentage, 
                    draw_percentage, away_win_percentage, avg_home_goals, 
                    avg_away_goals, qualifies, created_at, all_odds, 
                    bookmaker_name, bookmaker_url)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', test_matches)

db.commit()
print(f'✅ Test database created with {len(test_matches)} matches')
print(f'📂 Location: outputs/matches.db')

# Verify
cursor.execute('SELECT COUNT(*) FROM matches')
count = cursor.fetchone()[0]
print(f'📊 Total matches in database: {count}')

db.close()
