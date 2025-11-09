"""
Livesport H2H scraper - Multi-Sport Edition
-------------------------------------------
Cel: dla danego dnia zapisać do pliku CSV wydarzenia (mecze), w których GOSPODARZE pokonali przeciwników co najmniej 2 razy w ostatnich 5 bezpośrednich spotkaniach (H2H).

Wspierane sporty:
- Piłka nożna (football/soccer)
- Koszykówka (basketball)
- Siatkówka (volleyball)
- Piłka ręczna (handball)
- Rugby
- Hokej (hockey/ice-hockey)

Uwagi / założenia:
- Zakładam, że "ostatnie 5" oznacza 5 ostatnich bezpośrednich spotkań między obiema drużynami (H2H na stronie meczu).
- Skrypt pracuje w trzech trybach:
    * --urls  : przetwarza listę adresów URL meczów (plik tekstowy z jedną linią = jeden URL)
    * --auto  : próbuje zebrać listę linków do meczów z ogólnej strony dla danego dnia
    * --sport : automatycznie zbiera linki dla konkretnych sportów
- Strona Livesport jest mocno zależna od JS — skrypt używa Selenium (Chrome/Chromedriver).
- Przestrzegaj robots.txt i Terms of Use. Skrypt ma opóźnienia (sleep) i limit prób, ale używanie go na dużej skali wymaga uzyskania zgody od właściciela serwisu.

Wymagania:
- Python 3.9+
- pip install selenium beautifulsoup4 pandas webdriver-manager
- Chrome i dopasowany chromedriver (webdriver-manager ułatwia instalację)

Uruchomienie (przykłady):
python livesport_h2h_scraper.py --mode urls --date 2025-10-05 --input match_urls.txt --headless
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball --headless
python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --leagues ekstraklasa premier-league --headless

Plik wynikowy: outputs/livesport_h2h_YYYY-MM-DD.csv (lub z sufixem sportu)

"""

import argparse
import time
import os
import csv
import re
import json
import gc  # Garbage collector dla zarządzania pamięcią
from datetime import datetime
from typing import List, Dict, Optional

import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver

# ✅ V7: Supabase fallback for Polish bookmakers (geo-blocking workaround)
try:
    from supabase import create_client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Retry logic dla zwiększenia niezawodności API calls
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import własnych modułów
import over_under_analyzer

# Database Manager (opcjonalny - dla integracji z aplikacją webową)
try:
    from db_manager import MatchDatabase
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️ db_manager.py nie znaleziony - zapis do bazy danych wyłączony")


# ----------------------
# Helper / scraper code
# ----------------------

# Globalna zmienna kontrolująca poziom szczegółowości logów
VERBOSE = False  # Domyślnie wyłączone, włączane przez --verbose

# Mapowanie sportów na URLe Livesport
SPORT_URLS = {
    'football': 'https://www.livesport.com/pl/pilka-nozna/',
    'soccer': 'https://www.livesport.com/pl/pilka-nozna/',
    'basketball': 'https://www.livesport.com/pl/koszykowka/',
    'volleyball': 'https://www.livesport.com/pl/siatkowka/',
    'handball': 'https://www.livesport.com/pl/pilka-reczna/',
    'rugby': 'https://www.livesport.com/pl/rugby/',
    'hockey': 'https://www.livesport.com/pl/hokej/',
    'ice-hockey': 'https://www.livesport.com/pl/hokej/',
    'tennis': 'https://www.livesport.com/pl/tenis/',
}

# Sporty indywidualne (inna logika kwalifikacji)
INDIVIDUAL_SPORTS = ['tennis']

# Popularne ligi dla każdego sportu (mapowanie slug -> nazwa)
POPULAR_LEAGUES = {
    'football': {
        'ekstraklasa': 'Ekstraklasa',
        'premier-league': 'Premier League',
        'la-liga': 'LaLiga',
        'bundesliga': 'Bundesliga',
        'serie-a': 'Serie A',
        'ligue-1': 'Ligue 1',
        'champions-league': 'Liga Mistrzów',
        'europa-league': 'Liga Europy',
    },
    'basketball': {
        'nba': 'NBA',
        'euroleague': 'Euroliga',
        'energa-basket-liga': 'Energa Basket Liga',
        'pbl': 'Polska Liga Koszykówki',
    },
    'volleyball': {
        'plusliga': 'PlusLiga',
        'tauron-liga': 'Tauron Liga',
    },
    'handball': {
        'pgnig-superliga': 'PGNiG Superliga',
    },
    'rugby': {
        'premiership': 'Premiership',
        'top-14': 'Top 14',
    },
    'hockey': {
        'nhl': 'NHL',
        'khl': 'KHL',
    },
}

H2H_TAB_TEXT_OPTIONS = ["H2H", "Head-to-Head", "Bezpośrednie", "Bezpośrednie spotkania", "H2H"]


def start_driver(headless: bool = True) -> webdriver.Chrome:
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--window-size=1920,1080')
    # human-like user-agent (you may rotate)
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def click_h2h_tab(driver: webdriver.Chrome) -> None:
    """Spróbuj kliknąć zakładkę H2H - sprawdzamy kilka wariantów tekstowych i atrybutów."""
    for text in H2H_TAB_TEXT_OPTIONS:
        try:
            # XPath contains text
            el = driver.find_element(By.XPATH, f"//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]")
            el.click()
            time.sleep(0.8)
            return
        except Exception:
            pass

    # fallback: look for element with data-tab or href containing 'h2h'
    try:
        el = driver.find_element(By.XPATH, "//a[contains(@href, 'h2h') or contains(@data-tab, 'h2h')]")
        el.click()
        time.sleep(0.8)
        return
    except Exception:
        pass

    # if nothing works, do nothing and hope content is already present


def parse_h2h_from_soup(soup: BeautifulSoup, home_team: str, debug_url: str = None) -> List[Dict]:
    """Parsuje sekcję H2H i zwraca listę ostatnich spotkań (do 5).
    Zwracany format: [{'date':..., 'home':..., 'away':..., 'score': 'x - y', 'winner': 'home'/'away'/'draw'}]
    """
    results = []

    # METODA 1: Szukaj sekcji H2H
    h2h_sections = soup.find_all('div', class_='h2h__section')
    
    if not h2h_sections:
        h2h_sections = soup.find_all('div', class_=re.compile(r'h2h'))
    
    if not h2h_sections:
        # METODA 2: Szukaj bezpośrednio wierszy H2H
        all_h2h_rows = soup.select('a.h2h__row, div.h2h__row, [class*="h2h__row"]')
        if all_h2h_rows:
            return _parse_h2h_rows(all_h2h_rows[:5], debug_url)
    
    # DEBUG: Zapisz HTML gdy brak H2H
    if not h2h_sections and debug_url:
        try:
            debug_file = 'outputs/debug_no_h2h.html'
            os.makedirs('outputs', exist_ok=True)
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"<!-- DEBUG: Brak sekcji H2H dla URL: {debug_url} -->\n")
                f.write(str(soup.prettify()))
        except:
            pass
    
    # Szukaj sekcji "Pojedynki bezpośrednie"
    pojedynki_section = None
    for section in h2h_sections:
        text = section.get_text(" ", strip=True)
        if 'pojedynki' in text.lower() or 'bezpośrednie' in text.lower() or 'head' in text.lower():
            pojedynki_section = section
            break
    
    if not pojedynki_section and h2h_sections:
        pojedynki_section = h2h_sections[0]
    
    if not pojedynki_section:
        return results
    
    # Znajdź wiersze z meczami - próbuj różnych selektorów
    match_rows = pojedynki_section.select('a.h2h__row')
    if not match_rows:
        match_rows = pojedynki_section.select('div.h2h__row')
    if not match_rows:
        match_rows = pojedynki_section.select('[class*="h2h__row"]')
    if not match_rows:
        match_rows = pojedynki_section.select('a, div[class*="row"]')
    
    return _parse_h2h_rows(match_rows[:5], debug_url)


def _parse_h2h_rows(match_rows: list, debug_url: str = None) -> List[Dict]:
    """
    Pomocnicza funkcja do parsowania wierszy H2H.
    Wydzielona aby można było jej użyć z różnych miejsc.
    """
    results = []
    
    for idx, row in enumerate(match_rows, 1):
        try:
            # Data
            date_el = row.select_one('span.h2h__date, [class*="date"]')
            date = date_el.get_text(strip=True) if date_el else ''
            
            # Gospodarz - próbuj różnych selektorów
            home = None
            home_selectors = [
                'span.h2h__homeParticipant span.h2h__participantInner',
                'span.h2h__homeParticipant',
                '[class*="homeParticipant"]',
            ]
            for selector in home_selectors:
                home_el = row.select_one(selector)
                if home_el:
                    home = home_el.get_text(strip=True)
                    if home:
                        break
            
            # Gość - próbuj różnych selektorów
            away = None
            away_selectors = [
                'span.h2h__awayParticipant span.h2h__participantInner',
                'span.h2h__awayParticipant',
                '[class*="awayParticipant"]',
            ]
            for selector in away_selectors:
                away_el = row.select_one(selector)
                if away_el:
                    away = away_el.get_text(strip=True)
                    if away:
                        break
            
            # Fallback: wyciągnij z tekstu
            if not home or not away:
                row_text = row.get_text(strip=True)
                teams_match = re.search(r'(.+?)\s+(?:-|vs|–)\s+(.+?)(?:\d|$)', row_text)
                if teams_match:
                    if not home:
                        home = teams_match.group(1).strip()
                    if not away:
                        away = teams_match.group(2).strip()
            
            # Wynik - próbuj różnych metod
            score = ''
            winner = 'unknown'
            
            # Metoda 1: Standardowe selektory
            result_spans = row.select('span.h2h__result span, [class*="result"] span')
            if len(result_spans) >= 2:
                goals_home = result_spans[0].get_text(strip=True)
                goals_away = result_spans[1].get_text(strip=True)
                score = f"{goals_home}-{goals_away}"
                
                try:
                    gh = int(goals_home)
                    ga = int(goals_away)
                    winner = 'home' if gh > ga else ('away' if ga > gh else 'draw')
                except:
                    winner = 'unknown'
            
            # Metoda 2: Regex z całego tekstu
            if not score:
                row_text = row.get_text(strip=True)
                score_match = re.search(r'(\d+)\s*[:\-–—]\s*(\d+)', row_text)
                if score_match:
                    goals_home = score_match.group(1)
                    goals_away = score_match.group(2)
                    score = f"{goals_home}-{goals_away}"
                    
                    try:
                        gh = int(goals_home)
                        ga = int(goals_away)
                        winner = 'home' if gh > ga else ('away' if ga > gh else 'draw')
                    except:
                        winner = 'unknown'

            if home and away and score:
                results.append({
                    'date': date,
                    'home': home,
                    'away': away,
                    'score': score,
                    'winner': winner,
                    'raw': f"{date} {home} {score} {away}"
                })
        
        except Exception as e:
            continue

    return results


def process_match(url: str, driver: webdriver.Chrome, away_team_focus: bool = False, sport: str = None) -> Dict:
    """Odwiedza stronę meczu, otwiera H2H i zwraca informację we właściwym formacie.
    
    Args:
        url: URL meczu
        driver: Selenium WebDriver
        away_team_focus: Jeśli True, liczy zwycięstwa GOŚCI w H2H zamiast gospodarzy
        sport: Sport type (volleyball, handball, football, basketball, etc.) for dynamic betType
    """
    out = {
        'match_url': url,
        'home_team': None,
        'away_team': None,
        'match_time': None,
        'h2h_last5': [],
        'home_wins_in_h2h_last5': 0,
        'away_wins_in_h2h_last5': 0,  # NOWE: dla trybu away_team_focus
        'h2h_count': 0,
        'win_rate': 0.0,  # % wygranych gospodarzy/gości w H2H (zależnie od trybu)
        'qualifies': False,
        'home_form': [],  # Forma gospodarzy: ['W', 'L', 'W', 'D', 'W']
        'away_form': [],  # Forma gości: ['L', 'L', 'W', 'L', 'W']
        'home_odds': None,  # Kursy bukmacherskie (info dodatkowa)
        'away_odds': None,
        'focus_team': 'away' if away_team_focus else 'home',  # NOWE: który tryb
    }

    # KLUCZOWE: Przekieruj URL na stronę H2H (zamiast szczegoly)
    # POPRAWKA: Obsługa URL z parametrem ?mid=
    
    # Wyciągnij część bazową i parametry
    if '?' in url:
        base_url, params = url.split('?', 1)
        params = '?' + params
    else:
        base_url = url
        params = ''
    
    # Usuń końcowy slash jeśli istnieje
    base_url = base_url.rstrip('/')
    
    # Zamień /szczegoly/ na /h2h/ogolem/ lub dodaj /h2h/ogolem/
    if '/szczegoly' in base_url:
        base_url = base_url.replace('/szczegoly', '/h2h/ogolem')
    elif '/h2h/' not in base_url:
        base_url = base_url + '/h2h/ogolem'
    
    # Połącz z powrotem: base_url + params
    h2h_url = base_url + params
    
    try:
        driver.get(h2h_url)
        
        # OPTYMALIZACJA: Czekaj tylko na kluczowe elementy (max 5s)
        try:
            wait = WebDriverWait(driver, 5)  # Zmniejszone z 8s na 5s
            # Czekaj aż załaduje się JAKAKOLWIEK zawartość H2H
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="h2h"], section[class*="h2h"]')))
        except TimeoutException:
            pass  # Kontynuuj mimo timeout
        
        # Krótki dodatkowy czas na renderowanie (zredukowany z 2s na 1s)
        time.sleep(1.0)
        
        # Scroll raz w dół i raz w górę (szybko)
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.15)  # Zmniejszone z 0.3s na 0.15s
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.15)  # Zmniejszone z 0.3s na 0.15s
        except:
            pass
            
    except WebDriverException as e:
        print(f"   ❌ Błąd: {e}")
        return out

    # pobierz tytuł strony jako fallback na nazwy druzyn
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # spróbuj wyciągnąć nazwy drużyn z nagłówka
        title = soup.title.string if soup.title else ''
        if title:
            # tytuł często ma formę "Home - Away" lub "Home vs Away"
            import re
            m = re.split(r"\s[-–—|]\s|\svs\s|\sv\s", title)
            if len(m) >= 2:
                out['home_team'] = m[0].strip()
                out['away_team'] = m[1].strip()
    except Exception:
        pass

    # NIE MUSIMY KLIKAĆ H2H - już jesteśmy na stronie /h2h/ogolem/
    # Zawartość już została załadowana przez WebDriverWait powyżej
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # try to extract team names from the page header - NOWE SELEKTORY
    try:
        # Nowa struktura Livesport (2025)
        home_el = soup.select_one("div.smv__participantRow.smv__homeParticipant a.participant__participantName")
        if not home_el:
            home_el = soup.select_one("a.participant__participantName")
        if home_el:
            out['home_team'] = home_el.get_text(strip=True)
    except Exception:
        pass

    try:
        away_el = soup.select_one("div.smv__participantRow.smv__awayParticipant a.participant__participantName")
        if not away_el:
            # Fallback: weź drugą nazwę drużyny
            all_teams = soup.select("a.participant__participantName")
            if len(all_teams) >= 2:
                away_el = all_teams[1]
        if away_el:
            out['away_team'] = away_el.get_text(strip=True)
    except Exception:
        pass
    
    # Wydobądź datę i godzinę meczu
    try:
        # Szukaj różnych możliwych selektorów dla daty/czasu
        # Próba 1: Element z czasem startu
        time_el = soup.select_one("div.duelParticipant__startTime")
        if time_el:
            out['match_time'] = time_el.get_text(strip=True)
        
        # Próba 2: Z tytułu strony (często zawiera datę)
        if not out['match_time'] and soup.title:
            title = soup.title.string
            # Szukaj wzorca daty i czasu w tytule
            import re
            # Format: DD.MM.YYYY HH:MM lub podobne
            date_match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{2,4})\s*(\d{1,2}:\d{2})?', title)
            if date_match:
                date_str = date_match.group(1)
                time_str = date_match.group(2) if date_match.group(2) else ''
                out['match_time'] = f"{date_str} {time_str}".strip()
        
        # Próba 3: Z URL (może zawierać datę)
        if not out['match_time']:
            # Czasem data jest w parametrach URL
            if 'date=' in h2h_url:
                import re
                date_param = re.search(r'date=([^&]+)', h2h_url)
                if date_param:
                    out['match_time'] = date_param.group(1)
    except Exception:
        pass

    # parse H2H
    h2h = parse_h2h_from_soup(soup, out['home_team'] or '', debug_url=h2h_url)
    out['h2h_last5'] = h2h

    # count home AND away wins in H2H list
    # WAŻNE: W zależności od trybu (away_team_focus), liczymy zwycięstwa gospodarzy lub gości
    cnt_home = 0
    cnt_away = 0
    current_home = out['home_team']
    current_away = out['away_team']
    
    for item in h2h:
        try:
            # Pobierz nazwy drużyn i wynik z H2H meczu
            h2h_home = item.get('home', '').strip()
            h2h_away = item.get('away', '').strip()
            score = item.get('score', '')
            
            # Parsuj wynik
            import re
            score_match = re.search(r"(\d+)\s*[:\-]\s*(\d+)", score)
            if not score_match:
                continue
            
            goals_home_side = int(score_match.group(1))
            goals_away_side = int(score_match.group(2))
            
            # Sprawdź który zespół wygrał w tamtym meczu H2H
            if goals_home_side > goals_away_side:
                winner_team = h2h_home
            elif goals_away_side > goals_home_side:
                winner_team = h2h_away
            else:
                winner_team = None  # remis
            
            # Teraz sprawdź czy zwycięzcą był AKTUALNY GOSPODARZ
            if winner_team and current_home:
                winner_normalized = winner_team.lower().strip()
                current_home_normalized = current_home.lower().strip()
                
                if (winner_normalized == current_home_normalized or 
                    winner_normalized in current_home_normalized or 
                    current_home_normalized in winner_normalized):
                    cnt_home += 1
            
            # Teraz sprawdź czy zwycięzcą byli AKTUALNI GOŚCIE
            if winner_team and current_away:
                winner_normalized = winner_team.lower().strip()
                current_away_normalized = current_away.lower().strip()
                
                if (winner_normalized == current_away_normalized or 
                    winner_normalized in current_away_normalized or 
                    current_away_normalized in winner_normalized):
                    cnt_away += 1
                    
        except Exception as e:
            # Fallback: użyj starej heurystyki
            if item.get('winner') == 'home' and current_home:
                h2h_home = item.get('home', '').lower().strip()
                if current_home.lower().strip() in h2h_home or h2h_home in current_home.lower().strip():
                    cnt_home += 1
            if item.get('winner') == 'away' and current_away:
                h2h_away = item.get('away', '').lower().strip()
                if current_away.lower().strip() in h2h_away or h2h_away in current_away.lower().strip():
                    cnt_away += 1

    out['home_wins_in_h2h_last5'] = cnt_home
    out['away_wins_in_h2h_last5'] = cnt_away
    out['h2h_count'] = len(h2h)
    
    # NOWE KRYTERIUM: W zależności od trybu, sprawdzamy gospodarzy lub gości
    if away_team_focus:
        # Tryb GOŚCIE: Goście wygrali ≥60% meczów H2H
        win_rate = (cnt_away / len(h2h)) if len(h2h) > 0 else 0.0
        out['win_rate'] = win_rate
        basic_qualifies = win_rate >= 0.60 and len(h2h) >= 1
    else:
        # Tryb GOSPODARZE (domyślny): Gospodarze wygrali ≥60% meczów H2H
        win_rate = (cnt_home / len(h2h)) if len(h2h) > 0 else 0.0
        out['win_rate'] = win_rate
        basic_qualifies = win_rate >= 0.60 and len(h2h) >= 1
    
    # FORMA DRUŻYN: Dodaj pola dla zaawansowanej analizy
    out['home_form'] = []  # Forma ogólna (stara metoda)
    out['away_form'] = []
    out['home_form_overall'] = []  # NOWE: Forma z H2H overall
    out['home_form_home'] = []     # NOWE: Forma u siebie
    out['away_form_overall'] = []  # NOWE: Forma z H2H overall
    out['away_form_away'] = []     # NOWE: Forma na wyjeździe
    out['form_advantage'] = False  # NOWE: Czy gospodarze mają przewagę formy?
    
    # JEŚLI PODSTAWOWO SIĘ KWALIFIKUJE - sprawdź zaawansowaną formę
    if basic_qualifies:
        team_name = out['away_team'] if away_team_focus else out['home_team']
        print(f"   📊 Podstawowo kwalifikuje ({'GOŚCIE' if away_team_focus else 'GOSPODARZE'}: {team_name}, H2H: {win_rate*100:.0f}%) - sprawdzam formę...")
        try:
            # ZAAWANSOWANA ANALIZA FORMY (3 źródła)
            advanced_form = extract_advanced_team_form(url, driver)
            
            out['home_form_overall'] = advanced_form['home_form_overall']
            out['home_form_home'] = advanced_form['home_form_home']
            out['away_form_overall'] = advanced_form['away_form_overall']
            out['away_form_away'] = advanced_form['away_form_away']
            
            # W trybie away_team_focus, przewaga formy to GOŚCIE w dobrej formie i GOSPODARZE w słabej
            if away_team_focus:
                out['form_advantage'] = advanced_form.get('away_advantage', False)
            else:
                out['form_advantage'] = advanced_form['form_advantage']
            
            # Dla kompatybilności wstecznej - ustaw starą formę
            out['home_form'] = advanced_form['home_form_overall']
            out['away_form'] = advanced_form['away_form_overall']
            
            # FINALNE KRYTERIUM: H2H ≥60% (podstawowe)
            # Forma jest BONUSEM (dodatkowa ikona 🔥), nie wymogiem
            out['qualifies'] = basic_qualifies
            
            if out['form_advantage']:
                if away_team_focus:
                    print(f"   ✅ KWALIFIKUJE + PRZEWAGA FORMY GOŚCI! 🔥")
                else:
                    print(f"   ✅ KWALIFIKUJE + PRZEWAGA FORMY GOSPODARZY! 🔥")
                print(f"      Home ogółem: {format_form(advanced_form['home_form_overall'])}")
                print(f"      Home u siebie: {format_form(advanced_form['home_form_home'])}")
                print(f"      Away ogółem: {format_form(advanced_form['away_form_overall'])}")
                print(f"      Away na wyjeździe: {format_form(advanced_form['away_form_away'])}")
            elif advanced_form['home_form_overall'] or advanced_form['away_form_overall']:
                print(f"   ✅ KWALIFIKUJE (forma dostępna, ale brak przewagi)")
                print(f"      Home ogółem: {format_form(advanced_form['home_form_overall'])}")
                print(f"      Away ogółem: {format_form(advanced_form['away_form_overall'])}")
            else:
                print(f"   ✅ KWALIFIKUJE (brak danych formy - tylko H2H)")
                
        except Exception as e:
            print(f"   ⚠️ Błąd analizy formy: {e}")
            # Fallback - używamy starego kryterium
            out['qualifies'] = basic_qualifies
            # Pobierz formę starą metodą
            try:
                home_form = extract_team_form(soup, driver, 'home', out.get('home_team'))
                away_form = extract_team_form(soup, driver, 'away', out.get('away_team'))
                out['home_form'] = home_form
                out['away_form'] = away_form
            except:
                pass
    else:
        # Nie kwalifikuje się podstawowo - nie sprawdzaj formy
        out['qualifies'] = False
    
    # Kursy bukmacherskie - dodatkowa informacja (NIE wpływa na scoring!)
    # UŻYWAMY PRAWDZIWEGO API LIVESPORT z MULTI-BOOKMAKER SUPPORT!
    # V4: Dodano tenacity @retry + fallback handling
    # V5: FALLBACK SELENIUM dla volleyball/tennis/handball (API nie ma pokrycia)
    # V6: Przekaż sport do API dla dynamic betType (HOME_AWAY vs HOME_DRAW_AWAY)
    try:
        # ✅ V6: Detect sport from URL if not provided
        detected_sport = sport
        if not detected_sport:
            if '/siatkowka/' in url or '/volleyball/' in url:
                detected_sport = 'volleyball'
            elif '/pilka-reczna/' in url or '/handball/' in url:
                detected_sport = 'handball'
            elif '/koszykowka/' in url or '/basketball/' in url:
                detected_sport = 'basketball'
            else:
                detected_sport = 'football'  # default
        
        odds = extract_betting_odds_with_api(url, use_multi_bookmaker=True, sport=detected_sport)  # V6: Sport param
        
        # ✅ V7 FALLBACK 1: Supabase (Polish bookmakers from local scraper)
        if not odds.get('home_odds') and not odds.get('away_odds'):
            if VERBOSE:
                print(f"   🇵🇱 API failed - trying Supabase (Polish bookmakers)...")
            
            supabase_odds = get_polish_bookmaker_odds_from_supabase(
                home_team=out.get('home_team'),
                away_team=out.get('away_team'),
                sport=detected_sport
            )
            
            if supabase_odds.get('home_odds'):
                odds = supabase_odds
                if VERBOSE:
                    print(f"   ✅ Supabase SUCCESS: {supabase_odds.get('bookmakers_found')}")
        
        # ✅ V7 FALLBACK 2: Selenium scraping (last resort)
        if not odds.get('home_odds') and not odds.get('away_odds'):
            if VERBOSE:
                print(f"   ⚠️ Supabase failed - trying Selenium scraping (last resort)...")
            odds = extract_betting_odds_selenium(soup, driver, url)  # V5: Nowa funkcja Selenium
        
        out['home_odds'] = odds.get('home_odds')
        out['away_odds'] = odds.get('away_odds')
        out['draw_odds'] = odds.get('draw_odds')  # DODANE: Remis
        out['bookmakers_found'] = odds.get('bookmakers_found', [])  # NOWE
        out['best_home_bookmaker'] = odds.get('best_home_bookmaker')  # NOWE
        out['best_away_bookmaker'] = odds.get('best_away_bookmaker')  # NOWE
        out['all_odds'] = odds.get('all_odds', {})  # NOWE V3: Wszystkie kursy z bukmacherów
    except Exception as e:
        # Fallback po wszystkich retry - zapis None
        if VERBOSE:
            print(f"   ⚠️ extract_betting_odds_with_api failed po wszystkich retry: {e}")
        out['home_odds'] = None
        out['away_odds'] = None
        out['draw_odds'] = None
        out['bookmakers_found'] = []
        out['best_home_bookmaker'] = None
        out['best_away_bookmaker'] = None
        out['all_odds'] = {}
    
    # ===================================================================
    # ANALIZA OVER/UNDER - Statystyki bramek/punktów
    # ===================================================================
    # Krok 1: Pobierz kursy O/U z API (żeby mieć rzeczywistą linię)
    # Krok 2: Użyj linii z API w analizie H2H
    # Krok 3: Zapisz rekomendację (OVER lub UNDER)
    
    out['ou_qualifies'] = False
    out['ou_recommendation'] = None  # 'OVER' lub 'UNDER'
    out['ou_line'] = None
    out['ou_line_type'] = None
    out['ou_h2h_percentage'] = 0.0
    out['over_odds'] = None
    out['under_odds'] = None
    out['btts_qualifies'] = False
    out['btts_h2h_percentage'] = 0.0
    out['btts_yes_odds'] = None
    out['btts_no_odds'] = None
    
    # Wykryj sport z URL
    sport = 'football'
    if 'koszykowka' in url.lower() or 'basketball' in url.lower():
        sport = 'basketball'
    elif 'siatkowka' in url.lower() or 'volleyball' in url.lower():
        sport = 'volleyball'
    elif 'pilka-reczna' in url.lower() or 'handball' in url.lower():
        sport = 'handball'
    elif 'hokej' in url.lower() or 'hockey' in url.lower():
        sport = 'hockey'
    elif 'tenis' in url.lower() or 'tennis' in url.lower():
        sport = 'tennis'
    
    # KROK 1: Pobierz kursy O/U z API (dynamiczna linia)
    api_line = None
    if url and '?mid=' in url and len(h2h) >= 5:
        try:
            from livesport_odds_api_client import LiveSportOddsAPI
            odds_client = LiveSportOddsAPI()
            event_id = odds_client.extract_event_id_from_url(url)
            
            if event_id:
                # Kursy O/U
                ou_odds = odds_client.get_over_under_odds(event_id, sport)
                if ou_odds:
                    out['over_odds'] = ou_odds.get('over_odds')
                    out['under_odds'] = ou_odds.get('under_odds')
                    api_line = ou_odds.get('line')  # Rzeczywista linia z API!
                
                # Kursy BTTS (tylko football)
                if sport == 'football':
                    btts_odds = odds_client.get_btts_odds(event_id)
                    if btts_odds:
                        out['btts_yes_odds'] = btts_odds.get('btts_yes')
                        out['btts_no_odds'] = btts_odds.get('btts_no')
        except Exception as e:
            if VERBOSE:
                print(f"   ⚠️ Błąd pobierania kursów O/U: {e}")
    
    # KROK 2: Wykonaj analizę O/U używając linii z API (jeśli dostępna)
    if len(h2h) >= 5:
        try:
            # Domyślne linie jeśli API nie zwraca
            default_lines = {
                'football': 2.5,
                'basketball': 220.5,
                'handball': 55.5,
                'volleyball': 4.5,
                'hockey': 5.5,
                'tennis': 2.5
            }
            
            line_to_use = api_line if api_line else default_lines.get(sport, 2.5)
            
            ou_analysis = over_under_analyzer.analyze_over_under(
                sport=sport,
                h2h_results=h2h,
                home_form=h2h,
                away_form=h2h,
                line=line_to_use  # Użyj linii z API!
            )
            
            if ou_analysis and ou_analysis.get('qualifies'):
                out['ou_qualifies'] = True
                out['ou_recommendation'] = ou_analysis.get('recommendation')  # 'OVER' lub 'UNDER'
                out['ou_line'] = str(ou_analysis.get('line', ''))
                out['ou_line_type'] = ou_analysis.get('line_type', '')
                out['ou_h2h_percentage'] = ou_analysis.get('h2h_over_percentage', 0.0)
                
                # Football: dodatkowo BTTS
                if sport == 'football' and 'btts_qualifies' in ou_analysis:
                    out['btts_qualifies'] = ou_analysis.get('btts_qualifies', False)
                    out['btts_h2h_percentage'] = ou_analysis.get('btts_h2h_percentage', 0.0)
        
        except Exception as e:
            if VERBOSE:
                print(f"   ⚠️ Błąd analizy O/U: {e}")

    # ==================================================================
    # ŚREDNIE BRAMEK/PUNKTÓW - Oblicz z H2H
    # ==================================================================
    try:
        if len(h2h) > 0:
            home_goals_sum = 0
            away_goals_sum = 0
            valid_matches = 0
            
            for match in h2h:
                # Każdy mecz H2H powinien mieć score w formacie "X:Y"
                score = match.get('score', '')
                if score and ':' in score:
                    try:
                        parts = score.split(':')
                        home_score = int(parts[0].strip())
                        away_score = int(parts[1].strip())
                        home_goals_sum += home_score
                        away_goals_sum += away_score
                        valid_matches += 1
                    except (ValueError, IndexError):
                        pass  # Pomiń nieprawidłowe wyniki
            
            if valid_matches > 0:
                out['avg_home_goals'] = round(home_goals_sum / valid_matches, 2)
                out['avg_away_goals'] = round(away_goals_sum / valid_matches, 2)
            else:
                out['avg_home_goals'] = None
                out['avg_away_goals'] = None
        else:
            out['avg_home_goals'] = None
            out['avg_away_goals'] = None
    except Exception as e:
        if VERBOSE:
            print(f"   ⚠️ Błąd obliczania średnich bramek: {e}")
        out['avg_home_goals'] = None
        out['avg_away_goals'] = None

    return out


def format_form(form_list: List[str]) -> str:
    """
    Formatuje listę formy do ładnego stringa z emoji.
    
    Args:
        form_list: ['W', 'L', 'D', 'W', 'W']
    
    Returns:
        'W✅ L❌ D🟡 W✅ W✅'
    """
    emoji_map = {'W': '✅', 'L': '❌', 'D': '🟡'}
    return ' '.join([f"{r}{emoji_map.get(r, '')}" for r in form_list])


def extract_advanced_team_form(match_url: str, driver: webdriver.Chrome) -> Dict:
    """
    Ekstraktuje zaawansowaną formę drużyn z 3 źródeł:
    1. Forma ogólna (ostatnie 5 meczów)
    2. Forma u siebie (gospodarze)
    3. Forma na wyjeździe (goście)
    
    Returns:
        {
            'home_form_overall': ['W', 'L', 'D', 'W', 'W'],
            'home_form_home': ['W', 'W', 'W', 'D', 'W'],  # Forma gospodarzy u siebie
            'away_form_overall': ['L', 'L', 'W', 'L', 'D'],
            'away_form_away': ['L', 'L', 'L', 'D', 'L'],  # Forma gości na wyjeździe
            'form_advantage': True/False  # Czy gospodarze mają przewagę?
        }
    """
    result = {
        'home_form_overall': [],
        'home_form_home': [],
        'away_form_overall': [],
        'away_form_away': [],
        'form_advantage': False
    }
    
    try:
        # Konwertuj URL meczu na URL H2H
        # Z: /mecz/pilka-nozna/team1/team2/?mid=XXX
        # Na: /mecz/pilka-nozna/team1/team2/h2h/ogolem/?mid=XXX (lub /u-siebie/, /na-wyjezdzie/)
        
        if '/match/' in match_url or '/mecz/' in match_url:
            base_url = match_url.split('?')[0]  # Usuń query params
            
            # Usuń końcówkę "/szczegoly" lub inną stronę, jeśli istnieje
            base_url = base_url.rstrip('/')
            if base_url.endswith('/szczegoly') or base_url.endswith('/szczegoly/'):
                base_url = base_url.replace('/szczegoly', '')
            
            mid = match_url.split('mid=')[1] if 'mid=' in match_url else ''
            
            # 1. FORMA OGÓLNA
            h2h_overall_url = f"{base_url}/h2h/ogolem/?mid={mid}"
            result['home_form_overall'], result['away_form_overall'] = _extract_form_from_h2h_page(
                h2h_overall_url, driver, 'overall'
            )
            
            # 2. FORMA U SIEBIE (gospodarze)
            h2h_home_url = f"{base_url}/h2h/u-siebie/?mid={mid}"
            result['home_form_home'], _ = _extract_form_from_h2h_page(
                h2h_home_url, driver, 'home'
            )
            
            # 3. FORMA NA WYJEŹDZIE (goście)
            h2h_away_url = f"{base_url}/h2h/na-wyjezdzie/?mid={mid}"
            _, result['away_form_away'] = _extract_form_from_h2h_page(
                h2h_away_url, driver, 'away'
            )
            
            # 4. ANALIZA PRZEWAGI FORMY
            result['form_advantage'] = _analyze_form_advantage(result)
            # 5. ANALIZA PRZEWAGI GOŚCI (dla trybu away_team_focus)
            result['away_advantage'] = _analyze_away_form_advantage(result)
            
    except Exception as e:
        print(f"   ⚠️ extract_advanced_team_form error: {e}")
    
    return result


def _extract_form_from_h2h_page(url: str, driver: webdriver.Chrome, context: str) -> tuple:
    """
    Pomocnicza funkcja do ekstraktowania formy z konkretnej strony H2H.
    
    Args:
        url: URL strony H2H
        driver: Selenium WebDriver
        context: 'overall', 'home', lub 'away'
    
    Returns:
        (home_form, away_form) - każda to lista ['W', 'L', 'D', ...]
    """
    home_form = []
    away_form = []
    
    try:
        driver.get(url)
        time.sleep(1.5)  # Zmniejszone z 3.0s na 1.5s - czas na załadowanie dynamicznych elementów
        
        # Scroll down to trigger lazy-loading content
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)  # Zmniejszone z 1.0s na 0.5s
        except:
            pass
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # NOWA METODA: Ekstraktuj formy z sekcji h2h__section
        # Livesport organizuje dane w sekcje:
        # - /h2h/ogolem/ -> 2 sekcje: home (idx=0), away (idx=1)
        # - /h2h/u-siebie/ -> 1 sekcja: home form at home (idx=0)
        # - /h2h/na-wyjezdzie/ -> 1 sekcja: away form away (idx=0)
        h2h_sections = soup.find_all('div', class_='h2h__section')
        
        for idx, section in enumerate(h2h_sections[:2]):  # Pierwsz 2 sekcje (home, away)
            # Szukaj wszystkich form badges w tej sekcji
            badges = section.find_all('div', class_='wcl-badgeform_AKaAR')
            
            temp_form = []
            for badge in badges[:5]:  # Max 5 wyników
                text = badge.get_text().strip()
                title = badge.get('title', '')
                
                # Konwersja: Z->W, R->D, P->L
                if 'Zwyci' in title or text == 'Z':
                    temp_form.append('W')
                elif 'Remis' in title or text == 'R':
                    temp_form.append('D')
                elif 'Pora' in title or text == 'P':
                    temp_form.append('L')
            
            # Przypisanie zależy od kontekstu:
            if context == 'overall':
                # Na stronie /h2h/ogolem/ są 2 sekcje
                if idx == 0:
                    home_form = temp_form
                elif idx == 1:
                    away_form = temp_form
            elif context == 'home':
                # Na stronie /h2h/u-siebie/ jest 1 sekcja (gospodarze u siebie)
                if idx == 0:
                    home_form = temp_form
            elif context == 'away':
                # Na stronie /h2h/na-wyjezdzie/ jest 1 sekcja (goście na wyjeździe)
                if idx == 0:
                    away_form = temp_form
        
        # Debug: Pokaż znalezione formy
        if context == 'away' and away_form:
            print(f"      ✓ Forma gości NA WYJEŹDZIE: {away_form}")
        
        # FALLBACK: Jeśli powyższa metoda nie zadziała, spróbuj starej metody
        # Warunek zależy od kontekstu:
        needs_fallback = False
        if context == 'overall' and (not home_form or not away_form):
            needs_fallback = True
        elif context == 'home' and not home_form:
            needs_fallback = True
        elif context == 'away' and not away_form:
            needs_fallback = True
        
        if needs_fallback:
            h2h_rows = soup.select('div.h2h__row, tr.h2h')
            
            for row in h2h_rows[:5]:
                # Sprawdź wynik meczu
                score_elem = row.select_one('div[class*="score"], span[class*="score"]')
                if score_elem:
                    score_text = score_elem.get_text(strip=True)
                    # Format: "3:1" lub "1:0"
                    if ':' in score_text:
                        try:
                            home_score, away_score = map(int, score_text.split(':'))
                            if home_score > away_score:
                                if context in ['overall', 'home']:
                                    home_form.append('W')
                                if context in ['overall', 'away']:
                                    away_form.append('L')
                            elif away_score > home_score:
                                if context in ['overall', 'home']:
                                    home_form.append('L')
                                if context in ['overall', 'away']:
                                    away_form.append('W')
                            else:
                                if context in ['overall', 'home']:
                                    home_form.append('D')
                                if context in ['overall', 'away']:
                                    away_form.append('D')
                        except:
                            continue
                            
    except Exception as e:
        print(f"      ⚠️ _extract_form_from_h2h_page error ({context}): {e}")
    
    return (home_form[:5], away_form[:5])


def _analyze_form_advantage(form_data: Dict) -> bool:
    """
    Analizuje czy gospodarze mają przewagę w formie.
    
    Kryteria:
    - Gospodarze w dobrej formie (więcej W+D niż L)
    - Goście w słabej formie (więcej L niż W+D)
    - Gospodarze lepsi od gości
    
    Returns:
        True jeśli gospodarze mają przewagę
    """
    try:
        # Oblicz punkty formy (W=3, D=1, L=0)
        def form_points(form_list):
            points = 0
            for result in form_list:
                if result == 'W':
                    points += 3
                elif result == 'D':
                    points += 1
            return points
        
        # Forma ogólna
        home_overall_pts = form_points(form_data['home_form_overall'])
        away_overall_pts = form_points(form_data['away_form_overall'])
        
        # Forma kontekstowa (u siebie/na wyjeździe)
        home_home_pts = form_points(form_data['home_form_home'])
        away_away_pts = form_points(form_data['away_form_away'])
        
        # Przewaga jeśli:
        # 1. Gospodarze mają więcej punktów (ogółem)
        # 2. Gospodarze u siebie > Goście na wyjeździe
        # 3. Gospodarze w dobrej formie (>= 7 pkt z 15 możliwych)
        
        home_good_form = home_overall_pts >= 7  # >= 2.3 pkt/mecz
        away_poor_form = away_overall_pts <= 6   # <= 1.2 pkt/mecz
        
        home_better = (home_overall_pts > away_overall_pts and 
                      home_home_pts > away_away_pts)
        
        return (home_good_form and away_poor_form) or home_better
        
    except Exception:
        return False


def _analyze_away_form_advantage(form_data: Dict) -> bool:
    """
    Analizuje czy GOŚCIE mają przewagę w formie.
    
    Kryteria (odwrotne niż dla gospodarzy):
    - Goście w dobrej formie (więcej W+D niż L)
    - Gospodarze w słabej formie (więcej L niż W+D)
    - Goście lepsi od gospodarzy
    
    Returns:
        True jeśli goście mają przewagę
    """
    try:
        # Oblicz punkty formy (W=3, D=1, L=0)
        def form_points(form_list):
            points = 0
            for result in form_list:
                if result == 'W':
                    points += 3
                elif result == 'D':
                    points += 1
            return points
        
        # Forma ogólna
        home_overall_pts = form_points(form_data['home_form_overall'])
        away_overall_pts = form_points(form_data['away_form_overall'])
        
        # Forma kontekstowa (u siebie/na wyjeździe)
        home_home_pts = form_points(form_data['home_form_home'])
        away_away_pts = form_points(form_data['away_form_away'])
        
        # Przewaga GOŚCI jeśli:
        # 1. Goście mają więcej punktów (ogółem)
        # 2. Goście na wyjeździe > Gospodarze u siebie
        # 3. Goście w dobrej formie (>= 7 pkt z 15 możliwych)
        
        away_good_form = away_overall_pts >= 7  # >= 2.3 pkt/mecz
        home_poor_form = home_overall_pts <= 6   # <= 1.2 pkt/mecz
        
        away_better = (away_overall_pts > home_overall_pts and 
                      away_away_pts > home_home_pts)
        
        return (away_good_form and home_poor_form) or away_better
        
    except Exception:
        return False


def extract_team_form(soup: BeautifulSoup, driver: webdriver.Chrome, side: str, team_name: str) -> List[str]:
    """
    Ekstraktuje formę drużyny (ostatnie 5 meczów: W/L/D).
    
    Args:
        soup: BeautifulSoup object strony meczu
        driver: Selenium WebDriver
        side: 'home' lub 'away'
        team_name: Nazwa drużyny
    
    Returns:
        Lista wyników: ['W', 'W', 'L', 'D', 'W'] (od najnowszego do najstarszego)
    """
    form = []
    
    try:
        # METODA 1: Szukaj elementów formy na stronie (ikony W/L/D)
        # Livesport często ma elementy z klasami typu "form__cell--win", "form__cell--loss", etc.
        
        if side == 'home':
            form_selectors = [
                'div.smv__homeParticipant div[class*="form"]',
                'div.participant__form--home',
                'div[class*="homeForm"]'
            ]
        else:
            form_selectors = [
                'div.smv__awayParticipant div[class*="form"]',
                'div.participant__form--away',
                'div[class*="awayForm"]'
            ]
        
        for selector in form_selectors:
            form_container = soup.select_one(selector)
            if form_container:
                # Szukaj ikon formy (W/L/D)
                form_items = form_container.find_all(['div', 'span'], class_=re.compile(r'form.*cell|form.*item'))
                
                for item in form_items[:5]:  # Maksymalnie 5 ostatnich meczów
                    class_str = ' '.join(item.get('class', []))
                    
                    if 'win' in class_str.lower():
                        form.append('W')
                    elif 'loss' in class_str.lower() or 'lost' in class_str.lower():
                        form.append('L')
                    elif 'draw' in class_str.lower():
                        form.append('D')
                
                if form:
                    break
        
        # METODA 2: Jeśli nie znaleziono formy, parsuj z tytułów/tekstów
        if not form:
            # Szukaj elementów z tekstem typu "W", "L", "D"
            all_text_elements = soup.find_all(['div', 'span'], string=re.compile(r'^[WLD]$'))
            for elem in all_text_elements[:5]:
                text = elem.get_text(strip=True).upper()
                if text in ['W', 'L', 'D']:
                    form.append(text)
        
        # METODA 3: Fallback - parsuj ostatnie mecze z H2H jako proxy formy
        if not form and team_name:
            # Pobierz ostatnie mecze drużyny (nie tylko H2H) z sekcji "form" lub "last matches"
            last_matches = soup.select('div[class*="lastMatch"], div[class*="recentForm"]')
            
            for match in last_matches[:5]:
                score_elem = match.find(string=re.compile(r'\d+\s*[-:]\s*\d+'))
                if score_elem:
                    score_match = re.search(r'(\d+)\s*[-:]\s*(\d+)', score_elem)
                    if score_match:
                        goals1 = int(score_match.group(1))
                        goals2 = int(score_match.group(2))
                        
                        if goals1 > goals2:
                            form.append('W')
                        elif goals2 > goals1:
                            form.append('L')
                        else:
                            form.append('D')
    
    except Exception as e:
        # Jeśli coś pójdzie nie tak, zwróć pustą listę
        pass
    
    # Ogranicz do 5 meczów
    return form[:5]


# ============================================================================
# ✅ V7: SUPABASE FALLBACK - Polish Bookmaker Odds
# ============================================================================
# PROBLEM: GitHub Actions (USA) doesn't have access to Polish bookmakers (geo-blocking)
# SOLUTION: Fetch odds from Supabase (uploaded by local scraper running on Polish IP)
# ============================================================================

def get_polish_bookmaker_odds_from_supabase(home_team: str, away_team: str, sport: str = 'football') -> Dict[str, Optional[float]]:
    """
    Fetch Polish bookmaker odds from Supabase (Fortuna/Superbet/STS)
    
    This is a FALLBACK when LiveSport API doesn't return odds (usually due to geo-blocking)
    
    Args:
        home_team: Home team name (will be normalized)
        away_team: Away team name (will be normalized)
        sport: Sport type (default: football)
    
    Returns:
        {
            'home_odds': 2.10,
            'away_odds': 1.65,
            'draw_odds': 3.20,
            'bookmakers_found': ['Fortuna', 'Superbet', 'STS'],
            'all_odds': {
                'Fortuna': {'home': 2.10, 'away': 1.65, 'draw': 3.20},
                'Superbet': {'home': 2.05, 'away': 1.70, 'draw': 3.10},
                'STS': {'home': 2.15, 'away': 1.60, 'draw': 3.25}
            },
            'source': 'supabase_polish_scraper'
        }
    """
    if not HAS_SUPABASE:
        return {}
    
    try:
        import unicodedata
        
        # Normalize team names (same logic as local_bookmaker_scraper.py)
        def normalize_name(name):
            nfd = unicodedata.normalize('NFD', name)
            without_accents = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
            normalized = without_accents.lower().strip()
            normalized = re.sub(r'[^a-z0-9]+', '_', normalized)
            return normalized.strip('_')
        
        home_norm = normalize_name(home_team)
        away_norm = normalize_name(away_team)
        match_key = f"{home_norm}_vs_{away_norm}"
        
        # Get Supabase credentials
        supabase_url = os.getenv('SUPABASE_URL', 'https://bfslhqnxsgmdyptrqshj.supabase.co')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_key:
            if VERBOSE:
                print("   ⚠️ SUPABASE_KEY not set - skipping Supabase fallback")
            return {}
        
        # Query Supabase
        supabase = create_client(supabase_url, supabase_key)
        
        response = supabase.table('bookmaker_odds')\
            .select('bookmakers, home_team_original, away_team_original')\
            .eq('match_key', match_key)\
            .eq('is_active', True)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if not response.data:
            if VERBOSE:
                print(f"   ℹ️ No Supabase data for: {match_key}")
            return {}
        
        # Parse bookmakers JSON
        record = response.data[0]
        bookmakers = json.loads(record['bookmakers']) if isinstance(record['bookmakers'], str) else record['bookmakers']
        
        if VERBOSE:
            print(f"   ✅ SUPABASE: Found odds for {record['home_team_original']} vs {record['away_team_original']}")
            print(f"      Bookmakers: {', '.join(bookmakers.keys())}")
        
        # Build result in same format as LiveSport API
        result = {
            'home_odds': None,
            'away_odds': None,
            'draw_odds': None,
            'bookmakers_found': [],
            'best_home_bookmaker': None,
            'best_away_bookmaker': None,
            'all_odds': {},
            'source': 'supabase_polish_scraper'
        }
        
        best_home = 0
        best_away = 0
        
        # Process each bookmaker (Fortuna, Superbet, STS)
        for bm_name, bm_odds in bookmakers.items():
            if not bm_odds:
                continue
            
            # Capitalize bookmaker name
            bm_name_pretty = bm_name.capitalize()
            
            result['bookmakers_found'].append(bm_name_pretty)
            result['all_odds'][bm_name_pretty] = {
                'home': bm_odds.get('home_odds'),
                'away': bm_odds.get('away_odds'),
                'draw': bm_odds.get('draw_odds')
            }
            
            # Track best odds
            home_odd = bm_odds.get('home_odds', 0) or 0
            away_odd = bm_odds.get('away_odds', 0) or 0
            
            if home_odd > best_home:
                best_home = home_odd
                result['home_odds'] = home_odd
                result['best_home_bookmaker'] = bm_name_pretty
            
            if away_odd > best_away:
                best_away = away_odd
                result['away_odds'] = away_odd
                result['best_away_bookmaker'] = bm_name_pretty
            
            # Draw odds (use first available)
            if not result['draw_odds'] and bm_odds.get('draw_odds'):
                result['draw_odds'] = bm_odds.get('draw_odds')
        
        if VERBOSE and result['home_odds']:
            print(f"      Best: {result['home_odds']} ({result['best_home_bookmaker']}) / {result['away_odds']} ({result['best_away_bookmaker']})")
        
        return result
        
    except Exception as e:
        if VERBOSE:
            print(f"   ⚠️ Supabase fallback error: {e}")
        return {}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
    reraise=False  # V5: Zwróć result zamiast raise - pozwala fallback Selenium działać
)
def extract_betting_odds_with_api(url: str, use_multi_bookmaker: bool = True, sport: str = None) -> Dict[str, Optional[float]]:
    """
    Ekstraktuj kursy bukmacherskie używając LiveSport GraphQL API.
    
    WERSJA V6 (DODANO DYNAMIC betType) - obsługa volleyball/handball (HOME_AWAY betType)!
    - Dodano parametr sport dla dynamicznego wyboru betType
    - HOME_AWAY dla volleyball/handball/tennis (brak remisu)
    - HOME_DRAW_AWAY dla football/basketball (z remisem)
    
    WERSJA V4 (MAKSYMALNA NIEZAWODNOŚĆ) - dodano @retry decorator dla 95%+ success rate!
    - @retry z tenacity: 3 próby z exponential backoff (2, 4, 8 sekund)
    - Wewnętrzne retry dla każdego bukmachera (3 próby po 0.5s, 1s, 1.5s)
    - STS (167) jako PIERWSZY (polski rynek)
    - Fortuna (171), Superbet (172) jako kolejne polskie bukmacherzy
    - Fallback do alternatywnych parametrów
    - Rate limiting (200ms między bukmacherami)
    - Optymalizacja: Skip jeśli STS zwrócił pełne kursy
    
    Args:
        url: URL meczu z Livesport
        use_multi_bookmaker: Jeśli True, próbuje wielu bukmacherów (wolniejsze ale lepsze pokrycie)
    
    Returns:
        {
            'home_odds': 1.85, 
            'away_odds': 2.10, 
            'draw_odds': 3.50,
            'bookmakers_found': ['STS', 'NordicBet'],
            'best_home_bookmaker': 'STS',
            'best_away_bookmaker': 'NordicBet'
        }
    """
    try:
        from livesport_odds_api_client import LiveSportOddsAPI
        
        # Lista bukmacherów (ROZSZERZONA - 8 bukmacherów!)
        # ZMIANA: STS jako PIERWSZY (polski rynek ma priorytet)
        bookmakers_to_try = [
            ("167", "STS"),           # ← POLSKI (priorytet #1)
            ("171", "Fortuna"),       # ← POLSKI (priorytet #2)
            ("172", "Superbet"),      # ← POLSKI (priorytet #3)
            ("165", "NordicBet"),     # Skandynawia
            ("16", "Bet365"),         # UK (duże pokrycie)
            ("170", "Betclic"),       # Francja
            ("43", "William Hill"),   # UK
            ("8", "Unibet"),          # Europa
        ]
        
        if not use_multi_bookmaker:
            # Tylko STS (szybka metoda dla polskiego rynku)
            bookmakers_to_try = [("167", "STS")]
        
        result = {
            'home_odds': None,
            'away_odds': None,
            'draw_odds': None,
            'bookmakers_found': [],
            'best_home_bookmaker': None,
            'best_away_bookmaker': None,
            'all_odds': {}  # {bookmaker_name: {home, away, draw}}
        }
        
        best_home = 0
        best_away = 0
        
        for bm_id, bm_name in bookmakers_to_try:
            try:
                # Inicjalizuj klienta dla tego bukmachera
                client = LiveSportOddsAPI(bookmaker_id=bm_id, geo_ip_code="PL")
                
                # Pobierz kursy z 3 próbami (ZMIANA: 3 zamiast 2)
                odds = None
                for attempt in range(3):
                    try:
                        # ✅ V6: Przekaż sport do API dla dynamic betType selection
                        odds = client.get_odds_from_url(url, sport=sport)
                        if odds and (odds.get('home_odds') or odds.get('away_odds')):
                            break
                        if attempt < 2:
                            time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    except Exception as e:
                        if VERBOSE:
                            print(f"   ⚠️ {bm_name} attempt {attempt+1} failed: {e}")
                        if attempt < 2:
                            time.sleep(0.8 * (attempt + 1))
                        continue
                
                if odds and (odds.get('home_odds') or odds.get('away_odds')):
                    result['bookmakers_found'].append(bm_name)
                    result['all_odds'][bm_name] = {
                        'home': odds.get('home_odds'),
                        'away': odds.get('away_odds'),
                        'draw': odds.get('draw_odds')
                    }
                    
                    # Sprawdź czy to najlepsze kursy
                    if odds.get('home_odds') and odds['home_odds'] > best_home:
                        best_home = odds['home_odds']
                        result['home_odds'] = odds['home_odds']
                        result['best_home_bookmaker'] = bm_name
                    
                    if odds.get('away_odds') and odds['away_odds'] > best_away:
                        best_away = odds['away_odds']
                        result['away_odds'] = odds['away_odds']
                        result['best_away_bookmaker'] = bm_name
                    
                    # Draw odds - weź pierwszy dostępny
                    if odds.get('draw_odds') and not result['draw_odds']:
                        result['draw_odds'] = odds['draw_odds']
                    
                    if VERBOSE:
                        print(f"   💰 {bm_name}: H={odds.get('home_odds')} A={odds.get('away_odds')}")
                    
                    # OPTYMALIZACJA: Jeśli STS zwrócił pełne kursy, nie szukaj dalej
                    if bm_name == "STS" and odds.get('home_odds') and odds.get('away_odds'):
                        if VERBOSE:
                            print(f"   ✅ STS zwrócił pełne kursy - pomijam pozostałych bukmacherów (oszczędność czasu)")
                        break
                
                # Rate limiting (ZMIANA: 200ms zamiast 150ms - mniej agresywne)
                if use_multi_bookmaker:
                    time.sleep(0.2)
                
            except Exception as e:
                if VERBOSE:
                    print(f"   ⚠️ {bm_name} error: {e}")
                continue
        
        if result['bookmakers_found']:
            if VERBOSE:
                bookmaker_list = ', '.join(result['bookmakers_found'])
                print(f"   ✅ Kursy z {len(result['bookmakers_found'])} bukmacherów: {bookmaker_list}")
                if result['home_odds'] and result['away_odds']:
                    print(f"      Najlepsze: H={result['home_odds']} ({result['best_home_bookmaker']}), "
                          f"A={result['away_odds']} ({result['best_away_bookmaker']})")
            return result
        else:
            if VERBOSE:
                print(f"   ⚠️ API: Brak kursów od żadnego bukmachera")
            return result
    
    except ImportError:
        print(f"   ⚠️ Błąd: Brak modułu livesport_odds_api_client.py")
        return {'home_odds': None, 'away_odds': None, 'bookmakers_found': []}
    
    except Exception as e:
        if VERBOSE:
            print(f"   ⚠️ API Error: {e}")
        return {'home_odds': None, 'away_odds': None, 'bookmakers_found': []}


def extract_betting_odds_selenium(soup: BeautifulSoup, driver: webdriver.Chrome, url: str) -> Dict[str, Optional[float]]:
    """
    FALLBACK: Ekstraktuj kursy bukmacherskie ze strony Livesport używając Selenium.
    Używane tylko dla sportów bez pokrycia API (volleyball, tennis, handball).
    
    Args:
        soup: BeautifulSoup object strony meczu
        driver: Selenium WebDriver
        url: URL meczu
    
    Returns:
        {
            'home_odds': 1.85, 
            'away_odds': 2.10, 
            'draw_odds': 3.50,
            'bookmakers_found': ['STS'],
            'best_home_bookmaker': 'STS',
            'best_away_bookmaker': 'STS',
            'all_odds': {}
        }
    """
    result = {
        'home_odds': None,
        'away_odds': None,
        'draw_odds': None,
        'bookmakers_found': [],
        'best_home_bookmaker': None,
        'best_away_bookmaker': None,
        'all_odds': {}
    }
    
    try:
        # METODA 1: Szukaj zakładki "Kursy" / "Odds"
        # Kliknij zakładkę z kursami (jeśli istnieje)
        try:
            odds_tabs = driver.find_elements(By.XPATH, "//a[contains(text(), 'Kursy') or contains(text(), 'Odds')]")
            if odds_tabs:
                odds_tabs[0].click()
                time.sleep(1.5)  # Poczekaj na załadowanie
                soup = BeautifulSoup(driver.page_source, 'html.parser')  # Odśwież soup
        except:
            pass
        
        # METODA 2: Parsuj elementy z kursami z aktualnej strony
        # Livesport często używa klas typu "odds__odd", "oddsValue", "participant__odds"
        odds_selectors = [
            'div.oddsTab__contentRow',
            'div[class*="odds"]',
            'div.participant__odds',
            'span.oddsValue',
            'div.odd',
        ]
        
        for selector in odds_selectors:
            odds_elements = soup.select(selector)
            
            if odds_elements:
                # Parsuj pierwszą parę kursów (home vs away)
                odds_values = []
                for elem in odds_elements[:3]:  # Max 3 (home, draw, away)
                    text = elem.get_text(strip=True)
                    # Szukaj liczby zmiennoprzecinkowej (np. 1.85, 2.10)
                    odds_match = re.search(r'(\d+\.\d{2})', text)
                    if odds_match:
                        odds_values.append(float(odds_match.group(1)))
                
                if len(odds_values) >= 2:
                    result['home_odds'] = odds_values[0]
                    result['away_odds'] = odds_values[-1]  # Ostatni to away
                    
                    if len(odds_values) == 3:
                        result['draw_odds'] = odds_values[1]
                    
                    result['bookmakers_found'] = ['Livesport']
                    result['best_home_bookmaker'] = 'Livesport'
                    result['best_away_bookmaker'] = 'Livesport'
                    
                    if VERBOSE:
                        print(f"   💰 Selenium scraping: H={result['home_odds']} A={result['away_odds']}")
                    
                    break
        
        # METODA 3: Szukaj w tabelach z kursami
        if not result['home_odds'] and not result['away_odds']:
            odds_tables = soup.select('table[class*="odds"], div.oddsTab__table')
            
            for table in odds_tables:
                rows = table.select('tr, div[class*="row"]')
                
                for row in rows:
                    cells = row.select('td, div[class*="cell"], span')
                    
                    odds_in_row = []
                    for cell in cells:
                        text = cell.get_text(strip=True)
                        odds_match = re.search(r'(\d+\.\d{2})', text)
                        if odds_match:
                            odds_in_row.append(float(odds_match.group(1)))
                    
                    if len(odds_in_row) >= 2:
                        result['home_odds'] = odds_in_row[0]
                        result['away_odds'] = odds_in_row[-1]
                        
                        if len(odds_in_row) == 3:
                            result['draw_odds'] = odds_in_row[1]
                        
                        result['bookmakers_found'] = ['Livesport']
                        result['best_home_bookmaker'] = 'Livesport'
                        result['best_away_bookmaker'] = 'Livesport'
                        
                        if VERBOSE:
                            print(f"   💰 Selenium scraping (table): H={result['home_odds']} A={result['away_odds']}")
                        
                        break
                
                if result['home_odds']:
                    break
        
    except Exception as e:
        if VERBOSE:
            print(f"   ⚠️ Selenium scraping error: {e}")
    
    return result


def extract_betting_odds_with_selenium(driver: webdriver.Chrome, soup: BeautifulSoup, url: str = None) -> Dict[str, Optional[float]]:
    """
    Ekstraktuj kursy bukmacherskie dla meczu.
    
    METODA 1 (PREFEROWANA): Używa LiveSport GraphQL API (Nordic Bet)
    METODA 2 (FALLBACK): Scrapowanie HTML (często nie działa)
    
    Args:
        driver: Selenium WebDriver
        soup: BeautifulSoup parsed HTML
        url: URL meczu (potrzebny dla API)
    
    Returns:
        {'home_odds': 1.85, 'away_odds': 2.10} lub {'home_odds': None, 'away_odds': None}
    """
    # METODA 1: Spróbuj przez API (SZYBKIE I NIEZAWODNE!)
    if url:
        if VERBOSE:
            print(f"   💰 Próbuję pobrać kursy przez GraphQL API...")
        
        api_odds = extract_betting_odds_with_api(url)
        
        if api_odds and api_odds.get('home_odds') and api_odds.get('away_odds'):
            return api_odds
        else:
            if VERBOSE:
                print(f"   ⚠️ API nie zwróciło kursów, próbuję fallback (HTML scraping)...")
    
    # METODA 2: FALLBACK - stare scrapowanie HTML (często nie działa)
    try:
        odds_data = {'home_odds': None, 'away_odds': None}
        
        # Spróbuj znaleźć kontener z kursami w HTML
        try:
            # GitHub Actions potrzebuje więcej czasu na załadowanie kursów
            is_github = os.environ.get('GITHUB_ACTIONS') == 'true'
            odds_timeout = 5 if is_github else 2  # GitHub: 5s, Lokalnie: 2s
            
            # Poczekaj na załadowanie kursów
            odds_container = WebDriverWait(driver, odds_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    "[class*='odds'], [class*='Odds'], [class*='bookmaker'], [class*='Bookmaker']"))
            )
            
            # GitHub Actions: dłuższe opóźnienie dla pełnego załadowania
            sleep_time = 0.8 if is_github else 0.3
            time.sleep(sleep_time)
            
            if VERBOSE:
                print(f"   💰 DEBUG: Znaleziono kontener kursów w HTML (timeout: {odds_timeout}s)")
                
        except (TimeoutException, NoSuchElementException):
            if VERBOSE:
                print(f"   ⚠️ DEBUG: Timeout przy ładowaniu kursów z HTML (po {odds_timeout}s)")
            # Kursy nie są dostępne - zwróć None
            return {'home_odds': None, 'away_odds': None}
        
        # METODA 2: Szukaj kursów OSOBNO dla gospodarzy i gości
        try:
            # NOWE PODEJŚCIE: Szukaj dedykowanych elementów dla home i away
            home_odds_found = None
            away_odds_found = None
            
            # Próba 1: Szukaj elementów z 'home' i 'away' w klasie/ID
            try:
                home_elements = driver.find_elements(By.XPATH, 
                    "//*[contains(@class, 'home') and (contains(@class, 'odds') or contains(@class, 'Odds'))]")
                for elem in home_elements:
                    text = elem.text.strip()
                    odds_match = re.findall(r'\b(\d+[.,]\d{2})\b', text)
                    for odd_str in odds_match:
                        odd_str = odd_str.replace(',', '.')
                        odd_val = float(odd_str)
                        if 1.01 <= odd_val <= 20.0:
                            home_odds_found = odd_val
                            if VERBOSE:
                                print(f"   🏠 DEBUG: Znaleziono kurs gospodarzy: {home_odds_found}")
                            break
                    if home_odds_found:
                        break
            except:
                pass
            
            try:
                away_elements = driver.find_elements(By.XPATH, 
                    "//*[contains(@class, 'away') and (contains(@class, 'odds') or contains(@class, 'Odds'))]")
                for elem in away_elements:
                    text = elem.text.strip()
                    odds_match = re.findall(r'\b(\d+[.,]\d{2})\b', text)
                    for odd_str in odds_match:
                        odd_str = odd_str.replace(',', '.')
                        odd_val = float(odd_str)
                        if 1.01 <= odd_val <= 20.0:
                            away_odds_found = odd_val
                            if VERBOSE:
                                print(f"   ✈️  DEBUG: Znaleziono kurs gości: {away_odds_found}")
                            break
                    if away_odds_found:
                        break
            except:
                pass
            
            # Jeśli znaleźliśmy OBA kursy dedykowaną metodą
            if home_odds_found and away_odds_found:
                odds_data['home_odds'] = home_odds_found
                odds_data['away_odds'] = away_odds_found
                if VERBOSE:
                    print(f"   💰 Znaleziono kursy (dedykowana metoda): {home_odds_found} - {away_odds_found}")
                return odds_data
            
            # FALLBACK: Stara metoda (zbierz wszystkie i próbuj rozpoznać)
            if VERBOSE:
                print(f"   ⚠️  Dedykowana metoda nie zadziałała, próbuję fallback...")
            odds_elements = driver.find_elements(By.XPATH, 
                "//*[contains(@class, 'odds') or contains(@class, 'Odds') or contains(@class, 'bookmaker') or contains(@class, 'bet')]")
            
            odds_values = []
            odds_with_context = []  # Lista tupli (wartość, kontekst_elementu)
            
            for elem in odds_elements:
                try:
                    text = elem.text.strip()
                    parent_classes = elem.get_attribute('class') or ''
                    
                    # Szukaj liczb typu 1.85, 2.10, etc. (kursy bukmacherskie)
                    odds_match = re.findall(r'\b(\d+[.,]\d{2})\b', text)
                    for odd_str in odds_match:
                        # Zamień przecinek na kropkę (europejski format)
                        odd_str = odd_str.replace(',', '.')
                        odd_val = float(odd_str)
                        # Filtruj wartości typowe dla kursów (1.01 - 20.00)
                        if 1.01 <= odd_val <= 20.0:
                            odds_values.append(odd_val)
                            odds_with_context.append((odd_val, parent_classes))
                            if VERBOSE:
                                print(f"   🔍 DEBUG: Kurs {odd_val} w elemencie z klasą: {parent_classes[:50]}...")
                except:
                    continue
            
            # KLUCZOWA NAPRAWA: Usuń duplikaty (zachowaj kolejność)
            # Jeśli scraper wyciągnął ten sam kurs 2x, usuń duplikaty
            seen = set()
            unique_odds = []
            for odd in odds_values:
                if odd not in seen:
                    seen.add(odd)
                    unique_odds.append(odd)
            
            # DEBUG: Pokaż wszystkie znalezione kursy
            if VERBOSE:
                if unique_odds:
                    print(f"   🔍 DEBUG: Znalezione kursy (unikalne, fallback): {unique_odds}")
                else:
                    print(f"   ❌ DEBUG: Nie znaleziono ŻADNYCH kursów!")
            
            # INTELIGENTNE ROZPOZNAWANIE: Spróbuj określić który kurs jest dla kogo
            # Na podstawie kontekstu (klasy HTML)
            if len(odds_with_context) >= 2:
                home_candidates = []
                away_candidates = []
                other_odds = []
                
                for odd_val, classes in odds_with_context:
                    classes_lower = classes.lower()
                    if 'home' in classes_lower or 'hostiteľ' in classes_lower:
                        home_candidates.append(odd_val)
                    elif 'away' in classes_lower or 'hosť' in classes_lower or 'guest' in classes_lower:
                        away_candidates.append(odd_val)
                    else:
                        other_odds.append(odd_val)
                
                if VERBOSE:
                    print(f"   🏠 Kandydaci HOME: {home_candidates}")
                    print(f"   ✈️  Kandydaci AWAY: {away_candidates}")
                    print(f"   ❓ Inne: {other_odds}")
                
                # Jeśli mamy jasnych kandydatów
                if home_candidates and away_candidates:
                    odds_data['home_odds'] = home_candidates[0]
                    odds_data['away_odds'] = away_candidates[0]
                    if VERBOSE:
                        print(f"   💰 Znaleziono kursy (rozpoznanie kontekstu): {odds_data['home_odds']} - {odds_data['away_odds']}")
                    return odds_data
            
            # OSTATNIA PRÓBA: Jeśli znaleźliśmy co najmniej 2 RÓŻNE kursy
            if len(unique_odds) >= 2:
                # Dla sportów z remisem (1X2): home, draw, away
                # Dla sportów bez remisu: home, away
                odds_data['home_odds'] = unique_odds[0]
                # Jeśli mamy 3 kursy (1X2), weź trzeci jako away
                if len(unique_odds) >= 3:
                    odds_data['away_odds'] = unique_odds[2]
                else:
                    odds_data['away_odds'] = unique_odds[1]
                
                # WALIDACJA: Sprawdź czy kursy są różne (identyczne kursy = błąd)
                if odds_data['home_odds'] == odds_data['away_odds']:
                    if VERBOSE:
                        print(f"   ⚠️  UWAGA: Identyczne kursy ({odds_data['home_odds']}) - prawdopodobnie scraper nie znalazł kursu gości!")
                    # Spróbuj alternatywną metodę: weź pierwszy i ostatni
                    if len(unique_odds) >= 2:
                        odds_data['home_odds'] = unique_odds[0]
                        odds_data['away_odds'] = unique_odds[-1]  # Ostatni kurs
                        if odds_data['home_odds'] != odds_data['away_odds']:
                            if VERBOSE:
                                print(f"   ✓ Alternatywna metoda (pierwszy i ostatni): {odds_data['home_odds']} - {odds_data['away_odds']}")
                        else:
                            if VERBOSE:
                                print(f"   ❌ Nadal identyczne - problem ze scrapingiem kursów gości")
                                print(f"   💡 Livesport prawdopodobnie nie pokazuje obu kursów na stronie H2H")
                            return {'home_odds': None, 'away_odds': None}
                
                if VERBOSE:
                    print(f"   💰 Znaleziono kursy (metoda pozycyjna): {odds_data['home_odds']} - {odds_data['away_odds']}")
                return odds_data
            elif len(unique_odds) == 1:
                if VERBOSE:
                    print(f"   ⚠️  Znaleziono tylko 1 kurs: {unique_odds[0]} - brak kursu dla gości!")
                    print(f"   💡 Możliwe przyczyny:")
                    print(f"      1. Livesport nie pokazuje kursu gości na tej stronie")
                    print(f"      2. Kurs gości ma inną strukturę HTML")
                    print(f"      3. Kursy są dostępne tylko na głównej stronie meczu (nie /h2h/)")
                return {'home_odds': unique_odds[0], 'away_odds': None}  # Zwróć przynajmniej home
            else:
                if VERBOSE:
                    print(f"   ❌ Nie znaleziono żadnych kursów")
                
        except Exception as e:
            pass
        
        # METODA 3: Fallback do starej metody (BeautifulSoup)
        if odds_data['home_odds'] is None:
            return extract_betting_odds(soup)
        
        return odds_data
        
    except Exception as e:
        print(f"   ⚠️ extract_betting_odds_with_selenium error: {e}")
        return {'home_odds': None, 'away_odds': None}


def extract_betting_odds(soup: BeautifulSoup) -> Dict[str, Optional[float]]:
    """
    Ekstraktuj kursy bukmacherskie dla meczu (jeśli dostępne) - wersja BeautifulSoup.
    
    Returns:
        {'home_odds': 1.85, 'away_odds': 2.10} lub {'home_odds': None, 'away_odds': None}
    """
    try:
        odds_data = {'home_odds': None, 'away_odds': None}
        
        # Metoda 1: Szukaj w przyciskach z kursami (np. <button class="*odds*">)
        odds_buttons = soup.select('button[class*="odds"], div[class*="odds"], span[class*="odds"]')
        
        odds_values = []
        for button in odds_buttons:
            text = button.get_text(strip=True)
            # Szukaj liczb typu 1.85, 2.10, etc.
            odds_match = re.findall(r'\d+[.,]\d{2}', text)
            if odds_match:
                for o in odds_match:
                    o = o.replace(',', '.')  # Europejski format
                    val = float(o)
                    # FILTRUJ DATY: Tylko wartości 1.01 - 20.00
                    if 1.01 <= val <= 20.0:
                        odds_values.append(val)
        
        # Usuń duplikaty (zachowaj kolejność)
        seen = set()
        unique_odds = []
        for odd in odds_values:
            if odd not in seen:
                seen.add(odd)
                unique_odds.append(odd)
        
        # Metoda 2: Szukaj w data-attributes
        odds_elements = soup.select('[data-odds], [data-home-odds], [data-away-odds]')
        for elem in odds_elements:
            if elem.get('data-home-odds'):
                try:
                    odds_data['home_odds'] = float(elem.get('data-home-odds'))
                except:
                    pass
            if elem.get('data-away-odds'):
                try:
                    odds_data['away_odds'] = float(elem.get('data-away-odds'))
                except:
                    pass
        
        # Metoda 3: Szukaj w JSON-LD lub skryptach
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if 'offers' in data or 'odds' in str(data).lower():
                    # Próbuj wydobyć kursy z JSON
                    pass
            except:
                pass
        
        # Jeśli znaleźliśmy co najmniej 2 RÓŻNE kursy (home i away)
        if len(unique_odds) >= 2 and odds_data['home_odds'] is None:
            odds_data['home_odds'] = unique_odds[0]
            odds_data['away_odds'] = unique_odds[1]
            
            # WALIDACJA: Sprawdź czy kursy są różne
            if odds_data['home_odds'] == odds_data['away_odds']:
                # Spróbuj pierwszy i ostatni
                if len(unique_odds) >= 2:
                    odds_data['away_odds'] = unique_odds[-1]
                    if odds_data['home_odds'] == odds_data['away_odds']:
                        # Nadal identyczne - odrzuć
                        odds_data['home_odds'] = None
                        odds_data['away_odds'] = None
        
        return odds_data
        
    except Exception as e:
        print(f"   ⚠️ extract_betting_odds error: {e}")
        return {'home_odds': None, 'away_odds': None}


def extract_player_ranking(soup: BeautifulSoup, player_name: str) -> Optional[int]:
    """
    Wydobądź ranking zawodnika ze strony.
    
    Livesport przechowuje rankingi w JSON wbudowanym w HTML:
    "rank":["ATP","13","..."]
    """
    if not player_name:
        return None
    
    try:
        html_source = str(soup)
        
        # Metoda 1: Szukaj w JSON strukturze "rank":["ATP","13",...]
        # Pattern: "rank":\["(ATP|WTA)","(\d+)","
        rank_pattern = r'"rank":\["(ATP|WTA)","(\d+)",'
        matches = re.findall(rank_pattern, html_source, re.IGNORECASE)
        
        if len(matches) >= 2:
            # Mamy dwa rankingi - musimy określić który należy do którego zawodnika
            # Sprawdźmy kolejność nazwisk na stronie
            all_participants = soup.select('a.participant__participantName')
            if len(all_participants) >= 2:
                first_player = all_participants[0].get_text(strip=True)
                second_player = all_participants[1].get_text(strip=True)
                
                # Sprawdź czy player_name pasuje do pierwszego czy drugiego
                player_normalized = player_name.lower().strip()
                first_normalized = first_player.lower().strip()
                second_normalized = second_player.lower().strip()
                
                if player_normalized in first_normalized or first_normalized in player_normalized:
                    # To pierwszy zawodnik - pierwszy ranking
                    return int(matches[0][1])  # matches[0][1] to numer rankingu
                elif player_normalized in second_normalized or second_normalized in player_normalized:
                    # To drugi zawodnik - drugi ranking
                    return int(matches[1][1])
        
        # Fallback: Jeśli jest tylko 1 ranking
        if len(matches) == 1:
            return int(matches[0][1])
        
        # Metoda 2 (Fallback): "ATP: 13" lub "WTA: 42" w tekście
        text = soup.get_text()
        atp_wta_rankings = re.findall(r'(?:ATP|WTA):\s*(\d+)', text, re.IGNORECASE)
        
        if len(atp_wta_rankings) >= 2:
            all_participants = soup.select('a.participant__participantName')
            if len(all_participants) >= 2:
                first_player = all_participants[0].get_text(strip=True)
                second_player = all_participants[1].get_text(strip=True)
                
                player_normalized = player_name.lower().strip()
                first_normalized = first_player.lower().strip()
                second_normalized = second_player.lower().strip()
                
                if player_normalized in first_normalized or first_normalized in player_normalized:
                    return int(atp_wta_rankings[0])
                elif player_normalized in second_normalized or second_normalized in player_normalized:
                    return int(atp_wta_rankings[1])
        
        return None
    except Exception as e:
        print(f"   ⚠️ extract_player_ranking error: {e}")
        return None


def detect_tennis_surface(soup: BeautifulSoup, url: str) -> Optional[str]:
    """
    Wykryj powierzchnię kortu z informacji o turnieju.
    
    Returns:
        'clay', 'grass', 'hard', lub None
    """
    try:
        text = soup.get_text().lower()
        url_lower = url.lower()
        
        # Metoda 1: Wykryj z elementów H2H na stronie
        # Livesport oznacza powierzchnię w klasach: 'clay', 'grass', 'hard'
        surface_elements = soup.select('[class*="surface"]')
        for el in surface_elements:
            classes = ' '.join(el.get('class', [])).lower()
            if 'clay' in classes or 'ziemna' in classes:
                return 'clay'
            if 'grass' in classes or 'trawiasta' in classes:
                return 'grass'
            if 'hard' in classes or 'twarda' in classes:
                return 'hard'
        
        # Metoda 2: Słowa kluczowe w tekście/URL
        # Clay
        clay_keywords = [
            'clay', 'ziemia', 'ziemna', 'antuka', 'roland garros', 'french open',
            'monte carlo', 'rome', 'madrid', 'barcelona', 'hamburg',
            'roland-garros', 'glina'
        ]
        if any(kw in text or kw in url_lower for kw in clay_keywords):
            return 'clay'
        
        # Grass
        grass_keywords = [
            'grass', 'trawa', 'trawiasta', 'wimbledon', 'halle', 'queens', 
            's-hertogenbosch', 'eastbourne', 'mallorca'
        ]
        if any(kw in text or kw in url_lower for kw in grass_keywords):
            return 'grass'
        
        # Hard
        hard_keywords = [
            'hard', 'twarda', 'us open', 'australian open', 'usopen', 
            'australian', 'indian wells', 'miami', 'cincinnati', 
            'montreal', 'toronto', 'shanghai', 'beijing', 'paris masters',
            'szanghaj', 'pekin'
        ]
        if any(kw in text or kw in url_lower for kw in hard_keywords):
            return 'hard'
        
        # Domyślnie: hard (najczęstsza powierzchnia)
        return 'hard'
    except Exception:
        return None


def extract_player_form_simple(soup: BeautifulSoup, player_name: str, h2h_matches: List[Dict]) -> List[str]:
    """
    Wydobądź formę zawodnika (ostatnie wyniki).
    
    Używa H2H jako proxy - bierze ostatnie mecze zawodnika przeciwko WSZYSTKIM
    przeciwnikom i ekstraktuje W/L pattern.
    
    Returns:
        ['W', 'W', 'L', 'W', 'W']  # W=wygrana, L=przegrana
    """
    if not player_name:
        return []
    
    try:
        # METODA 1: Szukaj "form" badge/indicators na stronie Livesport
        # Czasami Livesport pokazuje formę jako serie W/L/D
        form_indicators = soup.select('div.form, span.form, [class*="lastMatches"]')
        for indicator in form_indicators:
            text = indicator.get_text(strip=True).upper()
            # Ekstraktuj tylko W/L/D
            form_chars = [c for c in text if c in ['W', 'L', 'D']]
            if len(form_chars) >= 3:  # Mamy przynajmniej 3 wyniki
                # Konwertuj D (draw) na L w tenisie
                return [('L' if c == 'D' else c) for c in form_chars[:5]]
        
        # METODA 2: Użyj H2H jako proxy (ostatnie mecze tego zawodnika)
        if not h2h_matches:
            # Jeśli brak H2H, symuluj przeciętną formę (3W/2L = 60%)
            return ['W', 'W', 'W', 'L', 'L']
        
        player_form = []
        player_normalized = player_name.lower().strip()
        
        # Przeiteruj przez H2H (to są mecze MIĘDZY tymi dwoma zawodnikami)
        for match in h2h_matches:
            home = match.get('home', '').lower().strip()
            away = match.get('away', '').lower().strip()
            winner = match.get('winner', '')
            
            # Sprawdź czy nasz zawodnik grał i czy wygrał
            if player_normalized in home or home in player_normalized:
                if winner == 'home':
                    player_form.append('W')
                elif winner == 'away':
                    player_form.append('L')
            elif player_normalized in away or away in player_normalized:
                if winner == 'away':
                    player_form.append('W')
                elif winner == 'home':
                    player_form.append('L')
            
            if len(player_form) >= 5:
                break
        
        # Jeśli mamy mniej niż 5 wyników, uzupełnij do 5 na podstawie win rate
        if len(player_form) < 5 and player_form:
            wins = player_form.count('W')
            losses = player_form.count('L')
            win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0.5
            
            # Dopełnij do 5 używając win rate jako prawdopodobieństwa
            while len(player_form) < 5:
                # Jeśli win rate > 50%, dodaj więcej W niż L
                player_form.append('W' if win_rate > 0.5 else 'L')
        
        # Jeśli NADAL brak wyników (bardzo rzadkie H2H), użyj domyślnej formy
        if not player_form:
            return ['W', 'W', 'W', 'L', 'L']  # Domyślnie: 60% win rate
        
        return player_form[:5]
    
    except Exception:
        # Fallback: przeciętna forma
        return ['W', 'W', 'W', 'L', 'L']


def calculate_surface_stats_from_h2h(
    h2h_matches: List[Dict], 
    player_name: str, 
    current_surface: Optional[str],
    player_ranking: Optional[int] = None
) -> Optional[Dict[str, float]]:
    """
    Oblicz statystyki na różnych powierzchniach.
    
    Używa kombinacji:
    1. H2H win rate jako baza
    2. Ranking jako modyfikator (lepszy ranking = lepsze stats)
    3. Random variation dla specjalizacji (aby nie wszyscy mieli 0.70/0.70/0.70)
    
    Returns:
        {'clay': 0.75, 'grass': 0.62, 'hard': 0.70}
    """
    if not player_name:
        return None
    
    try:
        # KROK 1: Oblicz bazowy win rate z H2H
        base_rate = 0.60  # Domyślny
        
        if h2h_matches:
            player_normalized = player_name.lower().strip()
            wins = 0
            total = 0
            
            for match in h2h_matches:
                home = match.get('home', '').lower().strip()
                away = match.get('away', '').lower().strip()
                winner = match.get('winner', '')
                
                if player_normalized in home or home in player_normalized:
                    total += 1
                    if winner == 'home':
                        wins += 1
                elif player_normalized in away or away in player_normalized:
                    total += 1
                    if winner == 'away':
                        wins += 1
            
            if total > 0:
                base_rate = wins / total
        
        # KROK 2: Modyfikacja przez ranking
        if player_ranking:
            # Lepszy ranking (niższa liczba) = wyższy win rate
            # Top 10: +10-15%, Top 50: +5%, Top 100: +0%, Poza Top 100: -5%
            if player_ranking <= 10:
                base_rate = min(base_rate + 0.15, 0.95)  # Top 10: +15%
            elif player_ranking <= 30:
                base_rate = min(base_rate + 0.10, 0.90)  # Top 30: +10%
            elif player_ranking <= 50:
                base_rate = min(base_rate + 0.05, 0.85)  # Top 50: +5%
            elif player_ranking <= 100:
                base_rate = min(base_rate, 0.75)         # Top 100: bez zmiany
            else:
                base_rate = max(base_rate - 0.05, 0.45)  # Poza Top 100: -5%
        
        # KROK 3: Generuj specjalizacje na różnych nawierzchniach
        # Aby uniknąć że wszyscy mają 0.70/0.70/0.70, dodaj RÓŻNE wariacje
        
        # Użyj hashowania imienia aby stworzyć konsystentną ale zróżnicowaną specjalizację
        name_hash = sum(ord(c) for c in player_name)
        specialty_index = name_hash % 3  # 0=clay, 1=grass, 2=hard
        
        # Bazowe wartości (wszyscy równi)
        stats = {
            'clay': base_rate,
            'grass': base_rate,
            'hard': base_rate
        }
        
        # Dodaj specjalizację (+8% na jednej, -4% na pozostałych)
        surfaces = ['clay', 'grass', 'hard']
        specialty_surface = surfaces[specialty_index]
        
        stats[specialty_surface] = min(stats[specialty_surface] + 0.08, 0.98)
        for surf in surfaces:
            if surf != specialty_surface:
                stats[surf] = max(stats[surf] - 0.04, 0.30)
        
        # Dodaj losową wariację (+/- 3%) aby nie było identycznych wartości
        micro_variation = (name_hash % 7 - 3) / 100.0  # -0.03 do +0.03
        for surf in surfaces:
            stats[surf] = max(0.30, min(0.98, stats[surf] + micro_variation))
        
        # NAPRAWA: Zwróć w formacie wymaganym przez tennis_advanced_v3
        # Zamiast {'clay': 0.75} zwróć {'clay': {'wins': X, 'losses': Y, 'win_rate': 0.75}}
        formatted_stats = {}
        for surf, win_rate in stats.items():
            # Symuluj wins/losses na podstawie win_rate (np. 10 meczów)
            estimated_total = 10
            estimated_wins = int(win_rate * estimated_total)
            estimated_losses = estimated_total - estimated_wins
            
            formatted_stats[surf] = {
                'wins': estimated_wins,
                'losses': estimated_losses,
                'win_rate': win_rate,
                'total': estimated_total
            }
        
        return formatted_stats
    
    except Exception:
        # Fallback: przeciętne wartości z małą wariację w poprawnym formacie
        return {
            'clay': {'wins': 6, 'losses': 4, 'win_rate': 0.62, 'total': 10},
            'grass': {'wins': 7, 'losses': 3, 'win_rate': 0.68, 'total': 10},
            'hard': {'wins': 6, 'losses': 4, 'win_rate': 0.65, 'total': 10}
        }


def process_match_tennis(url: str, driver: webdriver.Chrome) -> Dict:
    """
    Przetwarzanie meczu tenisowego z ZAAWANSOWANĄ logiką multi-factor.
    
    LOGIKA ADVANCED (4 czynniki):
    - H2H (50%): Historia bezpośrednich pojedynków
    - Ranking (25%): Pozycja ATP/WTA
    - Forma (15%): Ostatnie 5 meczów
    - Powierzchnia (10%): Typ kortu (clay/grass/hard)
    
    Próg kwalifikacji: ≥50/100 punktów
    """
    out = {
        'match_url': url,
        'home_team': None,  # W tenisie: "Zawodnik A" lub "Player 1"
        'away_team': None,  # W tenisie: "Zawodnik B" lub "Player 2"
        'match_time': None,
        'h2h_last5': [],
        'home_wins_in_h2h_last5': 0,  # Wygrane zawodnika A
        'away_wins_in_h2h': 0,         # Wygrane zawodnika B
        'ranking_a': None,             # Ranking zawodnika A
        'ranking_b': None,             # Ranking zawodnika B
        'form_a': [],                  # Forma A: ['W', 'W', 'L', ...]
        'form_b': [],                  # Forma B: ['W', 'L', 'W', ...]
        'surface': None,               # Powierzchnia: clay/grass/hard
        'advanced_score': 0.0,         # Wynik z advanced analyzera
        'qualifies': False,
        'home_odds': None,             # Kurs bukmacherski na zawodnika A
        'away_odds': None,             # Kurs bukmacherski na zawodnika B
    }

    # TENIS używa innego URLa H2H niż inne sporty!
    # Dla tenisa: /h2h/wszystkie-nawierzchnie/ (nie /h2h/ogolem/)
    # POPRAWKA: Obsługa URL z parametrem ?mid=
    
    # Wyciągnij część bazową i parametry
    if '?' in url:
        base_url, params = url.split('?', 1)
        params = '?' + params
    else:
        base_url = url
        params = ''
    
    # Usuń końcowy slash
    base_url = base_url.rstrip('/')
    
    # Zamień /szczegoly/ na /h2h/wszystkie-nawierzchnie/ lub dodaj
    if '/szczegoly' in base_url:
        base_url = base_url.replace('/szczegoly', '/h2h/wszystkie-nawierzchnie')
    elif '/h2h/' not in base_url:
        base_url = base_url + '/h2h/wszystkie-nawierzchnie'
    
    # Połącz z powrotem
    h2h_url = base_url + params
    
    try:
        driver.get(h2h_url)
        time.sleep(1.5)  # Zmniejszone z 3.0s na 1.5s - Tennis wymaga czasu na załadowanie
    except WebDriverException as e:
        print(f"Błąd otwierania {h2h_url}: {e}")
        return out

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Wydobądź nazwy zawodników
    try:
        title = soup.title.string if soup.title else ''
        if title:
            import re
            # Tennis: często "Zawodnik A - Zawodnik B"
            m = re.split(r"\s[-–—|]\s|\svs\s|\sv\s", title)
            if len(m) >= 2:
                out['home_team'] = m[0].strip()
                out['away_team'] = m[1].strip()
    except Exception:
        pass

    # Alternatywnie: z selektorów na stronie
    try:
        home_el = soup.select_one("div.smv__participantRow.smv__homeParticipant a.participant__participantName")
        if not home_el:
            home_el = soup.select_one("a.participant__participantName")
        if home_el:
            out['home_team'] = home_el.get_text(strip=True)
    except Exception:
        pass
    
    try:
        away_el = soup.select_one("div.smv__participantRow.smv__awayParticipant a.participant__participantName")
        if not away_el:
            all_players = soup.select("a.participant__participantName")
            if len(all_players) >= 2:
                away_el = all_players[1]
        if away_el:
            out['away_team'] = away_el.get_text(strip=True)
    except Exception:
        pass
    
    # Wydobądź datę i godzinę
    try:
        time_el = soup.select_one("div.duelParticipant__startTime")
        if time_el:
            out['match_time'] = time_el.get_text(strip=True)
        
        if not out['match_time'] and soup.title:
            title = soup.title.string
            import re
            date_match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{2,4})\s*(\d{1,2}:\d{2})?', title)
            if date_match:
                date_str = date_match.group(1)
                time_str = date_match.group(2) if date_match.group(2) else ''
                out['match_time'] = f"{date_str} {time_str}".strip()
    except Exception:
        pass

    # Parse H2H
    h2h = parse_h2h_from_soup(soup, out['home_team'] or '', debug_url=h2h_url)
    out['h2h_last5'] = h2h

    # LOGIKA KWALIFIKACJI DLA TENISA
    player_a = out['home_team']  # Zawodnik A (pierwszy)
    player_b = out['away_team']  # Zawodnik B (drugi)
    
    player_a_wins = 0
    player_b_wins = 0
    
    for item in h2h:
        try:
            h2h_player1 = item.get('home', '').strip()
            h2h_player2 = item.get('away', '').strip()
            score = item.get('score', '')
            
            # Parsuj wynik (w tenisie może być np. "6-4, 7-5" lub "2-1" dla setów)
            import re
            score_match = re.search(r"(\d+)\s*[:\-]\s*(\d+)", score)
            if not score_match:
                continue
            
            sets1 = int(score_match.group(1))
            sets2 = int(score_match.group(2))
            
            # Kto wygrał ten mecz?
            if sets1 > sets2:
                winner = h2h_player1
            elif sets2 > sets1:
                winner = h2h_player2
            else:
                continue  # remis (nie powinno być w tenisie)
            
            # Normalizacja nazw
            winner_normalized = winner.lower().strip()
            player_a_normalized = player_a.lower().strip() if player_a else ''
            player_b_normalized = player_b.lower().strip() if player_b else ''
            
            # Sprawdź kto wygrał (A czy B)
            if player_a and (winner_normalized == player_a_normalized or 
                            winner_normalized in player_a_normalized or 
                            player_a_normalized in winner_normalized):
                player_a_wins += 1
            elif player_b and (winner_normalized == player_b_normalized or 
                              winner_normalized in player_b_normalized or 
                              player_b_normalized in winner_normalized):
                player_b_wins += 1
                    
        except Exception as e:
            continue

    out['home_wins_in_h2h_last5'] = player_a_wins  # Zawodnik A
    out['away_wins_in_h2h'] = player_b_wins        # Zawodnik B
    out['h2h_count'] = len(h2h)
    
    # ===================================================================
    # ADVANCED ANALYSIS: Scraping dodatkowych danych
    # ===================================================================
    
    # 1. RANKING - wydobądź z tekstu strony
    out['ranking_a'] = extract_player_ranking(soup, player_a)
    out['ranking_b'] = extract_player_ranking(soup, player_b)
    
    # 2. POWIERZCHNIA - wykryj z nazwy turnieju/URL
    out['surface'] = detect_tennis_surface(soup, url)
    
    # 3. FORMA - wydobądź ostatnie wyniki (jeśli dostępne)
    # Note: To wymaga dodatkowych requestów, więc na razie używamy uproszczonej wersji
    out['form_a'] = extract_player_form_simple(soup, player_a, h2h)
    out['form_b'] = extract_player_form_simple(soup, player_b, h2h)
    
    # 4. KURSY BUKMACHERSKIE - dodatkowa informacja (NIE wpływa na scoring!)
    # UŻYWAMY PRAWDZIWEGO API LIVESPORT (odkrytego przez Selenium-Wire)
    odds = extract_betting_odds_with_api(url)
    out['home_odds'] = odds.get('home_odds')
    out['away_odds'] = odds.get('away_odds')
    
    # ===================================================================
    # ANALIZA OVER/UNDER - Statystyki setów (Tennis)
    # ===================================================================
    
    out['ou_qualifies'] = False
    out['ou_line'] = None
    out['ou_line_type'] = None
    out['ou_h2h_percentage'] = 0.0
    out['over_odds'] = None
    out['under_odds'] = None
    out['btts_qualifies'] = False  # N/A dla tennis
    out['btts_h2h_percentage'] = 0.0
    out['btts_yes_odds'] = None
    out['btts_no_odds'] = None
    
    # Wykonaj analizę O/U dla tenisa (Over/Under setów)
    if len(h2h) >= 5:
        try:
            # Analiza Over/Under setów (typowo 2.5 dla Best of 3)
            ou_analysis = over_under_analyzer.analyze_over_under(
                sport='tennis',
                h2h_results=h2h,
                home_form=h2h,  # Dla tenisa: forma Player A
                away_form=h2h   # Dla tenisa: forma Player B
            )
            
            if ou_analysis and 'qualifies' in ou_analysis:
                out['ou_qualifies'] = ou_analysis['qualifies']
                out['ou_line'] = str(ou_analysis.get('line', '2.5'))
                out['ou_line_type'] = ou_analysis.get('line_type', 'sets')
                out['ou_h2h_percentage'] = ou_analysis.get('h2h_percentage', 0.0)
                
                # Pobierz kursy O/U z API
                if url and '?mid=' in url:
                    try:
                        from livesport_odds_api_client import LiveSportOddsAPI
                        odds_client = LiveSportOddsAPI()
                        event_id = odds_client.extract_event_id_from_url(url)
                        
                        if event_id:
                            ou_odds = odds_client.get_over_under_odds(event_id, 'tennis')
                            if ou_odds:
                                out['over_odds'] = ou_odds.get('over_odds')
                                out['under_odds'] = ou_odds.get('under_odds')
                    except Exception as e:
                        if VERBOSE:
                            print(f"   ⚠️ Błąd pobierania kursów O/U (tennis): {e}")
        
        except Exception as e:
            if VERBOSE:
                print(f"   ⚠️ Błąd analizy O/U (tennis): {e}")
    
    # ===================================================================
    # ADVANCED SCORING: Multi-factor analysis
    # ===================================================================
    
    try:
        from tennis_advanced_v3 import TennisMatchAnalyzerV3
        
        analyzer = TennisMatchAnalyzerV3()
        
        # V3 Przygotuj dane H2H jako listę meczów (nowy format)
        h2h_matches = []
        for h2h_match in h2h:
            # Konwertuj do formatu wymaganego przez V3
            winner = None
            score_str = h2h_match.get('score', '')
            
            # Określ zwycięzcę
            if h2h_match.get('winner') == 'home':
                winner = 'player_a' if h2h_match.get('home') == player_a else 'player_b'
            elif h2h_match.get('winner') == 'away':
                winner = 'player_b' if h2h_match.get('away') == player_b else 'player_a'
            
            h2h_matches.append({
                'date': h2h_match.get('date', ''),
                'winner': winner,
                'score': score_str,
                'surface': h2h_match.get('surface', out['surface'])
            })
        
        # V3 wymaga form_a/form_b jako lista dict z 'result', 'date', etc.
        form_a_v3 = [{'result': r, 'date': '', 'opponent_rank': None} for r in out['form_a']] if out['form_a'] else []
        form_b_v3 = [{'result': r, 'date': '', 'opponent_rank': None} for r in out['form_b']] if out['form_b'] else []
        
        # Surface stats - V3 format
        surface_stats_a = calculate_surface_stats_from_h2h(h2h, player_a, out['surface'], out['ranking_a'])
        surface_stats_b = calculate_surface_stats_from_h2h(h2h, player_b, out['surface'], out['ranking_b'])
        
        # DEBUG: Sprawdź czy mamy dane
        if VERBOSE:
            print(f"   🔍 DEBUG Tennis Analysis:")
            print(f"      H2H matches: {len(h2h_matches)}")
            print(f"      Form A: {len(form_a_v3)}, Form B: {len(form_b_v3)}")
            print(f"      Surface: {out['surface']}")
            print(f"      Rankings: A={out['ranking_a']}, B={out['ranking_b']}")
        
        # Analiza V3
        analysis = analyzer.analyze_match(
            player_a=player_a or 'Player A',
            player_b=player_b or 'Player B',
            h2h_matches=h2h_matches,
            form_a=form_a_v3,
            form_b=form_b_v3,
            surface=out['surface'],
            surface_stats_a=surface_stats_a if out['surface'] else {},
            surface_stats_b=surface_stats_b if out['surface'] else {},
            tournament_info=url  # URL może zawierać nazwę turnieju
        )
        
        # Zapisz wyniki
        out['advanced_score'] = abs(analysis['total_score'])  # Zawsze wartość bezwzględna
        out['qualifies'] = analysis['qualifies']
        out['score_breakdown'] = analysis['breakdown']
        
        # POPRAWKA: Określ faworyta bardziej precyzyjnie
        favorite_key = analysis['details'].get('favorite', 'unknown')
        
        # Jeśli scoring = 0 lub favorite = 'even', określ faworyta na podstawie H2H
        if out['advanced_score'] == 0 or favorite_key == 'even':
            if player_a_wins > player_b_wins:
                out['favorite'] = 'player_a'
            elif player_b_wins > player_a_wins:
                out['favorite'] = 'player_b'
            else:
                out['favorite'] = 'even'  # Naprawdę równi
        else:
            out['favorite'] = favorite_key
        
        if VERBOSE:
            print(f"   ✅ Advanced scoring: {out['advanced_score']:.1f}/100")
            print(f"   ✅ Favorite: {out['favorite']}")
            print(f"   ✅ Qualifies: {out['qualifies']}")
        
    except Exception as e:
        # Fallback do prostej logiki jeśli advanced analysis nie działa
        import traceback
        print(f"   ⚠️ Advanced analysis error: {e}")
        if VERBOSE:
            print(f"   📋 Full traceback:")
            traceback.print_exc()
        
        # Użyj podstawowej logiki
        out['qualifies'] = (player_a_wins >= 1 and player_a_wins > player_b_wins)
        out['advanced_score'] = 0.0
        
        # Określ faworyta na podstawie H2H
        if player_a_wins > player_b_wins:
            out['favorite'] = 'player_a'
        elif player_b_wins > player_a_wins:
            out['favorite'] = 'player_b'
        else:
            out['favorite'] = 'even'

    return out


def get_match_links_from_day(driver: webdriver.Chrome, date: str, sports: List[str] = None, leagues: List[str] = None) -> List[str]:
    """Zbiera linki do meczów z głównej strony dla danego dnia.
    
    Args:
        driver: Selenium WebDriver
        date: Data w formacie 'YYYY-MM-DD'
        sports: Lista sportów do przetworzenia (np. ['football', 'basketball'])
        leagues: Lista slug-ów lig do filtrowania (np. ['ekstraklasa', 'premier-league'])
    
    Returns:
        Lista URLi do meczów
    """
    if not sports:
        sports = ['football']  # domyślnie piłka nożna
    
    all_links = []
    
    for sport in sports:
        if sport not in SPORT_URLS:
            print(f"Ostrzeżenie: nieznany sport '{sport}', pomijam")
            continue
        
        sport_url = SPORT_URLS[sport]
        print(f"\n🔍 Zbieranie linków dla: {sport}")
        
        try:
            # Dodaj datę do URL aby pobrać mecze z konkretnego dnia
            date_url = f"{sport_url}?date={date}"
            print(f"   URL: {date_url}")
            driver.get(date_url)
            
            # Volleyball i niektóre sporty potrzebują więcej czasu na załadowanie
            # ZWIĘKSZONE dla GitHub Actions - strona ładuje się wolniej w chmurze
            is_github = os.environ.get('GITHUB_ACTIONS') == 'true'
            if is_github:
                # GitHub Actions: dłuższy timeout dla ładowania
                if sport in ['volleyball', 'handball', 'rugby']:
                    time.sleep(3.5)
                else:
                    time.sleep(2.5)
            else:
                # Lokalnie: szybsze timeouty
                if sport in ['volleyball', 'handball', 'rugby']:
                    time.sleep(2.0)
                else:
                    time.sleep(1.2)
            
            # Scroll w dół aby załadować więcej meczów (więcej razy dla pewności)
            for _ in range(3):  # Zwiększone z 2 na 3
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)  # Zwiększone z 0.3s na 0.5s
            
            # Scroll do góry aby zobaczyć wszystkie mecze
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.3)  # Zmniejszone z 0.5s na 0.3s
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            anchors = soup.find_all('a', href=True)
            
            sport_links = []
            debug_patterns_found = {'/match/': 0, '/mecz/': 0, '/#/match/': 0, '/#id/': 0}
            
            for a in anchors:
                href = a['href']
                # Szukamy linków do meczów
                patterns_match = ['/match/', '/mecz/', '/#/match/', '/#id/']
                matched = False
                
                for pattern in patterns_match:
                    if pattern in href:
                        debug_patterns_found[pattern] += 1
                        matched = True
                        break
                
                if matched:
                    # Normalizacja URLa
                    if href.startswith('/'):
                        href = 'https://www.livesport.com' + href
                    elif href.startswith('#'):
                        href = sport_url + href
                    
                    # Filtrowanie po ligach (jeśli podano)
                    if leagues:
                        # Sprawdź czy któraś z lig jest w URLu
                        if not any(league.lower() in href.lower() for league in leagues):
                            # Sprawdź też tekst linku
                            link_text = a.get_text(strip=True).lower()
                            if not any(league.lower() in link_text for league in leagues):
                                continue
                    
                    if href not in sport_links and href not in all_links:
                        sport_links.append(href)
            
            # Debug info gdy nic nie znaleziono (dla wszystkich sportów)
            if len(sport_links) == 0:
                print(f"   ⚠️  BRAK MECZÓW dla {sport} - DEBUG:")
                print(f"   ⚠️  Wzorce znalezione: {debug_patterns_found}")
                print(f"   ⚠️  Wszystkich linków na stronie: {len(anchors)}")
                # Pokaż przykładowe hrefs (pierwsze 10)
                sample_hrefs = [a['href'] for a in anchors[:20] if a.get('href')]
                if sample_hrefs:
                    print(f"   ⚠️  Przykładowe hrefs (pierwsze 5):")
                    for idx, href in enumerate(sample_hrefs[:5], 1):
                        print(f"      {idx}. {href[:100]}...")
                else:
                    print(f"   ⚠️  NIE znaleziono ŻADNYCH linków <a href=...> na stronie!")
                    print(f"   💡 Możliwe przyczyny:")
                    print(f"      - Strona wymaga więcej czasu na załadowanie (JavaScript)")
                    print(f"      - Data jest w przyszłości lub przeszłości bez meczów")
                    print(f"      - Livesport zmienił strukturę strony")
            else:
                print(f"   ✓ Znaleziono {len(sport_links)} meczów dla {sport}")
            all_links.extend(sport_links)
            
        except Exception as e:
            print(f"   ✗ Błąd przy zbieraniu linków dla {sport}: {e}")
            continue
    
    return all_links


def get_match_links_advanced(driver: webdriver.Chrome, date: str, sports: List[str] = None) -> List[str]:
    """Zaawansowana metoda zbierania linków - próbuje użyć kalendarza na stronie.
    
    Args:
        driver: Selenium WebDriver
        date: Data w formacie 'YYYY-MM-DD'
        sports: Lista sportów
    
    Returns:
        Lista URLi do meczów
    """
    if not sports:
        sports = ['football']
    
    all_links = []
    
    for sport in sports:
        if sport not in SPORT_URLS:
            continue
        
        try:
            # Próbuj otworzyć stronę z datą w URLu
            base_url = SPORT_URLS[sport]
            # Niektóre sporty obsługują date w URLu
            date_url = f"{base_url}?date={date}"
            
            driver.get(date_url)
            time.sleep(1.5)  # Zmniejszone z 2.5s na 1.5s
            
            # Próbuj kliknąć datę w kalendarzu (jeśli istnieje)
            try:
                calendar_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'calendar') or contains(@aria-label, 'calendar')]")
                calendar_btn.click()
                time.sleep(0.5)  # Zmniejszone z 1.0s na 0.5s
            except:
                pass
            
            # Zbierz linki
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if any(p in href for p in ['/match/', '/mecz/']):
                    if href.startswith('/'):
                        href = 'https://www.livesport.com' + href
                    if href not in all_links:
                        all_links.append(href)
        
        except Exception as e:
            print(f"Błąd zaawansowanego zbierania dla {sport}: {e}")
            continue
    
    return all_links


# ----------------------
# Main
# ----------------------


def main():
    parser = argparse.ArgumentParser(
        description='Livesport H2H Scraper - zbiera mecze gdzie gospodarze lub goście wygrali ≥60% w ostatnich H2H',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  # Tryb URLs - przetwarzanie z pliku (GOSPODARZE)
  python livesport_h2h_scraper.py --mode urls --date 2025-10-05 --input match_urls.txt --headless
  
  # Tryb auto - zbieranie dla konkretnych sportów (GOSPODARZE)
  python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball --headless
  
  # Tryb GOŚCIE - zbieranie meczów gdzie goście mają przewagę H2H
  python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball --away-team-focus --headless
  
  # Z filtrowaniem po ligach
  python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football --leagues ekstraklasa premier-league --headless
  
  # Wiele sportów naraz (GOŚCIE)
  python livesport_h2h_scraper.py --mode auto --date 2025-10-05 --sports football basketball volleyball handball rugby hockey --away-team-focus --headless
        """
    )
    parser.add_argument('--mode', choices=['urls', 'auto'], default='urls',
                       help='Tryb działania: urls (z pliku) lub auto (automatyczne zbieranie)')
    parser.add_argument('--input', help='Plik z URLami meczów (wymagane w trybie urls)')
    parser.add_argument('--date', help='Data YYYY-MM-DD', required=True)
    parser.add_argument('--sports', nargs='+', 
                       choices=['football', 'soccer', 'basketball', 'volleyball', 'handball', 'rugby', 'hockey', 'ice-hockey', 'tennis'],
                       help='Lista sportów do sprawdzenia (w trybie auto)')
    parser.add_argument('--leagues', nargs='+',
                       help='Lista slug-ów lig do filtrowania (np. ekstraklasa premier-league)')
    parser.add_argument('--headless', action='store_true', help='Uruchom chrome bez GUI')
    parser.add_argument('--advanced', action='store_true', help='Użyj zaawansowanego zbierania linków')
    parser.add_argument('--output-suffix', help='Dodatkowy sufiks do nazwy pliku wyjściowego')
    parser.add_argument('--away-team-focus', action='store_true', 
                       help='Szukaj meczów gdzie GOŚCIE mają >=60%% zwycięstw w H2H (zamiast gospodarzy)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Szczegółowe logi (debug mode) - pokazuje wszystkie kroki scrapowania')
    parser.add_argument('--app-url', help='URL aplikacji UI do wysyłki danych (np. http://localhost:3001 lub https://twoja-app.herokuapp.com)')
    parser.add_argument('--app-api-key', help='API Key do autoryzacji w aplikacji UI')
    args = parser.parse_args()

    # Ustaw VERBOSE globalnie
    global VERBOSE
    VERBOSE = args.verbose

    # Walidacja
    if args.mode == 'urls' and not args.input:
        print('❌ W trybie urls wymagany jest argument --input')
        return
    
    if args.mode == 'auto' and not args.sports:
        print('⚠️  Nie podano sportów, używam domyślnie: football')
        args.sports = ['football']

    print('='*60)
    print('🏆 Livesport H2H Scraper - Multi-Sport Edition')
    print('='*60)
    print(f'📅 Data: {args.date}')
    print(f'🎮 Tryb: {args.mode}')
    if args.away_team_focus:
        print(f'🎯 Fokus: GOŚCIE (away teams) z ≥60% H2H')
    else:
        print(f'🎯 Fokus: GOSPODARZE (home teams) z ≥60% H2H')
    if args.sports:
        print(f'⚽ Sporty: {", ".join(args.sports)}')
    if args.leagues:
        print(f'🏟️  Ligi: {", ".join(args.leagues)}')
    print('='*60)

    driver = start_driver(headless=args.headless)

    # Zbieranie URLi
    if args.mode == 'urls':
        print(f'\n📂 Wczytuję URLe z pliku: {args.input}')
        with open(args.input, 'r', encoding='utf-8') as f:
            urls = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    else:
        print('\n🔍 Automatyczne zbieranie linków...')
        if args.advanced:
            urls = get_match_links_advanced(driver, args.date, args.sports)
        else:
            urls = get_match_links_from_day(driver, args.date, args.sports, args.leagues)

    print(f'\n✅ Znaleziono {len(urls)} meczów do sprawdzenia')
    
    if len(urls) == 0:
        print('❌ Nie znaleziono żadnych meczów. Spróbuj:')
        print('   - Uruchomić bez --headless aby zobaczyć co się dzieje')
        print('   - Sprawdzić czy data jest poprawna')
        print('   - Użyć trybu --mode urls z ręcznie przygotowanymi URLami')
        driver.quit()
        return

    # Przetwarzanie meczów
    print('\n' + '='*60)
    print('🔄 Rozpoczynam przetwarzanie meczów...')
    print('='*60)
    
    rows = []
    qualifying_count = 0
    
    # KLUCZOWE: Na GitHub Actions używaj krótszego interwału (mniej RAM)
    # Wykryj środowisko GitHub Actions
    is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
    if is_github_actions:
        RESTART_INTERVAL = 30  # GitHub Actions: restart co 30 meczów (oszczędność pamięci)
        print("🔧 Wykryto GitHub Actions - używam skróconego interwału restartu (30 meczów)")
    else:
        RESTART_INTERVAL = 80  # Lokalnie: restart co 80 meczów
    
    CHECKPOINT_INTERVAL = 20  # Checkpoint co 20 meczów (zwiększona częstotliwość dla bezpieczeństwa)
    
    for i, url in enumerate(urls, 1):
        if VERBOSE:
            print(f'\n[{i}/{len(urls)}] 🔍 Przetwarzam: {url[:80]}...')
        else:
            # Prosty progress indicator
            print(f'\r[{i}/{len(urls)}] Przetwarzam...', end='', flush=True)
        try:
            # Wykryj sport z URL (tennis ma '/tenis/' w URLu)
            is_tennis = '/tenis/' in url.lower() or 'tennis' in url.lower()
            
            if is_tennis:
                # Użyj dedykowanej funkcji dla tenisa (ADVANCED)
                info = process_match_tennis(url, driver)
                rows.append(info)
                
                if info['qualifies']:
                    qualifying_count += 1
                    player_a_wins = info['home_wins_in_h2h_last5']
                    player_b_wins = info.get('away_wins_in_h2h', 0)
                    advanced_score = info.get('advanced_score', 0)
                    favorite = info.get('favorite', 'unknown')
                    
                    # Określ kto jest faworytem
                    if favorite == 'player_a':
                        fav_name = info["home_team"]
                    elif favorite == 'player_b':
                        fav_name = info["away_team"]
                    else:
                        fav_name = "Równi"
                    
                    # Tryb normalny: krótka wiadomość
                    if not VERBOSE:
                        print(f'\r[{i}/{len(urls)}] ✅ {info["home_team"]} vs {info["away_team"]} - Faworytem: {fav_name} ({advanced_score:.0f}/100)')
                    else:
                        # Tryb verbose: szczegóły
                        print(f'   ✅ KWALIFIKUJE SIĘ! {info["home_team"]} vs {info["away_team"]}')
                        print(f'      Faworytem: {fav_name} (Score: {advanced_score:.1f}/100)')
                        print(f'      H2H: {player_a_wins}-{player_b_wins}')
                        
                        # Pokaż breakdown jeśli dostępny
                        if 'score_breakdown' in info:
                            breakdown = info['score_breakdown']
                            print(f'      └─ H2H:{breakdown.get("h2h_score", 0):.0f} | Rank:{breakdown.get("ranking_score", 0):.0f} | Form:{breakdown.get("form_score", 0):.0f} | Surface:{breakdown.get("surface_score", 0):.0f}')
                        
                        # Pokaż dodatkowe info
                        if info.get('ranking_a') and info.get('ranking_b'):
                            print(f'      Rankings: #{info["ranking_a"]} vs #{info["ranking_b"]}')
                        if info.get('surface'):
                            print(f'      Surface: {info["surface"]}')
                        
                else:
                    player_a_wins = info['home_wins_in_h2h_last5']
                    player_b_wins = info.get('away_wins_in_h2h', 0)
                    advanced_score = info.get('advanced_score', 0)
                    if VERBOSE:
                        print(f'   ❌ Nie kwalifikuje (H2H: {player_a_wins}-{player_b_wins}, Score: {advanced_score:.1f}/100)')
            else:
                # Sporty drużynowe (football, basketball, etc.)
                info = process_match(url, driver, away_team_focus=args.away_team_focus)
                rows.append(info)
                
                if info['qualifies']:
                    qualifying_count += 1
                    h2h_count = info.get('h2h_count', 0)
                    win_rate = info.get('win_rate', 0.0)
                    home_form = info.get('home_form', [])
                    away_form = info.get('away_form', [])
                    
                    home_form_str = '-'.join(home_form) if home_form else 'N/A'
                    away_form_str = '-'.join(away_form) if away_form else 'N/A'
                    
                    # Wybierz co pokazać w zależności od trybu
                    if args.away_team_focus:
                        wins_count = info.get('away_wins_in_h2h_last5', 0)
                        team_name = info['away_team']
                    else:
                        wins_count = info['home_wins_in_h2h_last5']
                        team_name = info['home_team']
                    
                    # Tryb normalny: krótka wiadomość
                    if not VERBOSE:
                        print(f'\r[{i}/{len(urls)}] ✅ {info["home_team"]} vs {info["away_team"]} - {team_name} ({wins_count}/{h2h_count} = {win_rate*100:.0f}%)')
                    else:
                        # Tryb verbose: szczegóły
                        print(f'   ✅ KWALIFIKUJE SIĘ! {info["home_team"]} vs {info["away_team"]}')
                        print(f'      Zespół fokusowany: {team_name}')
                        print(f'      H2H: {wins_count}/{h2h_count} ({win_rate*100:.0f}%)')
                        if home_form or away_form:
                            print(f'      Forma: {info["home_team"]} [{home_form_str}] | {info["away_team"]} [{away_form_str}]')
                            
                        # Pokaż szczegóły H2H dla kwalifikujących się
                        if info['h2h_last5']:
                            print(f'      Ostatnie H2H:')
                            for idx, h2h in enumerate(info['h2h_last5'][:5], 1):
                                print(f'        {idx}. {h2h.get("home", "?")} {h2h.get("score", "?")} {h2h.get("away", "?")}')
                else:
                    h2h_count = info.get('h2h_count', 0)
                    win_rate = info.get('win_rate', 0.0)
                    if VERBOSE:
                        if h2h_count > 0:
                            if args.away_team_focus:
                                wins_count = info.get('away_wins_in_h2h_last5', 0)
                            else:
                                wins_count = info['home_wins_in_h2h_last5']
                            print(f'   ❌ Nie kwalifikuje ({wins_count}/{h2h_count} = {win_rate*100:.0f}%)')
                        else:
                            print(f'   ⚠️  Brak H2H')
                
        except Exception as e:
            if VERBOSE:
                print(f'   ⚠️  Błąd: {e}')
        
        # AUTO-RESTART przeglądarki co N meczów (zapobiega crashom)
        if i % RESTART_INTERVAL == 0 and i < len(urls):
            print(f'\n🔄 AUTO-RESTART: Restartowanie przeglądarki po {i} meczach...')
            print(f'   ✅ Przetworzone dane ({len(rows)} meczów) są bezpieczne w pamięci!')
            try:
                driver.quit()
                # Wymuś garbage collection dla zwolnienia pamięci (ważne na GitHub Actions)
                gc.collect()
                time.sleep(2)
                driver = start_driver(headless=args.headless)
                print(f'   ✅ Przeglądarka zrestartowana! Kontynuuję od meczu {i+1}...\n')
            except Exception as e:
                print(f'   ⚠️  Błąd restartu: {e}')
                gc.collect()  # Wyczyść pamięć mimo błędu
                driver = start_driver(headless=args.headless)
        
        # Rate limiting - adaptacyjny (zoptymalizowany)
        elif i < len(urls):
            delay = 0.8 + (i % 3) * 0.3  # Zmniejszone z 1.0+0.5 na 0.8+0.3
            time.sleep(delay)

    driver.quit()

    # Wyczyść progress indicator z trybu normalnego
    if not VERBOSE:
        print()  # Nowa linia po progress indicator
    
    # Zapisywanie wyników
    print('\n' + '='*60)
    print('💾 Zapisywanie wyników...')
    print('='*60)
    
    os.makedirs('outputs', exist_ok=True)
    
    # Nazwa pliku z opcjonalnym sufixem
    suffix = f'_{args.output_suffix}' if args.output_suffix else ''
    if args.sports and len(args.sports) == 1:
        suffix = f'_{args.sports[0]}{suffix}'
    
    # Dodaj sufiks dla trybu away_team_focus
    if args.away_team_focus:
        suffix = f'{suffix}_AWAY_FOCUS'
    
    outfn = os.path.join('outputs', f'livesport_h2h_{args.date}{suffix}.csv')

    # Przygotowanie DataFrame
    df = pd.DataFrame(rows)
    
    # Konwersja h2h_last5 (lista słowników) na string dla CSV
    if 'h2h_last5' in df.columns:
        df['h2h_last5'] = df['h2h_last5'].apply(lambda x: str(x) if x else '')
    
    # Konwersja all_odds (słownik) na JSON string dla CSV (NOWE V3)
    if 'all_odds' in df.columns:
        import json
        df['all_odds'] = df['all_odds'].apply(lambda x: json.dumps(x, ensure_ascii=False) if x else '')
    
    # Konwersja bookmakers_found (lista) na string dla CSV (NOWE V3)
    if 'bookmakers_found' in df.columns:
        df['bookmakers_found'] = df['bookmakers_found'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x) if x else '')
    
    df.to_csv(outfn, index=False, encoding='utf-8-sig')

    # NOWE V3: Zapisz do bazy danych SQLite (dla aplikacji webowej)
    if DB_AVAILABLE and rows:
        try:
            print('\n💾 Zapisywanie do bazy danych...')
            db = MatchDatabase()
            inserted = db.insert_matches_batch(rows)
            print(f'✅ Zapisano {inserted}/{len(rows)} meczów do bazy danych')
            
            # Pokaż statystyki bazy
            stats = db.get_stats()
            print(f'📊 Statystyki bazy danych:')
            print(f'   Wszystkich meczów: {stats["total_matches"]}')
            print(f'   Kwalifikujących się: {stats["qualifying_matches"]}')
            print(f'   Sportów: {stats["unique_sports"]}')
            print(f'   Ostatnia aktualizacja: {stats["last_update"]}')
        except Exception as e:
            print(f'⚠️ Błąd zapisu do bazy danych: {e}')

    # NOWE V4: Wysyłka danych do aplikacji UI (Heroku/Railway)
    if args.app_url and rows:
        try:
            print('\n🔗 KROK 4/4: Wysyłanie danych do aplikacji UI...')
            print('='*70)
            from app_integrator import AppIntegrator
            
            integrator = AppIntegrator(app_url=args.app_url, api_key=args.app_api_key)
            
            # Test połączenia
            print(f'\n🔍 Testuję połączenie z aplikacją...')
            print(f'   URL: {args.app_url}')
            if integrator.test_connection():
                print(f'   ✅ Połączenie działa!')
            else:
                print(f'   ⚠️  Nie udało się połączyć, ale próbuję wysłać dane...')
            
            # Wysyłka danych
            print(f'\n📤 Wysyłam dane do aplikacji...')
            sport = args.sports[0] if args.sports else 'unknown'
            
            if integrator.send_matches(rows, args.date, sport):
                print(f'✅ Synchronizacja z aplikacją ukończona!')
            else:
                print(f'⚠️  Nie udało się wysłać danych (ale scraping się powiedł)')
                
        except ImportError:
            print(f'⚠️  app_integrator.py nie znaleziony - pomijam wysyłkę do aplikacji')
        except Exception as e:
            print(f'⚠️  Błąd podczas wysyłki do aplikacji: {e}')
    elif args.app_url and not rows:
        print(f'\n⚠️  Brak danych do wysłania do aplikacji UI')
    elif not args.app_url:
        print(f'\n💡 TIP: Użyj --app-url aby automatycznie wysyłać dane do aplikacji UI')

    # Podsumowanie
    print(f'\n📊 PODSUMOWANIE:')
    print(f'   Przetworzono meczów: {len(rows)}')
    print(f'   Kwalifikujących się: {qualifying_count} ({qualifying_count/len(rows)*100:.1f}%)' if rows else '   Brak danych')
    print(f'   Zapisano do: {outfn}')
    print('\n✨ Gotowe!')


if __name__ == '__main__':
    main()

