#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 WERYFIKACJA PRZEWIDYWAŃ - Sprawdza trafność typów z poprzednich dni

Usage:
  python verify_predictions.py --date 2025-10-07 --headless
  
Funkcje:
- Wczytuje przewidywania z pliku predictions_{date}.json
- Scrapuje wyniki zakończonych meczów
- Porównuje z przewidywaniami
- Generuje raport ze statystykami:
  * Ogólna trafność (%)
  * Trafność Tennis vs Team Sports
  * ROI (jeśli gralibyśmy kursy)
  * Top 5 najlepszych typów
  * Top 5 najgorszych typów
"""

import json
import argparse
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from email_notifier import send_email_notification


class PredictionVerifier:
    """Weryfikuje trafność przewidywań z poprzednich dni"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        
    def _init_driver(self):
        """Inicjalizuje Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
    def load_predictions(self, date: str) -> Optional[List[Dict]]:
        """Wczytuje przewidywania z pliku JSON"""
        # Szukaj pliku predictions dla danej daty (może mieć różne nazwy)
        output_dir = Path("outputs")
        if not output_dir.exists():
            print(f"❌ Brak folderu outputs/")
            return None
        
        # Szukaj pliku z datą i _predictions.json
        predictions_files = list(output_dir.glob(f"*{date}*_predictions.json"))
        
        if not predictions_files:
            print(f"❌ Brak pliku z przewidywaniami dla daty {date}")
            print(f"   Szukano w: outputs/*{date}*_predictions.json")
            return None
        
        predictions_file = predictions_files[0]
        print(f"📂 Znaleziono plik: {predictions_file}")
        
        if len(predictions_files) > 1:
            print(f"⚠️  Znaleziono {len(predictions_files)} plików, używam: {predictions_file.name}")
        
        try:
            with open(predictions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Wczytano {len(data)} przewidywań z {date}")
            return data
        except Exception as e:
            print(f"❌ Błąd wczytywania: {e}")
            return None
    
    def scrape_match_result(self, match_url: str) -> Optional[Dict]:
        """Scrapuje wynik zakończonego meczu"""
        try:
            self.driver.get(match_url)
            time.sleep(2.0)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Sprawdź czy mecz się zakończył
            status_elem = soup.find('div', class_='detailScore__status')
            if status_elem:
                status_text = status_elem.get_text(strip=True).lower()
                if any(x in status_text for x in ['zakończony', 'finished', 'ft', 'ao']):
                    # Mecz zakończony, pobierz wynik
                    pass
                else:
                    # Mecz jeszcze się nie zakończył
                    return {'status': 'not_finished'}
            
            # Pobierz wynik
            score_home = None
            score_away = None
            
            # Próba 1: Główny wynik
            score_divs = soup.find_all('div', class_='detailScore__wrapper')
            if len(score_divs) >= 2:
                try:
                    score_home = int(score_divs[0].get_text(strip=True))
                    score_away = int(score_divs[1].get_text(strip=True))
                except:
                    pass
            
            # Próba 2: JSON-LD
            if score_home is None:
                scripts = soup.find_all('script', type='application/ld+json')
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, dict) and 'homeTeam' in data:
                            score_home = data.get('homeTeam', {}).get('score')
                            score_away = data.get('awayTeam', {}).get('score')
                            break
                    except:
                        continue
            
            if score_home is None or score_away is None:
                return {'status': 'no_score'}
            
            # Określ zwycięzcę
            if score_home > score_away:
                winner = 'home'
            elif score_away > score_home:
                winner = 'away'
            else:
                winner = 'draw'
            
            return {
                'status': 'finished',
                'score_home': score_home,
                'score_away': score_away,
                'winner': winner
            }
            
        except Exception as e:
            print(f"   ⚠️ Błąd scrapingu wyniku: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def verify_predictions(self, date: str) -> Dict:
        """Weryfikuje wszystkie przewidywania z danego dnia"""
        predictions = self.load_predictions(date)
        if not predictions:
            return {}
        
        print(f"\n{'='*70}")
        print(f"🎯 WERYFIKACJA PRZEWIDYWAŃ - {date}")
        print(f"{'='*70}\n")
        
        # Inicjalizuj driver
        if not self.driver:
            self._init_driver()
        
        stats = {
            'total': len(predictions),
            'finished': 0,
            'not_finished': 0,
            'correct': 0,
            'incorrect': 0,
            'draws': 0,
            'errors': 0,
            'tennis_correct': 0,
            'tennis_incorrect': 0,
            'tennis_total': 0,
            'team_correct': 0,
            'team_incorrect': 0,
            'team_total': 0,
            'results': []
        }
        
        for i, prediction in enumerate(predictions, 1):
            match_url = prediction.get('match_url', '')
            home = prediction.get('home_team') or prediction.get('player_a', 'N/A')
            away = prediction.get('away_team') or prediction.get('player_b', 'N/A')
            is_tennis = 'player_a' in prediction
            favorite = prediction.get('favorite', 'home')  # Dla tenisa
            
            print(f"[{i}/{len(predictions)}] {home} vs {away}")
            
            # Scrapuj wynik
            result = self.scrape_match_result(match_url)
            
            if result['status'] == 'finished':
                stats['finished'] += 1
                winner = result['winner']
                
                # Sprawdź czy przewidywanie było poprawne
                if is_tennis:
                    stats['tennis_total'] += 1
                    # W tenisie favorite to 'A' lub 'B'
                    predicted_winner = 'home' if favorite == 'A' else 'away'
                    correct = (predicted_winner == winner)
                    
                    if correct:
                        stats['tennis_correct'] += 1
                        stats['correct'] += 1
                        emoji = '✅'
                    else:
                        stats['tennis_incorrect'] += 1
                        stats['incorrect'] += 1
                        emoji = '❌'
                else:
                    stats['team_total'] += 1
                    # W sportach drużynowych zawsze typujemy gospodarza
                    correct = (winner == 'home')
                    
                    if winner == 'draw':
                        stats['draws'] += 1
                        emoji = '🟡'
                    elif correct:
                        stats['team_correct'] += 1
                        stats['correct'] += 1
                        emoji = '✅'
                    else:
                        stats['team_incorrect'] += 1
                        stats['incorrect'] += 1
                        emoji = '❌'
                
                # Zapisz szczegóły
                stats['results'].append({
                    'match': f"{home} vs {away}",
                    'predicted': 'home' if not is_tennis or favorite == 'A' else 'away',
                    'actual': winner,
                    'correct': correct,
                    'score': f"{result['score_home']}-{result['score_away']}",
                    'is_tennis': is_tennis,
                    'home_odds': prediction.get('home_odds'),
                    'away_odds': prediction.get('away_odds')
                })
                
                print(f"   {emoji} {result['score_home']}-{result['score_away']} | Wynik: {winner}")
                
            elif result['status'] == 'not_finished':
                stats['not_finished'] += 1
                print(f"   ⏳ Mecz jeszcze się nie zakończył")
            else:
                stats['errors'] += 1
                print(f"   ⚠️ Błąd: {result.get('status')}")
            
            time.sleep(0.5)  # Przerwa między requestami
        
        return stats
    
    def generate_report(self, stats: Dict, date: str) -> str:
        """Generuje raport HTML ze statystykami"""
        if stats['total'] == 0:
            return "<p>Brak danych do wygenerowania raportu.</p>"
        
        finished = stats['finished']
        if finished == 0:
            return "<p>Żaden mecz się jeszcze nie zakończył.</p>"
        
        accuracy = (stats['correct'] / finished * 100) if finished > 0 else 0
        
        # Trafność Tennis
        tennis_acc = 0
        if stats['tennis_total'] > 0:
            tennis_finished = stats['tennis_correct'] + stats['tennis_incorrect']
            tennis_acc = (stats['tennis_correct'] / tennis_finished * 100) if tennis_finished > 0 else 0
        
        # Trafność Team Sports
        team_acc = 0
        if stats['team_total'] > 0:
            team_finished = stats['team_correct'] + stats['team_incorrect']
            team_acc = (stats['team_correct'] / team_finished * 100) if team_finished > 0 else 0
        
        # Oblicz ROI (gdyby grać kursy po 100 PLN na mecz)
        roi_total = 0
        roi_count = 0
        stake = 100  # PLN na mecz
        
        for result in stats['results']:
            if result.get('home_odds') and result['predicted'] == 'home':
                if result['correct']:
                    roi_total += (result['home_odds'] * stake - stake)
                else:
                    roi_total -= stake
                roi_count += 1
            elif result.get('away_odds') and result['predicted'] == 'away':
                if result['correct']:
                    roi_total += (result['away_odds'] * stake - stake)
                else:
                    roi_total -= stake
                roi_count += 1
        
        roi_pct = (roi_total / (roi_count * stake) * 100) if roi_count > 0 else 0
        
        # Top 5 najlepszych i najgorszych
        correct_results = [r for r in stats['results'] if r['correct']]
        incorrect_results = [r for r in stats['results'] if not r['correct'] and r['actual'] != 'draw']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .stat-card.success {{ background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); }}
                .stat-card.danger {{ background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }}
                .stat-card.info {{ background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%); }}
                .stat-value {{ font-size: 36px; font-weight: bold; margin: 10px 0; }}
                .stat-label {{ font-size: 14px; opacity: 0.9; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #34495e; color: white; font-weight: 600; }}
                tr:hover {{ background: #f8f9fa; }}
                .correct {{ color: #27ae60; font-weight: bold; }}
                .incorrect {{ color: #e74c3c; font-weight: bold; }}
                .draw {{ color: #f39c12; font-weight: bold; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #ecf0f1; text-align: center; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 Raport Weryfikacji Przewidywań - {date}</h1>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">OGÓLNA TRAFNOŚĆ</div>
                        <div class="stat-value">{accuracy:.1f}%</div>
                        <div class="stat-label">{stats['correct']}/{finished} meczów</div>
                    </div>
                    
                    <div class="stat-card success">
                        <div class="stat-label">🎾 TENIS</div>
                        <div class="stat-value">{tennis_acc:.1f}%</div>
                        <div class="stat-label">{stats['tennis_correct']}/{stats['tennis_correct'] + stats['tennis_incorrect']} meczów</div>
                    </div>
                    
                    <div class="stat-card info">
                        <div class="stat-label">⚽ DRUŻYNOWE</div>
                        <div class="stat-value">{team_acc:.1f}%</div>
                        <div class="stat-label">{stats['team_correct']}/{stats['team_correct'] + stats['team_incorrect']} meczów</div>
                    </div>
                    
                    <div class="stat-card {'success' if roi_total > 0 else 'danger'}">
                        <div class="stat-label">💰 ROI (100 PLN/mecz)</div>
                        <div class="stat-value">{roi_pct:+.1f}%</div>
                        <div class="stat-label">{roi_total:+.0f} PLN</div>
                    </div>
                </div>
                
                <h2>📊 Podsumowanie</h2>
                <table>
                    <tr>
                        <td><strong>Wszystkie przewidywania:</strong></td>
                        <td>{stats['total']}</td>
                    </tr>
                    <tr>
                        <td><strong>Mecze zakończone:</strong></td>
                        <td>{stats['finished']}</td>
                    </tr>
                    <tr>
                        <td><strong>Mecze niezakończone:</strong></td>
                        <td>{stats['not_finished']}</td>
                    </tr>
                    <tr class="correct">
                        <td><strong>✅ Trafne:</strong></td>
                        <td>{stats['correct']}</td>
                    </tr>
                    <tr class="incorrect">
                        <td><strong>❌ Nietrafne:</strong></td>
                        <td>{stats['incorrect']}</td>
                    </tr>
                    <tr class="draw">
                        <td><strong>🟡 Remisy:</strong></td>
                        <td>{stats['draws']}</td>
                    </tr>
                </table>
                
                <h2>✅ Top 5 Najlepszych Typów</h2>
                <table>
                    <tr>
                        <th>Mecz</th>
                        <th>Wynik</th>
                        <th>Kurs</th>
                    </tr>
        """
        
        for result in correct_results[:5]:
            odds = result.get('home_odds') if result['predicted'] == 'home' else result.get('away_odds')
            odds_str = f"{odds:.2f}" if odds else "N/A"
            html += f"""
                    <tr>
                        <td>{result['match']}</td>
                        <td class="correct">{result['score']}</td>
                        <td>{odds_str}</td>
                    </tr>
            """
        
        html += """
                </table>
                
                <h2>❌ Top 5 Najgorszych Typów</h2>
                <table>
                    <tr>
                        <th>Mecz</th>
                        <th>Wynik</th>
                        <th>Kurs</th>
                    </tr>
        """
        
        for result in incorrect_results[:5]:
            odds = result.get('home_odds') if result['predicted'] == 'home' else result.get('away_odds')
            odds_str = f"{odds:.2f}" if odds else "N/A"
            html += f"""
                    <tr>
                        <td>{result['match']}</td>
                        <td class="incorrect">{result['score']}</td>
                        <td>{odds_str}</td>
                    </tr>
            """
        
        html += f"""
                </table>
                
                <div class="footer">
                    <p>📧 Raport wygenerowany automatycznie: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>🔔 Livesport H2H Scraper - Verification System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def save_report(self, html: str, date: str):
        """Zapisuje raport do pliku HTML"""
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        report_file = output_dir / f"verification_report_{date}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Raport zapisany: {report_file}")
        return report_file
    
    def close(self):
        """Zamyka driver"""
        if self.driver:
            self.driver.quit()


def main():
    parser = argparse.ArgumentParser(description='🎯 Weryfikacja przewidywań')
    parser.add_argument('--date', required=True, help='Data YYYY-MM-DD')
    parser.add_argument('--headless', action='store_true', help='Tryb headless')
    parser.add_argument('--send-email', action='store_true', help='Wyślij raport emailem')
    parser.add_argument('--to', help='Email odbiorcy')
    parser.add_argument('--from-email', help='Email nadawcy')
    parser.add_argument('--password', help='Hasło email')
    
    args = parser.parse_args()
    
    verifier = PredictionVerifier(headless=args.headless)
    
    try:
        # Weryfikuj przewidywania
        stats = verifier.verify_predictions(args.date)
        
        if not stats:
            print("❌ Brak danych do weryfikacji")
            return
        
        # Generuj raport
        html = verifier.generate_report(stats, args.date)
        report_file = verifier.save_report(html, args.date)
        
        # Wyślij email (opcjonalnie)
        if args.send_email and args.to:
            print("\n📧 Wysyłam raport emailem...")
            
            subject = f"🎯 Raport Weryfikacji - {args.date} ({stats['correct']}/{stats['finished']} = {stats['correct']/stats['finished']*100:.1f}%)"
            
            # Zapisz tymczasowy plik HTML
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
                tmp.write(html)
                tmp_path = tmp.name
            
            try:
                # Użyj standardowej funkcji wysyłania
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                import smtplib
                
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = args.from_email or args.to
                msg['To'] = args.to
                
                html_part = MIMEText(html, 'html', 'utf-8')
                msg.attach(html_part)
                
                # Wykryj provider
                provider = 'gmail' if 'gmail' in (args.from_email or args.to) else 'smtp'
                
                if provider == 'gmail':
                    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    smtp_server.login(args.from_email or args.to, args.password)
                    smtp_server.sendmail(args.from_email or args.to, args.to, msg.as_string())
                    smtp_server.quit()
                
                print("✅ Email wysłany!")
            except Exception as e:
                print(f"❌ Błąd wysyłania: {e}")
            finally:
                import os
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        # Podsumowanie w konsoli
        print(f"\n{'='*70}")
        print(f"🎯 PODSUMOWANIE WERYFIKACJI")
        print(f"{'='*70}")
        print(f"📅 Data: {args.date}")
        print(f"📊 Mecze zakończone: {stats['finished']}/{stats['total']}")
        
        if stats['finished'] > 0:
            print(f"✅ Trafne: {stats['correct']} ({stats['correct']/stats['finished']*100:.1f}%)")
            print(f"❌ Nietrafne: {stats['incorrect']} ({stats['incorrect']/stats['finished']*100:.1f}%)")
            
            if stats['tennis_total'] > 0:
                tennis_finished = stats['tennis_correct'] + stats['tennis_incorrect']
                if tennis_finished > 0:
                    print(f"🎾 Tenis: {stats['tennis_correct']}/{tennis_finished} ({stats['tennis_correct']/tennis_finished*100:.1f}%)")
            
            if stats['team_total'] > 0:
                team_finished = stats['team_correct'] + stats['team_incorrect']
                if team_finished > 0:
                    print(f"⚽ Drużynowe: {stats['team_correct']}/{team_finished} ({stats['team_correct']/team_finished*100:.1f}%)")
        else:
            print(f"⏳ Żaden mecz się jeszcze nie zakończył - sprawdź później!")
        
        print(f"{'='*70}\n")
        
    finally:
        verifier.close()


if __name__ == '__main__':
    main()

