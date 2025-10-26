"""
🧪 Test GraphQL API dla Kursów Bukmacherskich

Ten skrypt testuje nowy system pobierania kursów przez LiveSport GraphQL API.
"""

from livesport_odds_api_client import LiveSportOddsAPI, get_odds_for_matches_batch

def test_single_match():
    """Test 1: Pobierz kursy dla pojedynczego meczu"""
    print("="*70)
    print("📝 TEST 1: Pobieranie kursów dla pojedynczego meczu")
    print("="*70)
    
    # Inicjalizuj klienta
    client = LiveSportOddsAPI(bookmaker_id="165", geo_ip_code="PL")
    
    # Przykładowy URL (ZMIEŃ NA AKTUALNY MECZ!)
    # Format: https://www.livesport.com/pl/mecz/sport/team1/team2/?mid=ABC123
    test_url = input("\n📎 Wklej URL meczu z Livesport (lub Enter dla przykładu): ").strip()
    
    if not test_url:
        test_url = "https://www.livesport.com/pl/mecz/pilka-nozna/atalanta-8C9JjMXu/slavia-praga-viXGgnyB/?mid=KQAaF7d2"
        print(f"📎 Używam przykładowego URL: {test_url[:80]}...")
    
    print(f"\n🔍 Pobieram kursy...")
    odds = client.get_odds_from_url(test_url)
    
    if odds:
        print(f"\n✅ SUKCES! Kursy pobrane pomyślnie:")
        print(f"   🏠 Gospodarz: {odds['home_odds']}")
        if odds.get('draw_odds'):
            print(f"   ⚖️  Remis: {odds['draw_odds']}")
        print(f"   ✈️  Gość: {odds['away_odds']}")
        print(f"   📊 Źródło: {odds['bookmaker_name']}")
        print(f"   🔗 API: {odds['source']}")
        print(f"   🆔 Event ID: {odds['event_id']}")
        return True
    else:
        print(f"\n❌ BŁĄD: Nie udało się pobrać kursów")
        print(f"\n💡 Możliwe przyczyny:")
        print(f"   1. URL nie zawiera parametru ?mid= (Event ID)")
        print(f"   2. Mecz nie ma dostępnych kursów w Nordic Bet")
        print(f"   3. Event ID jest nieprawidłowe")
        print(f"   4. Mecz już się skończył/jest bardzo stary")
        
        # Sprawdź czy URL ma ?mid=
        if '?mid=' in test_url or '&mid=' in test_url:
            print(f"\n   ✅ URL zawiera ?mid= - to dobrze")
        else:
            print(f"\n   ❌ URL NIE zawiera ?mid= - to jest problem!")
            print(f"      Przykład poprawnego URL:")
            print(f"      https://www.livesport.com/pl/mecz/.../?mid=ABC123")
        
        return False


def test_batch_matches():
    """Test 2: Pobierz kursy dla wielu meczów"""
    print("\n" + "="*70)
    print("📝 TEST 2: Batch processing (wiele meczów)")
    print("="*70)
    
    print("\n📎 Podaj URL-e meczów (po jednym w linii, Enter 2x aby zakończyć):")
    
    urls = []
    while True:
        url = input(f"   Mecz {len(urls)+1}: ").strip()
        if not url:
            break
        urls.append(url)
    
    if not urls:
        print("\n⚠️  Brak URL-i, pomijam test batch processing")
        return
    
    print(f"\n🔍 Pobieram kursy dla {len(urls)} meczów...")
    
    results = get_odds_for_matches_batch(
        match_urls=urls,
        bookmaker_id="165",
        delay=0.5,
        verbose=True
    )
    
    print(f"\n{'='*70}")
    print(f"✨ PODSUMOWANIE:")
    print(f"   Meczów ogółem: {len(urls)}")
    print(f"   Z kursami: {len(results)}")
    print(f"   Bez kursów: {len(urls) - len(results)}")
    
    if results:
        print(f"\n✅ Mecze z kursami:")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['match_url'][:60]}...")
            print(f"      Home: {result['home_odds']}, Away: {result['away_odds']}")


def test_api_connectivity():
    """Test 3: Sprawdź połączenie z API"""
    print("\n" + "="*70)
    print("📝 TEST 3: Test połączenia z API")
    print("="*70)
    
    try:
        import requests
        
        # Testowy request do API
        api_url = "https://www.livesport.com/req/api/v2/configurator/data"
        
        print(f"\n🔍 Testuję połączenie z {api_url}...")
        
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Połączenie z API działa!")
            print(f"   Status Code: {response.status_code}")
        else:
            print(f"⚠️  Dziwny status code: {response.status_code}")
    
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT - API nie odpowiada (>10s)")
    
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - Brak połączenia z internetem?")
    
    except Exception as e:
        print(f"❌ Błąd: {e}")


def test_event_id_extraction():
    """Test 4: Ekstrakcja Event ID z różnych formatów URL"""
    print("\n" + "="*70)
    print("📝 TEST 4: Ekstrakcja Event ID z URL")
    print("="*70)
    
    client = LiveSportOddsAPI()
    
    test_cases = [
        "https://www.livesport.com/pl/mecz/pilka-nozna/team1/team2/?mid=ABC123",
        "https://www.livesport.com/pl/mecz/koszykowka/team1/team2/?mid=XYZ789&tab=h2h",
        "https://www.livesport.com/pl/mecz/siatkowka/team1/team2/#id/DEF456",
        "https://www.livesport.com/pl/mecz/tenis/player1/player2/",  # Brak ?mid=
    ]
    
    print("\n🔍 Testuję różne formaty URL...")
    
    for i, url in enumerate(test_cases, 1):
        event_id = client.extract_event_id_from_url(url)
        print(f"\n   {i}. URL: {url[:60]}...")
        if event_id:
            print(f"      ✅ Event ID: {event_id}")
        else:
            print(f"      ❌ Nie znaleziono Event ID")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("🎲 TEST GRAPHQL API DLA KURSÓW BUKMACHERSKICH")
    print("="*70)
    print("\nTen skrypt testuje nowy system pobierania kursów.")
    print("Używamy LiveSport GraphQL API + Nordic Bet (bukmacher ID: 165)")
    
    try:
        # Test 1: Pojedynczy mecz
        success = test_single_match()
        
        if success:
            # Test 2: Batch (opcjonalnie)
            response = input("\n❓ Czy chcesz przetestować batch processing? (t/N): ").lower()
            if response == 't':
                test_batch_matches()
            
            # Test 3: API connectivity
            response = input("\n❓ Czy chcesz przetestować połączenie z API? (t/N): ").lower()
            if response == 't':
                test_api_connectivity()
            
            # Test 4: Event ID extraction
            response = input("\n❓ Czy chcesz przetestować ekstrakcję Event ID? (t/N): ").lower()
            if response == 't':
                test_event_id_extraction()
        
        print("\n" + "="*70)
        print("✨ Testy zakończone!")
        print("="*70)
        
        if success:
            print("\n✅ System pobierania kursów działa poprawnie!")
            print("\n📝 Następne kroki:")
            print("   1. Commit i push zmian")
            print("   2. Uruchom scraping na GitHub Actions")
            print("   3. Sprawdź czy kursy pojawiają się w mailach")
        else:
            print("\n⚠️  Wykryto problemy!")
            print("\n📝 Co sprawdzić:")
            print("   1. Czy URL ma parametr ?mid=")
            print("   2. Czy mecz jest aktualny (nie skończony)")
            print("   3. Czy masz połączenie z internetem")
            print("   4. Czy Nordic Bet obsługuje tę ligę")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Przerwano przez użytkownika (Ctrl+C)")
    
    except Exception as e:
        print(f"\n\n❌ Nieoczekiwany błąd: {e}")
        import traceback
        traceback.print_exc()

