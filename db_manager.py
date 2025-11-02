"""
Database Manager - SQLite dla meczów H2H
Automatyczne zapisywanie wyników scrapera + API dla aplikacji webowej
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os

class MatchDatabase:
    def __init__(self, db_path: str = "outputs/matches.db"):
        """Inicjalizuj bazę danych SQLite"""
        self.db_path = db_path
        
        # Utwórz folder outputs jeśli nie istnieje
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Inicjalizuj tabele
        self._init_tables()
    
    def _init_tables(self):
        """Stwórz tabele jeśli nie istnieją"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela meczów
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_date TEXT NOT NULL,
                match_time TEXT,
                sport TEXT NOT NULL,
                league TEXT,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                match_url TEXT UNIQUE NOT NULL,
                
                -- Kursy
                home_odds REAL,
                draw_odds REAL,
                away_odds REAL,
                bookmakers_found TEXT,
                best_home_bookmaker TEXT,
                best_away_bookmaker TEXT,
                all_odds TEXT,
                
                -- H2H Stats
                home_wins_in_h2h_last5 INTEGER DEFAULT 0,
                away_wins_in_h2h INTEGER DEFAULT 0,
                draws_last_5 INTEGER DEFAULT 0,
                h2h_count INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0.0,
                h2h_last5 TEXT,
                
                -- Form
                home_form TEXT,
                away_form TEXT,
                home_form_overall TEXT,
                away_form_overall TEXT,
                form_advantage INTEGER DEFAULT 0,
                
                -- Status
                qualifies INTEGER DEFAULT 0,
                focus_team TEXT DEFAULT 'home',
                
                -- Metadata
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index dla szybkich zapytań
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_match_date 
            ON matches(match_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sport 
            ON matches(sport)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_qualifies 
            ON matches(qualifies)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON matches(created_at)
        """)
        
        conn.commit()
        conn.close()
    
    def insert_match(self, match_data: Dict) -> int:
        """
        Wstaw mecz do bazy (lub zaktualizuj jeśli już istnieje)
        
        Args:
            match_data: Słownik z danymi meczu (z process_match)
        
        Returns:
            ID wstawionego/zaktualizowanego rekordu
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Konwertuj listy/słowniki na JSON/string
        bookmakers_found = match_data.get('bookmakers_found', [])
        if isinstance(bookmakers_found, list):
            bookmakers_found = ', '.join(bookmakers_found)
        
        all_odds = match_data.get('all_odds', {})
        if isinstance(all_odds, dict):
            all_odds = json.dumps(all_odds, ensure_ascii=False)
        
        h2h_last5 = match_data.get('h2h_last5', [])
        if isinstance(h2h_last5, list):
            h2h_last5 = json.dumps(h2h_last5, ensure_ascii=False)
        
        # Konwertuj formy z list na stringi
        home_form = match_data.get('home_form', [])
        if isinstance(home_form, list):
            home_form = '-'.join(home_form)
        
        away_form = match_data.get('away_form', [])
        if isinstance(away_form, list):
            away_form = '-'.join(away_form)
        
        home_form_overall = match_data.get('home_form_overall', [])
        if isinstance(home_form_overall, list):
            home_form_overall = '-'.join(home_form_overall)
        
        away_form_overall = match_data.get('away_form_overall', [])
        if isinstance(away_form_overall, list):
            away_form_overall = '-'.join(away_form_overall)
        
        try:
            cursor.execute("""
                INSERT INTO matches (
                    match_date, match_time, sport, league, home_team, away_team, match_url,
                    home_odds, draw_odds, away_odds, 
                    bookmakers_found, best_home_bookmaker, best_away_bookmaker, all_odds,
                    home_wins_in_h2h_last5, away_wins_in_h2h, draws_last_5, h2h_count, win_rate, h2h_last5,
                    home_form, away_form, home_form_overall, away_form_overall, form_advantage,
                    qualifies, focus_team
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(match_url) DO UPDATE SET
                    home_odds = excluded.home_odds,
                    draw_odds = excluded.draw_odds,
                    away_odds = excluded.away_odds,
                    bookmakers_found = excluded.bookmakers_found,
                    best_home_bookmaker = excluded.best_home_bookmaker,
                    best_away_bookmaker = excluded.best_away_bookmaker,
                    all_odds = excluded.all_odds,
                    home_wins_in_h2h_last5 = excluded.home_wins_in_h2h_last5,
                    away_wins_in_h2h = excluded.away_wins_in_h2h,
                    draws_last_5 = excluded.draws_last_5,
                    h2h_count = excluded.h2h_count,
                    win_rate = excluded.win_rate,
                    h2h_last5 = excluded.h2h_last5,
                    home_form = excluded.home_form,
                    away_form = excluded.away_form,
                    home_form_overall = excluded.home_form_overall,
                    away_form_overall = excluded.away_form_overall,
                    form_advantage = excluded.form_advantage,
                    qualifies = excluded.qualifies,
                    focus_team = excluded.focus_team,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                match_data.get('date', ''),
                match_data.get('time', ''),
                match_data.get('sport', ''),
                match_data.get('league', ''),
                match_data.get('home_team', ''),
                match_data.get('away_team', ''),
                match_data.get('match_url', ''),
                match_data.get('home_odds'),
                match_data.get('draw_odds'),
                match_data.get('away_odds'),
                bookmakers_found,
                match_data.get('best_home_bookmaker'),
                match_data.get('best_away_bookmaker'),
                all_odds,
                match_data.get('home_wins_in_h2h_last5', 0),
                match_data.get('away_wins_in_h2h', 0),
                match_data.get('draws_last_5', 0),
                match_data.get('h2h_count', 0),
                match_data.get('win_rate', 0.0),
                h2h_last5,
                home_form,
                away_form,
                home_form_overall,
                away_form_overall,
                1 if match_data.get('form_advantage') else 0,
                1 if match_data.get('qualifies') else 0,
                match_data.get('focus_team', 'home')
            ))
            
            match_id = cursor.lastrowid
            conn.commit()
            return match_id
        
        except Exception as e:
            print(f"❌ Błąd zapisu do DB: {e}")
            conn.rollback()
            return -1
        
        finally:
            conn.close()
    
    def insert_matches_batch(self, matches: List[Dict]) -> int:
        """Wstaw wiele meczów na raz (szybsze)"""
        inserted = 0
        for match_data in matches:
            match_id = self.insert_match(match_data)
            if match_id > 0:
                inserted += 1
        return inserted
    
    def get_matches(self, 
                   date: Optional[str] = None,
                   sport: Optional[str] = None,
                   qualifies_only: bool = False,
                   limit: int = 100) -> List[Dict]:
        """
        Pobierz mecze z bazy
        
        Args:
            date: Data meczu (YYYY-MM-DD) lub None (wszystkie)
            sport: Sport lub None (wszystkie)
            qualifies_only: Tylko kwalifikujące się mecze
            limit: Max liczba wyników
        
        Returns:
            Lista słowników z meczami
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM matches WHERE 1=1"
        params = []
        
        if date:
            query += " AND match_date = ?"
            params.append(date)
        
        if sport:
            query += " AND sport = ?"
            params.append(sport)
        
        if qualifies_only:
            query += " AND qualifies = 1"
        
        query += " ORDER BY match_date DESC, home_team ASC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Konwertuj Row na dict i parsuj JSON
        matches = []
        for row in rows:
            match = dict(row)
            
            # Parsuj JSON fields
            if match.get('all_odds'):
                try:
                    match['all_odds'] = json.loads(match['all_odds'])
                except:
                    match['all_odds'] = {}
            
            if match.get('h2h_last5'):
                try:
                    match['h2h_last5'] = json.loads(match['h2h_last5'])
                except:
                    match['h2h_last5'] = []
            
            if match.get('bookmakers_found'):
                match['bookmakers_found'] = match['bookmakers_found'].split(', ')
            
            # Konwertuj formy z string na list
            for form_field in ['home_form', 'away_form', 'home_form_overall', 'away_form_overall']:
                if match.get(form_field):
                    match[form_field] = match[form_field].split('-')
            
            matches.append(match)
        
        conn.close()
        return matches
    
    def get_stats(self) -> Dict:
        """Pobierz statystyki bazy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM matches")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches WHERE qualifies = 1")
        qualifying = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT sport) FROM matches")
        sports = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT match_date) FROM matches")
        dates = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(scraped_at) FROM matches")
        last_update = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_matches': total,
            'qualifying_matches': qualifying,
            'unique_sports': sports,
            'date_range': dates,
            'last_update': last_update
        }
    
    def cleanup_old_matches(self, days: int = 7):
        """Usuń mecze starsze niż X dni"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM matches 
            WHERE match_date < date('now', '-' || ? || ' days')
        """, (days,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted


# Test
if __name__ == "__main__":
    db = MatchDatabase()
    
    # Test insert
    test_match = {
        'date': '2025-11-01',
        'time': '18:00',
        'sport': 'football',
        'league': 'Ekstraklasa',
        'home_team': 'Legia Warszawa',
        'away_team': 'Górnik Zabrze',
        'match_url': 'https://example.com/match1',
        'home_odds': 1.85,
        'draw_odds': 3.50,
        'away_odds': 4.20,
        'bookmakers_found': ['STS', 'Fortuna'],
        'best_home_bookmaker': 'STS',
        'best_away_bookmaker': 'Fortuna',
        'all_odds': {'STS': {'home': 1.85, 'draw': 3.40, 'away': 4.10}},
        'home_wins_in_h2h_last5': 3,
        'away_wins_in_h2h': 1,
        'draws_last_5': 1,
        'h2h_count': 5,
        'win_rate': 0.60,
        'h2h_last5': [],
        'home_form': ['W', 'W', 'L', 'W', 'D'],
        'away_form': ['L', 'L', 'W', 'L', 'L'],
        'home_form_overall': ['W', 'W', 'L', 'W', 'D'],
        'away_form_overall': ['L', 'L', 'W', 'L', 'L'],
        'form_advantage': True,
        'qualifies': True,
        'focus_team': 'home'
    }
    
    match_id = db.insert_match(test_match)
    print(f"✅ Inserted match ID: {match_id}")
    
    # Test query
    matches = db.get_matches(date='2025-11-01', qualifies_only=True)
    print(f"✅ Found {len(matches)} matches")
    
    # Stats
    stats = db.get_stats()
    print(f"📊 Stats: {stats}")
