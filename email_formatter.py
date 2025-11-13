"""
Email Formatter - Bookmaker Filtering for Email Notifications
=============================================================

FUNKCJONALNOŚĆ:
- Formatuje mecze do wysyłki emailowej
- Pokazuje TYLKO kursy z wybranych bukmacherów: Fortuna, Superbet, STS
- Fortuna w pierwszej kolumnie (priorytet) - czerwone tło
- Piękna tabela HTML z kolorami
- Aplikacja nadal przechowuje wszystkie kursy w bazie danych (bez zmian)

UŻYCIE:
    from email_formatter import get_email_formatter
    
    formatter = get_email_formatter()
    html = formatter.format_matches_for_email(matches)

AUTHOR: Automated Assistant
VERSION: 1.0
"""

import json
from typing import List, Dict, Optional


class EmailFormatter:
    """Formatuje mecze dla wysyłki emailowej z filtrowaniem bukmacherów"""
    
    # ✅ Bukmacherzy dozwoleni w emailu (TYLKO te 3!)
    ALLOWED_BOOKMAKERS = ['Fortuna', 'Superbet', 'STS']
    
    # 🎨 Kolory dla każdego bukmachera
    BOOKMAKER_COLORS = {
        'Fortuna': '#dc3545',    # Czerwony - PRIORYTET
        'Superbet': '#0d6efd',   # Niebieski
        'STS': '#198754'         # Zielony
    }
    
    def __init__(self):
        """Inicjalizacja formattera"""
        pass
    
    def _extract_odds_for_bookmaker(self, all_odds: Dict, bookmaker: str) -> Dict[str, Optional[float]]:
        """
        Wyciąga kursy dla konkretnego bukmachera z all_odds JSON
        
        Args:
            all_odds: Słownik z kursami wszystkich bukmacherów
            bookmaker: Nazwa bukmachera (np. 'Fortuna')
        
        Returns:
            {'home': 1.85, 'away': 2.10, 'draw': 3.50} lub {'home': None, ...}
        """
        if not all_odds or not isinstance(all_odds, dict):
            return {'home': None, 'away': None, 'draw': None}
        
        # Sprawdź czy bukmacher ma kursy
        if bookmaker not in all_odds:
            return {'home': None, 'away': None, 'draw': None}
        
        bm_odds = all_odds[bookmaker]
        return {
            'home': bm_odds.get('home'),
            'away': bm_odds.get('away'),
            'draw': bm_odds.get('draw')
        }
    
    def _format_odds_value(self, odds: Optional[float]) -> str:
        """
        Formatuje wartość kursu do wyświetlenia
        
        Args:
            odds: Kurs (np. 1.85) lub None
        
        Returns:
            "1.85" lub "-" (jeśli brak kursu)
        """
        if odds is None:
            return "-"
        return f"{odds:.2f}"
    
    def _create_table_header(self) -> str:
        """Tworzy nagłówek tabeli HTML z kolumnami bukmacherów"""
        return f"""
        <tr style="background-color: #f8f9fa;">
            <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">Mecz</th>
            <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">Czas</th>
            <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center; background-color: {self.BOOKMAKER_COLORS['Fortuna']}; color: white;">
                🎯 Fortuna<br><small>(PRIORYTET)</small>
            </th>
            <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center; background-color: {self.BOOKMAKER_COLORS['Superbet']}; color: white;">
                Superbet
            </th>
            <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center; background-color: {self.BOOKMAKER_COLORS['STS']}; color: white;">
                STS
            </th>
            <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">H2H</th>
        </tr>
        """
    
    def _create_odds_cell(self, bookmaker: str, odds: Dict[str, Optional[float]], sport: str) -> str:
        """
        Tworzy komórkę z kursami dla danego bukmachera
        
        Args:
            bookmaker: Nazwa bukmachera
            odds: Słownik z kursami {'home': 1.85, 'away': 2.10, 'draw': 3.50}
            sport: Sport (volleyball/handball nie mają remisu)
        
        Returns:
            HTML komórki z kursami
        """
        color = self.BOOKMAKER_COLORS.get(bookmaker, '#6c757d')
        
        # Sprawdź czy sport ma remis
        no_draw_sports = ['volleyball', 'handball', 'tennis', 'rugby']
        has_draw = sport.lower() not in no_draw_sports
        
        home = self._format_odds_value(odds['home'])
        away = self._format_odds_value(odds['away'])
        draw = self._format_odds_value(odds['draw']) if has_draw else None
        
        # Format: 1-X-2 (dla sportów z remisem) lub 1-2 (bez remisu)
        if has_draw:
            odds_text = f"{home} / {draw} / {away}"
        else:
            odds_text = f"{home} / {away}"
        
        # Jeśli wszystkie kursy są "-", pokaż "Brak"
        if home == "-" and away == "-" and (not has_draw or draw == "-"):
            odds_text = "<em>Brak kursów</em>"
        
        return f"""
        <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center; background-color: {color}15;">
            <strong style="color: {color};">{odds_text}</strong>
        </td>
        """
    
    def _create_match_row(self, match: Dict) -> str:
        """
        Tworzy wiersz tabeli dla jednego meczu
        
        Args:
            match: Słownik z danymi meczu
        
        Returns:
            HTML wiersza tabeli
        """
        # Podstawowe dane meczu
        home = match.get('home_team', 'Unknown')
        away = match.get('away_team', 'Unknown')
        match_time = match.get('match_time', 'TBA')
        sport = match.get('sport', 'football')
        
        # H2H data
        h2h_home = match.get('home_wins_in_h2h_last5', 0)
        h2h_away = match.get('away_wins_in_h2h_last5', 0)
        h2h_count = match.get('h2h_count', 0)
        
        # all_odds może być string (JSON) lub dict
        all_odds = match.get('all_odds', {})
        if isinstance(all_odds, str):
            try:
                all_odds = json.loads(all_odds)
            except:
                all_odds = {}
        
        # Wyciągnij kursy dla każdego bukmachera
        fortuna_odds = self._extract_odds_for_bookmaker(all_odds, 'Fortuna')
        superbet_odds = self._extract_odds_for_bookmaker(all_odds, 'Superbet')
        sts_odds = self._extract_odds_for_bookmaker(all_odds, 'STS')
        
        # Utwórz komórki z kursami
        fortuna_cell = self._create_odds_cell('Fortuna', fortuna_odds, sport)
        superbet_cell = self._create_odds_cell('Superbet', superbet_odds, sport)
        sts_cell = self._create_odds_cell('STS', sts_odds, sport)
        
        return f"""
        <tr>
            <td style="padding: 12px; border: 1px solid #dee2e6;">
                <strong>{home}</strong> vs <strong>{away}</strong>
            </td>
            <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">
                {match_time}
            </td>
            {fortuna_cell}
            {superbet_cell}
            {sts_cell}
            <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">
                {h2h_home}-{h2h_away}<br>
                <small style="color: #6c757d;">(z {h2h_count})</small>
            </td>
        </tr>
        """
    
    def format_matches_for_email(self, matches: List[Dict]) -> str:
        """
        Formatuje listę meczów do HTML dla emaila
        
        Args:
            matches: Lista słowników z danymi meczów
        
        Returns:
            HTML tabeli z meczami (tylko kursy Fortuna/Superbet/STS)
        """
        if not matches:
            return "<p>Brak meczów kwalifikujących się.</p>"
        
        # Nagłówek
        html = """
        <div style="font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto;">
            <h2 style="color: #212529;">🎯 Mecze z filtrowanymi kursami</h2>
            <p style="color: #6c757d; margin-bottom: 20px;">
                <strong>Bukmacherzy:</strong> 
                <span style="color: #dc3545;">■</span> Fortuna (PRIORYTET) | 
                <span style="color: #0d6efd;">■</span> Superbet | 
                <span style="color: #198754;">■</span> STS
            </p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
        """
        
        # Nagłówek tabeli
        html += self._create_table_header()
        
        # Wiersze z meczami
        for match in matches:
            html += self._create_match_row(match)
        
        # Stopka
        html += """
            </table>
            <p style="color: #6c757d; margin-top: 20px; font-size: 0.9em;">
                💡 <strong>Uwaga:</strong> Aplikacja przechowuje kursy od wszystkich bukmacherów, 
                ale email pokazuje tylko Fortuna, Superbet i STS zgodnie z konfiguracją.
            </p>
        </div>
        """
        
        return html


# ===================================================================
# HELPER FUNCTION - pobierz formatter (Singleton pattern)
# ===================================================================

_formatter_instance = None

def get_email_formatter() -> EmailFormatter:
    """
    Zwraca instancję EmailFormatter (Singleton)
    
    Returns:
        EmailFormatter instance
    """
    global _formatter_instance
    if _formatter_instance is None:
        _formatter_instance = EmailFormatter()
    return _formatter_instance


# ===================================================================
# TEST - uruchom lokalnie dla testów
# ===================================================================

if __name__ == '__main__':
    # Test data
    test_matches = [
        {
            'home_team': 'Resovia Rzeszów',
            'away_team': 'Jastrzębski Węgiel',
            'match_time': '2024-01-15 18:00',
            'sport': 'volleyball',
            'home_wins_in_h2h_last5': 2,
            'away_wins_in_h2h_last5': 3,
            'h2h_count': 5,
            'all_odds': {
                'Fortuna': {'home': 2.10, 'away': 1.65, 'draw': None},
                'Superbet': {'home': 2.05, 'away': 1.70, 'draw': None},
                'STS': {'home': 2.15, 'away': 1.60, 'draw': None},
                'Bet365': {'home': 2.12, 'away': 1.68, 'draw': None}  # Ten NIE będzie w emailu
            }
        },
        {
            'home_team': 'Legia Warszawa',
            'away_team': 'Lech Poznań',
            'match_time': '2024-01-15 20:30',
            'sport': 'football',
            'home_wins_in_h2h_last5': 3,
            'away_wins_in_h2h_last5': 1,
            'h2h_count': 5,
            'all_odds': {
                'Fortuna': {'home': 2.30, 'away': 2.90, 'draw': 3.20},
                'STS': {'home': 2.25, 'away': 3.00, 'draw': 3.10}
                # Brak Superbet - pokaże "Brak kursów"
            }
        }
    ]
    
    formatter = get_email_formatter()
    html = formatter.format_matches_for_email(test_matches)
    
    # Zapisz do pliku testowego
    with open('test_email_output.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ Test completed! Check test_email_output.html")
