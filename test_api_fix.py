"""
Test script dla weryfikacji naprawy błędu API "NoneType is not iterable"

Testuje:
1. Pobieranie kursów z API dla różnych sportów
2. Weryfikuje że nie występują błędy NoneType
3. Sprawdza czy kursy są poprawnie parsowane
"""

import sys
from livesport_odds_api_client import LiveSportOddsAPI

def test_api_none_handling():
    """Test czy API prawidłowo obsługuje None"""
    print("=" * 70)
    print("🧪 TEST 1: Obsługa None w API")
    print("=" * 70)
    
    client = LiveSportOddsAPI()
    
    # Test z nieprawidłowym event_id (powinien zwrócić None bez błędu)
    print("\n1️⃣ Test nieprawidłowego Event ID...")
    result = client.get_odds_for_event("invalid_event_id_12345")
    
    if result is None:
        print("   ✅ API poprawnie zwróciło None dla nieprawidłowego ID")
    else:
        print(f"   ❌ Oczekiwano None, otrzymano: {result}")
        return False
    
    print("\n2️⃣ Test pustego Event ID...")
    result = client.get_odds_for_event("")
    
    if result is None:
        print("   ✅ API poprawnie zwróciło None dla pustego ID")
    else:
        print(f"   ❌ Oczekiwano None, otrzymano: {result}")
        return False
    
    print("\n3️⃣ Test None jako Event ID...")
    result = client.get_odds_for_event(None)
    
    if result is None:
        print("   ✅ API poprawnie zwróciło None dla None ID")
    else:
        print(f"   ❌ Oczekiwano None, otrzymano: {result}")
        return False
    
    return True


def test_real_volleyball_event():
    """Test na prawdziwym wydarzeniu volleyball"""
    print("\n" + "=" * 70)
    print("🧪 TEST 2: Prawdziwe wydarzenie Volleyball")
    print("=" * 70)
    
    client = LiveSportOddsAPI()
    
    # Użyj przykładowego URL z volleyball (jeśli masz)
    # Zastąp to prawdziwym URL z volleyball
    test_url = "https://www.livesport.com/en/match/volleyball/czech-republic/extraliga-men/liberec-zlin/?mid=dAFbWGJe"
    
    print(f"\n🔗 URL: {test_url}")
    print("   Próba pobrania kursów...")
    
    try:
        result = client.get_odds_from_url(test_url)
        
        if result is None:
            print("   ⚠️ Brak kursów dla tego wydarzenia (to jest OK - może nie być dostępne)")
            return True
        
        print(f"\n   ✅ Otrzymano kursy:")
        print(f"      Bukmacher: {result.get('bookmaker_name', 'N/A')}")
        print(f"      Home: {result.get('home_odds', 'N/A')}")
        print(f"      Away: {result.get('away_odds', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ BŁĄD: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_over_under_none_handling():
    """Test O/U API z None"""
    print("\n" + "=" * 70)
    print("🧪 TEST 3: Obsługa None w O/U API")
    print("=" * 70)
    
    client = LiveSportOddsAPI()
    
    print("\n1️⃣ Test O/U dla nieprawidłowego Event ID...")
    result = client.get_over_under_odds("invalid_id", sport="volleyball")
    
    if result is None:
        print("   ✅ O/U API poprawnie zwróciło None")
    else:
        print(f"   ❌ Oczekiwano None, otrzymano: {result}")
        return False
    
    print("\n2️⃣ Test BTTS dla nieprawidłowego Event ID...")
    result = client.get_btts_odds("invalid_id")
    
    if result is None:
        print("   ✅ BTTS API poprawnie zwróciło None")
    else:
        print(f"   ❌ Oczekiwano None, otrzymano: {result}")
        return False
    
    return True


def main():
    """Główna funkcja testowa"""
    print("\n" + "=" * 70)
    print("🚀 START TESTÓW NAPRAWY API")
    print("=" * 70)
    
    results = []
    
    # Test 1: None handling
    try:
        result = test_api_none_handling()
        results.append(("Obsługa None", result))
    except Exception as e:
        print(f"\n❌ Test 1 FAILED z wyjątkiem: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Obsługa None", False))
    
    # Test 2: Real volleyball
    try:
        result = test_real_volleyball_event()
        results.append(("Volleyball Event", result))
    except Exception as e:
        print(f"\n❌ Test 2 FAILED z wyjątkiem: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Volleyball Event", False))
    
    # Test 3: O/U None handling
    try:
        result = test_over_under_none_handling()
        results.append(("O/U None Handling", result))
    except Exception as e:
        print(f"\n❌ Test 3 FAILED z wyjątkiem: {e}")
        import traceback
        traceback.print_exc()
        results.append(("O/U None Handling", False))
    
    # Podsumowanie
    print("\n" + "=" * 70)
    print("📊 PODSUMOWANIE TESTÓW")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Passed: {passed}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 WSZYSTKIE TESTY PRZESZŁY! Naprawa API działa poprawnie.")
        return 0
    else:
        print(f"\n⚠️ {failed} test(ów) nie przeszło. Sprawdź logi powyżej.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
