"""
PROSTY SKRYPT: Wysyła email z istniejącego pliku CSV (bez ponownego scrapowania)
"""

import argparse
from email_notifier import send_email_notification


def main():
    parser = argparse.ArgumentParser(
        description='Wyślij email z istniejącego pliku CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:

  # Podstawowy: wyślij z pliku CSV
  python resend_from_csv.py --csv outputs/livesport_h2h_2025-10-09_football_EMAIL.csv \\
    --to twoj@email.com --from jakub.majka.zg@gmail.com --password "haslo"

  # 🔥 Tylko mecze z przewagą formy + sortowanie po czasie
  python resend_from_csv.py --csv outputs/livesport_h2h_2025-10-09_football_EMAIL.csv \\
    --to twoj@email.com --from jakub.majka.zg@gmail.com --password "haslo" \\
    --only-form-advantage --sort time

  # 💰 Tylko mecze z kursami
  python resend_from_csv.py --csv outputs/livesport_h2h_2025-10-09_football_EMAIL.csv \\
    --to twoj@email.com --from jakub.majka.zg@gmail.com --password "haslo" \\
    --skip-no-odds --sort wins
        """
    )
    
    parser.add_argument('--csv', required=True, help='Ścieżka do pliku CSV')
    parser.add_argument('--to', required=True, help='Email odbiorcy')
    parser.add_argument('--from', dest='from_email', required=True, help='Email nadawcy')
    parser.add_argument('--password', required=True, help='Hasło email (App Password dla Gmail)')
    parser.add_argument('--provider', default='gmail', choices=['gmail', 'outlook', 'yahoo'],
                       help='Provider email (domyślnie: gmail)')
    parser.add_argument('--subject', default=None, help='Opcjonalny tytuł emaila')
    parser.add_argument('--sort', default='time', choices=['time', 'wins', 'team'],
                       help='Sortowanie: time (godzina), wins (wygrane), team (alfabetycznie)')
    parser.add_argument('--only-form-advantage', action='store_true',
                       help='🔥 Tylko mecze z PRZEWAGĄ FORMY gospodarzy')
    parser.add_argument('--skip-no-odds', action='store_true',
                       help='💰 Pomijaj mecze BEZ KURSÓW bukmacherskich')
    
    args = parser.parse_args()
    
    print("="*70)
    print("📧 WYSYŁANIE EMAILA Z ISTNIEJĄCEGO PLIKU CSV")
    print("="*70)
    print(f"📂 Plik: {args.csv}")
    print(f"📧 Do: {args.to}")
    print(f"📧 Z: {args.from_email}")
    print(f"🔧 Provider: {args.provider}")
    print(f"📊 Sortowanie: {args.sort}")
    if args.only_form_advantage:
        print("🔥 Filtr: Tylko PRZEWAGA FORMY")
    if args.skip_no_odds:
        print("💰 Filtr: Tylko mecze Z KURSAMI")
    print("="*70)
    
    # Wyślij email
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
    
    print("\n✅ Email wysłany pomyślnie!")


if __name__ == '__main__':
    main()





