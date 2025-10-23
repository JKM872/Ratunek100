"""
🎾 ADVANCED TENNIS ANALYZER V3
===========================
System scoringu skoncentrowany na JAKOŚCI predykcji, nie ilości

Nowa metodologia:
- H2H (40%): Historia bezpośrednia z wagą czasową (nowsze mecze = więcej)
- Forma aktualna (30%): Ostatnie 10 meczów z analizą trendów
- Forma na nawierzchni (20%): Skuteczność na konkretnej nawierzchni
- Momentum (10%): Serie zwycięstw, pewność siebie

RANKING jest IGNOROWANY - w tenisie forma > ranking

System punktacji: 0-100 pkt, próg kwalifikacji: 45 pkt (WYSOKI - tylko pewne typy)
"""

from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta


# ==========================================
# KONFIGURACJA SYSTEMU PUNKTACJI V3
# ==========================================

SCORING_CONFIG = {
    # Wagi czynników (suma = 100%)
    'h2h_weight': 40.0,              # H2H z wagą czasową
    'current_form_weight': 30.0,     # Forma ogólna (ostatnie 10 meczów)
    'surface_form_weight': 20.0,     # Forma na danej nawierzchni
    'momentum_weight': 10.0,         # Momentum (serie, mental game)
    
    'threshold': 45.0,               # Bazowy próg = tylko pewne typy
    'adaptive_threshold': True,      # Czy używać adaptacyjnych progów
    
    # H2H scoring (40 pkt max)
    'h2h_base_points': 8.0,          # Bazowe punkty za każdą wygraną w H2H
    'h2h_recent_multiplier': 1.5,    # Mnożnik dla meczów z ostatnich 12 miesięcy
    'h2h_very_recent_multiplier': 2.0, # Mnożnik dla meczów z ostatnich 6 miesięcy
    'h2h_dominance_bonus': 10.0,     # Bonus za całkowitą dominację (100% H2H)
    'h2h_quality_bonus': 5.0,        # Bonus za dominację w wynikach (2-0 vs 2-1)
    'h2h_max_points': 40.0,
    
    # Current Form scoring (30 pkt max)
    'form_base_points': 3.0,         # Punkty za każdą wygraną w ostatnich 10
    'form_recent_weight': 1.5,       # Ostatnie 3 mecze liczą się bardziej
    'form_win_streak_bonus': 8.0,   # Bonus za serię 5+ zwycięstw
    'form_quality_bonus': 5.0,       # Bonus za wygrane z top zawodnikami
    'form_max_points': 30.0,
    'fatigue_penalty': 5.0,          # Kara za zmęczenie (5+ meczów w tydzień)
    'freshness_bonus': 3.0,          # Bonus za świeżość (optymalna częstotliwość)
    
    # Surface Form scoring (20 pkt max)
    'surface_winrate_multiplier': 25.0,  # Mnożnik różnicy win rate
    'surface_specialist_bonus': 8.0,     # Bonus dla specjalisty (>80% WR)
    'surface_consistency_bonus': 5.0,    # Bonus za grę na tej nawierzchni (10+ meczów)
    'surface_transition_bonus': 5.0,     # Bonus za rozgrzanie na nawierzchni
    'surface_max_points': 20.0,
    
    # Momentum scoring (10 pkt max)
    'momentum_streak_bonus': 5.0,        # Bonus za aktywną serię zwycięstw
    'momentum_confidence_bonus': 5.0,    # Bonus za zwycięstwa w tie-breakach/setach
    'momentum_max_points': 10.0,
}

# Wagi dla różnych typów turniejów
TOURNAMENT_WEIGHTS = {
    'grand_slam': 1.5,      # Wimbledon, US Open, Roland Garros, Australian Open
    'masters_1000': 1.3,    # Indian Wells, Miami, Monte Carlo, Madrid, etc.
    'atp_500': 1.1,         # Rotterdam, Dubai, Barcelona, etc.
    'atp_250': 1.0,         # Standardowe turnieje
    'challenger': 0.8,      # Challenger level
    'unknown': 1.0          # Domyślnie
}

# Wykrywanie typów turniejów po nazwach
GRAND_SLAM_KEYWORDS = [
    'wimbledon', 'us open', 'roland garros', 'australian open', 
    'french open', 'open usa', 'open australii'
]

MASTERS_1000_KEYWORDS = [
    'indian wells', 'miami', 'monte carlo', 'madrid', 'rome', 
    'canada', 'montreal', 'toronto', 'cincinnati', 'shanghai', 
    'paris', 'masters'
]


# ==========================================
# KLASA: TennisMatchAnalyzerV3
# ==========================================

class TennisMatchAnalyzerV3:
    """Zaawansowana analiza meczów tenisowych - fokus na formę i H2H"""
    
    def __init__(self, config: Dict = None):
        self.config = config or SCORING_CONFIG
    
    
    def analyze_match(
        self,
        player_a: str,
        player_b: str,
        h2h_matches: List[Dict],  # Lista meczów H2H z datami
        form_a: List[Dict],       # [{'result': 'W', 'date': '2025-01-15', 'opponent_rank': 50}, ...]
        form_b: List[Dict],
        surface: str,             # 'clay', 'grass', 'hard'
        surface_stats_a: Dict[str, Dict],  # {'clay': {'wins': 20, 'total': 25, 'recent': [...]}, ...}
        surface_stats_b: Dict[str, Dict],
        tournament_info: str = '',  # Nazwa turnieju lub URL (do wykrycia poziomu)
        debug: bool = False,        # Tryb debugowania (szczegółowe logi)
    ) -> Dict:
        """
        Kompleksowa analiza meczu tenisowego V3
        
        Returns:
            {
                'qualifies': bool,
                'total_score': float,
                'confidence': str,  # 'very_high', 'high', 'medium', 'low'
                'breakdown': {...},
                'details': {...}
            }
        """
        
        result = {
            'qualifies': False,
            'total_score': 0.0,
            'confidence': 'low',
            'breakdown': {
                'h2h_score': 0.0,
                'current_form_score': 0.0,
                'surface_form_score': 0.0,
                'momentum_score': 0.0
            },
            'details': {
                'player_a': player_a,
                'player_b': player_b,
                'surface': surface,
                'factors_used': [],
                'warnings': []
            }
        }
        
        # 1. H2H Analysis (40 pkt max) - KLUCZOWY CZYNNIK
        h2h_score = self._analyze_h2h_advanced(h2h_matches, player_a, player_b)
        result['breakdown']['h2h_score'] = h2h_score
        result['total_score'] += h2h_score
        if abs(h2h_score) > 0:
            result['details']['factors_used'].append('h2h')
            result['details']['h2h_matches_count'] = len(h2h_matches)
        
        # 2. Current Form Analysis (30 pkt max)
        if form_a and form_b:
            form_score = self._analyze_current_form(form_a, form_b)
            result['breakdown']['current_form_score'] = form_score
            result['total_score'] += form_score
            result['details']['factors_used'].append('current_form')
        else:
            result['details']['warnings'].append('missing_form_data')
        
        # 3. Surface Form Analysis (20 pkt max) - BARDZO WAŻNY
        if surface and surface_stats_a and surface_stats_b:
            surface_score = self._analyze_surface_form(
                surface, surface_stats_a, surface_stats_b, form_a, form_b
            )
            result['breakdown']['surface_form_score'] = surface_score
            result['total_score'] += surface_score
            result['details']['factors_used'].append('surface_form')
        else:
            result['details']['warnings'].append('missing_surface_data')
        
        # 4. Momentum Analysis (10 pkt max)
        if form_a and form_b:
            momentum_score = self._analyze_momentum(form_a, form_b)
            result['breakdown']['momentum_score'] = momentum_score
            result['total_score'] += momentum_score
            result['details']['factors_used'].append('momentum')
        
        # Wykryj typ turnieju i zastosuj wagę
        tournament_tier = self._detect_tournament_tier(tournament_info)
        tournament_weight = TOURNAMENT_WEIGHTS.get(tournament_tier, 1.0)
        result['details']['tournament_tier'] = tournament_tier
        result['details']['tournament_weight'] = tournament_weight
        
        # Zastosuj wagę turnieju do total_score
        if tournament_weight != 1.0:
            result['total_score'] *= tournament_weight
            result['details']['score_before_tournament_weight'] = result['total_score'] / tournament_weight
        
        # Określenie pewności predykcji
        abs_score = abs(result['total_score'])
        
        # Adaptacyjny próg (jeśli włączony)
        if self.config.get('adaptive_threshold', True):
            threshold = self._calculate_adaptive_threshold(result)
        else:
            threshold = self.config['threshold']
        
        result['details']['threshold_used'] = threshold
        result['qualifies'] = abs_score >= threshold
        
        # Poziomy pewności
        if abs_score >= 60:
            result['confidence'] = 'very_high'
        elif abs_score >= 50:
            result['confidence'] = 'high'
        elif abs_score >= 40:
            result['confidence'] = 'medium'
        else:
            result['confidence'] = 'low'
        
        # Określ faworyta
        if result['total_score'] < 0:
            result['details']['favorite'] = 'player_b'
            result['details']['favorite_score'] = abs_score
        elif result['total_score'] > 0:
            result['details']['favorite'] = 'player_a'
            result['details']['favorite_score'] = abs_score
        else:
            result['details']['favorite'] = 'even'
            result['details']['favorite_score'] = 0.0
        
        # Oblicz prawdopodobieństwo wygranej
        win_prob = self._calculate_win_probability(result['total_score'])
        result['details']['win_probability'] = win_prob
        result['details']['win_probability_pct'] = f"{win_prob*100:.1f}%"
        
        # Debug mode
        if debug:
            self._print_debug_breakdown(result)
        
        return result
    
    
    def _analyze_h2h_advanced(
        self, 
        h2h_matches: List[Dict], 
        player_a: str, 
        player_b: str
    ) -> float:
        """
        Zaawansowana analiza H2H z wagą czasową
        
        Args:
            h2h_matches: [
                {
                    'date': '2025-01-15',
                    'winner': 'player_a' lub 'player_b',
                    'score': '2-1',
                    'surface': 'clay'
                },
                ...
            ]
        
        Returns:
            Punkty (-40 do +40)
        """
        if not h2h_matches:
            return 0.0
        
        total_points = 0.0
        wins_a = 0
        wins_b = 0
        
        # Dzisiejsza data do obliczania wagi czasowej
        today = datetime.now()
        
        for match in h2h_matches:
            winner = match.get('winner')
            if not winner:
                continue
            
            # Bazowe punkty za wygraną
            base_points = self.config['h2h_base_points']
            
            # Waga czasowa - nowsze mecze liczą się bardziej
            match_date_str = match.get('date')
            if match_date_str:
                try:
                    match_date = datetime.strptime(match_date_str, '%d.%m.%y')
                    days_ago = (today - match_date).days
                    
                    # Ostatnie 6 miesięcy - najważniejsze
                    if days_ago <= 180:
                        base_points *= self.config['h2h_very_recent_multiplier']
                    # Ostatnie 12 miesięcy - ważne
                    elif days_ago <= 365:
                        base_points *= self.config['h2h_recent_multiplier']
                    # Starsze mecze - mniejsza waga (0.5x)
                    elif days_ago > 730:  # 2+ lata temu
                        base_points *= 0.5
                except:
                    pass  # Jeśli nie ma daty, użyj bazowej wagi
            
            # Dodaj punkty dla zwycięzcy
            if winner == 'player_a' or winner == 'home':
                total_points += base_points
                wins_a += 1
            else:
                total_points -= base_points
                wins_b += 1
        
        # Bonus za całkowitą dominację (wszystkie wygrane)
        total_matches = wins_a + wins_b
        if total_matches >= 3:  # Minimum 3 mecze
            if wins_a == total_matches:
                total_points += self.config['h2h_dominance_bonus']
            elif wins_b == total_matches:
                total_points -= self.config['h2h_dominance_bonus']
        
        # Analiza JAKOŚCI dominacji (jak łatwo wygrywał)
        if total_matches > 0:
            dominance_level = self._calculate_h2h_dominance_level(h2h_matches, player_a, player_b)
            
            # Jeśli player_a wygrywał łatwo (dominance > 0.8)
            if dominance_level > 0.8 and wins_a > wins_b:
                total_points += self.config.get('h2h_quality_bonus', 5.0)
            # Jeśli player_b wygrywał łatwo
            elif dominance_level < -0.8 and wins_b > wins_a:
                total_points -= self.config.get('h2h_quality_bonus', 5.0)
        
        # Cap do maksimum/minimum
        if total_points > 0:
            return min(total_points, self.config['h2h_max_points'])
        else:
            return max(total_points, -self.config['h2h_max_points'])
    
    
    def _analyze_current_form(
        self, 
        form_a: List[Dict], 
        form_b: List[Dict]
    ) -> float:
        """
        Analiza aktualnej formy (ostatnie 10 meczów)
        
        Args:
            form_a: [
                {
                    'result': 'W' lub 'L',
                    'date': '2025-01-15',
                    'opponent_rank': 50,  # opcjonalne
                    'score': '2-0'  # opcjonalne
                },
                ...
            ]
        
        Returns:
            Punkty (-30 do +30)
        """
        # Weź ostatnie 10 meczów
        form_a = form_a[-10:] if len(form_a) > 10 else form_a
        form_b = form_b[-10:] if len(form_b) > 10 else form_b
        
        if not form_a or not form_b:
            return 0.0
        
        # Bazowa analiza - wygrane vs przegrane
        wins_a = sum(1 for m in form_a if m.get('result') == 'W')
        wins_b = sum(1 for m in form_b if m.get('result') == 'W')
        
        # Bazowe punkty za przewagę w formie
        points = (wins_a - wins_b) * self.config['form_base_points']
        
        # Ostatnie 3 mecze liczą się bardziej (aktualna forma)
        recent_a = form_a[-3:] if len(form_a) >= 3 else form_a
        recent_b = form_b[-3:] if len(form_b) >= 3 else form_b
        
        recent_wins_a = sum(1 for m in recent_a if m.get('result') == 'W')
        recent_wins_b = sum(1 for m in recent_b if m.get('result') == 'W')
        
        # Dodatkowe punkty za dobrą aktualną formę
        if recent_wins_a == 3 and recent_wins_b <= 1:
            points += 5.0  # Świetna forma A, słaba B
        elif recent_wins_b == 3 and recent_wins_a <= 1:
            points -= 5.0  # Świetna forma B, słaba A
        
        # Bonus za serię zwycięstw (5+ z rzędu)
        if self._has_win_streak(form_a, 5):
            points += self.config['form_win_streak_bonus']
        if self._has_win_streak(form_b, 5):
            points -= self.config['form_win_streak_bonus']
        
        # Bonus za jakość wygranych (przeciwko wyżej notowanym)
        quality_a = self._calculate_form_quality(form_a)
        quality_b = self._calculate_form_quality(form_b)
        
        if quality_a > quality_b + 0.2:  # Znacząco lepsza jakość
            points += self.config['form_quality_bonus']
        elif quality_b > quality_a + 0.2:
            points -= self.config['form_quality_bonus']
        
        # Analiza zmęczenia/świeżości
        fatigue_a = self._analyze_fatigue(form_a)
        fatigue_b = self._analyze_fatigue(form_b)
        points += (fatigue_a - fatigue_b)
        
        # Cap do maksimum/minimum
        if points > 0:
            return min(points, self.config['form_max_points'])
        else:
            return max(points, -self.config['form_max_points'])
    
    
    def _analyze_surface_form(
        self,
        surface: str,
        stats_a: Dict[str, Dict],
        stats_b: Dict[str, Dict],
        form_a: List[Dict] = None,
        form_b: List[Dict] = None
    ) -> float:
        """
        Analiza formy na konkretnej nawierzchni
        
        Args:
            surface: 'clay', 'grass', 'hard'
            stats_a: {
                'clay': {
                    'wins': 20,
                    'total': 25,
                    'win_rate': 0.80,
                    'recent_form': ['W', 'W', 'L', 'W', 'W']  # ostatnie 5 na tej nawierzchni
                },
                ...
            }
        
        Returns:
            Punkty (-20 do +20)
        """
        if surface not in stats_a or surface not in stats_b:
            return 0.0
        
        surface_a = stats_a[surface]
        surface_b = stats_b[surface]
        
        # Win rate na tej nawierzchni
        wr_a = surface_a.get('win_rate', 0.0)
        wr_b = surface_b.get('win_rate', 0.0)
        
        # Bazowe punkty z różnicy win rate
        advantage = wr_a - wr_b
        points = advantage * self.config['surface_winrate_multiplier']
        
        # Bonus dla specjalisty (>80% WR i znacząca przewaga)
        if wr_a >= 0.80 and advantage >= 0.15:
            points += self.config['surface_specialist_bonus']
        elif wr_b >= 0.80 and advantage <= -0.15:
            points -= self.config['surface_specialist_bonus']
        
        # Bonus za doświadczenie na nawierzchni (10+ meczów)
        total_a = surface_a.get('total', 0)
        total_b = surface_b.get('total', 0)
        
        if total_a >= 10 and total_b < 5:
            points += self.config['surface_consistency_bonus']
        elif total_b >= 10 and total_a < 5:
            points -= self.config['surface_consistency_bonus']
        
        # Aktualna forma na tej nawierzchni (jeśli dostępna)
        recent_a = surface_a.get('recent_form', [])
        recent_b = surface_b.get('recent_form', [])
        
        if recent_a and recent_b:
            recent_wr_a = sum(1 for r in recent_a if r == 'W') / len(recent_a)
            recent_wr_b = sum(1 for r in recent_b if r == 'W') / len(recent_b)
            
            # Dodatkowe punkty za dobrą aktualną formę na nawierzchni
            recent_advantage = recent_wr_a - recent_wr_b
            points += recent_advantage * 10
        
        # Analiza przejść między nawierzchniami (czy zawodnik jest "rozgrzany" na tej nawierzchni)
        if form_a and form_b:
            transition_a = self._analyze_surface_transition(surface, form_a)
            transition_b = self._analyze_surface_transition(surface, form_b)
            points += (transition_a - transition_b)
        
        # Cap do maksimum/minimum
        if points > 0:
            return min(points, self.config['surface_max_points'])
        else:
            return max(points, -self.config['surface_max_points'])
    
    
    def _analyze_momentum(
        self,
        form_a: List[Dict],
        form_b: List[Dict]
    ) -> float:
        """
        Analiza momentum (seria zwycięstw, pewność siebie)
        
        Returns:
            Punkty (-10 do +10)
        """
        points = 0.0
        
        # Aktywna seria zwycięstw
        streak_a = self._get_current_streak(form_a)
        streak_b = self._get_current_streak(form_b)
        
        if streak_a >= 3 and streak_b <= 0:
            points += self.config['momentum_streak_bonus']
        elif streak_b >= 3 and streak_a <= 0:
            points -= self.config['momentum_streak_bonus']
        
        # Pewność siebie - łatwe wygrane (2-0) vs trudne (2-1, tie-breaki)
        confidence_a = self._calculate_confidence(form_a)
        confidence_b = self._calculate_confidence(form_b)
        
        if confidence_a > confidence_b + 0.3:
            points += self.config['momentum_confidence_bonus']
        elif confidence_b > confidence_a + 0.3:
            points -= self.config['momentum_confidence_bonus']
        
        # Cap do maksimum/minimum
        if points > 0:
            return min(points, self.config['momentum_max_points'])
        else:
            return max(points, -self.config['momentum_max_points'])
    
    
    # ========== HELPER FUNCTIONS ==========
    
    def _has_win_streak(self, form: List[Dict], length: int) -> bool:
        """Sprawdź czy jest seria N zwycięstw z rzędu"""
        if len(form) < length:
            return False
        
        recent = form[-length:]
        return all(m.get('result') == 'W' for m in recent)
    
    
    def _calculate_form_quality(self, form: List[Dict]) -> float:
        """
        Oblicz jakość formy na podstawie poziomu przeciwników
        
        Returns:
            0.0-1.0 (wyższa wartość = lepsza jakość)
        """
        if not form:
            return 0.5
        
        quality_scores = []
        for match in form:
            if match.get('result') != 'W':
                continue
            
            opp_rank = match.get('opponent_rank')
            if opp_rank:
                # Wygrana z top 10 = 1.0, z top 50 = 0.8, z top 100 = 0.6
                if opp_rank <= 10:
                    quality_scores.append(1.0)
                elif opp_rank <= 50:
                    quality_scores.append(0.8)
                elif opp_rank <= 100:
                    quality_scores.append(0.6)
                else:
                    quality_scores.append(0.4)
        
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.5
    
    
    def _get_current_streak(self, form: List[Dict]) -> int:
        """Pobierz aktualną serię zwycięstw (od końca)"""
        streak = 0
        for match in reversed(form):
            if match.get('result') == 'W':
                streak += 1
            else:
                break
        return streak
    
    
    def _calculate_confidence(self, form: List[Dict]) -> float:
        """
        Oblicz pewność siebie na podstawie wyników setowych
        
        Returns:
            0.0-1.0 (wyższa wartość = większa pewność)
        """
        if not form:
            return 0.5
        
        confidence_scores = []
        for match in form:
            if match.get('result') != 'W':
                continue
            
            score = match.get('score', '')
            # Łatwa wygrana 2-0 = 1.0
            if '2-0' in score:
                confidence_scores.append(1.0)
            # Trudna wygrana 2-1 = 0.6
            elif '2-1' in score:
                confidence_scores.append(0.6)
            # Inne = 0.8
            else:
                confidence_scores.append(0.8)
        
        return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
    
    
    # ========== NOWE METODY POMOCNICZE - ULEPSZENIA V3 ===========
    
    def _detect_tournament_tier(self, tournament_info: str) -> str:
        """
        Wykryj poziom turnieju z nazwy lub URL
        
        Returns:
            'grand_slam', 'masters_1000', 'atp_500', 'atp_250', 'challenger', 'unknown'
        """
        if not tournament_info:
            return 'unknown'
        
        info_lower = tournament_info.lower()
        
        # Grand Slam
        if any(keyword in info_lower for keyword in GRAND_SLAM_KEYWORDS):
            return 'grand_slam'
        
        # Masters 1000
        if any(keyword in info_lower for keyword in MASTERS_1000_KEYWORDS):
            return 'masters_1000'
        
        # ATP 500 (można rozszerzyć o więcej turniejów)
        if 'atp 500' in info_lower or 'atp500' in info_lower:
            return 'atp_500'
        
        # Challenger
        if 'challenger' in info_lower:
            return 'challenger'
        
        # Domyślnie ATP 250
        return 'atp_250'
    
    
    def _analyze_fatigue(self, form: List[Dict]) -> float:
        """
        Wykrywa zmęczenie na podstawie częstotliwości meczów
        
        Returns:
            -5 do +5 punktów
            NEGATYWNE = zmęczony
            POZYTYWNE = świeży
        """
        if not form:
            return 0.0
        
        # Policz mecze w ostatnich 7 i 14 dniach
        today = datetime.now()
        
        matches_last_7d = 0
        matches_last_14d = 0
        
        for match in form:
            date_str = match.get('date')
            if not date_str:
                continue
            
            try:
                # Obsługa różnych formatów daty
                for date_format in ['%d.%m.%y', '%d.%m.%Y', '%Y-%m-%d']:
                    try:
                        match_date = datetime.strptime(date_str, date_format)
                        break
                    except ValueError:
                        continue
                else:
                    continue
                
                days_ago = (today - match_date).days
                
                if days_ago <= 7:
                    matches_last_7d += 1
                if days_ago <= 14:
                    matches_last_14d += 1
            except:
                continue
        
        # SCENARIUSZE:
        # 5+ meczów w 7 dni = ZMĘCZONY (-5 pkt)
        if matches_last_7d >= 5:
            return -self.config.get('fatigue_penalty', 5.0)
        
        # 3-4 mecze w 7 dni = INTENSYWNY (-2 pkt)
        if matches_last_7d >= 3:
            return -2.0
        
        # 0 meczów w 14 dni = ZA DŁUGA PRZERWA (-3 pkt)
        if matches_last_14d == 0:
            return -3.0
        
        # 1-2 mecze w 7 dni = ŚWIEŻY (+3 pkt)
        if 1 <= matches_last_7d <= 2:
            return self.config.get('freshness_bonus', 3.0)
        
        return 0.0
    
    
    def _calculate_h2h_dominance_level(
        self, 
        h2h_matches: List[Dict],
        player_a: str,
        player_b: str
    ) -> float:
        """
        Oblicz poziom dominacji w H2H (nie tylko kto wygrał, ale JAK wygrywał)
        
        Returns:
            -1.0 do +1.0 
            +1.0 = player_a dominuje (łatwe wygrane 2-0, 3-0)
            -1.0 = player_b dominuje
            0.0 = wyrównane mecze
        """
        if not h2h_matches:
            return 0.0
        
        dominance_scores = []
        
        for match in h2h_matches:
            score = match.get('score', '')
            winner = match.get('winner', '')
            
            if not winner:
                continue
            
            # Określ poziom dominacji w tym meczu
            match_dominance = 0.0
            
            # 2-0, 3-0 = dominacja (1.0)
            if '2-0' in score or '3-0' in score:
                match_dominance = 1.0
            # 2-1, 3-1 = zwykła wygrana (0.6)
            elif '2-1' in score or '3-1' in score:
                match_dominance = 0.6
            # 3-2 = wyrównany mecz (0.5)
            elif '3-2' in score:
                match_dominance = 0.5
            else:
                match_dominance = 0.7  # Domyślnie
            
            # Przypisz dominację do odpowiedniego zawodnika
            if winner == 'player_a' or winner == 'home':
                dominance_scores.append(match_dominance)
            else:
                dominance_scores.append(-match_dominance)
        
        if not dominance_scores:
            return 0.0
        
        # Średni poziom dominacji
        avg_dominance = sum(dominance_scores) / len(dominance_scores)
        
        return avg_dominance
    
    
    def _analyze_surface_transition(
        self,
        current_surface: str,
        form: List[Dict]
    ) -> float:
        """
        Wykrywa czy zawodnik jest 'rozgrzany' na tej nawierzchni
        
        Returns:
            -5 do +5 punktów
        """
        if not form or not current_surface:
            return 0.0
        
        # Sprawdź ostatnie 5 meczów - ile było na current_surface?
        recent_5 = form[-5:] if len(form) >= 5 else form
        
        matches_on_current_surface = sum(
            1 for m in recent_5 
            if m.get('surface', '').lower() == current_surface.lower()
        )
        
        # SCENARIUSZE:
        # 5/5 na tej nawierzchni = ROZGRZANY (+5 pkt)
        if matches_on_current_surface == len(recent_5) and len(recent_5) == 5:
            return self.config.get('surface_transition_bonus', 5.0)
        
        # 3-4/5 na tej nawierzchni = PRZYZWYCZAJONY (+3 pkt)
        if matches_on_current_surface >= 3:
            return 3.0
        
        # 0-1/5 na tej nawierzchni = PRZEJŚCIE (-3 pkt)
        if matches_on_current_surface <= 1:
            return -3.0
        
        return 0.0
    
    
    def _calculate_adaptive_threshold(self, analysis: Dict) -> float:
        """
        Dostosuj próg w zależności od dostępności danych
        
        Im więcej danych, tym można być bardziej wymagającym.
        Im mniej danych, tym niższy próg (dajemy szansę).
        """
        base_threshold = self.config['threshold']  # 45
        
        factors_count = len(analysis['details']['factors_used'])
        
        # Pełne dane (4 czynniki: h2h, form, surface, momentum)
        if factors_count == 4:
            return base_threshold
        
        # Brakujące dane - obniż próg proporcjonalnie
        # 3 czynniki: próg 40
        # 2 czynniki: próg 35
        # 1 czynnik: próg 30
        adjustment = (4 - factors_count) * 5
        
        # Ale tylko jeśli mamy H2H (najważniejszy czynnik)
        if 'h2h' in analysis['details']['factors_used']:
            return base_threshold - adjustment
        else:
            # Bez H2H - wyższy próg (mniej pewności)
            return base_threshold + 5
    
    
    def _calculate_win_probability(self, total_score: float) -> float:
        """
        Konwertuj scoring na prawdopodobieństwo wygranej
        
        Używa sigmoid function dla smooth transition
        
        Returns:
            0.5-0.95 (50%-95%) - nigdy 100% pewności
        """
        import math
        
        # Sigmoid: 1 / (1 + e^(-x))
        # Scaling: score 50 = 75% probability
        #          score 70 = 90% probability
        #          score 30 = 60% probability
        
        # Przeskaluj score do -5 to +5 range
        scaled_score = (abs(total_score) - 45) / 10
        
        # Sigmoid
        try:
            probability = 1 / (1 + math.exp(-scaled_score))
        except:
            probability = 0.5
        
        # Clamp to 50-95% range (nigdy 100%)
        probability = max(0.50, min(0.95, probability))
        
        return probability
    
    
    def _print_debug_breakdown(self, analysis: Dict):
        """Szczegółowe wyjaśnienie scoring dla debugowania"""
        print("\n" + "="*70)
        print(f"🎾 DEBUG: {analysis['details']['player_a']} vs {analysis['details']['player_b']}")
        print("="*70)
        
        bd = analysis['breakdown']
        details = analysis['details']
        
        print(f"\n📊 PUNKTACJA:")
        print(f"   H2H (40%):              {bd['h2h_score']:+.1f} / 40.0 pkt")
        print(f"   Forma aktualna (30%):   {bd['current_form_score']:+.1f} / 30.0 pkt")
        print(f"   Forma na nawierzchni:   {bd['surface_form_score']:+.1f} / 20.0 pkt")
        print(f"   Momentum (10%):         {bd['momentum_score']:+.1f} / 10.0 pkt")
        print(f"   " + "-" * 50)
        print(f"   SUMA BAZOWA:            {sum(bd.values()):+.1f} / 100.0 pkt")
        
        # Informacje o turnieju
        if 'tournament_tier' in details:
            print(f"\n🏆 TURNIEJ:")
            print(f"   Typ: {details['tournament_tier']}")
            print(f"   Waga: {details['tournament_weight']:.2f}x")
            if 'score_before_tournament_weight' in details:
                print(f"   Score przed wagą: {details['score_before_tournament_weight']:+.1f}")
        
        print(f"\n🎯 WYNIK KOŃCOWY:")
        print(f"   Total Score:  {analysis['total_score']:+.1f} / 100.0 pkt")
        print(f"   Próg użyty:   {details.get('threshold_used', 45):.1f} pkt")
        print(f"   Pewność:      {analysis['confidence'].upper()}")
        print(f"   Prawdopodobieństwo: {details.get('win_probability_pct', 'N/A')}")
        
        # Faworyt
        fav = details.get('favorite', 'unknown')
        fav_score = details.get('favorite_score', 0)
        print(f"\n👤 FAWORYT:")
        print(f"   {fav} ({fav_score:.1f} pkt)")
        
        # Kwalifikacja
        if analysis['qualifies']:
            print(f"\n✅ KWALIFIKUJE SIĘ!")
        else:
            print(f"\n❌ NIE KWALIFIKUJE (za niski scoring)")
        
        # Ostrzeżenia
        warnings = details.get('warnings', [])
        if warnings:
            print(f"\n⚠️  Ostrzeżenia:")
            for w in warnings:
                print(f"   - {w}")
        
        # Użyte czynniki
        print(f"\n📋 Użyte czynniki: {', '.join(details.get('factors_used', []))}")
        
        print("="*70 + "\n")
    
    
    def format_analysis(self, analysis: Dict) -> str:
        """Formatuje wyniki analizy do czytelnego tekstu"""
        lines = []
        
        lines.append(f"🎾 ANALIZA V3: {analysis['details']['player_a']} vs {analysis['details']['player_b']}")
        lines.append("=" * 70)
        
        # Breakdown
        breakdown = analysis['breakdown']
        lines.append(f"\n📊 PUNKTACJA:")
        lines.append(f"   H2H (40%):           {breakdown['h2h_score']:+.1f} / 40.0 pkt")
        lines.append(f"   Forma aktualna (30%): {breakdown['current_form_score']:+.1f} / 30.0 pkt")
        lines.append(f"   Forma na nawierzchni: {breakdown['surface_form_score']:+.1f} / 20.0 pkt")
        lines.append(f"   Momentum (10%):       {breakdown['momentum_score']:+.1f} / 10.0 pkt")
        lines.append(f"   " + "-" * 50)
        lines.append(f"   RAZEM:               {analysis['total_score']:+.1f} / 100.0 pkt")
        
        # Wynik
        lines.append(f"\n🎯 WYNIK:")
        lines.append(f"   Pewność: {analysis['confidence'].upper()}")
        
        if analysis['qualifies']:
            fav = analysis['details'].get('favorite', 'unknown')
            fav_score = analysis['details'].get('favorite_score', 0)
            lines.append(f"   ✅ KWALIFIKUJE SIĘ - Faworytem: {fav} ({fav_score:.1f} pkt)")
        else:
            lines.append(f"   ❌ NIE KWALIFIKUJE (próg: {self.config['threshold']} pkt)")
        
        # Ostrzeżenia
        warnings = analysis['details'].get('warnings', [])
        if warnings:
            lines.append(f"\n⚠️  Ostrzeżenia:")
            for w in warnings:
                lines.append(f"   - {w}")
        
        return '\n'.join(lines)


# ==========================================
# PRZYKŁAD UŻYCIA
# ==========================================

if __name__ == '__main__':
    analyzer = TennisMatchAnalyzerV3()
    
    # Przykład: Alcaraz vs Rune z pełnymi danymi + nowe funkcje
    print("="*70)
    print("🎾 TENNIS ANALYZER V3 - ENHANCED VERSION")
    print("="*70)
    print("\nTest 1: Grand Slam mecz z pełnymi danymi\n")
    
    analysis = analyzer.analyze_match(
        player_a='Carlos Alcaraz',
        player_b='Holger Rune',
        h2h_matches=[
            {'date': '15.08.24', 'winner': 'player_a', 'score': '2-0', 'surface': 'hard'},
            {'date': '20.05.24', 'winner': 'player_a', 'score': '2-1', 'surface': 'clay'},
            {'date': '10.03.24', 'winner': 'player_a', 'score': '2-0', 'surface': 'hard'},
            {'date': '15.07.23', 'winner': 'player_b', 'score': '2-1', 'surface': 'grass'},
        ],
        form_a=[
            {'result': 'W', 'date': '01.10.25', 'opponent_rank': 15, 'score': '2-0', 'surface': 'hard'},
            {'result': 'W', 'date': '28.09.25', 'opponent_rank': 22, 'score': '2-0', 'surface': 'hard'},
            {'result': 'W', 'date': '25.09.25', 'opponent_rank': 8, 'score': '2-1', 'surface': 'hard'},
            {'result': 'L', 'date': '20.09.25', 'opponent_rank': 3, 'score': '0-2', 'surface': 'hard'},
            {'result': 'W', 'date': '18.09.25', 'opponent_rank': 45, 'score': '2-0', 'surface': 'hard'},
            {'result': 'W', 'date': '15.09.25', 'opponent_rank': 30, 'score': '2-0', 'surface': 'clay'},
            {'result': 'W', 'date': '12.09.25', 'opponent_rank': 18, 'score': '2-1', 'surface': 'clay'},
            {'result': 'W', 'date': '10.09.25', 'opponent_rank': 55, 'score': '2-0', 'surface': 'clay'},
            {'result': 'L', 'date': '05.09.25', 'opponent_rank': 12, 'score': '1-2', 'surface': 'clay'},
            {'result': 'W', 'date': '01.09.25', 'opponent_rank': 40, 'score': '2-0', 'surface': 'grass'},
        ],
        form_b=[
            {'result': 'L', 'date': '02.10.25', 'opponent_rank': 10, 'score': '0-2', 'surface': 'clay'},
            {'result': 'W', 'date': '29.09.25', 'opponent_rank': 35, 'score': '2-1', 'surface': 'hard'},
            {'result': 'L', 'date': '26.09.25', 'opponent_rank': 5, 'score': '1-2', 'surface': 'hard'},
            {'result': 'W', 'date': '22.09.25', 'opponent_rank': 50, 'score': '2-0', 'surface': 'hard'},
            {'result': 'L', 'date': '19.09.25', 'opponent_rank': 8, 'score': '0-2', 'surface': 'hard'},
            {'result': 'W', 'date': '16.09.25', 'opponent_rank': 60, 'score': '2-0', 'surface': 'hard'},
            {'result': 'W', 'date': '13.09.25', 'opponent_rank': 25, 'score': '2-1', 'surface': 'grass'},
            {'result': 'L', 'date': '11.09.25', 'opponent_rank': 4, 'score': '1-2', 'surface': 'grass'},
            {'result': 'W', 'date': '08.09.25', 'opponent_rank': 70, 'score': '2-0', 'surface': 'clay'},
            {'result': 'W', 'date': '05.09.25', 'opponent_rank': 45, 'score': '2-0', 'surface': 'clay'},
        ],
        surface='hard',
        surface_stats_a={
            'hard': {
                'wins': 45,
                'total': 55,
                'win_rate': 0.82,
                'recent_form': ['W', 'W', 'W', 'L', 'W']
            },
            'clay': {'wins': 30, 'total': 40, 'win_rate': 0.75},
            'grass': {'wins': 15, 'total': 20, 'win_rate': 0.75}
        },
        surface_stats_b={
            'hard': {
                'wins': 32,
                'total': 50,
                'win_rate': 0.64,
                'recent_form': ['L', 'W', 'L', 'W', 'L']
            },
            'clay': {'wins': 25, 'total': 35, 'win_rate': 0.71},
            'grass': {'wins': 12, 'total': 18, 'win_rate': 0.67}
        },
        tournament_info='US Open 2025',  # Grand Slam = 1.5x waga
        debug=True  # Włącz szczegółowy debug
    )
    
    print(analyzer.format_analysis(analysis))
    print()
    print(f"📊 NOWE FEATURES:")
    print(f"   Kwalifikuje się: {analysis['qualifies']}")
    print(f"   Wynik końcowy: {analysis['total_score']:+.1f}/100 pkt")
    print(f"   Pewność: {analysis['confidence']}")
    print(f"   Prawdopodobieństwo: {analysis['details']['win_probability_pct']}")
    print(f"   Typ turnieju: {analysis['details']['tournament_tier']}")
    print(f"   Waga turnieju: {analysis['details']['tournament_weight']}x")
    print(f"   Próg użyty: {analysis['details']['threshold_used']:.1f} pkt")
