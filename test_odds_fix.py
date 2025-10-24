"""
Test naprawionego scrapowania kursów - sprawdza czy kursy są poprawnie wydobywane
"""

import sys
from livesport_h2h_scraper import start_driver, extract_betting_odds_with_selenium
from bs4 import BeautifulSoup
import time

def test_single_match_odds(url: str):
    """Testuje wydobywanie kursów z pojedynczego meczu"""
    
    print("="*70)
    print("🧪 TEST SCRAPOWANIA KURSÓW BUKMACHERSKICH")
    print("="*70)
    print(f"URL: {url}")
    print()
    
    driver = start_driver(headless=False)  # Widoczna przeglądarka dla debugowania
    
    try:
        # Otwórz stronę meczu (nie H2H - tam mogą nie być kursy!)
        print("🌐 Ładuję stronę meczu...")
        driver.get(url)
        time.sleep(5)  # Daj czas na załadowanie
        
        # Scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Testuj wydobywanie kursów
        print("\n📊 Próbuję wydobyć kursy...")
        odds = extract_betting_odds_with_selenium(driver, soup)
        
        print("\n" + "="*70)
        print("📋 WYNIKI:")
        print("="*70)
        print(f"  Home Odds: {odds['home_odds']}")
        print(f"  Away Odds: {odds['away_odds']}")
        print()
        
        if odds['home_odds'] and odds['away_odds']:
            # Sprawdź czy kursy są realistyczne
            if 1.01 <= odds['home_odds'] <= 20.0 and 1.01 <= odds['away_odds'] <= 20.0:
                print("✅ SUKCES! Kursy wyglądają poprawnie")
                print(f"   {odds['home_odds']:.2f} vs {odds['away_odds']:.2f}")
                return True
            else:
                print("❌ BŁĄD! Kursy poza zakresem 1.01-20.00")
                print(f"   Możliwe że to nadal daty lub inne błędne wartości")
                return False
        else:
            print("⚠️  Brak kursów na stronie")
            print()
            print("💡 Możliwe przyczyny:")
            print("   1. Livesport nie pokazuje kursów dla tego meczu")
            print("   2. Kursy są na osobnej zakładce")
            print("   3. Kursy wymagają kliknięcia/interakcji")
            print("   4. Mecz jest za stary/nowy aby mieć kursy")
            
            # DEBUG: Pokaż co znaleźliśmy
            print("\n🔍 DEBUG: Elementy zawierające liczby z formatem X.XX:")
            import re
            all_numbers = re.findall(r'\b(\d+[.,]\d{2})\b', driver.page_source)
            unique_numbers = sorted(set([n.replace(',', '.') for n in all_numbers]))
            print(f"   Znaleziono {len(unique_numbers)} unikalnych liczb:")
            for num in unique_numbers[:20]:  # Pokaż pierwsze 20
                try:
                    val = float(num)
                    if 1.01 <= val <= 20.0:
                        print(f"      ✓ {num} - możliwy kurs")
                    else:
                        print(f"      ✗ {num} - prawdopodobnie data lub inna wartość")
                except:
                    pass
            
            return False
    
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n🔒 Zamykam przeglądarkę...")
        time.sleep(3)  # Daj czas na przejrzenie
        driver.quit()


if __name__ == '__main__':
    # Przykładowy URL meczu (zamień na aktualny)
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        # Domyślny URL testowy - zamień na aktualny mecz z Livesport
        print("⚠️  Użycie: python test_odds_fix.py <URL_MECZU>")
        print()
        print("Przykład:")
        print("  python test_odds_fix.py https://www.livesport.com/pl/pilka-nozna/polska/ekstraklasa/...")
        print()
        test_url = "https://www.livesport.com/pl/pilka-nozna/polska/ekstraklasa/"
        print(f"Używam domyślnego URL: {test_url}")
        print()
    
    success = test_single_match_odds(test_url)
    
    if success:
        print("\n✨ Test zakończony sukcesem!")
        sys.exit(0)
    else:
        print("\n⚠️  Test nie znalazł poprawnych kursów")
        sys.exit(1)

