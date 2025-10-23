"""
Generator przykładowych URLi dla Livesport H2H Scraper
------------------------------------------------------
Skrypt pomocniczy do szybkiego generowania pliku match_urls.txt
z przykładowymi URLami dla różnych sportów i lig.

Uwaga: To tylko przykłady - rzeczywiste URLe muszą pochodzić z Livesport.com
"""

import argparse
from datetime import datetime, timedelta


# Przykładowe szablony URLi dla różnych sportów
URL_TEMPLATES = {
    'football': {
        'ekstraklasa': 'https://www.livesport.com/pl/pilka-nozna/polska/ekstraklasa/',
        'premier-league': 'https://www.livesport.com/pl/pilka-nozna/anglia/premier-league/',
        'la-liga': 'https://www.livesport.com/pl/pilka-nozna/hiszpania/laliga/',
        'bundesliga': 'https://www.livesport.com/pl/pilka-nozna/niemcy/bundesliga/',
        'serie-a': 'https://www.livesport.com/pl/pilka-nozna/wlochy/serie-a/',
        'ligue-1': 'https://www.livesport.com/pl/pilka-nozna/francja/ligue-1/',
    },
    'basketball': {
        'nba': 'https://www.livesport.com/pl/koszykowka/usa/nba/',
        'euroleague': 'https://www.livesport.com/pl/koszykowka/europa/euroliga/',
        'pbl': 'https://www.livesport.com/pl/koszykowka/polska/energa-basket-liga/',
    },
    'volleyball': {
        'plusliga': 'https://www.livesport.com/pl/siatkowka/polska/plusliga/',
        'tauron-liga': 'https://www.livesport.com/pl/siatkowka/polska/tauron-liga/',
    },
    'handball': {
        'superliga': 'https://www.livesport.com/pl/pilka-reczna/polska/superliga/',
    },
    'rugby': {
        'premiership': 'https://www.livesport.com/pl/rugby-union/anglia/premiership/',
        'top-14': 'https://www.livesport.com/pl/rugby-union/francja/top-14/',
    },
    'hockey': {
        'nhl': 'https://www.livesport.com/pl/hokej/usa/nhl/',
        'khl': 'https://www.livesport.com/pl/hokej/rosja/khl/',
    }
}


def generate_template(sports=None, leagues=None):
    """Generuje szablon pliku match_urls.txt"""
    
    if not sports:
        sports = list(URL_TEMPLATES.keys())
    
    output = []
    output.append("# " + "="*60)
    output.append("# Plik z URLami meczów - automatycznie wygenerowany")
    output.append("# " + "="*60)
    output.append("#")
    output.append("# Wygenerowano: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    output.append("#")
    output.append("# JAK UŻYĆ:")
    output.append("# 1. Wejdź na Livesport.com")
    output.append("# 2. Znajdź interesujące Cię mecze")
    output.append("# 3. Skopiuj pełny URL meczu")
    output.append("# 4. Wklej poniżej (odkomentuj linię usuwając '#')")
    output.append("# 5. Uruchom: python livesport_h2h_scraper.py --mode urls --date YYYY-MM-DD --input match_urls.txt --headless")
    output.append("#")
    output.append("# " + "="*60)
    output.append("")
    
    for sport in sports:
        if sport not in URL_TEMPLATES:
            continue
        
        sport_leagues = URL_TEMPLATES[sport]
        
        # Filtrowanie po ligach jeśli podano
        if leagues:
            sport_leagues = {k: v for k, v in sport_leagues.items() if k in leagues}
        
        if not sport_leagues:
            continue
        
        output.append("")
        output.append(f"# {sport.upper()}")
        output.append("# " + "-"*60)
        
        for league, url in sport_leagues.items():
            output.append(f"# {league}: {url}")
            output.append(f"# Przykład: {url}team1-team2/match-id/")
            output.append("")
    
    output.append("")
    output.append("# " + "="*60)
    output.append("# DODAJ SWOJE URLe PONIŻEJ (bez # na początku)")
    output.append("# " + "="*60)
    output.append("")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Generator szablonu match_urls.txt dla Livesport H2H Scraper'
    )
    parser.add_argument('--sports', nargs='+',
                       choices=['football', 'basketball', 'volleyball', 'handball', 'rugby', 'hockey'],
                       help='Lista sportów do uwzględnienia')
    parser.add_argument('--leagues', nargs='+',
                       help='Lista konkretnych lig do uwzględnienia')
    parser.add_argument('--output', default='match_urls_generated.txt',
                       help='Nazwa pliku wyjściowego (domyślnie: match_urls_generated.txt)')
    
    args = parser.parse_args()
    
    print('🏆 Generator URLi dla Livesport H2H Scraper')
    print('='*60)
    
    content = generate_template(args.sports, args.leagues)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'✅ Wygenerowano szablon: {args.output}')
    print(f'\nKroki dalej:')
    print(f'1. Otwórz plik: {args.output}')
    print(f'2. Dodaj rzeczywiste URLe meczów z Livesport.com')
    print(f'3. Uruchom scraper:')
    print(f'   python livesport_h2h_scraper.py --mode urls --date 2025-10-05 --input {args.output} --headless')
    print()


if __name__ == '__main__':
    main()

