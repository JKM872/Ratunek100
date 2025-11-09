"""
🇵🇱 LOCAL POLISH BOOKMAKER SCRAPER
====================================

PROBLEM: GitHub Actions (USA) nie ma dostępu do polskich bukmacherów (geo-blocking)
ROZWIĄZANIE: Scraper działa lokalnie (Polska IP) i wysyła dane do Supabase

FLOW:
1. Scraper (Polska IP) → Pobiera kursy z Fortuna/Superbet/STS
2. Normalizuje nazwy drużyn (lowercase, bez polskich znaków)
3. Wysyła do Supabase (bookmaker_odds table)
4. GitHub Actions (USA) → Odczytuje z Supabase
5. Email z pełnymi kursami ✅

USAGE:
    # Setup
    pip install requests beautifulsoup4 cloudscraper supabase
    
    # Set env vars
    set SUPABASE_URL=https://bfslhqnxsgmdyptrqshj.supabase.co
    set SUPABASE_KEY=your_service_role_key
    
    # Run
    python local_bookmaker_scraper.py
    
    # Or schedule daily at 21:00
    # See: setup_windows_task_scheduler.bat

AUTHOR: AI Assistant
VERSION: 1.0
DATE: 2025-01-15
"""

import os
import sys
import json
import time
import re
import unicodedata
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import logging

import requests
from bs4 import BeautifulSoup
try:
    from cloudscraper import create_scraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    print("⚠️  cloudscraper not installed - using requests (may fail on CloudFlare)")
    HAS_CLOUDSCRAPER = False

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    print("❌ supabase-py not installed! Run: pip install supabase")
    HAS_SUPABASE = False
    sys.exit(1)

# ============================================================================
# Configuration
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase config
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://bfslhqnxsgmdyptrqshj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')  # SERVICE_ROLE key (not anon key!)

if not SUPABASE_KEY:
    logger.error("❌ SUPABASE_KEY not set! Export it: set SUPABASE_KEY=your_key")
    sys.exit(1)

# Rate limiting
DELAY_BETWEEN_BOOKMAKERS = 3  # seconds
DELAY_BETWEEN_MATCHES = 0.5  # seconds

# User agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# ============================================================================
# Utility Functions
# ============================================================================

def normalize_team_name(team_name: str) -> str:
    """
    Normalizuje nazwę drużyny:
    - Usuwa polskie znaki (ą→a, ć→c, etc.)
    - Lowercase
    - Usuwa białe znaki z boków
    - Zastępuje spacje underscore
    
    Example:
        "Legia Warszawa" → "legia_warszawa"
        "Śląsk Wrocław" → "slask_wroclaw"
    """
    # Usuń polskie znaki
    nfd = unicodedata.normalize('NFD', team_name)
    without_accents = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    
    # Lowercase i trim
    normalized = without_accents.lower().strip()
    
    # Zastąp spacje i znaki specjalne underscores
    normalized = re.sub(r'[^a-z0-9]+', '_', normalized)
    
    # Usuń trailing underscores
    normalized = normalized.strip('_')
    
    return normalized


def generate_match_key(home_team: str, away_team: str) -> str:
    """
    Generuje unikalny klucz meczu
    
    Example:
        ("Legia Warszawa", "Lech Poznań") → "legia_warszawa_vs_lech_poznan"
    """
    home_norm = normalize_team_name(home_team)
    away_norm = normalize_team_name(away_team)
    return f"{home_norm}_vs_{away_norm}"


# ============================================================================
# Bookmaker Scrapers
# ============================================================================

class BookmakerScraperBase:
    """Base class for bookmaker scrapers"""
    
    def __init__(self):
        if HAS_CLOUDSCRAPER:
            self.session = create_scraper()  # Bypass CloudFlare
        else:
            self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def fetch_page(self, url: str, timeout: int = 15) -> Optional[BeautifulSoup]:
        """Fetch and parse HTML page"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None


class FortunaScraperPL(BookmakerScraperBase):
    """Scraper for Fortuna Polska (www.ifortuna.pl)"""
    
    BASE_URL = 'https://www.ifortuna.pl'
    
    def scrape_football_odds(self) -> Dict[str, Dict]:
        """
        Scrape football odds from Fortuna
        
        Returns:
            {
                "legia_warszawa_vs_lech_poznan": {
                    "home_team": "Legia Warszawa",
                    "away_team": "Lech Poznań",
                    "home_odds": 2.10,
                    "away_odds": 1.65,
                    "draw_odds": 3.20,
                    "match_time": "2025-01-15 20:00"
                },
                ...
            }
        """
        logger.info("🔴 Scraping Fortuna odds...")
        
        # URL do zakładów piłkarskich
        url = f"{self.BASE_URL}/zaklady-bukmacherskie/pilka-nozna"
        
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        odds_data = {}
        
        # TODO: Customize selectors based on actual Fortuna HTML structure
        # This is a TEMPLATE - you'll need to inspect actual HTML
        
        try:
            # Find match containers (adjust selector!)
            matches = soup.find_all('div', class_='event-row')  # EXAMPLE selector
            
            for match in matches[:100]:  # Limit to 100 matches
                try:
                    # Extract team names (adjust!)
                    teams = match.find_all('span', class_='team-name')
                    if len(teams) < 2:
                        continue
                    
                    home_team = teams[0].text.strip()
                    away_team = teams[1].text.strip()
                    
                    # Extract odds (adjust!)
                    odds_buttons = match.find_all('button', class_='odd-button')
                    if len(odds_buttons) < 3:
                        continue
                    
                    home_odds = float(odds_buttons[0].text.strip())
                    draw_odds = float(odds_buttons[1].text.strip())
                    away_odds = float(odds_buttons[2].text.strip())
                    
                    # Extract match time (optional)
                    time_elem = match.find('span', class_='match-time')
                    match_time = time_elem.text.strip() if time_elem else None
                    
                    # Generate match key
                    match_key = generate_match_key(home_team, away_team)
                    
                    odds_data[match_key] = {
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_odds': home_odds,
                        'away_odds': away_odds,
                        'draw_odds': draw_odds,
                        'match_time': match_time,
                        'bookmaker': 'fortuna'
                    }
                    
                except Exception as e:
                    logger.debug(f"Error parsing Fortuna match: {e}")
                    continue
            
            logger.info(f"✅ Fortuna: Found {len(odds_data)} matches")
            return odds_data
            
        except Exception as e:
            logger.error(f"❌ Fortuna scraping failed: {e}")
            return {}


class SuperbetScraperPL(BookmakerScraperBase):
    """Scraper for Superbet Polska (www.superbet.pl)"""
    
    BASE_URL = 'https://www.superbet.pl'
    
    def scrape_football_odds(self) -> Dict[str, Dict]:
        """Scrape football odds from Superbet"""
        logger.info("🔵 Scraping Superbet odds...")
        
        url = f"{self.BASE_URL}/zaklady-sportowe/pilka-nozna"
        
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        odds_data = {}
        
        try:
            # TODO: Customize selectors for Superbet
            matches = soup.find_all('div', class_='match-card')
            
            for match in matches[:100]:
                try:
                    teams = match.find_all('span', class_='match-team')
                    if len(teams) < 2:
                        continue
                    
                    home_team = teams[0].text.strip()
                    away_team = teams[1].text.strip()
                    
                    odds = match.find_all('span', class_='price')
                    if len(odds) < 3:
                        continue
                    
                    home_odds = float(odds[0].text.strip())
                    draw_odds = float(odds[1].text.strip())
                    away_odds = float(odds[2].text.strip())
                    
                    match_key = generate_match_key(home_team, away_team)
                    
                    odds_data[match_key] = {
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_odds': home_odds,
                        'away_odds': away_odds,
                        'draw_odds': draw_odds,
                        'bookmaker': 'superbet'
                    }
                    
                except Exception as e:
                    logger.debug(f"Error parsing Superbet match: {e}")
                    continue
            
            logger.info(f"✅ Superbet: Found {len(odds_data)} matches")
            return odds_data
            
        except Exception as e:
            logger.error(f"❌ Superbet scraping failed: {e}")
            return {}


class STSScraperPL(BookmakerScraperBase):
    """Scraper for STS Polska (www.sts.pl)"""
    
    BASE_URL = 'https://www.sts.pl'
    
    def scrape_football_odds(self) -> Dict[str, Dict]:
        """Scrape football odds from STS"""
        logger.info("🟢 Scraping STS odds...")
        
        url = f"{self.BASE_URL}/zaklady-bukmacherskie"
        
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        odds_data = {}
        
        try:
            # TODO: Customize selectors for STS
            matches = soup.find_all('div', class_='event')
            
            for match in matches[:100]:
                try:
                    teams = match.find_all('span', class_='competitor')
                    if len(teams) < 2:
                        continue
                    
                    home_team = teams[0].text.strip()
                    away_team = teams[1].text.strip()
                    
                    odds = match.find_all('span', class_='coeff')
                    if len(odds) < 3:
                        continue
                    
                    home_odds = float(odds[0].text.strip())
                    draw_odds = float(odds[1].text.strip())
                    away_odds = float(odds[2].text.strip())
                    
                    match_key = generate_match_key(home_team, away_team)
                    
                    odds_data[match_key] = {
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_odds': home_odds,
                        'away_odds': away_odds,
                        'draw_odds': draw_odds,
                        'bookmaker': 'sts'
                    }
                    
                except Exception as e:
                    logger.debug(f"Error parsing STS match: {e}")
                    continue
            
            logger.info(f"✅ STS: Found {len(odds_data)} matches")
            return odds_data
            
        except Exception as e:
            logger.error(f"❌ STS scraping failed: {e}")
            return {}


# ============================================================================
# Supabase Uploader
# ============================================================================

class SupabaseOddsUploader:
    """Uploads bookmaker odds to Supabase"""
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info(f"✅ Connected to Supabase: {SUPABASE_URL}")
    
    def merge_odds(self, fortuna: Dict, superbet: Dict, sts: Dict) -> Dict[str, Dict]:
        """
        Merge odds from all bookmakers
        
        Returns:
            {
                "legia_warszawa_vs_lech_poznan": {
                    "home_team_original": "Legia Warszawa",
                    "away_team_original": "Lech Poznań",
                    "bookmakers": {
                        "fortuna": {"home_odds": 2.10, "away_odds": 1.65, "draw_odds": 3.20},
                        "superbet": {"home_odds": 2.05, "away_odds": 1.70, "draw_odds": 3.10},
                        "sts": {"home_odds": 2.15, "away_odds": 1.60, "draw_odds": 3.25}
                    }
                },
                ...
            }
        """
        merged = {}
        
        # Get all unique match keys
        all_keys = set(fortuna.keys()) | set(superbet.keys()) | set(sts.keys())
        
        for match_key in all_keys:
            bookmakers_data = {}
            
            # Add Fortuna odds
            if match_key in fortuna:
                bookmakers_data['fortuna'] = {
                    'home_odds': fortuna[match_key]['home_odds'],
                    'away_odds': fortuna[match_key]['away_odds'],
                    'draw_odds': fortuna[match_key].get('draw_odds')
                }
            
            # Add Superbet odds
            if match_key in superbet:
                bookmakers_data['superbet'] = {
                    'home_odds': superbet[match_key]['home_odds'],
                    'away_odds': superbet[match_key]['away_odds'],
                    'draw_odds': superbet[match_key].get('draw_odds')
                }
            
            # Add STS odds
            if match_key in sts:
                bookmakers_data['sts'] = {
                    'home_odds': sts[match_key]['home_odds'],
                    'away_odds': sts[match_key]['away_odds'],
                    'draw_odds': sts[match_key].get('draw_odds')
                }
            
            # Get team names (prefer Fortuna, fallback to others)
            source = fortuna.get(match_key) or superbet.get(match_key) or sts.get(match_key)
            
            merged[match_key] = {
                'home_team_original': source['home_team'],
                'away_team_original': source['away_team'],
                'bookmakers': bookmakers_data,
                'match_time': source.get('match_time')
            }
        
        return merged
    
    def upload_to_supabase(self, merged_odds: Dict) -> Tuple[int, int]:
        """
        Upload merged odds to Supabase
        
        Returns:
            (success_count, error_count)
        """
        logger.info(f"\n📤 Uploading {len(merged_odds)} matches to Supabase...")
        
        success_count = 0
        error_count = 0
        
        today = date.today().isoformat()
        
        for match_key, data in merged_odds.items():
            try:
                record = {
                    'match_key': match_key,
                    'match_date': today,
                    'home_team_original': data['home_team_original'],
                    'away_team_original': data['away_team_original'],
                    'bookmakers': json.dumps(data['bookmakers']),
                    'sport': 'football',
                    'source': 'local_polish_scraper',
                    'is_active': True
                }
                
                # Upsert (insert or update if exists)
                response = self.supabase.table('bookmaker_odds').upsert(
                    record,
                    on_conflict='match_key,match_date'
                ).execute()
                
                success_count += 1
                
                if success_count % 10 == 0:
                    logger.info(f"   Progress: {success_count}/{len(merged_odds)}")
                
            except Exception as e:
                logger.error(f"❌ Upload error for {match_key}: {e}")
                error_count += 1
        
        logger.info(f"\n✅ Upload complete!")
        logger.info(f"   Success: {success_count}")
        logger.info(f"   Errors: {error_count}")
        
        return success_count, error_count


# ============================================================================
# Main Orchestrator
# ============================================================================

class PolishBookmakerOrchestrator:
    """Main orchestrator for Polish bookmaker scraping"""
    
    def __init__(self):
        self.fortuna = FortunaScraperPL()
        self.superbet = SuperbetScraperPL()
        self.sts = STSScraperPL()
        self.uploader = SupabaseOddsUploader()
    
    def run_daily_scraping(self):
        """Main function - run daily"""
        print("\n" + "="*80)
        print("🇵🇱 POLISH BOOKMAKER ODDS SCRAPER")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Supabase: {SUPABASE_URL}")
        print("="*80 + "\n")
        
        try:
            # Step 1: Scrape Fortuna
            fortuna_odds = self.fortuna.scrape_football_odds()
            time.sleep(DELAY_BETWEEN_BOOKMAKERS)
            
            # Step 2: Scrape Superbet
            superbet_odds = self.superbet.scrape_football_odds()
            time.sleep(DELAY_BETWEEN_BOOKMAKERS)
            
            # Step 3: Scrape STS
            sts_odds = self.sts.scrape_football_odds()
            time.sleep(DELAY_BETWEEN_BOOKMAKERS)
            
            # Step 4: Merge
            logger.info("\n📊 Merging odds from all bookmakers...")
            merged = self.uploader.merge_odds(fortuna_odds, superbet_odds, sts_odds)
            
            # Step 5: Statistics
            logger.info(f"\n📈 STATISTICS:")
            logger.info(f"   Total unique matches: {len(merged)}")
            logger.info(f"   With Fortuna: {sum(1 for m in merged.values() if 'fortuna' in m['bookmakers'])}")
            logger.info(f"   With Superbet: {sum(1 for m in merged.values() if 'superbet' in m['bookmakers'])}")
            logger.info(f"   With STS: {sum(1 for m in merged.values() if 'sts' in m['bookmakers'])}")
            logger.info(f"   With all 3: {sum(1 for m in merged.values() if len(m['bookmakers']) == 3)}")
            
            # Step 6: Upload to Supabase
            if merged:
                success, errors = self.uploader.upload_to_supabase(merged)
                
                if success > 0:
                    print("\n" + "="*80)
                    print("✅ SUCCESS!")
                    print("="*80)
                    print(f"Uploaded {success} matches to Supabase")
                    print(f"GitHub Actions can now read these odds")
                    print("="*80 + "\n")
                else:
                    print("\n⚠️  No matches uploaded")
            else:
                print("\n⚠️  No odds data collected")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        except Exception as e:
            logger.error(f"\n❌ FATAL ERROR: {e}")
            import traceback
            traceback.print_exc()


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Entry point"""
    orchestrator = PolishBookmakerOrchestrator()
    orchestrator.run_daily_scraping()


if __name__ == '__main__':
    main()
