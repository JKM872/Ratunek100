"""
Test naprawionego scrapingu H2H
"""

import sys
from livesport_h2h_scraper import start_driver, process_match

def test_h2h_scraping():
    """Testuje czy scraping H2H działa poprawnie"""
    
    print("="*70)
    print("🔧 TEST NAPRAWIONEGO SCRAPINGU H2H")
    print("="*70)
    
    # Uruchom driver
    print("\n🚀 Uruchamiam przeglądarkę...")
    driver = start_driver(headless=False)  # Nie-headless aby móc zobaczyć co się dzieje
    
    try:
        # Testowy URL siatkówki (użyj prawdziwego URLa z Livesport)
        # UWAGA: To przykładowy URL - musisz podać prawdziwy URL meczu
        test_url = input("\nPodaj URL meczu do przetestowania (np. https://www.livesport.com/pl/mecz/...): ")
        
        if not test_url or test_url.strip() == '':
            print("❌ Nie podano URL. Kończę test.")
            return
        
        print(f"\n🔍 Testuję URL: {test_url}")
        print("⏳ Pobieram dane H2H...")
        
        # Przetwórz mecz
        result = process_match(test_url, driver, away_team_focus=False)
        
        # Wyświetl wyniki
        print("\n" + "="*70)
        print("📊 WYNIKI:")
        print("="*70)
        print(f"Gospodarz: {result['home_team']}")
        print(f"Gość: {result['away_team']}")
        print(f"Godzina: {result['match_time']}")
        print(f"\n📈 H2H:")
        print(f"  Znalezionych meczów H2H: {result['h2h_count']}")
        print(f"  Wygrane gospodarzy: {result['home_wins_in_h2h_last5']}")
        print(f"  Wygrane gości: {result['away_wins_in_h2h_last5']}")
        print(f"  Win rate: {result['win_rate']*100:.1f}%")
        
        if result['h2h_last5']:
            print(f"\n📋 Ostatnie 5 meczów H2H:")
            for i, match in enumerate(result['h2h_last5'], 1):
                print(f"  {i}. {match['date']:12} {match['home']:20} {match['score']:8} {match['away']:20}")
        else:
            print(f"\n⚠️  Brak danych H2H!")
            print(f"   Sprawdź plik outputs/debug_no_h2h.html aby zobaczyć HTML strony")
        
        print(f"\n🎯 Kwalifikuje się: {'✅ TAK' if result['qualifies'] else '❌ NIE'}")
        
        if result.get('form_advantage'):
            print(f"🔥 PRZEWAGA FORMY!")
        
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔒 Zamykam przeglądarkę...")
        driver.quit()
        print("✅ Test zakończony!")


if __name__ == '__main__':
    test_h2h_scraping()

