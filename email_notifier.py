"""
Moduł do wysyłania powiadomień email o kwalifikujących się meczach
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import pandas as pd
from datetime import datetime
import math  # dla sprawdzania NaN

# Konfiguracja SMTP
SMTP_CONFIG = {
    'gmail': {
        'server': 'smtp.gmail.com',
        'port': 587,
        'use_tls': True
    },
    'outlook': {
        'server': 'smtp-mail.outlook.com',
        'port': 587,
        'use_tls': True
    },
    'yahoo': {
        'server': 'smtp.mail.yahoo.com',
        'port': 587,
        'use_tls': True
    }
}

def create_html_email(matches: List[Dict], date: str, sort_by: str = 'time') -> str:
    """
    Tworzy ładny HTML email z listą meczów
    
    Args:
        matches: Lista meczów
        date: Data
        sort_by: 'time' (godzina), 'wins' (liczba wygranych), 'team' (alfabetycznie)
    """
    
    # SORTOWANIE MECZÓW
    sorted_matches = matches.copy()
    
    if sort_by == 'time':
        # Sortuj po godzinie meczu
        def get_time_key(match):
            match_time = match.get('match_time', '')
            if not match_time:
                return '99:99'  # Mecze bez czasu na końcu
            
            # Wyciągnij godzinę z różnych formatów
            import re
            # Format: DD.MM.YYYY HH:MM lub HH:MM
            time_match = re.search(r'(\d{1,2}:\d{2})', match_time)
            if time_match:
                return time_match.group(1)
            return '99:99'
        
        sorted_matches = sorted(sorted_matches, key=get_time_key)
    
    elif sort_by == 'wins':
        # Sortuj po liczbie wygranych (malejąco) - uwzględnij tryb away_team_focus
        def get_wins(match):
            focus_team = match.get('focus_team', 'home')
            if focus_team == 'away':
                return match.get('away_wins_in_h2h_last5', 0)
            else:
                return match.get('home_wins_in_h2h_last5', 0)
        sorted_matches = sorted(sorted_matches, key=get_wins, reverse=True)
    
    elif sort_by == 'team':
        # Sortuj alfabetycznie po nazwie gospodarzy
        sorted_matches = sorted(sorted_matches, key=lambda x: x.get('home_team', '').lower())
    
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .match {{
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
                background-color: #f9f9f9;
            }}
            .match-title {{
                font-size: 18px;
                font-weight: bold;
                color: #2196F3;
            }}
            .match-details {{
                margin: 5px 0;
                color: #666;
            }}
            .match-time {{
                font-size: 20px;
                color: #FF5722;
                font-weight: bold;
            }}
            .stats {{
                background-color: #fff3cd;
                padding: 10px;
                border-radius: 3px;
                margin-top: 10px;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #888;
                font-size: 12px;
            }}
            .h2h-record {{
                color: #4CAF50;
                font-weight: bold;
            }}
            .time-badge {{
                display: inline-block;
                background-color: #FF5722;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                margin-right: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏆 Kwalifikujące się mecze - {date}</h1>
            <p>🎾 Tennis: Advanced scoring (≥50/100) | ⚽ Drużynowe: Gospodarze wygrali ≥60% H2H</p>
            <p style="font-size: 14px; margin-top: 10px;">⏰ Posortowane chronologicznie</p>
        </div>
        
        <div class="content">
            <p>Znaleziono <strong>{len(sorted_matches)}</strong> kwalifikujących się meczów:</p>
    """
    
    for i, match in enumerate(sorted_matches, 1):
        home = match.get('home_team', 'N/A')
        away = match.get('away_team', 'N/A')
        
        # Uwzględnij tryb away_team_focus
        focus_team = match.get('focus_team', 'home')
        if focus_team == 'away':
            wins = match.get('away_wins_in_h2h_last5', 0)
            focused_team_name = away
        else:
            wins = match.get('home_wins_in_h2h_last5', 0)
            focused_team_name = home
        
        match_time = match.get('match_time', 'Brak danych')
        match_url = match.get('match_url', '#')
        
        # Wyciągnij godzinę dla lepszego wyświetlania
        import re
        time_display = match_time
        time_badge = ''
        if match_time and match_time != 'Brak danych':
            time_match = re.search(r'(\d{1,2}:\d{2})', match_time)
            if time_match:
                time_only = time_match.group(1)
                time_badge = f'<span class="time-badge">🕐 {time_only}</span>'
                time_display = match_time
        
        # Sprawdź czy to tenis z advanced scoring (tylko tennis ma pole 'favorite')
        is_tennis = 'favorite' in match
        h2h_info = ''
        form_info = ''
        
        if is_tennis:  # Tennis z advanced scoring
            advanced_score = match.get('advanced_score', 0)
            
            # Wyświetl scoring dla tenisa
            favorite = match.get('favorite', 'unknown')
            if favorite == 'player_a':
                fav_name = home
            elif favorite == 'player_b':
                fav_name = away
            else:
                fav_name = "Równi"
            
            h2h_info = f'<span class="h2h-record">🎾 Score: {advanced_score:.1f}/100 | Faworytem: {fav_name}</span>'
        else:  # Sporty drużynowe (football, basketball, etc.)
            # H2H z win rate
            h2h_count = match.get('h2h_count', 0)
            win_rate = match.get('win_rate', 0.0)
            form_advantage = match.get('form_advantage', False)
            
            # Emoji dla przewagi formy
            advantage_emoji = ' 🔥' if form_advantage else ''
            
            if h2h_count > 0:
                # Dynamiczny komunikat w zależności od focus_team
                if focus_team == 'away':
                    h2h_info = f'<span class="h2h-record">📊 H2H: {away} (goście) wygrał {wins}/{h2h_count} ({win_rate*100:.0f}%){advantage_emoji}</span>'
                else:
                    h2h_info = f'<span class="h2h-record">📊 H2H: {home} wygrał {wins}/{h2h_count} ({win_rate*100:.0f}%){advantage_emoji}</span>'
            else:
                h2h_info = f'<span class="h2h-record">📊 H2H: Brak danych</span>'
            
            # ZAAWANSOWANA FORMA DRUŻYN (3 źródła)
            home_form_overall = match.get('home_form_overall', match.get('home_form', []))
            home_form_home = match.get('home_form_home', [])
            away_form_overall = match.get('away_form_overall', match.get('away_form', []))
            away_form_away = match.get('away_form_away', [])
            
            if home_form_overall or away_form_overall:
                # Funkcja pomocnicza do formatowania formy z emoji
                def format_form_with_emoji(form_list):
                    emoji_map = {'W': '✅', 'L': '❌', 'D': '🟡'}
                    return ' '.join([emoji_map.get(r, r) for r in form_list]) if form_list else 'N/A'
                
                # Formatuj formę
                home_overall_str = format_form_with_emoji(home_form_overall)
                home_home_str = format_form_with_emoji(home_form_home)
                away_overall_str = format_form_with_emoji(away_form_overall)
                away_away_str = format_form_with_emoji(away_form_away)
                
                # Oblicz przewagę
                home_wins = home_form_overall.count('W') if home_form_overall else 0
                away_wins = away_form_overall.count('W') if away_form_overall else 0
                
                form_info = f'''
                    <div style="margin-top: 10px; font-size: 13px; background-color: #F5F9FF; padding: 10px; border-radius: 5px;">
                        <strong>📊 Analiza Formy (ostatnie 5 meczów):</strong>
                        <div style="margin-top: 6px;">
                            <div style="margin-bottom: 4px;">
                                🏠 <strong>{home}:</strong>
                            </div>
                            <div style="margin-left: 20px; font-size: 12px;">
                                • Ogółem: <span style="background-color: #E8F5E9; padding: 2px 6px; border-radius: 3px;">{home_overall_str}</span>
                                {f'<br>• U siebie: <span style="background-color: #E8F5E9; padding: 2px 6px; border-radius: 3px;">{home_home_str}</span>' if home_form_home else ''}
                            </div>
                        </div>
                        <div style="margin-top: 8px;">
                            <div style="margin-bottom: 4px;">
                                ✈️ <strong>{away}:</strong>
                            </div>
                            <div style="margin-left: 20px; font-size: 12px;">
                                • Ogółem: <span style="background-color: #FFEBEE; padding: 2px 6px; border-radius: 3px;">{away_overall_str}</span>
                                {f'<br>• Na wyjeździe: <span style="background-color: #FFEBEE; padding: 2px 6px; border-radius: 3px;">{away_away_str}</span>' if away_form_away else ''}
                            </div>
                        </div>
                        {f'<div style="margin-top: 8px; padding: 6px; background-color: #FFF3CD; border-radius: 3px; font-weight: bold;">🔥 {focused_team_name} ma przewagę w formie!</div>' if form_advantage else ''}
                    </div>
                '''
        
        # Kursy bukmacherskie (jeśli dostępne)
        odds_html = ''
        home_odds = match.get('home_odds')
        away_odds = match.get('away_odds')
        
        # POPRAWKA: Sprawdź czy kursy są liczbami (nie NaN/None)
        # pandas NaN przechodzi przez `if home_odds and away_odds` i pokazuje się jako "nan"!
        has_valid_odds = False
        try:
            if home_odds is not None and away_odds is not None:
                # Sprawdź czy to liczby (nie NaN)
                if not (pd.isna(home_odds) or pd.isna(away_odds)):
                    # Dodatkowo sprawdź czy są w sensownym zakresie
                    if 1.0 <= float(home_odds) <= 100.0 and 1.0 <= float(away_odds) <= 100.0:
                        has_valid_odds = True
        except (ValueError, TypeError):
            pass
        
        if has_valid_odds:
            odds_html = f'''
                <div class="match-details" style="background-color: #FFF9E6; padding: 8px; border-radius: 5px; margin-top: 8px;">
                    🎲 <strong>Kursy:</strong> {home} <span style="background-color: #FFD700; padding: 2px 6px; border-radius: 3px; font-weight: bold;">{home_odds:.2f}</span> | {away} <span style="background-color: #FFD700; padding: 2px 6px; border-radius: 3px; font-weight: bold;">{away_odds:.2f}</span>
                    <br><em style="font-size: 11px; color: #666;">⚠️ Kursy są wyłącznie informacją dodatkową, nie wpływają na scoring</em>
                </div>
            '''
        
        html += f"""
            <div class="match">
                <div style="margin-bottom: 10px;">
                    {time_badge}
                </div>
                <div class="match-title">
                    #{i}. {home} vs {away}
                </div>
                <div class="match-details">
                    📅 Data: <strong>{time_display}</strong>
                </div>
                <div class="stats">
                    {h2h_info}
                    {form_info}
                </div>
                {odds_html}
                <div class="match-details">
                    🔗 <a href="{match_url}">Zobacz mecz na Livesport</a>
                </div>
            </div>
        """
    
    html += """
        </div>
        
        <div class="footer">
            <p>📧 Wygenerowano automatycznie przez Livesport H2H Scraper v6.1</p>
            <p>🔔 <strong>Kryteria kwalifikacji:</strong></p>
            <p>🎾 <strong>Tennis:</strong> Multi-factor scoring (H2H + ranking + forma + powierzchnia) ≥ 50/100</p>
            <p>⚽ <strong>Sporty drużynowe:</strong></p>
            <p style="margin-left: 20px;">
                1️⃣ Gospodarze wygrali ≥60% H2H<br>
                2️⃣ <strong>ZAAWANSOWANA ANALIZA FORMY (3 źródła):</strong><br>
                &nbsp;&nbsp;&nbsp;&nbsp;• Forma ogólna (ostatnie 5 meczów)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;• Forma gospodarzy U SIEBIE<br>
                &nbsp;&nbsp;&nbsp;&nbsp;• Forma gości NA WYJEŹDZIE<br>
                3️⃣ Gospodarze w dobrej formie + Goście w słabej = 🔥 Przewaga!
            </p>
        </div>
    </body>
    </html>
    """
    
    return html


def send_email_notification(
    csv_file: str,
    to_email: str,
    from_email: str,
    password: str,
    provider: str = 'gmail',
    subject: str = None,
    sort_by: str = 'time',
    only_form_advantage: bool = False,
    skip_no_odds: bool = False
):
    """
    Wysyła email z powiadomieniem o kwalifikujących się meczach
    
    Args:
        csv_file: Ścieżka do pliku CSV z wynikami
        to_email: Email odbiorcy
        from_email: Email nadawcy
        password: Hasło do email (lub App Password dla Gmail)
        provider: 'gmail', 'outlook', lub 'yahoo'
        subject: Opcjonalny tytuł emaila
        sort_by: Sortowanie: 'time' (godzina), 'wins' (wygrane), 'team' (alfabetycznie)
        only_form_advantage: Wysyłaj tylko mecze z przewagą formy gospodarzy (🔥)
        skip_no_odds: Pomijaj mecze bez kursów bukmacherskich
    """
    
    # Wczytaj dane
    print(f"Wczytuje dane z: {csv_file}")
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    # Filtruj kwalifikujące się mecze
    qualified = df[df['qualifies'] == True]
    
    # OPCJA 1: Filtruj tylko mecze z przewagą formy
    if only_form_advantage:
        print("🔥 TRYB: Tylko mecze z PRZEWAGĄ FORMY (gospodarzy/gości)")
        if 'form_advantage' in qualified.columns:
            qualified = qualified[qualified['form_advantage'] == True]
            print(f"   Przefiltrowano do meczów z przewagą formy")
        else:
            print("   ⚠️ Brak kolumny 'form_advantage' w danych - pokazuję wszystkie kwalifikujące")
    
    # OPCJA 2: Pomijaj mecze bez kursów
    if skip_no_odds:
        print("💰 TRYB: Pomijam mecze BEZ KURSÓW bukmacherskich")
        before_count = len(qualified)
        # Filtruj mecze, które mają OBA kursy (home_odds i away_odds)
        if 'home_odds' in qualified.columns and 'away_odds' in qualified.columns:
            qualified = qualified[(qualified['home_odds'].notna()) & (qualified['away_odds'].notna())]
            skipped = before_count - len(qualified)
            print(f"   Pominięto {skipped} meczów bez kursów")
        else:
            print("   ⚠️ Brak kolumn z kursami w danych - pokazuję wszystkie mecze")
    
    if len(qualified) == 0:
        messages = []
        if only_form_advantage:
            messages.append("PRZEWAGĄ FORMY")
        if skip_no_odds:
            messages.append("KURSAMI")
        
        print("="*70)
        print("⚠️  BRAK ZDARZEŃ DO WYSŁANIA")
        print("="*70)
        if messages:
            print(f"📊 Powód: Brak kwalifikujących się meczów z {' i '.join(messages)}")
        else:
            print(f"📊 Powód: Brak kwalifikujących się meczów")
        print(f"📄 CSV: {csv_file}")
        print(f"📧 Email: {to_email}")
        print("="*70)
        return

    # Policz mecze z kursami i bez (tylko jeśli nie pomijamy meczów bez kursów)
    if not skip_no_odds:
        with_odds = qualified[(qualified['home_odds'].notna()) & (qualified['away_odds'].notna())]
        without_odds = len(qualified) - len(with_odds)
    else:
        without_odds = 0  # Wszystkie mają kursy, bo filtrujemy

    # Komunikat o znalezionych meczach
    msg_parts = []
    if only_form_advantage:
        msg_parts.append("z PRZEWAGĄ FORMY 🔥")
    if skip_no_odds:
        msg_parts.append("z KURSAMI 💰")
    
    if msg_parts:
        print(f"Znaleziono {len(qualified)} kwalifikujacych sie meczow {' i '.join(msg_parts)}")
    else:
        print(f"Znaleziono {len(qualified)} kwalifikujacych sie meczow")
    
    if without_odds > 0 and not skip_no_odds:
        print(f"   W tym {without_odds} meczow bez kursow bukmacherskich")
    
    # Przygotuj dane
    matches = qualified.to_dict('records')
    date = datetime.now().strftime('%Y-%m-%d')
    
    if subject is None:
        subject_parts = []
        if only_form_advantage:
            subject_parts.append("🔥 PRZEWAGA FORMY")
        if skip_no_odds:
            subject_parts.append("💰 Z KURSAMI")
        
        if subject_parts:
            subject = f"{len(qualified)} meczów ({' + '.join(subject_parts)}) - {date}"
        else:
            subject = f"{len(qualified)} kwalifikujacych sie meczow - {date}"
    
    # Utwórz wiadomość
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    # Dodaj treść HTML
    html_content = create_html_email(matches, date, sort_by=sort_by)
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    # Wyślij email
    try:
        print(f"\nWysylam email do: {to_email}")
        print(f"   Provider: {provider}")
        
        smtp_config = SMTP_CONFIG[provider]
        
        with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
            if smtp_config['use_tls']:
                server.starttls()
            
            server.login(from_email, password)
            server.send_message(msg)
        
        print("Email wyslany pomyslnie!")
        
    except Exception as e:
        print(f"Blad wysylania emaila: {e}")
        print("\nWSKAZOWKI:")
        print("   - Dla Gmail: uzyj App Password (nie zwyklego hasla)")
        print("     Jak uzyskac: https://myaccount.google.com/apppasswords")
        print("   - Sprawdz czy SMTP jest wlaczony w ustawieniach konta")
        print("   - Sprawdz dane logowania")


def main():
    """Przykład użycia"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Wyślij powiadomienie email o kwalifikujących się meczach')
    parser.add_argument('--csv', required=True, help='Plik CSV z wynikami')
    parser.add_argument('--to', required=True, help='Email odbiorcy')
    parser.add_argument('--from-email', required=True, help='Email nadawcy')
    parser.add_argument('--password', required=True, help='Hasło email (lub App Password)')
    parser.add_argument('--provider', default='gmail', choices=['gmail', 'outlook', 'yahoo'], 
                       help='Provider email')
    parser.add_argument('--subject', help='Opcjonalny tytuł emaila')
    parser.add_argument('--sort', default='time', choices=['time', 'wins', 'team'],
                       help='Sortowanie: time (godzina), wins (wygrane), team (alfabetycznie)')
    parser.add_argument('--only-form-advantage', action='store_true',
                       help='🔥 Wyślij tylko mecze z PRZEWAGĄ FORMY gospodarzy')
    parser.add_argument('--skip-no-odds', action='store_true',
                       help='💰 Pomijaj mecze BEZ KURSÓW bukmacherskich')
    
    args = parser.parse_args()
    
    send_email_notification(
        csv_file=args.csv,
        to_email=args.to,
        from_email=args.from_email,
        password=args.password,
        provider=args.provider,
        subject=args.subject,
        sort_by=args.sort,
        only_form_advantage=args.only_form_advantage,
        skip_no_odds=args.skip_no_odds
    )


if __name__ == '__main__':
    main()

