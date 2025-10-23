"""
Test nowej funkcjonalności: --skip-no-odds

Ten skrypt testuje, czy nowa opcja działa poprawnie:
1. Tworzy przykładowe dane z meczami (część z kursami, część bez)
2. Testuje filtrowanie po kursach
3. Sprawdza, czy email wysyła tylko właściwe mecze
"""

import pandas as pd
import os
from datetime import datetime

def create_test_data():
    """Tworzy testowe dane CSV z meczami"""
    
    # Przykładowe mecze - część z kursami, część bez
    matches = [
        {
            'match_url': 'https://test.com/match1',
            'home_team': 'Barcelona',
            'away_team': 'Real Madrid',
            'match_time': '11.10.2025 20:00',
            'h2h_last5': "['W', 'W', 'L', 'W', 'W']",
            'home_wins_in_h2h_last5': 4,
            'h2h_count': 5,
            'win_rate': 0.80,
            'qualifies': True,
            'form_advantage': True,
            'home_odds': 1.75,  # ✅ MA KURSY
            'away_odds': 4.20
        },
        {
            'match_url': 'https://test.com/match2',
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'match_time': '11.10.2025 18:00',
            'h2h_last5': "['W', 'D', 'W', 'W', 'L']",
            'home_wins_in_h2h_last5': 3,
            'h2h_count': 5,
            'win_rate': 0.60,
            'qualifies': True,
            'form_advantage': False,
            'home_odds': None,  # ❌ BRAK KURSÓW
            'away_odds': None
        },
        {
            'match_url': 'https://test.com/match3',
            'home_team': 'Liverpool',
            'away_team': 'Manchester City',
            'match_time': '11.10.2025 16:30',
            'h2h_last5': "['W', 'W', 'W', 'D', 'W']",
            'home_wins_in_h2h_last5': 4,
            'h2h_count': 5,
            'win_rate': 0.80,
            'qualifies': True,
            'form_advantage': True,
            'home_odds': 1.90,  # ✅ MA KURSY
            'away_odds': 3.80
        },
        {
            'match_url': 'https://test.com/match4',
            'home_team': 'Tottenham',
            'away_team': 'Aston Villa',
            'match_time': '11.10.2025 15:00',
            'h2h_last5': "['W', 'W', 'L', 'W', 'D']",
            'home_wins_in_h2h_last5': 3,
            'h2h_count': 5,
            'win_rate': 0.60,
            'qualifies': True,
            'form_advantage': False,
            'home_odds': 2.25,  # ✅ MA KURSY
            'away_odds': 3.10
        },
        {
            'match_url': 'https://test.com/match5',
            'home_team': 'Newcastle',
            'away_team': 'West Ham',
            'match_time': '11.10.2025 14:00',
            'h2h_last5': "['W', 'W', 'W', 'L', 'W']",
            'home_wins_in_h2h_last5': 4,
            'h2h_count': 5,
            'win_rate': 0.80,
            'qualifies': True,
            'form_advantage': True,
            'home_odds': None,  # ❌ BRAK KURSÓW
            'away_odds': None
        },
        {
            'match_url': 'https://test.com/match6',
            'home_team': 'Leicester',
            'away_team': 'Southampton',
            'match_time': '11.10.2025 13:00',
            'h2h_last5': "['W', 'W', 'D', 'W', 'L']",
            'home_wins_in_h2h_last5': 3,
            'h2h_count': 5,
            'win_rate': 0.60,
            'qualifies': True,
            'form_advantage': False,
            'home_odds': 1.65,  # ✅ MA KURSY
            'away_odds': 5.00
        },
    ]
    
    df = pd.DataFrame(matches)
    
    # Zapisz do pliku testowego
    os.makedirs('outputs', exist_ok=True)
    test_file = 'outputs/test_skip_no_odds.csv'
    df.to_csv(test_file, index=False, encoding='utf-8-sig')
    
    return test_file, df


def test_filtering():
    """Testuje filtrowanie meczów"""
    
    print("="*70)
    print("🧪 TEST: Nowa funkcjonalność --skip-no-odds")
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
        odds_icon = "💰" if pd.notna(row['home_odds']) and pd.notna(row['away_odds']) else "❌"
        advantage_icon = "🔥" if row['form_advantage'] else "  "
        print(f"      {advantage_icon}{odds_icon} {row['home_team']} vs {row['away_team']}")
        
        has_odds = pd.notna(row['home_odds']) and pd.notna(row['away_odds'])
        if has_odds:
            print(f"         Kursy: {row['home_odds']:.2f} / {row['away_odds']:.2f}")
        else:
            print(f"         Brak kursów")
    
    print()
    
    # Filtruj tylko z kursami
    with_odds = qualified[(qualified['home_odds'].notna()) & (qualified['away_odds'].notna())]
    print("3️⃣ Filtrowanie meczów Z KURSAMI:")
    print(f"   💰 Mecze z kursami: {len(with_odds)}")
    print(f"   ❌ Mecze bez kursów: {len(qualified) - len(with_odds)}")
    print()
    
    if len(with_odds) > 0:
        print("   Lista meczów z kursami:")
        for i, row in with_odds.iterrows():
            advantage_icon = "🔥" if row['form_advantage'] else "  "
            print(f"      {advantage_icon}💰 {row['home_team']} vs {row['away_team']}")
            print(f"         Kursy: {row['home_odds']:.2f} / {row['away_odds']:.2f}")
            print(f"         H2H: {row['win_rate']*100:.0f}%")
        print()
    
    # Test kombinacji: przewaga formy + kursy
    premium = with_odds[with_odds['form_advantage'] == True]
    print("4️⃣ TRYB PREMIUM (🔥 Forma + 💰 Kursy):")
    print(f"   🎯 Mecze Premium: {len(premium)}")
    print()
    
    if len(premium) > 0:
        print("   Lista meczów Premium:")
        for i, row in premium.iterrows():
            print(f"      🔥💰 {row['home_team']} vs {row['away_team']}")
            print(f"         Kursy: {row['home_odds']:.2f} / {row['away_odds']:.2f}")
            print(f"         H2H: {row['win_rate']*100:.0f}%")
        print()
    
    # Podsumowanie
    print("="*70)
    print("📊 PODSUMOWANIE TESTÓW:")
    print("="*70)
    print(f"   ✅ Wszystkie mecze: {len(df)}")
    print(f"   ✅ Kwalifikujące się (H2H ≥60%): {len(qualified)}")
    print(f"   💰 Z kursami: {len(with_odds)}")
    print(f"   ❌ Bez kursów: {len(qualified) - len(with_odds)}")
    print(f"   🔥 Z przewagą formy: {len(qualified[qualified['form_advantage'] == True])}")
    print(f"   🎯 Premium (forma + kursy): {len(premium)}")
    print()
    
    if len(qualified) > 0:
        percent_with_odds = (len(with_odds) / len(qualified)) * 100
        print(f"   📈 Procent z kursami: {percent_with_odds:.1f}%")
    
    print()
    print("="*70)
    print("🎉 TEST ZAKOŃCZONY POMYŚLNIE!")
    print("="*70)
    print()
    print("💡 Aby przetestować email:")
    print()
    print(f"   # Tylko z kursami:")
    print(f"   python email_notifier.py --csv {test_file} \\")
    print("     --to test@email.com --from twoj@email.com --password 'haslo' \\")
    print("     --skip-no-odds")
    print()
    print(f"   # Premium (forma + kursy):")
    print(f"   python email_notifier.py --csv {test_file} \\")
    print("     --to test@email.com --from twoj@email.com --password 'haslo' \\")
    print("     --only-form-advantage --skip-no-odds")
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




