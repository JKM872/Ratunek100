"""
Skrypt do wysyłania emaili z istniejącego pliku CSV (bez ponownego scrapingu)
"""

import argparse
from email_notifier import send_email_notification

def main():
    parser = argparse.ArgumentParser(description='Wyślij email z wynikami z pliku CSV')
    parser.add_argument('--csv', required=True, help='Ścieżka do pliku CSV z wynikami')
    parser.add_argument('--to', required=True, help='Email odbiorcy')
    parser.add_argument('--from-email', required=True, help='Email nadawcy')
    parser.add_argument('--password', required=True, help='Hasło email')
    parser.add_argument('--provider', default='gmail', choices=['gmail', 'outlook', 'yahoo'], help='Provider email')
    parser.add_argument('--sort', default='time', choices=['time', 'wins', 'team'], help='Sortowanie')
    parser.add_argument('--only-form-advantage', action='store_true', help='Wysyłaj tylko mecze z przewagą formy')
    parser.add_argument('--skip-no-odds', action='store_true', help='Pomijaj mecze bez kursów')
    
    args = parser.parse_args()
    
    print("="*70)
    print("📧 WYSYŁANIE EMAILA Z CSV")
    print("="*70)
    print(f"📄 CSV: {args.csv}")
    print(f"📧 Do: {args.to}")
    print(f"🔧 Provider: {args.provider}")
    if args.only_form_advantage:
        print(f"🔥 TRYB: Tylko mecze z PRZEWAGĄ FORMY")
    if args.skip_no_odds:
        print(f"💰 TRYB: Pomijam mecze BEZ KURSÓW")
    print("="*70)
    
    # Wyślij email używając istniejącego pliku CSV
    send_email_notification(
        csv_file=args.csv,
        to_email=args.to,
        from_email=args.from_email,
        password=args.password,
        provider=args.provider,
        sort_by=args.sort,
        only_form_advantage=args.only_form_advantage,
        skip_no_odds=args.skip_no_odds
    )
    
    print("✅ Email wysłany!")

if __name__ == '__main__':
    main()

