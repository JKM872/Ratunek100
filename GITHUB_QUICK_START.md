# ⚡ GitHub Actions - Quick Start (5 minut)

## 🎯 TO ZROBISZ

1. Wrzucisz kod na GitHub (5 min)
2. Dodasz hasło email (1 min)
3. Gotowe! Scraper działa 24/7 🎉

---

## 📝 KROK 1: Stwórz repo (2 min)

1. Wejdź: https://github.com/JKM2828
2. Kliknij: **New** (zielony przycisk)
3. Wypełnij:
   ```
   Repository name: volleyball-scraper
   ✅ Private
   ✅ Add a README file
   ```
4. Kliknij: **Create repository**

---

## 📤 KROK 2: Upload plików (3 min)

### **Opcja A: Przez przeglądarkę** ⭐ ŁATWIEJSZE

1. W repo kliknij: **Add file** → **Upload files**
2. Przeciągnij **WSZYSTKIE** pliki z `C:\Users\jakub\Downloads\Ratowanie\`
   - ⚠️ WAŻNE: Przeciągnij cały folder `.github` (może być ukryty!)
3. Commit: `Initial commit`
4. Kliknij: **Commit changes**

### **Opcja B: Przez git**

W PowerShell w folderze `C:\Users\jakub\Downloads\Ratowanie\`:

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/JKM2828/volleyball-scraper.git
git push -u origin main
```

---

## 🔒 KROK 3: Dodaj hasło email (1 min)

1. W repo: **Settings** → **Secrets and variables** → **Actions**
2. Kliknij: **New repository secret**
3. Wypełnij:
   ```
   Name: EMAIL_PASSWORD
   Secret: vurb tcai zaaq itjx
   ```
4. Kliknij: **Add secret**

---

## 🚀 KROK 4: Test! (1 min)

1. Zakładka: **Actions**
2. Wybierz: **All Sports Scraping (Manual)**
3. Kliknij: **Run workflow** → **Run workflow**
4. Poczekaj 3-5 minut
5. ✅ Sprawdź email!

---

## ✅ GOTOWE!

**Od teraz:**
- 🕐 Codziennie o 11:00 automatyczny scraping
- 📧 Email z wynikami na `jakub.majka.zg@gmail.com`
- 💻 Działa bez Twojego laptopa
- 💰 Całkowicie za darmo (GitHub Student Pack)

**Więcej opcji?** Zobacz: `GITHUB_ACTIONS_SETUP.md`

---

## ⚙️ ZMIEŃ USTAWIENIA

### Zmień godzinę scrapingu

Edytuj: `.github/workflows/daily-scraping.yml`

```yaml
cron: '0 9 * * *'  # 11:00 PL
# Zmień na:
cron: '0 7 * * *'  # 09:00 PL
cron: '0 10 * * *' # 12:00 PL
```

### Dodaj więcej sportów

Edytuj: `.github/workflows/daily-scraping.yml`

```yaml
--sports volleyball \
# Zmień na:
--sports volleyball basketball handball \
```

### Zmień email

Edytuj: `.github/workflows/daily-scraping.yml`

```yaml
--to jakub.majka.zg@gmail.com \
# Zmień na:
--to twoj.nowy@email.com \
```

---

## 🆘 PROBLEMY?

**Email nie przychodzi?**
- Sprawdź SPAM
- Zobacz logi w Actions
- Sprawdź czy są mecze spełniające kryteria

**Workflow nie działa?**
- Actions → Enable workflow
- Sprawdź czy hasło EMAIL_PASSWORD jest dodane

**Szczegóły:** `GITHUB_ACTIONS_SETUP.md`

