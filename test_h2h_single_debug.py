"""
Test pojedynczego meczu z PEŁNYM debugowaniem
"""

import time
from livesport_h2h_scraper import start_driver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# URL testowy - siatkówka z przyszłości
test_url = "https://www.livesport.com/pl/siatkowka/?date=2025-10-06"

print("="*70)
print("🔧 DIAGNOZA H2H - Pojedynczy mecz")
print("="*70)

driver = start_driver(headless=False)  # BEZ headless - zobaczymy co się dzieje

try:
    print(f"\n1️⃣ Otwieram stronę listy meczów...")
    driver.get(test_url)
    time.sleep(3)
    
    print(f"\n2️⃣ Szukam pierwszego linku do meczu...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Znajdź wszystkie linki
    all_links = soup.find_all('a', href=True)
    match_link = None
    
    for a in all_links:
        href = a['href']
        if '/mecz/' in href or '/match/' in href:
            if href.startswith('/'):
                match_link = 'https://www.livesport.com' + href
            else:
                match_link = href
            print(f"   ✅ Znaleziono: {match_link}")
            break
    
    if not match_link:
        print("   ❌ Nie znaleziono żadnego linku do meczu!")
        driver.quit()
        exit()
    
    # Konwertuj na URL H2H (NOWA LOGIKA - obsługuje ?mid=)
    if '?' in match_link:
        base_url, params = match_link.split('?', 1)
        params = '?' + params
    else:
        base_url = match_link
        params = ''
    
    base_url = base_url.rstrip('/')
    
    if '/szczegoly' in base_url:
        base_url = base_url.replace('/szczegoly', '/h2h/ogolem')
    elif '/h2h/' not in base_url:
        base_url = base_url + '/h2h/ogolem'
    
    h2h_url = base_url + params
    
    print(f"\n3️⃣ Otwieram stronę H2H...")
    print(f"   URL: {h2h_url}")
    driver.get(h2h_url)
    
    print(f"\n4️⃣ Czekam na załadowanie (8 sekund)...")
    time.sleep(8)
    
    print(f"\n5️⃣ Zapisuję HTML do pliku...")
    html = driver.page_source
    with open('outputs/test_h2h_debug.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"   ✅ Zapisano: outputs/test_h2h_debug.html")
    
    print(f"\n6️⃣ Analizuję HTML...")
    soup = BeautifulSoup(html, 'html.parser')
    
    # Szukaj różnych elementów
    print(f"\n   📊 Statystyki:")
    
    h2h_sections = soup.find_all('div', class_='h2h__section')
    print(f"   - div.h2h__section: {len(h2h_sections)}")
    
    h2h_rows = soup.select('a.h2h__row')
    print(f"   - a.h2h__row: {len(h2h_rows)}")
    
    h2h_rows2 = soup.select('div.h2h__row')
    print(f"   - div.h2h__row: {len(h2h_rows2)}")
    
    all_h2h = soup.find_all(class_=lambda x: x and 'h2h' in x.lower())
    print(f"   - elementy z 'h2h' w klasie: {len(all_h2h)}")
    
    # Pokaż przykładowe klasy
    print(f"\n   📝 Przykładowe klasy znalezionych elementów:")
    for elem in all_h2h[:10]:
        classes = ' '.join(elem.get('class', []))
        print(f"      - {elem.name}.{classes[:60]}")
    
    # Szukaj tekstu "Pojedynki" lub "bezpośrednie"
    print(f"\n   🔍 Szukam tekstu 'Pojedynki' lub 'bezpośrednie'...")
    text_content = soup.get_text()
    if 'pojedynki' in text_content.lower():
        print(f"      ✅ Znaleziono 'pojedynki' w tekście!")
    else:
        print(f"      ❌ NIE znaleziono 'pojedynki'")
    
    if 'bezpośrednie' in text_content.lower():
        print(f"      ✅ Znaleziono 'bezpośrednie' w tekście!")
    else:
        print(f"      ❌ NIE znaleziono 'bezpośrednie'")
    
    # Sprawdź tytuł strony
    print(f"\n   📄 Tytuł strony:")
    print(f"      {soup.title.string if soup.title else 'BRAK'}")
    
    print(f"\n" + "="*70)
    print(f"✅ DIAGNOZA ZAKOŃCZONA")
    print(f"="*70)
    print(f"\nOtwórz plik: outputs/test_h2h_debug.html")
    print(f"i sprawdź jego zawartość w przeglądarce lub edytorze.")
    print(f"\nSzukaj w nim:")
    print(f"  - sekcji 'Pojedynki bezpośrednie'")
    print(f"  - wyników meczów (np. '3-1', '82-70')")
    print(f"  - nazw drużyn")
    print(f"\nPrzeglądarka pozostanie otwarta - możesz zobaczyć stronę!")
    print(f"Naciśnij Enter aby zamknąć...")
    input()
    
except Exception as e:
    print(f"\n❌ BŁĄD: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print("\n🔒 Zamknięto przeglądarkę")

