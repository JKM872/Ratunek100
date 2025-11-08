"""
🔗 APP INTEGRATOR - Połączenie scrapera z aplikacją UI
=====================================================

Ten moduł umożliwia automatyczne wysyłanie danych ze scrapera
do Twojej aplikacji UI przez różne metody.
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime


class AppIntegrator:
    """Klasa do integracji scrapera z aplikacją zewnętrzną"""
    
    def __init__(self, app_url: str, api_key: Optional[str] = None):
        """
        Inicjalizacja integratora
        
        Args:
            app_url: URL Twojej aplikacji (np. 'http://localhost:3000' lub 'https://twoja-app.com')
            api_key: Opcjonalny klucz API dla autoryzacji
        """
        self.app_url = app_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'FlashscoreScraper/1.0'
        }
        
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def send_matches(self, matches: List[Dict], date: str, sport: str, endpoint: str = '/api/webhook/matches') -> bool:
        """
        Wyślij mecze do aplikacji w BATCH MODE
        
        Args:
            matches: Lista meczów (dict)
            date: Data meczów (YYYY-MM-DD)
            sport: Sport (football, basketball, etc.)
            endpoint: Endpoint w Twojej aplikacji
        
        Returns:
            True jeśli sukces, False jeśli błąd
        """
        import time
        
        # Dla małych zbiorów - wyślij wszystko naraz
        if len(matches) <= 100:
            return self._send_single_batch(matches, date, sport, endpoint)
        
        # Dla dużych zbiorów - wysyłaj w paczkach po 100
        print(f"\n📦 Duży zbiór ({len(matches)} meczów) - wysyłam w paczkach po 100...")
        
        BATCH_SIZE = 100
        total_batches = (len(matches) + BATCH_SIZE - 1) // BATCH_SIZE
        success_count = 0
        fail_count = 0
        
        for i in range(0, len(matches), BATCH_SIZE):
            batch = matches[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            
            print(f"\n   📤 Batch {batch_num}/{total_batches} ({len(batch)} meczów)...")
            
            if self._send_single_batch(batch, date, sport, endpoint):
                success_count += 1
                print(f"      ✅ Batch {batch_num} zapisany")
            else:
                fail_count += 1
                print(f"      ❌ Batch {batch_num} failed")
            
            # Przerwa między batchami (nie dla ostatniego)
            if i + BATCH_SIZE < len(matches):
                print(f"      ⏸️  Czekam 2s...")
                time.sleep(2)
        
        print(f"\n✅ Wysłano {success_count}/{total_batches} batchy")
        if fail_count > 0:
            print(f"⚠️  {fail_count} batchy nie udały się")
        
        return fail_count == 0
    
    def _send_single_batch(self, matches: List[Dict], date: str, sport: str, endpoint: str) -> bool:
        """Wyślij pojedynczą paczkę meczów (internal method)"""
        url = f"{self.app_url}{endpoint}"
        
        payload = {
            'date': date,
            'sport': sport,
            'matches': matches,
            'qualified_count': len([m for m in matches if m.get('qualifies')]),
            'total_count': len(matches),
            'timestamp': datetime.now().isoformat(),
            'source': 'flashscore_scraper'
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=60)
            
            if response.status_code in [200, 201, 202]:
                try:
                    response_data = response.json()
                    saved = response_data.get('saved', 0)
                    duplicates = response_data.get('duplicates', 0)
                    print(f"      � Saved: {saved}, ⏭️ Duplicates: {duplicates}")
                except:
                    pass
                return True
            else:
                print(f"      ❌ Status: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"      ❌ Connection error: {self.app_url}")
            return False
        except requests.exceptions.Timeout:
            print(f"      ❌ Timeout (60s)")
            return False
        except Exception as e:
            print(f"      ❌ Error: {e}")
            return False
    
    def send_progress(self, progress: int, total: int, current_match: str, endpoint: str = '/api/webhook/progress') -> bool:
        """
        Wyślij postęp scrapingu (dla real-time updates)
        
        Args:
            progress: Aktualna liczba przetworzonych meczów
            total: Całkowita liczba meczów
            current_match: URL aktualnie przetwarzanego meczu
            endpoint: Endpoint w Twojej aplikacji
        
        Returns:
            True jeśli sukces, False jeśli błąd
        """
        url = f"{self.app_url}{endpoint}"
        
        payload = {
            'progress': progress,
            'total': total,
            'percent': round((progress / total) * 100, 1) if total > 0 else 0,
            'current_match': current_match,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=5)
            return response.status_code in [200, 201, 202]
        except:
            return False
    
    def test_connection(self) -> bool:
        """
        Testuj połączenie z aplikacją
        
        Returns:
            True jeśli aplikacja odpowiada, False w przeciwnym razie
        """
        try:
            print(f"\n🔍 Testuję połączenie z aplikacją...")
            print(f"   URL: {self.app_url}")
            
            # Próbuj różne endpointy
            test_endpoints = ['/api/health', '/health', '/api/status', '/']
            
            for endpoint in test_endpoints:
                url = f"{self.app_url}{endpoint}"
                try:
                    response = requests.get(url, headers=self.headers, timeout=5)
                    if response.status_code in [200, 201, 202, 204]:
                        print(f"   ✅ Połączenie działa! Endpoint: {endpoint}")
                        return True
                except:
                    continue
            
            print(f"   ❌ Nie udało się połączyć z aplikacją")
            print(f"   💡 Upewnij się że aplikacja działa pod adresem: {self.app_url}")
            return False
            
        except Exception as e:
            print(f"   ❌ Błąd testowania połączenia: {e}")
            return False
    
    def send_batch_by_sport(self, all_matches: Dict[str, List[Dict]], date: str) -> Dict[str, bool]:
        """
        Wyślij mecze pogrupowane po sportach
        
        Args:
            all_matches: Dict gdzie klucz = sport, wartość = lista meczów
            date: Data meczów
        
        Returns:
            Dict z wynikami (sport -> sukces/błąd)
        """
        results = {}
        
        for sport, matches in all_matches.items():
            success = self.send_matches(matches, date, sport)
            results[sport] = success
            
        return results


def create_integrator_from_config(config_file: str = 'app_integration_config.json') -> Optional[AppIntegrator]:
    """
    Utwórz integrator z pliku konfiguracyjnego
    
    Args:
        config_file: Ścieżka do pliku JSON z konfiguracją
    
    Returns:
        AppIntegrator lub None jeśli błąd
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return AppIntegrator(
            app_url=config.get('app_url'),
            api_key=config.get('api_key')
        )
    except FileNotFoundError:
        print(f"⚠️  Plik konfiguracyjny {config_file} nie istnieje")
        print(f"💡 Utwórz plik z konfiguracją:")
        print(f"""
{{
    "app_url": "http://localhost:3000",
    "api_key": "optional-api-key-here"
}}
        """)
        return None
    except Exception as e:
        print(f"❌ Błąd wczytywania konfiguracji: {e}")
        return None


# ============================================
# PRZYKŁADY UŻYCIA
# ============================================

def example_basic():
    """Podstawowy przykład użycia"""
    
    # 1. Utwórz integrator
    integrator = AppIntegrator(
        app_url='http://localhost:3000',
        api_key='optional-api-key'  # opcjonalne
    )
    
    # 2. Testuj połączenie
    if not integrator.test_connection():
        print("❌ Nie można połączyć się z aplikacją!")
        return
    
    # 3. Wyślij mecze
    matches = [
        {
            'match_url': 'https://www.livesport.com/pl/pilka-nozna/mecz/123',
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'match_time': '20:00',
            'home_wins': 3,
            'qualifies': True
        }
    ]
    
    integrator.send_matches(matches, '2025-10-11', 'football')


def example_from_csv():
    """Przykład z pliku CSV"""
    import pandas as pd
    
    # Wczytaj dane z CSV
    df = pd.read_csv('outputs/livesport_h2h_2025-10-11_football_EMAIL.csv')
    
    # Konwertuj do dict
    matches = df.to_dict('records')
    
    # Wyślij do aplikacji
    integrator = AppIntegrator('http://localhost:3000')
    integrator.send_matches(matches, '2025-10-11', 'football')


if __name__ == '__main__':
    print("🔗 App Integrator - Test")
    print("=" * 50)
    
    # Test z konfiguracją
    integrator = create_integrator_from_config()
    
    if integrator:
        integrator.test_connection()
    else:
        print("\n💡 Przykład użycia:")
        example_basic()

