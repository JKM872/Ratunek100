"""
Skrypt do zbierania linków do meczów z Livesport
Używany przez massive-scraping-parallel workflow
"""

import argparse
from livesport_h2h_scraper import start_driver, get_match_links_from_day

def main():
    parser = argparse.ArgumentParser(description='Zbierz linki do meczów')
    parser.add_argument('--date', required=True, help='Data YYYY-MM-DD')
    parser.add_argument('--sports', nargs='+', required=True, help='Lista sportów')
    parser.add_argument('--output', default='match_urls.txt', help='Plik wyjściowy')
    parser.add_argument('--headless', action='store_true', help='Tryb headless')
    
    args = parser.parse_args()
    
    print(f'🔍 Zbieranie linków dla: {", ".join(args.sports)}')
    print(f'📅 Data: {args.date}')
    
    driver = start_driver(headless=args.headless)
    
    try:
        urls = get_match_links_from_day(driver, args.date, sports=args.sports, leagues=None)
        
        print(f'\n✅ Znaleziono {len(urls)} meczów')
        
        with open(args.output, 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(url + '\n')
        
        print(f'💾 Zapisano do: {args.output}')
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()

