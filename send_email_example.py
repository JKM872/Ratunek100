"""
PRZYKŁAD: Jak wysłać email z powiadomieniami o meczach
"""

from email_notifier import send_email_notification

# ============================================================================
# KONFIGURACJA - WYPEŁNIJ SWOIMI DANYMI
# ============================================================================

# Ścieżka do pliku CSV z wynikami scrapera
CSV_FILE = 'outputs/livesport_h2h_2025-10-05_football.csv'

# Email odbiorcy (na który chcesz dostać powiadomienie)
TO_EMAIL = 'twoj_email@gmail.com'

# Email nadawcy (z którego będziesz wysyłać)
FROM_EMAIL = 'twoj_email@gmail.com'

# Hasło do emaila
# ⚠️ DLA GMAIL: Użyj "App Password" zamiast zwykłego hasła!
# Jak uzyskać: https://myaccount.google.com/apppasswords
PASSWORD = 'twoje_haslo_lub_app_password'

# Provider: 'gmail', 'outlook', lub 'yahoo'
PROVIDER = 'gmail'

# Opcjonalny tytuł emaila
SUBJECT = '🏆 Dzisiejsze kwalifikujące się mecze - Livesport H2H'

# ============================================================================
# URUCHOMIENIE
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("📧 WYSYŁANIE POWIADOMIENIA EMAIL")
    print("="*70)
    print(f"\n📂 Plik CSV: {CSV_FILE}")
    print(f"📧 Do: {TO_EMAIL}")
    print(f"📤 Od: {FROM_EMAIL}")
    print(f"🔧 Provider: {PROVIDER}")
    print("\n" + "="*70)
    
    send_email_notification(
        csv_file=CSV_FILE,
        to_email=TO_EMAIL,
        from_email=FROM_EMAIL,
        password=PASSWORD,
        provider=PROVIDER,
        subject=SUBJECT
    )
    
    print("\n✅ Gotowe!")

