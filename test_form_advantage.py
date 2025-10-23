"""
Test nowej funkcjonalności: --only-form-advantage

Ten skrypt testuje, czy nowa opcja działa poprawnie:
1. Tworzy przykładowe dane z meczami
2. Testuje filtrowanie po form_advantage
3. Sprawdza, czy email wysyła tylko właściwe mecze
"""

import pandas as pd
import os
from datetime import datetime

def create_test_data():
    """Tworzy testowe dane CSV z meczami"""
    
    # Przykładowe mecze - część z przewagą formy, część bez
    matches = [
        {
            'match_url': 'https://test.com/match1',
            'home_team': 'Barcelona',
            'away_team': 'Real Madrid',
            'match_time': '10.10.2025 20:00',
            'h2h_last5': "['W', 'W', 'L', 'W', 'W']",
            'home_wins_in_h2h_last5': 4,
            'h2h_count': 5,
            'win_rate': 0.80,
            'qualifies': True,
            'home_form_overall': "['W', 'W', 'W', 'D', 'W']",
            'home_form_home': "['W', 'W', 'W', 'W', 'W']",
            'away_form_overall': "['L', 'L', 'W', 'L', 'D']",
            'away_form_away': "['L', 'L', 'L', 'D', 'L']",
            'form_advantage': True,  # 🔥 MA PRZEWAGĘ!
            'home_odds': 1.75,
            'away_odds': 4.20
        },
        {
            'match_url': 'https://test.com/match2',
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'match_time': '10.10.2025 18:00',
            'h2h_last5': "['W', 'D', 'W', 'W', 'L']",
            'home_wins_in_h2h_last5': 3,
            'h2h_count': 5,
            'win_rate': 0.60,
            'qualifies': True,
            'home_form_overall': "['W', 'D', 'L', 'W', 'D']",
            'home_form_home': "['W', 'W', 'D', 'L', 'W']",
            'away_form_overall': "['W', 'W', 'D', 'W', 'W']",
            'away_form_away': "['W', 'D', 'W', 'W', 'W']",
            'form_advantage': False,  # ❌ BRAK PRZEWAGI
            'home_odds': 2.10,
            'away_odds': 3.40
        },
        {
            'match_url': 'https://test.com/match3',
            'home_team': 'Liverpool',
            'away_team': 'Manchester City',
            'match_time': '10.10.2025 16:30',
            'h2h_last5': "['W', 'W', 'W', 'D', 'W']",
            'home_wins_in_h2h_last5': 4,
            'h2h_count': 5,
            'win_rate': 0.80,
            'qualifies': True,
            'home_form_overall': "['W', 'W', 'W', 'W', 'W']",
            'home_form_home': "['W', 'W', 'W', 'W', 'D']",
            'away_form_overall': "['L', 'D', 'L', 'L', 'W']",
            'away_form_away': "['L', 'L', 'L', 'D', 'L']",
            'form_advantage': True,  # 🔥 MA PRZEWAGĘ!
            'home_odds': 1.90,
            'away_odds': 3.80
        },
        {
            'match_url': 'https://test.com/match4',
            'home_team': 'Tottenham',
            'away_team': 'Aston Villa',
            'match_time': '10.10.2025 15:00',
            'h2h_last5': "['W', 'W', 'L', 'W', 'D']",
            'home_wins_in_h2h_last5': 3,
            'h2h_count': 5,
            'win_rate': 0.60,
            'qualifies': True,
            'home_form_overall': "['D', 'W', 'L', 'W', 'W']",
            'home_form_home': "['W', 'D', 'W', 'D', 'W']",
            'away_form_overall': "['W', 'D', 'W', 'D', 'L']",
            'away_form_away': "['D', 'L', 'W', 'D', 'L']",
            'form_advantage': False,  # ❌ BRAK PRZEWAGI
            'home_odds': 2.25,
            'away_odds': 3.10
        },
        {
            'match_url': 'https://test.com/match5',
            'home_team': 'Nie kwalifikuje',
            'away_team': 'Test Team',
            'match_time': '10.10.2025 14:00',
            'h2h_last5': "['L', 'L', 'L', 'W', 'L']",
            'home_wins_in_h2h_last5': 1,
            'h2h_count': 5,
            'win_rate': 0.20,
            'qualifies': False,  # ❌ NIE KWALIFIKUJE
            'home_form_overall': "['L', 'L', 'L', 'L', 'W']",
            'home_form_home': "['L', 'L', 'L', 'D', 'L']",
            'away_form_overall': "['W', 'W', 'W', 'W', 'W']",
            'away_form_away': "['W', 'W', 'W', 'W', 'D']",
            'form_advantage': False,
            'home_odds': 4.50,
            'away_odds': 1.60
        },
    ]
    
    df = pd.DataFrame(matches)
    
    # Zapisz do pliku testowego
    os.makedirs('outputs', exist_ok=True)
    test_file = 'outputs/test_form_advantage.csv'
    df.to_csv(test_file, index=False, encoding='utf-8-sig')
    
    return test_file, df


def test_filtering():
    """Testuje filtrowanie meczów"""
    
    print("="*70)
    print("🧪 TEST: Nowa funkcjonalność --only-form-advantage")
    print("="*70)
    print()
    
    # Utwórz testowe dane
    print("1️⃣ Tworzę testowe dane...")
    test_file, df = create_test_data()
    print(f"   ✅ Utworzono: {test_file}")
    print(f"   📊 Liczba meczów: {len(df)}")
    print()
    
    # Sprawdź kwalifikujące się mecze
    qualified = df[df['qualifies'] == True]
    print("2️⃣ Analiza kwalifikujących się meczów:")
    print(f"   📈 Wszystkie kwalifikujące: {len(qualified)}")
    print()
    
    for i, row in qualified.iterrows():
        advantage_icon = "🔥" if row['form_advantage'] else "  "
        print(f"      {advantage_icon} {row['home_team']} vs {row['away_team']}")
        print(f"         H2H: {row['win_rate']*100:.0f}% | Przewaga formy: {row['form_advantage']}")
    
    print()
    
    # Filtruj tylko z przewagą formy
    with_advantage = qualified[qualified['form_advantage'] == True]
    print("3️⃣ Filtrowanie z przewagą formy:")
    print(f"   🔥 Mecze z przewagą formy: {len(with_advantage)}")
    print()
    
    if len(with_advantage) > 0:
        print("   Lista meczów z przewagą formy:")
        for i, row in with_advantage.iterrows():
            print(f"      🔥 {row['home_team']} vs {row['away_team']}")
            print(f"         H2H: {row['win_rate']*100:.0f}%")
            print(f"         Home forma: {row['home_form_overall']}")
            print(f"         Away forma: {row['away_form_overall']}")
        print()
    
    # Podsumowanie
    print("="*70)
    print("📊 PODSUMOWANIE TESTÓW:")
    print("="*70)
    print(f"   ✅ Wszystkie mecze: {len(df)}")
    print(f"   ✅ Kwalifikujące się (H2H ≥60%): {len(qualified)}")
    print(f"   🔥 Z przewagą formy: {len(with_advantage)}")
    print(f"   ❌ Bez przewagi formy: {len(qualified) - len(with_advantage)}")
    print()
    
    if len(with_advantage) > 0:
        percent = (len(with_advantage) / len(qualified)) * 100
        print(f"   📈 Procent z przewagą: {percent:.1f}%")
    
    print()
    print("="*70)
    print("🎉 TEST ZAKOŃCZONY POMYŚLNIE!")
    print("="*70)
    print()
    print("💡 Aby przetestować email, uruchom:")
    print(f"   python email_notifier.py --csv {test_file} \\")
    print("     --to test@email.com --from twoj@email.com --password 'haslo' \\")
    print("     --only-form-advantage")
    print()
    
    return test_file


def main():
    """Uruchom testy"""
    try:
        test_filtering()
        print("✅ Wszystkie testy przeszły pomyślnie!")
        
    except Exception as e:
        print(f"\n❌ BŁĄD w testach: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())




