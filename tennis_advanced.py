"""
🎾 ADVANCED TENNIS ANALYZER
===========================
Multi-factor scoring system dla meczów tenisowych

Czynniki:
- H2H (50%): Historia bezpośrednich pojedynków
- Ranking (25%): Pozycja w ATP/WTA
- Forma (15%): Ostatnie 5 meczów
- Powierzchnia (10%): Specjalizacja na clay/grass/hard

System punktacji: 0-100 pkt, próg kwalifikacji: 50 pkt
"""

from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import re


# ==========================================
# KONFIGURACJA SYSTEMU PUNKTACJI
# ==========================================

SCORING_CONFIG = {
    'h2h_weight': 50.0,          # Waga H2H (%)
    'ranking_weight': 25.0,      # Waga rankingu (%)
    'form_weight': 15.0,         # Waga formy (%)
    'surface_weight': 10.0,      # Waga powierzchni (%)
    'threshold': 50.0,           # Minimalny wynik do kwalifikacji
    
    # H2H scoring
    'h2h_points_per_win': 10.0,  # Punkty za każdą wygraną w H2H
    'h2h_max_points': 50.0,      # Maksymalne punkty z H2H
    
    # Ranking scoring
    'ranking_points_per_position': 0.5,  # Punkty za każde miejsce różnicy
    'ranking_max_points': 25.0,  # Maksymalne punkty z rankingu
    
    # Form scoring
    'form_points_per_win': 3.0,  # Punkty za każdą wygraną w ostatnich 5
    'form_max_points': 15.0,     # Maksymalne punkty z formy
    
    # Surface scoring
    'surface_max_points': 10.0,  # Maksymalne punkty z powierzchni
    'surface_specialist_bonus': 5.0,  # Bonus dla specjalisty
}


# ==========================================
# KLASA: TennisMatchAnalyzer
# ==========================================

class TennisMatchAnalyzer:
    """Zaawansowana analiza meczów tenisowych"""
    
    def __init__(self, config: Dict = None):
        """
        Args:
            config: Konfiguracja systemu punktacji (opcjonalna)
        """
        self.config = config or SCORING_CONFIG
    
    
    def analyze_match(
        self,
        player_a: str,
        player_b: str,
        h2h_data: Dict,
        ranking_a: Optional[int] = None,
        ranking_b: Optional[int] = None,
        form_a: Optional[List[str]] = None,  # ['W', 'W', 'L', 'W', 'W']
        form_b: Optional[List[str]] = None,
        surface: Optional[str] = None,  # 'clay', 'grass', 'hard'
        surface_stats_a: Optional[Dict] = None,  # {'clay': 0.85, 'grass': 0.72, ...}
        surface_stats_b: Optional[Dict] = None,
    ) -> Dict:
        """
        Kompleksowa analiza meczu tenisowego
        
        Returns:
            {
                'qualifies': bool,
                'total_score': float,
                'breakdown': {
                    'h2h_score': float,
                    'ranking_score': float,
                    'form_score': float,
                    'surface_score': float
                },
                'details': {...}
            }
        """
        
        result = {
            'qualifies': False,
            'total_score': 0.0,
            'breakdown': {
                'h2h_score': 0.0,
                'ranking_score': 0.0,
                'form_score': 0.0,
                'surface_score': 0.0
            },
            'details': {
                'player_a': player_a,
                'player_b': player_b,
                'factors_used': []
            }
        }
        
        # 1. H2H Analysis (50 pkt max)
        h2h_score = self._analyze_h2h(h2h_data)
        result['breakdown']['h2h_score'] = h2h_score
        result['total_score'] += h2h_score
        if h2h_score > 0:
            result['details']['factors_used'].append('h2h')
        
        # 2. Ranking Analysis (25 pkt max)
        if ranking_a is not None and ranking_b is not None:
            ranking_score = self._analyze_ranking(ranking_a, ranking_b)
            result['breakdown']['ranking_score'] = ranking_score
            result['total_score'] += ranking_score
            result['details']['factors_used'].append('ranking')
            result['details']['ranking_a'] = ranking_a
            result['details']['ranking_b'] = ranking_b
        
        # 3. Form Analysis (15 pkt max)
        if form_a and form_b:
            form_score = self._analyze_form(form_a, form_b)
            result['breakdown']['form_score'] = form_score
            result['total_score'] += form_score
            result['details']['factors_used'].append('form')
            result['details']['form_a'] = form_a
            result['details']['form_b'] = form_b
        
        # 4. Surface Analysis (10 pkt max)
        if surface and surface_stats_a and surface_stats_b:
            surface_score = self._analyze_surface(
                surface, surface_stats_a, surface_stats_b
            )
            result['breakdown']['surface_score'] = surface_score
            result['total_score'] += surface_score
            result['details']['factors_used'].append('surface')
            result['details']['surface'] = surface
        
        # Kwalifikacja
        # W tenisie home/away nie ma znaczenia - liczy się KTO jest faworytem
        # Jeśli total_score < 0, to Player B jest faworytem
        # Jeśli total_score > 0, to Player A jest faworytem
        # Kwalifikujemy jeśli KTÓRYKOLWIEK ma wystarczająco dużą przewagę
        
        abs_score = abs(result['total_score'])
        result['qualifies'] = abs_score >= self.config['threshold']
        
        # Dodaj info kto jest faworytem
        if result['total_score'] < 0:
            result['details']['favorite'] = 'player_b'
            result['details']['favorite_score'] = abs_score
        elif result['total_score'] > 0:
            result['details']['favorite'] = 'player_a'
            result['details']['favorite_score'] = abs_score
        else:
            result['details']['favorite'] = 'even'
            result['details']['favorite_score'] = 0.0
        
        return result
    
    
    def _analyze_h2h(self, h2h_data: Dict) -> float:
        """
        Analiza H2H
        
        Args:
            h2h_data: {'player_a_wins': int, 'player_b_wins': int, 'total': int}
        
        Returns:
            Punkty (-50 do +50)
            POZYTYWNE jeśli Player A ma przewagę
            NEGATYWNE jeśli Player B ma przewagę
        """
        player_a_wins = h2h_data.get('player_a_wins', 0)
        player_b_wins = h2h_data.get('player_b_wins', 0)
        total = h2h_data.get('total', 0)
        
        if total == 0:
            return 0.0
        
        # Przewaga w H2H (może być ujemna!)
        advantage = player_a_wins - player_b_wins
        
        if advantage == 0:
            return 0.0  # Remis w H2H
        
        # Punkty za każdą wygraną w przewadze (pozytywne lub negatywne)
        points = advantage * self.config['h2h_points_per_win']
        
        # Bonus/Penalty za dominację (≥75% wygranych)
        if advantage > 0:
            # Player A dominuje
            win_rate_a = player_a_wins / total
            if win_rate_a >= 0.75:
                points += 10.0  # Bonus za dominację
        else:
            # Player B dominuje
            win_rate_b = player_b_wins / total
            if win_rate_b >= 0.75:
                points -= 10.0  # Penalty (Player B dominuje)
        
        # Cap do maksimum/minimum
        if points > 0:
            return min(points, self.config['h2h_max_points'])
        else:
            return max(points, -self.config['h2h_max_points'])
    
    
    def _analyze_ranking(self, ranking_a: int, ranking_b: int) -> float:
        """
        Analiza różnicy w rankingu
        
        W tenisie NIŻSZY ranking = LEPSZY zawodnik (#1 > #100)
        
        Returns:
            Punkty (0-25) - POZYTYWNE jeśli A lepszy, NEGATYWNE jeśli B lepszy
        """
        # W tenisie: niższy numer = lepszy ranking
        # Jeśli ranking_a < ranking_b, to A jest lepszy
        # Jeśli ranking_a > ranking_b, to B jest lepszy
        
        if ranking_a >= ranking_b:
            # Player A ma gorszy lub równy ranking
            # Zwróć UJEMNE punkty (oznacza to że B jest lepszy)
            diff = ranking_a - ranking_b
            points = -diff * self.config['ranking_points_per_position']
            
            # Penalty za grę przeciwko top 10
            if ranking_b <= 10 and ranking_a > 50:
                points -= 5.0
            
            return max(points, -self.config['ranking_max_points'])
        else:
            # Player A ma lepszy ranking (niższą liczbę)
            diff = ranking_b - ranking_a
            
            # Punkty za różnicę
            points = diff * self.config['ranking_points_per_position']
            
            # Bonus za top 10 vs poza top 50
            if ranking_a <= 10 and ranking_b > 50:
                points += 5.0
            
            # Cap do maksimum
            return min(points, self.config['ranking_max_points'])
    
    
    def _analyze_form(self, form_a: List[str], form_b: List[str]) -> float:
        """
        Analiza formy (ostatnie mecze)
        
        Args:
            form_a: Lista wyników ['W', 'W', 'L', 'W', 'W']
            form_b: Lista wyników ['W', 'L', 'L', 'W', 'L']
        
        Returns:
            Punkty (-15 do +15) - POZYTYWNE jeśli A lepsza forma, NEGATYWNE jeśli B
        """
        # Policz wygrane
        wins_a = sum(1 for r in form_a if r == 'W')
        wins_b = sum(1 for r in form_b if r == 'W')
        
        # Przewaga w formie (może być ujemna!)
        advantage = wins_a - wins_b
        
        # Punkty za przewagę (pozytywne lub ujemne)
        points = advantage * self.config['form_points_per_win']
        
        # Bonus/Penalty za streaki
        if advantage > 0:
            # A ma lepszą formę
            if self._has_streak(form_a, 'W', 3):
                points += 3.0
        elif advantage < 0:
            # B ma lepszą formę
            if self._has_streak(form_b, 'W', 3):
                points -= 3.0
        
        # Cap do maksimum/minimum
        if points > 0:
            return min(points, self.config['form_max_points'])
        else:
            return max(points, -self.config['form_max_points'])
    
    
    def _analyze_surface(
        self,
        surface: str,
        stats_a: Dict[str, float],
        stats_b: Dict[str, float]
    ) -> float:
        """
        Analiza specjalizacji na danej powierzchni
        
        Args:
            surface: 'clay', 'grass', 'hard'
            stats_a: {'clay': 0.85, 'grass': 0.70, 'hard': 0.75}
            stats_b: {'clay': 0.72, 'grass': 0.80, 'hard': 0.78}
        
        Returns:
            Punkty (-10 do +10)
            POZYTYWNE jeśli Player A lepszy na tej nawierzchni
            NEGATYWNE jeśli Player B lepszy na tej nawierzchni
        """
        if surface not in stats_a or surface not in stats_b:
            return 0.0
        
        win_rate_a = stats_a[surface]
        win_rate_b = stats_b[surface]
        
        # Przewaga na tej powierzchni (może być ujemna!)
        advantage = win_rate_a - win_rate_b
        
        if abs(advantage) < 0.01:  # Praktycznie równi
            return 0.0
        
        # Punkty proporcjonalne do przewagi (pozytywne lub negatywne)
        points = advantage * 50  # 0.10 różnicy = 5 pkt
        
        # Bonus/Penalty dla specjalisty (>80% na tej powierzchni)
        if advantage > 0:
            # Player A lepszy na tej nawierzchni
            if win_rate_a >= 0.80 and advantage >= 0.10:
                points += self.config['surface_specialist_bonus']
        else:
            # Player B lepszy na tej nawierzchni
            if win_rate_b >= 0.80 and abs(advantage) >= 0.10:
                points -= self.config['surface_specialist_bonus']
        
        # Cap do maksimum/minimum
        if points > 0:
            return min(points, self.config['surface_max_points'])
        else:
            return max(points, -self.config['surface_max_points'])
    
    
    def _has_streak(self, form: List[str], result: str, length: int) -> bool:
        """Sprawdź czy jest seria wyników"""
        if len(form) < length:
            return False
        
        # Sprawdź ostatnie N wyników
        recent = form[-length:]
        return all(r == result for r in recent)
    
    
    def format_analysis(self, analysis: Dict) -> str:
        """Formatuje wyniki analizy do czytelnego tekstu"""
        lines = []
        
        lines.append(f"🎾 ANALIZA: {analysis['details']['player_a']} vs {analysis['details']['player_b']}")
        lines.append("=" * 70)
        
        # Breakdown
        breakdown = analysis['breakdown']
        lines.append(f"\n📊 PUNKTACJA:")
        lines.append(f"   H2H:        {breakdown['h2h_score']:.1f} / 50.0 pkt")
        lines.append(f"   Ranking:    {breakdown['ranking_score']:.1f} / 25.0 pkt")
        lines.append(f"   Forma:      {breakdown['form_score']:.1f} / 15.0 pkt")
        lines.append(f"   Powierzchnia: {breakdown['surface_score']:.1f} / 10.0 pkt")
        lines.append(f"   " + "-" * 40)
        lines.append(f"   RAZEM:      {analysis['total_score']:.1f} / 100.0 pkt")
        
        # Wynik
        if analysis['qualifies']:
            lines.append(f"\n✅ WYNIK: KWALIFIKUJE SIĘ (≥{self.config['threshold']} pkt)")
        else:
            lines.append(f"\n❌ WYNIK: NIE KWALIFIKUJE (próg: {self.config['threshold']} pkt)")
        
        # Czynniki użyte
        factors = analysis['details']['factors_used']
        lines.append(f"\n📋 Użyte czynniki: {', '.join(factors)}")
        
        return '\n'.join(lines)


# ==========================================
# PARSOWANIE DANYCH Z LIVESPORT
# ==========================================

def extract_ranking_from_page(soup: BeautifulSoup, player_name: str) -> Optional[int]:
    """
    Wydobądź ranking zawodnika ze strony Livesport
    
    Livesport często pokazuje ranking obok nazwy zawodnika:
    "Novak Djokovic (1)" → ranking 1
    """
    try:
        # Szukaj wzorca: Nazwisko (ranking)
        text = soup.get_text()
        pattern = rf"{re.escape(player_name)}\s*\((\d+)\)"
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
        
        # Alternatywnie: szukaj elementu z rankingiem
        # Livesport może mieć dedykowany element dla rankingu
        ranking_els = soup.select('[class*="ranking"]')
        for el in ranking_els:
            text = el.get_text(strip=True)
            if player_name.lower() in text.lower():
                # Wyciągnij liczbę
                nums = re.findall(r'\d+', text)
                if nums:
                    return int(nums[0])
        
        return None
    except Exception:
        return None


def extract_recent_form(soup: BeautifulSoup, player_name: str) -> List[str]:
    """
    Wydobądź ostatnie wyniki zawodnika (forma)
    
    Returns:
        ['W', 'W', 'L', 'W', 'W']  # W=wygrana, L=przegrana
    """
    try:
        # Livesport może mieć sekcję z ostatnimi wynikami
        # Szukamy elementów typu: result-w, result-l, etc.
        
        form = []
        
        # Metoda 1: Szukaj dedykowanych elementów formy
        form_els = soup.select('[class*="form"]')
        for el in form_els:
            text = el.get_text(strip=True).upper()
            # W, L, D (draw - traktujemy jako L w tenisie)
            for char in text:
                if char in ['W', 'L', 'D']:
                    form.append('L' if char == 'D' else char)
                    if len(form) >= 5:
                        break
            if len(form) >= 5:
                break
        
        return form[:5]  # Ostatnie 5
    except Exception:
        return []


def detect_surface(soup: BeautifulSoup, url: str) -> Optional[str]:
    """
    Wykryj powierzchnię kortu z informacji o turnieju
    
    Returns:
        'clay', 'grass', 'hard', lub None
    """
    try:
        text = soup.get_text().lower()
        url_lower = url.lower()
        
        # Słowa kluczowe dla powierzchni
        if any(keyword in text or keyword in url_lower for keyword in [
            'clay', 'ziemia', 'antuka', 'roland garros', 'monte carlo', 'rome', 'madrid'
        ]):
            return 'clay'
        
        if any(keyword in text or keyword in url_lower for keyword in [
            'grass', 'trawa', 'wimbledon', 'halle', 'queens'
        ]):
            return 'grass'
        
        if any(keyword in text or keyword in url_lower for keyword in [
            'hard', 'twarda', 'us open', 'australian open', 'indian wells', 'miami'
        ]):
            return 'hard'
        
        return None
    except Exception:
        return None


def calculate_surface_stats(h2h_matches: List[Dict], player_name: str) -> Dict[str, float]:
    """
    Oblicz statystyki na różnych powierzchniach na podstawie H2H
    
    Note: To uproszczona wersja - w pełnej implementacji
    potrzebowalibyśmy danych o wszystkich meczach zawodnika
    
    Returns:
        {'clay': 0.75, 'grass': 0.82, 'hard': 0.70}
    """
    # W tej wersji zwracamy domyślne wartości
    # W pełnej implementacji analizowalibyśmy historię meczów
    
    return {
        'clay': 0.70,  # Domyślnie: 70% win rate
        'grass': 0.70,
        'hard': 0.70
    }


# ==========================================
# PRZYKŁAD UŻYCIA
# ==========================================

if __name__ == '__main__':
    # Test systemu
    analyzer = TennisMatchAnalyzer()
    
    # Przykład: Alcaraz vs Rune
    analysis = analyzer.analyze_match(
        player_a='Carlos Alcaraz',
        player_b='Holger Rune',
        h2h_data={'player_a_wins': 3, 'player_b_wins': 1, 'total': 4},
        ranking_a=2,
        ranking_b=8,
        form_a=['W', 'W', 'W', 'L', 'W'],  # 4/5
        form_b=['W', 'L', 'W', 'L', 'L'],  # 2/5
        surface='clay',
        surface_stats_a={'clay': 0.85, 'grass': 0.72, 'hard': 0.78},
        surface_stats_b={'clay': 0.72, 'grass': 0.68, 'hard': 0.75}
    )
    
    print(analyzer.format_analysis(analysis))
    print()
    print(f"Kwalifikuje się: {analysis['qualifies']}")
    print(f"Wynik końcowy: {analysis['total_score']:.1f}/100 pkt")

