"""
Test scrapowania kursów - SPECJALNIE dla problemu z kursami GOŚCI

Ten skrypt pomoże zdiagnozować dlaczego scraper nie znajduje kursu gości
"""

import sys
from livesport_h2h_scraper import start_driver, extract_betting_odds_with_selenium
from bs4 import BeautifulSoup
import time

def test_odds_with_debug(url: str):
    """Testuje scraping kursów z maksymalnym debugowaniem"""
    
    print("="*80)
    print("🔍 TEST SCRAPOWANIA KURSÓW - DEBUG MODE")
    print("="*80)
    print(f"URL: {url}")
    print("\n💡 Ten test pomoże zidentyfikować problem z kursami GOŚCI")
    print()
    
    driver = start_driver(headless=False)  # Widoczna przeglądarka
    
    try:
        print("🌐 Ładuję stronę meczu...")
        driver.get(url)
        time.sleep(5)
        
        # Scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        print("\n" + "="*80)
        print("📊 ROZPOCZYNAM SCRAPING KURSÓW...")
        print("="*80)
        print("\n👀 Obserwuj debug messages poniżej:\n")
        
        # Testuj wydobywanie kursów (teraz z dużo więcej debugowania)
        odds = extract_betting_odds_with_selenium(driver, soup)
        
        print("\n" + "="*80)
        print("📋 WYNIKI:")
        print("="*80)
        print(f"  🏠 Home Odds: {odds['home_odds']}")
        print(f"  ✈️  Away Odds: {odds['away_odds']}")
        print()
        
        # Analiza wyników
        if odds['home_odds'] and odds['away_odds']:
            if odds['home_odds'] == odds['away_odds']:
                print("❌ PROBLEM: Identyczne kursy!")
                print(f"   Scraper znalazł: {odds['home_odds']} dla obu drużyn")
                print()
                print("💡 To wskazuje że:")
                print("   1. Kurs gospodarzy został znaleziony ✓")
                print("   2. Kurs gości NIE został znaleziony ✗")
                print("   3. Scraper użył tego samego kursu dla obu")
                return False
            elif 1.01 <= odds['home_odds'] <= 20.0 and 1.01 <= odds['away_odds'] <= 20.0:
                print("✅ SUKCES! Kursy wyglądają poprawnie")
                print(f"   🏠 Gospodarze: {odds['home_odds']:.2f}")
                print(f"   ✈️  Goście: {odds['away_odds']:.2f}")
                return True
            else:
                print("⚠️  Kursy poza zakresem 1.01-20.00")
                return False
        elif odds['home_odds'] and not odds['away_odds']:
            print("⚠️  CZĘŚCIOWY PROBLEM:")
            print(f"   🏠 Home: {odds['home_odds']:.2f} ✓")
            print(f"   ✈️  Away: BRAK ✗")
            print()
            print("💡 Scraper znalazł kurs gospodarzy ale NIE znalazł kursu gości!")
            print()
            print("Możliwe przyczyny:")
            print("   1. Livesport nie pokazuje kursu gości na stronie H2H")
            print("   2. Kurs gości ma inną strukturę HTML niż oczekiwana")
            print("   3. Kursy są tylko na głównej stronie meczu (nie /h2h/)")
            return False
        else:
            print("❌ Brak kursów na stronie")
            return False
    
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n🔒 Zamykam przeglądarkę za 5 sekund...")
        print("   (Daj czas na przejrzenie strony)")
        time.sleep(5)
        driver.quit()


if __name__ == '__main__':
    print()
    print("="*80)
    print("🎯 TEST KURSÓW GOŚCI - NARZĘDZIE DIAGNOSTYCZNE")
    print("="*80)
    print()
    print("Ten skrypt pomoże zdiagnozować dlaczego kursy gości nie są poprawnie scrapowane.")
    print()
    print("Użycie:")
    print("  python test_away_odds_debug.py <URL_MECZU>")
    print()
    print("Przykład:")
    print("  python test_away_odds_debug.py https://www.livesport.com/pl/koszykowka/...")
    print()
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        print("⚠️  Podaj URL meczu jako argument!")
        print()
        print("Przykład z Twojego emaila (koszykówka):")
        print("  Znajdź mecz Ziraat Bankasi vs Fenerbahce na Livesport")
        print("  Skopiuj URL")
        print("  Uruchom: python test_away_odds_debug.py <URL>")
        print()
        sys.exit(1)
    
    success = test_odds_with_debug(test_url)
    
    print()
    print("="*80)
    if success:
        print("✅ TEST ZAKOŃCZONY SUKCESEM - Kursy są poprawne!")
    else:
        print("⚠️  TEST POKAZAŁ PROBLEM - Zobacz debug messages powyżej")
        print()
        print("📧 Skopiuj output i prześlij aby pomóc w naprawie!")
    print("="*80)
    print()
    
    sys.exit(0 if success else 1)



