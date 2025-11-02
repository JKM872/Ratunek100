# 🚀 KOMPLETNA INSTRUKCJA WDROŻENIA
## Scraper (GitHub Actions) → Aplikacja UI

---

## 📋 SPIS TREŚCI

1. [Przegląd Architektury](#przegląd-architektury)
2. [Krok 1: Przygotowanie Aplikacji UI](#krok-1-przygotowanie-aplikacji-ui)
3. [Krok 2: Deployment Aplikacji](#krok-2-deployment-aplikacji)
4. [Krok 3: Konfiguracja GitHub Actions](#krok-3-konfiguracja-github-actions)
5. [Krok 4: Test końcowy](#krok-4-test-końcowy)
6. [Troubleshooting](#troubleshooting)

---

## 📊 PRZEGLĄD ARCHITEKTURY

```
┌─────────────────────────────────────┐
│      GITHUB ACTIONS                 │
│  (Scraper - hosting + automation)   │
│                                     │
│  ⏰ Codziennie o północy (0:00)    │
│  🔄 Automatyczne uruchamianie       │
│  📡 Scrapuje LiveSport              │
│  📧 Wysyła email z wynikami         │
└──────────────┬──────────────────────┘
               │
               │ HTTP POST
               │ /api/webhook/matches
               │ Authorization: Bearer API_KEY
               │
               ▼
┌─────────────────────────────────────┐
│      APLIKACJA UI                   │
│   (Railway/Render/localhost)        │
│                                     │
│  📥 Odbiera dane z webhook          │
│  💾 Zapisuje do SQLite              │
│  📊 REST API dla frontendu          │
│  🖥️ Interfejs użytkownika          │
└─────────────────────────────────────┘
```

**FLOW DANYCH:**
1. GitHub Actions uruchamia scraper o północy
2. Scraper zbiera mecze z LiveSport
3. Filtruje mecze (H2H ≥60%, forma, kursy)
4. Wysyła POST do Twojej aplikacji UI
5. Aplikacja zapisuje do bazy SQLite
6. Frontend wyświetla mecze użytkownikom
7. Użytkownik dostaje email z podsumowaniem

---

## 🎯 KROK 1: PRZYGOTOWANIE APLIKACJI UI

### 1.1 Skopiuj przykładową aplikację

Masz już gotową aplikację w folderze `example_ui_app/`:

```
example_ui_app/
├── server.js           # Backend Express + SQLite
├── package.json        # Zależności Node.js
├── .env.example        # Przykładowa konfiguracja
├── test_webhook.js     # Testy połączenia
└── README.md           # Dokumentacja
```

### 1.2 Zainstaluj zależności

```bash
cd example_ui_app
npm install
```

### 1.3 Skonfiguruj aplikację

Utwórz plik `.env`:

```bash
cp .env.example .env
```

Edytuj `.env` i ustaw **TAJNY KLUCZ API** (WAŻNE - zmień na własny!):

```env
PORT=3000
SCRAPER_API_KEY=twoj-super-tajny-klucz-xyz-12345
NODE_ENV=development
```

⚠️ **UWAGA:** Ten sam klucz musisz użyć w GitHub Secrets (krok 3)!

### 1.4 Test lokalny

Uruchom aplikację:

```bash
npm start
```

Powinieneś zobaczyć:

```
=======================================================================
🚀 APLIKACJA UI URUCHOMIONA
=======================================================================
📍 URL: http://localhost:3000
📊 API: http://localhost:3000/api
💾 Baza: C:\...\example_ui_app\data\matches.db
🔑 API Key: ✅ Ustawiony
=======================================================================

📝 Dostępne endpointy:
  GET  /api/health          - Health check
  POST /api/webhook/matches - Odbierz dane ze scrapera (wymaga API Key)
  GET  /api/matches         - Lista meczów
  GET  /api/stats           - Statystyki bazy danych
  GET  /api/sports          - Lista sportów z licznikami
```

Testuj połączenie:

```bash
npm test
```

Oczekiwany output:

```
✅ Aplikacja działa!
✅ Webhook działa!
✅ API działa!
✅ Statystyki działa!

🎉 WSZYSTKIE TESTY PRZESZŁY!
```

---

## 🌐 KROK 2: DEPLOYMENT APLIKACJI

Wybierz jedną z opcji:

### **OPCJA A: Railway (ZALECANE)** 🚂

Railway oferuje darmowy hosting (dla Student Pack) i prosty deployment.

#### 2.1 Zaloguj się do Railway

1. Wejdź: https://railway.app
2. Zaloguj się przez GitHub
3. Aktywuj Student Pack (jeśli masz)

#### 2.2 Utwórz nowy projekt

1. Kliknij **"New Project"**
2. Wybierz **"Deploy from GitHub repo"**
3. Autoryzuj Railway do dostępu do GitHub
4. Wybierz swoje repo (np. `Ratunek100`)

#### 2.3 Skonfiguruj service

1. Railway automatycznie wykryje Node.js
2. **Root Directory:** Ustaw na `example_ui_app`
3. **Build Command:** `npm install`
4. **Start Command:** `npm start`

#### 2.4 Dodaj zmienne środowiskowe

W Railway Dashboard → Variables → Add Variables:

```
SCRAPER_API_KEY=twoj-super-tajny-klucz-xyz-12345
NODE_ENV=production
```

#### 2.5 Deploy

1. Kliknij **"Deploy"**
2. Poczekaj ~2 minuty
3. Railway wygeneruje URL: `https://twoja-app.up.railway.app`
4. **ZAPISZ TEN URL** - będzie potrzebny w kroku 3!

#### 2.6 Test deploymentu

```bash
curl https://twoja-app.up.railway.app/api/health
```

Oczekiwana odpowiedź:

```json
{
  "status": "ok",
  "message": "Aplikacja UI działa!",
  "timestamp": "2025-10-26T12:00:00.000Z"
}
```

---

### **OPCJA B: Render** 🎨

Render również oferuje darmowy tier.

#### 2.1 Zaloguj się do Render

1. Wejdź: https://render.com
2. Zaloguj się przez GitHub

#### 2.2 Utwórz Web Service

1. Kliknij **"New"** → **"Web Service"**
2. Połącz z GitHub repo
3. Wybierz `Ratunek100`

#### 2.3 Konfiguracja

- **Name:** `livesport-ui-app`
- **Root Directory:** `example_ui_app`
- **Environment:** `Node`
- **Build Command:** `npm install`
- **Start Command:** `npm start`
- **Plan:** Free

#### 2.4 Zmienne środowiskowe

W sekcji "Environment Variables":

```
SCRAPER_API_KEY=twoj-super-tajny-klucz-xyz-12345
NODE_ENV=production
```

#### 2.5 Deploy

1. Kliknij **"Create Web Service"**
2. Poczekaj ~5 minut
3. Render wygeneruje URL: `https://livesport-ui-app.onrender.com`
4. **ZAPISZ TEN URL**

---

### **OPCJA C: Localhost + ngrok (Development)** 💻

Idealne do testów przed deploymentem.

#### 2.1 Uruchom aplikację lokalnie

```bash
cd example_ui_app
npm start
```

#### 2.2 Zainstaluj ngrok

Windows (PowerShell):
```powershell
# Pobierz z https://ngrok.com/download
# LUB zainstaluj przez Chocolatey:
choco install ngrok
```

Linux/Mac:
```bash
# Snap
sudo snap install ngrok

# Homebrew (Mac)
brew install ngrok
```

#### 2.3 Uruchom tunel ngrok

W **NOWYM terminalu**:

```bash
ngrok http 3000
```

Output:

```
Session Status    online
Forwarding        https://abc123xyz.ngrok.io -> http://localhost:3000
```

#### 2.4 Zapisz URL

**WAŻNE:** Skopiuj URL `https://abc123xyz.ngrok.io` - to Twój tymczasowy URL.

⚠️ **UWAGA:** Ngrok URL zmienia się po każdym restarcie! To rozwiązanie tylko na rozwój.

---

## 🔧 KROK 3: KONFIGURACJA GITHUB ACTIONS

### 3.1 Dodaj Secrets do GitHub

1. Wejdź na GitHub → Twoje repo (`Ratunek100`)
2. **Settings** → **Secrets and variables** → **Actions**
3. Kliknij **"New repository secret"**

Dodaj **2 secrets**:

#### Secret 1: APP_URL

```
Name: APP_URL
Secret: https://twoja-app.up.railway.app
```

(Lub URL z Render/ngrok)

#### Secret 2: APP_API_KEY

```
Name: APP_API_KEY
Secret: twoj-super-tajny-klucz-xyz-12345
```

⚠️ **WAŻNE:** To MUSI być ten sam klucz co w `.env` aplikacji!

### 3.2 Sprawdź workflow

Workflow `midnight-auto-scraping.yml` jest już zaktualizowany! ✅

Teraz scraper automatycznie wyśle dane do Twojej aplikacji.

### 3.3 Test ręczny (przed czekaniem do północy)

1. GitHub → **Actions**
2. Wybierz workflow **"Midnight Auto Scraping (All Sports)"**
3. Kliknij **"Run workflow"** → **"Run workflow"**
4. Poczekaj 5-10 minut
5. Sprawdź logi:

Powinieneś zobaczyć:

```
📤 Wysyłam dane do aplikacji...
   URL: https://twoja-app.up.railway.app
   Sport: football
   Mecze: 150 (kwalifikujących: 15)
   ✅ Sukces! Status: 200
   📨 Odpowiedź: {'success': true, 'received': 150, 'saved': 150}
```

---

## ✅ KROK 4: TEST KOŃCOWY

### 4.1 Test manualny ze scrapera (lokalnie)

W folderze głównym scrapera:

```bash
python scrape_and_notify.py \
  --date 2025-10-26 \
  --sports football \
  --to jakub.majka.zg@gmail.com \
  --from-email jakub.majka.zg@gmail.com \
  --password "vurb tcai zaaq itjx" \
  --headless \
  --max-matches 10 \
  --app-url https://twoja-app.up.railway.app \
  --app-api-key "twoj-super-tajny-klucz-xyz-12345"
```

Oczekiwany output:

```
🔗 KROK 4/4: Wysyłanie danych do aplikacji UI...
======================================================================

🔍 Testuję połączenie z aplikacją...
   URL: https://twoja-app.up.railway.app
   ✅ Połączenie działa! Endpoint: /api/health

📤 Wysyłam dane do aplikacji...
   URL: https://twoja-app.up.railway.app/api/webhook/matches
   Sport: football
   Mecze: 10 (kwalifikujących: 3)
   ✅ Sukces! Status: 200
   📨 Odpowiedź: {'success': True, 'received': 10, 'saved': 10}
```

### 4.2 Sprawdź bazę danych aplikacji

Wejdź na URL aplikacji i sprawdź API:

```bash
# Statystyki
curl https://twoja-app.up.railway.app/api/stats

# Lista meczów
curl https://twoja-app.up.railway.app/api/matches?qualifies=true
```

Powinieneś zobaczyć zapisane mecze! 🎉

### 4.3 Sprawdź logi aplikacji

**Railway:**
1. Railway Dashboard → Twój projekt
2. Zakładka **"Logs"**

**Render:**
1. Render Dashboard → Twój service
2. Zakładka **"Logs"**

Powinieneś zobaczyć:

```
📥 OTRZYMANO DANE ZE SCRAPERA
=======================================================================
📅 Data: 2025-10-26
⚽ Sport: football
📊 Mecze: 10 (kwalifikujących: 3)
⏰ Timestamp: 2025-10-26T12:00:00.000Z

✅ Zapisano: 10 meczów
```

---

## 🎉 GOTOWE!

Teraz masz **pełną automatyzację**:

✅ **Scraper** działa codziennie o północy (GitHub Actions)  
✅ **Automatycznie** wysyła dane do aplikacji UI  
✅ **Aplikacja** zapisuje do bazy SQLite  
✅ **API** dostępne dla frontendu  
✅ **Email** z podsumowaniem meczów  

**Wszystko bez Twojej interwencji!** 🚀

---

## 🐛 TROUBLESHOOTING

### Problem 1: "Connection refused"

**Objawy:**
```
❌ Błąd połączenia! Sprawdź czy aplikacja działa pod adresem: ...
```

**Fix:**
1. Sprawdź czy aplikacja działa:
   ```bash
   curl https://twoja-app.up.railway.app/api/health
   ```
2. Sprawdź logi aplikacji (Railway/Render Dashboard)
3. Sprawdź czy `APP_URL` w GitHub Secrets jest poprawny

---

### Problem 2: "401 Unauthorized"

**Objawy:**
```
❌ Błąd! Status: 401
Odpowiedź: {"success": false, "error": "Unauthorized - Invalid API Key"}
```

**Fix:**
1. Sprawdź czy `APP_API_KEY` w GitHub Secrets = `SCRAPER_API_KEY` w aplikacji
2. Upewnij się że nagłówek to `Bearer twoj-klucz` (ze spacją!)
3. Sprawdź czy `.env` aplikacji ma poprawny klucz

---

### Problem 3: "500 Internal Server Error"

**Objawy:**
```
❌ Błąd! Status: 500
```

**Fix:**
1. Sprawdź logi aplikacji (Railway/Render Dashboard → Logs)
2. Sprawdź czy baza danych jest dostępna
3. Sprawdź czy folder `data/` ma uprawnienia zapisu:
   ```bash
   mkdir -p data
   chmod 755 data
   ```

---

### Problem 4: "Timeout"

**Objawy:**
```
❌ Timeout! Aplikacja nie odpowiedziała w ciągu 30 sekund
```

**Fix:**
1. Sprawdź czy aplikacja nie śpi (Render Free tier usypia po 15 min)
2. "Obudź" aplikację:
   ```bash
   curl https://twoja-app.up.railway.app/api/health
   ```
3. Rozważ płatny plan (Railway: $5/mo, Render: $7/mo)

---

### Problem 5: Brak danych w bazie

**Objawy:**
- API działa, ale zwraca 0 meczów
- Email przychodzi, ale baza pusta

**Fix:**
1. Sprawdź logi GitHub Actions - czy scraper rzeczywiście wysłał dane?
2. Sprawdź czy `--app-url` i `--app-api-key` są w poleceniu scrapera
3. Sprawdź logi aplikacji - czy webhook został wywołany?

---

### Problem 6: ngrok URL się zmienia

**Objawy:**
- Scraper nie może połączyć się z localhost
- ngrok URL jest inny niż w GitHub Secrets

**Fix:**
1. To normalne - ngrok URL zmienia się po restarcie
2. Rozwiązania:
   - **Płatny ngrok:** Stały URL ($8/mo)
   - **Użyj Railway/Render:** Stały URL (darmowy/tani)
   - **Aktualizuj Secret:** Za każdym razem gdy restart ngrok

---

## 📞 POMOC

Masz problem?

1. ✅ Sprawdź logi GitHub Actions
2. ✅ Sprawdź logi aplikacji (Railway/Render)
3. ✅ Testuj lokalnie: `npm test` w `example_ui_app/`
4. ✅ Testuj scraper lokalnie z `--app-url`
5. ✅ Sprawdź dokumentację: `example_ui_app/README.md`

---

## 📚 DODATKOWE ZASOBY

- **Dokumentacja scrapera:** `JAK_POŁĄCZYĆ_Z_APLIKACJĄ.md`
- **Dokumentacja aplikacji:** `example_ui_app/README.md`
- **Przykłady API:** `API_EXAMPLES.md`
- **Test integracji:** `example_ui_app/test_webhook.js`

---

**Powodzenia! 🚀**

Jakub Majka | LiveSport Scraper v7.0
