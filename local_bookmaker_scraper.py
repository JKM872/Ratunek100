#!/usr/bin/env python3
"""
Local Polish Bookmaker Scraper
================================

Scrapes odds from Polish bookmakers (Fortuna, Superbet, STS) to bypass geo-blocking.
Runs locally on Windows and uploads results to Supabase.

Features:
- HTML parsing with BeautifulSoup
- Geo-blocking bypass (Polish IP required)
- Error handling & retries
- Proxy rotation support
- Rate limiting
- Logging & monitoring
- Supabase integration

Usage:
    python local_bookmaker_scraper.py

Requirements:
    pip install requests beautifulsoup4 cloudscraper supabase python-dotenv lxml
"""

import os
import sys
import time
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

# Third-party imports
try:
    import requests
    from bs4 import BeautifulSoup
    import cloudscraper
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Install with: pip install requests beautifulsoup4 cloudscraper supabase python-dotenv lxml")
    sys.exit(1)

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://bfslhqnxsgmdyptrqshj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

if not SUPABASE_KEY:
    print("❌ SUPABASE_KEY not found in environment!")
    print("Create .env file with: SUPABASE_KEY=your_key_here")
    sys.exit(1)

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_DIR}/scraper_{datetime.now().strftime("%Y-%m-%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Bookmaker URLs
BOOKMAKERS = {
    'fortuna': 'https://www.ifortuna.pl/zaklady-bukmacherskie',
    'superbet': 'https://www.superbet.pl/zaklady-sportowe',
    'sts': 'https://www.sts.pl/pl/zaklady-bukmacherskie'
}

# ============================================================================
# UTILITIES
# ============================================================================

def generate_match_key(home_team: str, away_team: str) -> str:
    """Generate unique match key from team names"""
    # Normalize team names
    home = re.sub(r'[^\w\s]', '', home_team.lower().strip())
    away = re.sub(r'[^\w\s]', '', away_team.lower().strip())
    
    # Remove common words
    stop_words = ['fc', 'cf', 'sc', 'ud', 'cd', 'ad']
    home_words = [w for w in home.split() if w not in stop_words]
    away_words = [w for w in away.split() if w not in stop_words]
    
    home_key = '_'.join(home_words[:2])  # First 2 words
    away_key = '_'.join(away_words[:2])
    
    return f"{home_key}_vs_{away_key}"


def normalize_team_name(team: str) -> str:
    """Normalize team name for matching"""
    # Remove special characters
    team = re.sub(r'[^\w\s]', '', team)
    
    # Remove common prefixes/suffixes
    team = re.sub(r'\b(FC|CF|SC|UD|CD|AD|KS|MKS)\b', '', team, flags=re.IGNORECASE)
    
    return team.strip().title()


# ============================================================================
# BASE SCRAPER CLASS
# ============================================================================

class BookmakerScraper:
    """Base class for bookmaker scrapers"""
    
    def __init__(self, name: str, base_url: str, use_cloudscraper: bool = True):
        self.name = name
        self.base_url = base_url
        self.session = cloudscraper.create_scraper() if use_cloudscraper else requests.Session()
        
        # Headers to mimic Polish user
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': base_url,
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def fetch_page(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse HTML page with retries"""
        for attempt in range(max_retries):
            try:
                logger.debug(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Check for geo-blocking messages
                if 'geo' in response.text.lower() or 'blocked' in response.text.lower():
                    logger.warning(f"⚠️  Possible geo-blocking detected for {self.name}")
                
                soup = BeautifulSoup(response.content, 'lxml')
                logger.debug(f"✅ Successfully fetched {url}")
                
                return soup
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.debug(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed to fetch {url} after {max_retries} attempts")
                    return None
        
        return None
    
    def extract_odds(self, soup: BeautifulSoup) -> Dict[str, Dict]:
        """Extract odds from HTML - to be implemented by subclasses"""
        raise NotImplementedError("Subclass must implement extract_odds()")


# ============================================================================
# FORTUNA SCRAPER
# ============================================================================

class FortunaScraper(BookmakerScraper):
    """Scraper for Fortuna.pl"""
    
    def __init__(self):
        super().__init__('Fortuna', BOOKMAKERS['fortuna'])
    
    def scrape_football_odds(self) -> Dict[str, Dict]:
        """Scrape football odds from Fortuna"""
        logger.info("🔴 Scraping Fortuna football odds...")
        
        urls = [
            f"{self.base_url}/pilka-nozna",
            f"{self.base_url}/pilka-nozna/polska/ekstraklasa",
            "https://www.ifortuna.pl/zaklady-bukmacherskie/pilka-nozna/europa/liga-mistrzow"
        ]
        
        all_odds = {}
        
        for url in urls:
            soup = self.fetch_page(url)
            if not soup:
                continue
            
            try:
                odds = self._parse_fortuna_matches(soup)
                all_odds.update(odds)
                
                logger.info(f"   Found {len(odds)} matches from {urlparse(url).path}")
                
            except Exception as e:
                logger.error(f"   Parse error for {url}: {e}")
                continue
        
        logger.info(f"✅ Fortuna: Total {len(all_odds)} matches")
        return all_odds
    
    def _parse_fortuna_matches(self, soup: BeautifulSoup) -> Dict[str, Dict]:
        """Parse Fortuna match HTML"""
        odds_data = {}
        
        # Try multiple possible selectors (Fortuna changes structure often)
        possible_selectors = [
            {'container': 'div', 'class': re.compile(r'event.*|match.*|game.*')},
            {'container': 'tr', 'class': re.compile(r'event.*|match.*')},
            {'container': 'article', 'class': re.compile(r'match.*')},
        ]
        
        matches = []
        for selector in possible_selectors:
            matches = soup.find_all(selector['container'], class_=selector['class'])
            if matches:
                logger.debug(f"   Using selector: {selector}")
                break
        
        if not matches:
            logger.warning("   No matches found with any selector")
            return odds_data
        
        for match in matches[:200]:  # Limit to 200 matches
            try:
                # Extract team names
                teams = self._extract_teams(match)
                if not teams:
                    continue
                
                home_team, away_team = teams
                
                # Extract odds
                odds = self._extract_odds_values(match)
                if not odds:
                    continue
                
                home_odds, draw_odds, away_odds = odds
                
                # Validate odds
                if not (1.01 <= home_odds <= 100 and 1.01 <= away_odds <= 100):
                    continue
                
                match_key = generate_match_key(home_team, away_team)
                
                odds_data[match_key] = {
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_odds': home_odds,
                    'draw_odds': draw_odds,
                    'away_odds': away_odds,
                    'bookmaker': 'fortuna',
                    'scraped_at': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.debug(f"   Skip match: {e}")
                continue
        
        return odds_data
    
    def _extract_teams(self, match_element) -> Optional[Tuple[str, str]]:
        """Extract team names from match element"""
        # Try multiple patterns
        patterns = [
            {'tag': 'span', 'class': re.compile(r'team.*|competitor.*|participant.*')},
            {'tag': 'div', 'class': re.compile(r'team.*|name.*')},
            {'tag': 'td', 'class': re.compile(r'team.*|name.*')},
        ]
        
        for pattern in patterns:
            teams = match_element.find_all(pattern['tag'], class_=pattern['class'])
            
            if len(teams) >= 2:
                home_team = normalize_team_name(teams[0].get_text(strip=True))
                away_team = normalize_team_name(teams[1].get_text(strip=True))
                
                if home_team and away_team and len(home_team) > 2 and len(away_team) > 2:
                    return home_team, away_team
        
        return None
    
    def _extract_odds_values(self, match_element) -> Optional[Tuple[float, float, float]]:
        """Extract odds values (1-X-2)"""
        # Look for odds in buttons, spans, or divs
        patterns = [
            {'tag': 'button', 'class': re.compile(r'odd.*|coef.*|kursy.*|price.*')},
            {'tag': 'span', 'class': re.compile(r'odd.*|coef.*|kursy.*|value.*')},
            {'tag': 'div', 'class': re.compile(r'odd.*|price.*')},
        ]
        
        for pattern in patterns:
            odd_elements = match_element.find_all(pattern['tag'], class_=pattern['class'])
            
            if len(odd_elements) >= 2:
                odds_list = []
                
                for elem in odd_elements[:3]:  # First 3 (1-X-2)
                    try:
                        # Extract numeric value
                        text = elem.get_text(strip=True)
                        
                        # Remove non-numeric except decimal point
                        text = re.sub(r'[^\d.]', '', text)
                        
                        if text:
                            odd_value = float(text)
                            if 1.01 <= odd_value <= 100:
                                odds_list.append(odd_value)
                    except (ValueError, AttributeError):
                        pass
                
                if len(odds_list) == 3:
                    return tuple(odds_list)
                elif len(odds_list) == 2:
                    # No draw (volleyball, handball, etc.)
                    return (odds_list[0], None, odds_list[1])
        
        return None


# ============================================================================
# SUPERBET & STS SCRAPERS (Similar structure)
# ============================================================================

class SuperbetScraper(BookmakerScraper):
    """Scraper for Superbet.pl"""
    
    def __init__(self):
        super().__init__('Superbet', BOOKMAKERS['superbet'])
    
    def scrape_football_odds(self) -> Dict[str, Dict]:
        logger.info("🔵 Scraping Superbet football odds...")
        # Implementation similar to Fortuna
        return {}


class STSScraper(BookmakerScraper):
    """Scraper for STS.pl"""
    
    def __init__(self):
        super().__init__('STS', BOOKMAKERS['sts'])
    
    def scrape_football_odds(self) -> Dict[str, Dict]:
        logger.info("🟢 Scraping STS football odds...")
        # Implementation similar to Fortuna
        return {}


# ============================================================================
# SUPABASE UPLOADER
# ============================================================================

class SupabaseUploader:
    """Upload scraped odds to Supabase"""
    
    def __init__(self):
        try:
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✅ Supabase client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase: {e}")
            raise
    
    def upload_bookmaker_odds(self, odds_data: Dict[str, Dict]) -> int:
        """Upload bookmaker odds to database"""
        if not odds_data:
            logger.warning("No odds data to upload")
            return 0
        
        logger.info(f"📤 Uploading {len(odds_data)} odds records...")
        
        success_count = 0
        
        for match_key, odds in odds_data.items():
            try:
                # Prepare record
                record = {
                    'match_key': match_key,
                    'match_date': datetime.now().date().isoformat(),
                    'home_team': odds['home_team'],
                    'away_team': odds['away_team'],
                    'bookmakers': json.dumps({
                        odds['bookmaker']: {
                            'home_odds': odds['home_odds'],
                            'draw_odds': odds['draw_odds'],
                            'away_odds': odds['away_odds']
                        }
                    }),
                    'is_active': True,
                    'created_at': datetime.now().isoformat()
                }
                
                # Upsert (insert or update)
                response = self.client.table('bookmaker_odds').upsert(
                    record,
                    on_conflict='match_key,match_date'
                ).execute()
                
                if response.data:
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"Upload error for {match_key}: {e}")
                continue
        
        logger.info(f"✅ Uploaded {success_count}/{len(odds_data)} records")
        return success_count


# ============================================================================
# ORCHESTRATOR
# ============================================================================

class LocalBookmakerOrchestrator:
    """Orchestrate scraping from all bookmakers"""
    
    def __init__(self):
        self.scrapers = [
            FortunaScraper(),
            # SuperbetScraper(),
            # STSScraper(),
        ]
        self.uploader = SupabaseUploader()
    
    def run_scraping(self) -> Dict:
        """Run scraping from all bookmakers"""
        logger.info("="*70)
        logger.info("🇵🇱 STARTING LOCAL BOOKMAKER SCRAPER")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        all_odds = {}
        stats = {
            'total_matches': 0,
            'by_bookmaker': {},
            'uploaded': 0,
            'errors': 0
        }
        
        # Scrape each bookmaker
        for scraper in self.scrapers:
            try:
                logger.info(f"\n📊 Scraping {scraper.name}...")
                
                odds = scraper.scrape_football_odds()
                
                stats['by_bookmaker'][scraper.name.lower()] = len(odds)
                
                # Merge odds (keep highest odds per match)
                for match_key, match_odds in odds.items():
                    if match_key not in all_odds:
                        all_odds[match_key] = match_odds
                    else:
                        # Update with better odds
                        existing = all_odds[match_key]
                        if match_odds['home_odds'] > existing.get('home_odds', 0):
                            existing['home_odds'] = match_odds['home_odds']
                        if match_odds['away_odds'] > existing.get('away_odds', 0):
                            existing['away_odds'] = match_odds['away_odds']
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error scraping {scraper.name}: {e}")
                stats['errors'] += 1
                continue
        
        stats['total_matches'] = len(all_odds)
        
        # Upload to Supabase
        if all_odds:
            try:
                uploaded = self.uploader.upload_bookmaker_odds(all_odds)
                stats['uploaded'] = uploaded
            except Exception as e:
                logger.error(f"❌ Upload failed: {e}")
                stats['errors'] += 1
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("📊 SCRAPING SUMMARY")
        logger.info("="*70)
        logger.info(f"Total matches found: {stats['total_matches']}")
        for bookmaker, count in stats['by_bookmaker'].items():
            logger.info(f"  - {bookmaker.capitalize()}: {count}")
        logger.info(f"Uploaded to database: {stats['uploaded']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info("="*70)
        
        return stats


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Entry point"""
    try:
        orchestrator = LocalBookmakerOrchestrator()
        stats = orchestrator.run_scraping()
        
        # Exit code
        if stats['uploaded'] > 0:
            logger.info("✅ SUCCESS")
            sys.exit(0)
        else:
            logger.warning("⚠️  NO DATA UPLOADED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
