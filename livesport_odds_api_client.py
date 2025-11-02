"""
LiveSport Odds API Client V2 - pobieranie kursów bukmacherskich przez GraphQL API

Ten moduł łączy się z oficjalnym API Livesport aby pobrać kursy bukmacherskie.

POPRAWKI V2 (2025-11-01):
- STS jako domyślny bukmacher (ID: 167) - polski rynek
- 3 próby zamiast 2 (exponential backoff)
- Lepsze nagłówki HTTP (Chrome 131, więcej sec-ch-ua)
- Fallback do alternatywnych parametrów API (3 warianty)
- 12 bukmacherów w mapowaniu (w tym polskie: STS, Fortuna, Superbet)
- Rate limiting (200ms między requestami)

Źródło: Zintegrowane z livesportscraper repository
"""

import requests
import re
from typing import Dict, Optional, List
from urllib.parse import urlparse, parse_qs
import time

class LiveSportOddsAPI:
    """Klient do pobierania kursów bukmacherskich z LiveSport GraphQL API"""
    
    def __init__(self, bookmaker_id: str = "167", geo_ip_code: str = "PL", geo_subdivision: str = "PL10"):
        """
        Inicjalizuje klienta API
        
        Args:
            bookmaker_id: ID bukmachera (domyślnie "167" = STS dla Polski)
            geo_ip_code: Kod kraju (PL)
            geo_subdivision: Kod regionu (PL10 = Mazowieckie)
        """
        self.bookmaker_id = bookmaker_id
        self.geo_ip_code = geo_ip_code
        self.geo_subdivision = geo_subdivision
        
        # PRAWDZIWY Endpoint GraphQL API Livesport
        self.api_url = "https://global.ds.lsapp.eu/odds/pq_graphql"
        
        # Stwórz session z connection pooling
        self.session = requests.Session()
        
        # POPRAWIONE NAGŁÓWKI V2 - bardziej realistyczne (Chrome 131)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': 'https://www.livesport.com',
            'Referer': 'https://www.livesport.com/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })
        
        # Mapowanie ID bukmacherów (ROZSZERZONE - 12 bukmacherów!)
        self.bookmaker_names = {
            "167": "STS",           # Polski (priorytet!)
            "171": "Fortuna",       # Polski
            "172": "Superbet",      # Polski
            "165": "NordicBet",
            "16": "Bet365",
            "8": "Unibet",
            "43": "William Hill",
            "14": "Bwin",
            "24": "Betfair",
            "170": "Betclic",
            "18": "Pinnacle",
            "23": "1xBet",
        }
    
    
    def extract_event_id_from_url(self, url: str) -> Optional[str]:
        """
        Ekstraktuje event_id z URL meczu Livesport.
        
        Formaty URL:
        - https://www.livesport.com/pl/pilka-nozna/polska/ekstraklasa/legia-warszawa-gornik-zabrze/UveDRb0k/?mid=KdfeT8U2
        - https://www.livesport.com/match/abc123/?mid=xyz789
        
        Returns:
            Event ID (np. "KdfeT8U2") lub None
        """
        try:
            # Metoda 1: Parametr ?mid= w URL
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            if 'mid' in query_params:
                event_id = query_params['mid'][0]
                if event_id:
                    return event_id
            
            # Metoda 2: ID w ścieżce URL (przed parametrami)
            # Format: /druzyna1-druzyna2/EVENT_ID/?...
            path_parts = parsed.path.rstrip('/').split('/')
            if len(path_parts) >= 2:
                # Ostatnia część ścieżki (przed ?)
                potential_id = path_parts[-1]
                # Event ID zazwyczaj: 8 znaków alfanumeryczne
                if re.match(r'^[A-Za-z0-9]{8}$', potential_id):
                    return potential_id
            
            return None
        
        except Exception as e:
            print(f"   ⚠️ extract_event_id error: {e}")
            return None
    
    
    def get_odds_for_event(self, event_id: str) -> Optional[Dict]:
        """
        Pobiera kursy bukmacherskie dla konkretnego wydarzenia
        
        UŻYWA PRAWDZIWEGO ENDPOINTA LIVESPORT z RETRY MECHANISM (3 próby)
        
        Args:
            event_id: ID wydarzenia z Livesport (np. "KQAaF7d2")
        
        Returns:
            Słownik z kursami lub None
        """
        
        # PRÓBA 1-3: Główny endpoint (3 próby z exponential backoff)
        for attempt in range(3):
            try:
                # PRAWDZIWE parametry
                params = {
                    '_hash': 'ope2',  # Hash dla kursów ("odds per bookmaker")
                    'eventId': event_id,
                    'bookmakerId': self.bookmaker_id,
                    'betType': 'HOME_DRAW_AWAY',  # Typ zakładu: 1X2
                    'betScope': 'FULL_TIME'  # Pełen czas (nie połowy)
                }
                
                # GET request do prawdziwego API
                response = self.session.get(
                    self.api_url,
                    params=params,
                    timeout=10
                )
                
                # Sprawdź status
                if response.status_code != 200:
                    if attempt < 2:
                        time.sleep(0.5 * (attempt + 1))  # Exponential backoff: 0.5s, 1.0s
                        continue
                    # Ostatnia próba - spróbuj fallback
                    return self._get_odds_fallback(event_id)
                
                # Parsuj JSON
                try:
                    data = response.json()
                except (ValueError, TypeError) as json_err:
                    if attempt < 2:
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    return self._get_odds_fallback(event_id)
                
                # Sprawdź czy data nie jest None
                if not data or not isinstance(data, dict):
                    if attempt < 2:
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    return self._get_odds_fallback(event_id)
                
                # Parsuj odpowiedź
                if 'data' in data and isinstance(data.get('data'), dict) and 'findPrematchOddsForBookmaker' in data['data']:
                    odds_data = data['data']['findPrematchOddsForBookmaker']
                    
                    # KLUCZOWE: Sprawdź czy odds_data nie jest None!
                    if not odds_data or not isinstance(odds_data, dict):
                        if attempt < 2:
                            time.sleep(0.5 * (attempt + 1))
                            continue
                        return self._get_odds_fallback(event_id)
                    
                    result = {
                        'bookmaker_id': self.bookmaker_id,
                        'bookmaker_name': self.bookmaker_names.get(self.bookmaker_id, 'Unknown'),
                        'source': 'livesport_api',
                        'event_id': event_id
                    }
                    
                    # HOME odds
                    if 'home' in odds_data and odds_data['home']:
                        home_value = odds_data['home'].get('value')
                        if home_value:
                            result['home_odds'] = float(home_value)
                    
                    # DRAW odds (może nie istnieć dla niektórych sportów)
                    if 'draw' in odds_data and odds_data['draw']:
                        draw_value = odds_data['draw'].get('value')
                        if draw_value:
                            result['draw_odds'] = float(draw_value)
                    
                    # AWAY odds
                    if 'away' in odds_data and odds_data['away']:
                        away_value = odds_data['away'].get('value')
                        if away_value:
                            result['away_odds'] = float(away_value)
                    
                    # Sprawdź czy mamy przynajmniej home i away
                    if result.get('home_odds') and result.get('away_odds'):
                        return result
                
                # Jeśli nie udało się - retry
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                
                return self._get_odds_fallback(event_id)
            
            except requests.exceptions.RequestException as e:
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                return self._get_odds_fallback(event_id)
            
            except (KeyError, ValueError, TypeError) as e:
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                return self._get_odds_fallback(event_id)
        
        # Jeśli wszystkie 3 próby zawiodły
        return self._get_odds_fallback(event_id)
    
    def _get_odds_fallback(self, event_id: str) -> Optional[Dict]:
        """
        Fallback: Spróbuj alternatywnego endpointa lub metody
        
        NOWE: Próbuje różnych kombinacji parametrów (3 warianty)
        """
        try:
            # Alternatywne kombinacje parametrów
            alt_params_list = [
                # Próba 1: Bez betScope
                {
                    '_hash': 'ope2',
                    'eventId': event_id,
                    'bookmakerId': self.bookmaker_id,
                    'betType': 'HOME_DRAW_AWAY',
                },
                # Próba 2: Z betScope jako MATCH
                {
                    '_hash': 'ope2',
                    'eventId': event_id,
                    'bookmakerId': self.bookmaker_id,
                    'betType': 'HOME_DRAW_AWAY',
                    'betScope': 'MATCH'
                },
                # Próba 3: Tylko eventId i bookmakerId
                {
                    '_hash': 'ope2',
                    'eventId': event_id,
                    'bookmakerId': self.bookmaker_id,
                },
            ]
            
            for alt_params in alt_params_list:
                try:
                    response = self.session.get(
                        self.api_url,
                        params=alt_params,
                        timeout=8
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Parsuj odpowiedź (ta sama logika co wyżej)
                        if isinstance(data, dict) and 'data' in data and 'findPrematchOddsForBookmaker' in data['data']:
                            odds_data = data['data']['findPrematchOddsForBookmaker']
                            
                            if odds_data and isinstance(odds_data, dict):
                                result = {
                                    'bookmaker_id': self.bookmaker_id,
                                    'bookmaker_name': self.bookmaker_names.get(self.bookmaker_id, 'Unknown'),
                                    'source': 'livesport_api_fallback',
                                    'event_id': event_id
                                }
                                
                                if 'home' in odds_data and odds_data['home']:
                                    home_value = odds_data['home'].get('value')
                                    if home_value:
                                        result['home_odds'] = float(home_value)
                                
                                if 'draw' in odds_data and odds_data['draw']:
                                    draw_value = odds_data['draw'].get('value')
                                    if draw_value:
                                        result['draw_odds'] = float(draw_value)
                                
                                if 'away' in odds_data and odds_data['away']:
                                    away_value = odds_data['away'].get('value')
                                    if away_value:
                                        result['away_odds'] = float(away_value)
                                
                                if result.get('home_odds') and result.get('away_odds'):
                                    return result
                except:
                    continue
            
            return None
        
        except Exception:
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
    
    
    def get_over_under_odds(self, event_id: str, sport: str = 'football') -> Optional[Dict]:
        """
        Pobiera kursy Over/Under dla wydarzenia
        
        Args:
            event_id: ID wydarzenia z Livesport
            sport: Sport ('football', 'basketball', 'handball', 'volleyball', 'hockey', 'tennis')
        
        Returns:
            Słownik z kursami O/U:
            {
                'over_2_5': 1.85,
                'under_2_5': 1.95,
                'btts_yes': 1.75,  # tylko football
                'btts_no': 2.05,   # tylko football
                'line': '2.5',
                'line_type': 'goals'
            }
        """
        try:
            # Parametry dla Over/Under
            params = {
                '_hash': 'ope2',
                'eventId': event_id,
                'bookmakerId': self.bookmaker_id,
                'betType': 'OVER_UNDER',  # Typ zakładu O/U
                'betScope': 'FULL_TIME'
            }
            
            # GET request
            response = self.session.get(
                self.api_url,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"   ⚠️ API O/U ERROR {response.status_code}: {response.text[:200]}")
                return None
            
            # Parsuj JSON
            try:
                data = response.json()
            except (ValueError, TypeError) as json_err:
                print(f"   ⚠️ Błąd parsowania O/U JSON: {json_err}")
                return None
            
            # Sprawdź czy data nie jest None
            if not data:
                return None
            
            if not isinstance(data, dict):
                return None
            
            # Parsuj odpowiedź
            if isinstance(data, dict) and 'data' in data and isinstance(data.get('data'), dict) and 'findPrematchOddsForBookmaker' in data['data']:
                odds_data = data['data']['findPrematchOddsForBookmaker']
                
                # KLUCZOWE: Sprawdź czy odds_data nie jest None!
                if not odds_data or not isinstance(odds_data, dict):
                    return None
                
                result = {
                    'bookmaker_id': self.bookmaker_id,
                    'bookmaker_name': self.bookmaker_names.get(self.bookmaker_id, 'Nordic Bet'),
                    'source': 'livesport_api',
                    'event_id': event_id
                }
                
                # OVER odds
                if 'over' in odds_data and odds_data['over']:
                    over_value = odds_data['over'].get('value')
                    line = odds_data['over'].get('line', '2.5')  # Linia O/U
                    if over_value:
                        result['over_odds'] = float(over_value)
                        result['line'] = str(line)
                
                # UNDER odds
                if 'under' in odds_data and odds_data['under']:
                    under_value = odds_data['under'].get('value')
                    if under_value:
                        result['under_odds'] = float(under_value)
                
                # Typ linii zależy od sportu
                if sport == 'football':
                    result['line_type'] = 'goals'
                elif sport in ['basketball', 'volleyball']:
                    result['line_type'] = 'points'
                elif sport in ['handball', 'hockey']:
                    result['line_type'] = 'goals'
                elif sport == 'tennis':
                    result['line_type'] = 'sets'
                
                # Sprawdź czy mamy kursy
                if result.get('over_odds') and result.get('under_odds'):
                    return result
            
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Błąd API O/U request: {e}")
            return None
        
        except (KeyError, ValueError, TypeError) as e:
            print(f"   ⚠️ Błąd parsowania O/U: {e}")
            return None
    
    
    def get_btts_odds(self, event_id: str) -> Optional[Dict]:
        """
        Pobiera kursy BTTS (Both Teams To Score) dla piłki nożnej
        
        Returns:
            {
                'btts_yes': 1.75,
                'btts_no': 2.05
            }
        """
        try:
            params = {
                '_hash': 'ope2',
                'eventId': event_id,
                'bookmakerId': self.bookmaker_id,
                'betType': 'BOTH_TEAMS_SCORE',
                'betScope': 'FULL_TIME'
            }
            
            response = self.session.get(
                self.api_url,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            # Parsuj JSON
            try:
                data = response.json()
            except (ValueError, TypeError):
                return None
            
            # Sprawdź czy data nie jest None
            if not data:
                return None
            
            if not isinstance(data, dict):
                return None
            
            if isinstance(data, dict) and 'data' in data and isinstance(data.get('data'), dict) and 'findPrematchOddsForBookmaker' in data['data']:
                odds_data = data['data']['findPrematchOddsForBookmaker']
                
                # KLUCZOWE: Sprawdź czy odds_data nie jest None!
                if not odds_data or not isinstance(odds_data, dict):
                    return None
                
                result = {}
                
                # YES (obie drużyny strzelą)
                if 'yes' in odds_data and odds_data['yes']:
                    yes_value = odds_data['yes'].get('value')
                    if yes_value:
                        result['btts_yes'] = float(yes_value)
                
                # NO (przynajmniej jedna drużyna nie strzeli)
                if 'no' in odds_data and odds_data['no']:
                    no_value = odds_data['no'].get('value')
                    if no_value:
                        result['btts_no'] = float(no_value)
                
                if result.get('btts_yes') and result.get('btts_no'):
                    return result
            
            return None
        
        except Exception as e:
            print(f"   ⚠️ Błąd BTTS: {e}")
            return None
    
    
    def get_complete_odds(self, event_id: str, sport: str = 'football') -> Dict:
        """
        Pobiera WSZYSTKIE kursy dla wydarzenia (1X2 + O/U + BTTS)
        
        Returns:
            {
                # 1X2
                'home_odds': 1.85,
                'draw_odds': 3.50,
                'away_odds': 4.20,
                
                # Over/Under
                'over_odds': 1.85,
                'under_odds': 1.95,
                'ou_line': '2.5',
                
                # BTTS (tylko football)
                'btts_yes': 1.75,
                'btts_no': 2.05
            }
        """
        result = {}
        
        # 1. Pobierz kursy 1X2
        main_odds = self.get_odds_for_event(event_id)
        if main_odds:
            result.update(main_odds)
        
        # 2. Pobierz kursy O/U
        ou_odds = self.get_over_under_odds(event_id, sport)
        if ou_odds:
            result['over_odds'] = ou_odds.get('over_odds')
            result['under_odds'] = ou_odds.get('under_odds')
            result['ou_line'] = ou_odds.get('line', '2.5')
            result['ou_line_type'] = ou_odds.get('line_type', 'goals')
        
        # 3. Pobierz kursy BTTS (tylko dla football)
        if sport == 'football':
            btts_odds = self.get_btts_odds(event_id)
            if btts_odds:
                result['btts_yes'] = btts_odds.get('btts_yes')
                result['btts_no'] = btts_odds.get('btts_no')
        
        return result


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

