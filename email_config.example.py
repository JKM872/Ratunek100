"""
PRZYKŁADOWY PLIK KONFIGURACYJNY DLA EMAILA

1. Skopiuj ten plik jako 'email_config.py'
2. Wypełnij swoimi danymi
3. Użyj w skryptach

WAŻNE: NIE commituj email_config.py do Git!
(Jest już w .gitignore)
"""

# ============================================================================
# KONFIGURACJA EMAIL
# ============================================================================

# Email odbiorcy (na który chcesz otrzymywać powiadomienia)
TO_EMAIL = 'your_email@gmail.com'

# Email nadawcy (z którego będziesz wysyłać)
FROM_EMAIL = 'your_email@gmail.com'

# Hasło do emaila
# ⚠️ DLA GMAIL: Użyj "App Password" (nie zwykłego hasła!)
#    Jak uzyskać: https://myaccount.google.com/apppasswords
PASSWORD = 'your_password_or_app_password'

# Provider: 'gmail', 'outlook', lub 'yahoo'
PROVIDER = 'gmail'

# ============================================================================
# OPCJE SCRAPOWANIA
# ============================================================================

# Domyślne sporty do scrapowania
DEFAULT_SPORTS = ['football']

# Maksymalna liczba meczów (None = bez limitu)
MAX_MATCHES = None  # Zmień na liczbę (np. 50) dla testów

# Tryb headless (True = bez wyświetlania przeglądarki)
HEADLESS = True

# ============================================================================
# OPCJE EMAILA
# ============================================================================

# Szablon tytułu emaila
# Dostępne zmienne: {count}, {date}
EMAIL_SUBJECT_TEMPLATE = '🏆 {count} kwalifikujących się meczów - {date}'

# Czy wysyłać email jeśli nie ma kwalifikujących się meczów?
SEND_EMPTY_EMAIL = False

