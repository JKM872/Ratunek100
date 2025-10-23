"""
🎾 Tennis Scraper V3 - Funkcje pomocnicze
==========================================
Dodatkowe funkcje do zbierania rozszerzonych danych dla Tennis Scoring V3

Wymagania:
- Selenium WebDriver
- BeautifulSoup4
- Requests (opcjonalne)
"""

import re
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ==========================================
# CACHE dla wydajności
# ==========================================

PLAYER_URL_CACHE = {}
PLAYER_DATA_CACHE = {}


# ==========================================
# 1. H2H Z DATAMI I SZCZEGÓŁAMI
# ==========================================

def extract_h2h_with_dates(soup: BeautifulSoup, player_a: str, player_b: str) -> List[Dict]:
    """
    Wydobywa H2H z datami, wynikami setowymi i nawierzchnią.
    
    Args:
        soup: BeautifulSoup object strony H2H
        player_a: Nazwa pierwszego zawodnika
        player_b: Nazwa drugiego zawodnika
    
    Returns:
        [
            {
                'date': '15.08.24',
                'winner': 'player_a' lub 'player_b',
                'score': '2-0',  # Wynik setowy
                'raw_score': '6-4, 7-5',  # Szczegółowy wynik
                'surface': 'hard'
            },
            ...
        ]
    """
    h2h_matches = []
    
    try:
        # Szukaj wierszy H2H (różne selektory dla różnych wersji strony)
        h2h_rows = soup.select('div.h2h__row')
        if not h2h_rows:
            h2h_rows = soup.select('div.rows div.h2h')
        if not h2h_rows:
            h2h_rows = soup.select('div[class*="h2h"]')
        
        for row in h2h_rows:
            match_data = {}
            
            # 1. WYDOBĄDŹ DATĘ
            date_text = row.get_text()
            date_match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{2,4})', date_text)
            if date_match:
                match_data['date'] = date_match.group(1)
            else:
                continue  # Pomiń jeśli brak daty
            
            # 2. WYDOBĄDŹ WYNIK
            # Format może być: "6-4, 7-5" lub "2-1" (sety)
            score_el = row.select_one('div.h2h__result, span.h2h__result, div[class*="result"]')
            if score_el:
                raw_score = score_el.get_text(strip=True)
                match_data['raw_score'] = raw_score
                
                # Parsuj wynik setowy
                sets_score = parse_tennis_score_to_sets(raw_score)
                match_data['score'] = sets_score
            else:
                continue  # Pomiń jeśli brak wyniku
            
            # 3. OKREŚL ZWYCIĘZCĘ
            # Metoda 1: Klasa CSS (np. winner)
            winner_el = row.select_one('div.winner, span.winner, [class*="winner"]')
            if winner_el:
                winner_text = winner_el.get_text(strip=True).lower()
            else:
                # Metoda 2: Z wyniku (który zawodnik jest wymieniony pierwszy?)
                winner_text = row.get_text().lower()
            
            # Normalizuj nazwy
            player_a_norm = player_a.lower().strip()
            player_b_norm = player_b.lower().strip()
            
            # Sprawdź który zawodnik wygrał
            if player_a_norm in winner_text:
                match_data['winner'] = 'player_a'
            elif player_b_norm in winner_text:
                match_data['winner'] = 'player_b'
            else:
                # Fallback: parsuj z wyniku setowego
                if sets_score:
                    sets_a, sets_b = map(int, sets_score.split('-'))
                    match_data['winner'] = 'player_a' if sets_a > sets_b else 'player_b'
                else:
                    continue
            
            # 4. WYKRYJ NAWIERZCHNIĘ (z kontekstu strony lub nazwy turnieju)
            surface = detect_surface_from_row(row)
            if surface:
                match_data['surface'] = surface
            else:
                match_data['surface'] = 'unknown'
            
            h2h_matches.append(match_data)
        
    except Exception as e:
        print(f"   ⚠️ Błąd parsowania H2H z datami: {e}")
    
    return h2h_matches


def parse_tennis_score_to_sets(raw_score: str) -> Optional[str]:
    """
    Konwertuje szczegółowy wynik na wynik setowy.
    
    Args:
        raw_score: '6-4, 7-5' lub '2-1' lub '6-4 6-3'
    
    Returns:
        '2-0' lub '2-1' (wynik setowy)
    """
    try:
        # Jeśli już jest w formacie setowym (np. "2-1")
        if re.match(r'^\d-\d$', raw_score):
            return raw_score
        
        # Parsuj szczegółowy wynik (np. "6-4, 7-5" lub "6-4 6-3")
        sets = re.findall(r'(\d+)[:\-–—](\d+)', raw_score)
        if not sets:
            return None
        
        # Policz sety wygrane przez każdego zawodnika
        sets_a = 0
        sets_b = 0
        
        for games_a, games_b in sets:
            if int(games_a) > int(games_b):
                sets_a += 1
            else:
                sets_b += 1
        
        return f"{sets_a}-{sets_b}"
    
    except Exception:
        return None


def detect_surface_from_row(row) -> Optional[str]:
    """Wykrywa nawierzchnię z wiersza H2H (z nazwy turnieju)."""
    try:
        text = row.get_text().lower()
        
        # Słowa kluczowe dla nawierzchni
        if any(keyword in text for keyword in ['clay', 'ziemia', 'antuka', 'roland garros', 'monte carlo']):
            return 'clay'
        elif any(keyword in text for keyword in ['grass', 'trawa', 'wimbledon']):
            return 'grass'
        elif any(keyword in text for keyword in ['hard', 'twarda', 'us open', 'australian open']):
            return 'hard'
        
        return None
    except:
        return None


# ==========================================
# 2. ROZSZERZONA FORMA ZAWODNIKA
# ==========================================

def extract_player_detailed_form(driver: webdriver.Chrome, player_name: str, player_url: Optional[str] = None) -> List[Dict]:
    """
    Zbiera ostatnie 10 meczów zawodnika z pełnymi szczegółami.
    
    Args:
        driver: Selenium WebDriver
        player_name: Nazwa zawodnika
        player_url: URL profilu zawodnika (opcjonalne - będzie znalezione)
    
    Returns:
        [
            {
                'result': 'W' lub 'L',
                'date': '01.10.25',
                'opponent': 'Novak Djokovic',
                'opponent_rank': 15,
                'score': '2-0',  # Wynik setowy
                'surface': 'hard'
            },
            ...
        ]
    """
    form = []
    
    try:
        # 1. Znajdź URL profilu zawodnika (jeśli nie podano)
        if not player_url:
            player_url = find_player_url_from_search(driver, player_name)
            if not player_url:
                print(f"   ⚠️ Nie znaleziono profilu zawodnika: {player_name}")
                return []
        
        # Cache URL
        PLAYER_URL_CACHE[player_name] = player_url
        
        # 2. Odwiedź stronę wyników zawodnika
        results_url = player_url.rstrip('/') + '/wyniki/'
        
        driver.get(results_url)
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 3. Parsuj ostatnie mecze
        match_rows = soup.select('div.sportName, div[class*="result"], div[class*="match"]')[:10]
        
        for row in match_rows:
            match_info = {}
            
            # Data
            date_el = row.select_one('div.date, span.date, [class*="date"]')
            if date_el:
                match_info['date'] = date_el.get_text(strip=True)
            
            # Przeciwnik
            opponent_el = row.select_one('div.opponent, a.participant, [class*="opponent"]')
            if opponent_el:
                match_info['opponent'] = opponent_el.get_text(strip=True)
                
                # Ranking przeciwnika (jeśli widoczny)
                rank_match = re.search(r'\((\d+)\)', opponent_el.get_text())
                if rank_match:
                    match_info['opponent_rank'] = int(rank_match.group(1))
            
            # Wynik
            score_el = row.select_one('div.score, span.score, [class*="score"]')
            if score_el:
                raw_score = score_el.get_text(strip=True)
                match_info['score'] = parse_tennis_score_to_sets(raw_score) or raw_score
            
            # Wynik (W/L)
            if 'win' in row.get('class', []) or 'winner' in row.get_text().lower():
                match_info['result'] = 'W'
            elif 'loss' in row.get('class', []) or 'loser' in row.get_text().lower():
                match_info['result'] = 'L'
            else:
                # Fallback: z wyniku
                if match_info.get('score'):
                    sets_a, sets_b = map(int, match_info['score'].split('-'))
                    match_info['result'] = 'W' if sets_a > sets_b else 'L'
            
            # Nawierzchnia (z nazwy turnieju lub osobnej kolumny)
            surface_el = row.select_one('div.surface, span.surface, [class*="surface"]')
            if surface_el:
                surface_text = surface_el.get_text().lower()
                if 'clay' in surface_text or 'ziemia' in surface_text:
                    match_info['surface'] = 'clay'
                elif 'grass' in surface_text or 'trawa' in surface_text:
                    match_info['surface'] = 'grass'
                elif 'hard' in surface_text or 'twarda' in surface_text:
                    match_info['surface'] = 'hard'
            
            # Dodaj jeśli ma wymagane pola
            if match_info.get('result'):
                form.append(match_info)
        
    except Exception as e:
        print(f"   ⚠️ Błąd pobierania formy zawodnika {player_name}: {e}")
    
    return form[:10]  # Maksymalnie 10 ostatnich meczów


def find_player_url_from_search(driver: webdriver.Chrome, player_name: str) -> Optional[str]:
    """
    Znajduje URL profilu zawodnika przez wyszukiwarkę Livesport.
    
    Args:
        driver: Selenium WebDriver
        player_name: Nazwa zawodnika do znalezienia
    
    Returns:
        URL profilu zawodnika lub None
    """
    try:
        # Sprawdź cache
        if player_name in PLAYER_URL_CACHE:
            return PLAYER_URL_CACHE[player_name]
        
        # Livesport search URL
        search_url = f"https://www.livesport.com/pl/szukaj/?q={player_name.replace(' ', '+')}"
        
        driver.get(search_url)
        time.sleep(1.5)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Szukaj linku do profilu gracza
        player_links = soup.select('a[href*="/gracz/"]')
        
        for link in player_links:
            href = link.get('href')
            link_text = link.get_text().lower()
            
            # Sprawdź czy to właściwy zawodnik
            if player_name.lower() in link_text:
                if href.startswith('http'):
                    return href
                else:
                    return f"https://www.livesport.com{href}"
        
        return None
        
    except Exception as e:
        print(f"   ⚠️ Błąd wyszukiwania zawodnika {player_name}: {e}")
        return None


# ==========================================
# 3. STATYSTYKI NAWIERZCHNI
# ==========================================

def extract_surface_statistics(driver: webdriver.Chrome, player_url: str) -> Dict[str, Dict]:
    """
    Zbiera statystyki zawodnika na różnych nawierzchniach.
    
    Args:
        driver: Selenium WebDriver
        player_url: URL profilu zawodnika
    
    Returns:
        {
            'clay': {
                'wins': 45,
                'total': 60,
                'win_rate': 0.75,
                'recent_form': ['W', 'W', 'L', 'W', 'W']
            },
            'hard': {...},
            'grass': {...}
        }
    """
    stats = {
        'clay': {'wins': 0, 'total': 0, 'win_rate': 0.0, 'recent_form': []},
        'hard': {'wins': 0, 'total': 0, 'win_rate': 0.0, 'recent_form': []},
        'grass': {'wins': 0, 'total': 0, 'win_rate': 0.0, 'recent_form': []}
    }
    
    try:
        # Przejdź na stronę statystyk zawodnika
        stats_url = player_url.rstrip('/') + '/statystyki/'
        
        driver.get(stats_url)
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Szukaj sekcji ze statystykami nawierzchni
        surface_sections = soup.select('div[class*="surface"], section[class*="surface"]')
        
        for section in surface_sections:
            text = section.get_text().lower()
            
            # Określ nawierzchnię
            surface = None
            if 'clay' in text or 'ziemia' in text:
                surface = 'clay'
            elif 'grass' in text or 'trawa' in text:
                surface = 'grass'
            elif 'hard' in text or 'twarda' in text:
                surface = 'hard'
            
            if not surface:
                continue
            
            # Parsuj statystyki (np. "45/60" lub "45 - 15")
            wins_losses = re.search(r'(\d+)[\s\-–—/]+(\d+)', text)
            if wins_losses:
                wins = int(wins_losses.group(1))
                total = wins + int(wins_losses.group(2))
                
                stats[surface]['wins'] = wins
                stats[surface]['total'] = total
                stats[surface]['win_rate'] = wins / total if total > 0 else 0.0
        
        # Jeśli brak dedykowanych statystyk, oblicz z ostatnich meczów
        if all(s['total'] == 0 for s in stats.values()):
            stats = calculate_surface_stats_from_form(driver, player_url)
        
    except Exception as e:
        print(f"   ⚠️ Błąd pobierania statystyk nawierzchni: {e}")
    
    return stats


def calculate_surface_stats_from_form(driver: webdriver.Chrome, player_url: str) -> Dict[str, Dict]:
    """
    Oblicza statystyki nawierzchni z ostatnich meczów (fallback).
    """
    stats = {
        'clay': {'wins': 0, 'total': 0, 'win_rate': 0.0, 'recent_form': []},
        'hard': {'wins': 0, 'total': 0, 'win_rate': 0.0, 'recent_form': []},
        'grass': {'wins': 0, 'total': 0, 'win_rate': 0.0, 'recent_form': []}
    }
    
    try:
        # Pobierz ostatnie mecze
        form = extract_player_detailed_form(driver, "", player_url)
        
        # Pogrupuj po nawierzchni
        for match in form:
            surface = match.get('surface')
            result = match.get('result')
            
            if surface in stats:
                stats[surface]['total'] += 1
                if result == 'W':
                    stats[surface]['wins'] += 1
                
                # Ostatnie 5 na tej nawierzchni
                if len(stats[surface]['recent_form']) < 5:
                    stats[surface]['recent_form'].append(result)
        
        # Oblicz win rate
        for surface in stats:
            total = stats[surface]['total']
            if total > 0:
                stats[surface]['win_rate'] = stats[surface]['wins'] / total
    
    except Exception as e:
        print(f"   ⚠️ Błąd obliczania statystyk z formy: {e}")
    
    return stats


# ==========================================
# 4. DODATKOWE FUNKCJE POMOCNICZE
# ==========================================

def find_player_url_from_match_page(soup: BeautifulSoup, player_name: str) -> Optional[str]:
    """
    Znajduje URL profilu zawodnika bezpośrednio ze strony meczu.
    
    Args:
        soup: BeautifulSoup object strony meczu
        player_name: Nazwa zawodnika
    
    Returns:
        URL profilu lub None
    """
    try:
        # Szukaj linków do profili graczy
        player_links = soup.select('a.participant__participantName, a[href*="/gracz/"]')
        
        for link in player_links:
            link_text = link.get_text(strip=True).lower()
            player_name_norm = player_name.lower().strip()
            
            if player_name_norm in link_text or link_text in player_name_norm:
                href = link.get('href')
                if href:
                    if href.startswith('http'):
                        return href
                    else:
                        return f"https://www.livesport.com{href}"
        
        return None
        
    except Exception:
        return None


# ==========================================
# EKSPORT
# ==========================================

__all__ = [
    'extract_h2h_with_dates',
    'extract_player_detailed_form',
    'extract_surface_statistics',
    'find_player_url_from_match_page',
    'find_player_url_from_search',
    'PLAYER_URL_CACHE',
    'PLAYER_DATA_CACHE'
]


















