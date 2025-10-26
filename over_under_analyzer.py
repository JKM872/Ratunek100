"""
Over/Under Statistics Analyzer
Analizuje statystyki Over/Under dla różnych sportów:
- Football: Over/Under goals, BTTS (Both Teams To Score)
- Basketball: Over/Under points
- Handball: Over/Under goals
- Volleyball: Over/Under sets, Over/Under points
- Hockey: Over/Under goals
- Tennis: Over/Under sets, Over/Under games
"""

from typing import Dict, List, Optional
import re

# ============================================================================
# KONFIGURACJA LINII DLA KAŻDEGO SPORTU
# ============================================================================

SPORT_LINES = {
    'football': {
        'goals': 2.5,  # Najpopularniejsza linia
        'btts': True   # Both Teams To Score
    },
    'basketball': {
        'points': 220.5  # Domyślna (dostosuje się do ligi)
    },
    'handball': {
        'goals': 55.5   # Typowa linia dla piłki ręcznej
    },
    'volleyball': {
        'sets': 4.5,    # Over/Under setów
        'points': 195.5  # Over/Under punktów
    },
    'hockey': {
        'goals': 5.5    # Typowa linia dla hokeja
    },
    'tennis': {
        'sets': 2.5,    # Best of 3: Over 2.5 = 3 sety
        'games': 22.5   # Łączna liczba gemów
    }
}

# Threshold: 60% meczów musi przekroczyć linię
OVER_UNDER_THRESHOLD = 0.60


# ============================================================================
# FUNKCJE POMOCNICZE - PARSOWANIE WYNIKÓW
# ============================================================================

def parse_score(score_str: str) -> Optional[tuple]:
    """
    Parsuje wynik meczu do tupli (home, away)
    
    Args:
        score_str: Wynik w formacie "3-1", "2:0", "95-102", etc.
    
    Returns:
        (home_score, away_score) lub None jeśli nie można sparsować
    """
    if not score_str or score_str == 'N/A':
        return None
    
    # Usuń whitespace i spróbuj różnych separatorów
    score_str = score_str.strip()
    
    # Spróbuj separatora "-" (np. "3-1")
    match = re.search(r'(\d+)\s*-\s*(\d+)', score_str)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    
    # Spróbuj separatora ":" (np. "2:0")
    match = re.search(r'(\d+)\s*:\s*(\d+)', score_str)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    
    return None


def count_goals_football(results: List[Dict]) -> Dict:
    """
    Zlicza statystyki bramek dla piłki nożnej
    
    Returns:
        {
            'over_2_5_count': 3,
            'total_matches': 5,
            'over_2_5_percentage': 60.0,
            'btts_count': 4,
            'btts_percentage': 80.0
        }
    """
    over_count = 0
    btts_count = 0
    total = 0
    
    for match in results:
        score = parse_score(match.get('score', ''))
        if not score:
            continue
        
        home, away = score
        total_goals = home + away
        total += 1
        
        # Over 2.5 goals
        if total_goals > 2.5:
            over_count += 1
        
        # BTTS (Both Teams To Score)
        if home > 0 and away > 0:
            btts_count += 1
    
    if total == 0:
        return {'over_2_5_count': 0, 'total_matches': 0, 'over_2_5_percentage': 0.0,
                'btts_count': 0, 'btts_percentage': 0.0}
    
    return {
        'over_2_5_count': over_count,
        'total_matches': total,
        'over_2_5_percentage': round((over_count / total) * 100, 1),
        'btts_count': btts_count,
        'btts_percentage': round((btts_count / total) * 100, 1)
    }


def count_points_basketball(results: List[Dict], line: float = 220.5) -> Dict:
    """
    Zlicza statystyki punktów dla koszykówki
    
    Args:
        line: Linia O/U (domyślnie 220.5)
    
    Returns:
        {
            'over_count': 4,
            'under_count': 1,
            'total_matches': 5,
            'over_percentage': 80.0,
            'under_percentage': 20.0,
            'line': 220.5
        }
    """
    over_count = 0
    under_count = 0
    total = 0
    
    for match in results:
        score = parse_score(match.get('score', ''))
        if not score:
            continue
        
        home, away = score
        total_points = home + away
        total += 1
        
        if total_points > line:
            over_count += 1
        else:
            under_count += 1
    
    if total == 0:
        return {
            'over_count': 0,
            'under_count': 0,
            'total_matches': 0,
            'over_percentage': 0.0,
            'under_percentage': 0.0,
            'line': line
        }
    
    return {
        'over_count': over_count,
        'under_count': under_count,
        'total_matches': total,
        'over_percentage': round((over_count / total) * 100, 1),
        'under_percentage': round((under_count / total) * 100, 1),
        'line': line
    }


def count_goals_handball_hockey(results: List[Dict], line: float = 55.5) -> Dict:
    """
    Zlicza statystyki bramek dla piłki ręcznej i hokeja
    
    Args:
        line: Linia O/U (55.5 dla handball, 5.5 dla hockey)
    """
    over_count = 0
    under_count = 0
    total = 0
    
    for match in results:
        score = parse_score(match.get('score', ''))
        if not score:
            continue
        
        home, away = score
        total_goals = home + away
        total += 1
        
        if total_goals > line:
            over_count += 1
        else:
            under_count += 1
    
    if total == 0:
        return {
            'over_count': 0,
            'under_count': 0,
            'total_matches': 0,
            'over_percentage': 0.0,
            'under_percentage': 0.0,
            'line': line
        }
    
    return {
        'over_count': over_count,
        'under_count': under_count,
        'total_matches': total,
        'over_percentage': round((over_count / total) * 100, 1),
        'under_percentage': round((under_count / total) * 100, 1),
        'line': line
    }


def count_sets_volleyball(results: List[Dict], line: float = 4.5) -> Dict:
    """
    Zlicza statystyki setów dla siatkówki
    
    Wynik siatkówki często w formacie "3-1" (sety) lub "(25-23, 23-25, 25-20, 25-18)"
    """
    over_count = 0
    under_count = 0
    total = 0
    
    for match in results:
        score = parse_score(match.get('score', ''))
        if not score:
            continue
        
        home_sets, away_sets = score
        total_sets = home_sets + away_sets
        total += 1
        
        if total_sets > line:
            over_count += 1
        else:
            under_count += 1
    
    if total == 0:
        return {
            'over_count': 0,
            'under_count': 0,
            'total_matches': 0,
            'over_percentage': 0.0,
            'under_percentage': 0.0,
            'line': line
        }
    
    return {
        'over_count': over_count,
        'under_count': under_count,
        'total_matches': total,
        'over_percentage': round((over_count / total) * 100, 1),
        'under_percentage': round((under_count / total) * 100, 1),
        'line': line
    }


def count_sets_tennis(results: List[Dict], line: float = 2.5) -> Dict:
    """
    Zlicza statystyki setów dla tenisa
    
    Args:
        line: 2.5 dla Best of 3, 3.5 dla Best of 5
    """
    over_count = 0
    under_count = 0
    total = 0
    
    for match in results:
        score = parse_score(match.get('score', ''))
        if not score:
            continue
        
        home_sets, away_sets = score
        total_sets = home_sets + away_sets
        total += 1
        
        if total_sets > line:
            over_count += 1
        else:
            under_count += 1
    
    if total == 0:
        return {
            'over_count': 0,
            'under_count': 0,
            'total_matches': 0,
            'over_percentage': 0.0,
            'under_percentage': 0.0,
            'line': line
        }
    
    return {
        'over_count': over_count,
        'under_count': under_count,
        'total_matches': total,
        'over_percentage': round((over_count / total) * 100, 1),
        'under_percentage': round((under_count / total) * 100, 1),
        'line': line
    }


# ============================================================================
# ANALIZATORY SPORT-SPECIFIC
# ============================================================================

def analyze_football_over_under(h2h_results: List[Dict], home_form: List[Dict], 
                                 away_form: List[Dict]) -> Dict:
    """
    Analizuje statystyki Over/Under dla piłki nożnej
    
    Returns:
        {
            'over_2_5_qualifies': True/False,
            'over_2_5_h2h_percentage': 80.0,
            'over_2_5_home_percentage': 60.0,
            'over_2_5_away_percentage': 60.0,
            'btts_qualifies': True/False,
            'btts_h2h_percentage': 80.0,
            'btts_home_percentage': 60.0,
            'btts_away_percentage': 60.0
        }
    """
    # Analiza H2H
    h2h_stats = count_goals_football(h2h_results)
    
    # Analiza formy gospodarzy
    home_stats = count_goals_football(home_form)
    
    # Analiza formy gości
    away_stats = count_goals_football(away_form)
    
    # Kwalifikacja Over 2.5: 60% w H2H + 60% w formie obu drużyn
    over_qualifies = (
        h2h_stats['over_2_5_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        home_stats['over_2_5_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        away_stats['over_2_5_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    # Kwalifikacja BTTS: 60% w H2H + 60% w formie obu drużyn
    btts_qualifies = (
        h2h_stats['btts_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        home_stats['btts_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        away_stats['btts_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    return {
        'over_2_5_qualifies': over_qualifies,
        'over_2_5_h2h_percentage': h2h_stats['over_2_5_percentage'],
        'over_2_5_h2h_count': f"{h2h_stats['over_2_5_count']}/{h2h_stats['total_matches']}",
        'over_2_5_home_percentage': home_stats['over_2_5_percentage'],
        'over_2_5_home_count': f"{home_stats['over_2_5_count']}/{home_stats['total_matches']}",
        'over_2_5_away_percentage': away_stats['over_2_5_percentage'],
        'over_2_5_away_count': f"{away_stats['over_2_5_count']}/{away_stats['total_matches']}",
        
        'btts_qualifies': btts_qualifies,
        'btts_h2h_percentage': h2h_stats['btts_percentage'],
        'btts_h2h_count': f"{h2h_stats['btts_count']}/{h2h_stats['total_matches']}",
        'btts_home_percentage': home_stats['btts_percentage'],
        'btts_home_count': f"{home_stats['btts_count']}/{home_stats['total_matches']}",
        'btts_away_percentage': away_stats['btts_percentage'],
        'btts_away_count': f"{away_stats['btts_count']}/{away_stats['total_matches']}"
    }


def analyze_basketball_over_under(h2h_results: List[Dict], home_form: List[Dict],
                                   away_form: List[Dict], line: float = 220.5) -> Dict:
    """Analizuje statystyki Over/Under dla koszykówki"""
    
    h2h_stats = count_points_basketball(h2h_results, line)
    home_stats = count_points_basketball(home_form, line)
    away_stats = count_points_basketball(away_form, line)
    
    # Sprawdź OVER
    qualifies_over = (
        h2h_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        home_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        away_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    # Sprawdź UNDER
    qualifies_under = (
        h2h_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        home_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        away_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    # Rekomendacja
    recommendation = None
    if qualifies_over and not qualifies_under:
        recommendation = 'OVER'
    elif qualifies_under and not qualifies_over:
        recommendation = 'UNDER'
    # Jeśli oba lub żadne - brak rekomendacji
    
    return {
        'qualifies': qualifies_over or qualifies_under,
        'recommendation': recommendation,
        'line': line,
        'line_type': 'points',
        'h2h_over_percentage': h2h_stats['over_percentage'],
        'h2h_under_percentage': h2h_stats['under_percentage'],
        'h2h_count': f"{h2h_stats['over_count']}/{h2h_stats['total_matches']}",
        'home_percentage': home_stats['over_percentage'] if recommendation == 'OVER' else home_stats['under_percentage'],
        'home_count': f"{home_stats['over_count']}/{home_stats['total_matches']}",
        'away_percentage': away_stats['over_percentage'] if recommendation == 'OVER' else away_stats['under_percentage'],
        'away_count': f"{away_stats['over_count']}/{away_stats['total_matches']}"
    }


def analyze_handball_over_under(h2h_results: List[Dict], home_form: List[Dict],
                                 away_form: List[Dict], line: float = 55.5) -> Dict:
    """Analizuje statystyki Over/Under dla piłki ręcznej"""
    
    h2h_stats = count_goals_handball_hockey(h2h_results, line)
    home_stats = count_goals_handball_hockey(home_form, line)
    away_stats = count_goals_handball_hockey(away_form, line)
    
    # Sprawdź OVER
    qualifies_over = (
        h2h_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        home_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        away_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    # Sprawdź UNDER
    qualifies_under = (
        h2h_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        home_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        away_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    # Rekomendacja
    recommendation = None
    if qualifies_over and not qualifies_under:
        recommendation = 'OVER'
    elif qualifies_under and not qualifies_over:
        recommendation = 'UNDER'
    
    return {
        'qualifies': qualifies_over or qualifies_under,
        'recommendation': recommendation,
        'line': line,
        'line_type': 'goals',
        'h2h_over_percentage': h2h_stats['over_percentage'],
        'h2h_under_percentage': h2h_stats['under_percentage'],
        'h2h_count': f"{h2h_stats['over_count']}/{h2h_stats['total_matches']}",
        'home_percentage': home_stats['over_percentage'] if recommendation == 'OVER' else home_stats['under_percentage'],
        'home_count': f"{home_stats['over_count']}/{home_stats['total_matches']}",
        'away_percentage': away_stats['over_percentage'] if recommendation == 'OVER' else away_stats['under_percentage'],
        'away_count': f"{away_stats['over_count']}/{away_stats['total_matches']}"
    }


def analyze_volleyball_over_under(h2h_results: List[Dict], home_form: List[Dict],
                                   away_form: List[Dict], line: float = 4.5) -> Dict:
    """Analizuje statystyki Over/Under dla siatkówki (sety)"""
    
    h2h_stats = count_sets_volleyball(h2h_results, line)
    home_stats = count_sets_volleyball(home_form, line)
    away_stats = count_sets_volleyball(away_form, line)
    
    # Sprawdź OVER
    qualifies_over = (
        h2h_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        home_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        away_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    # Sprawdź UNDER
    qualifies_under = (
        h2h_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        home_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        away_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    # Rekomendacja
    recommendation = None
    if qualifies_over and not qualifies_under:
        recommendation = 'OVER'
    elif qualifies_under and not qualifies_over:
        recommendation = 'UNDER'
    
    return {
        'qualifies': qualifies_over or qualifies_under,
        'recommendation': recommendation,
        'line': line,
        'line_type': 'sets',
        'h2h_over_percentage': h2h_stats['over_percentage'],
        'h2h_under_percentage': h2h_stats['under_percentage'],
        'h2h_count': f"{h2h_stats['over_count']}/{h2h_stats['total_matches']}",
        'home_percentage': home_stats['over_percentage'] if recommendation == 'OVER' else home_stats['under_percentage'],
        'home_count': f"{home_stats['over_count']}/{home_stats['total_matches']}",
        'away_percentage': away_stats['over_percentage'] if recommendation == 'OVER' else away_stats['under_percentage'],
        'away_count': f"{away_stats['over_count']}/{away_stats['total_matches']}"
    }


def analyze_hockey_over_under(h2h_results: List[Dict], home_form: List[Dict],
                               away_form: List[Dict], line: float = 5.5) -> Dict:
    """Analizuje statystyki Over/Under dla hokeja"""
    
    h2h_stats = count_goals_handball_hockey(h2h_results, line)
    home_stats = count_goals_handball_hockey(home_form, line)
    away_stats = count_goals_handball_hockey(away_form, line)
    
    # Sprawdź OVER
    qualifies_over = (
        h2h_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        home_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        away_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    # Sprawdź UNDER
    qualifies_under = (
        h2h_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        home_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        away_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    # Rekomendacja
    recommendation = None
    if qualifies_over and not qualifies_under:
        recommendation = 'OVER'
    elif qualifies_under and not qualifies_over:
        recommendation = 'UNDER'
    
    return {
        'qualifies': qualifies_over or qualifies_under,
        'recommendation': recommendation,
        'line': line,
        'line_type': 'goals',
        'h2h_over_percentage': h2h_stats['over_percentage'],
        'h2h_under_percentage': h2h_stats['under_percentage'],
        'h2h_count': f"{h2h_stats['over_count']}/{h2h_stats['total_matches']}",
        'home_percentage': home_stats['over_percentage'] if recommendation == 'OVER' else home_stats['under_percentage'],
        'home_count': f"{home_stats['over_count']}/{home_stats['total_matches']}",
        'away_percentage': away_stats['over_percentage'] if recommendation == 'OVER' else away_stats['under_percentage'],
        'away_count': f"{away_stats['over_count']}/{away_stats['total_matches']}"
    }


def analyze_tennis_over_under(h2h_results: List[Dict], player_a_form: List[Dict],
                               player_b_form: List[Dict], line: float = 2.5) -> Dict:
    """Analizuje statystyki Over/Under dla tenisa (sety)"""
    
    h2h_stats = count_sets_tennis(h2h_results, line)
    player_a_stats = count_sets_tennis(player_a_form, line)
    player_b_stats = count_sets_tennis(player_b_form, line)
    
    # Sprawdź OVER
    qualifies_over = (
        h2h_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        player_a_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        player_b_stats['over_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    # Sprawdź UNDER
    qualifies_under = (
        h2h_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        player_a_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100 and
        player_b_stats['under_percentage'] >= OVER_UNDER_THRESHOLD * 100
    )
    
    # Rekomendacja
    recommendation = None
    if qualifies_over and not qualifies_under:
        recommendation = 'OVER'
    elif qualifies_under and not qualifies_over:
        recommendation = 'UNDER'
    
    return {
        'qualifies': qualifies_over or qualifies_under,
        'recommendation': recommendation,
        'line': line,
        'line_type': 'sets',
        'h2h_over_percentage': h2h_stats['over_percentage'],
        'h2h_under_percentage': h2h_stats['under_percentage'],
        'h2h_count': f"{h2h_stats['over_count']}/{h2h_stats['total_matches']}",
        'player_a_percentage': player_a_stats['over_percentage'] if recommendation == 'OVER' else player_a_stats['under_percentage'],
        'player_a_count': f"{player_a_stats['over_count']}/{player_a_stats['total_matches']}",
        'player_b_percentage': player_b_stats['over_percentage'] if recommendation == 'OVER' else player_b_stats['under_percentage'],
        'player_b_count': f"{player_b_stats['over_count']}/{player_b_stats['total_matches']}"
    }


# ============================================================================
# GŁÓWNA FUNKCJA ANALIZY
# ============================================================================

def analyze_over_under(sport: str, h2h_results: List[Dict], 
                       home_form: List[Dict], away_form: List[Dict],
                       **kwargs) -> Dict:
    """
    Główna funkcja analizy Over/Under - wybiera właściwy analyzer dla sportu
    
    Args:
        sport: Nazwa sportu ('football', 'basketball', etc.)
        h2h_results: Lista wyników H2H między drużynami
        home_form: Lista ostatnich meczów gospodarzy
        away_form: Lista ostatnich meczów gości
        **kwargs: Dodatkowe parametry (np. line dla basketball)
    
    Returns:
        Dict z wynikami analizy O/U lub None jeśli sport nieobsługiwany
    """
    sport = sport.lower()
    
    if sport == 'football':
        return analyze_football_over_under(h2h_results, home_form, away_form)
    
    elif sport == 'basketball':
        line = kwargs.get('line', SPORT_LINES['basketball']['points'])
        return analyze_basketball_over_under(h2h_results, home_form, away_form, line)
    
    elif sport == 'handball':
        line = kwargs.get('line', SPORT_LINES['handball']['goals'])
        return analyze_handball_over_under(h2h_results, home_form, away_form, line)
    
    elif sport == 'volleyball':
        line = kwargs.get('line', SPORT_LINES['volleyball']['sets'])
        return analyze_volleyball_over_under(h2h_results, home_form, away_form, line)
    
    elif sport == 'hockey':
        line = kwargs.get('line', SPORT_LINES['hockey']['goals'])
        return analyze_hockey_over_under(h2h_results, home_form, away_form, line)
    
    elif sport == 'tennis':
        line = kwargs.get('line', SPORT_LINES['tennis']['sets'])
        return analyze_tennis_over_under(h2h_results, home_form, away_form, line)
    
    else:
        print(f"⚠️ Sport '{sport}' nie jest obsługiwany dla analizy Over/Under")
        return None


# ============================================================================
# FUNKCJE TESTOWE
# ============================================================================

if __name__ == '__main__':
    # Test z przykładowymi danymi
    print("="*70)
    print("🧪 TEST OVER/UNDER ANALYZER")
    print("="*70)
    
    # Przykładowe dane Football
    h2h_football = [
        {'score': '3-1'},  # 4 goals - Over 2.5 ✅, BTTS ✅
        {'score': '2-2'},  # 4 goals - Over 2.5 ✅, BTTS ✅
        {'score': '1-0'},  # 1 goal  - Under 2.5 ❌, BTTS ❌
        {'score': '3-2'},  # 5 goals - Over 2.5 ✅, BTTS ✅
        {'score': '2-1'}   # 3 goals - Over 2.5 ✅, BTTS ✅
    ]
    
    home_form_football = [
        {'score': '3-0'},  # Over 2.5 ✅
        {'score': '2-1'},  # Under 2.5 ❌
        {'score': '4-2'},  # Over 2.5 ✅
        {'score': '1-1'},  # Under 2.5 ❌
        {'score': '3-1'}   # Over 2.5 ✅
    ]
    
    away_form_football = [
        {'score': '2-2'},  # Over 2.5 ✅
        {'score': '1-3'},  # Over 2.5 ✅
        {'score': '3-1'},  # Over 2.5 ✅
        {'score': '0-0'},  # Under 2.5 ❌
        {'score': '2-1'}   # Under 2.5 ❌
    ]
    
    result = analyze_over_under('football', h2h_football, home_form_football, away_form_football)
    
    print("\n⚽ FOOTBALL - Over 2.5 Goals:")
    print(f"   H2H: {result['over_2_5_h2h_count']} ({result['over_2_5_h2h_percentage']}%)")
    print(f"   Home: {result['over_2_5_home_count']} ({result['over_2_5_home_percentage']}%)")
    print(f"   Away: {result['over_2_5_away_count']} ({result['over_2_5_away_percentage']}%)")
    print(f"   ✅ Qualifies: {result['over_2_5_qualifies']}")
    
    print("\n⚽ FOOTBALL - BTTS:")
    print(f"   H2H: {result['btts_h2h_count']} ({result['btts_h2h_percentage']}%)")
    print(f"   Home: {result['btts_home_count']} ({result['btts_home_percentage']}%)")
    print(f"   Away: {result['btts_away_count']} ({result['btts_away_percentage']}%)")
    print(f"   ✅ Qualifies: {result['btts_qualifies']}")
    
    print("\n" + "="*70)

