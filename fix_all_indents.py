"""Kompleksowa naprawa wszystkich błędów wcięć"""
import re

with open('livesport_h2h_scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Lines 210-217 - winner assignment w try-except
old_pattern1 = r"""                try:
                    gh = int\(goals_home\)
                    ga = int\(goals_away\)
                    if gh > ga:
                winner = 'home'
                    elif ga > gh:
                winner = 'away'
            else:
                winner = 'draw'
                except:
                    winner = 'unknown'"""

new_pattern1 = """                try:
                    gh = int(goals_home)
                    ga = int(goals_away)
                    if gh > ga:
                        winner = 'home'
                    elif ga > gh:
                        winner = 'away'
                    else:
                        winner = 'draw'
                except:
                    winner = 'unknown'"""

content = re.sub(old_pattern1, new_pattern1, content)

# Fix 2: Lines 1665-1694 - główna pętla sportów zespołowych
old_pattern2 = r"""            else:
                # Sporty drużynowe \(football, basketball, etc\.\)
            info = process_match\(url, driver\)
            rows\.append\(info\)
            
            if info\['qualifies'\]:
                qualifying_count \+= 1
                    h2h_count = info\.get\('h2h_count', 0\)
                    win_rate = info\.get\('win_rate', 0\.0\)
                    home_form = info\.get\('home_form', \[\]\)"""

new_pattern2 = """            else:
                # Sporty drużynowe (football, basketball, etc.)
                info = process_match(url, driver)
                rows.append(info)
                
                if info['qualifies']:
                    qualifying_count += 1
                    h2h_count = info.get('h2h_count', 0)
                    win_rate = info.get('win_rate', 0.0)
                    home_form = info.get('home_form', [])"""

content = re.sub(old_pattern2, new_pattern2, content)

# Fix 3: Lines around 1684-1694 - else block
old_pattern3 = r"""                # Pokaż szczegóły H2H dla kwalifikujących się
                if info\['h2h_last5'\]:
                        print\(f'      Ostatnie H2H:'\)
                    for idx, h2h in enumerate\(info\['h2h_last5'\]\[:5\], 1\):
                        print\(f'        {idx}\. {h2h\.get\("home", "\?"\)} {h2h\.get\("score", "\?"\)} {h2h\.get\("away", "\?"\)}'\)
            else:
                    h2h_count = info\.get\('h2h_count', 0\)
                    win_rate = info\.get\('win_rate', 0\.0\)
                    if h2h_count > 0:
                        print\(f'   ❌ Nie kwalifikuje się \({info\["home_wins_in_h2h_last5"\]}/{h2h_count} = {win_rate\*100:.0f}%\)'\)
                    else:
                        print\(f'   ⚠️  Brak H2H'\)"""

new_pattern3 = """                    # Pokaż szczegóły H2H dla kwalifikujących się
                    if info['h2h_last5']:
                        print(f'      Ostatnie H2H:')
                        for idx, h2h in enumerate(info['h2h_last5'][:5], 1):
                            print(f'        {idx}. {h2h.get("home", "?")} {h2h.get("score", "?")} {h2h.get("away", "?")}')
                else:
                    h2h_count = info.get('h2h_count', 0)
                    win_rate = info.get('win_rate', 0.0)
                    if h2h_count > 0:
                        print(f'   ❌ Nie kwalifikuje się ({info["home_wins_in_h2h_last5"]}/{h2h_count} = {win_rate*100:.0f}%)')
                    else:
                        print(f'   ⚠️  Brak H2H')"""

content = re.sub(old_pattern3, new_pattern3, content)

# Zapisz naprawiony plik
with open('livesport_h2h_scraper.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Naprawiono błędy wcięć w livesport_h2h_scraper.py")

