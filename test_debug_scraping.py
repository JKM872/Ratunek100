"""
Test z prawdziwym scrapingiem - debug version
Uruchamia scraper z szczegółowym logowaniem
"""

import sys
import traceback

# Włącz szczegółowe logi
import livesport_h2h_scraper
livesport_h2h_scraper.VERBOSE = True

print("="*70)
print("🔍 DEBUG TEST - Prawdziwy scraping z pełnym traceback")
print("="*70)

# Uruchom scraper na 1 meczu volleyball
try:
    from scrape_and_notify import main
    
    # Symuluj argumenty wiersza poleceń
    sys.argv = [
        'scrape_and_notify.py',
        '--date', '2025-10-06',
        '--sports', 'volleyball',
        '--headless',
        '--skip-no-odds',
        '--only-form-advantage',
        '--no-email',  # Bez wysyłania emaila
        '--max-events', '1'  # Tylko 1 mecz
    ]
    
    main()
    
except Exception as e:
    print("\n" + "="*70)
    print("❌ BŁĄD PODCZAS SCRAPINGU:")
    print("="*70)
    print(f"Typ błędu: {type(e).__name__}")
    print(f"Komunikat: {e}")
    print("\nPełny traceback:")
    print("-"*70)
    traceback.print_exc()
    print("="*70)
