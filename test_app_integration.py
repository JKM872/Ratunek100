"""
🧪 TEST INTEGRACJI Z APLIKACJĄ UI
==================================

Prosty skrypt do testowania połączenia z aplikacją UI
"""

from app_integrator import AppIntegrator
import sys

def test_integration():
    """Test połączenia i wysyłania danych"""
    
    print("="*60)
    print("🧪 TEST INTEGRACJI Z APLIKACJĄ UI")
    print("="*60)
    
    # Pobierz URL od użytkownika
    app_url = input("\n📍 Podaj URL aplikacji (np. http://localhost:3000): ").strip()
    
    if not app_url:
        print("❌ URL nie może być pusty!")
        return False
    
    # Opcjonalnie API key
    api_key = input("🔑 Podaj API key (lub Enter aby pominąć): ").strip()
    if not api_key:
        api_key = None
    
    print(f"\n🔗 Testuję połączenie z: {app_url}")
    print("-"*60)
    
    # Utwórz integrator
    integrator = AppIntegrator(app_url=app_url, api_key=api_key)
    
    # TEST 1: Połączenie
    print("\n📡 TEST 1: Sprawdzam połączenie...")
    if not integrator.test_connection():
        print("❌ Nie można połączyć się z aplikacją!")
        print("\n💡 Sprawdź:")
        print("   1. Czy aplikacja działa?")
        print("   2. Czy URL jest poprawny?")
        print("   3. Czy firewall nie blokuje połączenia?")
        return False
    
    print("✅ Połączenie działa!")
    
    # TEST 2: Wysyłanie testowych danych
    print("\n📤 TEST 2: Wysyłam testowe dane...")
    
    test_matches = [
        {
            'match_url': 'https://www.livesport.com/pl/pilka-nozna/test/123',
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'match_time': '20:00',
            'h2h_last5': ['W', 'W', 'L', 'W', 'D'],
            'home_wins_in_h2h_last5': 3,
            'h2h_count': 5,
            'qualifies': True,
            'home_odds': 2.10,
            'away_odds': 3.50,
            'win_rate': 0.60
        },
        {
            'match_url': 'https://www.livesport.com/pl/pilka-nozna/test/456',
            'home_team': 'Liverpool',
            'away_team': 'Manchester City',
            'match_time': '18:30',
            'h2h_last5': ['W', 'W', 'W', 'L', 'W'],
            'home_wins_in_h2h_last5': 4,
            'h2h_count': 5,
            'qualifies': True,
            'home_odds': 2.50,
            'away_odds': 2.80,
            'win_rate': 0.80
        }
    ]
    
    success = integrator.send_matches(
        matches=test_matches,
        date='2025-10-11',
        sport='football_test'
    )
    
    if success:
        print("✅ Dane wysłane pomyślnie!")
    else:
        print("❌ Nie udało się wysłać danych!")
        print("\n💡 Sprawdź:")
        print("   1. Czy endpoint /api/webhook/matches istnieje?")
        print("   2. Czy aplikacja akceptuje POST requesty?")
        print("   3. Sprawdź logi aplikacji UI")
        return False
    
    # PODSUMOWANIE
    print("\n" + "="*60)
    print("✅ WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE!")
    print("="*60)
    print("\n🎉 Integracja działa poprawnie!")
    print("\n📝 Następne kroki:")
    print("   1. Uruchom scraper z parametrem --app-url")
    print("   2. Lub utwórz plik app_integration_config.json")
    print("   3. Dane będą automatycznie wysyłane do Twojej aplikacji")
    
    return True


def test_from_csv():
    """Test wysyłania danych z istniejącego pliku CSV"""
    
    print("\n📂 TEST WYSYŁANIA Z PLIKU CSV")
    print("-"*60)
    
    import pandas as pd
    import os
    from glob import glob
    
    # Znajdź najnowszy plik CSV
    csv_files = glob('outputs/livesport_h2h_*.csv')
    
    if not csv_files:
        print("⚠️  Brak plików CSV w katalogu outputs/")
        print("💡 Najpierw uruchom scraper aby wygenerować dane")
        return False
    
    latest_csv = max(csv_files, key=os.path.getmtime)
    print(f"📄 Znaleziono plik: {os.path.basename(latest_csv)}")
    
    try:
        df = pd.read_csv(latest_csv)
        matches = df.to_dict('records')
        
        print(f"   Mecze: {len(matches)}")
        print(f"   Kwalifikujących: {len([m for m in matches if m.get('qualifies')])}")
        
        # Pobierz URL
        app_url = input("\n📍 Podaj URL aplikacji: ").strip()
        
        if not app_url:
            print("❌ URL nie może być pusty!")
            return False
        
        integrator = AppIntegrator(app_url=app_url)
        
        if integrator.test_connection():
            success = integrator.send_matches(
                matches=matches,
                date='2025-10-11',
                sport='test_from_csv'
            )
            
            if success:
                print("\n✅ Dane z CSV wysłane pomyślnie!")
                return True
            else:
                print("\n❌ Nie udało się wysłać danych")
                return False
        else:
            print("\n❌ Nie można połączyć się z aplikacją")
            return False
            
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        return False


def main():
    """Menu główne"""
    
    print("\n🔗 APP INTEGRATION TESTER")
    print("="*60)
    print("\nWybierz opcję:")
    print("  1. Test podstawowy (testowe dane)")
    print("  2. Test z istniejącego pliku CSV")
    print("  3. Wyjście")
    
    choice = input("\nTwój wybór (1-3): ").strip()
    
    if choice == '1':
        test_integration()
    elif choice == '2':
        test_from_csv()
    elif choice == '3':
        print("👋 Do zobaczenia!")
        sys.exit(0)
    else:
        print("❌ Nieprawidłowy wybór!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Przerwano przez użytkownika")
        sys.exit(0)







