"""
Test generowania emaila z informacjami o bukmacherach
"""

import pandas as pd
import json

# Stwórz przykładowe dane CSV z nowymi kolumnami
test_data = {
    'date': ['2025-11-01', '2025-11-01', '2025-11-01'],
    'match_time': ['18:00', '20:00', '22:30'],
    'sport': ['football', 'basketball', 'football'],
    'league': ['Ekstraklasa', 'NBA', 'Premier League'],
    'home_team': ['Legia Warszawa', 'Lakers', 'Manchester City'],
    'away_team': ['Górnik Zabrze', 'Celtics', 'Liverpool'],
    'match_url': [
        'https://www.livesport.com/match/1',
        'https://www.livesport.com/match/2',
        'https://www.livesport.com/match/3'
    ],
    'qualifies': [True, True, True],
    'home_wins_in_h2h_last5': [3, 4, 3],
    'h2h_count': [5, 5, 5],
    'win_rate': [0.60, 0.80, 0.60],
    'form_advantage': [True, False, True],
    'home_form_overall': [['W', 'W', 'L', 'W', 'D'], ['W', 'L', 'W', 'W', 'W'], ['W', 'W', 'W', 'L', 'W']],
    'away_form_overall': [['L', 'L', 'W', 'L', 'L'], ['W', 'W', 'L', 'W', 'L'], ['L', 'W', 'L', 'L', 'D']],
    
    # NOWE KOLUMNY V3
    'home_odds': [1.85, 2.10, 1.65],
    'away_odds': [4.20, 1.80, 5.50],
    'draw_odds': [3.50, None, 3.80],
    'bookmakers_found': ['STS, Fortuna, NordicBet', 'STS, Bet365', 'STS, Fortuna, Superbet, Bet365'],
    'best_home_bookmaker': ['STS', 'STS', 'Bet365'],
    'best_away_bookmaker': ['Fortuna', 'Bet365', 'Superbet'],
    'all_odds': [
        json.dumps({
            'STS': {'home': 1.85, 'away': 4.10, 'draw': 3.40},
            'Fortuna': {'home': 1.82, 'away': 4.20, 'draw': 3.50},
            'NordicBet': {'home': 1.80, 'away': 4.15, 'draw': 3.50}
        }, ensure_ascii=False),
        json.dumps({
            'STS': {'home': 2.10, 'away': 1.75, 'draw': None},
            'Bet365': {'home': 2.05, 'away': 1.80, 'draw': None}
        }, ensure_ascii=False),
        json.dumps({
            'STS': {'home': 1.60, 'away': 5.40, 'draw': 3.80},
            'Fortuna': {'home': 1.62, 'away': 5.30, 'draw': 3.75},
            'Superbet': {'home': 1.63, 'away': 5.50, 'draw': 3.80},
            'Bet365': {'home': 1.65, 'away': 5.45, 'draw': 3.85}
        }, ensure_ascii=False)
    ]
}

# Stwórz DataFrame
df = pd.DataFrame(test_data)

# Zapisz do CSV (tak jak w scraperze)
output_file = 'outputs/test_email_bookmakers.csv'
import os
os.makedirs('outputs', exist_ok=True)
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("✅ Utworzono testowy CSV:", output_file)
print(f"📊 Liczba meczów: {len(df)}")
print()

# Sprawdź czy kolumny są poprawne
print("🔍 KOLUMNY CSV:")
for col in df.columns:
    print(f"   - {col}")
print()

# Sprawdź przykładowe dane
print("📋 PRZYKŁADOWY WIERSZ (mecz #1):")
match = df.iloc[0]
print(f"   Mecz: {match['home_team']} vs {match['away_team']}")
print(f"   Kursy: H={match['home_odds']} ({match['best_home_bookmaker']}) | A={match['away_odds']} ({match['best_away_bookmaker']})")
print(f"   Bukmacherzy: {match['bookmakers_found']}")
print(f"   All odds: {match['all_odds'][:80]}...")
print()

# Test generowania emaila
print("=" * 70)
print("TEST GENEROWANIA EMAILA")
print("=" * 70)

try:
    from email_notifier import create_html_email
    
    # Konwertuj DataFrame na listę słowników (jak w scraperze)
    matches = df.to_dict('records')
    
    # Generuj HTML
    html = create_html_email(matches, '2025-11-01', sort_by='time')
    
    # Zapisz do pliku
    with open('outputs/test_email_bookmakers.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ Email wygenerowany pomyślnie!")
    print("📧 Zapisano do: outputs/test_email_bookmakers.html")
    print()
    
    # Sprawdź czy zawiera informacje o bukmacherach
    checks = [
        ('Źródło kursu gospodarza', 'STS' in html and 'best_home_bookmaker' in str(matches[0])),
        ('Źródło kursu gościa', 'Fortuna' in html or 'Bet365' in html or 'Superbet' in html),
        ('Dropdown z bukmacherami', 'Wszystkie kursy' in html or '<details>' in html),
        ('Gwiazdka przy najlepszym', '★' in html),
        ('Footer o bukmacherach', 'LiveSport API' in html or 'bukmacher' in html.lower())
    ]
    
    print("🧪 SPRAWDZENIE ELEMENTÓW:")
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    print()
    
    # Statystyki HTML
    print("📊 STATYSTYKI HTML:")
    print(f"   Długość: {len(html)} znaków")
    print(f"   Wystąpienia 'STS': {html.count('STS')}")
    print(f"   Wystąpienia '<details>': {html.count('<details>')}")
    print(f"   Wystąpienia '★': {html.count('★')}")
    print()
    
    print("🎉 TEST ZAKOŃCZONY SUKCESEM!")
    print("👉 Otwórz plik outputs/test_email_bookmakers.html w przeglądarce")
    
except Exception as e:
    print(f"❌ BŁĄD: {e}")
    import traceback
    traceback.print_exc()
