import sqlite3
import json
import requests

# Load from local database
db = sqlite3.connect('outputs/matches.db')
cursor = db.cursor()
cursor.execute('SELECT * FROM matches')
rows = cursor.fetchall()
cols = [desc[0] for desc in cursor.description]
matches = [dict(zip(cols, row)) for row in rows]
db.close()

print(f'\n📊 Sending {len(matches)} matches to Heroku...')

# Send to Heroku webhook
response = requests.post(
    'https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/api/webhook/matches',
    json={
        'matches': matches,
        'date': '2025-11-04',
        'sport': 'all'
    },
    headers={'Authorization': 'Bearer super-secret-key-12345'}
)

print(f'✅ Response Status: {response.status_code}')

if response.status_code == 200:
    result = response.json()
    print(f"✅ Saved: {result.get('saved', 0)}/{result.get('total', 0)}")
    print(f"❌ Errors: {result.get('errors', 0)}")
    print(f"\n🎉 Data successfully uploaded to Heroku!")
else:
    print(f"❌ Error: {response.text[:200]}")
