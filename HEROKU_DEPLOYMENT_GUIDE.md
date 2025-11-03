# 🚀 HEROKU DEPLOYMENT GUIDE
## Wdrożenie aplikacji UI na Heroku

---

## ✅ PRZYGOTOWANIE - GOTOWE!

Wszystkie pliki zostały przygotowane i wypushowane na GitHub:

- ✅ `Procfile` - komenda startowa dla Heroku
- ✅ `.gitignore` - wykluczenie node_modules i plików lokalnych
- ✅ `package.json` - zaktualizowany z Node 18.x
- ✅ Commit i push na GitHub

---

## 📋 KROK PO KROKU - Deployment na Heroku

### **KROK 1: Zainstaluj Heroku CLI**

**Windows:**
```powershell
# Pobierz instalator
# https://devcenter.heroku.com/articles/heroku-cli

# LUB przez Chocolatey:
choco install heroku-cli
```

**Sprawdź instalację:**
```powershell
heroku --version
# Powinno zwrócić: heroku/8.x.x win32-x64 node-v18.x.x
```

---

### **KROK 2: Zaloguj się do Heroku**

```powershell
heroku login
```

- Otworzy się przeglądarka
- Zaloguj się na swoje konto Heroku
- Potwierdź w terminalu

---

### **KROK 3: Stwórz aplikację na Heroku**

```powershell
# Z folderu głównego repo
cd C:\Users\jakub\Downloads\Ratowanie

# Stwórz nową aplikację (wybierz własną nazwę!)
heroku create livesport-scraper-api

# LUB jeśli chcesz konkretną nazwę:
heroku create twoja-nazwa-app
```

**Output:**
```
Creating ⬢ livesport-scraper-api... done
https://livesport-scraper-api.herokuapp.com/ | https://git.heroku.com/livesport-scraper-api.git
```

**ZAPISZ TEN URL!** Będzie potrzebny w GitHub Secrets.

---

### **KROK 4: Ustaw Config Vars (zmienne środowiskowe)**

```powershell
# Ustaw API Key (zmień na własny!)
heroku config:set SCRAPER_API_KEY=super-secret-key-xyz-12345 -a livesport-scraper-api

# Ustaw tryb produkcyjny
heroku config:set NODE_ENV=production -a livesport-scraper-api

# Sprawdź czy się zapisało
heroku config -a livesport-scraper-api
```

**Oczekiwany output:**
```
=== livesport-scraper-api Config Vars
NODE_ENV:         production
SCRAPER_API_KEY:  super-secret-key-xyz-12345
```

---

### **KROK 5: Skonfiguruj Git Subtree (ważne!)**

Ponieważ aplikacja jest w podfolderze `example_ui_app`, używamy git subtree:

```powershell
# Dodaj remote Heroku
heroku git:remote -a livesport-scraper-api

# Sprawdź remote
git remote -v
```

Powinieneś zobaczyć:
```
heroku  https://git.heroku.com/livesport-scraper-api.git (fetch)
heroku  https://git.heroku.com/livesport-scraper-api.git (push)
origin  https://github.com/JKM872/Ratunek100.git (fetch)
origin  https://github.com/JKM872/Ratunek100.git (push)
```

---

### **KROK 6: Deploy na Heroku (subtree push)**

```powershell
# Push TYLKO folderu example_ui_app na Heroku
git subtree push --prefix example_ui_app heroku main

# LUB jeśli wystąpi błąd z историą, użyj force:
git push heroku `git subtree split --prefix example_ui_app main`:main --force
```

**Oczekiwany output:**
```
remote: Compressing source files... done.
remote: Building source:
remote: 
remote: -----> Building on the Heroku-22 stack
remote: -----> Determining which buildpack to use for this app
remote: -----> Node.js app detected
remote: 
remote: -----> Creating runtime environment
remote:        NPM_CONFIG_LOGLEVEL=error
remote:        NODE_VERBOSE=false
remote:        NODE_ENV=production
remote:        NODE_MODULES_CACHE=true
remote: 
remote: -----> Installing binaries
remote:        engines.node (package.json):  18.x
remote:        engines.npm (package.json):   unspecified (use default)
remote:        
remote:        Resolving node version 18.x...
remote:        Downloading and installing node 18.19.0...
remote:        Using default npm version: 10.2.3
remote: 
remote: -----> Installing dependencies
remote:        Installing node modules
remote:        added 120 packages, and audited 121 packages in 5s
remote: 
remote: -----> Build succeeded!
remote: -----> Discovering process types
remote:        Procfile declares types -> web
remote: 
remote: -----> Compressing...
remote:        Done: 45.2M
remote: -----> Launching...
remote:        Released v3
remote:        https://livesport-scraper-api.herokuapp.com/ deployed to Heroku
remote: 
remote: Verifying deploy... done.
```

---

### **KROK 7: Test aplikacji**

```powershell
# Otwórz aplikację w przeglądarce
heroku open -a livesport-scraper-api

# LUB test przez curl
curl https://livesport-scraper-api.herokuapp.com/api/health
```

**Oczekiwana odpowiedź:**
```json
{
  "status": "ok",
  "message": "Aplikacja UI działa!",
  "timestamp": "2025-11-03T12:00:00.000Z",
  "database": "C:\\app\\data\\matches.db"
}
```

---

### **KROK 8: Sprawdź logi (jeśli coś nie działa)**

```powershell
# Podgląd logów w czasie rzeczywistym
heroku logs --tail -a livesport-scraper-api

# Ostatnie 100 linii
heroku logs -n 100 -a livesport-scraper-api
```

---

### **KROK 9: Zaktualizuj GitHub Secrets**

1. Wejdź: https://github.com/JKM872/Ratunek100/settings/secrets/actions

2. Zaktualizuj/Dodaj 2 secrets:

   **Secret 1: APP_URL**
   ```
   Name: APP_URL
   Secret: https://livesport-scraper-api.herokuapp.com
   ```

   **Secret 2: APP_API_KEY**
   ```
   Name: APP_API_KEY
   Secret: super-secret-key-xyz-12345
   ```
   (Ten sam co w Config Vars!)

3. Kliknij **Update secret** / **Add secret**

---

### **KROK 10: Test GitHub Actions → Heroku**

```powershell
# Lokalny test z prawdziwym URL
python scrape_and_notify.py `
  --date 2025-10-26 `
  --sports football `
  --to jakub.majka.zg@gmail.com `
  --from-email jakub.majka.zg@gmail.com `
  --password "vurb tcai zaaq itjx" `
  --headless `
  --max-matches 5 `
  --app-url https://livesport-scraper-api.herokuapp.com `
  --app-api-key "super-secret-key-xyz-12345"
```

**Oczekiwany output:**
```
🔗 KROK 4/4: Wysyłanie danych do aplikacji UI...
======================================================================

🔍 Testuję połączenie z aplikacją...
   URL: https://livesport-scraper-api.herokuapp.com
   ✅ Połączenie działa! Endpoint: /api/health

📤 Wysyłam dane do aplikacji...
   URL: https://livesport-scraper-api.herokuapp.com/api/webhook/matches
   Sport: football
   Mecze: 5 (kwalifikujących: 2)
   ✅ Sukces! Status: 200
   📨 Odpowiedź: {'success': True, 'received': 5, 'saved': 5}
```

---

## 🎉 GOTOWE! Aplikacja działa na Heroku!

### **Twoje URL-e:**

- **Aplikacja:** https://livesport-scraper-api.herokuapp.com
- **Health check:** https://livesport-scraper-api.herokuapp.com/api/health
- **Webhook:** https://livesport-scraper-api.herokuapp.com/api/webhook/matches
- **API matches:** https://livesport-scraper-api.herokuapp.com/api/matches
- **Statystyki:** https://livesport-scraper-api.herokuapp.com/api/stats

---

## 🔧 Przydatne komendy Heroku

```powershell
# Sprawdź status aplikacji
heroku ps -a livesport-scraper-api

# Restart aplikacji
heroku restart -a livesport-scraper-api

# Otwórz dashboard
heroku dashboard -a livesport-scraper-api

# Sprawdź config vars
heroku config -a livesport-scraper-api

# Zmień config var
heroku config:set NOWA_ZMIENNA=wartosc -a livesport-scraper-api

# Usuń config var
heroku config:unset ZMIENNA -a livesport-scraper-api

# Sprawdź buildy
heroku builds -a livesport-scraper-api

# Rollback do poprzedniej wersji
heroku releases -a livesport-scraper-api
heroku rollback v2 -a livesport-scraper-api
```

---

## 📊 Heroku Basic Plan - Co dostajesz:

- ✅ **$7/miesiąc** (nie śpi jak Free tier)
- ✅ **24/7 uptime** - aplikacja zawsze dostępna
- ✅ **512MB RAM** - wystarczające dla SQLite + Express
- ✅ **Custom domain** - możesz dodać własną domenę
- ✅ **SSL certificate** - darmowy HTTPS
- ✅ **1000 dyno hours/miesiąc** - więcej niż Free tier
- ✅ **Metrics** - monitoring CPU, RAM, response time

---

## 🐛 Troubleshooting

### Problem 1: "Application error"

```powershell
# Sprawdź logi
heroku logs --tail -a livesport-scraper-api
```

**Możliwe przyczyny:**
- Błąd w Procfile (sprawdź czy to `web: node server.js`)
- Brak `package.json` w folderze
- Błąd w kodzie `server.js`

---

### Problem 2: "Database error"

```powershell
# Sprawdź czy folder data/ istnieje
heroku run ls -la -a livesport-scraper-api

# Stwórz folder data
heroku run mkdir -p data -a livesport-scraper-api
```

---

### Problem 3: "Cannot find module 'express'"

```powershell
# Rebuild aplikacji
heroku repo:purge_cache -a livesport-scraper-api
git commit --allow-empty -m "Rebuild"
git subtree push --prefix example_ui_app heroku main
```

---

### Problem 4: Git subtree nie działa

```powershell
# Użyj force push
git push heroku `git subtree split --prefix example_ui_app main`:main --force
```

---

## ✅ CHECKLIST KOŃCOWY

- [ ] Heroku CLI zainstalowane
- [ ] `heroku login` wykonane
- [ ] Aplikacja utworzona: `heroku create nazwa-app`
- [ ] Config vars ustawione (SCRAPER_API_KEY)
- [ ] Remote heroku dodany
- [ ] Deploy wykonany (git subtree push)
- [ ] Health check działa (200 OK)
- [ ] GitHub Secrets zaktualizowane (APP_URL + APP_API_KEY)
- [ ] Test lokalny ze scrapera zakończony sukcesem
- [ ] GitHub Actions przetestowane (ręczne uruchomienie)

---

## 🎯 NASTĘPNE KROKI

1. **Przetestuj automatyczne uruchomienie o północy**
   - Poczekaj do następnej nocy (00:00)
   - LUB uruchom ręcznie: GitHub → Actions → Run workflow

2. **Sprawdź bazę danych**
   ```powershell
   # Podłącz się do Heroku
   heroku run bash -a livesport-scraper-api
   
   # Sprawdź bazę
   ls -la data/
   sqlite3 data/matches.db "SELECT COUNT(*) FROM matches;"
   ```

3. **Monitoruj aplikację**
   - Dashboard: https://dashboard.heroku.com/apps/livesport-scraper-api
   - Metrics: CPU, RAM, Response time
   - Logs: Sprawdzaj codziennie po midnight scraping

---

**Powodzenia z deploymentem na Heroku! 🚀**

*Jakub Majka | LiveSport Scraper v7.0 + Heroku Integration*
