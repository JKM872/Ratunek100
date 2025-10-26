"""
LiveSport Odds API Client - pobieranie kursów bukmacherskich przez GraphQL API

Ten moduł łączy się z oficjalnym API Livesport aby pobrać kursy bukmacherskie.
Domyślnie używa Nordic Bet (ID: 165), ale można zmienić na innego bukmachera.

Źródło: Zintegrowane z livesportscraper repository
"""

import requests
import re
from typing import Dict, Optional
import time

class LiveSportOddsAPI:
    """Klient do pobierania kursów bukmacherskich z LiveSport GraphQL API"""
    
    def __init__(self, bookmaker_id: str = "165", geo_ip_code: str = "PL", geo_subdivision: str = "PL10"):
        """
        Inicjalizuje klienta API
        
        Args:
            bookmaker_id: ID bukmachera (domyślnie "165" = Nordic Bet)
            geo_ip_code: Kod kraju (np. "PL", "GB", "DE")
            geo_subdivision: Kod regionu (np. "PL10" dla Polski)
        """
        self.bookmaker_id = bookmaker_id
        self.geo_ip_code = geo_ip_code
        self.geo_subdivision = geo_subdivision
        
        # Endpoint GraphQL API Livesport
        self.api_url = "https://www.livesport.com/req/api/v2/configurator/data"
        
        # UWAGA: Jeśli 405 Method Not Allowed, spróbuj alternatywnego endpointa:
        # self.api_url = "https://www.livesport.com/api/v1/odds"
        
        # Nagłówki HTTP (symuluj prawdziwą przeglądarkę)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Origin': 'https://www.livesport.com',
            'Referer': 'https://www.livesport.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        # Mapowanie ID bukmacherów (najczęściej używane)
        self.bookmaker_names = {
            "165": "Nordic Bet",
            "16": "bet365",
            "8": "Unibet",
            "43": "William Hill",
            "14": "Bwin",
            "24": "Betfair",
        }
    
    
    def extract_event_id_from_url(self, url: str) -> Optional[str]:
        """
        Wydobywa Event ID z URL Livesport
        
        Args:
            url: URL meczu z Livesport (np. ".../?mid=ABC123")
        
        Returns:
            Event ID (np. "ABC123") lub None jeśli nie znaleziono
        
        Example:
            >>> url = "https://www.livesport.com/pl/mecz/pilka-nozna/team1/team2/?mid=KQAaF7d2"
            >>> extract_event_id_from_url(url)
            'KQAaF7d2'
        """
        # Szukaj parametru ?mid= lub &mid=
        match = re.search(r'[?&]mid=([a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)
        
        # Alternatywnie: event ID może być w hash (#id/)
        match = re.search(r'#id/([a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)
        
        return None
    
    
    def get_odds_for_event(self, event_id: str) -> Optional[Dict]:
        """
        Pobiera kursy bukmacherskie dla konkretnego wydarzenia
        
        Args:
            event_id: ID wydarzenia z Livesport (np. "KQAaF7d2")
        
        Returns:
            Słownik z kursami:
            {
                'home_odds': 1.85,
                'draw_odds': 3.50,  # Może być None dla sportów bez remisu
                'away_odds': 4.20,
                'bookmaker_id': '165',
                'bookmaker_name': 'Nordic Bet',
                'source': 'livesport_api'
            }
            lub None jeśli nie znaleziono kursów
        """
        
        # GraphQL query dla kursów
        query = {
            "operationName": "getEventOdds",
            "variables": {
                "eventId": event_id,
                "bookmakerId": self.bookmaker_id,
                "geoIpCode": self.geo_ip_code,
                "geoSubdivision": self.geo_subdivision
            },
            "query": """
                query getEventOdds($eventId: String!, $bookmakerId: String!, $geoIpCode: String, $geoSubdivision: String) {
                    event(id: $eventId) {
                        id
                        odds(
                            bookmakerId: $bookmakerId
                            geoIpCode: $geoIpCode
                            geoSubdivision: $geoSubdivision
                        ) {
                            avgOdds {
                                homeOdds
                                drawOdds
                                awayOdds
                            }
                            bookmaker {
                                id
                                name
                            }
                        }
                    }
                }
            """
        }
        
        try:
            # POPRAWKA: Spróbuj GET z parametrami zamiast POST
            # LiveSport API może wymagać GET request z query parameters
            
            # Metoda 1: Spróbuj POST (oryginalna)
            try:
                response = requests.post(
                    self.api_url,
                    json=query,
                    headers=self.headers,
                    timeout=10
                )
                
                # Jeśli 405, spróbuj GET
                if response.status_code == 405:
                    raise ValueError("POST not allowed, trying GET")
                    
            except (requests.exceptions.RequestException, ValueError):
                # Metoda 2: Spróbuj GET z prostszym endpointem
                # Użyj bezpośredniego URL do kursów
                simple_url = f"https://www.livesport.com/api/v1/event/{event_id}/odds"
                
                params = {
                    'bookmakerId': self.bookmaker_id,
                    'geoIpCode': self.geo_ip_code,
                    'geoSubdivision': self.geo_subdivision
                }
                
                response = requests.get(
                    simple_url,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
            
            response.raise_for_status()
            
            # DEBUG: Pokaż co API zwróciło
            try:
                data = response.json()
            except ValueError as e:
                print(f"   ⚠️ API zwróciło nieprawidłowy JSON: {e}")
                print(f"   📄 Response text (pierwsze 200 znaków): {response.text[:200]}")
                return None
            
            # Parsuj odpowiedź
            if 'data' in data and 'event' in data['data'] and data['data']['event']:
                event_data = data['data']['event']
                
                if 'odds' in event_data and event_data['odds']:
                    odds_data = event_data['odds']
                    avg_odds = odds_data.get('avgOdds', {})
                    
                    # Wydobądź kursy
                    home_odds = avg_odds.get('homeOdds')
                    draw_odds = avg_odds.get('drawOdds')  # Może być None
                    away_odds = avg_odds.get('awayOdds')
                    
                    # Sprawdź czy mamy przynajmniej home i away
                    if home_odds and away_odds:
                        bookmaker_name = self.bookmaker_names.get(
                            self.bookmaker_id,
                            odds_data.get('bookmaker', {}).get('name', 'Unknown')
                        )
                        
                        return {
                            'home_odds': float(home_odds),
                            'draw_odds': float(draw_odds) if draw_odds else None,
                            'away_odds': float(away_odds),
                            'bookmaker_id': self.bookmaker_id,
                            'bookmaker_name': bookmaker_name,
                            'source': 'livesport_api',
                            'event_id': event_id
                        }
            
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Błąd API request: {e}")
            return None
        
        except (KeyError, ValueError, TypeError) as e:
            print(f"   ⚠️ Błąd parsowania odpowiedzi API: {e}")
            return None
    
    
    def get_odds_from_url(self, match_url: str) -> Optional[Dict]:
        """
        Pobiera kursy bukmacherskie bezpośrednio z URL meczu
        
        Args:
            match_url: Pełny URL meczu z Livesport
        
        Returns:
            Słownik z kursami (jak get_odds_for_event) lub None
        
        Example:
            >>> client = LiveSportOddsAPI()
            >>> url = "https://www.livesport.com/pl/mecz/pilka-nozna/team1/team2/?mid=ABC123"
            >>> odds = client.get_odds_from_url(url)
            >>> print(f"Home: {odds['home_odds']}, Away: {odds['away_odds']}")
        """
        # Wydobądź Event ID z URL
        event_id = self.extract_event_id_from_url(match_url)
        
        if not event_id:
            print(f"   ⚠️ Nie znaleziono Event ID w URL: {match_url}")
            return None
        
        # Pobierz kursy dla tego event
        return self.get_odds_for_event(event_id)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_odds_for_matches_batch(match_urls: list, bookmaker_id: str = "165", 
                                delay: float = 0.5, verbose: bool = True) -> list:
    """
    Pobiera kursy dla listy URL-i meczów (batch processing)
    
    Args:
        match_urls: Lista URL-i meczów
        bookmaker_id: ID bukmachera (domyślnie "165" = Nordic Bet)
        delay: Opóźnienie między requestami (w sekundach)
        verbose: Czy wyświetlać logi
    
    Returns:
        Lista słowników z danymi meczów + kursami
    """
    if verbose:
        print(f"🎲 Rozpoczynam pobieranie kursów dla {len(match_urls)} meczów...")
        print(f"📊 Bukmacher: {bookmaker_id}")
    
    client = LiveSportOddsAPI(bookmaker_id=bookmaker_id)
    results = []
    
    for i, url in enumerate(match_urls, 1):
        if verbose:
            print(f"\n[{i}/{len(match_urls)}] {url}")
        
        odds = client.get_odds_from_url(url)
        
        if odds:
            result = {
                'match_url': url,
                'home_odds': odds['home_odds'],
                'draw_odds': odds['draw_odds'],
                'away_odds': odds['away_odds'],
                'bookmaker_name': odds['bookmaker_name'],
                'source': odds['source']
            }
            results.append(result)
            
            if verbose:
                print(f"   ✅ Home: {odds['home_odds']}, ", end='')
                if odds['draw_odds']:
                    print(f"Draw: {odds['draw_odds']}, ", end='')
                print(f"Away: {odds['away_odds']}")
        else:
            if verbose:
                print(f"   ⚠️ Brak kursów")
        
        # Rate limiting - nie spamuj API
        if i < len(match_urls):
            time.sleep(delay)
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"✅ Pobrano kursy dla {len(results)}/{len(match_urls)} meczów")
    
    return results


# ============================================================================
# PRZYKŁAD UŻYCIA
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("🎲 LIVESPORT ODDS API CLIENT - TEST")
    print("="*70)
    
    # Test 1: Pojedynczy mecz
    print("\n📝 TEST 1: Pobieranie kursów dla pojedynczego meczu")
    
    client = LiveSportOddsAPI(bookmaker_id="165")  # Nordic Bet
    
    # Przykładowy URL (ZMIEŃ NA AKTUALNY MECZ!)
    test_url = "https://www.livesport.com/pl/mecz/pilka-nozna/atalanta-8C9JjMXu/slavia-praga-viXGgnyB/?mid=KQAaF7d2"
    
    print(f"URL: {test_url}")
    
    odds = client.get_odds_from_url(test_url)
    
    if odds:
        print(f"\n✅ Kursy pobrane pomyślnie:")
        print(f"   🏠 Gospodarz: {odds['home_odds']}")
        if odds['draw_odds']:
            print(f"   ⚖️  Remis: {odds['draw_odds']}")
        print(f"   ✈️  Gość: {odds['away_odds']}")
        print(f"   📊 Źródło: {odds['bookmaker_name']}")
        print(f"   🔗 API: {odds['source']}")
    else:
        print("\n❌ Nie udało się pobrać kursów")
        print("   Możliwe przyczyny:")
        print("   - URL nie zawiera parametru ?mid=")
        print("   - Mecz nie ma dostępnych kursów w Nordic Bet")
        print("   - Event ID jest nieprawidłowe")
    
    # Test 2: Batch processing
    print("\n" + "="*70)
    print("📝 TEST 2: Batch processing (wiele meczów)")
    
    test_urls = [
        test_url,
        # Dodaj więcej URL-i do testu...
    ]
    
    results = get_odds_for_matches_batch(
        match_urls=test_urls,
        bookmaker_id="165",
        delay=0.5,
        verbose=True
    )
    
    print(f"\n✨ Gotowe! Pobrano kursy dla {len(results)} meczów.")

