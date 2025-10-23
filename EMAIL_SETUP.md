# 📧 Instrukcja: Wysyłanie powiadomień email

## 🎯 Co robi ta funkcjonalność?

Automatycznie wysyła **ładny email HTML** z listą kwalifikujących się meczów:
- ✅ Nazwy drużyn
- ✅ Data i godzina meczu
- ✅ Statystyki H2H
- ✅ Link do meczu na Livesport

---

## 🚀 SZYBKI START (3 kroki)

### Krok 1: Uzyskaj hasło do emaila

#### Dla **Gmail** (ZALECANE):
1. Wejdź na: https://myaccount.google.com/apppasswords
2. Zaloguj się do Google
3. Utwórz nowe hasło aplikacji:
   - Nazwa: "Livesport Scraper"
   - Skopiuj wygenerowane 16-znakowe hasło
4. **To hasło użyjesz zamiast zwykłego hasła!**

#### Dla **Outlook/Hotmail**:
- Możesz użyć zwykłego hasła
- Upewnij się że SMTP jest włączony w ustawieniach

#### Dla **Yahoo**:
- Musisz włączyć "Less secure apps"
- Lub użyj App Password

---

### Krok 2: Wybierz sposób użycia

Masz **3 opcje**:

---

## 📋 OPCJA 1: Scraping + Email w jednym (NAJPROSTSZE)

Jeden skrypt robi wszystko: scrapuje mecze i od razu wysyła email!

```bash
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football \
  --to twoj_email@gmail.com \
  --from-email twoj_email@gmail.com \
  --password "twoje_app_password" \
  --headless
```

### ⏰ NOWOŚĆ: Automatyczne sortowanie!

Mecze są **automatycznie sortowane po godzinie** (od najwcześniejszych)!

Możesz zmienić sortowanie:
```bash
# Po godzinie (domyślnie)
--sort time

# Po liczbie wygranych (od najwięcej do najmniej)
--sort wins

# Alfabetycznie po nazwie gospodarzy
--sort team
```

**Przykłady:**

```bash
# Test na 20 meczach
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "abc xyz 123 456" \
  --max-matches 20 \
  --headless

# Wiele sportów
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football basketball volleyball \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "abc xyz 123 456" \
  --headless

# Bez headless (zobaczysz przeglądarkę)
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "abc xyz 123 456"

# Sortowanie po liczbie wygranych (najlepsze mecze na górze)
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "abc xyz 123 456" \
  --sort wins \
  --headless
```

---

## 📋 OPCJA 2: Wyślij email z istniejącego CSV

Masz już plik CSV i chcesz tylko wysłać email?

### Sposób A: Z linii komend

```bash
python email_notifier.py \
  --csv outputs/livesport_h2h_2025-10-05_football.csv \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "abc xyz 123 456" \
  --provider gmail
```

### Sposób B: Edytuj i uruchom przykład

1. Otwórz `send_email_example.py`
2. Wypełnij swoimi danymi:

```python
CSV_FILE = 'outputs/livesport_h2h_2025-10-05_football.csv'
TO_EMAIL = 'twoj@gmail.com'
FROM_EMAIL = 'twoj@gmail.com'
PASSWORD = 'twoje_app_password_tutaj'
PROVIDER = 'gmail'
```

3. Uruchom:
```bash
python send_email_example.py
```

---

## 📋 OPCJA 3: Użyj w swoim skrypcie Python

```python
from email_notifier import send_email_notification

send_email_notification(
    csv_file='outputs/livesport_h2h_2025-10-05_football.csv',
    to_email='odbiorca@gmail.com',
    from_email='nadawca@gmail.com',
    password='twoje_app_password',
    provider='gmail',
    subject='🏆 Dzisiejsze mecze!'
)
```

---

## 📧 Jak wygląda email?

Email jest w formacie **HTML** i zawiera:

```
┌─────────────────────────────────────┐
│ 🏆 Kwalifikujące się mecze - 2025-10-05 │
│ Gospodarze wygrali ≥2 razy w ostatnich 5 H2H │
│ ⏰ Posortowane chronologicznie       │
└─────────────────────────────────────┘

Znaleziono 26 kwalifikujących się meczów:

┌─────────────────────────────────────┐
│ [🕐 15:00]                          │
│ #1. Newcastle vs Nottingham         │
│ 📅 Data: 05.10.2025 15:00           │
│ 📊 H2H: Newcastle wygrał 4/5 ostatnich meczów │
│ 🔗 Zobacz mecz na Livesport          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ [🕐 17:00]                          │
│ #2. Lyon vs Toulouse                │
│ 📅 Data: 05.10.2025 17:00           │
│ 📊 H2H: Lyon wygrał 4/5 ostatnich meczów │
│ 🔗 Zobacz mecz na Livesport          │
└─────────────────────────────────────┘

...
```

---

## ⚠️ Rozwiązywanie problemów

### Problem: "Authentication failed" (Gmail)

**Rozwiązanie:**
- Upewnij się że używasz **App Password**, nie zwykłego hasła!
- Uzyskaj tutaj: https://myaccount.google.com/apppasswords
- Jeśli nie masz opcji App Passwords, włącz weryfikację dwuetapową

### Problem: "SMTPAuthenticationError"

**Rozwiązanie:**
- Sprawdź dane logowania
- Dla Gmail: użyj App Password (16 znaków)
- Dla Outlook: sprawdź czy SMTP jest włączony
- Spróbuj innego providera

### Problem: "SMTPServerDisconnected"

**Rozwiązanie:**
- Sprawdź połączenie internetowe
- Firewall może blokować port 587
- Spróbuj z innej sieci

### Problem: Email nie dociera

**Rozwiązanie:**
- Sprawdź folder SPAM
- Dodaj adres nadawcy do kontaktów
- Poczekaj kilka minut (opóźnienie)

---

## 🔒 Bezpieczeństwo

### ✅ DOBRZE:
- Używaj App Password dla Gmail
- Przechowuj hasło w zmiennych środowiskowych
- Nie commituj haseł do Git

### ❌ ŹLE:
- Nie używaj zwykłego hasła Gmail
- Nie wklejaj hasła do kodu w repozytorium
- Nie udostępniaj hasła innym

### 💡 Przechowywanie hasła bezpiecznie:

**Windows:**
```powershell
$env:EMAIL_PASSWORD="twoje_haslo"
python scrape_and_notify.py ... --password %EMAIL_PASSWORD%
```

**Linux/Mac:**
```bash
export EMAIL_PASSWORD="twoje_haslo"
python scrape_and_notify.py ... --password $EMAIL_PASSWORD
```

---

## 🎨 Dostosowanie emaila

Możesz edytować wygląd emaila w pliku `email_notifier.py`:

- **Kolory**: Zmień `#4CAF50` na inny kolor
- **Czcionka**: Zmień `Arial, sans-serif`
- **Treść**: Edytuj funkcję `create_html_email()`

---

## 📊 Przykłady użycia w praktyce

### Codzienne powiadomienia (Windows Task Scheduler):

1. Utwórz plik `daily_scrape.bat`:
```batch
@echo off
cd C:\Users\jakub\Downloads\Flashscore2
python scrape_and_notify.py ^
  --date 2025-10-05 ^
  --sports football ^
  --to twoj@gmail.com ^
  --from-email twoj@gmail.com ^
  --password "abc xyz 123 456" ^
  --headless
```

2. Dodaj do Task Scheduler:
   - Otwórz Task Scheduler
   - Utwórz nowe zadanie
   - Trigger: Codziennie o 9:00
   - Action: Uruchom `daily_scrape.bat`

### Codzienne powiadomienia (Linux cron):

```bash
# Edytuj crontab
crontab -e

# Dodaj linię (codziennie o 9:00)
0 9 * * * cd /path/to/Flashscore2 && python scrape_and_notify.py --date $(date +\%Y-\%m-\%d) --sports football --to twoj@gmail.com --from-email twoj@gmail.com --password "haslo" --headless
```

---

## 🆘 Pomoc

Jeśli coś nie działa:
1. Uruchom bez `--headless` aby zobaczyć co się dzieje
2. Sprawdź czy masz najnowsze pakiety: `pip install -r requirements.txt`
3. Przetestuj najpierw z `--max-matches 5`
4. Sprawdź logi błędów

---

**Gotowy do testowania?** 🚀

Zacznij od prostego testu:

```bash
python scrape_and_notify.py \
  --date 2025-10-05 \
  --sports football \
  --to twoj@gmail.com \
  --from-email twoj@gmail.com \
  --password "twoje_app_password" \
  --max-matches 10 \
  --headless
```

To przetworzy tylko 10 meczów i wyśle testowy email!

