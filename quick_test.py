"""
🚀 SZYBKI TEST INTEGRACJI
========================

Test wysyła przykładowe dane do Twojej aplikacji UI
"""

from app_integrator import AppIntegrator

def main():
    print("="*60)
    print("🚀 SZYBKI TEST INTEGRACJI")
    print("="*60)
    
    # Pobierz URL od użytkownika
    print("\n📍 Podaj URL Twojej aplikacji UI")
    print("   Przykład: http://localhost:3000")
    app_url = input("\nURL: ").strip()
    
    if not app_url:
        print("❌ URL nie może być pusty!")
        return
    
    # Utwórz integrator
    integrator = AppIntegrator(app_url=app_url)
    
    # Test połączenia
    print(f"\n🔍 Testuję połączenie z {app_url}...")
    
    if not integrator.test_connection():
        print("\n❌ NIE MOŻNA POŁĄCZYĆ SIĘ Z APLIKACJĄ!")
        print("\n💡 Sprawdź:")
        print("   1. Czy aplikacja działa? (npm start / python app.py)")
        print("   2. Czy URL jest poprawny?")
        print("   3. Czy port jest otwarty?")
        return
    
    # Wyślij testowe dane
    print("\n✅ Połączenie działa!")
    print("\n📤 Wysyłam testowe dane...")
    
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
            'home_form_overall': ['W', 'W', 'L', 'W', 'D'],
            'away_form_overall': ['L', 'L', 'W', 'L', 'L'],
            'form_advantage': True,
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
            'home_form_overall': ['W', 'W', 'W', 'L', 'W'],
            'away_form_overall': ['L', 'W', 'L', 'L', 'L'],
            'form_advantage': True,
            'win_rate': 0.80
        }
    ]
    
    success = integrator.send_matches(
        matches=test_matches,
        date='2025-10-11',
        sport='football_test'
    )
    
    if success:
        print("\n✅ SUKCES!")
        print("="*60)
        print("🎉 Dane wysłane pomyślnie do aplikacji!")
        print("\n📊 Wysłano:")
        print(f"   • 2 mecze testowe")
        print(f"   • Real Madrid vs Barcelona")
        print(f"   • Liverpool vs Manchester City")
        print("\n💡 Sprawdź w swojej aplikacji czy dane się pojawiły!")
    else:
        print("\n❌ BŁĄD WYSYŁANIA!")
        print("\n💡 Sprawdź:")
        print("   1. Czy endpoint /api/webhook/matches istnieje?")
        print("   2. Czy aplikacja akceptuje POST requesty?")
        print("   3. Sprawdź logi aplikacji")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Przerwano")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")







